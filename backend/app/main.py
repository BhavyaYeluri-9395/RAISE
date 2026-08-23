from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Form,
    HTTPException,
    Depends
)

from fastapi.middleware.cors import CORSMiddleware

from typing import Optional, List
from datetime import datetime

from .models import (
    UploadResponse,
    AnalysisResponse,
    JobDescription,
    ResumeData,
    ShortlistResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse
)


from .parser import PDFParser
from .extractor import ResumeExtractor
from .matcher import ResumeMatcher
from .gemini import gemini_client
from .database import db
from .utils import generate_session_id

from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)


app = FastAPI(
    title="RAISE API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

extractor = ResumeExtractor()

matcher = ResumeMatcher()

@app.get("/")
async def root():

    return {
        "message":
            "RAISE - Resume Analysis & Intelligent Screening Engine",

        "version":
            "1.0.0",

        "status":
            "running",

        "gemini_enabled":
            gemini_client.enabled
    }

@app.post(
    "/auth/register",
    response_model=UserResponse
)
async def register(
    user: UserCreate
):


    if user.role not in [
        "individual",
        "recruiter"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Role must be "
                "individual or recruiter"
            )
        )


 
    existing_user = db.get_user_by_email(
        user.email
    )


    if existing_user:

        raise HTTPException(
            status_code=400,
            detail=(
                "An account with this "
                "email already exists"
            )
        )


    password_hashed = hash_password(
        user.password
    )


    try:

        user_id = db.create_user(
            full_name=user.full_name,
            email=user.email,
            password_hash=password_hashed,
            role=user.role
        )

    except Exception as e:

        print(
            f"Registration error: {e}"
        )

        raise HTTPException(
            status_code=400,
            detail="Unable to create account"
        )



    return UserResponse(
        id=user_id,
        full_name=user.full_name,
        email=user.email,
        role=user.role
    )


