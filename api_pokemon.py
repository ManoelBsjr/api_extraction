import requests
import json
from to_az_storage import to_blob_storage

def extrair_pokemon():
    url = 'https://pokeapi.co/api/v2/pokemon/'

    pokemon_list = []

    while url != None:
        payload = {}
        headers = {}

        #making request
        response = json.loads(requests.request("GET", url, headers = headers, data = payload).text)

        #pick the next 20 pokemon
        url = response["next"]

        for nome in response["results"]:
            #pick the pokemon name and search in the "url_pokemon", so every iteration is made a request for a diferent "url_pokemon"
            pokemon_name = nome["name"]
            url_pokemon = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
            response_pokemon = json.loads(requests.request("GET", url_pokemon, headers = headers, data = payload).text)

            # dictionary
            infos = {
                "ID": response_pokemon["id"],
                "Nome" : pokemon_name,
                "Altura": response_pokemon["height"],
                "Peso": response_pokemon["weight"]
            }

            #append the dictionary data to the pokemon_list
            pokemon_list.append(infos)

            #printing the "ID",to have a track
            print(response_pokemon["id"])

    #write on to azure storage
    to_blob_storage(pokemon_list, "api_pokemon")