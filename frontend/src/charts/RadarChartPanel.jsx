import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from "recharts";

export default function RadarChartPanel({ data }) {
  const chartData = Object.entries(data).map(([key, value]) => ({
    trait: key.replaceAll("_", " "),
    value
  }));

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <RadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="trait" />
          <PolarRadiusAxis angle={30} domain={[0, 100]} />
          <Radar dataKey="value" stroke="#b45309" fill="#b45309" fillOpacity={0.6} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
