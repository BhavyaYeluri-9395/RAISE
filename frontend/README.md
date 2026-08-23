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

```text
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
                              └──────────────┘
