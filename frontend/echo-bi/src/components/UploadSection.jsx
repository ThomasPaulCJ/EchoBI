// src/components/UploadSection.jsx
import React from "react";
import { uploadFile } from "../services/api";

export default function UploadSection({ setPreview, setCsv, onUploadComplete }) {
  const handleFile = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    
    try {
      const data = await uploadFile(f);
      if (data.preview) {
        setPreview(data.preview);
        setCsv(data.csv);
        if (onUploadComplete) {
          onUploadComplete(data.preview, data.csv, data.summary);
        }
      } else {
        alert("Upload failed: " + (data.detail || "unknown"));
      }
    } catch (error) {
      alert("Upload error: " + error.message);
    }
  };

  return (
    <div className="upload-section">
      <label htmlFor="file-upload" style={{
        display: "inline-block",
        padding: "0.625rem 1.25rem",
        backgroundColor: "var(--bg-secondary)",
        border: "2px dashed var(--border-color)",
        borderRadius: "6px",
        cursor: "pointer",
        transition: "all 0.2s ease",
        fontSize: "0.875rem",
        fontWeight: 500,
      }}>
        📁 Choose CSV or Excel file
      </label>
      <input 
        id="file-upload"
        type="file" 
        accept=".csv,.xlsx" 
        onChange={handleFile}
        style={{ display: "none" }}
      />
    </div>
  );
}
