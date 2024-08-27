## Api extraction using Airflow and Azure. The pokemon api documentation can be found [here](https://pokeapi.co/docs/v2)
### Content

* [Utilized technologies](#technologies)
* [Architecture](#project-architecture)
* [Api code](#api)
* [Configuration](#configs)
* [Azure storage](#azure-storage)
* [The Dag](#the-dag)
* [Azure data factory](#azure-data-factory)
* [Azure Sql](#azure-sql)
* [Postgresql](#postgresql)

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

Initially, just made a request to a simple return from the api (the first 20 registers), then implemented the while loop to interact until the url stop returning something, in that case the next 20 pokemon. The function 'to_blob_storage' sends the extracted data to azure storage (showed bellow).

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

The config_az.py defines as function load_config() that searchs in the conn.ini for the section 'azurestorage' and return that data in a dictionary 'config'. It will raise an exception if don`t find the section (azurestorage) in the conn.ini.
```python
from configparser import ConfigParser

def load_config(filename='conns.ini', section='azurestorage'):
    parser = ConfigParser()
    parser.read(filename)

    # get section
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')

    return config
```
### Azure storage

to_az_storage.py loads the configuration settings from load_config(). It defines a function to upload the given data as a parquet file to azure storage. It converts the data to a dataframe an to parquet, then upload to the specified container.
```python
from config_az import load_config
from io import BytesIO
import pandas as pd
from azure.storage.blob import BlobServiceClient
#pip install azure-storage-blob


def to_blob_storage(data, filename = ''):

    config = load_config()

    connection_string = config['connection_string']
    container_name = config['container_name']

    df = pd.DataFrame(data)

    parquet_file = BytesIO()
    df.to_parquet(parquet_file)
    parquet_file.seek(0)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container = container_name, blob = filename)

    blob_client.upload_blob(data = parquet_file, overwrite = True)
    print(f'file {filename} uploaded to azure storage')
```
### The Dag

Create empty operators 'start_pipeline' and 'done_pipeline' to mark the star and the end of the pipeline. The PythonOperator executes the extrair_pokemon function.
```python
from airflow import DAG
from datetime import datetime
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from api_pokemon import extrair_pokemon


default_args = {
    "owner": "Manoel",
    "start_date": datetime(2024, 8, 21),
}
with DAG(
    dag_id="pokemon_extraction",
    default_args = default_args,
    schedule = None,
    max_active_runs = 1,
) as dag:
    start_pipeline = EmptyOperator(
        task_id = "start_pipeline",
    )
    extract_pokemon = PythonOperator(
        task_id = "extract_pokemon",
        python_callable = extrair_pokemon,
    )
    done_pipeline = EmptyOperator(
        task_id = "done_pipeline",
    )
    start_pipeline >> extract_pokemon >> done_pipeline
```
![dag_graph](https://github.com/user-attachments/assets/d942ce9b-f4ae-4ec7-a1a3-0f03118ab1a9)

### Azure data factory

After the dag completes, it writes a file in the azure container that is configured with an trigger of the type Storage events. So it is triggered a pipeline that creates an table in Azure Sql.

#### File in storage:

![file_in_storage_2](https://github.com/user-attachments/assets/07fbd156-9a78-4c50-abfc-2a25ab45f6f7)

#### Pipeline:

![pipe_to_sql](https://github.com/user-attachments/assets/5ea3a6b4-a5b1-419b-9b93-8ae1166f8e34)

### Azure Sql

Using DBeaver, i connected to the server and database, and used the SalesLT schema that Azure sql already provides for tests.

![dbeaver](https://github.com/user-attachments/assets/7ca8627e-9536-427b-a8ea-bbbb36aef7cc)

### Postgresql

Alternativaly, you can create a table in local database, using to_postgresql.py. The scrpt defines a function that converts the 'extract_data' into a dataframe and insert into a table in a local postgresql. load_config function is similar to the azure load_config, passing the access for the local postgre connection.
```python
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from datetime import datetime
from config import load_config

def to_postgresql(extract_data, table_name, table_schema = ""):
    # making the convertion of the given parameter 'extract_data',
    # the pokemon_list in that case, to a pandas dataframe
    
    df = pd.DataFrame(extract_data)

    # add the load date
    df["DATA_CARGA"] = datetime.today().strftime('%Y-%m-%d')

    # Load
    config = load_config()

    user = config["user"]
    password = config["password"]
    host = config["host"]
    database = config["database"]
    schema = "testedel"

    #connection engine to postgresql, without specifying schema
    # engine = create_engine(f'postgresql://{user}:{password}@{host}/{database}')

    #connection engine to postgresql, specifying schema
    engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}/{database}',
                           connect_args={'options': f'-csearch_path={schema}'})

    #parameters for the connection with database
    conn = psycopg2.connect( host = host,
                            database = database,
                            user = user,
                            password = password
                            )
    
    conn.autocommit = True
    
    #cursor
    cursor = conn.cursor()
    
    sql_query = f"""
    DROP TABLE IF EXISTS {schema}.{table_name};
    CREATE TABLE {schema}.{table_name}(
        {table_schema},
        data_carga varchar(10)
    );
    """

    ##cursor to execute query
    print("executando query no sql")
    cursor.execute(sql_query)

    #insert the data in the created table in postgresql with the given table_name
    with engine.connect() as connection:
        try:
            df.to_sql(name=table_name, con=connection, if_exists= "replace", index=False)
            print("tabela inserida no PostgreSQL")
        except SQLAlchemyError as e:
            print(f"erro ao inserir tabela: {e}")

    #close connection
    conn.commit()
    conn.close()
    cursor.close()
```
To call the function in the api_pokemon.py, it is needed to pass the extracted data, name for the table and an schema, like that:
```python
    table_schema = """
        id int PRIMARY KEY,
        nome varchar(30),
        altura int,
        peso int
        """

    #calling the function to create the table "POKEMON", with the "table_schema" and pokemon_list data
    to_postgresql(pokemon_list, "pokemon", table_schema)

```
