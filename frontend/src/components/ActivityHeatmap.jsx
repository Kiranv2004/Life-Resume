const HOURS = Array.from({ length: 24 }, (_, i) => i);
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function maxVal(arr) {
  return Math.max(...arr, 1);
}

function HeatCell({ value, max, color }) {
  const intensity = max > 0 ? value / max : 0;
  const opacity = Math.max(0.06, intensity);
  return (
    <div
      title={`${value} commits`}
      style={{
        width: "100%",
        aspectRatio: "1",
        borderRadius: 5,
        background: color,
        opacity,
        transition: "all 0.3s cubic-bezier(0.4,0,0.2,1)",
        cursor: "default",
        boxShadow: intensity > 0.5 ? `0 0 8px ${color}40` : "none",
      }}
      onMouseEnter={e => { e.currentTarget.style.transform = "scale(1.3)"; e.currentTarget.style.zIndex = "2"; }}
      onMouseLeave={e => { e.currentTarget.style.transform = "scale(1)"; e.currentTarget.style.zIndex = "0"; }}
    />
  );
}

export default function ActivityHeatmap({ hourData, dayData }) {
  if (!hourData && !dayData) return null;

  const hMax = maxVal(hourData || []);
  const dMax = maxVal(dayData || []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

      {/* ── Hour Distribution ── */}
      {hourData && (
        <div>
          <p style={{ color: "var(--ink-muted)", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: "0 0 12px" }}>
            Commits by Hour
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(24, 1fr)", gap: 3, position: "relative" }}>
            {HOURS.map(h => (
              <HeatCell key={h} value={hourData[h] || 0} max={hMax} color="#a855f7" />
            ))}
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6 }}>
            <span style={{ fontSize: 10, color: "var(--ink-faint)" }}>12am</span>
            <span style={{ fontSize: 10, color: "var(--ink-faint)" }}>6am</span>
            <span style={{ fontSize: 10, color: "var(--ink-faint)" }}>12pm</span>
            <span style={{ fontSize: 10, color: "var(--ink-faint)" }}>6pm</span>
            <span style={{ fontSize: 10, color: "var(--ink-faint)" }}>11pm</span>
          </div>
        </div>
      )}

      {/* ── Day Distribution ── */}
      {dayData && (
        <div>
          <p style={{ color: "var(--ink-muted)", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: "0 0 12px" }}>
            Commits by Day
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 8 }}>
            {DAYS.map((day, i) => {
              const intensity = dMax > 0 ? (dayData[i] || 0) / dMax : 0;
              return (
                <div key={day} style={{ textAlign: "center" }}>
                  <div style={{
                    height: 48,
                    borderRadius: 10,
                    background: `linear-gradient(180deg, rgba(59,130,246,${Math.max(0.08, intensity)}), rgba(168,85,247,${Math.max(0.04, intensity * 0.5)}))`,
                    marginBottom: 6,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    border: "1px solid rgba(59,130,246,0.08)",
                    transition: "all 0.3s",
                    boxShadow: intensity > 0.5 ? "0 4px 16px rgba(59,130,246,0.15)" : "none",
                  }}>
                    <span style={{
                      color: "var(--ink)",
                      fontSize: 14,
                      fontWeight: 700,
                      fontFamily: "'Space Grotesk', sans-serif",
                      opacity: Math.max(0.4, intensity),
                    }}>
                      {dayData[i] || 0}
                    </span>
                  </div>
                  <span style={{ fontSize: 11, color: "var(--ink-faint)", fontWeight: 500 }}>{day}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
