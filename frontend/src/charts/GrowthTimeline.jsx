import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Legend,
} from "recharts";
import { useTheme } from "../hooks/useTheme.jsx";

const cv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

const LINES = [
  { key: "analytical",    color: "#a855f7" },
  { key: "discipline",    color: "#3b82f6" },
  { key: "creativity",    color: "#06b6d4" },
  { key: "collaboration", color: "#34d399" },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "var(--bg-deep)", borderRadius: 12, padding: "12px 16px",
      border: "1px solid var(--accent-alpha-20)", minWidth: 150,
      backdropFilter: "blur(12px)",
      boxShadow: "var(--shadow)",
    }}>
      <p style={{ color: "var(--ink-muted)", fontSize: 12, margin: "0 0 8px", fontWeight: 500 }}>{label}</p>
      {payload.map(p => (
        <div key={p.dataKey} style={{
          display: "flex", justifyContent: "space-between", gap: 16,
          padding: "3px 0",
        }}>
          <span style={{ color: p.color, fontSize: 12, textTransform: "capitalize" }}>
            {p.dataKey.replace("_", " ")}
          </span>
          <span style={{
            color: "var(--ink)", fontWeight: 700, fontSize: 12,
            fontFamily: "'Space Grotesk', sans-serif",
          }}>{Math.round(p.value)}</span>
        </div>
      ))}
    </div>
  );
};

export default function GrowthTimeline({ data }) {
  const { theme } = useTheme();
  if (!data || data.length === 0) {
    return (
      <div style={{ height: 280, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 8 }}>
        <div style={{ fontSize: 28, opacity: 0.6 }}>📈</div>
        <p style={{ color: "var(--ink-faint)", fontSize: 14 }}>Run multiple analyses over time to see growth trajectory</p>
      </div>
    );
  }

  const chartData = data.map((item, i) => ({
    label:        item.week || `Run ${i + 1}`,
    analytical:   item.analytical,
    discipline:   item.discipline,
    creativity:   item.creativity,
    collaboration: item.collaboration,
  }));

  return (
    <div>
      <div style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer>
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={cv('--border')} />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: cv('--ink-faint') }} axisLine={{ stroke: cv('--border') }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: cv('--ink-faint') }} axisLine={{ stroke: cv('--border') }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
              formatter={(val) => <span style={{ color: cv('--ink-muted') }}>{val.replace("_", " ")}</span>}
            />
            {LINES.map(l => (
              <Line
                key={l.key} type="monotone" dataKey={l.key}
                stroke={l.color} strokeWidth={2.5}
                dot={{ r: 4, fill: l.color, stroke: cv('--bg'), strokeWidth: 2 }}
                activeDot={{ r: 7, stroke: l.color, strokeWidth: 2, fill: cv('--bg') }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      {data.length === 1 && (
        <p style={{ color: "var(--ink-faint)", fontSize: 12, textAlign: "center", marginTop: 6 }}>
          Re-run analysis weekly to track your growth trajectory
        </p>
      )}
    </div>
  );
}

