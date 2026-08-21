import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager
from .models import ResumeData, MatchResult, AnalysisResponse, JobDescription

class Database:
    def __init__(self, db_path: str = "./data/resumes.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create resumes table with correct columns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT,
                    job_description TEXT,
                    company_name TEXT,
                    
                    -- Candidate Information
                    candidate_name TEXT,
                    email TEXT,
                    phone TEXT,
                    
                    -- Extracted Data (stored as JSON)
                    skills TEXT,
                    experience_years REAL,
                    education TEXT,
                    companies TEXT,
                    certifications TEXT,
                    
                    -- Matching Results
                    match_score REAL,
                    skill_match_score REAL,
                    experience_match_score REAL,
                    education_match_score REAL,
                    justification TEXT,
                    is_shortlisted INTEGER DEFAULT 0,
                    
                    -- Raw Data
                    raw_resume_text TEXT,
                    
                    -- Metadata
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_match_score 
                ON resumes(match_score)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_shortlisted 
                ON resumes(is_shortlisted)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_processed_at 
                ON resumes(processed_at DESC)
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_analysis(self, 
                     job_description: JobDescription,
                     resume_data: ResumeData,
                     match_result: MatchResult,
                     session_id: Optional[str] = None) -> int:
        """Save analysis results to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert education to JSON
            education_json = json.dumps([{
                'degree': e.degree,
                'field': e.field,
                'institution': e.institution,
                'year': e.year
            } for e in resume_data.education]) if resume_data.education else json.dumps([])
            
            cursor.execute("""
                INSERT INTO resumes (
                    job_title, job_description, company_name,
                    candidate_name, email, phone,
                    skills, experience_years, education, companies, certifications,
                    match_score, skill_match_score, experience_match_score, 
                    education_match_score, justification, is_shortlisted,
                    raw_resume_text, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_description.title,
                job_description.description,
                job_description.company,
                resume_data.candidate_name,
                resume_data.email,
                resume_data.phone,
                json.dumps(resume_data.skills),
                resume_data.experience_years,
                education_json,
                json.dumps(resume_data.companies),
                json.dumps(resume_data.certifications),
                match_result.match_score,
                match_result.skill_match_score,
                match_result.experience_match_score,
                match_result.education_match_score,
                match_result.justification,
                1 if match_result.is_shortlisted else 0,
                resume_data.raw_text,
                session_id
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve analysis by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resumes WHERE id = ?", (analysis_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_analyses_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all analyses for a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM resumes WHERE session_id = ? ORDER BY match_score DESC",
                (session_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_shortlisted_candidates(self, session_id: str) -> List[Dict[str, Any]]:
        """Get shortlisted candidates for a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM resumes WHERE session_id = ? AND is_shortlisted = 1 ORDER BY match_score DESC",
                (session_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

# Create a global database instance
db = Database()