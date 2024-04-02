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
        
def dlc_params(dlc):
    game = api.get_game(id=dlc)
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
            MERGE (juego)-[:CATEGORIA]->(categoria)
            """
        else:
            consulta_relacionar_categoria = f"""
            MATCH (juego:Game {{steam_appid: {params["steam_appid"]}}})
            MERGE (categoria:Categoria {{id: {categoria_id}, descripcion: '{categoria_descripcion}'}})
            MERGE (juego)-[:CATEGORIA]->(categoria)
            """
        # print(consulta_relacionar_categoria)
        ejecutar_consulta_cypher(consulta_relacionar_categoria)



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
"""

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
# theWitcher = [292030]


# Ejecutar la consulta Cypher

# Definir los parámetros para la consulta Cypher
for games in theWitcher:
    params = api.get_game(id=games)
    # Construye la parte de la consulta Cypher correspondiente a los campos presentes en los datos
    parametros = ""
    for campo, valor in params.items():
        if campo != "steam_appid" and valor is not None and campo not in exclude:
            parametros += f', {campo}: "{valor}"'

    # Completa la consulta Cypher con los parámetros correspondientes
    consulta_cypher_parametrizada = add_game2 % parametros
    # print(games)
    # print(consulta_cypher_parametrizada)
    resultado = ejecutar_consulta_cypher(consulta_cypher_parametrizada, **params)

    #categories
    related_categories(params)

    if params.get("dlc") is not None:
        for dlc in params.get("dlc"):
            extra_content = dlc_params(dlc)
            parametros = ""
            for campo, valor in extra_content.items():
                if campo != "steam_appid" and valor is not None and campo not in exclude:
                    parametros += f', {campo}: "{valor}"'

            consulta_cypher_parametrizada = add_dlc2 % parametros
            # print(dlc)
            # print(consulta_cypher_parametrizada)
            resultado = ejecutar_consulta_cypher(consulta_cypher_parametrizada, **extra_content)
            #categories
            related_categories(extra_content,dlc=True)

# # Iterar sobre los resultados directamente
# for registro in resultado:
    # print(registro)

# # O guardar los resultados en una lista si necesitas acceder a ellos varias veces
# registros = list(resultado)

# # Iterar sobre los resultados guardados en la lista
# for registro in registros:
    # print(registro)

