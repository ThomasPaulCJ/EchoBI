// src/components/upload/FileInfoCard.jsx
import React from "react";
import { Card, Badge } from "../common";
import "./FileInfoCard.css";

export default function FileInfoCard({ file, datasetInfo = null }) {
  const formatFileSize = (bytes) => {
    if (!bytes) return "Unknown";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  const formatDate = (date) => {
    if (!date) return "Unknown";
    return new Date(date).toLocaleString();
  };

  const getFileExtension = (filename) => {
    if (!filename) return "unknown";
    return filename.split(".").pop().toUpperCase();
  };

  return (
    <Card title="📄 File Information" className="file-info-card">
      <div className="file-info-grid">
        {/* File Details */}
        <div className="file-info-section">
          <h4 className="file-info-section-title">File Details</h4>
          <div className="file-info-items">
            <div className="file-info-item">
              <span className="file-info-label">Name:</span>
              <span className="file-info-value">{file.name}</span>
            </div>
            <div className="file-info-item">
              <span className="file-info-label">Size:</span>
              <span className="file-info-value">{formatFileSize(file.size)}</span>
            </div>
            <div className="file-info-item">
              <span className="file-info-label">Type:</span>
              <Badge variant="info">{getFileExtension(file.name)}</Badge>
            </div>
            <div className="file-info-item">
              <span className="file-info-label">Last Modified:</span>
              <span className="file-info-value">{formatDate(file.lastModified)}</span>
            </div>
          </div>
        </div>

        {/* Dataset Info (if available) */}
        {datasetInfo && (
          <div className="file-info-section">
            <h4 className="file-info-section-title">Dataset Information</h4>
            <div className="file-info-items">
              {datasetInfo.row_count !== undefined && (
                <div className="file-info-item">
                  <span className="file-info-label">Rows:</span>
                  <span className="file-info-value file-info-highlight">
                    {datasetInfo.row_count.toLocaleString()}
                  </span>
                </div>
              )}
              {datasetInfo.column_count !== undefined && (
                <div className="file-info-item">
                  <span className="file-info-label">Columns:</span>
                  <span className="file-info-value file-info-highlight">
                    {datasetInfo.column_count}
                  </span>
                </div>
              )}
              {datasetInfo.cleaned_row_count !== undefined && (
                <div className="file-info-item">
                  <span className="file-info-label">After Cleaning:</span>
                  <span className="file-info-value file-info-highlight">
                    {datasetInfo.cleaned_row_count.toLocaleString()}
                  </span>
                </div>
              )}
              {datasetInfo.columns && datasetInfo.columns.length > 0 && (
                <div className="file-info-item file-info-columns">
                  <span className="file-info-label">Columns:</span>
                  <div className="file-info-columns-list">
                    {datasetInfo.columns.slice(0, 10).map((col, idx) => (
                      <Badge key={idx} variant="default" size="small">
                        {col}
                      </Badge>
                    ))}
                    {datasetInfo.columns.length > 10 && (
                      <Badge variant="default" size="small">
                        +{datasetInfo.columns.length - 10} more
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
