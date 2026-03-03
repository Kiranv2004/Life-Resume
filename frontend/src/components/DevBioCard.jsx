const SCHEDULE_ICON = {
  "night owl": "🦉",
  "early bird": "🐦",
  "balanced-hours": "⚖️",
};

const ROLE_COLORS = {
  "Backend / Systems Engineer":     { bg: "linear-gradient(135deg, #1e3a5f 0%, #0f172a 50%, #12101a 100%)", accent: "#60a5fa", glow: "rgba(59,130,246,0.12)" },
  "Startup Engineer":               { bg: "linear-gradient(135deg, #4a1942 0%, #1e1b4b 50%, #12101a 100%)", accent: "#c084fc", glow: "rgba(192,132,252,0.12)" },
  "Team Maintainer / Tech Lead":    { bg: "linear-gradient(135deg, #14532d 0%, #052e16 50%, #12101a 100%)", accent: "#6ee7b7", glow: "rgba(110,231,183,0.12)" },
  "Generalist / Full-Stack Engineer":{ bg: "linear-gradient(135deg, #7c2d12 0%, #431407 50%, #12101a 100%)", accent: "#fdba74", glow: "rgba(251,146,60,0.12)" },
  "Research / ML Engineer":         { bg: "linear-gradient(135deg, #164e63 0%, #0c4a6e 50%, #12101a 100%)", accent: "#67e8f9", glow: "rgba(103,232,249,0.12)" },
};

export default function DevBioCard({ summary }) {
  if (!summary) return null;

  const roleStyle = ROLE_COLORS[summary.predicted_role] || {
    bg: "linear-gradient(135deg, rgba(168,85,247,0.15), #0f0d15, #06050a)",
    accent: "#c4b5fd",
    glow: "rgba(168,85,247,0.1)",
  };

  return (
    <div style={{
      background: roleStyle.bg,
      borderRadius: 20,
      padding: "30px 30px 26px",
      position: "relative",
      overflow: "hidden",
      border: "1px solid rgba(255,255,255,0.06)",
      boxShadow: `0 12px 48px ${roleStyle.glow}`,
    }}>
      {/* Decorative elements */}
      <div style={{
        position: "absolute", top: -50, right: -50,
        width: 180, height: 180, borderRadius: "50%",
        background: `radial-gradient(circle, ${roleStyle.glow}, transparent 70%)`,
      }} />
      <div style={{
        position: "absolute", bottom: -30, left: "30%",
        width: 120, height: 120, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(255,255,255,0.02), transparent 70%)",
      }} />
      {/* Top accent line */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0, height: 1,
        background: `linear-gradient(90deg, transparent, ${roleStyle.accent}30, transparent)`,
      }} />

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 18, position: "relative" }}>
        <div style={{
          width: 52, height: 52, borderRadius: 16,
          background: "rgba(255,255,255,0.08)",
          backdropFilter: "blur(8px)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 24,
          border: "1px solid rgba(255,255,255,0.06)",
          boxShadow: `0 4px 16px ${roleStyle.glow}`,
        }}>
          {SCHEDULE_ICON[summary.schedule_type] || "👤"}
        </div>
        <div>
          <h3 style={{ color: "#fff", margin: 0, fontSize: 20, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>
            {summary.github_login || "Developer"}
          </h3>
          <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
            {summary.top_traits?.map(t => (
              <span key={t} style={{
                background: "rgba(255,255,255,0.08)",
                backdropFilter: "blur(4px)",
                color: roleStyle.accent,
                padding: "3px 10px",
                borderRadius: 8,
                fontSize: 11,
                fontWeight: 600,
                border: "1px solid rgba(255,255,255,0.06)",
              }}>
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Bio */}
      <p style={{
        color: "rgba(255,255,255,0.75)", fontSize: 14,
        lineHeight: 1.8, margin: "0 0 18px",
        position: "relative",
      }}>
        {summary.bio}
      </p>

      {/* Tags */}
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", position: "relative" }}>
        {summary.predicted_role && (
          <span style={{
            background: roleStyle.accent,
            color: "#06050a",
            padding: "5px 14px",
            borderRadius: 10,
            fontSize: 12,
            fontWeight: 700,
            boxShadow: `0 4px 16px ${roleStyle.glow}`,
          }}>
            {summary.predicted_role}
          </span>
        )}
        {summary.work_style && (
          <span style={{
            background: "rgba(255,255,255,0.1)",
            backdropFilter: "blur(4px)",
            color: "#fff",
            padding: "5px 14px",
            borderRadius: 10,
            fontSize: 12,
            fontWeight: 600,
            border: "1px solid rgba(255,255,255,0.08)",
          }}>
            🧠 {summary.work_style}
          </span>
        )}
        <span style={{
          background: "rgba(255,255,255,0.06)",
          color: "rgba(255,255,255,0.5)",
          padding: "5px 14px",
          borderRadius: 10,
          fontSize: 12,
          border: "1px solid rgba(255,255,255,0.04)",
        }}>
          {SCHEDULE_ICON[summary.schedule_type]} {summary.schedule_type}
        </span>
      </div>
    </div>
  );
}
