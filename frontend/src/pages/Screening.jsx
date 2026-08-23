import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Upload,
  FileText,
  X,
  Loader2,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import axios from "axios";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function Screening() {
  const navigate = useNavigate();

  const [jobTitle, setJobTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [threshold, setThreshold] = useState(70);

  const [files, setFiles] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [results, setResults] = useState(null);

  // ============================================================
  // FILE HANDLING
  // ============================================================

  const handleFiles = (event) => {
    const selected = Array.from(event.target.files || []);

    const valid = selected.filter((file) => {
      const name = file.name.toLowerCase();
      return name.endsWith(".pdf") || name.endsWith(".txt");
    });

    if (valid.length !== selected.length) {
      setError("Only PDF and TXT resume files are supported.");
    } else {
      setError("");
    }

    setFiles((previous) => {
      const combined = [...previous, ...valid];

      const unique = combined.filter(
        (file, index, array) =>
          index ===
          array.findIndex(
            (item) =>
              item.name === file.name &&
              item.size === file.size
          )
      );

      return unique;
    });

    // Allows selecting the same file again later
    event.target.value = "";
  };

  const removeFile = (index) => {
    setFiles((previous) =>
      previous.filter((_, i) => i !== index)
    );
  };

  // ============================================================
  // AUTHENTICATION HELPER
  // ============================================================

  const getAuthToken = () => {
    const token = localStorage.getItem("raise_token");

    if (!token) {
      setError(
        "Your session has expired or you are not signed in. Please sign in again."
      );

      navigate("/login");

      return null;
    }

    return token;
  };

  // ============================================================
  // SUBMIT SCREENING
  // ============================================================

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setResults(null);

    // ------------------------------------------------------------
    // Validate form
    // ------------------------------------------------------------

    if (!jobTitle.trim()) {
      setError("Please enter a job title.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter the job description.");
      return;
    }

    if (files.length === 0) {
      setError("Please upload at least one resume.");
      return;
    }

    // ------------------------------------------------------------
    // Get JWT token
    // ------------------------------------------------------------

    const token = getAuthToken();

    if (!token) {
      return;
    }

    setLoading(true);

    try {
      // ----------------------------------------------------------
      // Create multipart/form-data
      // ----------------------------------------------------------

      const formData = new FormData();

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
        companyName || "Unknown Company"
      );

      // Backend expects threshold as 0-1
      formData.append(
        "threshold",
        String(threshold / 100)
      );

      files.forEach((file) => {
        formData.append("files", file);
      });

      // ----------------------------------------------------------
      // Send authenticated request
      // ----------------------------------------------------------

      const response = await axios.post(
        `${API_URL}/shortlist`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = response.data;

      // ----------------------------------------------------------
      // Save results
      // ----------------------------------------------------------

      setResults(data);

      setSuccess(
        `Successfully analyzed ${data.total_candidates} candidate${
          data.total_candidates === 1 ? "" : "s"
        }.`
      );

      // ----------------------------------------------------------
      // Save screening history
      // ----------------------------------------------------------

      const historyEntry = {
        id: Date.now(),
        createdAt: new Date().toISOString(),

        jobTitle,
        companyName: companyName || "Unknown Company",

        totalCandidates: data.total_candidates || 0,
        shortlistedCount: data.shortlisted_count || 0,

        candidates: data.candidates || [],
      };

      let existingHistory = [];

      try {
        existingHistory = JSON.parse(
          localStorage.getItem("raise_history") || "[]"
        );

        if (!Array.isArray(existingHistory)) {
          existingHistory = [];
        }
      } catch {
        existingHistory = [];
      }

      localStorage.setItem(
        "raise_history",
        JSON.stringify(
          [historyEntry, ...existingHistory].slice(0, 20)
        )
      );

      // ----------------------------------------------------------
      // Save latest results
      // ----------------------------------------------------------

      localStorage.setItem(
        "raise_latest_results",
        JSON.stringify({
          jobTitle,
          companyName,
          threshold,
          ...data,
        })
      );

    } catch (err) {
      console.error("Screening error:", err);

      // ----------------------------------------------------------
      // Handle authentication failure
      // ----------------------------------------------------------

      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");

        setError(
          "Your login session is invalid or expired. Please sign in again."
        );

        navigate("/login");

        return;
      }

      // ----------------------------------------------------------
      // Handle validation errors
      // ----------------------------------------------------------

      if (err.response?.status === 422) {
        const detail = err.response?.data?.detail;

        if (Array.isArray(detail)) {
          setError(
            detail
              .map((item) => item.msg || "Invalid input")
              .join(", ")
          );
        } else {
          setError(
            detail || "Some of the submitted information is invalid."
          );
        }

        return;
      }

      // ----------------------------------------------------------
      // Handle server errors
      // ----------------------------------------------------------

      const message =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Unable to analyze the resumes. Make sure the backend is running.";

      setError(
        typeof message === "string"
          ? message
          : "Something went wrong while analyzing the resumes."
      );

    } finally {
      setLoading(false);
    }
  };

  const candidates = results?.candidates || [];

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="screening-page">

      {/* ========================================================
          HEADER
      ======================================================== */}

      <header className="screening-header">

        <Link
          to="/recruiter"
          className="screening-back"
        >
          <ArrowLeft size={17} />
          Dashboard
        </Link>

        <div className="screening-brand">

          <div className="brand-mark">
            R
          </div>

          <div>
            <strong>RAISE</strong>
            <span>Resume Screening</span>
          </div>

        </div>

        <div />

      </header>

      {/* ========================================================
          MAIN
      ======================================================== */}

      <main className="screening-main">

        {/* ======================================================
            NEW SCREENING FORM
        ====================================================== */}

        {!results && (
          <>
            <div className="screening-heading">

              <div>

                <span className="dashboard-eyebrow">
                  NEW SCREENING
                </span>

                <h1>
                  Find your strongest candidates.
                </h1>

                <p>
                  Upload a job description and resumes.
                  RAISE will extract candidate information,
                  calculate match scores and build a shortlist.
                </p>

              </div>

            </div>

            <form
              className="screening-form"
              onSubmit={handleSubmit}
            >

              {/* ==================================================
                  JOB INFORMATION
              ================================================== */}

              <section className="screening-card">

                <div className="screening-card-heading">

                  <div>
                    <span>01</span>
                    <h2>Job information</h2>
                  </div>

                </div>

                <div className="screening-fields">

                  <label>
                    Job title

                    <input
                      type="text"
                      placeholder="e.g. Software Engineer"
                      value={jobTitle}
                      onChange={(event) =>
                        setJobTitle(event.target.value)
                      }
                    />

                  </label>

                  <label>
                    Company

                    <input
                      type="text"
                      placeholder="e.g. RAISE Technologies"
                      value={companyName}
                      onChange={(event) =>
                        setCompanyName(event.target.value)
                      }
                    />

                  </label>

                </div>

                <label className="full-field">

                  Job description

                  <textarea
                    rows="9"
                    placeholder="Paste the complete job description here..."
                    value={jobDescription}
                    onChange={(event) =>
                      setJobDescription(event.target.value)
                    }
                  />

                </label>

              </section>

              {/* ==================================================
                  RESUMES
              ================================================== */}

              <section className="screening-card">

                <div className="screening-card-heading">

                  <div>
                    <span>02</span>
                    <h2>Candidate resumes</h2>
                  </div>

                  <small>
                    PDF or TXT
                  </small>

                </div>

                <label className="upload-area">

                  <input
                    type="file"
                    accept=".pdf,.txt"
                    multiple
                    onChange={handleFiles}
                  />

                  <Upload size={28} />

                  <strong>
                    Upload resumes
                  </strong>

                  <span>
                    Select one or multiple PDF/TXT files
                  </span>

                </label>

                {files.length > 0 && (

                  <div className="file-list">

                    {files.map((file, index) => (

                      <div
                        className="uploaded-file"
                        key={`${file.name}-${file.size}`}
                      >

                        <FileText size={18} />

                        <div>

                          <strong>
                            {file.name}
                          </strong>

                          <span>
                            {(file.size / 1024).toFixed(1)} KB
                          </span>

                        </div>

                        <button
                          type="button"
                          onClick={() =>
                            removeFile(index)
                          }
                          aria-label={`Remove ${file.name}`}
                        >
                          <X size={16} />
                        </button>

                      </div>

                    ))}

                  </div>

                )}

              </section>

              {/* ==================================================
                  SHORTLIST SETTINGS
              ================================================== */}

              <section className="screening-card">

                <div className="screening-card-heading">

                  <div>
                    <span>03</span>
                    <h2>Shortlist settings</h2>
                  </div>

                </div>

                <div className="threshold-setting">

                  <div>

                    <strong>
                      Shortlist threshold
                    </strong>

                    <p>
                      Candidates scoring at or above this
                      percentage will be shortlisted.
                    </p>

                  </div>

                  <strong className="threshold-value">
                    {threshold}%
                  </strong>

                </div>

                <input
                  className="threshold-slider"
                  type="range"
                  min="50"
                  max="95"
                  step="5"
                  value={threshold}
                  onChange={(event) =>
                    setThreshold(
                      Number(event.target.value)
                    )
                  }
                />

              </section>

              {/* ==================================================
                  ERROR
              ================================================== */}

              {error && (

                <div className="screening-message error">

                  <AlertCircle size={18} />

                  {error}

                </div>

              )}

              {/* ==================================================
                  SUBMIT
              ================================================== */}

              <button
                type="submit"
                className="dashboard-primary-button screening-submit"
                disabled={loading}
              >

                {loading ? (

                  <>
                    <Loader2
                      size={18}
                      className="spin"
                    />

                    Analyzing candidates...
                  </>

                ) : (

                  <>
                    Analyze & Shortlist

                    <CheckCircle2 size={18} />
                  </>

                )}

              </button>

            </form>
          </>
        )}

        {/* ======================================================
            RESULTS
        ====================================================== */}

        {results && (

          <section className="screening-results">

            <div className="results-header">

              <div>

                <span className="dashboard-eyebrow">
                  SCREENING COMPLETE
                </span>

                <h1>
                  {jobTitle}
                </h1>

                <p>
                  {companyName || "Unknown Company"} ·{" "}
                  {results.total_candidates} candidates
                </p>

              </div>

              <button
                className="secondary-button"
                onClick={() => {
                  setResults(null);
                  setSuccess("");
                  setError("");
                }}
              >
                New screening
              </button>

            </div>

            {/* ==================================================
                SUCCESS MESSAGE
            ================================================== */}

            {success && (

              <div className="screening-message success">

                <CheckCircle2 size={18} />

                {success}

              </div>

            )}

            {/* ==================================================
                STATS
            ================================================== */}

            <div className="result-stats">

              <div>

                <span>
                  Total candidates
                </span>

                <strong>
                  {results.total_candidates || 0}
                </strong>

              </div>

              <div>

                <span>
                  Shortlisted
                </span>

                <strong>
                  {results.shortlisted_count || 0}
                </strong>

              </div>

              <div>

                <span>
                  Threshold
                </span>

                <strong>
                  {threshold}%
                </strong>

              </div>

            </div>

            {/* ==================================================
                CANDIDATE RESULTS
            ================================================== */}

            <div className="candidate-results">

              {candidates.length === 0 ? (

                <div className="screening-card empty-results">

                  <h2>
                    No candidates matched the threshold.
                  </h2>

                  <p>
                    Try lowering the shortlist threshold
                    or reviewing the job description.
                  </p>

                </div>

              ) : (

                candidates.map((candidate, index) => {

                  const resume =
                    candidate.resume_data || {};

                  const match =
                    candidate.match_result || {};

                  const score =
                    Number(match.match_score || 0);

                  return (

                    <article
                      className="candidate-result"
                      key={`${resume.email || "candidate"}-${index}`}
                    >

                      {/* Candidate information */}

                      <div className="candidate-result-main">

                        <div className="result-avatar">

                          {(resume.candidate_name || "C")
                            .charAt(0)
                            .toUpperCase()}

                        </div>

                        <div>

                          <h2>
                            {resume.candidate_name ||
                              "Candidate"}
                          </h2>

                          <p>
                            {resume.email ||
                              "Email not found"}
                          </p>

                          <div className="result-tags">

                            {(resume.skills || [])
                              .slice(0, 6)
                              .map((skill) => (

                                <span key={skill}>
                                  {skill}
                                </span>

                              ))}

                          </div>

                        </div>

                      </div>

                      {/* Score */}

                      <div className="result-score">

                        <div>

                          <span>
                            Match
                          </span>

                          <strong>
                            {score.toFixed(0)}%
                          </strong>

                        </div>

                        <div
                          className={`result-status ${
                            match.is_shortlisted
                              ? "shortlisted"
                              : "review"
                          }`}
                        >

                          {match.is_shortlisted
                            ? "Shortlisted"
                            : "Review"}

                        </div>

                      </div>

                      {/* Match details */}

                      <div className="result-details">

                        <div>

                          <span>
                            Skills
                          </span>

                          <strong>
                            {Number(
                              match.skill_match_score || 0
                            ).toFixed(0)}
                            %
                          </strong>

                        </div>

                        <div>

                          <span>
                            Experience
                          </span>

                          <strong>
                            {Number(
                              match.experience_match_score || 0
                            ).toFixed(0)}
                            %
                          </strong>

                        </div>

                        <div>

                          <span>
                            Education
                          </span>

                          <strong>
                            {Number(
                              match.education_match_score || 0
                            ).toFixed(0)}
                            %
                          </strong>

                        </div>

                      </div>

                      {/* AI justification */}

                      {match.justification && (

                        <div className="result-justification">

                          <span>
                            AI assessment
                          </span>

                          <p>
                            {match.justification}
                          </p>

                        </div>

                      )}

                    </article>

                  );

                })

              )}

            </div>

          </section>

        )}

      </main>

    </div>
  );
}

export default Screening;