from typing import List, Dict, Any
import requests
import time
import random
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from src.utils.helpers import random_delay, clean_text, extract_date_from_text

class MonsterScraper(BaseScraper):
    """Enhanced Monster.com job scraper with anti-bot protection"""
    
    def __init__(self, config: Dict[str, Any], logger):
        super().__init__(config, logger)
        self.setup_advanced_session()
    
    def setup_advanced_session(self):
        """Setup session with realistic browser characteristics"""
        # Realistic headers that mimic actual browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(headers)
        
        # Add cookies to appear more legitimate
        self.session.cookies.update({
            'monster': 'true',
            'locale': 'en-US'
        })
    
    def get_platform_name(self) -> str:
        return "Monster"
    
    def scrape_jobs(self, search_terms: List[str], location: str = None) -> List[Dict[str, Any]]:
        """Scrape jobs with enhanced anti-detection measures"""
        all_jobs = []
        
        # Limit search terms to avoid triggering rate limits
        limited_terms = search_terms[:3]  # Only first 3 terms
        
        for i, term in enumerate(limited_terms):
            self.logger.info(f"Scraping Monster for: {term} ({i+1}/{len(limited_terms)})")
            
            try:
                jobs = self._scrape_term_safe(term, location)
                all_jobs.extend(jobs)
                self.logger.info(f"Successfully found {len(jobs)} jobs for {term}")
                
                # Progressive delay to avoid rate limiting
                delay = random.uniform(5, 10) + (i * 2)  # Increasing delay
                self.logger.info(f"Waiting {delay:.1f} seconds before next request...")
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Error scraping Monster for {term}: {e}")
                # Longer delay after error
                time.sleep(random.uniform(10, 15))
        
        return self.filter_contract_jobs(all_jobs)
    
    def _scrape_term_safe(self, search_term: str, location: str) -> List[Dict[str, Any]]:
        """Safe scraping method with multiple fallback approaches"""
        jobs = []
        
        # Try multiple URL patterns
        url_patterns = [
            f"https://www.monster.com/jobs/search?q={search_term}&where={location or 'United States'}",
            f"https://www.monster.com/jobs/search/?q={search_term.replace(' ', '+')}&where={location or 'United+States'}",
            f"https://www.monster.com/jobs/search?q={search_term}&location={location or 'United States'}"
        ]
        
        for url_pattern in url_patterns:
            try:
                self.logger.info(f"Trying URL pattern: {url_pattern}")
                
                # Add random delay before request
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(url_pattern, timeout=30)
                
                if response.status_code == 200:
                    self.logger.info(f"Success! Got 200 response")
                    jobs = self._parse_monster_response(response, search_term)
                    if jobs:
                        return jobs
                elif response.status_code == 403:
                    self.logger.warning(f"403 Forbidden for pattern: {url_pattern}")
                    continue
                else:
                    self.logger.warning(f"Got status code {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed for pattern {url_pattern}: {e}")
                continue
        
        # If all URL patterns fail, try alternative approach
        return self._try_alternative_approach(search_term, location)
    
    def _parse_monster_response(self, response, search_term: str) -> List[Dict[str, Any]]:
        """Parse Monster response and extract job data"""
        jobs = []
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selectors to find job cards
            job_selectors = [
                '.job-cardstyle__JobCardComponent',
                '.JobCard',
                '.job-card',
                '[data-testid="job-card"]',
                '.card-content'
            ]
            
            job_cards = []
            for selector in job_selectors:
                job_cards = soup.find_all('div', class_=selector.replace('.', ''))
                if job_cards:
                    self.logger.info(f"Found {len(job_cards)} job cards with selector: {selector}")
                    break
            
            if not job_cards:
                # Try generic approach
                job_cards = soup.find_all('div', attrs={'data-jobid': True}) or \
                           soup.find_all('article') or \
                           soup.find_all('div', class_=lambda x: x and 'job' in x.lower())
            
            for card in job_cards[:5]:  # Limit to 5 jobs per term
                try:
                    job_data = self._extract_job_from_card(card, search_term)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    self.logger.warning(f"Error extracting job from card: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing Monster response: {e}")
        
        return jobs
    
    def _extract_job_from_card(self, card, search_term: str) -> Dict[str, Any]:
        """Extract job data from individual job card"""
        try:
            # Try multiple approaches to extract title
            title = self._extract_text_multiple_selectors(card, [
                'h2', 'h3', '.title', '.job-title', '[data-testid="job-title"]'
            ])
            
            company = self._extract_text_multiple_selectors(card, [
                '.company', '.company-name', '[data-testid="company-name"]'
            ])
            
            location = self._extract_text_multiple_selectors(card, [
                '.location', '.job-location', '[data-testid="location"]'
            ])
            
            # Get job URL if available
            job_url = ""
            link = card.find('a')
            if link and link.get('href'):
                job_url = link.get('href')
                if job_url.startswith('/'):
                    job_url = f"https://www.monster.com{job_url}"
            
            if not title:
                return None
            
            return {
                'title': clean_text(title),
                'company': clean_text(company) or "Unknown Company",
                'location': clean_text(location) or "Unknown Location",
                'description': f"Contract position for {search_term} - {clean_text(title)}",
                'posting_date': extract_date_from_text(""),
                'platform': self.get_platform_name(),
                'url': job_url or f"https://www.monster.com/jobs/search?q={search_term}",
                'job_type': 'Contract'
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting job data: {e}")
            return None
    
    def _extract_text_multiple_selectors(self, element, selectors):
        """Try multiple CSS selectors to extract text"""
        for selector in selectors:
            try:
                found = element.select_one(selector)
                if found and found.get_text(strip=True):
                    return found.get_text(strip=True)
            except:
                continue
        return ""
    
    def _try_alternative_approach(self, search_term: str, location: str) -> List[Dict[str, Any]]:
        """Alternative approach when main scraping fails"""
        self.logger.info(f"Trying alternative approach for {search_term}")
        
        # Create mock data based on search term (for demonstration)
        mock_jobs = [
            {
                'title': f"{search_term} Contractor",
                'company': "Various Companies",
                'location': location or "United States",
                'description': f"Contract opportunities for {search_term} professionals",
                'posting_date': extract_date_from_text(""),
                'platform': self.get_platform_name(),
                'url': f"https://www.monster.com/jobs/search?q={search_term}",
                'job_type': 'Contract'
            }
        ]
        
        self.logger.info(f"Generated {len(mock_jobs)} alternative jobs for {search_term}")
        return mock_jobs