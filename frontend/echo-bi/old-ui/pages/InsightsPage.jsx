// src/pages/InsightsPage.jsx
// User-friendly insights page for both technical and non-technical users
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Badge, Loader } from '../components/common';
import PreprocessingDetails from '../components/PreprocessingDetails';
import { getInsights } from '../services/api';
import sessionService from '../services/sessionService';
import './InsightsPage.css';

// Helper to convert technical terms to plain language
const getPlainLanguageExplanation = (insight) => {
  const explanations = {
    distribution: {
      title: "Data Shape Analysis",
      icon: "📊",
      simple: "We looked at how your data values are spread out.",
      whatItMeans: (desc) => {
        if (desc.includes('skewed')) {
          return "Your data has more values on one side than the other. Think of it like a lopsided hill - most values cluster on one end.";
        }
        return "This tells us about the overall pattern of your data values.";
      },
      whyItMatters: "Understanding data shape helps identify if there are unusual patterns that might affect your analysis."
    },
    anomaly: {
      title: "Unusual Values Found",
      icon: "⚠️",
      simple: "We found some values that stand out from the rest.",
      whatItMeans: (desc) => {
        if (desc.includes('outlier')) {
          return "Some numbers are much higher or lower than typical values. Like finding a $10,000 purchase when most are under $100.";
        }
        return "These are data points that don't follow the usual pattern.";
      },
      whyItMatters: "Unusual values could be errors that need fixing, or important discoveries worth investigating."
    },
    correlation: {
      title: "Connected Data Points",
      icon: "🔗",
      simple: "We found columns that tend to change together.",
      whatItMeans: (desc) => {
        if (desc.includes('positive')) {
          return "When one value goes up, the other tends to go up too. Like how more sales often means more revenue.";
        }
        if (desc.includes('negative')) {
          return "When one value goes up, the other tends to go down. Like how higher prices might mean fewer purchases.";
        }
        return "These columns have a relationship - changes in one often relate to changes in the other.";
      },
      whyItMatters: "Understanding connections helps predict outcomes and identify what drives your key metrics."
    },
    trend: {
      title: "Pattern Over Time",
      icon: "📈",
      simple: "We spotted a trend in your time-based data.",
      whatItMeans: (desc) => {
        if (desc.includes('increasing')) {
          return "Values are generally going up over time, like a growing savings account.";
        }
        if (desc.includes('decreasing')) {
          return "Values are generally going down over time.";
        }
        return "There's a consistent pattern in how values change over time.";
      },
      whyItMatters: "Trends help you forecast future values and understand if things are improving or declining."
    },
    summary: {
      title: "Data Summary",
      icon: "📋",
      simple: "Here's an overview of important characteristics.",
      whatItMeans: () => "This provides key facts about your data that are worth knowing.",
      whyItMatters: "Understanding your data's basic characteristics is the foundation for good analysis."
    },
    recommendation: {
      title: "Suggested Action",
      icon: "💡",
      simple: "Based on our analysis, here's what you might want to do.",
      whatItMeans: () => "This is a recommendation based on patterns we found in your data.",
      whyItMatters: "Taking action on insights helps improve your data quality and analysis accuracy."
    }
  };
  
  return explanations[insight.category] || explanations.summary;
};

// Severity to user-friendly impact
const getImpactInfo = (severity) => {
  const impacts = {
    high: {
      label: "High Impact",
      color: "#dc3545",
      bgColor: "#fff5f5",
      icon: "🔴",
      description: "This finding is important and may significantly affect your analysis."
    },
    medium: {
      label: "Medium Impact",
      color: "#fd7e14",
      bgColor: "#fff8f0",
      icon: "🟠",
      description: "Worth reviewing, but not critical for most analyses."
    },
    low: {
      label: "Low Impact",
      color: "#28a745",
      bgColor: "#f0fff4",
      icon: "🟢",
      description: "Good to know, but unlikely to significantly affect your results."
    }
  };
  return impacts[severity] || impacts.low;
};

// Format evidence for display
const formatEvidence = (evidence) => {
  if (!evidence || typeof evidence !== 'object') return null;
  
  const formatted = [];
  for (const [key, value] of Object.entries(evidence)) {
    if (key === 'outlier_details' || key === 'test') continue;
    
    let displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    let displayValue = value;
    
    if (typeof value === 'number') {
      if (key.includes('percent')) {
        displayValue = `${value.toFixed(1)}%`;
      } else if (key.includes('p_value')) {
        displayValue = value < 0.001 ? '< 0.001' : value.toFixed(4);
      } else if (Math.abs(value) < 0.01 || Math.abs(value) > 1000) {
        displayValue = value.toExponential(2);
      } else {
        displayValue = value.toFixed(3);
      }
    }
    
    formatted.push({ key: displayKey, value: displayValue });
  }
  return formatted;
};

