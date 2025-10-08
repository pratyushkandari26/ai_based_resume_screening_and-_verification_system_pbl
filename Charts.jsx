// frontend/src/components/Charts.jsx
import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";
import { Bar } from "react-chartjs-2";

// register
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function Charts({ topSkills }){
  const safeSkills = Array.isArray(topSkills) ? topSkills : [];
  const labels = safeSkills.map(s => s.skill_name || s.name || "Unknown");
  const dataVals = safeSkills.map(s => s.count ?? s.value ?? 0);

  const data = {
    labels,
    datasets: [{ label: "Top Skills", data: dataVals, backgroundColor: "rgba(37,99,235,0.7)" }]
  };

  const options = {
    responsive: true,
    plugins: { legend: { display: false }, title: { display: true, text: "Top Matched Skills" } },
    scales: { y: { beginAtZero:true } }
  };

  return (
    <div>
      <h3 style={{marginBottom:8}}>Top Matched Skills</h3>
      <Bar data={data} options={options} />
    </div>
  );
}
