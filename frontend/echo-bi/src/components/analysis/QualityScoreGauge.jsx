// src/components/analysis/QualityScoreGauge.jsx
import React from "react";
import { Card } from "../common";
import "./QualityScoreGauge.css";

export default function QualityScoreGauge({ score, breakdown }) {
  const getScoreColor = (score) => {
    if (score >= 0.8) return "#10b981"; // green
    if (score >= 0.6) return "#f59e0b"; // orange
    return "#ef4444"; // red
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return "Excellent";
    if (score >= 0.6) return "Good";
    if (score >= 0.4) return "Fair";
    return "Needs Improvement";
  };

  const percentage = Math.round((score || 0) * 100);
  const color = getScoreColor(score || 0);

  // Calculate circle properties for gauge
  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <Card title="📊 Data Quality Score" className="quality-score-gauge">
      <div className="gauge-container">
        <svg className="gauge-svg" viewBox="0 0 200 200">
          {/* Background circle */}
          <circle
            className="gauge-background"
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="12"
          />
          {/* Progress circle */}
          <circle
            className="gauge-progress"
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            transform="rotate(-90 100 100)"
          />
        </svg>
        
        <div className="gauge-content">
          <div className="gauge-score" style={{ color }}>
            {percentage}%
          </div>
          <div className="gauge-label">{getScoreLabel(score || 0)}</div>
        </div>
      </div>

      {breakdown && (
        <div className="quality-breakdown">
          <h4 className="breakdown-title">Quality Breakdown</h4>
          <div className="breakdown-items">
            {Object.entries(breakdown).map(([key, value]) => (
              <div key={key} className="breakdown-item">
                <div className="breakdown-header">
                  <span className="breakdown-name">
                    {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                  </span>
                  <span className="breakdown-score">{Math.round(value * 100)}%</span>
                </div>
                <div className="breakdown-bar-container">
                  <div
                    className="breakdown-bar"
                    style={{
                      width: `${value * 100}%`,
                      backgroundColor: getScoreColor(value)
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
