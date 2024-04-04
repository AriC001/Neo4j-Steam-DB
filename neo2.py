import api

from neo4j import GraphDatabase

# Función para ejecutar la consulta Cypher
def ejecutar_consulta_cypher(consulta, **params):
    uri = "bolt://localhost:7687"  # Cambia esto según tu configuración de Neo4j
    usuario = "neo4j"  # Cambia esto según tu configuración de Neo4j
    contraseña = "12345678"  # Cambia esto según tu configuración de Neo4j

    # Conexión a la base de datos Neo4j
    with GraphDatabase.driver(uri, auth=(usuario, contraseña)) as driver:
        with driver.session() as session:
            # Ejecutar la consulta Cypher
            resultado = session.run(consulta, **params)
            session.close()
            return resultado
        driver.close()
        
def dlc_params(dlc,saga):
    game = api.get_game(id=dlc,saga=saga)
    return game

def related_categories(params,dlc=False):
    for categoria in params.get("categories"):
        categoria_id = categoria["id"]
        categoria_descripcion = categoria["description"]

        # Verificar si la categoría ya existe en Neo4j
        # consulta_verificar_categoria = f"MATCH (c:Categoria {id: {categoria_id}}) RETURN c"
        # consulta_verificar_categoria = f"MATCH (c:Categoria {{id: {categoria_id}}}) RETURN c"

        # if not resultado:
            # Si la categoría no existe, crearla
        # consulta_crear_categoria = f"CREATE (c:Categoria {{id: {categoria_id}, descripcion: '{categoria_descripcion}'}})"
        consulta_crear_categoria = f"""
        MATCH (c:Categoria {{id: {categoria_id}}})
        MERGE (nueva_categoria:Categoria {{id: {categoria_id}, descripcion: '{categoria_descripcion}'}}) """
        # print(consulta_crear_categoria)
        ejecutar_consulta_cypher(consulta_crear_categoria)

        # Crear la relación entre el juego y la categoría
        if dlc == True:
            consulta_relacionar_categoria = f"""
            MATCH (juego:DLC {{steam_appid: {params["steam_appid"]}}})
            MERGE (categoria:Categoria {{id: {categoria_id}, descripcion: '{categoria_descripcion}'}})
            MERGE (juego)-[:TIENE_CATEGORIA]->(categoria)
            """
        else:
            consulta_relacionar_categoria = f"""
            MATCH (juego:Game {{steam_appid: {params["steam_appid"]}}})
            MERGE (categoria:Categoria {{id: {categoria_id}, descripcion: '{categoria_descripcion}'}})
            MERGE (juego)-[:TIENE_CATEGORIA {{required_age: {params["required_age"]}}}]->(categoria)
            """
        # print(consulta_relacionar_categoria)
        ejecutar_consulta_cypher(consulta_relacionar_categoria)

def compatibility(params):
    #crear los 4 tipos de compatibilidad y despues solo asignarlos no crearlos y asignarlos cada vez
    # VR tambien??

    platforms = params.get('platforms')
    if platforms["windows"] == True:
        relacionar_compatibility = f"""
            MATCH (juego:Game {{steam_appid: {params["steam_appid"]}}})
            MATCH (compatibility:Compatibility {{name: 'Windows'}})
            MERGE (juego)-[:COMPATIBLE_CON]->(compatibility)
            """
        ejecutar_consulta_cypher(relacionar_compatibility)
    if platforms["mac"] == True:
        relacionar_compatibility = f"""
            MATCH (juego:Game {{steam_appid: {params["steam_appid"]}}})
            MATCH (compatibility:Compatibility {{name: 'Mac'}})
            MERGE (juego)-[:COMPATIBLE_CON]->(compatibility)
            """
        ejecutar_consulta_cypher(relacionar_compatibility)
    if platforms["linux"] == True:
        relacionar_compatibility = f"""
            MATCH (juego:Game {{steam_appid: {params["steam_appid"]}}})
            MATCH (compatibility:Compatibility {{name: 'Linux'}})
            MERGE (juego)-[:COMPATIBLE_CON]->(compatibility)
            """
        ejecutar_consulta_cypher(relacionar_compatibility)


def genres(params):
    for genero in params.get("genres"):
        genero_id = genero["id"]
        genero_descripcion = genero["description"]
        consulta_crear_genero = f"""
        MATCH (genero:Genero{{id: {genero_id}}})
        MERGE (nuevo_genero:Genero {{id: {genero_id}, descripcion: '{genero_descripcion}'}}) """
        # print(consulta_crear_genero)
        ejecutar_consulta_cypher(consulta_crear_genero)

        consulta_relacionar_genero = f"""
            MATCH (juego:Game {{steam_appid: {params["steam_appid"]}}})
            MERGE (genero:Genero {{id: {genero_id}, descripcion: '{genero_descripcion}'}})
            MERGE (juego)-[:TIENE_GENERO]->(genero)
            """
        ejecutar_consulta_cypher(consulta_relacionar_genero)

