// src/components/upload/UploadError.jsx
import React from "react";
import { Button } from "../common";
import "./UploadError.css";

export default function UploadError({ error, onRetry, onDismiss }) {
  const getErrorDetails = (error) => {
    if (typeof error === "string") {
      return { message: error, details: null };
    }

    if (error?.detail) {
      return { message: error.detail, details: null };
    }

    if (error?.message) {
      return { 
        message: error.message,
        details: error.stack || null
      };
    }

    return { 
      message: "An unexpected error occurred during upload",
      details: JSON.stringify(error, null, 2)
    };
  };

  const { message, details } = getErrorDetails(error);

  return (
    <div className="upload-error">
      <div className="upload-error-header">
        <span className="upload-error-icon">❌</span>
        <h3 className="upload-error-title">Upload Failed</h3>
      </div>
      
      <div className="upload-error-content">
        <p className="upload-error-message">{message}</p>
        
        {details && (
          <details className="upload-error-details">
            <summary>Technical Details</summary>
            <pre className="upload-error-stack">{details}</pre>
          </details>
        )}
      </div>

      <div className="upload-error-actions">
        {onRetry && (
          <Button variant="primary" onClick={onRetry}>
            Retry Upload
          </Button>
        )}
        {onDismiss && (
          <Button variant="secondary" onClick={onDismiss}>
            Dismiss
          </Button>
        )}
      </div>

      <div className="upload-error-help">
        <h4 className="upload-error-help-title">Common Solutions:</h4>
        <ul className="upload-error-help-list">
          <li>Ensure the file is in a supported format (CSV, Excel, JSON)</li>
          <li>Check that the file is not corrupted or empty</li>
          <li>Verify the file size is within limits</li>
          <li>Make sure the backend server is running</li>
          <li>Check your network connection</li>
        </ul>
      </div>
    </div>
  );
}
