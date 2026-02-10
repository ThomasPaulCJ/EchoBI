// src/components/PreprocessingDetails.jsx
// Component to display detailed preprocessing statistics and operations
import React, { useState, useEffect } from 'react';
import { Card, Badge, Loader } from './common';
import { getPreprocessingSuggestions } from '../services/api';
import './PreprocessingDetails.css';

// Icons for different operation types
const operationIcons = {
  handle_missing: '🔧',
  remove_duplicates: '🔄',
  normalize_currency: '💰',
  standardize_dates: '📅',
  validate_emails: '📧',
  validate_quantities: '📦',
  standardize_product_ids: '🏷️',
  handle_outliers: '📊',
  type_conversion: '🔀',
  default: '⚙️'
};

// User-friendly operation names
const operationNames = {
  handle_missing: 'Handle Missing Values',
  remove_duplicates: 'Remove Duplicates',
  normalize_currency: 'Normalize Currency',
  standardize_dates: 'Standardize Dates',
  validate_emails: 'Validate Emails',
  validate_quantities: 'Validate Quantities',
  standardize_product_ids: 'Standardize Product IDs',
  handle_outliers: 'Handle Outliers',
  type_conversion: 'Type Conversion'
};

// Simple explanations for each operation
const operationExplanations = {
  handle_missing: 'Empty or null values in your data need attention. We can fill them with appropriate values or remove the rows.',
  remove_duplicates: 'Some rows appear multiple times. Removing duplicates ensures accurate analysis.',
  normalize_currency: 'Currency values need to be in a consistent format for accurate calculations.',
  standardize_dates: 'Date formats vary across your data. Standardizing them ensures proper time-based analysis.',
  validate_emails: 'Email addresses are checked for proper format to ensure data quality.',
  validate_quantities: 'Quantity values are verified to be valid numbers (not negative or unrealistic).',
  standardize_product_ids: 'Product IDs are formatted consistently for proper grouping and analysis.',
  handle_outliers: 'Some values are unusually high or low. These may need review or special handling.',
  type_conversion: 'Converting data to the appropriate type (numbers, dates, etc.) for proper analysis.'
};

