from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import uuid

from .models import (
    UploadRequest, UploadResponse, AnalysisResponse,
    JobDescription, ResumeData, MatchResult, ShortlistRequest, ShortlistResponse
)
from .parser import PDFParser
from .extractor import ResumeExtractor
from .matcher import ResumeMatcher
from .gemini import gemini_client
from .database import db
from .utils import generate_session_id

app = FastAPI(title="Smart Resume Screener", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
extractor = ResumeExtractor()
matcher = ResumeMatcher()

@app.get("/")
async def root():
    return {
        "message": "Smart Resume Screener API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/analyze", response_model=UploadResponse)
async def analyze_resume(
    job_description: str = Form(...),
    job_title: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """
    Analyze a single resume against a job description
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        allowed_extensions = [".pdf", ".txt"]
        file_extension = "." + file.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Parse file based on type
        if file_extension == ".pdf":
            resume_text = PDFParser.parse_pdf_bytes(file_content)
        else:  # .txt
            resume_text = PDFParser.parse_text_bytes(file_content)
        
        # Extract data from resume
        extracted_data = extractor.extract_all(resume_text)
        resume_data = ResumeData(**extracted_data)
        
        # Create job description object
        jd = JobDescription(
            title=job_title or "Software Engineer",
            company=company_name or "Unknown Company",
            description=job_description,
            required_skills=matcher.extract_jd_skills(job_description),
            min_experience=5.0,  # Default, could be extracted from JD
        )
        
        # Match resume with job description
        match_result = matcher.match(resume_data, jd)
        
        # Generate justification using Gemini
        justification = gemini_client.generate_justification(
            resume_data, jd, match_result
        )
        match_result.justification = justification
        
        # Generate session ID
        session_id = generate_session_id()
        
        # Save to database
        analysis_id = db.save_analysis(
            job_description=jd,
            resume_data=resume_data,
            match_result=match_result,
            session_id=session_id
        )
        
        # Create response
        analysis_response = AnalysisResponse(
            job_description=jd,
            resume_data=resume_data,
            match_result=match_result,
            processed_at=datetime.now()
        )
        
        return UploadResponse(
            success=True,
            message="Resume analyzed successfully",
            analysis_id=analysis_id,
            analysis=analysis_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/shortlist", response_model=ShortlistResponse)
async def shortlist_candidates(
    job_description: str = Form(...),
    job_title: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    threshold: Optional[float] = Form(0.70),
    files: List[UploadFile] = File(...)
):
    """
    Analyze multiple resumes and return shortlisted candidates
    """
    try:
        candidates = []
        session_id = generate_session_id()
        
        # Process each file
        for file in files:
            # Skip empty files
            if not file.filename:
                continue
                
            try:
                # Read and parse file
                file_content = await file.read()
                file_extension = "." + file.filename.split(".")[-1].lower()
                
                if file_extension == ".pdf":
                    resume_text = PDFParser.parse_pdf_bytes(file_content)
                else:
                    resume_text = PDFParser.parse_text_bytes(file_content)
                
                # Extract data
                extracted_data = extractor.extract_all(resume_text)
                resume_data = ResumeData(**extracted_data)
                
                # Create JD
                jd = JobDescription(
                    title=job_title or "Software Engineer",
                    company=company_name or "Unknown Company",
                    description=job_description,
                    required_skills=matcher.extract_jd_skills(job_description),
                    min_experience=5.0,
                )
                
                # Match
                match_result = matcher.match(resume_data, jd)
                
                # Generate justification
                justification = gemini_client.generate_justification(
                    resume_data, jd, match_result
                )
                match_result.justification = justification
                
                # Save to database
                db.save_analysis(
                    job_description=jd,
                    resume_data=resume_data,
                    match_result=match_result,
                    session_id=session_id
                )
                
                # Add to candidates list
                candidates.append(AnalysisResponse(
                    job_description=jd,
                    resume_data=resume_data,
                    match_result=match_result,
                    processed_at=datetime.now()
                ))
                
            except Exception as e:
                print(f"Error processing {file.filename}: {e}")
                continue
        
        # Shortlist based on threshold
        shortlisted = [c for c in candidates if c.match_result.match_score >= threshold * 100]
        
        # Sort shortlisted by score
        shortlisted.sort(key=lambda x: x.match_result.match_score, reverse=True)
        
        # Assign ranks
        for idx, candidate in enumerate(shortlisted, 1):
            candidate.match_result.rank = idx
        
        return ShortlistResponse(
            success=True,
            candidates=shortlisted,
            total_candidates=len(candidates),
            shortlisted_count=len(shortlisted)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses/{session_id}")
async def get_analyses(session_id: str):
    """
    Get all analyses for a session
    """
    analyses = db.get_analyses_by_session(session_id)
    if not analyses:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "analyses": analyses}

@app.get("/shortlisted/{session_id}")
async def get_shortlisted(session_id: str):
    """
    Get shortlisted candidates for a session
    """
    candidates = db.get_shortlisted_candidates(session_id)
    return {"session_id": session_id, "shortlisted": candidates}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gemini_available": gemini_client.enabled
    }
