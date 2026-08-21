import re
import spacy
from typing import List, Optional, Dict, Any
from .models import Education
from .utils import extract_email, extract_phone, extract_name, extract_company_names, clean_text

class ResumeExtractor:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Try to load skills package
        try:
            from skills import SkillLibrary
            self.skill_library = SkillLibrary()
            self.use_skills_package = True
        except:
            self.use_skills_package = False
            print("Skills package not found. Using fallback skill list.")
            self._init_fallback_skills()
    
    def _init_fallback_skills(self):
        """Initialize fallback skill list if skills package not available"""
        self.fallback_skills = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
            'swift', 'kotlin', 'php', 'html', 'css', 'sql', 'nosql', 'mongodb', 'postgresql',
            'mysql', 'oracle', 'redis', 'elasticsearch', 'graphql', 'rest', 'soap',
            # Frameworks
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'spring boot',
            'fastapi', 'laravel', 'rails', 'asp.net', 'jquery', 'bootstrap', 'tailwind',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
            'ci/cd', 'terraform', 'ansible', 'prometheus', 'grafana', 'elk', 'splunk',
            # Data & ML
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
            'data analysis', 'big data', 'hadoop', 'spark', 'airflow', 'etl',
            # Other
            'agile', 'scrum', 'project management', 'leadership', 'communication',
            'problem solving', 'critical thinking', 'teamwork', 'time management',
        ]
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills using skills package or fallback"""
        found_skills = set()
        text_lower = text.lower()
        
        if self.use_skills_package:
            # Use skills package
            try:
                # Get all skills from the library
                all_skills = self.skill_library.get_skills()
                for skill in all_skills:
                    if skill.lower() in text_lower:
                        found_skills.add(skill)
                    elif len(skill.split()) > 1:
                        pattern = r'\b' + skill.lower().replace(' ', r'\s+') + r'\b'
                        if re.search(pattern, text_lower):
                            found_skills.add(skill)
            except:
                # Fallback to manual extraction
                self.use_skills_package = False
                return self.extract_skills(text)
        else:
            # Use fallback skill list
            for skill in self.fallback_skills:
                if skill.lower() in text_lower:
                    found_skills.add(skill)
                elif len(skill.split()) > 1:
                    pattern = r'\b' + skill.lower().replace(' ', r'\s+') + r'\b'
                    if re.search(pattern, text_lower):
                        found_skills.add(skill)
        
        # Also extract using spaCy NER
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                if 3 <= len(ent.text) <= 15 and ent.text.upper() in text.upper():
                    found_skills.add(ent.text)
        
        return list(found_skills)[:50]
    
    def extract_education(self, text: str) -> List[Education]:
        """Extract education information"""
        education_list = []
        
        edu_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma',
            'b.tech', 'm.tech', 'mba', 'b.e.', 'm.e.', 'bsc', 'msc', 'b.a.', 'm.a.',
            'engineering', 'computer science', 'information technology',
            'business administration', 'management'
        ]
        
        sections = re.split(r'\n\s*\n', text)
        for section in sections:
            section_lower = section.lower()
            if any(keyword in section_lower for keyword in edu_keywords):
                degree = None
                field = None
                institution = None
                year = None
                
                degree_patterns = [
                    r'(bachelor|master|phd|doctorate)\s+of\s+([a-zA-Z\s]+)',
                    r'(b\.tech|m\.tech|mba|b\.e\.|m\.e\.|bsc|msc)\s+in\s+([a-zA-Z\s]+)',
                    r'(b\.a\.|m\.a\.)\s+in\s+([a-zA-Z\s]+)',
                    r'(bachelor|master)\'?s?\s+degree\s+in\s+([a-zA-Z\s]+)',
                ]
                
                for pattern in degree_patterns:
                    match = re.search(pattern, section, re.IGNORECASE)
                    if match:
                        degree = match.group(1).strip()
                        field = match.group(2).strip() if len(match.groups()) > 1 else None
                        break
                
                # Extract institution
                inst_patterns = [
                    r'(?:from|at|university of|college of)\s+([A-Z][a-zA-Z\s]+(?:University|College|Institute|School))',
                    r'(?:[A-Z][a-zA-Z\s]+(?:University|College|Institute|School))',
                ]
                for pattern in inst_patterns:
                    match = re.search(pattern, section, re.IGNORECASE)
                    if match:
                        institution = match.group(1).strip() if match.lastindex else match.group(0).strip()
                        break
                
                # Extract year
                year_pattern = r'\b(19|20)\d{2}\b'
                years = re.findall(year_pattern, section)
                if years:
                    year = years[0]
                
                if degree or field or institution:
                    education_list.append(Education(
                        degree=degree,
                        field=field,
                        institution=institution,
                        year=year
                    ))
        
        return education_list
    
    def extract_experience_years(self, text: str) -> float:
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*(?:-?\s*\d+)?\s*years?\s*(?:of)?\s*(?:experience|work)',
            r'(?:experience|work)\s*(?:of)?\s*(\d+)\+?\s*(?:-?\s*\d+)?\s*years?',
            r'(\d+)\+?\s*(?:-?\s*\d+)?\s*yrs?\s*(?:of)?\s*exp',
            r'(\d+)\s*\+\s*years?\s*experience',
            r'over\s*(\d+)\s*years?\s*experience',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    numbers = re.findall(r'\d+', matches[0])
                    if numbers:
                        return float(numbers[0])
                except:
                    pass
        
        # Estimate from work history dates
        date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*(\d{4})'
        years = re.findall(date_pattern, text, re.IGNORECASE)
        if len(years) >= 2:
            try:
                years = [int(y) for y in years]
                total = max(years) - min(years)
                if 1 <= total <= 50:
                    return float(total)
            except:
                pass
        
        return 0.0
    
    def extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        cert_keywords = [
            'certified', 'certification', 'certificate', 'licensed',
            'aws certified', 'azure certified', 'gcp certified',
            'pmp', 'scrum master', 'agile', 'six sigma', 'itil',
            'ccna', 'ccnp', 'mcsd', 'mct', 'cissp', 'ceh', 'oscp'
        ]
        
        patterns = [
            r'([A-Z][a-zA-Z\s]+)\s+certification',
            r'certification\s+in\s+([A-Za-z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+certified',
            r'certified\s+([A-Za-z\s]+)',
            r'(AWS|Azure|GCP|PMP|CCNA|CCNP|CISSP|CEH|OSCP)\s+certified',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cert = clean_text(match)
                if cert and len(cert) > 2:
                    certifications.append(cert.title())
        
        # Also check for explicit certifications
        lines = text.split('\n')
        for line in lines:
            line_clean = line.strip()
            if any(keyword.lower() in line_clean.lower() for keyword in cert_keywords):
                if len(line_clean) > 3 and not line_clean.startswith(('•', '-', '*')):
                    certifications.append(clean_text(line_clean))
        
        return list(set(certifications))[:20]
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """Extract all information from resume text"""
        return {
            'candidate_name': extract_name(text),
            'email': extract_email(text),
            'phone': extract_phone(text),
            'skills': self.extract_skills(text),
            'experience_years': self.extract_experience_years(text),
            'education': self.extract_education(text),
            'companies': extract_company_names(text),
            'certifications': self.extract_certifications(text),
            'raw_text': text
        }