// frontend/src/components/Dashboard.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function Dashboard() {
  const [jobId, setJobId] = useState("");
  const [rankings, setRankings] = useState([]);
  const [topSkills, setTopSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const backendUrl = "http://127.0.0.1:8000";

  // Fetch top skills for visualization
  useEffect(() => {
    axios
      .get(`${backendUrl}/api/analytics/top-skills`)
      .then((res) => setTopSkills(res.data))
      .catch(() => setTopSkills([]));
  }, []);

  const fetchRankings = async () => {
    if (!jobId) return alert("Please enter a Job ID");
    setLoading(true);
    setMessage("");
    try {
      const res = await axios.post(`${backendUrl}/api/jobs/${jobId}/rank`);
      if (res.data.status === "done") {
        const ranked = await axios.get(`${backendUrl}/api/jobs/${jobId}/rankings`);
        setRankings(ranked.data);
        setMessage(`✅ Rankings generated for Job ID ${jobId}`);
      } else {
        setMessage("⚠️ No rankings generated");
      }
    } catch (err) {
      console.error(err);
      setMessage("❌ Failed to fetch rankings. Check backend logs.");
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: topSkills.map((s) => s.skill_name),
    datasets: [
      {
        label: "Top Skills Frequency",
        data: topSkills.map((s) => s.matches),
        backgroundColor: "rgba(54, 162, 235, 0.6)",
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-8">
      <h1 className="text-3xl font-bold mb-6 text-center">
        📊 Resume Ranking Dashboard
      </h1>

      {/* --- Top Skills Chart --- */}
      <div className="bg-white p-6 rounded-2xl shadow-md mb-8 max-w-4xl mx-auto">
        <h2 className="text-xl font-semibold mb-4">Top Matched Skills</h2>
        {topSkills.length > 0 ? (
          <Bar data={chartData} />
        ) : (
          <p className="text-gray-500">No skills data available yet.</p>
        )}
      </div>

      {/* --- Ranking Section --- */}
      <div className="bg-white p-6 rounded-2xl shadow-md max-w-4xl mx-auto">
        <h2 className="text-xl font-semibold mb-4">Rank Candidates by Job</h2>
        <div className="flex gap-4 items-center mb-4">
          <input
            type="text"
            placeholder="Enter Job ID (e.g., 1)"
            className="border p-2 rounded-lg w-48"
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
          />
          <button
            onClick={fetchRankings}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            {loading ? "Processing..." : "Fetch Rankings"}
          </button>
        </div>

        {message && <p className="mb-4 text-green-700 font-medium">{message}</p>}

        {/* Rankings Table */}
        {rankings.length > 0 ? (
          <table className="w-full border border-gray-200 text-left text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="border px-3 py-2">#</th>
                <th className="border px-3 py-2">Candidate Name</th>
                <th className="border px-3 py-2">Resume ID</th>
                <th className="border px-3 py-2">Score</th>
              </tr>
            </thead>
            <tbody>
              {rankings.map((r, idx) => (
                <tr key={r.ranking_id} className="hover:bg-gray-50">
                  <td className="border px-3 py-2">{idx + 1}</td>
                  <td className="border px-3 py-2">{r.candidate_name}</td>
                  <td className="border px-3 py-2">{r.resume_id}</td>
                  <td className="border px-3 py-2 font-semibold">{r.score.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-gray-500">No rankings loaded yet.</p>
        )}
      </div>
    </div>
  );
}
