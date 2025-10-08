// frontend/src/App.jsx
import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import UploadResume from "./components/UploadResume";
import UploadJob from "./components/UploadJob";

export default function App(){
  return (
    <>
      <header className="header">
        <div className="brand">ResumeMatcher</div>
        <nav className="nav">
          <Link to="/">Dashboard</Link>
          <Link to="/upload-resume">Upload Resume</Link>
          <Link to="/upload-job">Upload Job</Link>
        </nav>
      </header>

      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard/>} />
          <Route path="/upload-resume" element={<UploadResume/>} />
          <Route path="/upload-job" element={<UploadJob/>} />
        </Routes>
      </main>
    </>
  );
}
