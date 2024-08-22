import requests
import json
from to_az_storage import to_blob_storage
from to_postgresql import to_postgresql
from save_file import save_file

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
                # "Primeira_Forma": response_pokemon["is_default"]
            }

            #append the dictionary data to the pokemon_list
            pokemon_list.append(infos)

            #printing the "ID",to have a track 
            print(response_pokemon["id"])
# CONSTRAINT pokemon_pkey PRIMARY KEY (ID),
    table_schema = """
        id int PRIMARY KEY,
        nome varchar(30),
        altura int,
        peso int
        """

    #calling the function to create the table "POKEMON", with the "table_schema" and pokemon_list data
    # to_postgresql(pokemon_list, "pokemon", table_schema)

    #save the file as CSV
    to_blob_storage(pokemon_list, "api_pokemon")
if __name__ == "__main__":
    extrair_pokemon()
    # extrair_pokemon = extrair_pokemon()