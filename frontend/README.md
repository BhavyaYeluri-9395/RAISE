# RAISE — Resume Analysis & Intelligent Screening Engine

RAISE is an AI-assisted resume analysis and candidate screening platform that helps recruiters evaluate candidates against job requirements and helps individuals understand how well their resume matches a target role.

## Features

### Recruiter

- Secure recruiter registration and login
- Recruiter dashboard
- Create screening sessions
- Enter job title, company and job description
- Upload multiple PDF/TXT resumes
- Extract candidate information automatically
- Skill matching
- Experience matching
- Education matching
- Overall candidate match score
- Configurable shortlist threshold
- Candidate ranking
- AI-generated recruitment assessment
- Screening history
- View previous screening results

### Individual

- Individual registration and login
- Individual dashboard
- Upload personal resume
- Enter target job description
- Analyze resume against a target role
- View match score
- View skill, experience and education scores
- View AI-generated assessment
- Maintain analysis history

---

# System Architecture

RAISE follows a client-server architecture.

                         ┌─────────────────────────┐
                         │       RAISE USER        │
                         │ Recruiter / Individual  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     React + Vite        │
                         │       Frontend          │
                         │                         │
                         │ Authentication          │
                         │ Dashboards              │
                         │ Resume Upload           │
                         │ Screening UI             │
                         │ Results & History       │
                         └────────────┬────────────┘
                                      │
                                REST API
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │       FastAPI           │
                         │        Backend          │
                         │                         │
                         │ Authentication          │
                         │ Resume Processing       │
                         │ Matching                │
                         │ Screening               │
                         │ History                 │
                         └────────────┬────────────┘
                                      │
             ┌────────────────────────┼──────────────────────┐
             │                        │                      │
             ▼                        ▼                      ▼
     ┌──────────────┐       ┌─────────────────┐     ┌──────────────┐
     │ PyMuPDF      │       │ Resume Matcher  │     │    Gemini    │
     │              │       │                 │     │     LLM      │
     │ PDF/TXT      │       │ Skills          │     │              │
     │ extraction   │       │ Experience      │     │ Assessment   │
     │              │       │ Education       │     │              │
     └──────────────┘       └─────────────────┘     └──────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │    SQLite    │
                              │              │
                              │ Users        │
                              │ Analyses     │
                              │ Sessions     │
                              │ Results      │
                              └──────────────



Technology Stack
Frontend
React
Vite
React Router
Axios
Lucide React
CSS
Backend
Python
FastAPI
Pydantic
PyMuPDF
spaCy
Sentence Transformers
NumPy
SQLite
AI / LLM
Google Gemini API
Gemini is used for recruiter-facing natural-language assessment and recommendations.
Authentication
JWT-based authentication
Password hashing
Role-based access for recruiter and individual users
Deployment
Frontend: Render Static Site
Backend: Render Web Service
Source Code: GitHub
Resume Processing Pipeline

The resume processing workflow is:

Resume Upload
      ↓
PDF/TXT Parsing
      ↓
Raw Resume Text
      ↓
Information Extraction
      ↓
Candidate Profile
      │
      ├── Name
      ├── Email
      ├── Phone
      ├── Skills
      ├── Experience
      ├── Education
      ├── Companies
      └── Certifications
      ↓
Job Description Processing
      ↓
Requirement Extraction
      ↓
Candidate Matching
      ↓
Weighted Match Score
      ↓
Shortlist Decision
      ↓
Gemini Assessment
      ↓
Database Storage
      ↓
Results / History
Candidate Matching

RAISE calculates the candidate's overall match using three major components:

Skills: 50%
Experience: 30%
Education: 20%

The overall score is calculated as:

Overall Score =
    Skill Score × 0.50
  + Experience Score × 0.30
  + Education Score × 0.20

The recruiter can select a shortlist threshold, such as 70%.

Candidates meeting or exceeding the threshold are considered shortlisted.

LLM Usage

Gemini is used to provide an explainable natural-language assessment after the structured matching stage.

The application provides the LLM with:

Candidate information
Extracted skills
Experience
Education
Job description
Required skills
Match scores
Matching strengths
Missing skills

The LLM then generates a recruiter-facing explanation.

Prompt Structure

A representative prompt structure is:

You are an AI recruitment assistant.

Analyze the candidate against the provided job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
Name: {candidate_name}
Skills: {skills}
Experience: {experience_years}
Education: {education}
Companies: {companies}
Certifications: {certifications}

MATCHING RESULTS:
Overall Match: {match_score}%
Skill Match: {skill_match_score}%
Experience Match: {experience_match_score}%
Education Match: {education_match_score}%

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Provide a professional recruitment assessment.

Include:

1. Overall fit
2. Key strengths
3. Relevant technical skills
4. Experience alignment
5. Education alignment
6. Areas for improvement
7. Final recommendation

Base the assessment only on the information provided.
Do not invent experience, skills, qualifications, or achievements.
Keep the response concise and useful to a recruiter.

The assignment itself recommends using an LLM for semantic comparison and gives the example of comparing a resume with a job description and providing a fit rating with justification.

Why LLM and deterministic matching are both used

RAISE separates numerical scoring from natural-language explanation.

The structured matching system calculates reproducible scores using skills, experience and education.

Gemini then converts the structured results into a readable recruitment assessment.

This separation makes the scoring process easier to understand while still providing an AI-generated explanation.

Authentication Flow
User
 ↓
Register
 ↓
Password Hashing
 ↓
SQLite users table
 ↓
Login
 ↓
JWT Access Token
 ↓
Protected Routes
 ↓
Role Validation
 ↓
Recruiter / Individual Dashboard
API Overview
Authentication
POST /auth/register
POST /auth/login
GET  /auth/me
Resume Analysis
POST /analyze

Analyzes a single resume.

Batch Screening
POST /shortlist

Analyzes multiple resumes and returns ranked candidates.

Results
GET /analyses/{session_id}
GET /shortlisted/{session_id}
History
GET /screening-history
Health
GET /health
