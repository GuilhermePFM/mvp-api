"""
Background job cleanup script for removing old batch jobs

This script should be run periodically (e.g., via cron) to clean up
batch jobs that are older than 24 hours to prevent database bloat.

Usage:
    python kafka/job_cleanup.py
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import Session, BatchJob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_old_jobs(max_age_hours=24):
    """
    Delete batch jobs older than specified hours
    
    Args:
        max_age_hours: Maximum age in hours before deletion (default: 24)
    
    Returns:
        Number of jobs deleted
    """
    try:
        session = Session()
        
        # Calculate cutoff time
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        # Find old jobs
        old_jobs = session.query(BatchJob).filter(
            BatchJob.created_at < cutoff_time
        ).all()
        
        deleted_count = len(old_jobs)
        
        if deleted_count > 0:
            logger.info(f"Found {deleted_count} jobs older than {max_age_hours} hours")
            
            # Delete old jobs
            for job in old_jobs:
                logger.info(f"Deleting job {job.id} (created: {job.created_at}, status: {job.status.value})")
                session.delete(job)
            
            session.commit()
            logger.info(f"Successfully deleted {deleted_count} old jobs")
        else:
            logger.info(f"No jobs older than {max_age_hours} hours found")
        
        session.close()
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("BATCH JOB CLEANUP STARTING")
    logger.info("=" * 60)
    
    try:
        deleted = cleanup_old_jobs(max_age_hours=24)
        logger.info(f"Cleanup complete. Deleted {deleted} jobs.")
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        sys.exit(1)

