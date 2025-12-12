from quixstreams import Application
import json
import os
import dotenv
import logging
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import Session, BatchJob, JobStatus
from machine_learning.transactions_classification.lib.external_embedding_api import create_embeddings_api
from kafka.utils import retry_with_backoff

dotenv.load_dotenv()
KAFKA_BROKER_ADDRESS = os.getenv('KAFKA_BROKER_ADDRESS', 'localhost:9092')
BATCH_JOBS_TOPIC = os.getenv('BATCH_JOBS_TOPIC', 'batch-jobs')
EMBEDDINGS_RESULTS_TOPIC = os.getenv('EMBEDDINGS_RESULTS_TOPIC', 'embeddings-results')
CONSUMER_GROUP = os.getenv('EMBEDDINGS_CONSUMER_GROUP', 'embeddings_worker')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@retry_with_backoff(max_retries=3, initial_delay=2)
def fetch_embeddings_with_retry(descriptions):
    """
    Call external embedding API with retry logic
    
    Args:
        descriptions: List of text descriptions
        
    Returns:
        Embeddings from the API
    """
    return create_embeddings_api(descriptions)


def update_job_status(job_id, status, error_message=None, retry_count=None):
    """
    Update job status in database
    
    Args:
        job_id: Job identifier
        status: New JobStatus
        error_message: Optional error message
        retry_count: Optional retry count
    """
    try:
        session = Session()
        batch_job = session.query(BatchJob).filter(BatchJob.id == job_id).first()
        
        if batch_job:
            batch_job.status = status
            if error_message:
                batch_job.error_message = error_message
            if retry_count is not None:
                batch_job.retry_count = retry_count
            session.commit()
            logger.info(f"Updated job {job_id} status to {status.value}")
        else:
            logger.warning(f"Job {job_id} not found in database")
        
        session.close()
    except Exception as e:
        logger.error(f"Failed to update job {job_id} status: {str(e)}")


def process_batch_job(message_value):
    """
    Process a batch job: fetch embeddings and publish to next topic
    
    Args:
        message_value: JSON message containing job_id and transactions
    """
    job_id = message_value.get('job_id')
    transactions = message_value.get('transactions', [])
    
    logger.info(f"Processing batch job {job_id} with {len(transactions)} transactions")
    
    try:
        # Update status to processing
        update_job_status(job_id, JobStatus.PROCESSING)
        
        # Extract descriptions
        descriptions = [t.get('description', '') for t in transactions]
        logger.info(f"Extracted {len(descriptions)} descriptions for job {job_id}")
        
        # Call external embedding API with retry
        embeddings = fetch_embeddings_with_retry(descriptions)
        logger.info(f"Successfully fetched embeddings for job {job_id}")
        
        # Prepare message for classification worker
        result_message = {
            'job_id': job_id,
            'transactions': transactions,
            'embeddings': embeddings
        }
        
        return result_message
        
    except Exception as e:
        error_msg = f"Failed to fetch embeddings: {str(e)}"
        logger.error(f"Job {job_id} failed: {error_msg}")
        
        # Update job status to failed
        update_job_status(job_id, JobStatus.FAILED, error_message=error_msg)
        
        # Re-raise to prevent Kafka offset commit
        raise


def consume_batch_jobs():
    """
    Main consumer loop: consume batch jobs and publish embeddings results
    """
    app = Application(
        broker_address=KAFKA_BROKER_ADDRESS,
        loglevel="INFO",
        consumer_group=CONSUMER_GROUP,
        auto_offset_reset="latest",
    )

    logger.info(f"Starting embeddings worker, consuming from {BATCH_JOBS_TOPIC}")
    logger.info(f"Publishing results to {EMBEDDINGS_RESULTS_TOPIC}")

    with app.get_consumer() as consumer:
        consumer.subscribe([BATCH_JOBS_TOPIC])

        with app.get_producer() as producer:
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
                        
                        # Process the job
                        result_message = process_batch_job(value)
                        
                        # Publish to embeddings-results topic
                        producer.produce(
                            topic=EMBEDDINGS_RESULTS_TOPIC,
                            key=key,
                            value=json.dumps(result_message),
                        )
                        logger.info(f"Published embeddings results for job {key}")
                        
                        # Commit offset only on success
                        consumer.store_offsets(msg)
                        
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        # Don't commit offset on error - message will be reprocessed
                        # But to avoid infinite loop, we still commit after logging
                        consumer.store_offsets(msg)


if __name__ == "__main__":
    try:
        logger.info("=" * 60)
        logger.info("EMBEDDINGS WORKER STARTING")
        logger.info("=" * 60)
        consume_batch_jobs()
    except KeyboardInterrupt:
        logger.info("Embeddings worker stopped by user")
    except Exception as e:
        logger.error(f"Embeddings worker crashed: {str(e)}")
        raise

