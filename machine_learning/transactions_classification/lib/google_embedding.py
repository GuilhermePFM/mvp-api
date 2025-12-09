import pandas as pd
from numpy.linalg import norm
import numpy as np
from google import genai
from google.genai import types
from tqdm.auto import tqdm
import os


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'models/gemini-embedding-001')
client = genai.Client(api_key=GEMINI_API_KEY)

from tqdm.auto import tqdm
tqdm.pandas()

DIMENSIONALITY = 768

# normalize embeddings
def normalize_embeddings(embeddings):
    embedding_values_np = np.array(embeddings)
    normed_embedding = embedding_values_np / norm(embedding_values_np)
    return normed_embedding


def embed_and_normalize_embeddings(complete_dataset, embeddings):
    """
    Expands the 'Embeddings' column (containing numpy arrays) into separate columns.
    Args:
        df (pd.DataFrame): DataFrame with an 'Embeddings' column containing arrays.
    Returns:
        pd.DataFrame: DataFrame with embeddings expanded into individual columns.
    """
    normalized_embeddings = [normalize_embeddings(arr) for arr in embeddings]

    embedding_df = pd.DataFrame(normalized_embeddings, 
                                columns=[f'embedding_{i}' for i in range(len(normalized_embeddings[0]))])

    embedded_dataset = pd.concat([complete_dataset, embedding_df], axis=1)
  
    return embedded_dataset

def make_embed_text_fn_batch(model):

    def embed_fn(texts: list[str]) -> list[list[float]]:
        # Set the task_type to CLASSIFICATION and embed the batch of texts
        result = client.models.embed_content(model=model,
                                            contents=texts,
                                            config=types.EmbedContentConfig(
                                                task_type="CLASSIFICATION",
                                                output_dimensionality=DIMENSIONALITY
                                                )).embeddings
        return [embedding.values for embedding in result]

    return embed_fn


def create_embeddings_batch(array_of_texts):
    embed_fn = make_embed_text_fn_batch(GEMINI_MODEL)

    batch_size = 25  # at most 100 requests can be in one batch
    all_embeddings = []

    # Loop over the texts in chunks of batch_size
    for i in tqdm(range(0, len(array_of_texts), batch_size)):
        batch = array_of_texts[i : i + batch_size]
        embeddings = embed_fn(batch)
        all_embeddings.extend(embeddings)

    return all_embeddings