## This project is an api extraction. The api documentation can be found [here](https://pokeapi.co/docs/v2)
### Content

* [Utilized technologies](#technologies)
* [Architecture](#project-architecture)
* [Api code](#api)

### Technologies
The followig tools were used for the development:

- Python
- Airflow
- Azure Storage
- Azure Data Factory
- Azure Sql

### Project architecture

![api_arch](https://github.com/user-attachments/assets/e854fa0f-5376-43f7-ac4c-502eca59c6ae)

### Api

Initially, just made a request to a simple return from the api (the first 20 registers), then implemented the while loop and later the function 'to_blob_storage' to send the extracted data to azure storage.

```python
# lib imports
import requests
import json
from to_az_storage import to_blob_storage

def extrair_pokemon():
    url = 'https://pokeapi.co/api/v2/pokemon/'

    pokemon_list = []

    # while the url still returning something, it`s still interacting to get the next 20 registers
    while url != None:
        payload = {}
        headers = {}

        # making request
        response = json.loads(requests.request("GET", url, headers = headers, data = payload).text)

        # pick the next 20 pokemon
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

    #write on to azure storage
    to_blob_storage(pokemon_list, "api_pokemon")
```
### Configs

In these section, it is configured an .ini file with the azure storage credentials, to use those credentials in the function without hard code, improving
the code security.

```
conn.ini content:

[azurestorage]
storage_account_key = <account key here>
storage_account_name = <account name here>
connection_string = <connection string here>
container_name = <container name here>
```
Those information can be found in Azure storage account > Security + networking > Access keys

![example](https://github.com/user-attachments/assets/245664a4-07ca-4219-b645-8be887ed86f2)
