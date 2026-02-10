// src/pages/AnalysisPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Button, Badge, Loader } from "../components/common";
import { 
  DatasetClassificationModal, 
  ColumnProfileCard, 
  QualityScoreGauge, 
  RelationshipMatrix 
} from "../components/analysis";
import sessionService from "../services/sessionService";
import "./AnalysisPage.css";

export default function AnalysisPage() {
  const navigate = useNavigate();
  const session = sessionService.getSession();
  const sessionId = session?.sessionId;
  const workflowStatus = sessionService.getWorkflowStatus();

  const [showClassificationModal, setShowClassificationModal] = useState(false);
  const [showAllColumns, setShowAllColumns] = useState(false);
  
  // Use session data if available
  const classification = session?.classification || null;
  const quality = session?.quality || { overall: 0, breakdown: {} };
  const columns = session?.columns || [];
  const relationships = session?.relationships || [];
  const isClassificationConfirmed = session?.classificationConfirmed || false;

  // No session at all
  if (!sessionId) {
    return (
      <div className="analysis-page">
        <div className="no-session">
          <div className="no-session-icon">📤</div>
          <h2>No Dataset Uploaded</h2>
          <p>Please upload a dataset first to view analysis.</p>
          <Button variant="primary" onClick={() => navigate('/upload')}>
            Go to Upload
          </Button>
        </div>
      </div>
    );
  }

  // Session exists but no classification yet
  if (!classification) {
    return (
      <div className="analysis-page">
        <div className="no-session">
          <div className="no-session-icon">⏳</div>
          <h2>Analysis In Progress</h2>
          <p>Please complete the upload and classification process first.</p>
          <Button variant="primary" onClick={() => navigate('/upload')}>
            Return to Upload
          </Button>
        </div>
      </div>
    );
  }

  const getDatasetTypeIcon = (type) => {
    const icons = {
      'Financial': '💰',
      'Sales': '🛒',
      'Time-Series': '📈',
      'Healthcare': '🏥',
      'Generic': '📊'
    };
    return icons[type] || '📊';
  };

  // Convert columns object to array if needed
  const columnsArray = Array.isArray(columns) ? columns : Object.entries(columns || {}).map(([name, data]) => ({
    name,
    ...data
  }));

  return (
    <div className="analysis-page">
      <div className="page-header">
        <h1 className="page-title">Dataset Analysis</h1>
        <Button 
          variant="primary" 
          onClick={() => setShowClassificationModal(true)}
        >
          View Classification Details
        </Button>
      </div>

      {/* Analysis Status */}
      <div className="analysis-status">
        <Card>
          <div className="status-content">
            <div className="status-icon">{getDatasetTypeIcon(classification.type)}</div>
            <div className="status-info">
              <h3 className="status-title">
                {classification.type} Dataset
              </h3>
              <p className="status-description">
                {isClassificationConfirmed 
                  ? "Classification confirmed. Your dataset has been analyzed and is ready for insights."
                  : "Classification detected. Please confirm in the Upload section to proceed."
                }
              </p>
              <div className="confidence-display">
                Confidence: {((classification.confidence || 0.85) * 100).toFixed(0)}%
              </div>
            </div>
            <Badge variant={isClassificationConfirmed ? "success" : "warning"}>
              {isClassificationConfirmed ? "Confirmed" : "Pending Confirmation"}
            </Badge>
          </div>
        </Card>
      </div>

      {/* Quality Score */}
      {quality && (
        <div className="analysis-grid">
          <div className="analysis-section quality-section">
            <QualityScoreGauge 
              score={quality.overall || quality.completeness || 0.8}
              breakdown={quality.breakdown || {
                completeness: quality.completeness || 0.9,
                validity: quality.validity || 0.85,
                consistency: quality.consistency || 0.8,
                uniqueness: quality.uniqueness || 0.75
              }}
            />
          </div>

          <div className="analysis-section relationships-section">
            <RelationshipMatrix correlations={relationships} />
          </div>
        </div>
      )}

      {/* Column Profiles */}
      {columnsArray.length > 0 && (
        <div className="columns-section">
          <h2 className="section-title">Column Profiles ({columnsArray.length} columns)</h2>
          <div className="columns-grid">
            {(showAllColumns ? columnsArray : columnsArray.slice(0, 8)).map((column, idx) => (
              <ColumnProfileCard key={idx} column={column} />
            ))}
          </div>
          {columnsArray.length > 8 && (
            <button 
              className="more-columns-btn"
              onClick={() => setShowAllColumns(!showAllColumns)}
            >
              {showAllColumns 
                ? "Show less columns ↑" 
                : `+ ${columnsArray.length - 8} more columns ↓`
              }
            </button>
          )}
        </div>
      )}

      {/* Classification Modal */}
      {classification && (
        <DatasetClassificationModal
          isOpen={showClassificationModal}
          onClose={() => setShowClassificationModal(false)}
          classification={classification}
          onConfirm={() => {
            setShowClassificationModal(false);
            if (!isClassificationConfirmed) {
              navigate('/upload');
            }
          }}
          onReject={() => {
            setShowClassificationModal(false);
            navigate('/upload');
          }}
        />
      )}

      {/* Action buttons */}
      {!isClassificationConfirmed && (
        <Card className="action-card">
          <div className="action-content">
            <p>⚠️ Please confirm the dataset classification to proceed with preprocessing and insights.</p>
            <Button variant="primary" onClick={() => navigate('/upload')}>
              Confirm Classification
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
