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

    # query that will create the table. The DEFAULT keyword is used while
    # creating the DARTA_CARGA column to set the current date as a default value.

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
# if __name__ == '__main__':
#     to_postgresql = to_postgresql()