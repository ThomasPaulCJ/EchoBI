// src/components/upload/UploadProgress.jsx
import React from "react";
import "./UploadProgress.css";

export default function UploadProgress({ progress = 0, status = "uploading", message = "" }) {
  const getStatusIcon = () => {
    switch (status) {
      case "uploading":
        return "⏳";
      case "processing":
        return "⚙️";
      case "success":
        return "✅";
      case "error":
        return "❌";
      default:
        return "📊";
    }
  };

  const getStatusText = () => {
    switch (status) {
      case "uploading":
        return "Uploading file...";
      case "processing":
        return "Processing dataset...";
      case "success":
        return "Upload complete!";
      case "error":
        return "Upload failed";
      default:
        return "Ready";
    }
  };

  const getStatusClass = () => {
    switch (status) {
      case "success":
        return "upload-progress-success";
      case "error":
        return "upload-progress-error";
      default:
        return "";
    }
  };

  return (
    <div className={`upload-progress ${getStatusClass()}`}>
      <div className="upload-progress-header">
        <span className="upload-progress-icon">{getStatusIcon()}</span>
        <span className="upload-progress-status">{message || getStatusText()}</span>
        <span className="upload-progress-percentage">{Math.round(progress)}%</span>
      </div>
      <div className="upload-progress-bar-container">
        <div
          className={`upload-progress-bar ${status === "error" ? "upload-progress-bar-error" : ""}`}
          style={{ width: `${progress}%` }}
        >
          <div className="upload-progress-bar-shimmer"></div>
        </div>
      </div>
    </div>
  );
}
