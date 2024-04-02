# Explanation of the Code

Here's a brief explanation of the code:

The `get_game` function is defined to fetch game details from the Steam Web API. It takes a game id as an argument.

The `config` function from the `decouple` library is used to get the Steam API key from the environment variables.

An instance of the `Steam` class is created with the API key.

The `get_app_details` method of the `Steam` instance is used to fetch the details of the game with the provided id. The country is set to "AR" (Argentina).

The game details are then extracted from the response and stored in a dictionary. The dictionary includes the game's Steam app id, name, type, whether it's free or not, a detailed description, and minimum system requirements for PC, Mac, and Linux.

If the game has any downloadable content (DLC), the DLC ids are also added to the dictionary.

The `ejecutar_consulta_cypher` function is used to execute a Cypher query on a Neo4j database. Cypher is Neo4j's graph query language. The function takes a query and parameters for the query, establishes a connection to the Neo4j database, and executes the query.

The `dlc_params` function is used to get the details of a game using an API. The details are fetched using the game's DLC id.

The `add_game` and `add_dlc` variables are Cypher queries. The `add_game` query is used to create a new node of type Game with various properties like `steam_appid`, `name`, `type`, etc. The `add_dlc` query is used to create a relationship `TIENE_DLCs` from a Game node to a DLC node. The DLC node is created with properties `steam_appid` and `name`.
