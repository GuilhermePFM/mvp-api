from quixstreams import Application
import json
import os
import dotenv
import logging
import sys
import pandas as pd

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import Session, BatchJob, JobStatus
from machine_learning.transactions_classifier import TransactionsClassifier

dotenv.load_dotenv()
KAFKA_BROKER_ADDRESS = os.getenv('KAFKA_BROKER_ADDRESS', 'localhost:9092')
EMBEDDINGS_RESULTS_TOPIC = os.getenv('EMBEDDINGS_RESULTS_TOPIC', 'embeddings-results')
CONSUMER_GROUP = os.getenv('CLASSIFICATION_CONSUMER_GROUP', 'classification_worker')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_job_completed(job_id, classified_transactions):
    """
    Update job status to completed with results
    
    Args:
        job_id: Job identifier
        classified_transactions: List of transactions with classifications
    """
    try:
        session = Session()
        batch_job = session.query(BatchJob).filter(BatchJob.id == job_id).first()
        
        if batch_job:
            batch_job.status = JobStatus.COMPLETED
            batch_job.transactions_output = json.dumps(classified_transactions)
            session.commit()
            logger.info(f"Job {job_id} completed successfully")
        else:
            logger.warning(f"Job {job_id} not found in database")
        
        session.close()
    except Exception as e:
        logger.error(f"Failed to update job {job_id} as completed: {str(e)}")


def update_job_failed(job_id, error_message):
    """
    Update job status to failed with error message
    
    Args:
        job_id: Job identifier
        error_message: Error description
    """
    try:
        session = Session()
        batch_job = session.query(BatchJob).filter(BatchJob.id == job_id).first()
        
        if batch_job:
            batch_job.status = JobStatus.FAILED
            batch_job.error_message = error_message
            session.commit()
            logger.info(f"Job {job_id} marked as failed: {error_message}")
        else:
            logger.warning(f"Job {job_id} not found in database")
        
        session.close()
    except Exception as e:
        logger.error(f"Failed to update job {job_id} as failed: {str(e)}")


def process_classification(message_value):
    """
    Process classification: combine embeddings with transactions and run ML model
    
    Args:
        message_value: JSON message containing job_id, transactions, and embeddings
    """
    job_id = message_value.get('job_id')
    transactions = message_value.get('transactions', [])
    embeddings = message_value.get('embeddings', [])
    
    logger.info(f"Processing classification for job {job_id} with {len(transactions)} transactions")
    
    try:
        # Convert embeddings to DataFrame
        embeddings_df = pd.DataFrame(embeddings, columns=[f'embedding_{i}' for i in range(len(embeddings[0]))])
        logger.info(f"Created embeddings DataFrame with shape {embeddings_df.shape}")
        
        # Create DataFrame with transaction data (excluding user and classification)
        transactions_data = []
        for t in transactions:
            datetime_obj = pd.to_datetime(t.get('date'), utc=True)
            datetime_ms = datetime_obj.astype('datetime64[ms]')
            tx_data = {
                'Data': datetime_ms,
                'Descrição': t.get('description'),
                'Valor': t.get('value')
            }
            transactions_data.append(tx_data)
        
        df = pd.DataFrame(transactions_data)
        logger.info(f"Created transactions DataFrame with shape {df.shape}")
        
        # Combine transactions with embeddings
        df_combined = pd.concat([df, embeddings_df], axis=1)
        logger.info(f"Combined DataFrame shape: {df_combined.shape}")
        logger.info(f"Combined DataFrame columns: {df_combined.columns}")
        logger.info(f": {df_combined.head()}")
        
        # Run ML classification
        model = TransactionsClassifier()
        classifications = model.predict(df_combined)
        logger.info(f"Model predicted {len(classifications)} classifications")
        
        # Create classified transactions list
        classified_transactions = []
        for i, t in enumerate(transactions):
            classified_tx = {
                'date': t.get('date'),
                'description': t.get('description'),
                'value': t.get('value'),
                'user': t.get('user'),
                'classification': classifications[i] if i < len(classifications) else None
            }
            classified_transactions.append(classified_tx)
        
        # Update job as completed
        update_job_completed(job_id, classified_transactions)
        
        logger.info(f"Successfully classified job {job_id}")
        
    except Exception as e:
        error_msg = f"Classification failed: {str(e)}"
        logger.error(f"Job {job_id} failed: {error_msg}")
        
        # Update job status to failed
        update_job_failed(job_id, error_msg)
        
        # Re-raise to log but don't break the worker
        raise


def consume_embeddings_results():
    """
    Main consumer loop: consume embeddings results and run classification
    """
    app = Application(
        broker_address=KAFKA_BROKER_ADDRESS,
        loglevel="INFO",
        consumer_group=CONSUMER_GROUP,
        auto_offset_reset="latest",
    )

    logger.info(f"Starting classification worker, consuming from {EMBEDDINGS_RESULTS_TOPIC}")

    with app.get_consumer() as consumer:
        consumer.subscribe([EMBEDDINGS_RESULTS_TOPIC])

        while True:
            msg = consumer.poll(1)

            if msg is None:
                continue
            elif msg.error() is not None:
                logger.error(f"Kafka error: {msg.error()}")
                raise Exception(msg.error())
            else:
                try:
                    key = msg.key().decode("utf8")
                    value = json.loads(msg.value())
                    offset = msg.offset()

                    logger.info(f"Received message at offset {offset} with key {key}")
                    
                    # Process the classification
                    process_classification(value)
                    
                    # Commit offset
                    consumer.store_offsets(msg)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    # Commit offset even on error to avoid infinite retries
                    consumer.store_offsets(msg)


if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("CLASSIFICATION WORKER STARTING")
        logger.info("=" * 60)
        consume_embeddings_results()
    except KeyboardInterrupt:
        logger.info("Classification worker stopped by user")
    except Exception as e:
        logger.error(f"Classification worker crashed: {str(e)}")
        raise

