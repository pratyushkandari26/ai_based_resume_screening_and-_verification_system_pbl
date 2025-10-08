import React, { useState } from "react";
import axios from "axios";

export default function UploadJob() {
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [skills, setSkills] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!title || !desc) {
      setError("⚠️ Please fill in title and description.");
      return;
    }

    setError("");
    setResponse("");

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/jobs", {
        title,
        description: desc,
        skills: skills.split(",").map((s) => s.trim()).filter(Boolean),
      });
      setResponse(`✅ Job created successfully (ID: ${res.data.job_id})`);
    } catch (err) {
      setError("❌ Job creation failed. Check backend logs.");
    }
  };

  return (
    <div className="p-6 bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">💼 Create New Job</h2>

      <input
        type="text"
        placeholder="Job title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="w-full mb-3 border border-gray-300 rounded-lg p-2 text-sm"
      />

      <textarea
        placeholder="Job description..."
        value={desc}
        onChange={(e) => setDesc(e.target.value)}
        rows={4}
        className="w-full mb-3 border border-gray-300 rounded-lg p-2 text-sm"
      />

      <input
        type="text"
        placeholder="Required skills (comma separated)"
        value={skills}
        onChange={(e) => setSkills(e.target.value)}
        className="w-full mb-3 border border-gray-300 rounded-lg p-2 text-sm"
      />

      <button
        onClick={handleUpload}
        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
      >
        Create Job
      </button>

      {error && <p className="mt-3 text-red-500 font-medium">{error}</p>}
      {response && <p className="mt-3 text-green-600 font-medium">{response}</p>}
    </div>
  );
}
