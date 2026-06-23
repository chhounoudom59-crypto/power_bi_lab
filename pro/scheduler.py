"""
Scheduler for ETL Pipeline Automation
Supports: Daily, Hourly, Real-time scheduling
"""

import schedule
import time
import json
import logging
from datetime import datetime
from etl_pipeline import ETLPipeline

logger = logging.getLogger(__name__)


class ETLScheduler:
    """Schedule ETL pipeline execution"""
    
    def __init__(self, config_file: str):
        """Initialize scheduler with config"""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.pipeline = ETLPipeline(
            self.config['source'],
            self.config['target']
        )
    
    def run_etl_job(self):
        """Execute ETL pipeline"""
        logger.info(f"[{datetime.now()}] Starting scheduled ETL job...")
        
        success = self.pipeline.run_pipeline(
            tables=self.config['pipeline'].get('tables'),
            mode=self.config['pipeline'].get('mode', 'replace')
        )
        
        if success:
            logger.info(f"[{datetime.now()}] ETL job completed successfully")
        else:
            logger.error(f"[{datetime.now()}] ETL job failed")
    
    def schedule_daily(self, time_str: str = "02:00"):
        """Schedule daily execution at specific time"""
        schedule.every().day.at(time_str).do(self.run_etl_job)
        logger.info(f"Scheduled ETL to run daily at {time_str}")
    
    def schedule_hourly(self):
        """Schedule hourly execution"""
        schedule.every().hour.do(self.run_etl_job)
        logger.info("Scheduled ETL to run every hour")
    
    def schedule_interval(self, minutes: int = 30):
        """Schedule execution at specified interval (minutes)"""
        schedule.every(minutes).minutes.do(self.run_etl_job)
        logger.info(f"Scheduled ETL to run every {minutes} minutes")
    
    def start(self):
        """Start scheduler (blocking)"""
        logger.info("Starting ETL Scheduler...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
    
    def start_non_blocking(self):
        """Start scheduler (non-blocking) - useful for production"""
        import threading
        scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("ETL Scheduler started (non-blocking mode)")
    
    def _run_scheduler(self):
        """Internal scheduler loop"""
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scheduler.log'),
            logging.StreamHandler()
        ]
    )
    
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    
    try:
        scheduler = ETLScheduler(config_file)
        logger.info(f"ETL Scheduler initialized with config: {config_file}")
        logger.info("Starting scheduler in non-blocking mode...")
        scheduler.start_non_blocking()
        
        # Keep the main thread alive
        while True:
            import time
            time.sleep(1)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_file}")
        logger.error("Usage: python scheduler.py [config.json]")
        exit(1)
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        exit(1)
    
    # Configure schedule based on config
    schedule_type = scheduler.config['pipeline'].get('schedule', 'daily')
    
    if schedule_type == 'daily':
        time_str = scheduler.config['pipeline'].get('time', '02:00')
        scheduler.schedule_daily(time_str)
    elif schedule_type == 'hourly':
        scheduler.schedule_hourly()
    elif schedule_type == 'interval':
        minutes = scheduler.config['pipeline'].get('interval_minutes', 30)
        scheduler.schedule_interval(minutes)
    
    # Start scheduler
    scheduler.start()
