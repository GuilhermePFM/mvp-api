import requests
import os
import json

EMBEDDING_API_URL = os.getenv('EMBEDDING_API_URL')

def create_embeddings_api(array_of_texts):
    descriptions = {'descriptions':[{'description': text} for text in array_of_texts]}
    response = requests.post(f"{EMBEDDING_API_URL}/embeddings", json=json.dumps(descriptions))
    if response.status_code != 200:
        raise Exception(f"Failed to create embeddings: {response.text}")
    return response.json()['embeddings']