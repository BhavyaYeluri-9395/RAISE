import numpy as np
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from .models import ResumeData, JobDescription, MatchResult
from .config import settings

class ResumeMatcher:
    def __init__(self):
        # Load sentence transformer model
        self.model = SentenceTransformer(settings.MODEL_NAME)
        self.skill_weight = settings.SKILL_WEIGHT
        self.experience_weight = settings.EXPERIENCE_WEIGHT
        self.education_weight = settings.EDUCATION_WEIGHT
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        embeddings = self.model.encode([text1, text2])
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)
    
    def calculate_skill_match(self, resume_skills: List[str], jd_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """Calculate skill match percentage"""
        if not jd_skills:
            return 0.0, [], resume_skills
        
        # Normalize skills
        resume_skills_lower = [s.lower() for s in resume_skills]
        jd_skills_lower = [s.lower() for s in jd_skills]
        
        # Find matched skills
        matched_skills = []
        missing_skills = []
        
        for jd_skill in jd_skills_lower:
            # Check if JD skill is in resume skills (exact or partial match)
            matched = False
            for resume_skill in resume_skills_lower:
                if jd_skill in resume_skill or resume_skill in jd_skill:
                    matched_skills.append(jd_skill)
                    matched = True
                    break
            if not matched:
                missing_skills.append(jd_skill)
        
        # Calculate match score
        if jd_skills:
            match_score = (len(matched_skills) / len(jd_skills)) * 100
        else:
            match_score = 0.0
        
        return min(match_score, 100.0), matched_skills, missing_skills
    
    def calculate_experience_match(self, resume_exp: float, jd_exp: float) -> float:
        """Calculate experience match percentage"""
        if jd_exp == 0:
            return 100.0  # No experience required
        
        if resume_exp >= jd_exp:
            return 100.0
        else:
            # Percentage of required experience
            return min((resume_exp / jd_exp) * 100, 100.0)
    
    def calculate_education_match(self, resume_education: List, jd_education: List) -> float:
        """Calculate education match percentage"""
        if not jd_education:
            return 100.0
        
        # Simple matching - check if any education matches requirements
        education_text = " ".join([e.field or e.degree or "" for e in resume_education]).lower()
        
        matched = 0
        for req in jd_education:
            if req.lower() in education_text:
                matched += 1
        
        if jd_education:
            return (matched / len(jd_education)) * 100
        return 0.0
    
    def extract_jd_skills(self, job_description: str) -> List[str]:
        """Extract skills from job description using skill taxonomy"""
        from .extractor import ResumeExtractor
        extractor = ResumeExtractor()
        return extractor.extract_skills(job_description)
    
    def match(self, resume_data: ResumeData, job_description: JobDescription) -> MatchResult:
        """Compute match score between resume and job description"""
        
        # Extract skills from job description if not provided
        if not job_description.required_skills:
            job_description.required_skills = self.extract_jd_skills(job_description.description)
        
        # 1. Calculate skill match
        skill_match_score, matched_skills, missing_skills = self.calculate_skill_match(
            resume_data.skills,
            job_description.required_skills
        )
        
        # 2. Calculate experience match
        experience_match_score = self.calculate_experience_match(
            resume_data.experience_years or 0,
            job_description.min_experience or 0
        )
        
        # 3. Calculate education match
        education_match_score = self.calculate_education_match(
            resume_data.education,
            job_description.education_requirements or []
        )
        
        # 4. Compute overall match score (weighted average)
        match_score = (
            skill_match_score * self.skill_weight +
            experience_match_score * self.experience_weight +
            education_match_score * self.education_weight
        )
        
        # 5. Determine if shortlisted
        is_shortlisted = match_score >= (settings.SHORTLIST_THRESHOLD * 100)
        
        return MatchResult(
            match_score=round(match_score, 2),
            skill_match_score=round(skill_match_score, 2),
            experience_match_score=round(experience_match_score, 2),
            education_match_score=round(education_match_score, 2),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            is_shortlisted=is_shortlisted,
            justification=None  # Will be filled by Gemini
        )
