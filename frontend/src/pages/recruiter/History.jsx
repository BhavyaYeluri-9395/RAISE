import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import {
  ArrowRight,
  Clock,
  Users,
  CheckCircle2,
  SlidersHorizontal,
  History as HistoryIcon,
} from "lucide-react";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const token = localStorage.getItem("raise_token");

        if (!token) {
          setError("You are not authenticated.");
          return;
        }

        const response = await axios.get(
          `${API_URL}/screening-history`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setHistory(response.data.history || []);
      } catch (err) {
        console.error("History error:", err);

        if (err.response?.status === 401) {
          localStorage.removeItem("raise_token");
          setError("Your session has expired. Please sign in again.");
        } else {
          setError(
            err.response?.data?.detail ||
              "Unable to load screening history."
          );
        }
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  const formatDate = (date) => {
    if (!date) return "Unknown date";

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return "Unknown date";
    }

    return parsedDate.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  return (
    <div className="history-page">

      {/* HEADER */}
      <div className="history-header">
        <div>
          <span className="section-label">
            RAISE WORKSPACE
          </span>

          <h1>Screening history</h1>

          <p>
            Review previous candidate screening sessions
            and their results.
          </p>
        </div>

        <Link
          to="/recruiter/screening"
          className="primary-button"
        >
          New screening
          <ArrowRight size={16} />
        </Link>
      </div>

      {/* LOADING */}
      {loading && (
        <div className="history-state">
          Loading your screening history...
        </div>
      )}

      {/* ERROR */}
      {!loading && error && (
        <div className="history-error">
          {error}
        </div>
      )}

      {/* EMPTY */}
      {!loading &&
        !error &&
        history.length === 0 && (
          <div className="history-empty">

            <div className="history-empty-icon">
              <HistoryIcon size={22} />
            </div>

            <h2>No screenings yet</h2>

            <p>
              Once you analyze a group of candidates,
              your screening sessions will appear here.
            </p>

            <Link
              to="/recruiter/screening"
              className="secondary-button"
            >
              Create your first screening
              <ArrowRight size={16} />
            </Link>

          </div>
        )}

      {/* HISTORY */}
      {!loading &&
        !error &&
        history.length > 0 && (
          <div className="history-list">

            {history.map((item) => (
              <div
                className="history-card"
                key={item.session_id}
              >

                <div className="history-card-main">

                  <div className="history-icon">
                    <HistoryIcon size={19} />
                  </div>

                  <div>
                    <div className="history-title-row">

                      <h2>
                        {item.job_title ||
                          "Untitled screening"}
                      </h2>

                      <span className="history-status">
                        Completed
                      </span>

                    </div>

                    <p className="history-company">
                      {item.company_name &&
                      item.company_name !==
                        "Unknown Company"
                        ? item.company_name
                        : "RAISE screening"}
                    </p>
                  </div>

                </div>

                <div className="history-meta">

                  <div>
                    <Users size={16} />
                    <span>
                      {item.total_candidates || 0}{" "}
                      {item.total_candidates === 1
                        ? "candidate"
                        : "candidates"}
                    </span>
                  </div>

                  <div>
                    <CheckCircle2 size={16} />
                    <span>
                      {item.shortlisted_count || 0} shortlisted
                    </span>
                  </div>

                  <div>
                    <SlidersHorizontal size={16} />
                    <span>
                      {Math.round(
                        Number(item.threshold ?? 0.70) * 100
                      )}% threshold
                    </span>
                  </div>

                  <div>
                    <Clock size={16} />
                    <span>
                      {formatDate(item.created_at)}
                    </span>
                  </div>

                </div>

                <div className="history-action">
                  <Link
                    to={`/recruiter/screening/${item.session_id}`}
                    className="history-view-button"
                  >
                    View results
                    <ArrowRight size={16} />
                  </Link>
                </div>

              </div>
            ))}

          </div>
        )}
    </div>
  );
}

export default History;