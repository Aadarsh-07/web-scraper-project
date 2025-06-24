import sys
import os
# clfrom src.scheduler.job_scheduler import JobScheduler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scheduler.job_scheduler import JobScheduler
from src.utils.logger import setup_logger
from src.utils.config import load_config
import argparse

def main():
    """Main entry point for the job scraper application"""
    logger = setup_logger()
    config = load_config()
    
    parser = argparse.ArgumentParser(description='Job Scraper Tool')
    parser.add_argument('--mode', choices=['manual', 'scheduled'], default='scheduled',
                       help='Run mode: manual or scheduled')
    parser.add_argument('--platform', choices=['linkedin', 'monster', 'dice', 'all'], 
                       default='all', help='Platform to scrape')
    
    args = parser.parse_args()
    
    scheduler = JobScheduler(config, logger)
    
    if args.mode == 'manual':
        logger.info("Running manual scraping...")
        scheduler.run_manual_scraping(args.platform)
    else:
        logger.info("Starting scheduled scraping...")
        scheduler.start_scheduled_scraping()

if __name__ == "__main__":
    main()
