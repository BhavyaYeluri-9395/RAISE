import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Clock3,
  FileSearch,
  FileText,
  History,
  LogOut,
  Upload,
  User,
  X,
} from "lucide-react";

import { useAuth } from "../../context/AuthContext";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


function IndividualDashboard() {

  const { user, logout } = useAuth();

  // ============================================================
  // FORM
  // ============================================================

  const [jobTitle, setJobTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const [resumeFile, setResumeFile] = useState(null);

  // ============================================================
  // STATE
  // ============================================================

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [success, setSuccess] = useState("");

  const [result, setResult] = useState(null);

  const [history, setHistory] = useState([]);

  const [historyLoading, setHistoryLoading] =
    useState(true);


  // ============================================================
  // LOAD PREVIOUS ANALYSES
  // ============================================================

  useEffect(() => {

    const loadHistory = async () => {

      try {

        const token =
          localStorage.getItem("raise_token");

        if (!token) {
          setHistoryLoading(false);
          return;
        }

        const response = await axios.get(
          `${API_URL}/my-analyses`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        setHistory(
          response.data.analyses || []
        );

      } catch (err) {

        console.error(
          "Failed to load individual history:",
          err
        );

      } finally {

        setHistoryLoading(false);

      }
    };

    loadHistory();

  }, []);


  // ============================================================
  // FILE HANDLING
  // ============================================================

  const handleFileChange = (event) => {

    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    const fileName =
      file.name.toLowerCase();

    if (
      !fileName.endsWith(".pdf") &&
      !fileName.endsWith(".txt")
    ) {

      setError(
        "Please upload a PDF or TXT resume."
      );

      event.target.value = "";

      return;
    }

    setError("");
    setResumeFile(file);
  };


  const removeFile = () => {
    setResumeFile(null);
  };


  // ============================================================
  // ANALYZE
  // ============================================================

  const handleAnalyze = async (event) => {

    event.preventDefault();

    setError("");
    setSuccess("");
    setResult(null);

    // ----------------------------------------------------------
    // VALIDATION
    // ----------------------------------------------------------

    if (!jobTitle.trim()) {

      setError(
        "Please enter the job title."
      );

      return;
    }

    if (!jobDescription.trim()) {

      setError(
        "Please enter the job description."
      );

      return;
    }

    if (!resumeFile) {

      setError(
        "Please upload your resume."
      );

      return;
    }

    const token =
      localStorage.getItem("raise_token");

    if (!token) {

      setError(
        "Your session has expired. Please sign in again."
      );

      return;
    }

    // ----------------------------------------------------------
    // FORM DATA
    // ----------------------------------------------------------

    const formData =
      new FormData();

    formData.append(
      "job_description",
      jobDescription
    );

    formData.append(
      "job_title",
      jobTitle
    );

    formData.append(
      "company_name",
      companyName ||
        "Unknown Company"
    );

    formData.append(
      "file",
      resumeFile
    );

    setLoading(true);

    try {

      const response =
        await axios.post(
          `${API_URL}/analyze`,
          formData,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

      const data =
        response.data;

      setResult(data);

      setSuccess(
        "Your resume has been analyzed successfully."
      );

      // --------------------------------------------------------
      // Add latest analysis to history immediately
      // --------------------------------------------------------

      const analysis =
        data.analysis || {};

      const resume =
        analysis.resume_data || {};

      const match =
        analysis.match_result || {};

      const historyItem = {

        id:
          data.analysis_id,

        candidate_name:
          resume.candidate_name,

        job_title:
          analysis.job_description?.title ||
          jobTitle,

        company_name:
          analysis.job_description?.company ||
          companyName,

        match_score:
          match.match_score,

        processed_at:
          analysis.processed_at ||
          new Date().toISOString(),

      };

      setHistory(
        (previous) => [
          historyItem,
          ...previous.filter(
            (item) =>
              item.id !==
              historyItem.id
          ),
        ].slice(0, 10)
      );

      // Scroll to result
      setTimeout(() => {

        document
          .getElementById(
            "individual-result"
          )
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });

      }, 100);

    } catch (err) {

      console.error(
        "Resume analysis error:",
        err
      );

      if (
        err.response?.status === 401
      ) {

        localStorage.removeItem(
          "raise_token"
        );

        setError(
          "Your session has expired. Please sign in again."
        );

      } else {

        const message =
          err.response?.data?.detail ||
          "Unable to analyze your resume. Please make sure the backend is running.";

        setError(
          typeof message === "string"
            ? message
            : "Something went wrong while analyzing your resume."
        );
      }

    } finally {

      setLoading(false);

    }
  };


  // ============================================================
  // HELPERS
  // ============================================================

  const parseJSON = (
    value,
    fallback = []
  ) => {

    try {

      if (!value) {
        return fallback;
      }

      if (Array.isArray(value)) {
        return value;
      }

      return JSON.parse(value);

    } catch {

      return fallback;

    }
  };


  const formatScore = (value) => {

    const score =
      Number(value || 0);

    return `${Math.round(score)}%`;
  };


  const formatDate = (value) => {

    if (!value) {
      return "Unknown date";
    }

    try {

      return new Date(
        value
      ).toLocaleDateString(
        "en-IN",
        {
          day: "numeric",
          month: "short",
          year: "numeric",
        }
      );

    } catch {

      return "Unknown date";

    }
  };


  // ============================================================
  // RESULT DATA
  // ============================================================

  const analysis =
    result?.analysis || null;

  const resume =
    analysis?.resume_data || {};

  const match =
    analysis?.match_result || {};

  const job =
    analysis?.job_description || {};

  const skills =
    resume.skills || [];

  const education =
    resume.education || [];


  // ============================================================
  // UI
  // ============================================================

  return (

    <div className="recruiter-layout individual-layout">

      {/* ======================================================
          SIDEBAR
          ====================================================== */}

      <aside className="recruiter-sidebar">

        <div className="sidebar-brand">

          <div className="brand-mark">
            R
          </div>

          <div>

            <div className="brand-name">
              RAISE
            </div>

            <div className="brand-subtitle">
              Resume Analysis & Intelligent
              Screening Engine
            </div>

          </div>

        </div>


        <nav className="sidebar-nav">

          <div className="nav-section-label">
            WORKSPACE
          </div>


          <Link
            to="/individual"
            className="sidebar-link active"
          >
            <BarChart3 size={18} />
            <span>Overview</span>
          </Link>


          <a
            href="#analyze"
            className="sidebar-link"
          >
            <FileSearch size={18} />
            <span>Analyze resume</span>
          </a>


          <a
            href="#history"
            className="sidebar-link"
          >
            <History size={18} />
            <span>History</span>
          </a>

        </nav>


        <div className="sidebar-bottom">

          <button
            className="sidebar-link sidebar-logout"
            onClick={logout}
          >
            <LogOut size={18} />
            <span>Sign out</span>
          </button>


          <div className="sidebar-user">

            <div className="user-avatar">
              {(user?.full_name || "U")
                .charAt(0)
                .toUpperCase()}
            </div>

            <div className="sidebar-user-info">

              <strong>
                {user?.full_name ||
                  "Individual"}
              </strong>

              <span>
                {user?.email ||
                  "Individual account"}
              </span>

            </div>

          </div>

        </div>

      </aside>


      {/* ======================================================
          MAIN
          ====================================================== */}

      <main className="recruiter-main">

        {/* ====================================================
            HEADER
            ==================================================== */}

        <header className="dashboard-header">

          <div>

            <div className="dashboard-eyebrow">
              INDIVIDUAL WORKSPACE
            </div>

            <h1>
              Good morning,{" "}
              {user?.full_name
                ?.split(" ")[0] ||
                "there"}.
            </h1>

            <p>
              Analyze your resume against a
              job and understand how strong
              your application is.
            </p>

          </div>


          <a
            href="#analyze"
            className="dashboard-primary-button"
          >
            <FileSearch size={17} />
            Analyze my resume
            <ArrowRight size={17} />
          </a>

        </header>


        {/* ====================================================
            STATS
            ==================================================== */}

        <section className="dashboard-stats">

          <div className="stat-card">

            <div className="stat-card-top">

              <span>
                Analyses
              </span>

              <div className="stat-icon">
                <FileSearch size={18} />
              </div>

            </div>

            <strong>
              {history.length}
            </strong>

            <p>
              Resume analyses
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-card-top">

              <span>
                Latest match
              </span>

              <div className="stat-icon">
                <BarChart3 size={18} />
              </div>

            </div>

            <strong>
              {history.length > 0
                ? formatScore(
                    history[0]
                      .match_score
                  )
                : "—"}
            </strong>

            <p>
              Most recent score
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-card-top">

              <span>
                Resume
              </span>

              <div className="stat-icon">
                <User size={18} />
              </div>

            </div>

            <strong>
              {resume.candidate_name
                ? "Ready"
                : "—"}
            </strong>

            <p>
              Candidate profile
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-card-top">

              <span>
                Status
              </span>

              <div className="stat-icon">
                <CheckCircle2 size={18} />
              </div>

            </div>

            <strong>
              {result
                ? "Analyzed"
                : "Ready"}
            </strong>

            <p>
              Workspace status
            </p>

          </div>

        </section>


        {/* ====================================================
            ANALYSIS FORM
            ==================================================== */}

        <section
          id="analyze"
          className="individual-analysis-section"
        >

          <div className="individual-section-heading">

            <div>

              <span className="panel-eyebrow">
                RESUME ANALYSIS
              </span>

              <h2>
                See how your resume matches.
              </h2>

              <p>
                Upload your resume and provide
                the job description. RAISE will
                analyze your skills, experience,
                education and overall fit.
              </p>

            </div>

          </div>


          <form
            className="individual-analysis-form"
            onSubmit={handleAnalyze}
          >

            {/* JOB INFORMATION */}

            <div className="individual-form-card">

              <div className="individual-form-title">

                <span>01</span>

                <div>
                  <h3>
                    Job information
                  </h3>

                  <p>
                    Tell us about the role
                    you're applying for.
                  </p>
                </div>

              </div>


              <div className="individual-fields">

                <label>

                  <span>
                    Job title
                  </span>

                  <input
                    type="text"
                    placeholder="e.g. Software Engineer"
                    value={jobTitle}
                    onChange={(event) =>
                      setJobTitle(
                        event.target.value
                      )
                    }
                  />

                </label>


                <label>

                  <span>
                    Company
                  </span>

                  <input
                    type="text"
                    placeholder="e.g. Microsoft"
                    value={companyName}
                    onChange={(event) =>
                      setCompanyName(
                        event.target.value
                      )
                    }
                  />

                </label>

              </div>


              <label className="individual-full-field">

                <span>
                  Job description
                </span>

                <textarea
                  rows="9"
                  placeholder="Paste the job description here..."
                  value={jobDescription}
                  onChange={(event) =>
                    setJobDescription(
                      event.target.value
                    )
                  }
                />

              </label>

            </div>


            {/* RESUME */}

            <div className="individual-form-card">

              <div className="individual-form-title">

                <span>02</span>

                <div>
                  <h3>
                    Your resume
                  </h3>

                  <p>
                    Upload the resume you want
                    RAISE to evaluate.
                  </p>
                </div>

              </div>


              {!resumeFile ? (

                <label className="individual-upload-area">

                  <input
                    type="file"
                    accept=".pdf,.txt"
                    onChange={
                      handleFileChange
                    }
                  />

                  <Upload size={30} />

                  <strong>
                    Upload your resume
                  </strong>

                  <span>
                    PDF or TXT · One resume
                  </span>

                </label>

              ) : (

                <div className="individual-uploaded-file">

                  <div className="individual-file-icon">
                    <FileText size={20} />
                  </div>

                  <div>

                    <strong>
                      {resumeFile.name}
                    </strong>

                    <span>
                      {(
                        resumeFile.size /
                        1024
                      ).toFixed(1)} KB
                    </span>

                  </div>

                  <button
                    type="button"
                    onClick={removeFile}
                    aria-label="Remove resume"
                  >
                    <X size={18} />
                  </button>

                </div>

              )}

            </div>


            {/* ERRORS */}

            {error && (

              <div className="individual-message individual-error">

                <span>
                  {error}
                </span>

              </div>

            )}


            {/* SUCCESS */}

            {success && (

              <div className="individual-message individual-success">

                <CheckCircle2 size={18} />

                <span>
                  {success}
                </span>

              </div>

            )}


            {/* SUBMIT */}

            <div className="individual-submit-row">

              <button
                type="submit"
                className="dashboard-primary-button"
                disabled={loading}
              >

                {loading ? (
                  <>
                    <span className="individual-spinner" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <FileSearch size={17} />
                    Analyze my resume
                    <ArrowRight size={17} />
                  </>
                )}

              </button>

            </div>

          </form>

        </section>


        {/* ====================================================
            RESULT
            ==================================================== */}

        {result && (

          <section
            id="individual-result"
            className="individual-result-section"
          >

            <div className="individual-result-header">

              <div>

                <span className="panel-eyebrow">
                  ANALYSIS COMPLETE
                </span>

                <h2>
                  Your resume assessment
                </h2>

                <p>
                  {job.title ||
                    jobTitle}
                  {job.company &&
                    job.company !==
                      "Unknown Company"
                    ? ` · ${job.company}`
                    : ""}
                </p>

              </div>

              <div className="individual-overall-score">

                <span>
                  Overall match
                </span>

                <strong>
                  {formatScore(
                    match.match_score
                  )}
                </strong>

              </div>

            </div>


            {/* SUCCESS */}

            <div className="individual-result-success">

              <CheckCircle2 size={18} />

              <span>
                Your resume was successfully
                analyzed.
              </span>

            </div>


            {/* SCORE CARDS */}

            <div className="individual-score-grid">

              <div className="individual-score-card">

                <span>
                  Skills match
                </span>

                <strong>
                  {formatScore(
                    match.skill_match_score
                  )}
                </strong>

              </div>


              <div className="individual-score-card">

                <span>
                  Experience match
                </span>

                <strong>
                  {formatScore(
                    match.experience_match_score
                  )}
                </strong>

              </div>


              <div className="individual-score-card">

                <span>
                  Education match
                </span>

                <strong>
                  {formatScore(
                    match.education_match_score
                  )}
                </strong>

              </div>

            </div>


            {/* PROFILE */}

            <div className="individual-result-card">

              <div className="individual-result-card-heading">

                <div className="individual-result-avatar">
                  {(resume.candidate_name ||
                    "C")
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <div>

                  <h3>
                    {resume.candidate_name ||
                      user?.full_name ||
                      "Your profile"}
                  </h3>

                  <p>
                    {resume.email ||
                      user?.email ||
                      "Email not found"}
                  </p>

                </div>

              </div>


              <div className="individual-skills">

                {skills.length > 0 ? (

                  skills
                    .slice(0, 12)
                    .map(
                      (skill, index) => (
                        <span
                          key={index}
                        >
                          {skill}
                        </span>
                      )
                    )

                ) : (

                  <span>
                    No skills detected
                  </span>

                )}

              </div>

            </div>


            {/* EDUCATION / EXPERIENCE */}

            <div className="individual-detail-grid">

              <div className="individual-result-card">

                <span className="individual-card-label">
                  EXPERIENCE
                </span>

                <strong className="individual-large-value">

                  {Number(
                    resume.experience_years ||
                      0
                  )}{" "}

                  {Number(
                    resume.experience_years ||
                      0
                  ) === 1
                    ? "year"
                    : "years"}

                </strong>

                <p>
                  Professional experience
                  detected in your resume.
                </p>

              </div>


              <div className="individual-result-card">

                <span className="individual-card-label">
                  EDUCATION
                </span>

                {education.length > 0 ? (

                  education.map(
                    (item, index) => (

                      <div
                        key={index}
                        className="individual-education-item"
                      >

                        <strong>
                          {item.degree ||
                            "Degree"}
                        </strong>

                        <span>
                          {[
                            item.field,
                            item.institution,
                            item.year,
                          ]
                            .filter(Boolean)
                            .join(
                              " · "
                            )}
                        </span>

                      </div>

                    )
                  )

                ) : (

                  <p>
                    Education information
                    was not detected.
                  </p>

                )}

              </div>

            </div>


            {/* AI ASSESSMENT */}

            {match.justification && (

              <div className="individual-assessment">

                <span>
                  AI ASSESSMENT
                </span>

                <h3>
                  RAISE's recommendation
                </h3>

                <p>
                  {match.justification}
                </p>

              </div>

            )}

          </section>

        )}


        {/* ====================================================
            HISTORY
            ==================================================== */}

        <section
          id="history"
          className="individual-history-section"
        >

          <div className="panel-header">

            <div>

              <span className="panel-eyebrow">
                ACTIVITY
              </span>

              <h2>
                Your recent analyses
              </h2>

            </div>

          </div>


          {historyLoading ? (

            <div className="individual-history-empty">
              Loading your analyses...
            </div>

          ) : history.length === 0 ? (

            <div className="individual-history-empty">

              <div className="empty-icon">
                <Clock3 size={22} />
              </div>

              <h3>
                No analyses yet
              </h3>

              <p>
                Upload your resume above to
                get your first match score.
              </p>

              <a
                href="#analyze"
                className="secondary-button"
              >
                Analyze my resume
                <ArrowRight size={16} />
              </a>

            </div>

          ) : (

            <div className="individual-history-list">

              {history.map(
                (item, index) => (

                  <div
                    className="individual-history-item"
                    key={
                      item.id ||
                      index
                    }
                  >

                    <div className="individual-history-icon">
                      <History size={18} />
                    </div>

                    <div className="individual-history-info">

                      <strong>
                        {item.job_title ||
                          "Resume analysis"}
                      </strong>

                      <span>
                        {item.company_name &&
                        item.company_name !==
                          "Unknown Company"
                          ? item.company_name
                          : "RAISE analysis"}
                      </span>

                    </div>

                    <div className="individual-history-score">

                      <strong>
                        {formatScore(
                          item.match_score
                        )}
                      </strong>

                      <span>
                        {formatDate(
                          item.processed_at ||
                          item.created_at
                        )}
                      </span>

                    </div>

                  </div>

                )
              )}

            </div>

          )}

        </section>


        {/* FOOTER */}

        <footer className="individual-footer">

          <span>
            RAISE
          </span>

          <p>
            Resume Analysis & Intelligent
            Screening Engine
          </p>

        </footer>

      </main>

    </div>
  );
}

export default IndividualDashboard;