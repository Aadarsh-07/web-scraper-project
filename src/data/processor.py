import pandas as pd
from typing import List, Dict, Any
import os
from datetime import datetime
from src.utils.config import get_role_mappings
from src.utils.helpers import get_us_states

class DataProcessor:
    """Process and analyze scraped job data"""
    
    def __init__(self, logger):
        self.logger = logger
        self.role_mappings = get_role_mappings()
        self.us_states = get_us_states()
    
    def process_jobs(self, jobs: List[Dict[str, Any]]) -> pd.DataFrame:
        """Process raw job data into structured DataFrame"""
        if not jobs:
            return pd.DataFrame()
        
        df = pd.DataFrame(jobs)
        
        # Add vertical classification
        df['vertical'] = df.apply(self._classify_vertical, axis=1)
        
        # Extract state from location
        df['state'] = df['location'].apply(self._extract_state)
        
        # Add contract duration if available
        df['contract_duration'] = df['description'].apply(self._extract_contract_duration)
        
        # Clean and standardize data
        df = self._clean_dataframe(df)
        
        return df
    
    def _classify_vertical(self, row) -> str:
        """Classify job into vertical based on title and description"""
        title = row['title'].lower()
        description = row['description'].lower()
        
        text_to_check = f"{title} {description}"
        
        # Check each vertical
        for vertical, keywords in self.role_mappings['verticals'].items():
            if any(keyword.lower() in text_to_check for keyword in keywords):
                return vertical
        
        return "Other"
    
    def _extract_state(self, location: str) -> str:
        """Extract US state from location string"""
        if not location:
            return "Unknown"
        
        location_upper = location.upper()
        
        for state in self.us_states:
            if state.upper() in location_upper:
                return state
        
        # Check for state abbreviations
        state_abbrevs = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming'
        }
        
        for abbrev, full_name in state_abbrevs.items():
            if f" {abbrev} " in f" {location_upper} " or location_upper.endswith(f" {abbrev}"):
                return full_name
        
        return "Unknown"
    
    def _extract_contract_duration(self, description: str) -> str:
        """Extract contract duration from job description"""
        if not description:
            return "Not specified"
        
        import re
        
        # Common patterns for contract duration
        patterns = [
            r'(\d+)\s*month[s]?\s*contract',
            r'(\d+)\s*week[s]?\s*contract',
            r'(\d+)\s*year[s]?\s*contract',
            r'contract\s*for\s*(\d+)\s*month[s]?',
            r'(\d+)-month\s*contract',
            r'(\d+)\s*to\s*(\d+)\s*month[s]?\s*contract'
        ]
        
        description_lower = description.lower()
        
        for pattern in patterns:
            match = re.search(pattern, description_lower)
            if match:
                return match.group(0)
        
        return "Not specified"
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize DataFrame"""
        # Remove duplicates based on title, company, and location
        df = df.drop_duplicates(subset=['title', 'company', 'location'])
        
        # Fill missing values
        df['description'] = df['description'].fillna('')
        df['contract_duration'] = df['contract_duration'].fillna('Not specified')
        
        # Standardize column order
        columns_order = [
            'title', 'vertical', 'state', 'platform', 'posting_date', 
            'contract_duration', 'company', 'location', 'description', 'url'
        ]
        
        # Reorder columns
        df = df.reindex(columns=[col for col in columns_order if col in df.columns])
        
        return df
    
    def save_to_excel(self, df: pd.DataFrame, filename: str = None) -> str:
        """Save DataFrame to Excel file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_scraping_results_{timestamp}.xlsx"
        
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'excel')
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Job_Data', index=False)
            
            # Summary sheets
            self._create_summary_sheets(df, writer)
        
        self.logger.info(f"Data saved to: {filepath}")
        return filepath
    
    def _create_summary_sheets(self, df: pd.DataFrame, writer):
        """Create summary analysis sheets"""
        # Vertical analysis
        vertical_summary = df.groupby('vertical').agg({
            'title': 'count',
            'state': lambda x: x.nunique(),
            'platform': lambda x: ', '.join(x.unique())
        }).rename(columns={'title': 'job_count', 'state': 'states_count'})
        
        vertical_summary.to_excel(writer, sheet_name='Vertical_Analysis')
        
        # State analysis
        state_summary = df.groupby('state').agg({
            'title': 'count',
            'vertical': lambda x: ', '.join(x.unique()),
            'platform': lambda x: ', '.join(x.unique())
        }).rename(columns={'title': 'job_count'})
        
        state_summary.to_excel(writer, sheet_name='State_Analysis')
        
        # Platform analysis
        platform_summary = df.groupby('platform').agg({
            'title': 'count',
            'vertical': lambda x: x.nunique(),
            'state': lambda x: x.nunique()
        }).rename(columns={'title': 'job_count', 'vertical': 'verticals_count', 'state': 'states_count'})
        
        platform_summary.to_excel(writer, sheet_name='Platform_Analysis')
