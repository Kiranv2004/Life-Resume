import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiRequest } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";

export default function Connect() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [oauthAvailable, setOauthAvailable] = useState(false);
  const [showPat, setShowPat] = useState(false);
  const [pat, setPat] = useState("");
  const [patLoading, setPatLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const { token } = useAuth();
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = params.get("code");
    if (code) {
      apiRequest("/github/callback?code=" + code, "POST", null, token)
        .then(() => loadStatus())
        .catch((err) => { setError("GitHub OAuth callback failed: " + err.message); setLoading(false); });
    } else {
      // Check if OAuth is configured
      apiRequest("/github/authorize", "GET", null, null)
        .then(() => setOauthAvailable(true))
        .catch(() => setOauthAvailable(false))
        .finally(() => loadStatus());
    }
  }, []);

  const loadStatus = async () => {
    try {
      const data = await apiRequest("/github/status", "GET", null, token);
      setStatus(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const connectGitHub = async () => {
    try {
      const data = await apiRequest("/github/authorize", "GET", null, null);
      window.location.href = data.authorization_url;
    } catch (err) {
      setError("GitHub OAuth is not configured. Use a Personal Access Token instead.");
      setShowPat(true);
    }
  };

  const connectWithPat = async () => {
    if (!pat.trim()) { setError("Please enter a valid token"); return; }
    setPatLoading(true);
    setError("");
    try {
      await apiRequest("/github/connect-pat", "POST", { token: pat.trim() }, token);
      setPat("");
      setShowPat(false);
      await loadStatus();
    } catch (err) {
      setError(err.message);
    } finally {
      setPatLoading(false);
    }
  };

  const startAnalysis = async () => {
    setAnalysisLoading(true);
    setError("");
    try {
      await apiRequest("/github/start-analysis", "POST", null, token);
      navigate("/progress");
    } catch (err) {
      setError(err.message);
      setAnalysisLoading(false);
    }
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container fade-in">
      <div className="card">
        <h1>Connect GitHub</h1>
        {error && <p style={{ color: "var(--red)", marginBottom: 12 }}>{error}</p>}

        {status && status.connected ? (
          <div>
            <p style={{ marginBottom: 16 }}>
              Connected as <strong>{status.github_login}</strong> ✓
            </p>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <button className="button" onClick={startAnalysis} disabled={analysisLoading}>
                {analysisLoading ? "Starting..." : "Run Analysis"}
              </button>
              <button className="button secondary" onClick={() => { setShowPat(true); setError(""); }}>
                Reconnect
              </button>
              <button className="button secondary" onClick={() => navigate("/dashboard")}>
                Go to Dashboard
              </button>
            </div>
          </div>
        ) : (
          <div>
            <p style={{ color: "var(--ink-muted)", marginBottom: 16 }}>
              Connect your GitHub account to analyse your coding personality.
            </p>
            {oauthAvailable && (
              <button className="button" onClick={connectGitHub} style={{ marginBottom: 12 }}>
                Authorize with GitHub OAuth
              </button>
            )}
            <div>
              {!showPat ? (
                <button
                  className="button secondary"
                  onClick={() => { setShowPat(true); setError(""); }}
                >
                  Connect with Personal Access Token
                </button>
              ) : null}
            </div>
          </div>
        )}

        {/* ── Token helper — always visible ── */}
        <div style={{
          marginTop: 24, padding: "16px 20px",
          background: "var(--accent-alpha-8)", border: "1px solid var(--accent-alpha-20)",
          borderRadius: 12,
        }}>
          <p style={{ color: "var(--accent-soft)", fontSize: 13, fontWeight: 600, margin: "0 0 6px" }}>
            🔑 Need a GitHub token?
          </p>
          <p style={{ color: "var(--ink-muted)", fontSize: 13, lineHeight: 1.6, margin: 0 }}>
            Go to{" "}
            <a
              href="https://github.com/settings/tokens"
              target="_blank"
              rel="noreferrer"
              style={{
                color: "var(--accent)", fontWeight: 700, textDecoration: "underline",
                textUnderlineOffset: 3,
              }}
            >
              github.com/settings/tokens
            </a>
            {" "}→ <strong style={{ color: "var(--ink)" }}>Generate new token (classic)</strong>
            {" "}→ select the <strong style={{ color: "var(--ink)" }}>repo</strong> scope → copy the token and paste it below.
          </p>
        </div>

        {showPat && (
          <div style={{ marginTop: 20, paddingTop: 20, borderTop: "1px solid var(--border)" }}>
            <h3 style={{ marginBottom: 8 }}>Personal Access Token</h3>
            <input
              className="input"
              type="password"
              placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
              value={pat}
              onChange={(e) => setPat(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && connectWithPat()}
              style={{ marginBottom: 12 }}
            />
            <div style={{ display: "flex", gap: 10 }}>
              <button className="button" onClick={connectWithPat} disabled={patLoading}>
                {patLoading ? "Connecting..." : "Connect"}
              </button>
              <button className="button secondary" onClick={() => { setShowPat(false); setError(""); setPat(""); }}>
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
