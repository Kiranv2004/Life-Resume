import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../services/api.js";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await apiRequest("/auth/register", "POST", { email, password });
      navigate("/login");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="container fade-in">
      <div className="card">
        <h1>Create account</h1>
        <p>Start building your behavioral personality portfolio.</p>
        {error && <p style={{ color: "#b91c1c" }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
          <label>Password</label>
          <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <div style={{ marginTop: 16 }}>
            <button className="button" type="submit">Register</button>
          </div>
        </form>
        <p style={{ marginTop: 16 }}>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
