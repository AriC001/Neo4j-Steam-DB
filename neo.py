import api

from neo4j import GraphDatabase

# Función para ejecutar la consulta Cypher
def ejecutar_consulta_cypher(consulta):
    uri = "bolt://localhost:7687"  # Cambia esto según tu configuración de Neo4j
    usuario = "neo4j"  # Cambia esto según tu configuración de Neo4j
    contraseña = "12345678"  # Cambia esto según tu configuración de Neo4j

    # Conexión a la base de datos Neo4j
    with GraphDatabase.driver(uri, auth=(usuario, contraseña)) as driver:
        with driver.session() as session:
            # Ejecutar la consulta Cypher
            resultado = session.run(consulta)
            session.close()
            return resultado
        driver.close()
        

Usuarios = list(range(1, 26))




from random import sample, randint

# Suponiendo que tienes una lista de usuarios


# Iterar sobre cada usuario
for usuario_id in Usuarios:
    # Detach Delete all users
    # detach_delete = f"""
    # MATCH (u:Usuario {{id: '{usuario_id}'}})
    # DETACH DELETE u
    # """
    # ejecutar_consulta_cypher(detach_delete)
    # Crear Usuario
    age = randint(11, 30)
    crear_usuario = f"""
    CREATE (u:Usuario {{id: '{usuario_id}',age:{age}}})
    """
    # Aquí deberías ejecutar la consulta Cypher
    ejecutar_consulta_cypher(crear_usuario)

    if age > 17:
        relacionar_user_juego = f"""
        // Seleccionar usuario
        MATCH (u:Usuario {{id: '{usuario_id}'}})
        
        // Seleccionar juegos de manera aleatoria (5 juegos en este ejemplo)
        MATCH (j:Game)
        WITH u, j,RAND() AS random
        ORDER BY random
        LIMIT TOINTEGER(RAND() * 30) + 1
        WITH COLLECT(j) AS juegos, u,j
        UNWIND juegos AS juego
        
        // Relacionar al usuario con el juego
        MERGE (u)-[:TIENE_JUEGO]->(juego)
        WITH u, juego
        
        // Si el juego tiene DLC, seleccionar algunos aleatoriamente
        OPTIONAL MATCH (juego)-[:TIENE_DLC]->(d:DLC)
        WITH u, juego, COLLECT(d) AS dlc_disponibles
        WHERE SIZE(dlc_disponibles) > 0
        WITH u, juego, dlc_disponibles, TOINTEGER(RAND() * SIZE(dlc_disponibles)) AS num_dlc
        WITH u, juego, dlc_disponibles[num_dlc..num_dlc + TOINTEGER(RAND() * 5)] AS dlc_seleccionados
        
        // Relacionar al usuario con los DLC seleccionados
        FOREACH (dlc IN dlc_seleccionados | 
            MERGE (u)-[:TIENE_DLC]->(dlc)
        )
        """
    else:
        relacionar_user_juego = f"""
        // Seleccionar usuario
        MATCH (u:Usuario {{id: '{usuario_id}'}})
        
        // Seleccionar juegos de manera aleatoria (5 juegos en este ejemplo)
        MATCH (j:Game) WHERE TOINTEGER(j.required_age) <= {age}
        WITH u, j,RAND() AS random
        ORDER BY random
        LIMIT TOINTEGER(RAND() * 30) + 1
        WITH COLLECT(j) AS juegos, u,j
        UNWIND juegos AS juego
        
        // Relacionar al usuario con el juego
        MERGE (u)-[:TIENE_JUEGO]->(juego)
        WITH u, juego
        
        // Si el juego tiene DLC, seleccionar algunos aleatoriamente
        OPTIONAL MATCH (juego)-[:TIENE_DLC]->(d:DLC)
        WITH u, juego, COLLECT(d) AS dlc_disponibles
        WHERE SIZE(dlc_disponibles) > 0
        WITH u, juego, dlc_disponibles, TOINTEGER(RAND() * SIZE(dlc_disponibles)) AS num_dlc
        WITH u, juego, dlc_disponibles[num_dlc..num_dlc + TOINTEGER(RAND() * 5)] AS dlc_seleccionados
        
        // Relacionar al usuario con los DLC seleccionados
        FOREACH (dlc IN dlc_seleccionados | 
            MERGE (u)-[:TIENE_DLC]->(dlc)
        )
        """
        # Aquí deberías ejecutar la consulta Cypher
        # ejecutar_consulta_cypher(relacionar_user_juego)

    print(usuario_id,end=" ")
    resultado = ejecutar_consulta_cypher(relacionar_user_juego)
