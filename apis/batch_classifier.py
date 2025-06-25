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


@app.post('/batchclassifier', tags=[tag],
          responses={"200": BatchClassifierListSchema, "500": ErrorSchema, "400": ErrorSchema})
def run_classifier(body: BatchClassifierListSchema):
    """
    Run the classification model on all transactions and return the results.
    """
    try:
        logger.debug(f"Running classifier")
        model = TransactionsClassifier()
        data = [i.model_dump() for i in body.transactions]
        import pandas as pd
        df =         pd.DataFrame(data)
        df = df.drop(["user",'classification'], axis=1)
        classifications = model.predict(df)
        

        classified_data = [{**row.model_dump(), 'classification': classification} for row, classification in zip(body.transactions, list(classifications))]
        classified_objects = BatchClassifierListSchema(transactions = classified_data) 
       
        return classified_objects.model_dump()

       
    except ValidationError as e:
        # If the JSON data doesn't match the Pydantic model, return a 400 Bad Request response
        # return jsonify({'error': str(e)}), 400
        pass

    except Exception as e:
        error_msg = "Could not run classifier"
        logger.warning(error_msg)
        return {"mesage": error_msg}, 400