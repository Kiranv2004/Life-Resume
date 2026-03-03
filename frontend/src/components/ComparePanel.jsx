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

function DeltaBadge({ value }) {
  if (value === 0) return <span style={{ color: "var(--ink-faint)", fontSize: 12 }}>—</span>;
  const positive = value > 0;
  return (
    <span style={{
      color: positive ? "var(--green)" : "var(--red)",
      fontWeight: 700,
      fontSize: 13,
      fontFamily: "'Space Grotesk', sans-serif",
      display: "inline-flex",
      alignItems: "center",
      gap: 3,
    }}>
      <span style={{
        display: "inline-block",
        width: 6, height: 6, borderRadius: "50%",
        background: positive ? "var(--green)" : "var(--red)",
      }} />
      {positive ? "+" : ""}{Math.abs(value).toFixed(1)}
    </span>
  );
}

export default function ComparePanel({ data }) {
  if (!data?.available) {
    return (
      <div className="card" style={{ textAlign: "center", padding: "48px 24px" }}>
        <div style={{ fontSize: 28 }}>📊</div>
        <p style={{ color: "var(--ink-muted)", fontSize: 14, lineHeight: 1.6 }}>
          {data?.message || "Run analysis at least twice to see your growth comparison."}
        </p>
      </div>
    );
  }

  const traits = Object.keys(data.deltas);
  const improved = traits.filter(t => data.deltas[t].delta > 0).length;
  const declined = traits.filter(t => data.deltas[t].delta < 0).length;

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, flexWrap: "wrap", gap: 10 }}>
        <div>
          <p style={{ color: "var(--ink-muted)", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: 0 }}>
            Growth Comparison
          </p>
          <p style={{ color: "var(--ink-faint)", fontSize: 13, margin: "6px 0 0" }}>
            {data.previous_week} → {data.latest_week}
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <span style={{
            background: "var(--green-dim)", color: "var(--green)",
            padding: "5px 12px", borderRadius: 10,
            fontSize: 12, fontWeight: 700,
            border: "1px solid var(--green-dim)",
          }}>
            ↑ {improved} improved
          </span>
          <span style={{
            background: "var(--red-dim)", color: "var(--red)",
            padding: "5px 12px", borderRadius: 10,
            fontSize: 12, fontWeight: 700,
            border: "1px solid var(--red-dim)",
          }}>
            ↓ {declined} declined
          </span>
        </div>
      </div>

      {data.latest_role !== data.previous_role && (
        <div style={{
          background: "var(--accent-alpha-8)",
          border: "1px solid var(--accent-alpha-15)", borderRadius: 12,
          padding: "12px 16px", marginBottom: 18, fontSize: 13, color: "var(--accent-soft)",
        }}>
          🔄 Role shifted: <strong>{data.previous_role}</strong> → <strong>{data.latest_role}</strong>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {traits.map(t => {
          const d = data.deltas[t];
          const label = t.replace(/_/g, " ");
          return (
            <div key={t} style={{
              display: "flex", alignItems: "center", gap: 10,
              padding: "10px 12px", borderRadius: 10,
              transition: "background 0.2s",
            }}
            onMouseEnter={e => e.currentTarget.style.background = "var(--glass-hover)"}
            onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
              <span style={{ fontSize: 16, width: 24, textAlign: "center" }}>
                {TRAIT_ICONS[t] || "·"}
              </span>
              <span style={{
                flex: 1, fontSize: 13, fontWeight: 600, color: "var(--ink)",
                textTransform: "capitalize",
              }}>
                {label}
              </span>
              <span style={{ fontSize: 12, color: "var(--ink-faint)", minWidth: 36, textAlign: "right", fontFamily: "'Space Grotesk', sans-serif" }}>
                {d.previous.toFixed(0)}
              </span>
              <span style={{ color: "var(--ink-faint)", fontSize: 10 }}>→</span>
              <span style={{ fontSize: 12, color: "var(--ink)", fontWeight: 600, minWidth: 36, textAlign: "right", fontFamily: "'Space Grotesk', sans-serif" }}>
                {d.current.toFixed(0)}
              </span>
              <div style={{ minWidth: 60, textAlign: "right" }}>
                <DeltaBadge value={d.delta} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
