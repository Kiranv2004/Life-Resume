import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest, apiBlob } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";
import RadarChartPanel from "../charts/RadarChartPanel.jsx";
import GrowthTimeline from "../charts/GrowthTimeline.jsx";
import LanguageChart from "../charts/LanguageChart.jsx";
import InsightsPanel from "../components/InsightsPanel.jsx";
import ComparePanel from "../components/ComparePanel.jsx";
import DevBioCard from "../components/DevBioCard.jsx";
import ActivityHeatmap from "../components/ActivityHeatmap.jsx";

function safeFloat(v) {
  const n = parseFloat(v);
  return isNaN(n) ? "\u2014" : n.toFixed(2);
}

/* Read a CSS variable from :root at render time */
function cv(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

const METRIC_LABELS = {
  total_commits: "Total Commits", total_repos: "Repos Analysed",
  commit_consistency: "Consistency", focus_depth: "Focus Depth",
  collaboration_index: "Collaboration", experimentation_index: "Experimentation",
  persistence_index: "Persistence", complexity_handling: "Complexity",
  night_commit_ratio: "Night Ratio", avg_commit_hour: "Avg Hour",
  burst_session_count: "Burst Sessions", pull_requests: "Pull Requests",
};

const STAT_GRADIENTS = [
  { bg: "linear-gradient(135deg, var(--accent-alpha-12), var(--accent2-alpha))", glow: "var(--accent-alpha-15)", accent: "var(--accent-soft)" },
  { bg: "linear-gradient(135deg, var(--accent2-alpha), rgba(6,182,212,0.08))", glow: "rgba(59,130,246,0.15)", accent: "var(--accent-2)" },
  { bg: "linear-gradient(135deg, rgba(6,182,212,0.1), var(--green-dim))", glow: "rgba(6,182,212,0.15)", accent: "var(--accent-3)" },
  { bg: "linear-gradient(135deg, rgba(251,146,60,0.1), var(--accent-alpha-8))", glow: "rgba(251,146,60,0.15)", accent: "var(--orange)" },
];

function StatCard({ label, value, sub, icon, index = 0 }) {
  const g = STAT_GRADIENTS[index % STAT_GRADIENTS.length];
  return (
    <div style={{
      background: g.bg,
      border: "1px solid var(--border)",
      borderRadius: 16, padding: "22px 18px", textAlign: "center",
      transition: "all 0.35s cubic-bezier(0.4,0,0.2,1)",
      cursor: "default",
      position: "relative",
      overflow: "hidden",
    }}
    onMouseEnter={e => {
      e.currentTarget.style.borderColor = g.glow;
      e.currentTarget.style.boxShadow = `0 8px 32px ${g.glow}`;
      e.currentTarget.style.transform = "translateY(-4px)";
    }}
    onMouseLeave={e => {
      e.currentTarget.style.borderColor = "";
      e.currentTarget.style.boxShadow = "none";
      e.currentTarget.style.transform = "translateY(0)";
    }}>
      {icon && <div style={{ fontSize: 24, marginBottom: 8 }}>{icon}</div>}
      <div className="stat-value" style={{ color: g.accent }}>{value}</div>
      <div style={{ fontSize: 12, color: "var(--ink-muted)", marginTop: 6, fontWeight: 500, letterSpacing: "0.03em" }}>{label}</div>
      {sub && <div style={{ fontSize: 10, color: "var(--ink-faint)", marginTop: 3 }}>{sub}</div>}
    </div>
  );
}

export default function Dashboard() {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [metrics, setMetrics] = useState(null);
  const [personality, setPersonality] = useState(null);
  const [history, setHistory] = useState([]);
  const [insights, setInsights] = useState(null);
  const [languages, setLanguages] = useState(null);
  const [compare, setCompare] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [noData, setNoData] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const isNoData = (msg = "") =>
      ["no metrics", "no personality", "not found", "404"].some(k =>
        msg.toLowerCase().includes(k));

    const tryFetch = async (path) => {
      try { return await apiRequest(path, "GET", null, token); }
      catch (e) { return { __err: e.message || String(e) }; }
    };

    const load = async () => {
      const [m, p, h, i, lang, cmp, sm] = await Promise.all([
        tryFetch("/analysis/metrics"),
        tryFetch("/analysis/personality"),
        tryFetch("/analysis/history"),
        tryFetch("/analysis/insights"),
        tryFetch("/analysis/languages"),
        tryFetch("/analysis/compare"),
        tryFetch("/analysis/summary"),
      ]);

      if (m.__err || p.__err) {
        const msg = m.__err || p.__err || "";
        if (isNoData(msg)) { setNoData(true); }
        else { setError(msg); }
        setLoading(false);
        return;
      }

      setMetrics(m);
      setPersonality(p);
      setHistory(Array.isArray(h) && !h.__err ? h : []);
      setInsights(!i.__err ? i : null);
      setLanguages(!lang.__err ? lang : null);
      setCompare(!cmp.__err ? cmp : null);
      setSummary(!sm.__err ? sm : null);
      setLoading(false);
    };
    load();
  }, [token]);

  const downloadReport = async () => {
    try {
      const blob = await apiBlob("/reports/download", token);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "life-resume-report.pdf"; a.click();
      URL.revokeObjectURL(url);
    } catch (e) { alert("Report download failed: " + e.message); }
  };

  if (loading) {
    return (
      <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "70vh" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{
            width: 56, height: 56,
            border: "3px solid var(--accent-alpha-15)",
            borderTopColor: "var(--accent)",
            borderRadius: "50%",
            animation: "spin 0.8s linear infinite",
            margin: "0 auto 20px",
          }} />
          <p style={{ color: "var(--ink-muted)", fontSize: 14, letterSpacing: "0.02em" }}>Decoding your behavioral fingerprint...</p>
          <div style={{ display: "flex", gap: 8, justifyContent: "center", marginTop: 20 }}>
            {[0,1,2].map(i => (
              <div key={i} className="skeleton" style={{ width: 60, height: 6, borderRadius: 3, animationDelay: `${i * 0.2}s` }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (noData) {
    return (
      <div className="container fade-in" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "70vh" }}>
        <div className="card" style={{ textAlign: "center", padding: "64px 40px", maxWidth: 500, border: "1px solid var(--accent-alpha-15)" }}>
          <div style={{
            width: 80, height: 80, borderRadius: 20,
            background: "linear-gradient(135deg, var(--accent-alpha-15), var(--accent2-alpha))",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 20px", fontSize: 36,
          }}>🧬</div>
          <h2 style={{ marginBottom: 10, fontSize: 24 }}>No analysis data yet</h2>
          <p style={{ color: "var(--ink-muted)", marginBottom: 32, lineHeight: 1.7, fontSize: 14 }}>
            Connect your GitHub account and run an analysis to generate your behavioral fingerprint, role prediction, and personality report.
          </p>
          <button className="button" onClick={() => navigate("/connect")} style={{ padding: "14px 32px", fontSize: 15 }}>
            Connect GitHub & Analyse
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="card" style={{ textAlign: "center", padding: 40 }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>⚠️</div>
          <p style={{ color: "var(--red)", marginBottom: 16, fontSize: 14 }}>{error}</p>
          <button className="button secondary" onClick={() => navigate("/connect")}>Go to Connect</button>
        </div>
      </div>
    );
  }

  const totalCommits = metrics?.total_commits ?? "\u2014";
  const totalRepos = metrics?.total_repos ?? "\u2014";
  const nightRatio = metrics?.night_commit_ratio != null
    ? (metrics.night_commit_ratio * 100).toFixed(0) + "%" : "\u2014";
  const bursts = metrics?.burst_session_count ?? "\u2014";
  const topLang = languages?.languages?.[0]?.language || "\u2014";

  return (
    <div className="container fade-in">
      {/* Header */}
      <div className="header">
        <div>
          <h1 style={{ fontSize: 28 }}>
            <span className="gradient-text">Intelligence Dashboard</span>
          </h1>
          <span className="badge" style={{ marginTop: 8 }}>behavioral fingerprint</span>
        </div>
        <div className="nav">
          <button className="button secondary" onClick={() => navigate("/connect")}>Re-Analyse</button>
          <button className="button secondary" onClick={downloadReport}>Export PDF</button>
        </div>
      </div>

      {/* Dev Bio */}
      <div style={{ marginBottom: 28 }}>
        <DevBioCard summary={summary} />
      </div>

      {/* Quick Stats */}
      <div className="section-label">Key Metrics</div>
      <div className="grid-4" style={{ display: "grid", gap: 16, marginBottom: 28 }}>
        <StatCard icon="📝" label="Commits Analysed" value={totalCommits} index={0} />
        <StatCard icon="📁" label="Repositories" value={totalRepos} index={1} />
        <StatCard icon="🌙" label="Night Commits" value={nightRatio} sub="after 8 PM" index={2} />
        <StatCard icon="🔥" label="Burst Sessions" value={bursts} sub="deep-focus sprints" index={3} />
      </div>

      {/* Radar + Languages */}
      <div className="section-label">Personality & Languages</div>
      <div className="grid grid-2" style={{ marginBottom: 28 }}>
        <div className="card">
          <h2 style={{ marginBottom: 16, fontSize: 18 }}>
            <span style={{ marginRight: 8, opacity: 0.7 }}>🎯</span>Personality Radar
          </h2>
          <RadarChartPanel data={personality} />
        </div>
        <div className="card">
          <h2 style={{ marginBottom: 16, fontSize: 18 }}>
            <span style={{ marginRight: 8, opacity: 0.7 }}>🧬</span>Language DNA
          </h2>
          <LanguageChart data={languages} />
        </div>
      </div>

      {/* Timeline + Heatmap */}
      <div className="section-label">Activity & Growth</div>
      <div className="grid grid-2" style={{ marginBottom: 28 }}>
        <div className="card">
          <h2 style={{ marginBottom: 16, fontSize: 18 }}>
            <span style={{ marginRight: 8, opacity: 0.7 }}>📈</span>Trait Evolution
          </h2>
          <GrowthTimeline data={history} />
        </div>
        <div className="card">
          <h2 style={{ marginBottom: 16, fontSize: 18 }}>
            <span style={{ marginRight: 8, opacity: 0.7 }}>🗓️</span>Activity Map
          </h2>
          <ActivityHeatmap hourData={summary?.hour_heatmap} dayData={summary?.day_heatmap} />
        </div>
      </div>

      {/* Insights (role + workstyle + reasoning) */}
      <div className="section-label">Intelligence Report</div>
      <InsightsPanel personality={personality} insights={insights} />

      {/* Compare */}
      <div style={{ marginTop: 28 }}>
        <div className="section-label">Growth Tracking</div>
        <ComparePanel data={compare} />
      </div>

      {/* Metrics Grid */}
      <div className="card" style={{ marginTop: 28 }}>
        <h2 style={{ marginBottom: 20, fontSize: 18 }}>
          <span style={{ marginRight: 8, opacity: 0.7 }}>📊</span>Raw Behavioral Metrics
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px,1fr))", gap: 10 }}>
          {Object.entries(metrics)
            .filter(([k]) => !["_id", "user", "created_at", "computed_at"].includes(k))
            .map(([k, v]) => (
              <div key={k} style={{
                background: "var(--bg-deep)", border: "1px solid var(--border)",
                borderRadius: 12, padding: "14px 16px",
                transition: "all 0.3s",
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = cv('--accent-alpha-20'); e.currentTarget.style.background = cv('--glass-active'); }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = ''; e.currentTarget.style.background = cv('--bg-deep'); }}>
                <div style={{ fontSize: 10, color: "var(--ink-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6, fontWeight: 600 }}>
                  {METRIC_LABELS[k] || k.replaceAll("_", " ")}
                </div>
                <div style={{ fontSize: 20, fontWeight: 700, color: "var(--ink)", fontFamily: "'Space Grotesk', sans-serif" }}>
                  {safeFloat(v)}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}