from schemas import TransactionSchema, ErrorSchema
from logger import logger
from schemas import *
from config import embedding_tag as embedding_tag
from config import app
from dotenv import load_dotenv
from pathlib import Path
import os
import requests
from machine_learning.embedding import normalize_embedding

# Load environment variables from the project root .env file, if present.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'models/gemini-embedding-001')
GEMINI_EMBEDDING_URL = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:embedContent"
DIMENSIONALITY = 768 # GOOGLE recommends using 768, 1536, or 3072 output dimensions.


@app.post('/embedding', tags=[embedding_tag],
          responses={"200": TransactionSchema, "409": ErrorSchema, "400": ErrorSchema})
def embedding(form: TransactionSchema):
    """
    Creates an embedding for a transaction description, using the Google Gemini API.

    REF: https://ai.google.dev/gemini-api/docs/embeddings#python
    """
    try:
        response = requests.post(GEMINI_EMBEDDING_URL, headers={"Authorization": f"Bearer {GEMINI_API_KEY}"}, 
        json={"model": GEMINI_MODEL, 
               "task_type": "CLASSIFICATION",
              "content": {'parts':[{'text': form.description}]},
              "output_dimensionality": DIMENSIONALITY
              }
        )
        logger.debug(f"Embedding created for transaction: '{form.description}'")
        embedding = response.json()['embeddings'][0]['values']  
        normalized_embedding = normalize_embedding(embedding)
        return normalized_embedding, 200
    
    except Exception as e:
        error_msg = f"Error creating embedding for transaction '{form}': {e}"   
        logger.warning(error_msg)
        return {"message": error_msg}, 400