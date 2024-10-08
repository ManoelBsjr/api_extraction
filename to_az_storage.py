from config_az import load_config
from io import BytesIO
import pandas as pd
from azure.storage.blob import BlobServiceClient
#pip install azure-storage-blob


def to_blob_storage(data, filename = ''):

    config = load_config()

    connection_string = config['connection_string']
    container_name = config['container_name']
    format = '.parquet'

    df = pd.DataFrame(data)

    parquet_file = BytesIO()
    df.to_parquet(parquet_file)
    parquet_file.seek(0)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container = container_name, blob = filename+format)

    blob_client.upload_blob(data = parquet_file, overwrite = True)
    print(f'file {filename} uploaded to azure storage')