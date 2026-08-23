import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axios from "axios";
import {
  ArrowLeft,
  CheckCircle2,
} from "lucide-react";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

function ScreeningResults() {
  const { sessionId } = useParams();

  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadResults = async () => {
      try {
        const token = localStorage.getItem("raise_token");

        if (!token) {
          setError("Not authenticated.");
          return;
        }

        const response = await axios.get(
          `${API_URL}/analyses/${sessionId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setAnalyses(response.data.analyses || []);
      } catch (err) {
        console.error(
          "Failed to load screening results:",
          err
        );

        if (err.response?.status === 401) {
          localStorage.removeItem("raise_token");
          setError(
            "Your session has expired. Please sign in again."
          );
        } else {
          setError(
            err.response?.data?.detail ||
              "Unable to load screening results."
          );
        }
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      loadResults();
    } else {
      setError("Invalid screening session.");
      setLoading(false);
    }
  }, [sessionId]);

  const parseJSON = (value, fallback = []) => {
    try {
      if (!value) return fallback;

      if (Array.isArray(value)) {
        return value;
      }

      const parsed = JSON.parse(value);

      return Array.isArray(parsed)
        ? parsed
        : fallback;
    } catch {
      return fallback;
    }
  };

  const getCandidateName = (candidate) => {
    const name = candidate.candidate_name;

    if (
      typeof name === "string" &&
      name.trim() &&
      name.trim().toLowerCase() !== "candidate"
    ) {
      return name.trim();
    }

    return "Candidate";
  };

  const getSkills = (candidate) => {
    return parseJSON(candidate.skills, [])
      .filter(Boolean)
      .slice(0, 8);
  };

  const formatScore = (value) => {
    const score = Number(value || 0);
    return `${Math.round(score)}%`;
  };

  /* -------------------------------
     LOADING
  -------------------------------- */

  if (loading) {
    return (
      <div className="results-page">
        <div className="results-loading">
          Loading screening results...
        </div>
      </div>
    );
  }

  /* -------------------------------
     ERROR
  -------------------------------- */

  if (error) {
    return (
      <div className="results-page">

        <div className="results-error">

          <h2>
            Unable to load results
          </h2>

          <p>
            {error}
          </p>

          <Link
            to="/recruiter/history"
            className="secondary-button"
          >
            <ArrowLeft size={16} />
            Back to history
          </Link>

        </div>

      </div>
    );
  }

  /* -------------------------------
     EMPTY
  -------------------------------- */

  if (!analyses.length) {
    return (
      <div className="results-page">

        <div className="results-error">

          <h2>
            No results found
          </h2>

          <p>
            This screening session does not contain
            any candidate analyses.
          </p>

          <Link
            to="/recruiter/history"
            className="secondary-button"
          >
            <ArrowLeft size={16} />
            Back to history
          </Link>

        </div>

      </div>
    );
  }

  /* -------------------------------
     SORT WITHOUT MUTATING STATE
  -------------------------------- */

  const sortedAnalyses = [...analyses].sort(
    (a, b) =>
      Number(b.match_score || 0) -
      Number(a.match_score || 0)
  );

  const first = sortedAnalyses[0];

  const shortlisted = sortedAnalyses.filter(
    (candidate) =>
      Number(candidate.is_shortlisted) === 1
  );

  const threshold =
    first.threshold != null
      ? Math.round(Number(first.threshold) * 100)
      : 70;

  return (
    <div className="results-page">

      {/* =========================
          TOP BAR
          ========================= */}

      <div className="results-topbar">

        <Link
          to="/recruiter/history"
          className="back-link"
        >
          <ArrowLeft size={16} />
          Back to history
        </Link>

      </div>


      {/* =========================
          HEADER
          ========================= */}

      <div className="results-header">

        <div>

          <span className="section-label">
            SCREENING COMPLETE
          </span>

          <h1>
            {first.job_title ||
              "Software Engineer"}
          </h1>

          <p>
            {first.company_name &&
            first.company_name !==
              "Unknown Company"
              ? first.company_name
              : "RAISE screening"}{" "}
            · {sortedAnalyses.length} candidates
          </p>

        </div>

        <Link
          to="/recruiter/screening"
          className="secondary-button"
        >
          New screening
        </Link>

      </div>


      {/* =========================
          SUCCESS
          ========================= */}

      <div className="results-success">

        <CheckCircle2 size={19} />

        <span>
          Successfully analyzed{" "}
          <strong>
            {sortedAnalyses.length}
          </strong>{" "}
          candidates.
        </span>

      </div>


      {/* =========================
          SUMMARY
          ========================= */}

      <div className="results-summary">

        <div className="summary-card">

          <span>
            Total candidates
          </span>

          <strong>
            {sortedAnalyses.length}
          </strong>

        </div>


        <div className="summary-card">

          <span>
            Shortlisted
          </span>

          <strong>
            {shortlisted.length}
          </strong>

        </div>


        <div className="summary-card">

          <span>
            Threshold
          </span>

          <strong>
            {threshold}%
          </strong>

        </div>

      </div>


      {/* =========================
          CANDIDATE LIST
          ========================= */}

      <div className="results-list">

        {sortedAnalyses.map(
          (candidate, index) => {

            const candidateName =
              getCandidateName(candidate);

            const skills =
              getSkills(candidate);

            const education =
              parseJSON(
                candidate.education,
                []
              );

            const isShortlisted =
              Number(
                candidate.is_shortlisted
              ) === 1;

            return (
              <div
                className="result-candidate"
                key={
                  candidate.id ||
                  `${candidate.email}-${index}`
                }
              >

                {/* CANDIDATE HEADER */}

                <div className="candidate-top">

                  <div className="candidate-identity">

                    <div className="candidate-avatar">
                      {candidateName
                        .charAt(0)
                        .toUpperCase()}
                    </div>

                    <div>

                      <h2>
                        {candidateName}
                      </h2>

                      <p>
                        {candidate.email ||
                          "Email not found"}
                      </p>

                    </div>

                  </div>


                  {/* MATCH SCORE */}

                  <div className="candidate-match">

                    <span>
                      Match
                    </span>

                    <strong>
                      {formatScore(
                        candidate.match_score
                      )}
                    </strong>

                    {isShortlisted && (
                      <small>
                        Shortlisted
                      </small>
                    )}

                  </div>

                </div>


                {/* SKILLS */}

                <div className="candidate-skills">

                  {skills.length > 0 ? (
                    skills.map(
                      (skill, skillIndex) => (
                        <span
                          key={skillIndex}
                        >
                          {skill}
                        </span>
                      )
                    )
                  ) : (
                    <span>
                      Skills not found
                    </span>
                  )}

                </div>


                {/* SCORE BREAKDOWN */}

                <div className="score-grid">

                  <div>
                    <span>
                      Skills
                    </span>

                    <strong>
                      {formatScore(
                        candidate.skill_match_score
                      )}
                    </strong>
                  </div>


                  <div>
                    <span>
                      Experience
                    </span>

                    <strong>
                      {formatScore(
                        candidate.experience_match_score
                      )}
                    </strong>
                  </div>


                  <div>
                    <span>
                      Education
                    </span>

                    <strong>
                      {formatScore(
                        candidate.education_match_score
                      )}
                    </strong>
                  </div>

                </div>


                {/* EDUCATION */}

                {education.length > 0 && (
                  <div className="candidate-education">

                    <strong>
                      Education
                    </strong>

                    <span>
                      {education
                        .map(
                          (item) =>
                            [
                              item.degree,
                              item.field,
                              item.institution,
                            ]
                              .filter(Boolean)
                              .join(" · ")
                        )
                        .join(" | ")}
                    </span>

                  </div>
                )}


                {/* AI ASSESSMENT */}

                {candidate.justification && (
                  <div className="candidate-assessment">

                    <span className="assessment-label">
                      AI ASSESSMENT
                    </span>

                    <p>
                      {candidate.justification}
                    </p>

                  </div>
                )}

              </div>
            );
          }
        )}

      </div>

    </div>
  );
}

export default ScreeningResults;