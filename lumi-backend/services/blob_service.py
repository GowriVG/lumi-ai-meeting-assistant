import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER")

client = BlobServiceClient.from_connection_string(conn)
container = client.get_container_client(container_name)

def upload_text(blob_name, text):
    container.upload_blob(blob_name, text, overwrite=True)

def download_text(blob_name):
    blob = container.get_blob_client(blob_name)
    return blob.download_blob().readall().decode("utf-8")

def blob_exists(blob_name):
    blob = container.get_blob_client(blob_name)
    return blob.exists()