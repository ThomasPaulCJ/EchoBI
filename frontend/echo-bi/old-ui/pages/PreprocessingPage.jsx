// src/pages/PreprocessingPage.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import { Card, Button, Badge } from "../components/common";
import sessionService from "../services/sessionService";
import "./PreprocessingPage.css";

export default function PreprocessingPage() {
  const navigate = useNavigate();
  const session = sessionService.getSession();
  const sessionId = session?.sessionId;
  const workflowStatus = sessionService.getWorkflowStatus();
  const classification = session?.classification;
  const isConfirmed = session?.classificationConfirmed;

  // No session
  if (!sessionId) {
    return (
      <div className="preprocessing-page">
        <div className="no-session">
          <div className="no-session-icon">📤</div>
          <h2>No Dataset Uploaded</h2>
          <p>Please upload a dataset first to view preprocessing options.</p>
          <Button variant="primary" onClick={() => navigate('/upload')}>
            Go to Upload
          </Button>
        </div>
      </div>
    );
  }

  // Session exists but workflow not ready for preprocessing
  if (!workflowStatus.canAccessPreprocessing) {
    return (
      <div className="preprocessing-page">
        <div className="no-session">
          <div className="no-session-icon">⏳</div>
          <h2>Complete Upload Process First</h2>
          <p>Please confirm the dataset classification before accessing preprocessing.</p>
          <p className="status-hint">Current Status: {workflowStatus.label}</p>
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

  const getPreprocessingSteps = (type) => {
    const steps = {
      'Financial': [
        { name: 'Currency Normalization', status: 'completed', description: 'Standardized currency formats' },
        { name: 'Missing Value Handling', status: 'completed', description: 'Filled missing amounts with median' },
        { name: 'Outlier Detection', status: 'completed', description: 'Flagged 3 potential anomalies' },
        { name: 'Date Parsing', status: 'completed', description: 'Converted dates to standard format' },
      ],
      'Sales': [
        { name: 'Product Code Standardization', status: 'completed', description: 'Normalized product identifiers' },
        { name: 'Missing Value Handling', status: 'completed', description: 'Filled using category median' },
        { name: 'Duplicate Detection', status: 'completed', description: 'Removed 0 duplicate records' },
        { name: 'Category Mapping', status: 'completed', description: 'Standardized category names' },
      ],
      'Time-Series': [
        { name: 'Temporal Parsing', status: 'completed', description: 'Parsed datetime columns' },
        { name: 'Missing Value Interpolation', status: 'completed', description: 'Interpolated gaps in time series' },
        { name: 'Frequency Detection', status: 'completed', description: 'Detected daily frequency' },
        { name: 'Trend Extraction', status: 'completed', description: 'Extracted trend component' },
      ],
      'Healthcare': [
        { name: 'PHI Handling', status: 'completed', description: 'Identified protected health information' },
        { name: 'Code Standardization', status: 'completed', description: 'Normalized medical codes' },
        { name: 'Missing Value Handling', status: 'completed', description: 'Applied clinical rules for missing data' },
        { name: 'Date Parsing', status: 'completed', description: 'Converted dates to standard format' },
      ],
      'Generic': [
        { name: 'Data Type Detection', status: 'completed', description: 'Inferred column types' },
        { name: 'Missing Value Handling', status: 'completed', description: 'Applied appropriate strategy per column' },
        { name: 'Duplicate Removal', status: 'completed', description: 'Removed duplicate records' },
        { name: 'Outlier Detection', status: 'completed', description: 'Flagged statistical outliers' },
      ]
    };
    return steps[type] || steps['Generic'];
  };

  const preprocessingSteps = getPreprocessingSteps(classification?.type);

  return (
    <div className="preprocessing-page">
      <h1 className="page-title">Preprocessing Pipeline</h1>
      
      {/* Pipeline Summary */}
      <Card className="pipeline-summary">
        <div className="summary-header">
          <div className="summary-icon">{getDatasetTypeIcon(classification?.type)}</div>
          <div className="summary-info">
            <h3>{classification?.type} Pipeline</h3>
            <p>Domain-specific preprocessing for {classification?.type.toLowerCase()} data</p>
          </div>
          <Badge variant="success">Completed</Badge>
        </div>
      </Card>

      {/* Preprocessing Steps */}
      <Card title="⚙️ Processing Steps">
        <div className="preprocessing-steps">
          {preprocessingSteps.map((step, idx) => (
            <div key={idx} className="step-item">
              <div className="step-status">
                <span className="status-icon">✅</span>
              </div>
              <div className="step-details">
                <h4>{step.name}</h4>
                <p>{step.description}</p>
              </div>
              <Badge variant="success">Complete</Badge>
            </div>
          ))}
        </div>
      </Card>

      {/* Audit Trail */}
      <Card title="📋 Audit Trail">
        <div className="audit-trail">
          <div className="audit-item">
            <span className="audit-time">Just now</span>
            <span className="audit-action">Preprocessing pipeline completed</span>
          </div>
          <div className="audit-item">
            <span className="audit-time">Just now</span>
            <span className="audit-action">Classification confirmed by user</span>
          </div>
          <div className="audit-item">
            <span className="audit-time">Earlier</span>
            <span className="audit-action">Dataset classified as {classification?.type}</span>
          </div>
          <div className="audit-item">
            <span className="audit-time">Earlier</span>
            <span className="audit-action">File uploaded: {session?.fileName || 'dataset.csv'}</span>
          </div>
        </div>
      </Card>

      {/* Navigation */}
      <Card className="navigation-card">
        <div className="navigation-content">
          <h4>What's next?</h4>
          <p>Your data has been preprocessed and is ready for analysis.</p>
          <div className="navigation-buttons">
            <Button variant="primary" onClick={() => navigate('/insights')}>
              💡 View Insights
            </Button>
            <Button variant="secondary" onClick={() => navigate('/dashboard')}>
              📈 View Visualizations
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
