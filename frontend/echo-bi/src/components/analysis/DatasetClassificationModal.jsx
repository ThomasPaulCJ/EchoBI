// src/components/analysis/DatasetClassificationModal.jsx
import React from "react";
import { Modal, Button, Badge } from "../common";
import "./DatasetClassificationModal.css";

export default function DatasetClassificationModal({ 
  isOpen, 
  onClose, 
  classification, 
  onConfirm, 
  onReject 
}) {
  if (!classification) return null;

  const getClassificationIcon = (type) => {
    const icons = {
      financial: "💰",
      sales: "🛒",
      timeseries: "📈",
      healthcare: "🏥",
      generic: "📊"
    };
    return icons[type?.toLowerCase()] || "📊";
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return "success";
    if (confidence >= 0.6) return "warning";
    return "danger";
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return "High Confidence";
    if (confidence >= 0.6) return "Medium Confidence";
    return "Low Confidence";
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose}
      title="Dataset Classification"
      size="large"
      closeOnBackdrop={false}
    >
      <div className="classification-modal-content">
        <div className="classification-header">
          <div className="classification-icon">
            {getClassificationIcon(classification.type)}
          </div>
          <div className="classification-info">
            <h3 className="classification-type">{classification.type}</h3>
            <Badge variant={getConfidenceColor(classification.confidence)}>
              {getConfidenceLabel(classification.confidence)} ({Math.round(classification.confidence * 100)}%)
            </Badge>
          </div>
        </div>

        <div className="classification-description">
          <p>{classification.description || "We've analyzed your dataset and determined its type based on column names, data patterns, and content."}</p>
        </div>

        {classification.features && classification.features.length > 0 && (
          <div className="classification-features">
            <h4 className="features-title">Detected Features:</h4>
            <ul className="features-list">
              {classification.features.map((feature, idx) => (
                <li key={idx} className="feature-item">
                  <span className="feature-icon">✓</span>
                  <span className="feature-text">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {classification.suggestions && classification.suggestions.length > 0 && (
          <div className="classification-suggestions">
            <h4 className="suggestions-title">Recommended Actions:</h4>
            <ul className="suggestions-list">
              {classification.suggestions.map((suggestion, idx) => (
                <li key={idx} className="suggestion-item">
                  <span className="suggestion-icon">💡</span>
                  <span className="suggestion-text">{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="classification-warning">
          <p>
            <strong>Important:</strong> Confirming this classification will apply domain-specific preprocessing 
            tailored to {classification.type} datasets. You can review all changes before they are applied.
          </p>
        </div>
      </div>

      <div className="classification-modal-footer">
        <Button variant="secondary" onClick={onReject}>
          Choose Different Type
        </Button>
        <Button variant="primary" onClick={onConfirm}>
          Confirm Classification
        </Button>
      </div>
    </Modal>
  );
}
