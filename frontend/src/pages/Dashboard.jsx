import { useEffect, useState } from "react";
import { apiRequest, apiBlob } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";
import RadarChartPanel from "../charts/RadarChartPanel.jsx";
import GrowthTimeline from "../charts/GrowthTimeline.jsx";

export default function Dashboard() {
  const { token, logout } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [personality, setPersonality] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const metricsData = await apiRequest("/analysis/metrics", "GET", null, token);
        const personalityData = await apiRequest("/analysis/personality", "GET", null, token);
        const historyData = await apiRequest("/analysis/history", "GET", null, token);
        setMetrics(metricsData);
        setPersonality(personalityData);
        setHistory(historyData);
      } catch (err) {
        setError(err.message);
      }
    };
    load();
  }, []);

  const downloadReport = async () => {
    const blob = await apiBlob("/reports/download", token);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "life-resume-report.pdf";
    link.click();
    URL.revokeObjectURL(url);
  };

  if (error) {
    return (
      <div className="container">
        <div className="card">{error}</div>
      </div>
    );
  }

  if (!metrics || !personality) {
    return <div className="container">Loading dashboard...</div>;
  }

  return (
    <div className="container fade-in">
      <div className="header">
        <div>
          <h1>Personality Intelligence Dashboard</h1>
          <span className="badge">Behavioral fingerprint</span>
        </div>
        <div className="nav">
          <button className="button secondary" onClick={downloadReport}>Export report</button>
          <button className="button" onClick={logout}>Logout</button>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>Personality Radar</h2>
          <RadarChartPanel data={personality} />
        </div>
        <div className="card">
          <h2>Growth timeline</h2>
          <GrowthTimeline data={history} />
        </div>
      </div>

      <div className="grid" style={{ marginTop: 24 }}>
        <div className="card">
          <h2>Behavior metrics</h2>
          <table className="table">
            <tbody>
              {Object.entries(metrics).map(([key, value]) => (
                <tr key={key}>
                  <th>{key.replaceAll("_", " ")}</th>
                  <td>{Number(value).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
