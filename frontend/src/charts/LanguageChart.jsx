import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { useTheme } from "../hooks/useTheme.jsx";

const cv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

const COLORS = [
  "#a855f7", "#3b82f6", "#06b6d4", "#34d399", "#f87171",
  "#fb923c", "#c084fc", "#60a5fa", "#2dd4bf", "#fbbf24",
  "#6366f1", "#8b85a1",
];

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{
      background: "var(--bg-deep)", borderRadius: 12, padding: "12px 16px",
      border: "1px solid var(--accent-alpha-20)",
      backdropFilter: "blur(12px)",
      boxShadow: "var(--shadow)",
    }}>
      <p style={{ color: "var(--ink)", fontWeight: 700, margin: 0, fontSize: 14 }}>{d.language}</p>
      <p style={{ color: "var(--ink-muted)", fontSize: 12, margin: "6px 0 0", lineHeight: 1.5 }}>
        {d.repos} repos &middot; {d.commits} commits &middot; {d.lines.toLocaleString()} lines
      </p>
    </div>
  );
};

export default function LanguageChart({ data }) {
  const { theme } = useTheme();
  if (!data?.languages?.length) {
    return (
      <div style={{ textAlign: "center", padding: 40, color: "var(--ink-faint)" }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>🧬</div>
        No language data yet
      </div>
    );
  }

  return (
    <div>
      <div style={{ width: "100%", height: 260 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data.languages}
              dataKey="percent"
              nameKey="language"
              cx="50%"
              cy="50%"
              outerRadius={90}
              innerRadius={50}
              strokeWidth={2}
              stroke={cv('--bg')}
            >
              {data.languages.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 12 }}
              formatter={(val) => <span style={{ color: cv('--ink-muted') }}>{val}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Language list breakdown */}
      <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 10 }}>
        {data.languages.slice(0, 6).map((lang, i) => (
          <div key={lang.language} style={{
            display: "flex", alignItems: "center", gap: 10,
            padding: "8px 10px", borderRadius: 8,
            transition: "background 0.2s",
          }}
          onMouseEnter={e => e.currentTarget.style.background = "var(--glass-hover)"}
          onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
            <div style={{
              width: 10, height: 10, borderRadius: "50%",
              background: COLORS[i % COLORS.length], flexShrink: 0,
            }} />
            <span style={{ flex: 1, fontSize: 13, fontWeight: 600, color: "var(--ink)" }}>
              {lang.language}
            </span>
            <span style={{ fontSize: 12, color: "var(--ink-faint)" }}>
              {lang.repos} repos
            </span>
            <span style={{ fontSize: 12, color: "var(--ink-faint)" }}>
              {lang.commits} commits
            </span>
            <span style={{
              fontSize: 12, fontWeight: 700,
              color: COLORS[i % COLORS.length],
              fontFamily: "'Space Grotesk', sans-serif",
            }}>
              {lang.percent}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
