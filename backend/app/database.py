import os
import sqlite3
import json

from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from .models import (
    ResumeData,
    MatchResult,
    JobDescription
)


class Database:

    def __init__(
        self,
        db_path: str = "./data/resumes.db"
    ):
        db_dir = os.path.dirname(db_path)

        if db_dir and not os.path.exists(db_dir):
            os.makedirs(
                db_dir,
                exist_ok=True
            )

        self.db_path = db_path

        self._init_db()


    # ============================================================
    # DATABASE INITIALIZATION
    # ============================================================

    def _init_db(self):

        with self.get_connection() as conn:

            cursor = conn.cursor()

            # ====================================================
            # USERS TABLE
            # ====================================================

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    full_name TEXT NOT NULL,

                    email TEXT NOT NULL UNIQUE,

                    password_hash TEXT NOT NULL,

                    role TEXT NOT NULL,

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


            # ====================================================
            # RESUMES / ANALYSES TABLE
            # ====================================================

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS resumes (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    -- Job Information
                    job_title TEXT,
                    job_description TEXT,
                    company_name TEXT,

                    -- Candidate Information
                    candidate_name TEXT,
                    email TEXT,
                    phone TEXT,

                    -- Extracted Resume Data
                    skills TEXT,
                    experience_years REAL,
                    education TEXT,
                    companies TEXT,
                    certifications TEXT,

                    -- Matching Results
                    match_score REAL,
                    skill_match_score REAL,
                    experience_match_score REAL,
                    education_match_score REAL,

                    justification TEXT,

                    is_shortlisted INTEGER
                        DEFAULT 0,

                    -- Raw Resume
                    raw_resume_text TEXT,

                    -- Metadata
                    processed_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP,

                    session_id TEXT,

                    -- Owner of this analysis
                    user_id INTEGER,

                    -- Recruiter threshold
                    threshold REAL
                )
                """
            )


            # ====================================================
            # MIGRATION FOR OLD DATABASES
            # ====================================================
            #
            # If resumes.db already existed before user_id /
            # threshold were added, CREATE TABLE IF NOT EXISTS
            # will NOT add the columns.
            #
            # These ALTER statements safely add them.
            # ====================================================

            existing_columns = {
                row["name"]
                for row in cursor.execute(
                    "PRAGMA table_info(resumes)"
                ).fetchall()
            }


            if "user_id" not in existing_columns:

                cursor.execute(
                    """
                    ALTER TABLE resumes
                    ADD COLUMN user_id INTEGER
                    """
                )


            if "threshold" not in existing_columns:

                cursor.execute(
                    """
                    ALTER TABLE resumes
                    ADD COLUMN threshold REAL
                    """
                )


            # ====================================================
            # INDEXES
            # ====================================================

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_resumes_match_score
                ON resumes(match_score)
                """
            )


            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_resumes_shortlisted
                ON resumes(is_shortlisted)
                """
            )


            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_resumes_processed_at
                ON resumes(processed_at DESC)
                """
            )


            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_resumes_user_id
                ON resumes(user_id)
                """
            )


            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_resumes_session_id
                ON resumes(session_id)
                """
            )


            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_users_email
                ON users(email)
                """
            )


            conn.commit()


    # ============================================================
    # CONNECTION
    # ============================================================

    @contextmanager
    def get_connection(self):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.row_factory = sqlite3.Row

        try:

            yield conn

        finally:

            conn.close()


    # ============================================================
    # USER MANAGEMENT
    # ============================================================

    def create_user(
        self,
        full_name: str,
        email: str,
        password_hash: str,
        role: str
    ) -> int:

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users (
                    full_name,
                    email,
                    password_hash,
                    role
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    full_name,
                    email,
                    password_hash,
                    role
                )
            )

            conn.commit()

            return cursor.lastrowid


    def get_user_by_email(
        self,
        email: str
    ) -> Optional[Dict[str, Any]]:

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    full_name,
                    email,
                    password_hash,
                    role,
                    created_at
                FROM users
                WHERE LOWER(email) = LOWER(?)
                """,
                (email,)
            )

            row = cursor.fetchone()

            if row:

                return dict(row)

            return None


    def get_user_by_id(
        self,
        user_id: int
    ) -> Optional[Dict[str, Any]]:

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    full_name,
                    email,
                    role,
                    created_at
                FROM users
                WHERE id = ?
                """,
                (user_id,)
            )

            row = cursor.fetchone()

            if row:

                return dict(row)

            return None


    # ============================================================
    # SAVE ANALYSIS
    # ============================================================

    def save_analysis(
        self,
        job_description: JobDescription,
        resume_data: ResumeData,
        match_result: MatchResult,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> int:

        with self.get_connection() as conn:

            cursor = conn.cursor()


            # ----------------------------------------------------
            # EDUCATION → JSON
            # ----------------------------------------------------

            education_json = json.dumps(
                [
                    {
                        "degree": e.degree,
                        "field": e.field,
                        "institution": e.institution,
                        "year": e.year
                    }
                    for e in resume_data.education
                ]
                if resume_data.education
                else []
            )


            # ----------------------------------------------------
            # SKILLS
            # ----------------------------------------------------

            skills_json = json.dumps(
                resume_data.skills
                if resume_data.skills
                else []
            )


            # ----------------------------------------------------
            # COMPANIES
            # ----------------------------------------------------

            companies_json = json.dumps(
                resume_data.companies
                if resume_data.companies
                else []
            )


            # ----------------------------------------------------
            # CERTIFICATIONS
            # ----------------------------------------------------

            certifications_json = json.dumps(
                resume_data.certifications
                if resume_data.certifications
                else []
            )


            # ----------------------------------------------------
            # SAVE
            # ----------------------------------------------------

            cursor.execute(
                """
                INSERT INTO resumes (

                    job_title,
                    job_description,
                    company_name,

                    candidate_name,
                    email,
                    phone,

                    skills,
                    experience_years,
                    education,
                    companies,
                    certifications,

                    match_score,
                    skill_match_score,
                    experience_match_score,
                    education_match_score,

                    justification,

                    is_shortlisted,

                    raw_resume_text,

                    session_id,
                    user_id,
                    threshold
                )

                VALUES (
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (

                    # Job
                    job_description.title,
                    job_description.description,
                    job_description.company,

                    # Candidate
                    resume_data.candidate_name,
                    resume_data.email,
                    resume_data.phone,

                    # Resume data
                    skills_json,
                    resume_data.experience_years,
                    education_json,
                    companies_json,
                    certifications_json,

                    # Scores
                    match_result.match_score,
                    match_result.skill_match_score,
                    match_result.experience_match_score,
                    match_result.education_match_score,

                    # Gemini
                    match_result.justification,

                    # Shortlist
                    1 if match_result.is_shortlisted else 0,

                    # Raw resume
                    resume_data.raw_text,

                    # Metadata
                    session_id,
                    user_id,
                    threshold
                )
            )


            conn.commit()

            return cursor.lastrowid


    # ============================================================
    # GET SINGLE ANALYSIS
    # ============================================================

    def get_analysis_by_id(
        self,
        analysis_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:

        with self.get_connection() as conn:

            cursor = conn.cursor()


            if user_id is not None:

                cursor.execute(
                    """
                    SELECT *
                    FROM resumes
                    WHERE id = ?
                    AND user_id = ?
                    """,
                    (
                        analysis_id,
                        user_id
                    )
                )

            else:

                cursor.execute(
                    """
                    SELECT *
                    FROM resumes
                    WHERE id = ?
                    """,
                    (analysis_id,)
                )


            row = cursor.fetchone()

            if row:

                return dict(row)

            return None


    # ============================================================
    # GET ANALYSES BY SESSION
    # ============================================================

    def get_analyses_by_session(
        self,
        session_id: str,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:

        with self.get_connection() as conn:

            cursor = conn.cursor()


            if user_id is not None:

                cursor.execute(
                    """
                    SELECT *
                    FROM resumes
                    WHERE session_id = ?
                    AND user_id = ?
                    ORDER BY match_score DESC
                    """,
                    (
                        session_id,
                        user_id
                    )
                )

            else:

                cursor.execute(
                    """
                    SELECT *
                    FROM resumes
                    WHERE session_id = ?
                    ORDER BY match_score DESC
                    """,
                    (session_id,)
                )


            rows = cursor.fetchall()

            return [
                dict(row)
                for row in rows
            ]


    # ============================================================
    # GET SHORTLISTED CANDIDATES
    # ============================================================

    def get_shortlisted_candidates(
        self,
        session_id: str,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:

        with self.get_connection() as conn:

            cursor = conn.cursor()


            if user_id is not None:

                cursor.execute(
                    """
                    SELECT *
                    FROM resumes
                    WHERE session_id = ?
                    AND user_id = ?
                    AND is_shortlisted = 1
                    ORDER BY match_score DESC
                    """,
                    (
                        session_id,
                        user_id
                    )
                )

            else:

                cursor.execute(
                    """
                    SELECT *
                    FROM resumes
                    WHERE session_id = ?
                    AND is_shortlisted = 1
                    ORDER BY match_score DESC
                    """,
                    (session_id,)
                )


            rows = cursor.fetchall()

            return [
                dict(row)
                for row in rows
            ]


    # ============================================================
    # GET RECRUITER SCREENING HISTORY
    # ============================================================

    def get_screening_history(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    session_id,

                    MAX(job_title)
                        AS job_title,

                    MAX(company_name)
                        AS company_name,

                    COUNT(*) 
                        AS total_candidates,

                    SUM(
                        CASE
                            WHEN is_shortlisted = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS shortlisted_count,

                    MAX(threshold)
                        AS threshold,

                    MAX(processed_at)
                        AS created_at

                FROM resumes

                WHERE user_id = ?

                AND session_id IS NOT NULL

                GROUP BY session_id

                ORDER BY created_at DESC
                """,
                (user_id,)
            )

            rows = cursor.fetchall()

            history = []

            for row in rows:

                item = dict(row)

                if item["threshold"] is None:

                    item["threshold"] = 0.70


                history.append(item)


            return history


    # ============================================================
    # GET INDIVIDUAL USER ANALYSIS HISTORY
    # ============================================================

    def get_analyses_by_user(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT
                    id,

                    job_title,
                    job_description,
                    company_name,

                    candidate_name,
                    email,
                    phone,

                    skills,
                    experience_years,
                    education,
                    companies,
                    certifications,

                    match_score,
                    skill_match_score,
                    experience_match_score,
                    education_match_score,

                    justification,

                    is_shortlisted,

                    processed_at,

                    session_id,

                    threshold

                FROM resumes

                WHERE user_id = ?

                ORDER BY processed_at DESC

                LIMIT ?
                """,
                (
                    user_id,
                    limit
                )
            )

            rows = cursor.fetchall()

            return [
                dict(row)
                for row in rows
            ]


    # ============================================================
    # GET INDIVIDUAL DASHBOARD SUMMARY
    # ============================================================

    def get_user_analysis_summary(
        self,
        user_id: int
    ) -> Dict[str, Any]:

        with self.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT

                    COUNT(*) AS total_analyses,

                    AVG(match_score)
                        AS average_score,

                    MAX(match_score)
                        AS best_score,

                    SUM(
                        CASE
                            WHEN is_shortlisted = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS shortlisted_count

                FROM resumes

                WHERE user_id = ?
                """,
                (user_id,)
            )

            row = cursor.fetchone()

            if not row:

                return {
                    "total_analyses": 0,
                    "average_score": 0,
                    "best_score": 0,
                    "shortlisted_count": 0
                }


            result = dict(row)

            return {
                "total_analyses":
                    result["total_analyses"] or 0,

                "average_score":
                    round(
                        result["average_score"] or 0,
                        2
                    ),

                "best_score":
                    round(
                        result["best_score"] or 0,
                        2
                    ),

                "shortlisted_count":
                    result["shortlisted_count"] or 0
            }


# ============================================================
# GLOBAL DATABASE INSTANCE
# ============================================================

db = Database()