# Create README.md with basic content
cat > README.md << 'EOF'
# Smart Resume Screener

Intelligently parse resumes, extract skills, and match them with job descriptions using AI.

## 🚀 Features

- 📄 **PDF/TXT Resume Parsing** - Extract text from resumes
- 🎯 **Smart Skill Extraction** - Uses skill taxonomy database
- 🤖 **Semantic Matching** - AI-powered match scoring
- 📊 **Interactive Dashboard** - Visual analytics and rankings
- 💾 **Database Storage** - SQLite for parsed resumes
- 📝 **AI Justification** - Gemini-powered recommendations

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: Streamlit
- **AI Models**: spaCy, sentence-transformers, Google Gemini
- **Database**: SQLite
- **PDF Parsing**: PyMuPDF

## 📋 How It Works

1. Upload a job description
2. Upload one or more resumes (PDF/TXT)
3. The system extracts skills, experience, and education
4. Semantic matching computes a match score
5. AI generates professional justification
6. View results in an interactive dashboard

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Gemini API Key (free from Google AI Studio)


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

Prompt Structure:
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

Why LLM and deterministic matching are both used?
RAISE separates numerical scoring from natural-language explanation.
The structured matching system calculates reproducible scores using skills, experience and education.
Gemini then converts the structured results into a readable recruitment assessment.
This separation makes the scoring process easier to understand while still providing an AI-generated explanation.


1. Analyzes a single resume.

Batch Screening
POST /shortlist

2. Analyzes multiple resumes and returns ranked candidates.

Results
GET /analyses/{session_id}
GET /shortlisted/{session_id}

History
GET /screening-history

Health
GET /health



**Deployment** :

The application is deployed as two services.

Frontend
React/Vite application deployed as a Render Static Site.
https://raise-frontend.onrender.com

Backend
FastAPI application deployed as a Render Web Service.
https://raise-api.onrender.com

### Installation

```bash
# Clone the repository
git clone https://github.com/BhavyaYeluri-9395/smart-resume-screener.git
cd smart-resume-screener

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
python -m spacy download en_core_web_sm

# Set up environment variables
echo GEMINI_API_KEY=your_api_key_here > .env

# Run the application
# Terminal 1 - Backend:
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend:
streamlit run frontend/app.py
