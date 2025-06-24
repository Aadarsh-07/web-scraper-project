from typing import List, Dict, Any
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .base_scraper import BaseScraper
from src.utils.helpers import random_delay, clean_text, extract_date_from_text

class LinkedInScraper(BaseScraper):
    """LinkedIn job scraper"""
    
    def get_platform_name(self) -> str:
        return "LinkedIn"
    
    def scrape_jobs(self, search_terms: List[str], location: str = None) -> List[Dict[str, Any]]:
        """Scrape jobs from LinkedIn"""
        all_jobs = []
        driver = self.get_selenium_driver()
        
        try:
            for term in search_terms:
                self.logger.info(f"Scraping LinkedIn for: {term}")
                jobs = self._scrape_term(driver, term, location)
                all_jobs.extend(jobs)
                random_delay(2, 4)
            
        finally:
            driver.quit()
        
        return self.filter_contract_jobs(all_jobs)
    
    def _scrape_term(self, driver, search_term: str, location: str) -> List[Dict[str, Any]]:
        """Scrape jobs for a specific search term"""
        jobs = []
        
        # Build LinkedIn search URL
        base_url = "https://www.linkedin.com/jobs/search"
        params = {
            'keywords': search_term,
            'location': location or 'United States',
            'f_JT': 'C',  # Contract jobs filter
            'f_TPR': 'r86400'  # Last 24 hours
        }
        
        url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        try:
            driver.get(url)
            time.sleep(3)
            
            # Scroll to load more jobs
            self._scroll_page(driver)
            
            # Find job cards
            job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-search-card')
            
            for card in job_cards[:20]:  # Limit to first 20 jobs
                try:
                    job_data = self._extract_job_data(driver, card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    self.logger.warning(f"Error extracting job data: {e}")
                    continue
                
                random_delay(1, 2)
            
        except Exception as e:
            self.logger.error(f"Error scraping LinkedIn for {search_term}: {e}")
        
        return jobs
    
    def _scroll_page(self, driver):
        """Scroll page to load more jobs"""
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
    
    def _extract_job_data(self, driver, card) -> Dict[str, Any]:
        """Extract job data from job card"""
        try:
            # Click on job card to get details
            card.click()
            time.sleep(2)
            
            # Extract job details
            title_element = card.find_element(By.CSS_SELECTOR, '.base-search-card__title')
            company_element = card.find_element(By.CSS_SELECTOR, '.base-search-card__subtitle')
            location_element = card.find_element(By.CSS_SELECTOR, '.job-search-card__location')
            
            # Try to get job description from detail panel
            try:
                description_element = driver.find_element(By.CSS_SELECTOR, '.show-more-less-html__markup')
                description = clean_text(description_element.text)
            except:
                description = ""
            
            # Try to get posting date
            try:
                date_element = card.find_element(By.CSS_SELECTOR, '.job-search-card__listdate')
                posting_date = extract_date_from_text(date_element.get_attribute('datetime'))
            except:
                posting_date = extract_date_from_text("")
            
            return {
                'title': clean_text(title_element.text),
                'company': clean_text(company_element.text),
                'location': clean_text(location_element.text),
                'description': description,
                'posting_date': posting_date,
                'platform': self.get_platform_name(),
                'url': driver.current_url,
                'job_type': 'Contract'
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting job data from card: {e}")
            return None
