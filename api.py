# import requests

# r = requests.get('http://localhost:5000/api/v1/resources/book')

# https://api.steampowered.com/ISteamApps/GetAppList/v2/?key=DB9EC1447E70155012A4A4BA0EBDB004

# import steam_py as steam
from steam import Steam
from decouple import config
import json


def get_game(id):
    KEY = config('STEAM_API_KEY')
    # KEY = os.enviorment.get("STEAM_API_KEY")
    # os.environment.get(KEY)
    # KEY.encode('utf-8')
    # KEY.decode('utf-8')
    # user = Steam.users.search_user("the12thchairman")

    app_id = str(id)
    steam = Steam(KEY)

    # arguments: app_id
    user = steam.apps.get_app_details(app_id,country="AR")

    # print(user)
    game = {
        'steam_appid': user[app_id]["data"]['steam_appid'],
        'name': user[app_id]["data"]['name'],
        'type': user[app_id]["data"]['type'],
        'is_free': user[app_id]["data"]['is_free'],
        'detailed_description': user[app_id]["data"]['detailed_description'],
        # 'pc_requirements': user[app_id]["data"].get('pc_requirements', None),
        # 'mac_requirements': user[app_id]["data"].get('mac_requirements', None),
        # 'linux_requirements': user[app_id]["data"].get('linux_requirements', None),
        'pc_minimum_requirements': user[app_id]["data"].get('pc_requirements', None),#.get("minimum",None),
        # 'pc_recommended_requirements': user[app_id]["data"].get('pc_requirements', None),#.get("recommended",None),
        'mac_minimum_requirements': user[app_id]["data"].get('mac_requirements', None),#.get("minimum",None),
        # 'mac_recommended_requirements': user[app_id]["data"].get('mac_requirements', None),#.get("recommended",None),
        'linux_minimum_requirements': user[app_id]["data"].get('linux_requirements', None),#.get("minimum",None),
        # 'linux_recommended_requirements': user[app_id]["data"].get('linux_requirements', None),#.get("recommended",None),
        # Add more properties as needed
        # 'fullgame_id': user[app_id]["data"].get('fullgame', None),
    }
    if user[app_id]["data"].get('dlc'):
        game["dlc"] = user[app_id]["data"]["dlc"]

    if user[app_id]["data"].get('fullgame'):
        game["fullgame_id"] = int(user[app_id]["data"]["fullgame"]["appid"])

    game["detailed_description"] = limpiar_html(game['detailed_description'])

    if game.get("pc_minimum_requirements"):
        if game["pc_minimum_requirements"].get("minimum"):
            game["pc_minimum_requirements"] = user[app_id]["data"]["pc_requirements"]["minimum"]
            game["pc_minimum_requirements"] = limpiar_html(game["pc_minimum_requirements"])
        # game["pc_minimum_requirements"] = limpiar_html(game['pc_minimum_requirements'])
        if user[app_id]["data"]['pc_requirements'].get("recommended"):
            game["pc_recommended_requirements"] = user[app_id]["data"]["pc_requirements"]["recommended"]
            game["pc_recommended_requirements"] = limpiar_html(game["pc_recommended_requirements"])
        # game["pc_recommended_requirements"] = limpiar_html(game['pc_recommended_requirements'])

    if game.get("mac_minimum_requirements"):
        if game["mac_minimum_requirements"].get("minimum"):
            game["mac_minimum_requirements"] = user[app_id]["data"]["mac_requirements"]["minimum"]
            game["mac_minimum_requirements"] = limpiar_html(game["mac_minimum_requirements"])

        # game["mac_minimum_requirements"] = limpiar_html(game['mac_minimum_requirements'])
        if user[app_id]["data"]['mac_requirements'].get("recommended"):
            game["mac_recommended_requirements"] = user[app_id]["data"]["mac_requirements"]["recommended"]
            game["mac_recommended_requirements"] = limpiar_html(game["mac_recommended_requirements"])
            # game["mac_recommended_requirements"] = limpiar_html(game['mac_recommended_requirements'])

    if game.get("linux_minimum_requirements"):
        if game["linux_minimum_requirements"].get("minimum"):
            game["linux_minimum_requirements"] = user[app_id]["data"]["linux_requirements"]["minimum"]
            game["linux_minimum_requirements"] = limpiar_html(game["linux_minimum_requirements"])
        # game["linux_minimum_requirements"] = limpiar_html(game['linux_minimum_requirements'])
        if user[app_id]["data"]['linux_requirements'].get("recommended"):
            game["linux_recommended_requirements"] = user[app_id]["data"]["linux_requirements"]["recommended"]
            game["linux_recommended_requirements"] = limpiar_html(game["linux_recommended_requirements"])
        # game["linux_recommended_requirements"] = limpiar_html(game['linux_recommended_requirements'])
    
    # print(game)
    # Reemplaza cada instancia de comillas dobles por comillas simples en los valores de los campos
    game = {campo: valor.replace('"', "'") if isinstance(valor, str) else valor for campo, valor in game.items()}

    return game

from bs4 import BeautifulSoup

def limpiar_html(texto_html):
    # Parsear el texto HTML
    soup = BeautifulSoup(texto_html, "html.parser")
    # Obtener solo el texto sin las etiquetas HTML
    texto_limpio = soup.get_text(separator=" ", strip=True)
    return texto_limpio
    
    # You can then print or use the 'game' dictionary as needed
    # print(game)

    # json.dump(game, open('a.json', 'w'), indent=4)
    # with open('a.json') as json_file:
    #     gamee = json.load(json_file)
    # print(gamee)


if __name__ == "__main__":
    game = get_game(20920)
    json.dump(game, open('a.json', 'w'), indent=4)
    # main()