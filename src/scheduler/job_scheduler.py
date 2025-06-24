import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from src.scrapers.linkedin_scraper import LinkedInScraper
from src.scrapers.monsters_scraper import MonsterScraper
from src.scrapers.dice_scraper import DiceScraper
from src.data.processor import DataProcessor
from src.utils.config import get_role_mappings

class JobScheduler:
    """Handle scheduled job scraping"""
    
    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        self.role_mappings = get_role_mappings()
        
        # Initialize scrapers
        self.scrapers = {
            'linkedin': LinkedInScraper(config, logger),
            'monster': MonsterScraper(config, logger),
            'dice': DiceScraper(config, logger)
        }
        
        self.data_processor = DataProcessor(logger)
    
    def start_scheduled_scraping(self):
        """Start the scheduled scraping process"""
        # Schedule Monday job (72-hour window)
        schedule.every().monday.at("09:00").do(self._run_monday_scraping)
        
        # Schedule weekday jobs (24-hour window)
        schedule.every().tuesday.at("09:00").do(self._run_daily_scraping)
        schedule.every().wednesday.at("09:00").do(self._run_daily_scraping)
        schedule.every().thursday.at("09:00").do(self._run_daily_scraping)
        schedule.every().friday.at("09:00").do(self._run_daily_scraping)
        
        self.logger.info("Scheduled scraping started. Waiting for scheduled times...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _run_monday_scraping(self):
        """Run Monday scraping (72-hour window)"""
        self.logger.info("Starting Monday scraping (72-hour window)")
        self._run_scraping_job("monday")
    
    def _run_daily_scraping(self):
        """Run daily scraping (24-hour window)"""
        self.logger.info("Starting daily scraping (24-hour window)")
        self._run_scraping_job("daily")
    
    def _run_scraping_job(self, job_type: str):
        """Execute the scraping job"""
        try:
            all_jobs = []
            
            # Get search terms for all verticals
            search_terms = self._get_search_terms()
            
            # Scrape from all platforms
            for platform_name, scraper in self.scrapers.items():
                try:
                    self.logger.info(f"Scraping {platform_name}...")
                    jobs = scraper.scrape_jobs(search_terms)
                    all_jobs.extend(jobs)
                    self.logger.info(f"Found {len(jobs)} jobs from {platform_name}")
                except Exception as e:
                    self.logger.error(f"Error scraping {platform_name}: {e}")
            
            # Process and save data
            if all_jobs:
                df = self.data_processor.process_jobs(all_jobs)
                
                # Generate filename with timestamp and job type
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"job_scraping_{job_type}_{timestamp}.xlsx"
                
                filepath = self.data_processor.save_to_excel(df, filename)
                
                self.logger.info(f"Scraping completed. Found {len(all_jobs)} total jobs.")
                self.logger.info(f"Results saved to: {filepath}")
            else:
                self.logger.warning("No jobs found in this scraping session.")
                
        except Exception as e:
            self.logger.error(f"Error in scraping job: {e}")
    
    def run_manual_scraping(self, platform: str = 'all'):
        """Run manual scraping for testing"""
        self.logger.info(f"Starting manual scraping for platform: {platform}")
        
        all_jobs = []
        search_terms = self._get_search_terms()
        
        if platform == 'all':
            scrapers_to_run = self.scrapers.items()
        else:
            scrapers_to_run = [(platform, self.scrapers[platform])]
        
        for platform_name, scraper in scrapers_to_run:
            try:
                self.logger.info(f"Scraping {platform_name}...")
                jobs = scraper.scrape_jobs(search_terms)
                all_jobs.extend(jobs)
                self.logger.info(f"Found {len(jobs)} jobs from {platform_name}")
            except Exception as e:
                self.logger.error(f"Error scraping {platform_name}: {e}")
        
        # Process and save data
        if all_jobs:
            df = self.data_processor.process_jobs(all_jobs)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_scraping_manual_{timestamp}.xlsx"
            
            filepath = self.data_processor.save_to_excel(df, filename)
            
            self.logger.info(f"Manual scraping completed. Found {len(all_jobs)} total jobs.")
            self.logger.info(f"Results saved to: {filepath}")
        else:
            self.logger.warning("No jobs found in manual scraping.")
    
    def _get_search_terms(self) -> list:
        """Get search terms from all verticals"""
        search_terms = []
        
        for vertical, keywords in self.role_mappings['verticals'].items():
            search_terms.extend(keywords)
        
        return list(set(search_terms))  # Remove duplicates
