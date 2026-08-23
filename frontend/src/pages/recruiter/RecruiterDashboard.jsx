import { Link } from "react-router-dom";
import {
  ArrowRight,
  BarChart3,
  BriefcaseBusiness,
  Clock3,
  FileSearch,
  History,
  LogOut,
  Settings,
  Users,
  UserCheck,
} from "lucide-react";

import { useAuth } from "../../context/AuthContext";

function RecruiterDashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="recruiter-layout">

      {/* SIDEBAR */}
      <aside className="recruiter-sidebar">

        <div className="sidebar-brand">
          <div className="brand-mark">R</div>

          <div>
            <div className="brand-name">RAISE</div>
            <div className="brand-subtitle">
              Resume Analysis & Intelligent Screening Engine
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">

          <div className="nav-section-label">
            WORKSPACE
          </div>

          <Link
            to="/recruiter"
            className="sidebar-link active"
          >
            <BarChart3 size={18} />
            <span>Overview</span>
          </Link>

          <Link
            to="/recruiter/screening"
            className="sidebar-link"
          >
            <FileSearch size={18} />
            <span>New screening</span>
          </Link>

          <Link
            to="/recruiter/candidates"
            className="sidebar-link"
          >
            <Users size={18} />
            <span>Candidates</span>
          </Link>

          <Link
            to="/recruiter/shortlist"
            className="sidebar-link"
          >
            <UserCheck size={18} />
            <span>Shortlist</span>
          </Link>

          <Link
            to="/recruiter/analytics"
            className="sidebar-link"
          >
            <BarChart3 size={18} />
            <span>Analytics</span>
          </Link>

          <Link
            to="/recruiter/history"
            className="sidebar-link"
          >
            <History size={18} />
            <span>History</span>
          </Link>

        </nav>

        <div className="sidebar-bottom">

          <Link
            to="/recruiter/settings"
            className="sidebar-link"
          >
            <Settings size={18} />
            <span>Settings</span>
          </Link>

          <button
            className="sidebar-link sidebar-logout"
            onClick={logout}
          >
            <LogOut size={18} />
            <span>Sign out</span>
          </button>

          <div className="sidebar-user">

            <div className="user-avatar">
              {(user?.full_name || "R")
                .charAt(0)
                .toUpperCase()}
            </div>

            <div className="sidebar-user-info">
              <strong>
                {user?.full_name || "Recruiter"}
              </strong>

              <span>
                {user?.email || "Recruiter account"}
              </span>
            </div>

          </div>

        </div>

      </aside>


      {/* MAIN CONTENT */}
      <main className="recruiter-main">

        {/* TOP BAR */}
        <header className="dashboard-header">

          <div>
            <div className="dashboard-eyebrow">
              RECRUITER WORKSPACE
            </div>

            <h1>
              Good morning,{" "}
              {user?.full_name?.split(" ")[0] || "Recruiter"}.
            </h1>

            <p>
              Manage screenings, evaluate candidates and build
              stronger shortlists.
            </p>
          </div>

          <Link
            to="/recruiter/screening"
            className="dashboard-primary-button"
          >
            <FileSearch size={17} />
            Start screening
            <ArrowRight size={17} />
          </Link>

        </header>


        {/* STAT CARDS */}
        <section className="dashboard-stats">

          <div className="stat-card">

            <div className="stat-card-top">
              <span>Total candidates</span>

              <div className="stat-icon">
                <Users size={18} />
              </div>
            </div>

            <strong>0</strong>

            <p>
              Candidates analyzed
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-card-top">
              <span>Screenings</span>

              <div className="stat-icon">
                <FileSearch size={18} />
              </div>
            </div>

            <strong>0</strong>

            <p>
              Screening sessions
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-card-top">
              <span>Shortlisted</span>

              <div className="stat-icon">
                <UserCheck size={18} />
              </div>
            </div>

            <strong>0</strong>

            <p>
              Candidates shortlisted
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-card-top">
              <span>Average match</span>

              <div className="stat-icon">
                <BarChart3 size={18} />
              </div>
            </div>

            <strong>—</strong>

            <p>
              Across all screenings
            </p>

          </div>

        </section>


        {/* MAIN GRID */}
        <section className="dashboard-grid">

          {/* RECENT SCREENINGS */}
          <div className="dashboard-panel recent-panel">

            <div className="panel-header">

              <div>
                <span className="panel-eyebrow">
                  ACTIVITY
                </span>

                <h2>
                  Recent screenings
                </h2>
              </div>

              <Link
                to="/recruiter/history"
                className="panel-link"
              >
                View history
                <ArrowRight size={15} />
              </Link>

            </div>


            <div className="empty-state">

              <div className="empty-icon">
                <Clock3 size={22} />
              </div>

              <h3>
                No screenings yet
              </h3>

              <p>
                Your recent screening sessions will appear here
                once you analyze a group of candidates.
              </p>

              <Link
                to="/recruiter/screening"
                className="secondary-button"
              >
                Create your first screening
                <ArrowRight size={16} />
              </Link>

            </div>

          </div>


          {/* QUICK ACTIONS */}
          <div className="dashboard-panel">

            <div className="panel-header">

              <div>
                <span className="panel-eyebrow">
                  QUICK ACTIONS
                </span>

                <h2>
                  Get started
                </h2>
              </div>

            </div>


            <div className="quick-actions">

              <Link
                to="/recruiter/screening"
                className="quick-action"
              >
                <div className="quick-action-icon">
                  <FileSearch size={19} />
                </div>

                <div>
                  <strong>
                    New screening
                  </strong>

                  <span>
                    Upload a JD and multiple resumes
                  </span>
                </div>

                <ArrowRight size={16} />
              </Link>


              <Link
                to="/recruiter/candidates"
                className="quick-action"
              >
                <div className="quick-action-icon">
                  <Users size={19} />
                </div>

                <div>
                  <strong>
                    Candidates
                  </strong>

                  <span>
                    Review your candidate pool
                  </span>
                </div>

                <ArrowRight size={16} />
              </Link>


              <Link
                to="/recruiter/analytics"
                className="quick-action"
              >
                <div className="quick-action-icon">
                  <BarChart3 size={19} />
                </div>

                <div>
                  <strong>
                    Analytics
                  </strong>

                  <span>
                    Explore recruitment insights
                  </span>
                </div>

                <ArrowRight size={16} />
              </Link>

            </div>

          </div>

        </section>


        {/* BOTTOM GETTING STARTED */}
        <section className="getting-started">

          <div className="getting-started-content">

            <span className="panel-eyebrow">
              RAISE SCREENING
            </span>

            <h2>
              Screen multiple candidates in one workflow.
            </h2>

            <p>
              Upload a job description and multiple resumes.
              RAISE will extract candidate information, compare
              requirements, calculate match scores and help you
              build a shortlist.
            </p>

            <Link
              to="/recruiter/screening"
              className="dashboard-primary-button"
            >
              Start a screening
              <ArrowRight size={17} />
            </Link>

          </div>


          <div className="getting-started-visual">

            <div className="visual-card">

              <div className="visual-card-header">
                <span>Candidate analysis</span>
                <strong>RAISE</strong>
              </div>

              <div className="visual-score">
                <strong>—</strong>
                <span>Match score</span>
              </div>

              <div className="visual-lines">
                <span />
                <span />
                <span />
              </div>

            </div>

          </div>

        </section>

      </main>

    </div>
  );
}

export default RecruiterDashboard;