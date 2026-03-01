import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../services/api.js";
import { useAuth } from "../auth/AuthProvider.jsx";

export default function Progress() {
  const [job, setJob] = useState(null);
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await apiRequest("/analysis/job", "GET", null, token);
        setJob(data);
        if (data.status === "completed") {
          clearInterval(interval);
          navigate("/dashboard");
        }
      } catch (err) {
        setJob({ status: "pending", progress: 0, message: "Waiting" });
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  if (!job) {
    return <div className="container">Checking progress...</div>;
  }

  return (
    <div className="container fade-in">
      <div className="card">
        <h1>Analysis in progress</h1>
        <p>Status: {job.status}</p>
        <p>{job.message}</p>
        <div style={{ marginTop: 16, background: "#efe0d2", borderRadius: 10, height: 12 }}>
          <div style={{ width: `${job.progress}%`, height: "100%", background: "#b45309", borderRadius: 10 }} />
        </div>
      </div>
    </div>
  );
}
