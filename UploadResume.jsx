import React, { useState } from "react";
import useUpload from "../hooks/useUpload";
import FileInput from "./atoms/FileInput";

export default function UploadResume() {
  const [file, setFile] = useState(null);
  const { uploadFile, progress, parsed, reset } = useUpload("/api/resumes/upload");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (file) await uploadFile(file);
  };

  return (
    <div className="grid">
      <div className="card">
        <div className="card-title">Upload Resume</div>
        <form onSubmit={handleSubmit}>
          <FileInput onChange={(e) => setFile(e.target.files[0])} />
          <div className="form-row" style={{ marginTop: 10 }}>
            <button className="btn" type="submit">Upload</button>
            <button type="button" className="btn secondary" onClick={reset}>Reset</button>
          </div>

          {file && <div className="small-muted">Selected: {file.name}</div>}
          {progress > 0 && <div style={{ marginTop: 8 }}>Uploading: {progress}%</div>}
        </form>
      </div>

      <div className="card">
        <div className="card-title">Parsed Resume Data</div>
        {parsed ? (
          <div>
            <div><strong>Name:</strong> {parsed.name ?? "—"}</div>
            <div><strong>Email:</strong> {parsed.email ?? "—"}</div>
            <div><strong>Phone:</strong> {parsed.phone ?? "—"}</div>
            <div><strong>Skills:</strong> {(parsed.skills ?? []).join(", ") || "—"}</div>
          </div>
        ) : (
          <div className="small-muted">
            No parsed data yet. Upload a resume to see extracted details.
          </div>
        )}
      </div>
    </div>
  );
}
