// src/components/analysis/RelationshipMatrix.jsx
import React from "react";
import { Card } from "../common";
import "./RelationshipMatrix.css";

export default function RelationshipMatrix({ correlations }) {
  if (!correlations || correlations.length === 0) {
    return (
      <Card title="🔗 Column Relationships">
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <p className="empty-message">No significant correlations found</p>
          <p className="empty-hint">
            Correlations appear when numeric columns have relationships above 0.3
          </p>
        </div>
      </Card>
    );
  }

  const getCorrelationColor = (value) => {
    const absValue = Math.abs(value);
    if (absValue >= 0.8) return value > 0 ? "#10b981" : "#ef4444";
    if (absValue >= 0.6) return value > 0 ? "#34d399" : "#f87171";
    if (absValue >= 0.4) return value > 0 ? "#6ee7b7" : "#fca5a5";
    return "#e5e7eb";
  };

  const getCorrelationLabel = (value) => {
    const absValue = Math.abs(value);
    if (absValue >= 0.8) return value > 0 ? "Strong Positive" : "Strong Negative";
    if (absValue >= 0.6) return value > 0 ? "Moderate Positive" : "Moderate Negative";
    if (absValue >= 0.4) return value > 0 ? "Weak Positive" : "Weak Negative";
    return "No Correlation";
  };

  return (
    <Card title="🔗 Column Relationships" className="relationship-matrix-card">
      <div className="correlation-list">
        {correlations.map((item, idx) => (
          <div key={idx} className="correlation-item">
            <div className="correlation-header">
              <div className="correlation-columns">
                <span className="column-name">{item.column1}</span>
                <span className="correlation-arrow">↔</span>
                <span className="column-name">{item.column2}</span>
              </div>
              <div 
                className="correlation-badge"
                style={{ backgroundColor: getCorrelationColor(item.value) }}
              >
                {item.value >= 0 ? "+" : ""}{item.value.toFixed(3)}
              </div>
            </div>
            <div className="correlation-bar-container">
              <div 
                className="correlation-bar"
                style={{ 
                  width: `${Math.abs(item.value) * 100}%`,
                  backgroundColor: getCorrelationColor(item.value)
                }}
              />
            </div>
            <div className="correlation-label">
              {getCorrelationLabel(item.value)}
            </div>
          </div>
        ))}
      </div>

      <div className="correlation-legend">
        <h5 className="legend-title">Correlation Strength:</h5>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#10b981" }}></div>
            <span>Strong Positive (0.8+)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#34d399" }}></div>
            <span>Moderate Positive (0.6-0.8)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#e5e7eb" }}></div>
            <span>Weak/None (&lt;0.4)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#fca5a5" }}></div>
            <span>Moderate Negative (-0.6 to -0.8)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: "#ef4444" }}></div>
            <span>Strong Negative (-0.8+)</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
