import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

def random_delay(min_seconds=1, max_seconds=3):
    """Add random delay to avoid being blocked"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-\.\,\(\)]', '', text)
    
    return text

def extract_date_from_text(text: str) -> str:
    """Extract and normalize date from job posting text"""
    if not text:
        return ""
    
    # Common patterns for job posting dates
    patterns = [
        r'(\d{1,2})\s+(day|days)\s+ago',
        r'(\d{1,2})\s+(hour|hours)\s+ago',
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        r'(\d{4})-(\d{1,2})-(\d{1,2})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            if 'day' in pattern:
                days_ago = int(match.group(1))
                date = datetime.now() - timedelta(days=days_ago)
                return date.strftime('%Y-%m-%d')
            elif 'hour' in pattern:
                hours_ago = int(match.group(1))
                date = datetime.now() - timedelta(hours=hours_ago)
                return date.strftime('%Y-%m-%d')
    
    return datetime.now().strftime('%Y-%m-%d')

def get_us_states() -> List[str]:
    """Return list of US states for filtering"""
    return [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
        'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
        'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
        'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
        'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
        'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
        'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
        'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
        'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
        'West Virginia', 'Wisconsin', 'Wyoming'
    ]
