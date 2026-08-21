import google.generativeai as genai
from typing import Optional
from .config import settings
from .models import ResumeData, JobDescription, MatchResult

class GeminiClient:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.enabled = False
            print("⚠️ Gemini API key not found. Justification feature disabled.")
    
    def generate_justification(self, 
                              resume_data: ResumeData,
                              job_description: JobDescription,
                              match_result: MatchResult) -> Optional[str]:
        """Generate professional justification using Gemini"""
        if not self.enabled:
            return "Gemini API key not configured. Please add GEMINI_API_KEY to .env file."
        
        try:
            # Construct the prompt
            prompt = f"""
            You are an expert HR recruiter analyzing a resume against a job description.
            
            JOB DESCRIPTION:
            Title: {job_description.title or 'Not specified'}
            Company: {job_description.company or 'Not specified'}
            Requirements:
            {job_description.description}
            
            CANDIDATE RESUME:
            Name: {resume_data.candidate_name or 'Unknown'}
            Skills: {', '.join(resume_data.skills) if resume_data.skills else 'Not specified'}
            Experience: {resume_data.experience_years or 0} years
            Education: {', '.join([f"{e.degree} in {e.field} from {e.institution}" 
                                  for e in resume_data.education if e.degree or e.field])}
            Companies: {', '.join(resume_data.companies) if resume_data.companies else 'Not specified'}
            Certifications: {', '.join(resume_data.certifications) if resume_data.certifications else 'None'}
            
            MATCH ANALYSIS:
            Overall Match Score: {match_result.match_score}%
            Skill Match: {match_result.skill_match_score}%
            Experience Match: {match_result.experience_match_score}%
            Education Match: {match_result.education_match_score}%
            Matched Skills: {', '.join(match_result.matched_skills) if match_result.matched_skills else 'None'}
            Missing Skills: {', '.join(match_result.missing_skills) if match_result.missing_skills else 'None'}
            
            Please provide a professional hiring recommendation in 3-4 paragraphs:
            1. Overall assessment of the candidate's fit
            2. Key strengths and how they align with the role
            3. Any gaps or areas for improvement
            4. Final recommendation (Strongly Recommend / Recommend / Consider / Not Recommended)
            
            Keep the tone professional and constructive.
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "Could not generate justification. Please try again."
                
        except Exception as e:
            return f"Error generating justification: {str(e)}"
    
    def extract_jd_skills_with_gemini(self, job_description: str) -> list:
        """Use Gemini to extract skills from job description (fallback method)"""
        if not self.enabled:
            return []
        
        try:
            prompt = f"""
            Extract the key technical and soft skills from this job description.
            Return only a JSON array of skills.
            
            Job Description:
            {job_description}
            
            Skills:
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Parse the response to extract skills
                import json
                import re
                text = response.text
                # Try to find JSON array
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    try:
                        skills = json.loads(match.group())
                        return skills if isinstance(skills, list) else []
                    except:
                        pass
                # Fallback: split by newline
                skills = [s.strip() for s in text.split('\n') if s.strip()]
                return skills            
            return []
            
        except Exception as e:
            print(f"Error extracting skills with Gemini: {e}")
            return []

# Create global instance
gemini_client = GeminiClient()
