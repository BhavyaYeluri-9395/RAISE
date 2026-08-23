import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

from .models import ResumeData, JobDescription, MatchResult
from .config import settings


class ResumeMatcher:

    def __init__(self):
        # Load sentence transformer model
        self.model = SentenceTransformer(settings.MODEL_NAME)

        self.skill_weight = settings.SKILL_WEIGHT
        self.experience_weight = settings.EXPERIENCE_WEIGHT
        self.education_weight = settings.EDUCATION_WEIGHT

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""

        embeddings = self.model.encode([text1, text2])

        similarity = np.dot(
            embeddings[0],
            embeddings[1]
        ) / (
            np.linalg.norm(embeddings[0]) *
            np.linalg.norm(embeddings[1])
        )

        return float(similarity)

    def calculate_skill_match(
        self,
        resume_skills: List[str],
        jd_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate skill match percentage."""

        # Normalize and deduplicate resume skills
        resume_normalized = list(dict.fromkeys(
            skill.strip().lower()
            for skill in resume_skills
            if skill and skill.strip()
        ))

        # Normalize and deduplicate JD skills
        jd_normalized = list(dict.fromkeys(
            skill.strip().lower()
            for skill in jd_skills
            if skill and skill.strip()
        ))

        if not jd_normalized:
            return 100.0, [], []

        matched_skills = []
        missing_skills = []

        for jd_skill in jd_normalized:

            matched = False

            for resume_skill in resume_normalized:

                if (
                    jd_skill == resume_skill
                    or jd_skill in resume_skill
                    or resume_skill in jd_skill
                ):
                    matched = True
                    break

            if matched:
                matched_skills.append(jd_skill)
            else:
                missing_skills.append(jd_skill)

        match_score = (
            len(matched_skills) / len(jd_normalized)
        ) * 100

        return (
            round(min(match_score, 100.0), 2),
            matched_skills,
            missing_skills
        )

    def calculate_experience_match(
        self,
        resume_exp: float,
        jd_exp: float
    ) -> float:
        """Calculate experience match percentage."""

        if jd_exp <= 0:
            return 100.0

        if resume_exp >= jd_exp:
            return 100.0

        return min(
            (resume_exp / jd_exp) * 100,
            100.0
        )

    def calculate_education_match(
        self,
        resume_education: List,
        jd_education: List
    ) -> float:
        """Calculate education match percentage."""

        if not jd_education:
            return 100.0

        # Combine degree and field information
        education_text = " ".join(
            filter(
                None,
                [
                    f"{e.degree or ''} {e.field or ''}"
                    for e in resume_education
                ]
            )
        ).lower()

        matched = 0

        for requirement in jd_education:
            requirement_lower = requirement.lower()

            if requirement_lower in education_text:
                matched += 1

        return (
            matched / len(jd_education)
        ) * 100

    def extract_jd_skills(
        self,
        job_description: str
    ) -> List[str]:
        """Extract and normalize unique skills from job description."""

        from .extractor import ResumeExtractor

        extractor = ResumeExtractor()

        skills = extractor.extract_skills(job_description)

        # Normalize and remove duplicates
        unique_skills = []
        seen = set()

        for skill in skills:

            normalized = skill.strip().lower()

            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_skills.append(normalized)

        return unique_skills

    def match(
        self,
        resume_data: ResumeData,
        job_description: JobDescription
    ) -> MatchResult:
        """Compute match score between resume and job description."""

        # Extract skills if not already provided
        if not job_description.required_skills:
            job_description.required_skills = (
                self.extract_jd_skills(
                    job_description.description
                )
            )

        # Skill match
        (
            skill_match_score,
            matched_skills,
            missing_skills
        ) = self.calculate_skill_match(
            resume_data.skills,
            job_description.required_skills
        )

        # Experience match
        experience_match_score = (
            self.calculate_experience_match(
                resume_data.experience_years or 0,
                job_description.min_experience or 0
            )
        )

        # Education match
        education_match_score = (
            self.calculate_education_match(
                resume_data.education,
                job_description.education_requirements or []
            )
        )

        # Weighted overall score
        match_score = (
            skill_match_score * self.skill_weight
            + experience_match_score * self.experience_weight
            + education_match_score * self.education_weight
        )

        # Shortlist decision
        is_shortlisted = (
            match_score
            >= settings.SHORTLIST_THRESHOLD * 100
        )

        return MatchResult(
            match_score=round(match_score, 2),
            skill_match_score=round(
                skill_match_score,
                2
            ),
            experience_match_score=round(
                experience_match_score,
                2
            ),
            education_match_score=round(
                education_match_score,
                2
            ),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            is_shortlisted=is_shortlisted,
            justification=None
        )