// src/pages/DashboardPage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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

  // No session at all
  if (!sessionId) {
    return (
      <div className="dashboard-page">
        <div className="no-session">
          <div className="no-session-icon">📤</div>
          <h2>No Dataset Uploaded</h2>
          <p>Please upload a dataset first to view visualizations.</p>
          <Button variant="primary" onClick={() => navigate('/upload')}>
            Go to Upload
          </Button>
        </div>
      </div>
    );
  }

  // Session exists but workflow not complete
  if (!workflowStatus.canAccessDashboard) {
    return (
      <div className="dashboard-page">
        <div className="no-session">
          <div className="no-session-icon">⏳</div>
          <h2>Complete Upload Process First</h2>
          <p>Please confirm the dataset classification in the Upload section before viewing visualizations.</p>
          <p className="status-hint">Current Status: {workflowStatus.label}</p>
          <Button variant="primary" onClick={() => navigate('/upload')}>
            Return to Upload
          </Button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <Loader fullPage text="Loading recommendations..." />
      </div>
    );
  }

  if (error && !recommendations.length) {
    return (
      <div className="dashboard-page">
        <Card title="Error Loading Visualizations">
          <p className="error-message">{error}</p>
          <Button variant="primary" onClick={fetchRecommendations}>
            Retry
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Visualization Dashboard</h1>
          <p className="subtitle">Smart chart recommendations for your data</p>
        </div>
        <div className="header-actions">
          <Button 
            variant="primary" 
            onClick={generateAllCharts}
            disabled={generatingCharts || !recommendations.length}
          >
            {generatingCharts ? '⏳ Generating...' : '🎨 Generate Top Charts'}
          </Button>
          <Button 
            variant="secondary" 
            onClick={fetchRecommendations}
            disabled={loading}
          >
            🔄 Refresh
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="summary-grid">
          <Card className="summary-card">
            <div className="stat-label">Recommendations</div>
            <div className="stat-value">{recommendations.length}</div>
          </Card>
          <Card className="summary-card">
            <div className="stat-label">High Priority</div>
            <div className="stat-value priority-high">
              {recommendations.filter(r => r.priority === 1).length}
            </div>
          </Card>
          <Card className="summary-card">
            <div className="stat-label">Chart Types</div>
            <div className="stat-value">{availableChartTypes.length}</div>
          </Card>
          <Card className="summary-card">
            <div className="stat-label">Generated</div>
            <div className="stat-value generated">{charts.length}</div>
          </Card>
        </div>
      )}

      {/* Generated Charts Section */}
      {charts.length > 0 && (
        <div className="charts-section">
          <h2>📊 Generated Visualizations</h2>
          <div className="charts-grid">
            {charts.map((chart, idx) => (
              <ChartCard 
                key={idx} 
                chart={chart}
                showControls={true}
              />
            ))}
          </div>
        </div>
      )}

      {/* Recommendations Section */}
      <div className="recommendations-section">
        <h2>💡 Chart Recommendations</h2>
        
        {/* Filters */}
        <Card className="filters-card">
          <div className="filters">
            <div className="filter-group">
              <label>Priority:</label>
              <select 
                value={selectedPriority} 
                onChange={(e) => setSelectedPriority(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Priorities</option>
                <option value="1">High (1)</option>
                <option value="2">Medium (2)</option>
                <option value="3">Low (3+)</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Chart Type:</label>
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
            <div className="filter-info">
              Showing {filteredRecommendations.length} of {recommendations.length} recommendations
            </div>
          </div>
        </Card>

        {/* Recommendations List */}
        <div className="recommendations-list">
          {filteredRecommendations.length === 0 ? (
            <Card>
              <div className="no-recommendations">
                <p>No recommendations match your filters.</p>
                <Button 
                  variant="secondary" 
                  size="small"
                  onClick={() => {
                    setSelectedPriority('all');
                    setSelectedType('all');
                  }}
                >
                  Clear Filters
                </Button>
              </div>
            </Card>
          ) : (
            filteredRecommendations.map((rec) => (
              <Card key={rec.chart_id} className="recommendation-card">
                <div className="rec-header">
                  <div className="rec-title-section">
                    <h3 className="rec-title">{rec.title}</h3>
                    <div className="rec-badges">
                      <Badge 
                        variant={rec.priority === 1 ? 'danger' : rec.priority === 2 ? 'warning' : 'info'}
                        size="small"
                      >
                        Priority {rec.priority}
                      </Badge>
                      <Badge variant="secondary" size="small">
                        {rec.chart_type}
                      </Badge>
                      <span className="confidence-badge">
                        {(rec.confidence * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>
                  <Button 
                    variant="primary" 
                    size="small"
                    onClick={() => generateSingleChart(rec.chart_id)}
                    disabled={charts.some(c => c.chart_id === rec.chart_id)}
                  >
                    {charts.some(c => c.chart_id === rec.chart_id) ? '✓ Generated' : '🎨 Generate'}
                  </Button>
                </div>

                <p className="rec-description">{rec.description}</p>

                <div className="rec-details">
                  <div className="detail-item">
                    <strong>Use Case:</strong> {rec.use_case}
                  </div>
                  {rec.reasoning && (
                    <div className="detail-item">
                      <strong>Reasoning:</strong> {rec.reasoning}
                    </div>
                  )}
                </div>

                {rec.config && (
                  <div className="rec-config">
                    <strong>Configuration:</strong>
                    <div className="config-grid">
                      {rec.config.x_axis && (
                        <div className="config-item">
                          <span className="config-key">X-Axis:</span>
                          <Badge variant="info" size="small">{rec.config.x_axis}</Badge>
                        </div>
                      )}
                      {rec.config.y_axis && rec.config.y_axis.length > 0 && (
                        <div className="config-item">
                          <span className="config-key">Y-Axis:</span>
                          {rec.config.y_axis.map((col, idx) => (
                            <Badge key={idx} variant="info" size="small">{col}</Badge>
                          ))}
                        </div>
                      )}
                      {rec.config.aggregation && (
                        <div className="config-item">
                          <span className="config-key">Aggregation:</span>
                          <Badge variant="success" size="small">{rec.config.aggregation}</Badge>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="dashboard-navigation">
        <Button 
          variant="secondary" 
          onClick={() => window.history.back()}
        >
          ← Back
        </Button>
        <Button 
          variant="primary" 
          onClick={() => window.location.href = '/insights'}
        >
          View Insights
        </Button>
      </div>
    </div>
  );
}
