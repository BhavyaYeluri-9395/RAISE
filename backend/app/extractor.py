import re
import spacy

from typing import List, Optional, Dict, Any

from .models import Education
from .utils import (
    extract_email,
    extract_phone,
    extract_company_names,
    clean_text
)


class ResumeExtractor:

    def __init__(self):


        try:
            self.nlp = spacy.load("en_core_web_sm")

        except Exception:
            import subprocess

            subprocess.run(
                [
                    "python",
                    "-m",
                    "spacy",
                    "download",
                    "en_core_web_sm"
                ],
                check=False
            )

            self.nlp = spacy.load("en_core_web_sm")


        try:
            from skills import SkillLibrary

            self.skill_library = SkillLibrary()
            self.use_skills_package = True

        except Exception:

            self.use_skills_package = False

            print(
                "Skills package not found. Using fallback skill list."
            )

            self._init_fallback_skills()


    def _init_fallback_skills(self):

        """Initialize fallback skill list if skills package is unavailable."""

        self.fallback_skills = [

            # Programming Languages
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c#",
            "ruby",
            "go",
            "rust",
            "swift",
            "kotlin",
            "php",

            # Web
            "html",
            "css",

            # Databases
            "sql",
            "nosql",
            "mongodb",
            "postgresql",
            "mysql",
            "oracle",
            "redis",
            "elasticsearch",
            "cassandra",
            "apache cassandra",

            # APIs
            "graphql",
            "rest",
            "soap",

            # Frameworks
            "react",
            "angular",
            "vue",
            "node.js",
            "django",
            "flask",
            "spring",
            "spring boot",
            "fastapi",
            "laravel",
            "rails",
            "asp.net",
            "jquery",
            "bootstrap",
            "tailwind",

            # ML / AI
            "tensorflow",
            "pytorch",
            "keras",
            "scikit-learn",
            "scikit learn",
            "pandas",
            "numpy",
            "machine learning",
            "deep learning",
            "nlp",
            "computer vision",
            "data science",
            "data analysis",
            "artificial intelligence",

            # Cloud & DevOps
            "aws",
            "azure",
            "gcp",
            "docker",
            "kubernetes",
            "jenkins",
            "git",
            "github",
            "gitlab",
            "ci/cd",
            "terraform",
            "ansible",
            "prometheus",
            "grafana",
            "elk",
            "splunk",
            "minio",
            "linux",
            "unix",

            # Data
            "big data",
            "hadoop",
            "spark",
            "airflow",
            "etl",

            # Other
            "agile",
            "scrum",
            "project management",
            "leadership",
            "communication",
            "problem solving",
            "critical thinking",
            "teamwork",
            "time management",
            "excel",
            "microsoft excel"
        ]


    def extract_candidate_name(
        self,
        text: str
    ) -> Optional[str]:

        """
        Extract a real candidate name from the beginning of a resume.

        Important:
        Resume PDFs often flatten columns and formatting. Therefore,
        we use several strategies but reject technology names,
        section headings, job titles, URLs, emails, and other
        non-person text.
        """

        if not text:
            return None


        text = text.replace("\r", "\n")

        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in text.split("\n")
            if line.strip()
        ]

        if not lines:
            return None


        ignored_lines = {
            "resume",
            "curriculum vitae",
            "curriculum-vitae",
            "cv",
            "profile",
            "professional profile",
            "professional summary",
            "summary",
            "about me",
            "education",
            "skills",
            "technical skills",
            "technical skill",
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "projects",
            "certifications",
            "certificates",
            "achievements",
            "contact",
            "contact information",
            "personal information",
            "objective",
            "career objective",
            "references",
            "internships",
            "internship",
            "languages",
            "interests",
            "hobbies",
            "publications",
            "awards",
            "leadership",
            "responsibilities",
            "qualifications",
            "academic qualifications",
            "academic background"
        }


        technical_terms = {
            "apache",
            "cassandra",
            "tools",
            "git",
            "github",
            "gitlab",
            "python",
            "java",
            "javascript",
            "typescript",
            "react",
            "angular",
            "vue",
            "node",
            "nodejs",
            "node.js",
            "django",
            "flask",
            "spring",
            "fastapi",
            "mongodb",
            "mysql",
            "postgresql",
            "oracle",
            "redis",
            "sql",
            "nosql",
            "docker",
            "kubernetes",
            "jenkins",
            "aws",
            "azure",
            "gcp",
            "linux",
            "unix",
            "html",
            "css",
            "graphql",
            "rest",
            "soap",
            "tensorflow",
            "pytorch",
            "keras",
            "pandas",
            "numpy",
            "scikit",
            "sklearn",
            "machine",
            "learning",
            "deep",
            "nlp",
            "data",
            "science",
            "analytics",
            "excel",
            "microsoft",
            "terraform",
            "ansible",
            "spark",
            "hadoop",
            "airflow",
            "kafka",
            "minio",
            "prometheus",
            "grafana",
            "ci",
            "cd",
            "agile",
            "scrum",
            "api",
            "apis",
            "database",
            "databases",
            "programming",
            "software",
            "developer",
            "development",
            "engineering",
            "engineer"
        }

        # Add fallback skills if available.
        for skill in getattr(
            self,
            "fallback_skills",
            []
        ):
            for word in re.findall(
                r"[A-Za-z]+",
                skill.lower()
            ):
                technical_terms.add(word)

        # ------------------------------------------------------------
        # Helper: reject obvious non-name candidates
        # ------------------------------------------------------------

        def looks_like_name(candidate: str) -> bool:

            if not candidate:
                return False

            candidate = re.sub(
                r"\s+",
                " ",
                candidate.strip()
            )

            candidate_lower = candidate.lower()



            if candidate_lower in ignored_lines:
                return False

            if "@" in candidate:
                return False

            if "http://" in candidate_lower:
                return False

            if "https://" in candidate_lower:
                return False

            if "www." in candidate_lower:
                return False

            # Phone numbers / years / scores
            if any(
                char.isdigit()
                for char in candidate
            ):
                return False

            # --------------------------------------------------------
            # Remove harmless name punctuation for validation
            # --------------------------------------------------------

            cleaned = (
                candidate
                .replace("-", " ")
                .replace("'", " ")
                .replace(".", " ")
            )

            words = cleaned.split()

            # A normal full name is generally 2–4 words.
            if not 2 <= len(words) <= 4:
                return False

            # Prevent extremely long text.
            if len(candidate) > 45:
                return False

            # Every word must be alphabetic.
            if not all(
                word.isalpha()
                for word in words
            ):
                return False

            # --------------------------------------------------------
            # Reject technical terms
            # --------------------------------------------------------

            normalized_words = {
                word.lower()
                for word in words
            }

            if normalized_words.intersection(
                technical_terms
            ):
                return False


            bad_phrases = [

                "software engineer",
                "software developer",
                "web developer",
                "full stack",
                "fullstack",
                "backend developer",
                "frontend developer",
                "data scientist",
                "data analyst",
                "machine learning",
                "computer science",
                "computer engineering",
                "information technology",
                "technical skills",
                "work experience",
                "professional experience",
                "bachelor of",
                "master of",
                "university",
                "institute",
                "college",
                "certification",
                "professional summary",
                "career objective",
                "project management",
                "candidate profile"
            ]

            for phrase in bad_phrases:

                if phrase in candidate_lower:
                    return False

            # --------------------------------------------------------
            # Names normally contain alphabetic words with
            # reasonable lengths.
            # --------------------------------------------------------

            if any(
                len(word) < 2
                for word in words
            ):
                return False

            # Reject words that are entirely uppercase when the
            # entire candidate looks like a technical label.
            if all(
                word.isupper()
                for word in words
            ):
                return False

            return True

        # ============================================================
        # STRATEGY 1
        # Look at the first lines of the resume.
        # ============================================================

        # We deliberately examine only the first 10 lines.
        # A person's name should normally be near the top.
        for line in lines[:10]:

            candidate = line.strip()

            if looks_like_name(candidate):

                # Additional spaCy validation:
                # If spaCy identifies the line as an ORG,
                # don't use it as a candidate name.
                try:

                    doc = self.nlp(candidate)

                    if any(
                        ent.label_ in {"ORG", "PRODUCT", "GPE"}
                        for ent in doc.ents
                    ):
                        continue

                except Exception:
                    pass

                return candidate

        # ============================================================
        # STRATEGY 2
        # Flattened PDF:
        #
        # Aarav Mehta aarav@example.com
        #
        # Look immediately before an email.
        # ============================================================

        first_part = text[:1500].strip()

        email_match = re.search(
            r"([A-Za-z][A-Za-z'.-]+"
            r"(?:\s+[A-Za-z][A-Za-z'.-]+){1,3})"
            r"\s+(?:Email\s*)?"
            r"[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            first_part,
            re.IGNORECASE
        )

        if email_match:

            candidate = email_match.group(1).strip()

            if looks_like_name(candidate):
                return candidate

        # ============================================================
        # STRATEGY 3
        # Look before contact labels.
        # ============================================================

        contact_match = re.search(
            r"^(.{2,50}?)"
            r"\s+(?:Email|E-mail|Phone|Mobile|Contact)\b",
            first_part,
            re.IGNORECASE
        )

        if contact_match:

            candidate = contact_match.group(1).strip()

            if looks_like_name(candidate):
                return candidate

        # ============================================================
        # STRATEGY 4
        # Search the beginning of the document for PERSON entities.
        #
        # We do NOT accept arbitrary PERSON entities. The candidate
        # must also pass our strict name validation.
        # ============================================================

        try:

            first_text = text[:1200]

            doc = self.nlp(first_text)

            for ent in doc.ents:

                if ent.label_ != "PERSON":
                    continue

                candidate = ent.text.strip()

                if looks_like_name(candidate):
                    return candidate

        except Exception:
            pass

        # ============================================================
        # STRATEGY 5
        # If the PDF has very poor formatting, inspect individual
        # lines near the beginning and choose the first strong
        # name-like line.
        # ============================================================

        for line in lines[:20]:

            candidate = line.strip()

            if not looks_like_name(candidate):
                continue

            # Don't accept a line containing known technology terms.
            words_lower = {
                word.lower()
                for word in re.findall(
                    r"[A-Za-z]+",
                    candidate
                )
            }

            if words_lower.intersection(
                technical_terms
            ):
                continue

            return candidate

        return None

    # ================================================================
    # SKILL EXTRACTION
    # ================================================================

    def extract_skills(
        self,
        text: str
    ) -> List[str]:

        """Extract skills using skills package or fallback list."""

        found_skills = set()

        text_lower = text.lower()

        if self.use_skills_package:

            try:

                all_skills = (
                    self.skill_library.get_skills()
                )

                for skill in all_skills:

                    skill_lower = skill.lower()

                    if skill_lower in text_lower:

                        found_skills.add(skill)

                    elif len(skill.split()) > 1:

                        pattern = (
                            r"\b"
                            + re.escape(
                                skill_lower
                            ).replace(
                                r"\ ",
                                r"\s+"
                            )
                            + r"\b"
                        )

                        if re.search(
                            pattern,
                            text_lower
                        ):
                            found_skills.add(skill)

            except Exception:

                self.use_skills_package = False

                return self.extract_skills(text)

        else:

            for skill in self.fallback_skills:

                skill_lower = skill.lower()

                if skill_lower in text_lower:

                    found_skills.add(skill)

                elif len(skill.split()) > 1:

                    pattern = (
                        r"\b"
                        + re.escape(
                            skill_lower
                        ).replace(
                            r"\ ",
                            r"\s+"
                        )
                        + r"\b"
                    )

                    if re.search(
                        pattern,
                        text_lower
                    ):
                        found_skills.add(skill)

        # ------------------------------------------------------------
        # Keep spaCy organization extraction
        # ------------------------------------------------------------

        try:

            doc = self.nlp(text)

            for ent in doc.ents:

                if ent.label_ == "ORG":

                    if (
                        3 <= len(ent.text) <= 15
                        and ent.text.upper()
                        in text.upper()
                    ):
                        found_skills.add(
                            ent.text
                        )

        except Exception:
            pass

        return list(found_skills)[:50]

    # ================================================================
    # EDUCATION EXTRACTION
    # ================================================================

    def extract_education(
        self,
        text: str
    ) -> List[Education]:

        """Extract education information from resume text."""

        education_list = []

        # ------------------------------------------------------------
        # Isolate education section
        # ------------------------------------------------------------

        education_match = re.search(
            r"(?:education|academic background|qualifications)"
            r"\s*:?\s*(.*?)"
            r"(?=\n\s*(?:skills|technical skills|experience|"
            r"work experience|projects|certifications|"
            r"achievements|leadership)\b|$)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if education_match:

            education_text = (
                education_match.group(1).strip()
            )

        else:

            education_text = text

        # ------------------------------------------------------------
        # Degree patterns
        # ------------------------------------------------------------

        degree_patterns = [

            (
                r"\b(B\.?\s*Tech|Bachelor(?:\s+of\s+Technology)?)"
                r"(?:\s*,?\s*(?:in|of)\s+)?"
                r"([A-Za-z][A-Za-z\s&]*)?",
                "Bachelor"
            ),

            (
                r"\b(M\.?\s*Tech|Master(?:\s+of\s+Technology)?)"
                r"(?:\s*,?\s*(?:in|of)\s+)?"
                r"([A-Za-z][A-Za-z\s&]*)?",
                "Master"
            ),

            (
                r"\b(B\.?\s*E\.?|Bachelor(?:\s+of\s+Engineering)?)"
                r"(?:\s*,?\s*(?:in|of)\s+)?"
                r"([A-Za-z][A-Za-z\s&]*)?",
                "Bachelor"
            ),

            (
                r"\b(M\.?\s*E\.?|Master(?:\s+of\s+Engineering)?)"
                r"(?:\s*,?\s*(?:in|of)\s+)?"
                r"([A-Za-z][A-Za-z\s&]*)?",
                "Master"
            ),

            (
                r"\b(MBA)\b",
                "MBA"
            )
        ]

        degree = None
        field = None

        for pattern, normalized_degree in degree_patterns:

            match = re.search(
                pattern,
                education_text,
                re.IGNORECASE
            )

            if match:

                degree = normalized_degree

                if (
                    match.lastindex
                    and match.lastindex >= 2
                ):

                    possible_field = (
                        match.group(2)
                    )

                    if possible_field:

                        field = (
                            possible_field.strip(
                                " ,.-:"
                            )
                        )

                break

        # ------------------------------------------------------------
        # Explicit field extraction
        # ------------------------------------------------------------

        if not field:

            field_match = re.search(
                r"\b(?:in|majoring\s+in)\s+"
                r"(computer\s+science|information\s+technology|"
                r"computer\s+engineering|software\s+engineering|"
                r"electronics(?:\s+and\s+communication)?|"
                r"data\s+science|"
                r"artificial\s+intelligence)\b",
                education_text,
                re.IGNORECASE
            )

            if field_match:

                field = (
                    field_match.group(1).strip()
                )

        # ------------------------------------------------------------
        # Institution
        # ------------------------------------------------------------

        institution = None

        institution_patterns = [

            r"([A-Z][A-Za-z\s]+"
            r"(?:University|Institute|College))",

            r"(?:at|from)\s+"
            r"([A-Z][A-Za-z\s]+"
            r"(?:University|Institute|College))"
        ]

        for pattern in institution_patterns:

            match = re.search(
                pattern,
                education_text
            )

            if match:

                institution = (
                    match.group(1).strip()
                )

                break

        # ------------------------------------------------------------
        # Graduation year
        # ------------------------------------------------------------

        year = None

        year_match = re.search(
            r"\b(19|20)\d{2}\b",
            education_text
        )

        if year_match:

            year = year_match.group(0)

        # ------------------------------------------------------------
        # Build education object
        # ------------------------------------------------------------

        if degree or field or institution:

            education_list.append(
                Education(
                    degree=degree,
                    field=field,
                    institution=institution,
                    year=year
                )
            )

        return education_list

    # ================================================================
    # EXPERIENCE YEARS
    # ================================================================

    def extract_experience_years(
        self,
        text: str
    ) -> float:

        """Extract years of professional experience."""

        patterns = [

            r"(\d+)\+?\s*(?:-?\s*\d+)?\s*years?"
            r"\s*(?:of)?\s*(?:experience|work)",

            r"(?:experience|work)"
            r"\s*(?:of)?\s*(\d+)\+?"
            r"\s*(?:-?\s*\d+)?\s*years?",

            r"(\d+)\+?\s*(?:-?\s*\d+)?"
            r"\s*yrs?\s*(?:of)?\s*exp",

            r"(\d+)\s*\+\s*years?"
            r"\s*experience",

            r"over\s*(\d+)\s*years?"
            r"\s*experience"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )

            if matches:

                try:

                    numbers = re.findall(
                        r"\d+",
                        matches[0]
                    )

                    if numbers:
                        return float(
                            numbers[0]
                        )

                except Exception:
                    pass

        # ------------------------------------------------------------
        # Estimate from work history dates
        # ------------------------------------------------------------

        date_pattern = (
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*\.?\s*(\d{4})"
        )

        years = re.findall(
            date_pattern,
            text,
            re.IGNORECASE
        )

        if len(years) >= 2:

            try:

                years = [
                    int(y)
                    for y in years
                ]

                total = (
                    max(years)
                    - min(years)
                )

                if 1 <= total <= 50:
                    return float(total)

            except Exception:
                pass

        return 0.0

    # ================================================================
    # CERTIFICATIONS
    # ================================================================

    def extract_certifications(
        self,
        text: str
    ) -> List[str]:

        """Extract certifications."""

        certifications = []

        cert_keywords = [

            "certified",
            "certification",
            "certificate",
            "licensed",

            "aws certified",
            "azure certified",
            "gcp certified",

            "pmp",
            "scrum master",
            "agile",
            "six sigma",
            "itil",

            "ccna",
            "ccnp",
            "mcsd",
            "mct",
            "cissp",
            "ceh",
            "oscp"
        ]

        patterns = [

            r"([A-Z][a-zA-Z\s]+)\s+certification",

            r"certification\s+in\s+([A-Za-z\s]+)",

            r"([A-Z][a-zA-Z\s]+)\s+certified",

            r"certified\s+([A-Za-z\s]+)",

            r"(AWS|Azure|GCP|PMP|CCNA|CCNP|CISSP|CEH|OSCP)"
            r"\s+certified"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )

            for match in matches:

                cert = clean_text(match)

                if cert and len(cert) > 2:

                    certifications.append(
                        cert.title()
                    )

        # ------------------------------------------------------------
        # Explicit certification lines
        # ------------------------------------------------------------

        lines = text.split("\n")

        for line in lines:

            line_clean = line.strip()

            if any(
                keyword.lower()
                in line_clean.lower()
                for keyword in cert_keywords
            ):

                if (
                    len(line_clean) > 3
                    and not line_clean.startswith(
                        ("•", "-", "*")
                    )
                ):

                    certifications.append(
                        clean_text(
                            line_clean
                        )
                    )

        return list(
            set(certifications)
        )[:20]

    # ================================================================
    # JOB DESCRIPTION EXPERIENCE REQUIREMENT
    # ================================================================

    def extract_experience_requirement(
        self,
        text: str
    ) -> float:

        """Extract minimum required experience from a job description."""

        text_lower = text.lower()

        patterns = [

            # minimum experience: 3 years
            r"minimum\s+experience\s*[:\-]?\s*"
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?",

            # minimum 3 years experience
            r"minimum\s+(\d+(?:\.\d+)?)"
            r"\s*\+?\s*years?",

            # minimum of 3 years experience
            r"minimum\s+of\s+(\d+(?:\.\d+)?)"
            r"\s*\+?\s*years?",

            # at least 3 years experience
            r"at\s+least\s+(\d+(?:\.\d+)?)"
            r"\s*\+?\s*years?",

            # 3+ years experience
            r"(\d+(?:\.\d+)?)\s*\+\s*years?"
            r"\s+(?:of\s+)?experience",

            # 3 years of experience
            r"(\d+(?:\.\d+)?)\s+years?"
            r"\s+of\s+experience",

            # 3 years experience
            r"(\d+(?:\.\d+)?)\s+years?"
            r"\s+experience"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text_lower,
                re.IGNORECASE
            )

            if match:

                return float(
                    match.group(1)
                )

        return 0.0

    # ================================================================
    # JOB DESCRIPTION EDUCATION REQUIREMENTS
    # ================================================================

    def extract_education_requirements(
        self,
        text: str
    ) -> List[str]:

        """Extract basic education requirements from a job description."""

        requirements = []

        text_lower = text.lower()

        education_patterns = [

            (
                "computer science",
                "computer science"
            ),

            (
                "information technology",
                "information technology"
            ),

            (
                "software engineering",
                "software engineering"
            ),

            (
                "computer engineering",
                "computer engineering"
            ),

            (
                "engineering",
                "engineering"
            ),

            (
                "bachelor",
                "bachelor"
            ),

            (
                "master",
                "master"
            ),

            (
                "b.tech",
                "b.tech"
            ),

            (
                "m.tech",
                "m.tech"
            ),

            (
                "b.e.",
                "b.e."
            ),

            (
                "m.e.",
                "m.e."
            ),

            (
                "mba",
                "mba"
            )
        ]

        for keyword, value in education_patterns:

            if keyword in text_lower:

                requirements.append(value)

        # Remove duplicates while preserving order
        return list(
            dict.fromkeys(
                requirements
            )
        )

    # ================================================================
    # EXTRACT EVERYTHING
    # ================================================================

    def extract_all(
        self,
        text: str
    ) -> Dict[str, Any]:

        """Extract all information from resume text."""

        candidate_name = (
            self.extract_candidate_name(
                text
            )
        )

        return {

            "candidate_name":
                candidate_name,

            "email":
                extract_email(text),

            "phone":
                extract_phone(text),

            "skills":
                self.extract_skills(text),

            "experience_years":
                self.extract_experience_years(
                    text
                ),

            "education":
                self.extract_education(
                    text
                ),

            "companies":
                extract_company_names(
                    text
                ),

            "certifications":
                self.extract_certifications(
                    text
                ),

            "raw_text":
                text
        }
