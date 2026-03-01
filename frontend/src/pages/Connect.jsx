import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiRequest } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";

export default function Connect() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState("");
  const { token } = useAuth();
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = params.get("code");
    if (code) {
      apiRequest("/github/callback?code=" + code, "POST", null, token)
        .then(() => loadStatus())
        .catch((err) => setError(err.message));
    } else {
      loadStatus();
    }
  }, []);

  const loadStatus = async () => {
    try {
      const data = await apiRequest("/github/status", "GET", null, token);
      setStatus(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const connectGitHub = async () => {
    const data = await apiRequest("/github/authorize");
    window.location.href = data.authorization_url;
  };

  const startAnalysis = async () => {
    await apiRequest("/github/start-analysis", "POST", null, token);
    navigate("/progress");
  };

  if (!status) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container fade-in">
      <div className="card">
        <h1>Connect GitHub</h1>
        {error && <p style={{ color: "#b91c1c" }}>{error}</p>}
        {status.connected ? (
          <>
            <p>Connected as <strong>{status.github_login}</strong></p>
            <button className="button" onClick={startAnalysis}>Run analysis</button>
          </>
        ) : (
          <button className="button" onClick={connectGitHub}>Authorize GitHub</button>
        )}
      </div>
    </div>
  );
}
