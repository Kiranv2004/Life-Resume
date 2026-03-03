import { useEffect, useState } from "react";
import { apiRequest } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";
import ActivityHeatmap from "../components/ActivityHeatmap.jsx";
import DevBioCard from "../components/DevBioCard.jsx";
import ComparePanel from "../components/ComparePanel.jsx";

export default function Profile() {
  const { token } = useAuth();
  const [summary, setSummary]   = useState(null);
  const [compare, setCompare]   = useState(null);
  const [history, setHistory]   = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    const tryFetch = async (path) => {
      try { return await apiRequest(path, "GET", null, token); }
      catch { return null; }
    };

    const load = async () => {
      const [sm, cmp, h] = await Promise.all([
        tryFetch("/analysis/summary"),
        tryFetch("/analysis/compare"),
        tryFetch("/analysis/history"),
      ]);
      setSummary(sm);
      setCompare(cmp);
      setHistory(Array.isArray(h) ? h : []);
      setLoading(false);
    };
    load();
  }, [token]);

  if (loading) {
    return (
      <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}>
        <div style={{ width: 48, height: 48, border: "3px solid var(--border)", borderTopColor: "var(--accent)", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
      </div>
    );
  }

  return (
    <div className="container fade-in">
      <div className="header">
        <div>
          <h1 className="gradient-text" style={{ fontSize: 26 }}>Developer Profile</h1>
          <span className="badge">your coding identity</span>
        </div>
      </div>

      {/* Bio card */}
      <DevBioCard summary={summary} />

      {/* Activity */}
      {summary && (
        <div className="card" style={{ marginTop: 24 }}>
          <h2 style={{ marginBottom: 16, fontSize: 18, fontFamily: "'Space Grotesk', sans-serif" }}>⚡ Activity Patterns</h2>
          <ActivityHeatmap hourData={summary?.hour_heatmap} dayData={summary?.day_heatmap} />
        </div>
      )}

      {/* Compare */}
      <div style={{ marginTop: 24 }}>
        <ComparePanel data={compare} />
      </div>

      {/* History timeline */}
      {history.length > 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <h2 style={{ marginBottom: 16, fontSize: 18, fontFamily: "'Space Grotesk', sans-serif" }}>📜 Analysis History</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {history.map((snap, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "center", gap: 14,
                padding: "12px 16px", background: "var(--glass)",
                borderRadius: 12, border: "1px solid var(--border)",
                transition: "all 0.25s ease",
              }}
              onMouseEnter={e => { e.currentTarget.style.background = "var(--glass-hover)"; e.currentTarget.style.borderColor = "var(--accent-alpha-15)"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "var(--glass)"; e.currentTarget.style.borderColor = "var(--border)"; }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 10,
                  background: "var(--accent-alpha-8)", display: "flex",
                  alignItems: "center", justifyContent: "center",
                  fontSize: 14, fontWeight: 700, color: "var(--accent)",
                  fontFamily: "'Space Grotesk', sans-serif",
                  border: "1px solid var(--accent-alpha-15)",
                }}>
                  {i + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14, color: "var(--ink)" }}>
                    {snap.week || `Run ${i + 1}`}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--ink-faint)" }}>
                    {snap.predicted_role || "—"} &middot; {snap.work_style || "—"}
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "var(--accent)", fontFamily: "'Space Grotesk', sans-serif" }}>
                    {Math.round((snap.analytical + snap.creativity + snap.discipline + snap.collaboration) / 4)}
                  </div>
                  <div style={{ fontSize: 10, color: "var(--ink-faint)" }}>avg score</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
