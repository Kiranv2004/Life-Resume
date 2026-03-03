import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";

const STATUS_COLOR = {
  running: "#b45309",
  completed: "#15803d",
  failed: "#b91c1c",
  queued: "#78716c",
};

const STEPS = [
  { label: "Connect",        min: 1  },
  { label: "Fetch repos",    min: 10 },
  { label: "Ingest commits", min: 15 },
  { label: "Metrics",        min: 60 },
  { label: "Personality",    min: 85 },
  { label: "Done",           min: 100 },
];

export default function Progress() {
  const [job, setJob] = useState(null);
  const logsEndRef = useRef(null);
  const { token } = useAuth();
  const navigate = useNavigate();
  const doneRef = useRef(false);

  const checkJob = async () => {
    try {
      const data = await apiRequest("/analysis/job", "GET", null, token);
      setJob(data);
      if (data.status === "completed" && !doneRef.current) {
        doneRef.current = true;
        setTimeout(() => navigate("/dashboard"), 1800);
        return true;
      }
      if (data.status === "failed") {
        doneRef.current = true;
        return true;
      }
    } catch {
      /* job not yet created — still starting */
    }
    return false;
  };

  useEffect(() => {
    doneRef.current = false;
    checkJob();
    const iv = setInterval(async () => {
      const done = await checkJob();
      if (done) clearInterval(iv);
    }, 1500);
    return () => clearInterval(iv);
  }, [token]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [job?.logs]);

  const progress  = job?.progress ?? 0;
  const status    = job?.status   ?? "queued";
  const color     = STATUS_COLOR[status] || "#78716c";
  const logLines  = (job?.logs || "").trim().split("\n").filter(Boolean);

  return (
    <div className="container fade-in" style={{ maxWidth: 700 }}>
      {/* Title */}
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ margin: 0, fontSize: 26 }}>Analysing your GitHub profile</h1>
        <p style={{ color: "#78716c", marginTop: 4, fontSize: 14 }}>
          Fetching commits, computing metrics, building your personality fingerprint
        </p>
      </div>

      {/* Status + progress card */}
      <div className="card" style={{ marginBottom: 14 }}>
        {/* Top row */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
          <span style={{
            fontWeight: 700, fontSize: 13, color,
            background: color + "20", padding: "4px 14px",
            borderRadius: 20, display: "flex", alignItems: "center", gap: 6,
          }}>
            {status === "running" && (
              <span style={{ display: "flex", gap: 3 }}>
                {[0,1,2].map(i => (
                  <span key={i} style={{
                    width: 5, height: 5, borderRadius: "50%", background: color,
                    animation: `dot-pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
                    display: "inline-block",
                  }} />
                ))}
              </span>
            )}
            {status === "running" ? "Running" : status === "completed" ? "Complete ✓" : status === "failed" ? "Failed ✗" : "Queued"}
          </span>
          <span style={{ fontWeight: 800, fontSize: 24, color }}>{progress}%</span>
        </div>

        {/* Bar */}
        <div style={{ background: "#efe0d2", borderRadius: 10, height: 12, overflow: "hidden", marginBottom: 10 }}>
          <div style={{
            width: `${progress}%`, height: "100%", borderRadius: 10,
            background: status === "failed" ? "#b91c1c" : status === "completed" ? "#15803d" : "#b45309",
            transition: "width 0.7s ease",
          }} />
        </div>

        <p style={{ color: "#57534e", fontSize: 14, marginBottom: 14 }}>
          {job?.message || "Starting…"}
        </p>

        {/* Step pills */}
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {STEPS.map((step) => {
            const done = progress >= step.min;
            return (
              <span key={step.label} style={{
                fontSize: 12, padding: "3px 11px", borderRadius: 20, fontWeight: done ? 600 : 400,
                background: done ? "#15803d18" : "#f5f0eb",
                color: done ? "#15803d" : "#a8a29e",
                border: `1px solid ${done ? "#15803d44" : "#e7e0da"}`,
              }}>
                {done ? "✓ " : ""}{step.label}
              </span>
            );
          })}
        </div>

        {status === "completed" && (
          <p style={{ marginTop: 14, color: "#15803d", fontWeight: 600 }}>
            ✓ Done! Redirecting to dashboard…
          </p>
        )}
      </div>

      {/* Terminal-style log panel */}
      <div style={{ borderRadius: 12, overflow: "hidden", boxShadow: "0 4px 20px rgba(0,0,0,0.15)", marginBottom: 16 }}>
        {/* Title bar */}
        <div style={{
          background: "#1c1917", padding: "9px 14px",
          display: "flex", alignItems: "center", gap: 7,
        }}>
          {["#ef4444","#f59e0b","#22c55e"].map(c => (
            <span key={c} style={{ width: 10, height: 10, borderRadius: "50%", background: c, display: "inline-block" }} />
          ))}
          <span style={{ marginLeft: 10, color: "#a8a29e", fontSize: 13, fontFamily: "monospace" }}>
            analysis.log
          </span>
          {status === "running" && (
            <span style={{ marginLeft: "auto", color: "#a8a29e", fontSize: 12 }}>live ●</span>
          )}
        </div>

        {/* Log body */}
        <div style={{
          background: "#0c0a09", minHeight: 200, maxHeight: 320,
          overflowY: "auto", padding: "14px 16px",
          fontFamily: "'Courier New', monospace", fontSize: 13, lineHeight: 1.75,
        }}>
          {logLines.length === 0 ? (
            <span style={{ color: "#44403c" }}>Waiting for output…</span>
          ) : logLines.map((line, i) => {
            const ts    = line.match(/^\[[\d:]+\]/)?.[0] ?? "";
            const body  = line.replace(/^\[[\d:]+\]\s?/, "");
            const isErr = body.toLowerCase().includes("error");
            const isOk  = body.includes("✓") || /complete|ingested|done/i.test(body);
            const isHdr = /^  Repo:/i.test(body);
            return (
              <div key={i} style={{ display: "flex", gap: 8, marginBottom: 1 }}>
                <span style={{ color: "#44403c", flexShrink: 0 }}>{ts}</span>
                <span style={{
                  color: isErr ? "#f87171" : isOk ? "#4ade80" : isHdr ? "#fbbf24" : "#d6d3d1",
                }}>
                  {body}
                </span>
              </div>
            );
          })}
          <div ref={logsEndRef} />
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ display: "flex", gap: 10 }}>
        {status === "failed" && (
          <button className="button" onClick={() => navigate("/connect")}>Try Again</button>
        )}
        {status === "completed" && (
          <button className="button" onClick={() => navigate("/dashboard")}>Go to Dashboard →</button>
        )}
        <button className="button secondary" onClick={() => navigate("/dashboard")}>
          {status === "running" ? "View Dashboard (runs in background)" : "Dashboard"}
        </button>
      </div>

      <style>{`
        @keyframes dot-pulse {
          0%, 100% { opacity: 0.25; transform: scale(0.75); }
          50%       { opacity: 1;    transform: scale(1.2); }
        }
      `}</style>
    </div>
  );
}
