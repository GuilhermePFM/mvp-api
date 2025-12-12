from schemas.batch_classifier import BatchClassifierListSchema
from config import app
from config import classification_model_tag as tag 
from logger import logger
from schemas import  ErrorSchema
from config import transaction_tag as transaction_tag
from config import app
from flask import request, json
from pydantic import ValidationError
from machine_learning.transactions_classifier import TransactionsClassifier
from machine_learning.transactions_classification.lib.external_embedding_api import create_embeddings_api
import pandas as pd

@app.post('/batchclassifier', tags=[tag],
          responses={"200": BatchClassifierListSchema, "500": ErrorSchema, "400": ErrorSchema})
def run_classifier(body: BatchClassifierListSchema):
    """
    Run the classification model on all transactions and return the results.
    """
    try:
        logger.debug(f"Running classifier")

        # get embeddings from the external API
        embeddings = create_embeddings_api([i.description for i in body.transactions])
        embeddings_df = pd.DataFrame(embeddings)

        # create a dataframe with the data
        data = [i.model_dump() for i in body.transactions]
        df =         pd.DataFrame(data)
        df = df.drop(["user",'classification'], axis=1)

        # add embeddings to the dataframe
        df = pd.concat([df, embeddings_df], axis=1)

        # run model classification
        model = TransactionsClassifier()
        classifications = model.predict(df)

        # create a list of classified data
        classified_data = [{**row.model_dump(), 'classification': classification} for row, classification in zip(body.transactions, list(classifications))]
        classified_objects = BatchClassifierListSchema(transactions = classified_data) 
       
        return classified_objects.model_dump()

       
    except ValidationError as e:
        # If the JSON data doesn't match the Pydantic model, return a 400 Bad Request response
        # return jsonify({'error': str(e)}), 400
        pass

    except Exception as e:
        error_msg = f"Could not run classifier: {e}"
        logger.error(error_msg)
        return {"message": error_msg}, 400