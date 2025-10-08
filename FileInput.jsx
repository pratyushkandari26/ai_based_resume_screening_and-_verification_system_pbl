import React from "react";

export default function FileInput({ onChange, accept = ".doc,.docx,.pdf" }) {
  return (
    <label
      style={{
        display: "block",
        padding: "10px",
        border: "2px dashed #bbb",
        borderRadius: "8px",
        textAlign: "center",
        cursor: "pointer",
        background: "#fafafa",
        transition: "0.3s ease all",
      }}
    >
      <input
        type="file"
        accept={accept}
        onChange={onChange}
        style={{ display: "none" }}
      />
      <span style={{ color: "#333" }}>📄 Click to choose a file</span>
    </label>
  );
}
