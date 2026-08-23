from app.gemini import gemini_client
from app.models import ResumeData, JobDescription, MatchResult


print("\n==============================")
print("REAL GEMINI JUSTIFICATION TEST")
print("==============================")

print("Gemini enabled:", gemini_client.enabled)

if not gemini_client.enabled:
    print("❌ Gemini is not enabled.")
    raise SystemExit(1)


resume = ResumeData(
    candidate_name="Test Candidate",
    email="test@example.com",
    phone="1234567890",
    skills=[
        "Python",
        "Java",
        "SQL",
        "Machine Learning",
        "Git"
    ],
    experience_years=2,
    education=[],
    companies=[],
    certifications=[],
    raw_text="Python developer with experience in machine learning and SQL."
)


job = JobDescription(
    title="Software Engineer",
    company="Test Company",
    description="""
    We are looking for a Software Engineer with experience in Python,
    SQL, machine learning and Git.
    The candidate should have at least 2 years of experience.
    """,
    required_skills=[
        "Python",
        "SQL",
        "Machine Learning",
        "Git"
    ],
    min_experience=2.0
)


match = MatchResult(
    match_score=90.0,
    skill_match_score=100.0,
    experience_match_score=100.0,
    education_match_score=50.0,
    matched_skills=[
        "python",
        "sql",
        "machine learning",
        "git"
    ],
    missing_skills=[],
    is_shortlisted=True,
    justification=None
)


print("\nSending real resume/JD data to Gemini...")

result = gemini_client.generate_justification(
    resume,
    job,
    match
)

print("\n==============================")
print("RESULT")
print("==============================")

print(result)