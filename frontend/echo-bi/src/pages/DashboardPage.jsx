// src/pages/DashboardPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Card, Button, Badge, Loader } from '../components/common';
import { ChartCard } from '../components/visualization';
import { getVisualizationRecommendations, generateChart } from '../services/api';
import sessionService from '../services/sessionService';
import './DashboardPage.css';

export default function DashboardPage() {
  const navigate = useNavigate();
  const session = sessionService.getSession();
  const sessionId = session?.sessionId;
  const workflowStatus = sessionService.getWorkflowStatus();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [charts, setCharts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [generatingCharts, setGeneratingCharts] = useState(false);
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [selectedType, setSelectedType] = useState('all');

  useEffect(() => {
    if (sessionId && workflowStatus.canAccessDashboard) {
      fetchRecommendations();
    }
  }, [sessionId]);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getVisualizationRecommendations(sessionId);
      setRecommendations(response.recommendations || []);
      setSummary(response.summary || null);
    } catch (err) {
      setError(err.message || 'Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  const generateAllCharts = async () => {
    if (!recommendations.length) return;

    setGeneratingCharts(true);
    const newCharts = [];

    try {
      // Generate top 10 high-priority charts
      const topRecommendations = recommendations
        .filter(r => r.priority <= 2)
        .slice(0, 10);

      for (const rec of topRecommendations) {
        try {
          const chart = await generateChart(sessionId, rec.chart_id);
          newCharts.push(chart);
        } catch (err) {
          console.error(`Failed to generate chart ${rec.chart_id}:`, err);
        }
      }

      setCharts(newCharts);
    } catch (err) {
      setError(err.message || 'Failed to generate charts');
    } finally {
      setGeneratingCharts(false);
    }
  };

  const generateSingleChart = async (chartId) => {
    try {
      const chart = await generateChart(sessionId, chartId);
      setCharts(prev => [...prev, chart]);
    } catch (err) {
      console.error(`Failed to generate chart ${chartId}:`, err);
    }
  };

  const filteredRecommendations = recommendations.filter(rec => {
    const priorityMatch = selectedPriority === 'all' || rec.priority === parseInt(selectedPriority);
    const typeMatch = selectedType === 'all' || rec.chart_type === selectedType;
    return priorityMatch && typeMatch;
  });

  const availableChartTypes = [...new Set(recommendations.map(r => r.chart_type))];
  const highPriorityCount = recommendations.filter(r => r.priority === 1).length;

  // No session at all
  if (!sessionId) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-empty-state">
          <div className="empty-state-icon">📤</div>
          <h2 className="empty-state-title">No Dataset Uploaded</h2>
          <p className="empty-state-description">
            Please upload a dataset first to view visualizations and insights.
          </p>
          <Link to="/upload" className="btn btn-primary btn-lg">
            Go to Upload
          </Link>
        </div>
      </div>
    );
  }

  // Session exists but workflow not complete
  if (!workflowStatus.canAccessDashboard) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-empty-state">
          <div className="empty-state-icon">⏳</div>
          <h2 className="empty-state-title">Complete Upload Process First</h2>
          <p className="empty-state-description">
            Please confirm the dataset classification in the Upload section before viewing visualizations.
          </p>
          <div className="empty-state-status">
            <span className="status-label">Current Status:</span>
            <span className="status-value">{workflowStatus.label}</span>
          </div>
          <Link to="/upload" className="btn btn-primary btn-lg">
            Return to Upload
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <p className="loading-text">Loading recommendations...</p>
        </div>
      </div>
    );
  }

  if (error && !recommendations.length) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-error">
          <div className="error-icon">⚠️</div>
          <h2 className="error-title">Error Loading Visualizations</h2>
          <p className="error-message">{error}</p>
          <button className="btn btn-primary" onClick={fetchRecommendations}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      {/* Page Header */}
      <div className="dashboard-header">
        <div className="dashboard-header-left">
          <h1 className="dashboard-title">Visualization Dashboard</h1>
          <p className="dashboard-subtitle">Smart chart recommendations for your data</p>
        </div>
        <div className="dashboard-header-actions">
          <button 
            className="btn btn-primary"
            onClick={generateAllCharts}
            disabled={generatingCharts || !recommendations.length}
          >
            {generatingCharts ? (
              <>
                <span className="btn-spinner"></span>
                Generating...
              </>
            ) : (
              <>🎨 Generate Top Charts</>
            )}
          </button>
          <button 
            className="btn btn-secondary"
            onClick={fetchRecommendations}
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-card-icon">📊</div>
          <div className="stat-card-content">
            <div className="stat-card-value">{recommendations.length}</div>
            <div className="stat-card-label">Recommendations</div>
          </div>
        </div>
        <div className="stat-card stat-card-warning">
          <div className="stat-card-icon">⚡</div>
          <div className="stat-card-content">
            <div className="stat-card-value">{highPriorityCount}</div>
            <div className="stat-card-label">High Priority</div>
          </div>
        </div>
        <div className="stat-card stat-card-info">
          <div className="stat-card-icon">📈</div>
          <div className="stat-card-content">
            <div className="stat-card-value">{availableChartTypes.length}</div>
            <div className="stat-card-label">Chart Types</div>
          </div>
        </div>
        <div className="stat-card stat-card-success">
          <div className="stat-card-icon">✅</div>
          <div className="stat-card-content">
            <div className="stat-card-value">{charts.length}</div>
            <div className="stat-card-label">Generated</div>
          </div>
        </div>
      </div>

      {/* Generated Charts Section */}
      {charts.length > 0 && (
        <section className="dashboard-section">
          <div className="section-header">
            <h2 className="section-title">
              <span className="section-icon">📊</span>
              Generated Visualizations
            </h2>
            <span className="section-count">{charts.length} charts</span>
          </div>
          <div className="charts-grid">
            {charts.map((chart, idx) => (
              <div key={idx} className="chart-wrapper">
                <ChartCard 
                  chart={chart}
                  showControls={true}
                />
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Recommendations Section */}
      <section className="dashboard-section">
        <div className="section-header">
          <h2 className="section-title">
            <span className="section-icon">💡</span>
            Chart Recommendations
          </h2>
          <span className="section-count">{filteredRecommendations.length} of {recommendations.length}</span>
        </div>
        
        {/* Filters */}
        <div className="filters-bar">
          <div className="filter-group">
            <label className="filter-label">Priority</label>
            <select 
              value={selectedPriority} 
              onChange={(e) => setSelectedPriority(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Priorities</option>
              <option value="1">🔴 High (1)</option>
              <option value="2">🟡 Medium (2)</option>
              <option value="3">🟢 Low (3+)</option>
            </select>
          </div>
          <div className="filter-group">
            <label className="filter-label">Chart Type</label>
            <select 
              value={selectedType} 
              onChange={(e) => setSelectedType(e.target.value)}
              className="filter-select"
            >
              <option value="all">All Types</option>
              {availableChartTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          {(selectedPriority !== 'all' || selectedType !== 'all') && (
            <button 
              className="filter-clear-btn"
              onClick={() => {
                setSelectedPriority('all');
                setSelectedType('all');
              }}
            >
              Clear Filters
            </button>
          )}
        </div>

        {/* Recommendations Grid */}
        {filteredRecommendations.length === 0 ? (
          <div className="no-results">
            <p>No recommendations match your filters.</p>
            <button 
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setSelectedPriority('all');
                setSelectedType('all');
              }}
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="recommendations-grid">
            {filteredRecommendations.map((rec) => (
              <div key={rec.chart_id} className="recommendation-card">
                <div className="recommendation-header">
                  <div className="recommendation-badges">
                    <span className={`priority-badge priority-${rec.priority}`}>
                      Priority {rec.priority}
                    </span>
                    <span className="type-badge">{rec.chart_type}</span>
                  </div>
                  <span className="confidence-badge">
                    {(rec.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                
                <h3 className="recommendation-title">{rec.title}</h3>
                <p className="recommendation-description">{rec.description}</p>
                
                <div className="recommendation-details">
                  <div className="detail-row">
                    <span className="detail-label">Use Case:</span>
                    <span className="detail-value">{rec.use_case}</span>
                  </div>
                  {rec.reasoning && (
                    <div className="detail-row">
                      <span className="detail-label">Reasoning:</span>
                      <span className="detail-value">{rec.reasoning}</span>
                    </div>
                  )}
                </div>

                {rec.config && (
                  <div className="recommendation-config">
                    <div className="config-label">Configuration</div>
                    <div className="config-items">
                      {rec.config.x_axis && (
                        <div className="config-item">
                          <span className="config-key">X:</span>
                          <span className="config-value">{rec.config.x_axis}</span>
                        </div>
                      )}
                      {rec.config.y_axis && rec.config.y_axis.length > 0 && (
                        <div className="config-item">
                          <span className="config-key">Y:</span>
                          <span className="config-value">{rec.config.y_axis.join(', ')}</span>
                        </div>
                      )}
                      {rec.config.aggregation && (
                        <div className="config-item">
                          <span className="config-key">Agg:</span>
                          <span className="config-value">{rec.config.aggregation}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <button 
                  className={`btn ${charts.some(c => c.chart_id === rec.chart_id) ? 'btn-success' : 'btn-primary'} btn-sm recommendation-btn`}
                  onClick={() => generateSingleChart(rec.chart_id)}
                  disabled={charts.some(c => c.chart_id === rec.chart_id)}
                >
                  {charts.some(c => c.chart_id === rec.chart_id) ? '✓ Generated' : '🎨 Generate'}
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Navigation */}
      <div className="dashboard-navigation">
        <div className="nav-info">
          <span className="nav-dataset">Dataset: {session?.fileName || 'Unknown'}</span>
        </div>
        <div className="nav-actions">
          <Link to="/insights" className="btn btn-secondary">
            ← Back to Insights
          </Link>
          <Link to="/upload" className="btn btn-primary">
            Upload New Dataset
          </Link>
        </div>
      </div>
    </div>
  );
}
