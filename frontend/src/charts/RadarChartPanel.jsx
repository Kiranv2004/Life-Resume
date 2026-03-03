import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";
import { useTheme } from "../hooks/useTheme.jsx";

const cv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

export default function RadarChartPanel({ data }) {
  if (!data) return null;
  const { theme } = useTheme();

  const TRAIT_LABELS = {
    analytical:        "Analytical",
    creativity:        "Creativity",
    discipline:        "Discipline",
    collaboration:     "Teamwork",
    adaptability:      "Adaptability",
    learning_velocity: "Learning",
    risk_appetite:     "Risk",
    stress_stability:  "Stability",
  };

  const chartData = Object.entries(data)
    .filter(([k]) => TRAIT_LABELS[k])
    .map(([key, value]) => ({
      trait: TRAIT_LABELS[key] || key,
      value: Math.round(value),
      fullMark: 100,
    }));

  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer>
        <RadarChart data={chartData} cx="50%" cy="50%" outerRadius="75%">
          <PolarGrid stroke={cv('--border')} />
          <PolarAngleAxis
            dataKey="trait"
            tick={{ fontSize: 11, fill: cv('--ink-muted'), fontWeight: 500 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fontSize: 10, fill: cv('--ink-faint') }}
            axisLine={false}
          />
          <Radar
            dataKey="value"
            stroke={cv('--accent')}
            fill="url(#radarGrad)"
            fillOpacity={0.35}
            strokeWidth={2.5}
            dot={{ r: 4, fill: cv('--accent'), stroke: cv('--bg'), strokeWidth: 2 }}
            activeDot={{ r: 6, fill: "#c084fc", stroke: cv('--bg'), strokeWidth: 2 }}
          />
          <defs>
            <linearGradient id="radarGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#a855f7" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.2} />
            </linearGradient>
          </defs>
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