def dlc_type(params):
    #crear los 2 tipos de dlc y despues solo asignarlos no crearlos y asignarlos cada vez
    if params.get("type") == "dlc":
        relacionar_dlc_tipo = f"""
            MATCH (dlc:DLC {{steam_appid: {params["steam_appid"]}}})
            MATCH (tipo:Tipo {{tipo: 'Juego'}})
            MERGE (dlc)-[:TIENE_TIPO]->(tipo)
            """
    else:
        relacionar_dlc_tipo = f"""
            MATCH (dlc:DLC {{steam_appid: {params["steam_appid"]}}})
            MATCH (tipo:Tipo {{tipo: 'Musica'}})
            MERGE (dlc)-[:TIENE_TIPO]->(tipo)
            """
    ejecutar_consulta_cypher(relacionar_dlc_tipo)

# Definir la consulta Cypher
add_game = """
    CREATE (g:Game {
        steam_appid: $steam_appid,
        name: $name,
        type: $type,
        is_free: $is_free,
        detailed_description: $detailed_description,
        pc_minimum_requirements: $pc_minimum_requirements,
        pc_recommended_requirements: $pc_recommended_requirements,
        mac_minimum_requirements: $mac_minimum_requirements,
        mac_recommended_requirements: $mac_recommended_requirements,
        linux_minimum_requirements: $linux_minimum_requirements,
        linux_recommended_requirements: $linux_recommended_requirements
    })
"""

add_dlc = """
    MATCH (g:Game {steam_appid: $fullgame_id})
    MERGE (g)-[:TIENE_DLCs]->(d:DLC {
        steam_appid: $steam_appid,
        name: $name,
        type: $type,
        is_free: $is_free,
        detailed_description: $detailed_description,
        pc_minimum_requirements: $pc_minimum_requirements,
        pc_recommended_requirements: $pc_recommended_requirements,
        mac_minimum_requirements: $mac_minimum_requirements,
        mac_recommended_requirements: $mac_recommended_requirements,
        linux_minimum_requirements: $linux_minimum_requirements,
        linux_recommended_requirements: $linux_recommended_requirements
    })
    )
"""

add_game2 = """
    CREATE (g:Game {
        steam_appid: $steam_appid%s
    })
    WITH g
    MATCH (s:Saga {name: $saga})
    MERGE (g)-[:SAGA]->(s)
"""
#o al reves  MERGE (s)-[:SAGA]->(g)

add_dlc2 = """
MATCH (juego:Game {steam_appid: $fullgame_id})
MERGE (juego)-[:TIENE_DLC]->(dlc:DLC {steam_appid: $steam_appid%s})
"""

categories = """
MATCH (c:Categorie {name: $})
"""



#excluded parameters
exclude = ["categories","genres","platforms","metacritic_score","dlc"]

#Saga
saga = "<The Witcher>"

#Games
theWitcher = [20900,20920,292030]
# theWitcher = [20920]



# Crear Saga
consulta_cypher_parametrizada = f"""CREATE (s:Saga {{name: '{saga}'}})"""
ejecutar_consulta_cypher(consulta_cypher_parametrizada)

# Definir los parámetros para la consulta Cypher
for games in theWitcher:
    params = api.get_game(id=games,saga=saga)
    # Construye la parte de la consulta Cypher correspondiente a los campos presentes en los datos
    parametros = ""
    for campo, valor in params.items():
        if campo != "steam_appid" and valor is not None and campo not in exclude:
            parametros += f', {campo}: "{valor}"'
    parametros += f', saga: "{saga}"'

    # Completa la consulta Cypher con los parámetros correspondientes
    consulta_cypher_parametrizada = add_game2 % parametros
    # print(games)
    print(consulta_cypher_parametrizada)
    resultado = ejecutar_consulta_cypher(consulta_cypher_parametrizada, **params)

    #categories
    related_categories(params)
    genres(params)
    compatibility(params)

    if params.get("dlc") is not None:
        for dlc in params.get("dlc"):
            extra_content = dlc_params(dlc,saga)
            parametros = ""
            for campo, valor in extra_content.items():
                if campo != "steam_appid" and valor is not None and campo not in exclude:
                    parametros += f', {campo}: "{valor}"'
            parametros += f', saga: "{saga}"'
            consulta_cypher_parametrizada = add_dlc2 % parametros
            # print(dlc)
            # print(consulta_cypher_parametrizada)
            resultado = ejecutar_consulta_cypher(consulta_cypher_parametrizada, **extra_content)
            #categories
            related_categories(extra_content,dlc=True)
            dlc_type(extra_content)

# # Iterar sobre los resultados directamente
# for registro in resultado:
    # print(registro)

# # O guardar los resultados en una lista si necesitas acceder a ellos varias veces
# registros = list(resultado)

# # Iterar sobre los resultados guardados en la lista
# for registro in registros:
    # print(registro)

