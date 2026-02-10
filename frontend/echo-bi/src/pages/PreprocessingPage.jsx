// src/pages/PreprocessingPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Button, Badge, Loader } from "../components/common";
import sessionService from "../services/sessionService";
import { 
  getPreprocessingSuggestions, 
  applyPreprocessing, 
  getPreprocessingComparison,
  getAIPreprocessingSummary 
} from "../services/api";
import "./PreprocessingPage.css";

export default function PreprocessingPage() {
  const navigate = useNavigate();
  const session = sessionService.getSession();
  const sessionId = session?.sessionId;
  const workflowStatus = sessionService.getWorkflowStatus();
  const classification = session?.classification;

  // State for preprocessing
  const [suggestions, setSuggestions] = useState([]);
  const [selectedOps, setSelectedOps] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [preprocessingResult, setPreprocessingResult] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [aiSummary, setAiSummary] = useState(null);
  const [error, setError] = useState(null);

  // Fetch preprocessing suggestions on mount
  useEffect(() => {
    if (sessionId && workflowStatus.canAccessPreprocessing) {
      fetchSuggestions();
      fetchComparison();
    }
  }, [sessionId, workflowStatus.canAccessPreprocessing]);

  const fetchSuggestions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getPreprocessingSuggestions(sessionId);
      setSuggestions(data.suggestions || []);
      // Select all by default
      setSelectedOps((data.suggestions || []).map(s => s.operation_id));
    } catch (err) {
      console.error("Failed to fetch suggestions:", err);
      setError("Failed to load preprocessing suggestions");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchComparison = async () => {
    try {
      const data = await getPreprocessingComparison(sessionId);
      setComparison(data);
      
      // If preprocessing was applied, also get AI summary
      if (data.preprocessing_applied) {
        fetchAISummary();
      }
    } catch (err) {
      console.error("Failed to fetch comparison:", err);
    }
  };

  const fetchAISummary = async () => {
    try {
      const data = await getAIPreprocessingSummary(sessionId);
      setAiSummary(data.summary);
    } catch (err) {
      console.error("Failed to fetch AI summary:", err);
    }
  };

  const handleApplyPreprocessing = async () => {
    if (selectedOps.length === 0) {
      setError("Please select at least one operation to apply");
      return;
    }

    setIsApplying(true);
    setError(null);
    try {
      const result = await applyPreprocessing(sessionId, selectedOps);
      setPreprocessingResult(result);
      
      // Update session with preprocessing status
      sessionService.updateSession({ preprocessingApplied: true });
      
      // Refresh comparison data
      await fetchComparison();
      
      // Get AI summary
      await fetchAISummary();
    } catch (err) {
      console.error("Failed to apply preprocessing:", err);
      setError("Failed to apply preprocessing: " + err.message);
    } finally {
      setIsApplying(false);
    }
  };

  const toggleOperation = (opId) => {
    setSelectedOps(prev => 
      prev.includes(opId) 
        ? prev.filter(id => id !== opId)
        : [...prev, opId]
    );
  };

  const selectAll = () => setSelectedOps(suggestions.map(s => s.operation_id));
  const deselectAll = () => setSelectedOps([]);

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

  const preprocessingApplied = comparison?.preprocessing_applied || preprocessingResult;

  return (
    <div className="preprocessing-page">
      <h1 className="page-title">Preprocessing Pipeline</h1>
      
      {/* Error Message */}
      {error && (
        <Card className="error-card">
          <p className="error-message">⚠️ {error}</p>
        </Card>
      )}
      
      {/* Pipeline Summary */}
      <Card className="pipeline-summary">
        <div className="summary-header">
          <div className="summary-icon">{getDatasetTypeIcon(classification?.type)}</div>
          <div className="summary-info">
            <h3>{classification?.type} Pipeline</h3>
            <p>Domain-specific preprocessing for {classification?.type?.toLowerCase()} data</p>
          </div>
          <Badge variant={preprocessingApplied ? "success" : "warning"}>
            {preprocessingApplied ? "Applied" : "Pending"}
          </Badge>
        </div>
      </Card>

      {/* Before/After Comparison */}
      {comparison && (
        <Card title="📊 Data Quality Comparison">
          <div className="comparison-grid">
            <div className="comparison-section">
              <h4>Before Preprocessing</h4>
              <div className="comparison-stats">
                <div className="stat-item">
                  <span className="stat-label">Rows</span>
                  <span className="stat-value">{comparison.comparison?.before?.rows?.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Columns</span>
                  <span className="stat-value">{comparison.comparison?.before?.columns}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Missing Values</span>
                  <span className="stat-value highlight-bad">{comparison.comparison?.before?.missing_cells?.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Duplicates</span>
                  <span className="stat-value highlight-bad">{comparison.comparison?.before?.duplicate_rows?.toLocaleString()}</span>
                </div>
              </div>
            </div>
            
            <div className="comparison-arrow">→</div>
            
            <div className="comparison-section">
              <h4>After Preprocessing</h4>
              <div className="comparison-stats">
                <div className="stat-item">
                  <span className="stat-label">Rows</span>
                  <span className="stat-value">{comparison.comparison?.after?.rows?.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Columns</span>
                  <span className="stat-value">{comparison.comparison?.after?.columns}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Missing Values</span>
                  <span className="stat-value highlight-good">{comparison.comparison?.after?.missing_cells?.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Duplicates</span>
                  <span className="stat-value highlight-good">{comparison.comparison?.after?.duplicate_rows?.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Changes Summary */}
          {comparison.comparison?.changes && (
            <div className="changes-summary">
              <h4>Changes Applied</h4>
              <div className="changes-badges">
                {comparison.comparison.changes.missing_cells_fixed > 0 && (
                  <Badge variant="success">
                    {comparison.comparison.changes.missing_cells_fixed} missing values fixed
                  </Badge>
                )}
                {comparison.comparison.changes.duplicates_removed > 0 && (
                  <Badge variant="success">
                    {comparison.comparison.changes.duplicates_removed} duplicates removed
                  </Badge>
                )}
                {comparison.comparison.changes.rows_removed > 0 && (
                  <Badge variant="info">
                    {comparison.comparison.changes.rows_removed} rows removed
                  </Badge>
                )}
                {comparison.comparison.changes.columns_added > 0 && (
                  <Badge variant="info">
                    {comparison.comparison.changes.columns_added} columns added
                  </Badge>
                )}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* AI Summary */}
      {aiSummary && (
        <Card title="🤖 AI Preprocessing Summary">
          <div className="ai-summary">
            <p>{aiSummary}</p>
          </div>
        </Card>
      )}

      {/* Preprocessing Operations */}
      <Card title="⚙️ Available Operations">
        {isLoading ? (
          <div className="loading-container">
            <Loader />
            <p>Loading preprocessing suggestions...</p>
          </div>
        ) : suggestions.length === 0 ? (
          <div className="no-suggestions">
            <p>No preprocessing operations suggested for this dataset.</p>
            <p className="hint">The data appears to be clean and ready for analysis.</p>
          </div>
        ) : (
          <>
            <div className="operations-controls">
              <Button variant="ghost" size="small" onClick={selectAll}>
                Select All ({suggestions.length})
              </Button>
              <Button variant="ghost" size="small" onClick={deselectAll}>
                Deselect All
              </Button>
              <span className="selected-count">
                {selectedOps.length} of {suggestions.length} selected
              </span>
            </div>
            
            <div className="preprocessing-steps">
              {suggestions.map((op) => (
                <div 
                  key={op.operation_id} 
                  className={`step-item ${selectedOps.includes(op.operation_id) ? 'selected' : ''}`}
                  onClick={() => !preprocessingApplied && toggleOperation(op.operation_id)}
                >
                  <div className="step-checkbox">
                    <input 
                      type="checkbox" 
                      checked={selectedOps.includes(op.operation_id)}
                      onChange={() => toggleOperation(op.operation_id)}
                      disabled={preprocessingApplied}
                    />
                  </div>
                  <div className="step-details">
                    <h4>{op.operation_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                    <p>{op.description}</p>
                    {op.column && <span className="column-tag">Column: {op.column}</span>}
                  </div>
                  <Badge variant={preprocessingApplied ? "success" : "default"}>
                    {preprocessingApplied ? "Applied" : "Pending"}
                  </Badge>
                </div>
              ))}
            </div>
            
            {!preprocessingApplied && (
              <div className="apply-section">
                <Button 
                  variant="primary" 
                  onClick={handleApplyPreprocessing}
                  disabled={isApplying || selectedOps.length === 0}
                >
                  {isApplying ? "Applying..." : `Apply ${selectedOps.length} Operations`}
                </Button>
              </div>
            )}
          </>
        )}
      </Card>

      {/* Audit Trail */}
      {comparison?.audit_trail && comparison.audit_trail.length > 0 && (
        <Card title="📋 Audit Trail">
          <div className="audit-trail">
            {comparison.audit_trail.map((entry, idx) => (
              <div key={idx} className="audit-item">
                <span className="audit-time">{new Date(entry.timestamp).toLocaleTimeString()}</span>
                <span className="audit-action">
                  <strong>{entry.operation_type}</strong> on {entry.column || 'all columns'}: {entry.description}
                  {entry.values_changed > 0 && (
                    <span className="audit-impact"> ({entry.values_changed.toLocaleString()} values changed)</span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Navigation */}
      <Card className="navigation-card">
        <div className="navigation-content">
          <h4>What's next?</h4>
          <p>
            {preprocessingApplied 
              ? "Your data has been preprocessed and is ready for analysis."
              : "Apply preprocessing operations above, or proceed with the original data."}
          </p>
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