const PreprocessingDetails = ({ columnProfiles, qualityReport, sessionId }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedSection, setExpandedSection] = useState('overview');

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!sessionId) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const data = await getPreprocessingSuggestions(sessionId);
        setSuggestions(data.suggestions || []);
      } catch (err) {
        console.error('Failed to fetch preprocessing suggestions:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSuggestions();
  }, [sessionId]);

  // Calculate data quality statistics from column profiles
  const calculateStats = () => {
    if (!columnProfiles || Object.keys(columnProfiles).length === 0) {
      return {
        totalColumns: 0,
        totalRows: 0,
        totalMissing: 0,
        missingPercent: 0,
        columnsWithMissing: [],
        completeColumns: [],
        columnTypes: {}
      };
    }

    const columns = Object.values(columnProfiles);
    const totalColumns = columns.length;
    const totalRows = columns[0]?.total_count || 0;
    
    let totalMissing = 0;
    const columnsWithMissing = [];
    const completeColumns = [];
    const columnTypes = {};

    columns.forEach(col => {
      const missingCount = col.missing_count || 0;
      totalMissing += missingCount;
      
      if (missingCount > 0) {
        columnsWithMissing.push({
          name: col.name,
          missing: missingCount,
          percent: ((col.missing_percent || 0) * 100).toFixed(1)
        });
      } else {
        completeColumns.push(col.name);
      }
      
      const type = col.type || 'unknown';
      columnTypes[type] = (columnTypes[type] || 0) + 1;
    });

    // Sort columns with missing by percentage (highest first)
    columnsWithMissing.sort((a, b) => parseFloat(b.percent) - parseFloat(a.percent));

    const totalCells = totalColumns * totalRows;
    const missingPercent = totalCells > 0 ? ((totalMissing / totalCells) * 100).toFixed(2) : 0;

    return {
      totalColumns,
      totalRows,
      totalMissing,
      missingPercent,
      columnsWithMissing,
      completeColumns,
      columnTypes
    };
  };

  const stats = calculateStats();

  // Group suggestions by operation type
  const groupedSuggestions = suggestions.reduce((acc, suggestion) => {
    const type = suggestion.operation_type || 'other';
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(suggestion);
    return acc;
  }, {});

  // Get quality score color
  const getQualityColor = (score) => {
    if (score >= 0.8) return '#28a745';
    if (score >= 0.6) return '#ffc107';
    if (score >= 0.4) return '#fd7e14';
    return '#dc3545';
  };

  // Get quality label
  const getQualityLabel = (score) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Needs Attention';
  };

  if (loading) {
    return (
      <Card className="preprocessing-details-card loading">
        <Loader size="medium" />
        <p>Loading preprocessing details...</p>
      </Card>
    );
  }

  return (
    <div className="preprocessing-details">
      {/* Section Header */}
      <div className="preprocessing-header">
        <h2>📋 Data Quality & Preprocessing Report</h2>
        <p className="preprocessing-subtitle">
          Understanding what we found and what cleaning steps may be needed
        </p>
      </div>

      {/* Quick Stats Overview */}
      <div className="stats-overview">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <span className="stat-value">{stats.totalRows.toLocaleString()}</span>
            <span className="stat-label">Total Rows</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <span className="stat-value">{stats.totalColumns}</span>
            <span className="stat-label">Total Columns</span>
          </div>
        </div>
        <div className="stat-card missing">
          <div className="stat-icon">❓</div>
          <div className="stat-content">
            <span className="stat-value">{stats.totalMissing.toLocaleString()}</span>
            <span className="stat-label">Missing Values</span>
            <span className="stat-percent">{stats.missingPercent}% of data</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <span className="stat-value">{stats.completeColumns.length}</span>
            <span className="stat-label">Complete Columns</span>
          </div>
        </div>
      </div>

      {/* Quality Score Section */}
      {qualityReport && (
        <Card className="quality-section">
          <h3>🏆 Overall Data Quality Score</h3>
          <div className="quality-score-display">
            <div 
              className="quality-circle"
              style={{ 
                borderColor: getQualityColor(qualityReport.overall),
                background: `conic-gradient(${getQualityColor(qualityReport.overall)} ${qualityReport.overall * 360}deg, #e9ecef 0deg)`
              }}
            >
              <div className="quality-inner">
                <span className="score-value">{Math.round(qualityReport.overall * 100)}%</span>
                <span className="score-label">{getQualityLabel(qualityReport.overall)}</span>
              </div>
            </div>
            
            <div className="quality-breakdown">
              <h4>Quality Breakdown</h4>
              <div className="quality-item">
                <span className="quality-name">📊 Completeness</span>
                <div className="quality-bar">
                  <div 
                    className="quality-fill" 
                    style={{ 
                      width: `${(qualityReport.breakdown?.completeness || 0) * 100}%`,
                      backgroundColor: getQualityColor(qualityReport.breakdown?.completeness || 0)
                    }}
                  />
                </div>
                <span className="quality-value">{Math.round((qualityReport.breakdown?.completeness || 0) * 100)}%</span>
              </div>
              <p className="quality-explain">How much of your data is filled in vs. missing</p>
              
              <div className="quality-item">
                <span className="quality-name">✓ Validity</span>
                <div className="quality-bar">
                  <div 
                    className="quality-fill" 
                    style={{ 
                      width: `${(qualityReport.breakdown?.validity || 0) * 100}%`,
                      backgroundColor: getQualityColor(qualityReport.breakdown?.validity || 0)
                    }}
                  />
                </div>
                <span className="quality-value">{Math.round((qualityReport.breakdown?.validity || 0) * 100)}%</span>
              </div>
              <p className="quality-explain">How well your data matches expected formats</p>
              
              <div className="quality-item">
                <span className="quality-name">🔄 Consistency</span>
                <div className="quality-bar">
                  <div 
                    className="quality-fill" 
                    style={{ 
                      width: `${(qualityReport.breakdown?.consistency || 0) * 100}%`,
                      backgroundColor: getQualityColor(qualityReport.breakdown?.consistency || 0)
                    }}
                  />
                </div>
                <span className="quality-value">{Math.round((qualityReport.breakdown?.consistency || 0) * 100)}%</span>
              </div>
              <p className="quality-explain">How uniform your data formats are</p>
              
              <div className="quality-item">
                <span className="quality-name">🎯 Uniqueness</span>
                <div className="quality-bar">
                  <div 
                    className="quality-fill" 
                    style={{ 
                      width: `${(qualityReport.breakdown?.uniqueness || 0) * 100}%`,
                      backgroundColor: getQualityColor(qualityReport.breakdown?.uniqueness || 0)
                    }}
                  />
                </div>
                <span className="quality-value">{Math.round((qualityReport.breakdown?.uniqueness || 0) * 100)}%</span>
              </div>
              <p className="quality-explain">How much of your data is unique vs. duplicated</p>
            </div>
          </div>
        </Card>
      )}

      {/* Missing Data Details */}
      {stats.columnsWithMissing.length > 0 && (
        <Card className="missing-data-section">
          <h3>
            <span className="section-icon">❓</span>
            Missing Data Analysis
          </h3>
          <p className="section-description">
            These columns have empty values that may need to be filled or the rows removed.
          </p>
          
          <div className="missing-columns-grid">
            {stats.columnsWithMissing.map((col, index) => (
              <div key={index} className={`missing-column-card ${parseFloat(col.percent) > 50 ? 'severe' : parseFloat(col.percent) > 20 ? 'moderate' : 'minor'}`}>
                <div className="missing-column-header">
                  <span className="column-name">{col.name}</span>
                  <Badge variant={parseFloat(col.percent) > 50 ? 'danger' : parseFloat(col.percent) > 20 ? 'warning' : 'info'}>
                    {col.percent}% missing
                  </Badge>
                </div>
                <div className="missing-bar">
                  <div className="missing-fill" style={{ width: `${col.percent}%` }} />
                </div>
                <div className="missing-count">
                  {col.missing.toLocaleString()} out of {stats.totalRows.toLocaleString()} values empty
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Data Types Summary */}
      <Card className="types-section">
        <h3>
          <span className="section-icon">🏷️</span>
          Column Data Types
        </h3>
        <p className="section-description">
          Each column in your data has been identified as one of these types:
        </p>
        
        <div className="types-grid">
          {Object.entries(stats.columnTypes).map(([type, count]) => (
            <div key={type} className="type-card">
              <span className="type-icon">
                {type === 'numeric' ? '🔢' : 
                 type === 'categorical' ? '📂' : 
                 type === 'datetime' ? '📅' : 
                 type === 'boolean' ? '✓' : '📄'}
              </span>
              <span className="type-name">{type.charAt(0).toUpperCase() + type.slice(1)}</span>
              <span className="type-count">{count} column{count !== 1 ? 's' : ''}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Preprocessing Suggestions */}
      {suggestions.length > 0 && (
        <Card className="suggestions-section">
          <h3>
            <span className="section-icon">🛠️</span>
            Recommended Preprocessing Steps
          </h3>
          <p className="section-description">
            Based on our analysis, here are the cleaning operations we recommend for your data:
          </p>
          
          <div className="suggestions-list">
            {Object.entries(groupedSuggestions).map(([type, items]) => (
              <div key={type} className="suggestion-group">
                <div className="suggestion-group-header">
                  <span className="suggestion-icon">{operationIcons[type] || operationIcons.default}</span>
                  <span className="suggestion-title">{operationNames[type] || type}</span>
                  <Badge variant="secondary">{items.length} operation{items.length !== 1 ? 's' : ''}</Badge>
                </div>
                
                <div className="suggestion-explanation">
                  {operationExplanations[type] || 'This operation helps clean and prepare your data for analysis.'}
                </div>
                
                <div className="suggestion-items">
                  {items.map((item, index) => (
                    <div key={index} className="suggestion-item">
                      <span className="suggestion-column">📍 {item.column}</span>
                      <span className="suggestion-description">{item.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Quality Issues and Recommendations */}
      {qualityReport && (qualityReport.issues?.length > 0 || qualityReport.recommendations?.length > 0) && (
        <Card className="issues-section">
          <h3>
            <span className="section-icon">💡</span>
            Issues & Recommendations
          </h3>
          
          {qualityReport.issues?.length > 0 && (
            <div className="issues-list">
              <h4>⚠️ Issues Found</h4>
              <ul>
                {qualityReport.issues.map((issue, index) => (
                  <li key={index} className="issue-item">{issue}</li>
                ))}
              </ul>
            </div>
          )}
          
          {qualityReport.recommendations?.length > 0 && (
            <div className="recommendations-list">
              <h4>✨ Recommendations</h4>
              <ul>
                {qualityReport.recommendations.map((rec, index) => (
                  <li key={index} className="recommendation-item">{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      )}

      {/* No Issues State */}
      {stats.columnsWithMissing.length === 0 && suggestions.length === 0 && (
        <Card className="no-issues-section">
          <div className="no-issues-content">
            <span className="no-issues-icon">🎉</span>
            <h3>Your Data Looks Great!</h3>
            <p>No major preprocessing steps are needed. Your data is clean and ready for analysis.</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default PreprocessingDetails;
