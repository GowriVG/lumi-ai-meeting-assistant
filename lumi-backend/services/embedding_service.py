import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

embedding_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
)

def get_embedding(text: str):
    response = embedding_client.embeddings.create(
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        input=text
    )
    return response.data[0].embedding