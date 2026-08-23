import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Register() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const { register } = useAuth();

  const initialRole =
    searchParams.get("role") === "recruiter"
      ? "recruiter"
      : "individual";

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState(initialRole);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      await register(
        fullName,
        email,
        password,
        role
      );

      navigate("/login");
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        "Unable to create your account.";

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-brand">
          <div className="brand-mark">R</div>
          <strong>RAISE</strong>
        </div>

        <div className="auth-heading">
          <span>CREATE ACCOUNT</span>

          <h1>Get started with RAISE</h1>

          <p>
            Choose your workspace and start using intelligent
            resume analysis.
          </p>
        </div>

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >

          <label>
            Full name

            <input
              type="text"
              placeholder="Your name"
              value={fullName}
              onChange={(event) =>
                setFullName(event.target.value)
              }
              required
            />
          </label>

          <label>
            Email

            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />
          </label>

          <label>
            Password

            <input
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              minLength={8}
              required
            />
          </label>

          <div className="account-type">
            <span>Account type</span>

            <div className="account-options">

              <label className="account-option">
                <input
                  type="radio"
                  name="role"
                  value="individual"
                  checked={role === "individual"}
                  onChange={(event) =>
                    setRole(event.target.value)
                  }
                />

                Individual
              </label>

              <label className="account-option">
                <input
                  type="radio"
                  name="role"
                  value="recruiter"
                  checked={role === "recruiter"}
                  onChange={(event) =>
                    setRole(event.target.value)
                  }
                />

                Recruiter
              </label>

            </div>
          </div>

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
              ? "Creating account..."
              : "Create account"}
          </button>

        </form>

        <p className="auth-switch">
          Already have an account?{" "}
          <Link to="/login">Sign in</Link>
        </p>

      </div>
    </div>
  );
}

export default Register;