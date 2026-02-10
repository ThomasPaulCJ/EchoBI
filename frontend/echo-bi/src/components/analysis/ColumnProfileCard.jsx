// src/components/analysis/ColumnProfileCard.jsx
import React, { useState } from "react";
import { Card, Badge } from "../common";
import "./ColumnProfileCard.css";

export default function ColumnProfileCard({ column }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!column) return null;

  const getTypeColor = (type) => {
    const colors = {
      numeric: "primary",
      categorical: "success",
      datetime: "warning",
      text: "info",
      boolean: "default"
    };
    return colors[type?.toLowerCase()] || "default";
  };

  const formatNumber = (num) => {
    if (num === null || num === undefined) return "N/A";
    return typeof num === "number" ? num.toLocaleString() : num;
  };

  const formatPercent = (num) => {
    if (num === null || num === undefined) return "N/A";
    return `${Math.round(num * 100)}%`;
  };

  return (
    <Card className="column-profile-card" hoverable>
      <div className="column-profile-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="column-profile-main">
          <h4 className="column-name">{column.name}</h4>
          <div className="column-badges">
            <Badge variant={getTypeColor(column.type)}>{column.type}</Badge>
            {column.is_key && <Badge variant="warning">Key</Badge>}
            {column.has_nulls && <Badge variant="danger">Has Nulls</Badge>}
          </div>
        </div>
        <button className="expand-button" aria-label={isExpanded ? "Collapse" : "Expand"}>
          {isExpanded ? "▼" : "▶"}
        </button>
      </div>

      {isExpanded && (
        <div className="column-profile-details">
          {/* Basic Statistics */}
          <div className="profile-section">
            <h5 className="section-title">Basic Statistics</h5>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Unique Values:</span>
                <span className="stat-value">{formatNumber(column.unique_count)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Missing:</span>
                <span className="stat-value">{formatPercent(column.missing_percent)}</span>
              </div>
              {column.type === "numeric" && (
                <>
                  <div className="stat-item">
                    <span className="stat-label">Mean:</span>
                    <span className="stat-value">{formatNumber(column.mean)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Median:</span>
                    <span className="stat-value">{formatNumber(column.median)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Min:</span>
                    <span className="stat-value">{formatNumber(column.min)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Max:</span>
                    <span className="stat-value">{formatNumber(column.max)}</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Top Values (for categorical) */}
          {column.top_values && column.top_values.length > 0 && (
            <div className="profile-section">
              <h5 className="section-title">Most Frequent Values</h5>
              <div className="top-values-list">
                {column.top_values.slice(0, 5).map((item, idx) => (
                  <div key={idx} className="top-value-item">
                    <span className="value-text">{item.value}</span>
                    <div className="value-bar-container">
                      <div 
                        className="value-bar" 
                        style={{ width: `${item.percent * 100}%` }}
                      />
                      <span className="value-count">
                        {formatNumber(item.count)} ({formatPercent(item.percent)})
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quality Indicators */}
          <div className="profile-section">
            <h5 className="section-title">Data Quality</h5>
            <div className="quality-indicators">
              <div className="quality-item">
                <span className="quality-label">Completeness:</span>
                <div className="quality-bar-container">
                  <div 
                    className="quality-bar quality-bar-success" 
                    style={{ width: `${(1 - (column.missing_percent || 0)) * 100}%` }}
                  />
                </div>
                <span className="quality-value">
                  {formatPercent(1 - (column.missing_percent || 0))}
                </span>
              </div>
              {column.uniqueness !== undefined && (
                <div className="quality-item">
                  <span className="quality-label">Uniqueness:</span>
                  <div className="quality-bar-container">
                    <div 
                      className="quality-bar quality-bar-primary" 
                      style={{ width: `${column.uniqueness * 100}%` }}
                    />
                  </div>
                  <span className="quality-value">{formatPercent(column.uniqueness)}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
