import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function GrowthTimeline({ data }) {
  const chartData = data.map((item) => ({
    date: new Date(item.created_at).toLocaleDateString(),
    analytical: item.analytical
  }));

  return (
    <div style={{ width: "100%", height: 280 }}>
      <ResponsiveContainer>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Line type="monotone" dataKey="analytical" stroke="#2f855a" strokeWidth={3} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
