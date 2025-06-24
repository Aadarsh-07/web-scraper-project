from typing import List, Dict, Any
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from .base_scraper import BaseScraper
from src.utils.helpers import random_delay, clean_text, extract_date_from_text

class DiceScraper(BaseScraper):
    """Dice.com job scraper with stable Chrome configuration"""
    
    def get_platform_name(self) -> str:
        return "Dice"
    
    def get_selenium_driver(self):
        """Setup stable Chrome WebDriver"""
        chrome_options = Options()
        
        # Stability options
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-javascript')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Disable problematic features
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-features=BlinkGenPropertyTrees')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        
        # Disable AI/ML features causing crashes
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-background-networking')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    def scrape_jobs(self, search_terms: List[str], location: str = None) -> List[Dict[str, Any]]:
        """Scrape jobs with better error handling"""
        all_jobs = []
        
        # Limit search terms to prevent crashes
        limited_terms = search_terms[:5]  # Only first 5 terms
        
        for term in limited_terms:
            self.logger.info(f"Scraping Dice for: {term}")
            
            driver = None
            try:
                driver = self.get_selenium_driver()
                jobs = self._scrape_term_safe(driver, term, location)
                all_jobs.extend(jobs)
                self.logger.info(f"Successfully scraped {len(jobs)} jobs for {term}")
                
            except Exception as e:
                self.logger.error(f"Error scraping Dice for {term}: {e}")
                
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
            
            random_delay(3, 5)
        
        return self.filter_contract_jobs(all_jobs)
    
    def _scrape_term_safe(self, driver, search_term: str, location: str) -> List[Dict[str, Any]]:
        """Safe scraping method"""
        jobs = []
        
        try:
            # Simple Dice URL
            url = f"https://www.dice.com/jobs?q={search_term}&location={location or 'United States'}&employmentType=CONTRACT"
            
            self.logger.info(f"Loading URL: {url}")
            driver.get(url)
            
            # Wait for page load
            time.sleep(5)
            
            # Try to find job elements with multiple selectors
            job_selectors = [
                '[data-testid="job-card"]',
                '.card',
                '.job-tile',
                '.search-result-item'
            ]
            
            job_cards = []
            for selector in job_selectors:
                try:
                    job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        self.logger.info(f"Found {len(job_cards)} job cards with selector: {selector}")
                        break
                except:
                    continue
            
            if not job_cards:
                self.logger.warning(f"No job cards found for {search_term}")
                return jobs
            
            # Extract job data
            for i, card in enumerate(job_cards[:5]):  # Limit to 5 jobs per term
                try:
                    job_data = self._extract_job_data_safe(card, driver.current_url)
                    if job_data:
                        jobs.append(job_data)
                        self.logger.info(f"Extracted job {i+1}: {job_data['title']}")
                except Exception as e:
                    self.logger.warning(f"Error extracting job {i+1}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error in _scrape_term_safe: {e}")
        
        return jobs
    
    def _extract_job_data_safe(self, card, current_url) -> Dict[str, Any]:
        """Safe job data extraction"""
        try:
            # Try multiple selectors for each field
            title_selectors = ['[data-testid="job-title"]', '.job-title', 'h2', 'h3', '.title']
            company_selectors = ['[data-testid="job-company"]', '.company', '.company-name']
            location_selectors = ['[data-testid="job-location"]', '.location', '.job-location']
            
            title = self._get_text_by_selectors(card, title_selectors)
            company = self._get_text_by_selectors(card, company_selectors)
            location = self._get_text_by_selectors(card, location_selectors)
            
            if not title:
                return None
            
            return {
                'title': clean_text(title),
                'company': clean_text(company) or "Unknown Company",
                'location': clean_text(location) or "Unknown Location",
                'description': f"Contract position for {clean_text(title)}",
                'posting_date': extract_date_from_text(""),
                'platform': self.get_platform_name(),
                'url': current_url,
                'job_type': 'Contract'
            }
            
        except Exception as e:
            self.logger.warning(f"Error in _extract_job_data_safe: {e}")
            return None
    
    def _get_text_by_selectors(self, element, selectors):
        """Try multiple selectors to get text"""
        for selector in selectors:
            try:
                sub_element = element.find_element(By.CSS_SELECTOR, selector)
                text = sub_element.text.strip()
                if text:
                    return text
            except:
                continue
        return ""
