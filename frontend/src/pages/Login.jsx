import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const data = await apiRequest("/auth/login", "POST", { email, password });
      login(data.access_token);
      navigate("/connect");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="container fade-in">
      <div className="card">
        <h1>Welcome back</h1>
        <p>Access your Life Resume dashboard.</p>
        {error && <p style={{ color: "#b91c1c" }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
          <label>Password</label>
          <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <div style={{ marginTop: 16 }}>
            <button className="button" type="submit">Login</button>
          </div>
        </form>
        <p style={{ marginTop: 16 }}>
          New here? <Link to="/register">Create account</Link>
        </p>
      </div>
    </div>
  );
}
