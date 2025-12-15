from schemas.batch_classifier import BatchClassifierListSchema
from schemas.batch_job import BatchClassifyAsyncRequest, BatchClassifyAsyncResponse, BatchJobStatusResponse
from config import app
from config import classification_model_tag as tag 
from logger import logger
from schemas import  ErrorSchema
from config import transaction_tag as transaction_tag
from config import app
from flask import request, json
from pydantic import ValidationError, BaseModel, Field
from machine_learning.transactions_classifier import TransactionsClassifier
from machine_learning.transactions_classification.lib.external_embedding_api import create_embeddings_api
from model import Session, BatchJob, JobStatus
from kafka.batch_job_publisher import publish_batch_job
import pandas as pd
import json as json_module


class JobIdPath(BaseModel):
    """Path parameter model for job_id"""
    job_id: str = Field(..., description="job id")


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


@app.post('/batch-classify-async', tags=[tag],
          responses={"202": BatchClassifyAsyncResponse, "400": ErrorSchema, "500": ErrorSchema})
def batch_classify_async(body: BatchClassifyAsyncRequest):
    """
    Submit a batch classification job for async processing.
    Returns a job ID for polling status.
    """
    try:
        logger.debug(f"Creating async batch classification job")
        
        # Convert transactions to JSON string for storage
        transactions_data = [t.model_dump(mode='json') for t in body.transactions]
        transactions_json = json_module.dumps(transactions_data)
        
        # Create job in database
        session = Session()
        batch_job = BatchJob(
            transactions_input=transactions_json,
            status=JobStatus.PENDING
        )
        session.add(batch_job)
        session.commit()
        
        job_id = batch_job.id
        logger.info(f"Created batch job {job_id} in database")
        
        # Publish to Kafka
        try:
            publish_batch_job(job_id, transactions_data)
            logger.info(f"Published batch job {job_id} to Kafka")
        except Exception as kafka_error:
            # If Kafka publish fails, mark job as failed
            batch_job.status = JobStatus.FAILED
            batch_job.error_message = f"Failed to publish to Kafka: {str(kafka_error)}"
            session.commit()
            session.close()
            raise kafka_error
        
        session.close()
        
        # Return job ID with 202 Accepted
        return BatchClassifyAsyncResponse(jobId=job_id).model_dump(), 202
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return {"message": f"Validation error: {str(e)}"}, 400
        
    except Exception as e:
        error_msg = f"Could not create batch classification job: {e}"
        logger.error(error_msg)
        return {"message": error_msg}, 500


@app.get('/batch-jobs/<str:job_id>', tags=[tag],
         responses={"200": BatchJobStatusResponse, "404": ErrorSchema, "500": ErrorSchema})
def get_batch_job_status(path: JobIdPath):
    """
    Get the status of a batch classification job.
    Returns status and results if completed.
    Deletes the job after successful fetch if status is completed.
    """
    try:
        job_id = path.job_id  # Extract job_id from path model
        
        logger.debug(f"Fetching status for job {job_id}")
        
        session = Session()
        batch_job = session.query(BatchJob).filter(BatchJob.id == job_id).first()
        
        if not batch_job:
            session.close()
            return {"message": f"Job {job_id} not found"}, 404
        
        # Build response based on status
        response = BatchJobStatusResponse(status=batch_job.status.value)
        
        if batch_job.status == JobStatus.COMPLETED:
            # Include results
            if batch_job.transactions_output:
                transactions_data = json_module.loads(batch_job.transactions_output)
                response.transactions = transactions_data
            
            # Delete job after successful fetch (cleanup)
            logger.info(f"Deleting completed job {job_id} after fetch")
            session.delete(batch_job)
            session.commit()
            
        elif batch_job.status == JobStatus.FAILED:
            # Include error message
            response.message = batch_job.error_message or "Classification failed"
        
        session.close()
        
        return response.model_dump(), 200
        
    except Exception as e:
        error_msg = f"Could not fetch job status: {e}"
        logger.error(error_msg)
        return {"message": error_msg}, 500