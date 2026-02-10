// src/components/upload/UploadZone.jsx
import React, { useState, useCallback } from "react";
import { Button, Loader } from "../common";
import "./UploadZone.css";

export default function UploadZone({ onFileSelect, onUploadComplete, isUploading = false }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      if (onFileSelect) {
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      if (onFileSelect) {
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);

  const handleClearFile = useCallback(() => {
    setSelectedFile(null);
    if (onFileSelect) {
      onFileSelect(null);
    }
  }, [onFileSelect]);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
  };

  return (
    <div className="upload-zone-container">
      <div
        className={`upload-zone ${isDragging ? "upload-zone-dragging" : ""} ${
          selectedFile ? "upload-zone-has-file" : ""
        } ${isUploading ? "upload-zone-uploading" : ""}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="upload-zone-loading">
            <Loader size="large" text="Uploading file..." />
          </div>
        ) : selectedFile ? (
          <div className="upload-zone-file-info">
            <div className="file-icon">📄</div>
            <div className="file-details">
              <div className="file-name">{selectedFile.name}</div>
              <div className="file-meta">
                <span className="file-size">{formatFileSize(selectedFile.size)}</span>
                <span className="file-type">{selectedFile.type || "Unknown type"}</span>
              </div>
            </div>
            <Button
              variant="danger"
              size="small"
              onClick={handleClearFile}
              disabled={isUploading}
            >
              Remove
            </Button>
          </div>
        ) : (
          <>
            <div className="upload-zone-icon">📤</div>
            <div className="upload-zone-text">
              <p className="upload-zone-title">
                {isDragging ? "Drop your file here" : "Drag & drop your file here"}
              </p>
              <p className="upload-zone-subtitle">or</p>
            </div>
            <input
              id="file-input"
              type="file"
              accept=".csv,.xlsx,.xls,.json"
              onChange={handleFileInput}
              className="upload-zone-input"
            />
            <Button 
              variant="primary" 
              onClick={() => document.getElementById('file-input').click()}
            >
              Browse Files
            </Button>
            <p className="upload-zone-hint">Supported formats: CSV, Excel, JSON</p>
          </>
        )}
      </div>
    </div>
  );
}
