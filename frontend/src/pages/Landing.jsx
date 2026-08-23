import { useNavigate } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  FileSearch,
  Users
} from "lucide-react";

function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">

      <header className="navbar">
        <div className="brand">
          <div className="brand-mark">R</div>

          <div>
            <div className="brand-name">RAISE</div>
            <div className="brand-subtitle">
              Resume Analysis & Intelligent Screening Engine
            </div>
          </div>
        </div>

        <div className="nav-actions">
          <button
            className="nav-login"
            onClick={() => navigate("/login")}
          >
            Sign in
          </button>

          <button
            className="nav-register"
            onClick={() => navigate("/register")}
          >
            Create account
          </button>
        </div>
      </header>

      <main>

        <section className="hero">

          <div className="hero-content">

            <div className="eyebrow">
              Intelligent Resume Screening
            </div>

            <h1>
              Find the right
              <br />
              <span>candidate faster.</span>
            </h1>

            <p>
              RAISE analyzes resumes against job requirements,
              identifies meaningful matches, and turns candidate
              information into clear, actionable insights.
            </p>

            <div className="hero-actions">

              <button
                className="primary-button"
                onClick={() => navigate("/register")}
              >
                Get started
                <ArrowRight size={18} />
              </button>

              <button
                className="secondary-button"
                onClick={() => navigate("/login")}
              >
                Sign in
              </button>

            </div>

          </div>

          <div className="hero-visual">

            <div className="analysis-card">

              <div className="analysis-header">
                <div>
                  <span className="small-label">
                    Candidate analysis
                  </span>

                  <h3>Software Engineer</h3>
                </div>

                <div className="score-circle">
                  87
                </div>
              </div>

              <div className="score-bar">
                <div />
              </div>

              <div className="analysis-grid">

                <div className="metric-card">
                  <FileSearch size={18} />
                  <span>Skills</span>
                  <strong>92%</strong>
                </div>

                <div className="metric-card">
                  <BarChart3 size={18} />
                  <span>Experience</span>
                  <strong>84%</strong>
                </div>

                <div className="metric-card">
                  <Users size={18} />
                  <span>Overall fit</span>
                  <strong>87%</strong>
                </div>

              </div>

              <div className="candidate-preview">

                <div className="candidate-avatar">
                  JS
                </div>

                <div className="candidate-info">
                  <strong>Candidate Profile</strong>
                  <span>
                    Python · SQL · Machine Learning · Git
                  </span>
                </div>

                <div className="candidate-status">
                  Strong match
                </div>

              </div>

            </div>

          </div>

        </section>

        <section className="choose-section">

          <div className="section-heading">
            <span>GET STARTED</span>

            <h2>
              Choose how you want to use RAISE.
            </h2>

            <p>
              Whether you're evaluating your own resume or
              screening an entire candidate pool, RAISE gives
              you the tools to make better decisions.
            </p>
          </div>

          <div className="role-grid">

            <button
              className="role-card"
              onClick={() => navigate("/register?role=individual")}
            >
              <div className="role-icon">
                <FileSearch size={24} />
              </div>

              <div className="role-content">
                <span className="role-label">
                  FOR INDIVIDUALS
                </span>

                <h3>
                  Analyze my resume
                </h3>

                <p>
                  Understand how well your resume matches a
                  specific job and discover the skills or
                  experience you can improve.
                </p>

                <div className="role-link">
                  Continue as individual
                  <ArrowRight size={17} />
                </div>
              </div>
            </button>

            <button
              className="role-card recruiter-card"
              onClick={() => navigate("/register?role=recruiter")}
            >
              <div className="role-icon">
                <Users size={24} />
              </div>

              <div className="role-content">
                <span className="role-label">
                  FOR RECRUITERS
                </span>

                <h3>
                  Screen candidates
                </h3>

                <p>
                  Upload a job description and multiple resumes,
                  rank candidates, compare profiles, and build
                  your shortlist.
                </p>

                <div className="role-link">
                  Continue as recruiter
                  <ArrowRight size={17} />
                </div>
              </div>
            </button>

          </div>

        </section>

      </main>

      <footer className="footer">
        <span>RAISE</span>
        <span>
          Resume Analysis & Intelligent Screening Engine
        </span>
      </footer>

    </div>
  );
}

export default Landing;
