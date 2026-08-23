from typing import List, Tuple

from .models import ResumeData, JobDescription, MatchResult
from .config import settings


class ResumeMatcher:

    def __init__(self):
        # Lightweight matcher.
        # We intentionally do NOT load SentenceTransformer here
        # because it loads PyTorch + a large ML model into memory.
        self.skill_weight = settings.SKILL_WEIGHT
        self.experience_weight = settings.EXPERIENCE_WEIGHT
        self.education_weight = settings.EDUCATION_WEIGHT

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Lightweight text similarity.

        This replaces the SentenceTransformer similarity calculation
        so the backend can run within Render's memory limit.
        """

        if not text1 or not text2:
            return 0.0

        words1 = set(
            word.strip().lower()
            for word in text1.split()
            if word.strip()
        )

        words2 = set(
            word.strip().lower()
            for word in text2.split()
            if word.strip()
        )

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def calculate_skill_match(
        self,
        resume_skills: List[str],
        jd_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:

        resume_normalized = list(dict.fromkeys(
            skill.strip().lower()
            for skill in resume_skills
            if skill and skill.strip()
        ))

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
            len(matched_skills) /
            len(jd_normalized)
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

        if not jd_education:
            return 100.0

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

            requirement_lower = (
                requirement.lower()
            )

            if requirement_lower in education_text:
                matched += 1

        return (
            matched /
            len(jd_education)
        ) * 100

    def extract_jd_skills(
        self,
        job_description: str
    ) -> List[str]:

        from .extractor import ResumeExtractor

        extractor = ResumeExtractor()

        skills = extractor.extract_skills(
            job_description
        )

        unique_skills = []
        seen = set()

        for skill in skills:

            normalized = (
                skill.strip().lower()
            )

            if (
                normalized
                and normalized not in seen
            ):
                seen.add(normalized)
                unique_skills.append(
                    normalized
                )

        return unique_skills

    def match(
        self,
        resume_data: ResumeData,
        job_description: JobDescription
    ) -> MatchResult:

        if not job_description.required_skills:

            job_description.required_skills = (
                self.extract_jd_skills(
                    job_description.description
                )
            )

        (
            skill_match_score,
            matched_skills,
            missing_skills
        ) = self.calculate_skill_match(
            resume_data.skills,
            job_description.required_skills
        )

        experience_match_score = (
            self.calculate_experience_match(
                resume_data.experience_years or 0,
                job_description.min_experience or 0
            )
        )

        education_match_score = (
            self.calculate_education_match(
                resume_data.education,
                job_description.education_requirements
                or []
            )
        )

        match_score = (
            skill_match_score *
            self.skill_weight

            + experience_match_score *
            self.experience_weight

            + education_match_score *
            self.education_weight
        )

        is_shortlisted = (
            match_score
            >= settings.SHORTLIST_THRESHOLD * 100
        )

        return MatchResult(
            match_score=round(
                match_score,
                2
            ),

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
