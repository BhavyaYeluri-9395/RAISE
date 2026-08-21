import fitz  # PyMuPDF
import re
from typing import Optional, List, Dict, Any
from .utils import clean_text

class PDFParser:
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return clean_text(text)
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def parse_pdf_bytes(file_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return clean_text(text)
        except Exception as e:
            raise Exception(f"Error parsing PDF bytes: {str(e)}")
    
    @staticmethod
    def parse_text_file(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return clean_text(f.read())
        except Exception as e:
            raise Exception(f"Error parsing text file: {str(e)}")
    
    @staticmethod
    def parse_text_bytes(file_bytes: bytes) -> str:
        """Extract text from TXT bytes"""
        try:
            text = file_bytes.decode('utf-8', errors='ignore')
            return clean_text(text)
        except Exception as e:
            raise Exception(f"Error parsing text bytes: {str(e)}")

def extract_sections(text: str) -> Dict[str, str]:
    """Extract different sections from resume text"""
    sections = {
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'certifications': '',
    }
    
    # Try to find section headers
    section_patterns = {
        'summary': r'(?:summary|profile|about|objective)\s*[:]?\s*(.*?)(?=(?:experience|education|skills|projects|certifications|$))',
        'experience': r'(?:experience|work experience|employment)\s*[:]?\s*(.*?)(?=(?:education|skills|projects|certifications|summary|$))',
        'education': r'(?:education|academic|qualifications)\s*[:]?\s*(.*?)(?=(?:experience|skills|projects|certifications|summary|$))',
        'skills': r'(?:skills|technical skills|core competencies)\s*[:]?\s*(.*?)(?=(?:experience|education|projects|certifications|summary|$))',
        'certifications': r'(?:certifications|certificates|licenses)\s*[:]?\s*(.*?)(?=(?:experience|education|skills|projects|summary|$))',
    }
    
    for section, pattern in section_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sections[section] = clean_text(match.group(1))
    
    return sections
