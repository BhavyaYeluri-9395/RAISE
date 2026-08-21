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
