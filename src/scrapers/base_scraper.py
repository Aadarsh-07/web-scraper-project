from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.utils.helpers import random_delay, clean_text

class BaseScraper(ABC):
    """Base class for all job scrapers"""
    
    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session with headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(headers)
    
    def get_selenium_driver(self):
        """Setup and return Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    @abstractmethod
    def scrape_jobs(self, search_terms: List[str], location: str = None) -> List[Dict[str, Any]]:
        """Abstract method to scrape jobs from platform"""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name"""
        pass
    
    def filter_contract_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter jobs to only include contract positions"""
        contract_keywords = ['contract', 'contractor', 'freelance', 'temporary', 'temp', 'consulting']
        
        filtered_jobs = []
        for job in jobs:
            job_title = job.get('title', '').lower()
            job_description = job.get('description', '').lower()
            job_type = job.get('job_type', '').lower()
            
            if any(keyword in job_title or keyword in job_description or keyword in job_type 
                   for keyword in contract_keywords):
                filtered_jobs.append(job)
        
        return filtered_jobs
