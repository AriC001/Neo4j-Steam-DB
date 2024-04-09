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
    if params.get("categories"):
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
    if params.get("genres"):
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

def set_dlc_count(params):
    consulta_dlc_count = f"""
        MATCH (j:Game {{steam_appid: {params["steam_appid"]}}})-[:TIENE_DLC]->(dlc)
        WITH j, COUNT(dlc) AS cantidad_dlc
        SET j.dlc_count= cantidad_dlc
        """
    ejecutar_consulta_cypher(consulta_dlc_count)

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

#Games
#Saga = ["DOTA","NOSAGA","NOSAGA","HELLDIVERS","NOSAGA","Grand Theft Auto","Baldurs Gate","NOSAGA","NOSAGA","DARK SOULS","Football Manager",
Saga =["EA SPORTS FC - FIFA","F1","NOSAGA","Red Dead Redemption","NOSAGA","The Sims",      "Age of Empires","Resident Evil","Metro","Call of Duty","Titanfall","Battlefield","BioShock", "Dishonored", "Forza", "NOSAGA", "Assassin's Creed", "Batman Arkham", "Mortal Kombat", "Tomb Raider","Age of Empires","Resident Evil","Metro","Call of Duty","Titanfall","Battlefield","BioShock", "Dishonored", "Forza", "NOSAGA", "Assassin's Creed", "Batman Arkham", "Mortal Kombat", "Tomb Raider"]

#Juegos repetidos: 1506830, 221040
#Juegos que hay que agregar de nuevo (porque la cagué): 1506830, 

#Games =[570,1046930,1269260,583950,0,578080,0,1172470,0,394510,553850,0,413150,0,271590,1546990,1547000,1546970,0,228280,257350,1695830,1889930,1086940,0,236390,0,1245620,0,570940,236430,374320,0,872790,1100600,1263850,1569040,1904540,2252570,0,1313860,
#Games = [1506830,1811260,2195250,0,226580,286570,391040,515220,737800,1080110,1134570,1692250,2108330,2488620,0,1091500,0,1174180,1404210,0,105600,0,47890,1222670,0,1017900,266840,813780,933110,1466860,0,339340, 304240, 883710, 952060, 222480, 2050650, 21690, 287290, 

Games = [221040, 418370, 1196590,0,286690, 287390, 2669410, 412020,0, 2519060, 311210, 476600, 2000950, 1985820, 202970, 42700, 1962660, 209160, 1985810, 0, 1454890, 1237970, 0, 1517290, 1238810, 1238880, 1238820, 1238860, 1238840, 0, 409710, 409720, 8870, 8850, 7670, 0, 205100, 403640, 614570, 0, 1551360, 1293830, 2440510, 0, 814380, 0, 2208920, 911400, 812140, 582160, 359600, 359610, 368500, 354380, 311560, 289650, 277590, 260210, 201870, 48190, 33230, 15100, 0, 2420110, 1151640, 0, 35140, 208650, 200260, 209000, 0, 1971870, 976310, 307780, 237110, 0, 2478970, 750920, 391220, 289690, 203160, 225020, 225000, 224980, 225320, 225300, 224960, 35130, 8140, 8000, 7000, 813780,933110,1466860,0,339340, 304240, 883710, 952060, 222480, 2050650, 21690, 287290, 221040, 418370, 1196590,0,286690, 287390, 2669410, 412020,0, 2519060, 311210, 476600, 2000950, 1985820, 202970, 42700, 1962660, 209160, 1985810, 0, 1454890, 1237970, 0, 1517290, 1238810, 1238880, 1238820, 1238860, 1238840, 0, 409710, 409720, 8870, 8850, 7670, 0, 205100, 403640, 614570, 0, 1551360, 1293830, 2440510, 0, 814380, 0, 2208920, 911400, 812140, 582160, 359600, 359610, 368500, 354380, 311560, 289650, 277590, 260210, 201870, 48190, 33230, 15100, 0, 2420110, 1151640, 0, 35140, 208650, 200260, 209000, 0, 1971870, 976310, 307780, 237110, 0, 2478970, 750920, 391220, 289690, 203160, 225020, 225000, 224980, 225320, 225300, 224960, 35130, 8140, 8000, 7000]



# Crear Saga
sagaTracking = 0
saga = Saga[sagaTracking]
# if saga != "NOSAGA":
#     consulta_cypher_parametrizada = f"""CREATE (s:Saga {{name: '{saga}',developers:""}})"""
#     ejecutar_consulta_cypher(consulta_cypher_parametrizada)

# Definir los parámetros para la consulta Cypher
for index,games in enumerate(Games):
    saga = Saga[sagaTracking]
    if games == 0:
        if saga != "NOSAGA":
            consulta_update_saga = f""" 
            MATCH (s:Saga {{name: '{saga}'}})
            SET s.developers = '{{params["developers"]}}'
            """
            ejecutar_consulta_cypher(consulta_update_saga)
        sagaTracking +=1
        saga = Saga[sagaTracking]
        if saga != "NOSAGA":
            consulta_cypher_parametrizada = f"""CREATE (s:Saga {{name: '{saga}',developers:""}})"""
            ejecutar_consulta_cypher(consulta_cypher_parametrizada)
            # if index == len(Games) - 1:
            print("last element of game saga")
            # games es el último elemento en la lista
        continue
    print("element: ",index)
    print("game_id: ",games)
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
    # print(consulta_cypher_parametrizada)
    resultado = ejecutar_consulta_cypher(consulta_cypher_parametrizada, **params)

    #categories
    related_categories(params)
    genres(params)
    compatibility(params)

    if params.get("dlc") is not None:
        count=0
        for dlc in params.get("dlc"):
            print("dlc: ",count)
            count+=1
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

    #Set dlc_count
    set_dlc_count(params)

    
# # Iterar sobre los resultados directamente
# for registro in resultado:
    # print(registro)

# # O guardar los resultados en una lista si necesitas acceder a ellos varias veces
# registros = list(resultado)

# # Iterar sobre los resultados guardados en la lista
# for registro in registros:
    # print(registro)

"""
// Supongamos que tienes el ID del usuario
WITH 'usuario_id' AS usuario_id

// Seleccionar juegos de manera aleatoria (5 juegos en este ejemplo)
MATCH (j:Game)
WITH usuario_id, COLLECT(j) AS juegos
LIMIT randomPython
UNWIND juegos AS juego

// Si el juego tiene DLC, selecciona algunos aleatoriamente
OPTIONAL MATCH (j)-[:TIENE_DLC]->(d:DLC)
WITH usuario_id, juego, COLLECT(d) AS dlc_disponibles
CALL {
    WITH dlc_disponibles
    WHERE SIZE(dlc_disponibles) > 0
    RETURN dlc_disponibles[TOINTEGER(RAND() * SIZE(dlc_disponibles))] AS dlc
    LIMIT TOINTEGER(RAND() * 10) + 1  // Máximo 10 DLC por juego
}
WITH usuario_id, juego, COLLECT(dlc) AS dlc_seleccionados

// Relacionar al usuario con el juego y los DLC seleccionados
FOREACH (dlc IN dlc_seleccionados | 
    MERGE (u:Usuario {id: usuario_id})-[:TIENE_JUEGO]->(juego)
    MERGE (u:Usuario {id: usuario_id})-[:TIENE_DLC]->(dlc)
)


"""