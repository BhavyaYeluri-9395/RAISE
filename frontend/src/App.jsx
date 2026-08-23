import "./App.css";

import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";

import RecruiterDashboard from "./pages/recruiter/RecruiterDashboard";
import IndividualDashboard from "./pages/individual/IndividualDashboard";
import Screening from "./pages/Screening";

import History from "./pages/recruiter/History";
import ScreeningResults from "./pages/recruiter/ScreeningResults";

import ProtectedRoute from "./components/ProtectedRoute";

function Placeholder({ title }) {
  return (
    <div className="placeholder-page">
      <div>
        <span>RAISE WORKSPACE</span>

        <h1>{title}</h1>

        <p>
          This section is coming next.
        </p>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ==================================================
            PUBLIC ROUTES
            ================================================== */}

        <Route
          path="/"
          element={<Landing />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />


        {/* ==================================================
            RECRUITER PROTECTED ROUTES
            ================================================== */}

        <Route
          element={
            <ProtectedRoute allowedRole="recruiter" />
          }
        >

          {/* Dashboard */}
          <Route
            path="/recruiter"
            element={<RecruiterDashboard />}
          />

          {/* New Screening */}
          <Route
            path="/recruiter/screening"
            element={<Screening />}
          />

          {/* Screening Results */}
          <Route
            path="/recruiter/screening/:sessionId"
            element={<ScreeningResults />}
          />

          {/* Candidates */}
          <Route
            path="/recruiter/candidates"
            element={
              <Placeholder title="Candidates" />
            }
          />

          {/* Shortlist */}
          <Route
            path="/recruiter/shortlist"
            element={
              <Placeholder title="Shortlist" />
            }
          />

          {/* Analytics */}
          <Route
            path="/recruiter/analytics"
            element={
              <Placeholder title="Analytics" />
            }
          />

          {/* History */}
          <Route
            path="/recruiter/history"
            element={<History />}
          />

        </Route>


        {/* ==================================================
            INDIVIDUAL PROTECTED ROUTES
            ================================================== */}

        <Route
          element={
            <ProtectedRoute allowedRole="individual" />
          }
        >

          <Route
            path="/individual"
            element={<IndividualDashboard />}
          />

        </Route>


        {/* ==================================================
            FALLBACK
            ================================================== */}

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;