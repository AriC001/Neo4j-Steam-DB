from neo4j import GraphDatabase

# Establecer conexión con la base de datos Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "12345678"
driver = GraphDatabase.driver(uri, auth=(username, password))


for user_id in range(1, 26):

    with driver.session() as session:
        query_recomandaciones_genero = f"""
            MATCH (u:Usuario {{id:'{user_id}'}})-[:TIENE_JUEGO]->(j:Game)
            WITH u, COLLECT(j) AS juegosUsuario

            // Obtener todos los géneros de los juegos del usuario
            UNWIND juegosUsuario AS juegoUsuario
            MATCH (juegoUsuario)-[:TIENE_GENERO]->(genero:Genero)
            WITH u, juegosUsuario, COLLECT(DISTINCT genero) AS generosUsuario

            // Encontrar juegos que no ha jugado el usuario
            MATCH (j2:Game)
            WHERE NOT (u)-[:TIENE_JUEGO]->(j2) and u.age >= TOINTEGER(j2.required_age)

            // Verificar que al menos uno de los géneros del juego coincida con uno de los géneros del usuario
            WITH u, juegosUsuario, j2, [(j2)-[:TIENE_GENERO]->(gen) WHERE gen IN generosUsuario | gen] AS generosJuego
            WHERE SIZE(generosJuego) > 0

            RETURN j2
            LIMIT 50
            """
        result = session.run(query_recomandaciones_genero)
        count = 0
        # Procesar resultados y escribir en un archivo de texto
        with open(f"./Recomendation/generoRec_{user_id}.txt", "w") as file:
            file.write("Recomendaciones de juegos para el usuario en base a los generos de sus juegos\n")
            file.write("=============================================\n\n")
            for record in result:
                juego_recomendado = record['j2']
                file.write(f"Nombre: {juego_recomendado['name']}\n")
        
        query_recomandaciones_saga = f""" 
            MATCH (u:Usuario {{id:'{user_id}'}})
            MATCH (j2:Game)
            WHERE NOT EXISTS((u)-[:TIENE_JUEGO]->(j2))
            WITH j2, u
            MATCH (j2)-[:SAGA]->(saga2)
            WITH j2, COLLECT(DISTINCT saga2.name) AS sagaNames
            MATCH (u)-[:TIENE_JUEGO]->(j:Game)
            WITH u, j, j2, sagaNames
            MATCH (j)-[:SAGA]->(saga)
            WITH u, j, j2, sagaNames, COLLECT(DISTINCT saga.name) AS userSagaNames
            WHERE ALL(sagaName IN sagaNames WHERE sagaName IN userSagaNames)
            RETURN DISTINCT j2
            """
        result = session.run(query_recomandaciones_saga)
        count = 0
        # Procesar resultados y escribir en un archivo de texto
        with open(f"./Recomendation/sagaRec_{user_id}.txt", "w") as file:
            file.write("Recomendaciones de juegos para el usuario en base a los saga de sus juegos\n")
            file.write("=============================================\n\n")
            for record in result:
                juego_recomendado = record['j2']
                file.write(f"Nombre: {juego_recomendado['name']}\n")



        query_recomandaciones_dlc = f"""
            MATCH (u:Usuario {{id:'{user_id}'}})-[:TIENE_JUEGO]->(j:Game)
            WITH u,j
            MATCH (u)-[:TIENE_DLC]->(d:DLC)
            WITH u,j,collect(distinct(d.type)) as tiposs
            MATCH (j)-[:TIENE_DLC]->(d2:DLC) WHERE NOT EXISTS((u)-[:TIENE_DLC]->(d2)) and d2.type in tiposs
            return d2
            """
        result = session.run(query_recomandaciones_dlc)
        count = 0
        # Procesar resultados y escribir en un archivo de texto
        with open(f"./Recomendation/DLCRec_{user_id}.txt", "w") as file:
            file.write("Recomendaciones de DLC para el usuario en base a los dlc y juegos que ya tiene\n")
            file.write("=============================================\n\n")
            for record in result:
                juego_recomendado = record['d2']
                file.write(f"Nombre: {juego_recomendado['name']}\n")
