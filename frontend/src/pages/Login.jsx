import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const data = await apiRequest("/auth/login", "POST", { email, password });
      login(data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card fade-in">
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>🧬</div>
          <h1>Welcome back</h1>
          <p className="subtitle">Sign in to your Life Resume dashboard</p>
        </div>

        {error && (
          <div style={{
            background: "rgba(220,38,38,0.1)", border: "1px solid rgba(220,38,38,0.3)",
            borderRadius: 10, padding: "10px 14px", marginBottom: 16,
            color: "#fca5a5", fontSize: 13,
          }}>{error}</div>
        )}

        <form onSubmit={handleSubmit}>
          <label>Email address</label>
          <input className="input" type="email" placeholder="you@example.com"
            value={email} onChange={(e) => setEmail(e.target.value)} required />

          <label>Password</label>
          <input className="input" type="password" placeholder="Enter password"
            value={password} onChange={(e) => setPassword(e.target.value)} required />

          <button className="button" type="submit"
            style={{ width: "100%", justifyContent: "center", marginTop: 20, padding: 14 }}
            disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p style={{ marginTop: 20, textAlign: "center", fontSize: 14, color: "var(--ink-muted)" }}>
          Don't have an account?{" "}
          <Link to="/register" className="link">Create one</Link>
        </p>
      </div>
    </div>
  );
}