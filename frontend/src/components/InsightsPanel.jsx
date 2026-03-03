const TRAIT_ICONS = {
  analytical:        "🔬",
  creativity:        "🎨",
  discipline:        "⏱️",
  collaboration:     "🤝",
  adaptability:      "🌊",
  learning_velocity: "⚡",
  risk_appetite:     "🎯",
  stress_stability:  "🧘",
};

const ROLE_BADGE_COLOR = {
  "Backend / Systems Engineer":     { bg: "linear-gradient(135deg, #1e3a5f, #0f172a)", text: "#93c5fd", glow: "rgba(59,130,246,0.15)" },
  "Startup Engineer":               { bg: "linear-gradient(135deg, #4a1942, #1e1b4b)", text: "#f0abfc", glow: "rgba(192,132,252,0.15)" },
  "Team Maintainer / Tech Lead":    { bg: "linear-gradient(135deg, #14532d, #052e16)", text: "#86efac", glow: "rgba(52,211,153,0.15)" },
  "Generalist / Full-Stack Engineer":{ bg: "linear-gradient(135deg, #7c2d12, #431407)", text: "#fdba74", glow: "rgba(251,146,60,0.15)" },
  "Research / ML Engineer":         { bg: "linear-gradient(135deg, #164e63, #0c4a6e)", text: "#a5f3fc", glow: "rgba(6,182,212,0.15)" },
};

const ScoreBar = ({ value }) => {
  const pct = Math.max(Math.min(Math.round(value), 100), 0);
  const fill = pct >= 65 ? "#34d399" : pct >= 40 ? "#fb923c" : "#f87171";
  const track = "rgba(139,133,161,0.18)";
  return (
    <div style={{
      width: "100%",
      height: 10,
      borderRadius: 6,
      background: `linear-gradient(to right, ${fill} ${pct}%, ${track} ${pct}%)`,
    }} />
  );
};

export default function InsightsPanel({ personality, insights }) {
  if (!insights) return null;

  const roleColors = ROLE_BADGE_COLOR[insights.predicted_role] || { bg: "linear-gradient(135deg, #1c1917, #0f0d15)", text: "#c4b5fd", glow: "rgba(168,85,247,0.15)" };

  const traitKeys = ["analytical","creativity","discipline","collaboration",
                     "adaptability","learning_velocity","risk_appetite","stress_stability"];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

      {/* ── Role Prediction Card ────────────────────────────── */}
      <div className="card" style={{
        background: roleColors.bg, border: "none",
        boxShadow: `0 8px 40px ${roleColors.glow}`,
      }}>
        {/* Decorative accent line */}
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${roleColors.text}40, transparent)` }} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
          <div>
            <p style={{ color: roleColors.text, fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: 0 }}>
              Predicted Role Fit
            </p>
            <h2 style={{ color: "#fff", margin: "8px 0 0", fontSize: 24, letterSpacing: "-0.02em" }}>
              {insights.predicted_role || "Unknown"}
            </h2>
          </div>
          <div style={{
            background: "rgba(255,255,255,0.1)", borderRadius: 16,
            padding: "10px 18px", textAlign: "center",
            backdropFilter: "blur(8px)",
            border: "1px solid rgba(255,255,255,0.08)",
          }}>
            <div style={{ color: "#fff", fontSize: 24, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif" }}>
              {Math.round(insights.role_confidence || 0)}%
            </div>
            <div style={{ color: roleColors.text, fontSize: 11, fontWeight: 500 }}>confidence</div>
          </div>
        </div>
        <p style={{ color: "rgba(255,255,255,0.7)", fontSize: 13, marginTop: 14, lineHeight: 1.7 }}>
          {insights.role_reason}
        </p>
      </div>

      {/* ── Work Style Card ────────────────────────────────── */}
      <div className="card">
        <p style={{ color: "var(--ink-muted)", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: 0 }}>
          Work Style Profile
        </p>
        <h3 style={{ color: "var(--ink)", margin: "8px 0 10px", fontSize: 20 }}>
          🧠 {insights.work_style}
        </h3>
        <p style={{ color: "var(--ink-muted)", fontSize: 14, lineHeight: 1.7, margin: 0 }}>
          {insights.work_style_detail}
        </p>
      </div>

      {/* ── Trait Reasoning ────────────────────────────────── */}
      <div className="card">
        <p style={{ color: "var(--ink-muted)", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 20 }}>
          Behavioral Evidence by Trait
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          {traitKeys.map(key => {
            const score   = personality?.[key] ?? 0;
            const reason  = insights.reasoning?.[key] ?? "";
            const label   = key.replace(/_/g, " ");
            return (
              <div key={key} style={{
                padding: "12px 14px", borderRadius: 12,
                background: "var(--glass)",
                border: "1px solid var(--border)",
                transition: "all 0.3s",
              }}
              onMouseEnter={e => { e.currentTarget.style.background = "var(--glass-active)"; e.currentTarget.style.borderColor = "var(--accent-alpha-15)"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "var(--glass)"; e.currentTarget.style.borderColor = "var(--border)"; }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                  <span style={{ fontSize: 18 }}>{TRAIT_ICONS[key]}</span>
                  <span style={{ fontWeight: 600, fontSize: 14, color: "var(--ink)", textTransform: "capitalize", flex: 1 }}>
                    {label}
                  </span>
                  <span style={{
                    fontWeight: 700, fontSize: 14, fontFamily: "'Space Grotesk', sans-serif",
                    color: score >= 65 ? "var(--green)" : score >= 40 ? "var(--orange)" : "var(--red)"
                  }}>
                    {Math.round(score)}%
                  </span>
                </div>
                <div style={{ marginLeft: 28 }}>
                  <ScoreBar value={score} />
                </div>
                {reason && (
                  <p style={{
                    color: "var(--ink-faint)", fontSize: 12.5, lineHeight: 1.6,
                    margin: "2px 0 0 28px", fontStyle: "italic",
                  }}>
                    {reason}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
