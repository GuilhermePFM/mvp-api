import json
import logging
from quixstreams import Application
import os
import dotenv

dotenv.load_dotenv()
KAFKA_BROKER_ADDRESS = os.getenv('KAFKA_BROKER_ADDRESS', 'localhost:9092')
BATCH_JOBS_TOPIC = os.getenv('BATCH_JOBS_TOPIC', 'batch-jobs')

logger = logging.getLogger(__name__)


def publish_batch_job(job_id: str, transactions: list):
    """
    Publish a batch classification job to Kafka
    
    Args:
        job_id: Unique identifier for the job
        transactions: List of transaction dictionaries to classify
    """
    try:
        app = Application(
            broker_address=KAFKA_BROKER_ADDRESS,
            loglevel="DEBUG",
        )

        with app.get_producer() as producer:
            message = {
                "job_id": job_id,
                "transactions": transactions
            }
            
            producer.produce(
                topic=BATCH_JOBS_TOPIC,
                key=job_id,
                value=json.dumps(message),
            )
            
            logger.info(f"Published batch job {job_id} to Kafka topic {BATCH_JOBS_TOPIC}")
            
    except Exception as e:
        logger.error(f"Failed to publish batch job {job_id}: {str(e)}")
        raise


if __name__ == "__main__":
    # Test publishing
    logging.basicConfig(level="DEBUG")
    test_transactions = [
        {
            "date": "2024-01-15",
            "description": "Grocery shopping",
            "value": 150.50,
            "user": "John Doe",
            "classification": None
        }
    ]
    publish_batch_job("test-job-123", test_transactions)