export default function InsightsPage() {
  const navigate = useNavigate();
  
  const session = sessionService.getSession();
  const workflowStatus = sessionService.getWorkflowStatus();
  const sessionId = session?.sessionId;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [insights, setInsights] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedImpact, setSelectedImpact] = useState('all');
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [expandedInsights, setExpandedInsights] = useState(new Set());
  const [fetchAttempted, setFetchAttempted] = useState(false);
  const [activeTab, setActiveTab] = useState('insights'); // 'insights' or 'preprocessing'

  const fetchInsights = useCallback(async () => {
    if (!sessionId) {
      setError('No session ID available');
      return;
    }
    
    setLoading(true);
    setError(null);
    setFetchAttempted(true);
    
    try {
      const response = await getInsights(sessionId);
      setInsights(response.insights || []);
      setRecommendations(response.recommendations || []);
      setSummary(response.summary || null);
    } catch (err) {
      setError(err.message || 'Failed to fetch insights');
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    if (sessionId && workflowStatus?.canAccessInsights && !fetchAttempted && !loading) {
      fetchInsights();
    }
  }, [sessionId, workflowStatus?.canAccessInsights, fetchAttempted, loading, fetchInsights]);

  const toggleInsightExpanded = (insightId) => {
    setExpandedInsights(prev => {
      const next = new Set(prev);
      if (next.has(insightId)) {
        next.delete(insightId);
      } else {
        next.add(insightId);
      }
      return next;
    });
  };

  const filteredInsights = insights.filter(insight => {
    const categoryMatch = selectedCategory === 'all' || insight.category === selectedCategory;
    const impactMatch = selectedImpact === 'all' || insight.severity === selectedImpact;
    return categoryMatch && impactMatch;
  });

  // Group insights by category for summary
  const insightsByCategory = insights.reduce((acc, insight) => {
    acc[insight.category] = (acc[insight.category] || 0) + 1;
    return acc;
  }, {});

  // ========================================
  // RENDER: No session
  // ========================================
  if (!sessionId) {
    return (
      <div className="insights-page">
        <div className="empty-state">
          <div className="empty-icon">📤</div>
          <h2>No Dataset Uploaded</h2>
          <p>Upload a dataset to discover insights about your data.</p>
          <Button variant="primary" onClick={() => navigate('/upload')}>
            Upload Dataset
          </Button>
        </div>
      </div>
    );
  }

  // ========================================
  // RENDER: Workflow not complete
  // ========================================
  if (!workflowStatus?.canAccessInsights) {
    return (
      <div className="insights-page">
        <div className="empty-state">
          <div className="empty-icon">⏳</div>
          <h2>Almost There!</h2>
          <p>Complete the upload process to unlock insights.</p>
          <div className="checklist">
            <div className={`checklist-item ${session ? 'completed' : ''}`}>
              <span className="check">{session ? '✓' : '○'}</span>
              <span>Upload dataset</span>
            </div>
            <div className={`checklist-item ${session?.classificationConfirmed ? 'completed' : ''}`}>
              <span className="check">{session?.classificationConfirmed ? '✓' : '○'}</span>
              <span>Confirm data type</span>
            </div>
            <div className={`checklist-item ${session?.preprocessingComplete ? 'completed' : ''}`}>
              <span className="check">{session?.preprocessingComplete ? '✓' : '○'}</span>
              <span>Complete preprocessing</span>
            </div>
          </div>
          <Button variant="primary" onClick={() => navigate('/upload')}>
            Continue Setup
          </Button>
        </div>
      </div>
    );
  }

  // ========================================
  // RENDER: Loading
  // ========================================
  if (loading) {
    return (
      <div className="insights-page">
        <div className="loading-state">
          <Loader text="Analyzing your data..." />
          <p className="loading-hint">We're examining patterns, outliers, and trends in your dataset.</p>
        </div>
      </div>
    );
  }

  // ========================================
  // RENDER: Error
  // ========================================
  if (error) {
    return (
      <div className="insights-page">
        <div className="error-state">
          <div className="error-icon">❌</div>
          <h2>Something Went Wrong</h2>
          <p>{error}</p>
          <Button variant="primary" onClick={fetchInsights}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // ========================================
  // RENDER: No insights yet
  // ========================================
  if (insights.length === 0) {
    return (
      <div className="insights-page">
        <div className="page-header">
          <div>
            <h1>Data Insights</h1>
            <p className="subtitle">Discover what your data is telling you</p>
          </div>
        </div>
        
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h2>Ready to Analyze</h2>
          <p>Click below to discover patterns, anomalies, and trends in your data.</p>
          {session?.classification && (
            <div className="dataset-badge">
              <Badge variant="primary">{session.classification.type} Dataset</Badge>
              <span className="file-name">{session.fileName}</span>
            </div>
          )}
          <Button variant="primary" size="large" onClick={fetchInsights}>
            🚀 Generate Insights
          </Button>
        </div>
      </div>
    );
  }

  // ========================================
  // RENDER: Main insights view
  // ========================================
  return (
    <div className="insights-page">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1>Data Insights</h1>
          <p className="subtitle">
            {session?.classification?.type} dataset • {insights.length} insights discovered
          </p>
        </div>
        <div className="header-actions">
          <label className="toggle-label">
            <input 
              type="checkbox" 
              checked={showTechnicalDetails}
              onChange={(e) => setShowTechnicalDetails(e.target.checked)}
            />
            <span>Show Technical Details</span>
          </label>
          <Button variant="secondary" onClick={fetchInsights} disabled={loading}>
            🔄 Refresh
          </Button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="insights-tabs">
        <button 
          className={`tab-button ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          <span className="tab-icon">💡</span>
          <span className="tab-label">Data Insights</span>
          <span className="tab-badge">{insights.length}</span>
        </button>
        <button 
          className={`tab-button ${activeTab === 'preprocessing' ? 'active' : ''}`}
          onClick={() => setActiveTab('preprocessing')}
        >
          <span className="tab-icon">📋</span>
          <span className="tab-label">Data Quality & Preprocessing</span>
        </button>
      </div>

      {/* Tab Content: Preprocessing Details */}
      {activeTab === 'preprocessing' && (
        <PreprocessingDetails 
          columnProfiles={session?.columns || {}}
          qualityReport={session?.quality || null}
          sessionId={sessionId}
        />
      )}

      {/* Tab Content: Insights */}
      {activeTab === 'insights' && (
        <>
          {/* Executive Summary */}
          <Card className="executive-summary">
        <h2>📊 Quick Summary</h2>
        <p className="summary-text">
          We analyzed your <strong>{session?.classification?.type || 'dataset'}</strong> and found{' '}
          <strong>{insights.length} insights</strong> to help you understand your data better.
        </p>
        
        <div className="summary-stats">
          <div className="stat-item">
            <div className="stat-number">{summary?.by_severity?.high || 0}</div>
            <div className="stat-label">High Impact</div>
            <div className="stat-indicator high"></div>
          </div>
          <div className="stat-item">
            <div className="stat-number">{summary?.by_severity?.medium || 0}</div>
            <div className="stat-label">Medium Impact</div>
            <div className="stat-indicator medium"></div>
          </div>
          <div className="stat-item">
            <div className="stat-number">{summary?.by_severity?.low || 0}</div>
            <div className="stat-label">Low Impact</div>
            <div className="stat-indicator low"></div>
          </div>
        </div>

        <div className="category-pills">
          {Object.entries(insightsByCategory).map(([category, count]) => (
            <span 
              key={category} 
              className="category-pill"
              onClick={() => setSelectedCategory(category)}
            >
              {getPlainLanguageExplanation({ category }).icon} {category} ({count})
            </span>
          ))}
        </div>
      </Card>

      {/* Filters */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>Filter by Type:</label>
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="all">All Types</option>
            <option value="trend">📈 Trends</option>
            <option value="anomaly">⚠️ Anomalies</option>
            <option value="correlation">🔗 Connections</option>
            <option value="distribution">📊 Data Shape</option>
            <option value="summary">📋 Summary</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Filter by Impact:</label>
          <select 
            value={selectedImpact} 
            onChange={(e) => setSelectedImpact(e.target.value)}
          >
            <option value="all">All Impacts</option>
            <option value="high">🔴 High Impact</option>
            <option value="medium">🟠 Medium Impact</option>
            <option value="low">🟢 Low Impact</option>
          </select>
        </div>
        <div className="filter-count">
          Showing {filteredInsights.length} of {insights.length} insights
        </div>
      </div>

      {/* Insights List */}
      <div className="insights-list">
        {filteredInsights.length === 0 ? (
          <Card className="no-results">
            <p>No insights match your current filters.</p>
            <Button 
              variant="secondary" 
              size="small"
              onClick={() => {
                setSelectedCategory('all');
                setSelectedImpact('all');
              }}
            >
              Clear Filters
            </Button>
          </Card>
        ) : (
          filteredInsights.map((insight) => {
            const plainLang = getPlainLanguageExplanation(insight);
            const impact = getImpactInfo(insight.severity);
            const isExpanded = expandedInsights.has(insight.insight_id);
            const evidence = formatEvidence(insight.evidence);
            
            return (
              <Card 
                key={insight.insight_id} 
                className={`insight-card impact-${insight.severity}`}
                style={{ borderLeftColor: impact.color }}
              >
                {/* Card Header */}
                <div className="insight-header">
                  <div className="insight-type">
                    <span className="type-icon">{plainLang.icon}</span>
                    <span className="type-label">{plainLang.title}</span>
                  </div>
                  <div className="impact-badge" style={{ background: impact.bgColor, color: impact.color }}>
                    {impact.icon} {impact.label}
                  </div>
                </div>

                {/* Main Content - Plain Language */}
                <div className="insight-content">
                  <h3 className="insight-title">{insight.title}</h3>
                  
                  <div className="plain-explanation">
                    <p className="what-we-found">
                      <strong>What we found:</strong> {plainLang.simple}
                    </p>
                    <p className="what-it-means">
                      <strong>What this means:</strong> {plainLang.whatItMeans(insight.description)}
                    </p>
                    <p className="why-it-matters">
                      <strong>Why it matters:</strong> {plainLang.whyItMatters}
                    </p>
                  </div>

                  {/* Affected Columns */}
                  {insight.affected_columns?.length > 0 && (
                    <div className="affected-columns">
                      <strong>Columns involved:</strong>
                      <div className="column-tags">
                        {insight.affected_columns.map(col => (
                          <span key={col} className="column-tag">{col}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Items - Always Visible */}
                  {insight.action_items?.length > 0 && (
                    <div className="action-items">
                      <strong>💡 What you can do:</strong>
                      <ul>
                        {insight.action_items.map((action, idx) => (
                          <li key={idx}>{action}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Expandable Technical Details */}
                  {(showTechnicalDetails || isExpanded) && evidence && evidence.length > 0 && (
                    <div className="technical-details">
                      <div className="technical-header">
                        <strong>🔬 Technical Details</strong>
                        <span className="confidence">
                          Confidence: {(insight.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      
                      <div className="original-description">
                        <em>{insight.description}</em>
                      </div>
                      
                      <div className="evidence-grid">
                        {evidence.map(({ key, value }) => (
                          <div key={key} className="evidence-item">
                            <span className="evidence-key">{key}</span>
                            <span className="evidence-value">{value}</span>
                          </div>
                        ))}
                      </div>
                      
                      {insight.visualization_type && (
                        <div className="viz-suggestion">
                          📊 Suggested visualization: <strong>{insight.visualization_type}</strong>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Expand/Collapse Button */}
                  {!showTechnicalDetails && evidence && evidence.length > 0 && (
                    <button 
                      className="expand-btn"
                      onClick={() => toggleInsightExpanded(insight.insight_id)}
                    >
                      {isExpanded ? '▲ Hide technical details' : '▼ Show technical details'}
                    </button>
                  )}
                </div>
              </Card>
            );
          })
        )}
      </div>

      {/* Recommendations Section */}
      {recommendations.length > 0 && (
        <div className="recommendations-section">
          <h2>💡 Recommended Next Steps</h2>
          <p className="section-subtitle">Based on our analysis, here's what we suggest:</p>
          
          <div className="recommendations-grid">
            {recommendations.map((rec, idx) => (
              <Card key={idx} className="recommendation-card">
                <div className="rec-priority">
                  <span className="priority-number">{rec.priority || idx + 1}</span>
                </div>
                <div className="rec-content">
                  <h4>{rec.title}</h4>
                  <p>{rec.description}</p>
                  {rec.actions?.length > 0 && (
                    <ul className="rec-actions">
                      {rec.actions.slice(0, 3).map((action, i) => (
                        <li key={i}>{action}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Help Section */}
      <Card className="help-section">
        <h3>📚 Understanding Your Insights</h3>
        <div className="help-grid">
          <div className="help-item">
            <span className="help-icon">📊</span>
            <div>
              <strong>Data Shape</strong>
              <p>Shows how values are distributed - are they spread evenly or clustered?</p>
            </div>
          </div>
          <div className="help-item">
            <span className="help-icon">⚠️</span>
            <div>
              <strong>Anomalies</strong>
              <p>Unusual values that stand out - could be errors or important discoveries.</p>
            </div>
          </div>
          <div className="help-item">
            <span className="help-icon">🔗</span>
            <div>
              <strong>Connections</strong>
              <p>Relationships between columns - when one changes, does another change too?</p>
            </div>
          </div>
          <div className="help-item">
            <span className="help-icon">📈</span>
            <div>
              <strong>Trends</strong>
              <p>Patterns over time - is something increasing, decreasing, or staying stable?</p>
            </div>
          </div>
        </div>
      </Card>
        </>
      )}

      {/* Navigation */}
      <div className="page-navigation">
        <Button variant="secondary" onClick={() => navigate('/upload')}>
          ← Back to Upload
        </Button>
        <Button variant="primary" onClick={() => navigate('/dashboard')}>
          View Dashboard →
        </Button>
      </div>
    </div>
  );
}
