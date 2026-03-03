import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../services/api.js";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await apiRequest("/auth/register", "POST", { email, password });
      navigate("/login");
    } catch (err) {
      setError(err.message);
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card fade-in">
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>🚀</div>
          <h1>Create account</h1>
          <p className="subtitle">Build your behavioral personality portfolio</p>
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
          <input className="input" type="password" placeholder="Min 6 characters"
            value={password} onChange={(e) => setPassword(e.target.value)} required />

          <button className="button" type="submit"
            style={{ width: "100%", justifyContent: "center", marginTop: 20, padding: 14 }}
            disabled={loading}>
            {loading ? "Creating..." : "Create Account"}
          </button>
        </form>

        <p style={{ marginTop: 20, textAlign: "center", fontSize: 14, color: "var(--ink-muted)" }}>
          Already have an account?{" "}
          <Link to="/login" className="link">Sign in</Link>
        </p>
      </div>
    </div>
  );
}