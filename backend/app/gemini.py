from google import genai
from typing import Optional

from .config import settings
from .models import ResumeData, JobDescription, MatchResult


class GeminiClient:

    def __init__(self):
        self.enabled = False
        self.client = None

        if not settings.GEMINI_API_KEY:
            print("⚠️ Gemini API key not found")
            return

        try:
            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY
            )

            self.enabled = True

            print("✅ Gemini API initialized successfully")

        except Exception as e:
            print(f"❌ Gemini initialization error: {e}")

    def generate_justification(
        self,
        resume_data: ResumeData,
        job_description: JobDescription,
        match_result: MatchResult
    ) -> Optional[str]:

        if not self.enabled or not self.client:
            return "Gemini API is not configured."

        prompt = f"""
You are an expert HR recruiter.

Analyze the candidate resume against the job description.

JOB DESCRIPTION:
Title: {job_description.title or 'Not specified'}
Company: {job_description.company or 'Not specified'}

Requirements:
{job_description.description[:1500]}

CANDIDATE RESUME:
Name: {resume_data.candidate_name or 'Unknown'}

Skills:
{', '.join(resume_data.skills[:15]) if resume_data.skills else 'Not specified'}

Experience:
{resume_data.experience_years or 0} years

Education:
{', '.join(
    [
        f"{e.degree or ''} in {e.field or ''}"
        for e in resume_data.education
        if e.degree or e.field
    ]
)}

Companies:
{', '.join(resume_data.companies[:5])
    if resume_data.companies
    else 'Not specified'}

MATCH ANALYSIS:
Overall Match: {match_result.match_score}%
Skill Match: {match_result.skill_match_score}%
Experience Match: {match_result.experience_match_score}%
Education Match: {match_result.education_match_score}%

Matched Skills:
{', '.join(match_result.matched_skills[:10])
    if match_result.matched_skills
    else 'None'}

Missing Skills:
{', '.join(match_result.missing_skills[:10])
    if match_result.missing_skills
    else 'None'}

Provide a concise professional recommendation.

Include:

1. Overall fit assessment
2. Key strengths
3. Areas for improvement
4. Final recommendation:
   Strongly Recommend / Recommend / Consider / Not Recommended

Keep the response clear and professional.
"""

        try:
            print("🤖 Sending request to Gemini...")

            response = self.client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

            if response and response.text:
                print("✅ Gemini response received")
                return response.text.strip()

            print("⚠️ Gemini returned an empty response")
            return "Could not generate justification."

        except Exception as e:
            print(f"❌ Gemini generation error: {e}")
            return f"Gemini error: {str(e)}"


gemini_client = GeminiClient()