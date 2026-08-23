import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Prevent duplicate login requests
  const submitting = useRef(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Stop duplicate submissions
    if (submitting.current) {
      return;
    }

    if (!email.trim() || !password) {
      setError("Please enter your email and password.");
      return;
    }

    submitting.current = true;
    setError("");
    setLoading(true);

    try {
      const loggedInUser = await login(
        email.trim(),
        password
      );

      console.log("RAISE login successful:", loggedInUser);

      if (loggedInUser?.role === "recruiter") {
        navigate("/recruiter", { replace: true });
      } else if (loggedInUser?.role === "individual") {
        navigate("/individual", { replace: true });
      } else {
        throw new Error("Invalid user role.");
      }

    } catch (err) {
      console.error("RAISE login error:", err);

      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to sign in. Please check your credentials.";

      setError(message);

      submitting.current = false;
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">

      <div className="auth-card">

        {/* BRAND */}

        <div className="auth-brand">
          <div className="brand-mark">
            R
          </div>

          <strong>RAISE</strong>
        </div>

        {/* HEADING */}

        <div className="auth-heading">

          <span>WELCOME BACK</span>

          <h1>
            Sign in to RAISE
          </h1>

          <p>
            Access your resume analysis and
            screening workspace.
          </p>

        </div>

        {/* FORM */}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >

          <label>
            Email

            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              autoComplete="email"
              disabled={loading}
              required
            />
          </label>

          <label>
            Password

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              autoComplete="current-password"
              disabled={loading}
              required
            />
          </label>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="primary-button auth-button"
            disabled={loading}
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>

        </form>

        {/* REGISTER */}

        <p className="auth-switch">
          Don't have an account?{" "}
          <Link to="/register">
            Create one
          </Link>
        </p>

      </div>

    </div>
  );
}

export default Login;
