import re
import json
from typing import List, Optional
from datetime import datetime
import hashlib

def extract_email(text: str) -> Optional[str]:
    """Extract email from text using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else None

def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    # Various phone number patterns
    patterns = [
        r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(\d{3}\)\s?\d{3}-\d{4}'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return None

def extract_name(text: str) -> Optional[str]:
    """Extract candidate name using simple heuristic"""
    # Look for name in the first few lines
    lines = text.split('\n')[:5]
    
    # Common name patterns: "Name: John Doe" or "John Doe" at start
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for "Name:" prefix
        if re.match(r'^Name:\s*', line, re.IGNORECASE):
            return re.sub(r'^Name:\s*', '', line).strip()
        
        # Check for line with 2-3 words (probable name)
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words):
            # Avoid common headers
            if not any(word.lower() in ['resume', 'curriculum', 'vitae', 'contact'] 
                      for word in words):
                return line.strip()
    
    return None

def extract_company_names(text: str) -> List[str]:
    """Extract company names using common patterns"""
    companies = []
    
    # Common patterns for company names
    patterns = [
        r'(?:at|@)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
        r'(?:worked\s+at|employed\s+at|joined)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        companies.extend(matches)
    
    # Remove duplicates
    return list(set(companies))

def extract_years_of_experience(text: str) -> Optional[float]:
    """Extract total years of experience"""
    # Look for patterns like "5 years", "5+ years", "5-7 years"
    patterns = [
        r'(\d+)\+?\s*(?:-?\s*\d+)?\s*years?\s*(?:of)?\s*experience',
        r'experience\s*[:|:]\s*(\d+)\+?\s*(?:-?\s*\d+)?\s*years?',
        r'(\d+)\+?\s*years?\s*working',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                # Extract the first number
                numbers = re.findall(r'\d+', match.group())
                if numbers:
                    return float(numbers[0])
            except:
                pass
    
    return None

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s.,;!?-]', '', text)
    return text.strip()

def generate_session_id() -> str:
    """Generate unique session ID"""
    timestamp = datetime.now().isoformat()
    return hashlib.md5(timestamp.encode()).hexdigest()[:12]

def parse_experience_string(exp_str: str) -> float:
    """Parse experience string like '5 years' to float"""
    try:
        # Extract numbers from string
        numbers = re.findall(r'(\d+\.?\d*)', exp_str)
        if numbers:
            return float(numbers[0])
    except:
        pass
    return 0.0

def estimate_experience_from_work_history(text: str) -> float:
    """Estimate experience from work history dates"""
    # Look for date patterns like "Jan 2020 - Dec 2022"
    date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})'
    years = re.findall(date_pattern, text, re.IGNORECASE)
    
    if len(years) >= 2:
        try:
            years = [int(y) for y in years]
            total_years = max(years) - min(years)
            return float(total_years)
        except:
            pass
    
    return 0.0
