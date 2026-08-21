from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class Education(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None

class ResumeData(BaseModel):
    # Candidate info
    candidate_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    # Extracted data
    skills: List[str] = []
    experience_years: Optional[float] = None
    education: List[Education] = []
    companies: List[str] = []
    certifications: List[str] = []
    
    # Raw text
    raw_text: Optional[str] = None
    
    # Metadata
    processed_at: Optional[datetime] = None

class MatchResult(BaseModel):
    # Scores
    match_score: float  # 0-100
    skill_match_score: float
    experience_match_score: float
    education_match_score: float
    
    # Details
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    justification: Optional[str] = None
    
    # Decision
    is_shortlisted: bool = False
    rank: Optional[int] = None

class JobDescription(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: str
    required_skills: Optional[List[str]] = None
    min_experience: Optional[float] = None
    education_requirements: Optional[List[str]] = None

class AnalysisResponse(BaseModel):
    job_description: JobDescription
    resume_data: ResumeData
    match_result: MatchResult
    processed_at: datetime

# Request/Response models for API
class UploadRequest(BaseModel):
    job_description: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    message: str
    analysis_id: Optional[int] = None
    analysis: Optional[AnalysisResponse] = None

class ShortlistRequest(BaseModel):
    job_description: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    threshold: Optional[float] = 0.70

class ShortlistResponse(BaseModel):
    success: bool
    candidates: List[AnalysisResponse]
    total_candidates: int
    shortlisted_count: int