@app.post(
    "/auth/login",
    response_model=TokenResponse
)
async def login(
    user: UserLogin
):

    db_user = db.get_user_by_email(
        user.email
    )


    if not db_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    if not verify_password(
        user.password,
        db_user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    token = create_access_token(
        db_user["id"]
    )


    return TokenResponse(

        access_token=token,

        token_type="bearer",

        user=UserResponse(
            id=db_user["id"],
            full_name=db_user["full_name"],
            email=db_user["email"],
            role=db_user["role"]
        )
    )



@app.get(
    "/auth/me",
    response_model=UserResponse
)
async def get_me(
    current_user=Depends(
        get_current_user
    )
):

    return UserResponse(
        id=current_user["id"],
        full_name=current_user["full_name"],
        email=current_user["email"],
        role=current_user["role"]
    )


@app.post(
    "/analyze",
    response_model=UploadResponse
)
async def analyze_resume(

    job_description: str = Form(...),

    job_title: Optional[str] = Form(None),

    company_name: Optional[str] = Form(None),

    file: UploadFile = File(...),

    current_user=Depends(
        get_current_user
    )
):

    """
    Analyze one resume against one
    job description.

    The result is permanently associated
    with the logged-in user.
    """

    try:

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="No file provided"
            )


        allowed_extensions = [
            ".pdf",
            ".txt"
        ]


        file_extension = (
            "."
            + file.filename
            .split(".")[-1]
            .lower()
        )


        if file_extension not in allowed_extensions:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported file type. "
                    "Allowed: "
                    + ", ".join(
                        allowed_extensions
                    )
                )
            )



        file_content = await file.read()

        if file_extension == ".pdf":

            resume_text = (
                PDFParser.parse_pdf_bytes(
                    file_content
                )
            )

        else:

            resume_text = (
                PDFParser.parse_text_bytes(
                    file_content
                )
            )


        extracted_data = (
            extractor.extract_all(
                resume_text
            )
        )


        resume_data = ResumeData(
            **extracted_data
        )


        jd = JobDescription(

            title=(
                job_title
                or "Software Engineer"
            ),

            company=(
                company_name
                or "Unknown Company"
            ),

            description=job_description,

            required_skills=(
                matcher.extract_jd_skills(
                    job_description
                )
            ),

            min_experience=(
                extractor
                .extract_experience_requirement(
                    job_description
                )
            ),

            education_requirements=(
                extractor
                .extract_education_requirements(
                    job_description
                )
            )
        )

        print(
            "========== SINGLE ANALYSIS =========="
        )

        print(
            "User:",
            current_user["email"]
        )

        print(
            "User ID:",
            current_user["id"]
        )

        print(
            "Resume:",
            file.filename
        )

        print(
            "JD:",
            jd.title
        )

        print(
            "JD minimum experience:",
            jd.min_experience
        )

        print(
            "Resume experience:",
            resume_data.experience_years
        )


        match_result = matcher.match(
            resume_data,
            jd
        )


        justification = (
            gemini_client
            .generate_justification(
                resume_data,
                jd,
                match_result
            )
        )


        match_result.justification = (
            justification
        )



        session_id = (
            generate_session_id()
        )


        analysis_id = db.save_analysis(

            job_description=jd,

            resume_data=resume_data,

            match_result=match_result,

            session_id=session_id,

            user_id=current_user["id"],

            threshold=None
        )


        analysis_response = AnalysisResponse(

            job_description=jd,

            resume_data=resume_data,

            match_result=match_result,

            processed_at=datetime.now()
        )


        return UploadResponse(

            success=True,

            message=(
                "Resume analyzed successfully"
            ),

            analysis_id=analysis_id,

            analysis=analysis_response
        )


    except HTTPException:

        raise


    except Exception as e:

        print(
            f"Error analyzing resume: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post(
    "/shortlist",
    response_model=ShortlistResponse
)
async def shortlist_candidates(

    job_description: str = Form(...),

    job_title: Optional[str] = Form(None),

    company_name: Optional[str] = Form(None),

    threshold: Optional[float] = Form(
        0.70
    ),

    files: List[UploadFile] = File(...),

    current_user=Depends(
        get_current_user
    )
):

    """
    Analyze multiple resumes against
    one job description.
    """

    try:


        if threshold is None:

            threshold = 0.70


        if threshold < 0 or threshold > 1:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Threshold must be "
                    "between 0 and 1"
                )
            )



        session_id = (
            generate_session_id()
        )


        candidates = []



        print(
            "MULTI-RESUME SCREENING"
        )

        print(
            "User:",
            current_user["email"]
        )

        print(
            "User ID:",
            current_user["id"]
        )

        print(
            "Session:",
            session_id
        )

        print(
            "Threshold:",
            threshold
        )

      

        for file in files:

            if not file.filename:

                continue


            try:

                allowed_extensions = [
                    ".pdf",
                    ".txt"
                ]


                file_extension = (
                    "."
                    + file.filename
                    .split(".")[-1]
                    .lower()
                )


                if (
                    file_extension
                    not in allowed_extensions
                ):

                    print(
                        "Skipping unsupported file:",
                        file.filename
                    )

                    continue


                # ------------------------------------------------
                # READ FILE
                # ------------------------------------------------

                file_content = (
                    await file.read()
                )


                # ------------------------------------------------
                # PARSE
                # ------------------------------------------------

                if file_extension == ".pdf":

                    resume_text = (
                        PDFParser
                        .parse_pdf_bytes(
                            file_content
                        )
                    )

                else:

                    resume_text = (
                        PDFParser
                        .parse_text_bytes(
                            file_content
                        )
                    )


                # ------------------------------------------------
                # EXTRACT
                # ------------------------------------------------

                extracted_data = (
                    extractor.extract_all(
                        resume_text
                    )
                )


                resume_data = ResumeData(
                    **extracted_data
                )


                # ------------------------------------------------
                # CREATE JD
                # ------------------------------------------------

                jd = JobDescription(

                    title=(
                        job_title
                        or "Software Engineer"
                    ),

                    company=(
                        company_name
                        or "Unknown Company"
                    ),

                    description=job_description,

                    required_skills=(
                        matcher.extract_jd_skills(
                            job_description
                        )
                    ),

                    min_experience=(
                        extractor
                        .extract_experience_requirement(
                            job_description
                        )
                    ),

                    education_requirements=(
                        extractor
                        .extract_education_requirements(
                            job_description
                        )
                    )
                )


                # ------------------------------------------------
                # MATCH
                # ------------------------------------------------

                match_result = matcher.match(
                    resume_data,
                    jd
                )


                # ------------------------------------------------
                # APPLY THRESHOLD
                # ------------------------------------------------

                match_result.is_shortlisted = (
                    match_result.match_score
                    >= threshold * 100
                )


                # ------------------------------------------------
                # GEMINI
                # ------------------------------------------------

                justification = (
                    gemini_client
                    .generate_justification(
                        resume_data,
                        jd,
                        match_result
                    )
                )


                match_result.justification = (
                    justification
                )


                # ------------------------------------------------
                # SAVE
                # ------------------------------------------------

                db.save_analysis(

                    job_description=jd,

                    resume_data=resume_data,

                    match_result=match_result,

                    session_id=session_id,

                    user_id=current_user["id"],

                    threshold=threshold
                )


                # ------------------------------------------------
                # RESPONSE
                # ------------------------------------------------

                candidates.append(
                    AnalysisResponse(

                        job_description=jd,

                        resume_data=resume_data,

                        match_result=match_result,

                        processed_at=datetime.now()
                    )
                )


                # ------------------------------------------------
                # DEBUG
                # ------------------------------------------------

                print(
                    "--------------------------------------"
                )

                print(
                    "Resume:",
                    file.filename
                )

                print(
                    "Candidate:",
                    resume_data.candidate_name
                )

                print(
                    "JD experience:",
                    jd.min_experience
                )

                print(
                    "Resume experience:",
                    resume_data.experience_years
                )

                print(
                    "Skill score:",
                    match_result.skill_match_score
                )

                print(
                    "Experience score:",
                    match_result.experience_match_score
                )

                print(
                    "Overall score:",
                    match_result.match_score
                )

                print(
                    "Shortlisted:",
                    match_result.is_shortlisted
                )


            except Exception as e:

                print(
                    f"Error processing "
                    f"{file.filename}: {e}"
                )

                continue


        # ====================================================
        # SORT ALL CANDIDATES
        # ====================================================

        candidates.sort(

            key=lambda candidate:
                candidate
                .match_result
                .match_score,

            reverse=True
        )


        # ====================================================
        # SHORTLISTED
        # ====================================================

        shortlisted = [

            candidate

            for candidate in candidates

            if candidate
            .match_result
            .match_score
            >= threshold * 100
        ]


        # ====================================================
        # ASSIGN RANKS
        # ====================================================

        for index, candidate in enumerate(
            shortlisted,
            1
        ):

            candidate.match_result.rank = (
                index
            )


        # ====================================================
        # DEBUG
        # ====================================================

        print(
            "======================================"
        )

        print(
            "Total candidates:",
            len(candidates)
        )

        print(
            "Shortlisted:",
            len(shortlisted)
        )

        print(
            "======================================"
        )


        # ====================================================
        # RESPONSE
        # ====================================================

        return ShortlistResponse(

            success=True,

            session_id=session_id,

            candidates=shortlisted,

            total_candidates=len(
                candidates
            ),

            shortlisted_count=len(
                shortlisted
            )
        )


    except HTTPException:

        raise


    except Exception as e:

        print(
            f"Shortlist error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GET SCREENING SESSION RESULTS
# ============================================================

@app.get(
    "/analyses/{session_id}"
)
async def get_analyses(

    session_id: str,

    current_user=Depends(
        get_current_user
    )
):

    """
    Get analyses for a screening session.

    Only the user who created the session
    can access it.
    """

    analyses = (
        db.get_analyses_by_session(
            session_id,
            current_user["id"]
        )
    )


    if not analyses:

        raise HTTPException(
            status_code=404,
            detail=(
                "Screening session not found"
            )
        )


    return {

        "session_id":
            session_id,

        "analyses":
            analyses
    }


# ============================================================
# GET SHORTLISTED CANDIDATES
# ============================================================

@app.get(
    "/shortlisted/{session_id}"
)
async def get_shortlisted(

    session_id: str,

    current_user=Depends(
        get_current_user
    )
):

    candidates = (
        db.get_shortlisted_candidates(
            session_id,
            current_user["id"]
        )
    )


    return {

        "session_id":
            session_id,

        "shortlisted":
            candidates
    }


# ============================================================
# RECRUITER SCREENING HISTORY
# ============================================================

@app.get(
    "/screening-history"
)
async def get_screening_history(

    current_user=Depends(
        get_current_user
    )
):

    """
    Return screening sessions belonging
    to the logged-in user.
    """

    try:

        history = (
            db.get_screening_history(
                current_user["id"]
            )
        )


        return {
            "history": history
        }


    except Exception as e:

        print(
            f"History error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                "screening history"
            )
        )


# ============================================================
# INDIVIDUAL USER ANALYSIS HISTORY
# ============================================================

@app.get(
    "/my-analyses"
)
async def get_my_analyses(

    current_user=Depends(
        get_current_user
    )
):

    """
    Return resume analyses belonging
    to the currently logged-in individual.
    """

    try:

        analyses = (
            db.get_analyses_by_user(
                current_user["id"]
            )
        )


        return {
            "analyses": analyses
        }


    except Exception as e:

        print(
            f"Individual history error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                "your analysis history"
            )
        )


# ============================================================
# INDIVIDUAL DASHBOARD SUMMARY
# ============================================================

@app.get(
    "/my-analyses/summary"
)
async def get_my_analysis_summary(

    current_user=Depends(
        get_current_user
    )
):

    """
    Return summary statistics for
    the logged-in individual's analyses.
    """

    try:

        summary = (
            db.get_user_analysis_summary(
                current_user["id"]
            )
        )


        return summary


    except Exception as e:

        print(
            f"Individual summary error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load "
                "analysis summary"
            )
        )


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health"
)
async def health_check():

    return {

        "status":
            "healthy",

        "gemini_available":
            gemini_client.enabled
    }
