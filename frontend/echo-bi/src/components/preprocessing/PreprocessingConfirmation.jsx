// src/components/preprocessing/PreprocessingConfirmation.jsx
// Intelligent preprocessing confirmation UI for user review and customization

import React, { useState, useEffect, useMemo } from "react";
import { Card, Button, Badge, Loader } from "../common";
import { getPreprocessingSuggestions, applyPreprocessing } from "../../services/api";
import "./PreprocessingConfirmation.css";

// Operation type metadata for better UX
const OPERATION_META = {
  impute_numeric: {
    icon: "🔢",
    category: "Missing Values",
    severity: "medium",
    impact: "Fills empty cells with calculated values",
    methods: {
      mean: "Average value (good for normally distributed data)",
      median: "Middle value (robust to outliers)",
      mode: "Most common value",
      zero: "Replace with zero"
    }
  },
  impute_categorical: {
    icon: "📝",
    category: "Missing Values",
    severity: "medium",
    impact: "Fills empty text cells",
    methods: {
      mode: "Most frequent value",
      unknown: "Replace with 'Unknown'"
    }
  },
  handle_outliers: {
    icon: "📊",
    category: "Outliers",
    severity: "high",
    impact: "Caps extreme values to reasonable range",
    methods: {
      iqr: "IQR method (recommended for most cases)",
      zscore: "Z-score method (good for normal distributions)"
    }
  },
  standardize: {
    icon: "📏",
    category: "Normalization",
    severity: "low",
    impact: "Scales values for ML models",
    methods: {
      zscore: "Z-score (mean=0, std=1)",
      minmax: "Min-Max (0 to 1 range)"
    }
  },
  encode_binary: {
    icon: "🔄",
    category: "Encoding",
    severity: "low",
    impact: "Converts yes/no to 0/1"
  },
  encode_onehot: {
    icon: "📋",
    category: "Encoding",
    severity: "low",
    impact: "Creates separate column for each category"
  },
  encode_label: {
    icon: "🏷️",
    category: "Encoding",
    severity: "low",
    impact: "Assigns number to each category"
  },
  remove_duplicates: {
    icon: "♻️",
    category: "Cleaning",
    severity: "medium",
    impact: "Removes duplicate rows"
  },
  drop_column: {
    icon: "🗑️",
    category: "Cleaning",
    severity: "high",
    impact: "Permanently removes column"
  },
  normalize_currency: {
    icon: "💵",
    category: "Financial",
    severity: "low",
    impact: "Standardizes currency format"
  },
  validate_transaction_dates: {
    icon: "📅",
    category: "Financial",
    severity: "medium",
    impact: "Validates and cleans date values"
  },
  handle_negative_amounts: {
    icon: "➖",
    category: "Financial",
    severity: "medium",
    impact: "Handles negative values in amount fields"
  }
};

// Grouping for operations
const CATEGORY_ORDER = ["Missing Values", "Outliers", "Cleaning", "Normalization", "Encoding", "Financial"];

export default function PreprocessingConfirmation({
  sessionId,
  datasetType,
  columns,
  quality,
  onComplete,
  onSkip
}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [selectedOps, setSelectedOps] = useState(new Set());
  const [expandedCategories, setExpandedCategories] = useState(new Set(["Missing Values", "Outliers"]));
  const [applying, setApplying] = useState(false);
  const [applyProgress, setApplyProgress] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);

  // Load preprocessing suggestions
  useEffect(() => {
    async function loadSuggestions() {
      try {
        setLoading(true);
        setError(null);
        const response = await getPreprocessingSuggestions(sessionId);
        setSuggestions(response.suggestions || []);
        
        // Pre-select recommended operations based on data quality
        const recommended = new Set();
        response.suggestions?.forEach(op => {
          // Auto-select missing value handling and critical issues
          if (op.operation_type === "impute_numeric" || op.operation_type === "impute_categorical") {
            recommended.add(op.operation_id);
          }
          // Auto-select outlier handling for severe outliers
          if (op.operation_type === "handle_outliers") {
            recommended.add(op.operation_id);
          }
        });
        setSelectedOps(recommended);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    
    if (sessionId) {
      loadSuggestions();
    }
  }, [sessionId]);

  // Group operations by category
  const groupedOperations = useMemo(() => {
    const groups = {};
    
    suggestions.forEach(op => {
      const meta = OPERATION_META[op.operation_type] || { 
        icon: "⚙️", 
        category: "Other", 
        severity: "low",
        impact: "Processes data"
      };
      
      const category = meta.category;
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push({ ...op, meta });
    });
    
    // Sort by category order
    const sortedGroups = {};
    CATEGORY_ORDER.forEach(cat => {
      if (groups[cat]) {
        sortedGroups[cat] = groups[cat];
      }
    });
    
    // Add any remaining categories
    Object.keys(groups).forEach(cat => {
      if (!sortedGroups[cat]) {
        sortedGroups[cat] = groups[cat];
      }
    });
    
    return sortedGroups;
  }, [suggestions]);

  // Calculate stats
  const stats = useMemo(() => {
    const total = suggestions.length;
    const selected = selectedOps.size;
    const byCategory = {};
    
    Object.entries(groupedOperations).forEach(([cat, ops]) => {
      const catSelected = ops.filter(op => selectedOps.has(op.operation_id)).length;
      byCategory[cat] = { total: ops.length, selected: catSelected };
    });
    
    return { total, selected, byCategory };
  }, [suggestions, selectedOps, groupedOperations]);

  // Toggle operation selection
  const toggleOperation = (opId) => {
    const newSelected = new Set(selectedOps);
    if (newSelected.has(opId)) {
      newSelected.delete(opId);
    } else {
      newSelected.add(opId);
    }
    setSelectedOps(newSelected);
  };

  // Toggle all in category
  const toggleCategory = (category) => {
    const categoryOps = groupedOperations[category] || [];
    const allSelected = categoryOps.every(op => selectedOps.has(op.operation_id));
    
    const newSelected = new Set(selectedOps);
    categoryOps.forEach(op => {
      if (allSelected) {
        newSelected.delete(op.operation_id);
      } else {
        newSelected.add(op.operation_id);
      }
    });
    setSelectedOps(newSelected);
  };

  // Toggle category expansion
  const toggleExpand = (category) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  // Select all / none
  const selectAll = () => {
    setSelectedOps(new Set(suggestions.map(op => op.operation_id)));
  };

  const selectNone = () => {
    setSelectedOps(new Set());
  };

  const selectRecommended = () => {
    const recommended = new Set();
    suggestions.forEach(op => {
      if (op.operation_type.includes("impute") || op.operation_type === "handle_outliers") {
        recommended.add(op.operation_id);
      }
    });
    setSelectedOps(recommended);
  };

  // Apply preprocessing
  const handleApply = async () => {
    if (selectedOps.size === 0) {
      // No operations selected, skip preprocessing
      onComplete?.({ skipped: true, operations: [] });
      return;
    }

    try {
      setApplying(true);
      setApplyProgress(10);

      const operationIds = Array.from(selectedOps);
      
      // Simulate progress
      const progressInterval = setInterval(() => {
        setApplyProgress(prev => Math.min(prev + 15, 85));
      }, 300);

      const result = await applyPreprocessing(sessionId, operationIds);
      
      clearInterval(progressInterval);
      setApplyProgress(100);

      // Brief delay to show completion
      await new Promise(resolve => setTimeout(resolve, 500));

      onComplete?.({
        skipped: false,
        operations: operationIds,
        auditTrail: result.audit_trail,
        beforeShape: result.before_shape,
        afterShape: result.after_shape
      });
    } catch (err) {
      setError(err.message);
      setApplying(false);
      setApplyProgress(0);
    }
  };

  // Get severity badge variant
  const getSeverityVariant = (severity) => {
    switch (severity) {
      case "high": return "warning";
      case "medium": return "info";
      case "low": return "success";
      default: return "default";
    }
  };

  if (loading) {
    return (
      <Card title="⚙️ Preprocessing Engine" className="preprocessing-confirmation-card">
        <div className="preprocessing-loading">
          <Loader size="large" />
          <p>Analyzing your dataset for preprocessing opportunities...</p>
          <span className="loading-subtext">Examining {Object.keys(columns || {}).length} columns</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="⚙️ Preprocessing Engine" className="preprocessing-confirmation-card">
        <div className="preprocessing-error">
          <span className="error-icon">❌</span>
          <p>Failed to generate preprocessing suggestions</p>
          <span className="error-detail">{error}</span>
          <Button variant="primary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  if (suggestions.length === 0) {
    return (
      <Card title="⚙️ Preprocessing Engine" className="preprocessing-confirmation-card">
        <div className="preprocessing-empty">
          <span className="empty-icon">✨</span>
          <h3>Your data looks great!</h3>
          <p>No preprocessing operations are needed. Your dataset is ready for analysis.</p>
          <div className="empty-actions">
            <Button variant="primary" onClick={() => onComplete?.({ skipped: true, operations: [] })}>
              Continue to Analysis →
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card title="⚙️ Smart Preprocessing" className="preprocessing-confirmation-card">
      {/* Header Stats */}
      <div className="preprocessing-header">
        <div className="preprocessing-intro">
          <p>
            Based on your <strong>{datasetType}</strong> dataset analysis, we've identified 
            <strong> {suggestions.length} preprocessing operations</strong> that could improve your data quality.
          </p>
          <p className="intro-subtext">
            Review and select the operations you want to apply. Each operation is reversible.
          </p>
        </div>

        <div className="preprocessing-summary">
          <div className="summary-stat">
            <span className="stat-value">{stats.selected}</span>
            <span className="stat-label">Selected</span>
          </div>
          <div className="summary-divider">/</div>
          <div className="summary-stat">
            <span className="stat-value">{stats.total}</span>
            <span className="stat-label">Available</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <Button variant="ghost" size="small" onClick={selectRecommended}>
          ⭐ Recommended
        </Button>
        <Button variant="ghost" size="small" onClick={selectAll}>
          ✓ Select All
        </Button>
        <Button variant="ghost" size="small" onClick={selectNone}>
          ✗ Clear All
        </Button>
        <Button 
          variant="ghost" 
          size="small" 
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={showAdvanced ? 'active' : ''}
        >
          ⚙️ {showAdvanced ? 'Simple View' : 'Advanced'}
        </Button>
      </div>

      {/* Operations by Category */}
      <div className="operations-container">
        {Object.entries(groupedOperations).map(([category, operations]) => {
          const isExpanded = expandedCategories.has(category);
          const categoryStats = stats.byCategory[category] || { total: 0, selected: 0 };
          const allSelected = categoryStats.selected === categoryStats.total;
          const someSelected = categoryStats.selected > 0 && categoryStats.selected < categoryStats.total;

          return (
            <div key={category} className={`operation-category ${isExpanded ? 'expanded' : ''}`}>
              <div 
                className="category-header"
                onClick={() => toggleExpand(category)}
              >
                <div className="category-left">
                  <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                  <h4 className="category-title">{category}</h4>
                  <Badge variant="default" size="small">
                    {categoryStats.total}
                  </Badge>
                </div>
                <div className="category-right">
                  <span className="category-selected">
                    {categoryStats.selected} selected
                  </span>
                  <button 
                    className={`category-toggle ${allSelected ? 'all-selected' : ''} ${someSelected ? 'some-selected' : ''}`}
                    onClick={(e) => { e.stopPropagation(); toggleCategory(category); }}
                  >
                    {allSelected ? '✓' : someSelected ? '−' : ''}
                  </button>
                </div>
              </div>

              {isExpanded && (
                <div className="category-operations">
                  {operations.map(op => {
                    const isSelected = selectedOps.has(op.operation_id);
                    
                    return (
                      <div 
                        key={op.operation_id}
                        className={`operation-item ${isSelected ? 'selected' : ''}`}
                        onClick={() => toggleOperation(op.operation_id)}
                      >
                        <div className="operation-checkbox">
                          <span className={`checkbox ${isSelected ? 'checked' : ''}`}>
                            {isSelected ? '✓' : ''}
                          </span>
                        </div>
                        
                        <div className="operation-icon">
                          {op.meta.icon}
                        </div>
                        
                        <div className="operation-content">
                          <div className="operation-header-row">
                            <span className="operation-title">{op.description}</span>
                            <Badge 
                              variant={getSeverityVariant(op.meta.severity)} 
                              size="small"
                            >
                              {op.meta.severity} impact
                            </Badge>
                          </div>
                          
                          <div className="operation-details">
                            {op.column && (
                              <span className="operation-column">
                                Column: <code>{op.column}</code>
                              </span>
                            )}
                            {showAdvanced && (
                              <>
                                <span className="operation-type">
                                  Type: <code>{op.operation_type}</code>
                                </span>
                                {op.parameters && Object.keys(op.parameters).length > 0 && (
                                  <span className="operation-params">
                                    Method: <code>{op.parameters.method || JSON.stringify(op.parameters)}</code>
                                  </span>
                                )}
                              </>
                            )}
                          </div>
                          
                          <p className="operation-impact">{op.meta.impact}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Apply Section */}
      {applying ? (
        <div className="applying-section">
          <div className="apply-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${applyProgress}%` }}
              />
            </div>
            <span className="progress-text">
              Applying {selectedOps.size} operations... {applyProgress}%
            </span>
          </div>
        </div>
      ) : (
        <div className="actions-section">
          <div className="actions-info">
            {selectedOps.size > 0 ? (
              <p>
                <strong>{selectedOps.size} operations</strong> will be applied to your dataset.
                All changes are recorded in an audit trail and can be reviewed later.
              </p>
            ) : (
              <p>
                No operations selected. You can skip preprocessing and proceed with the original data.
              </p>
            )}
          </div>
          
          <div className="actions-buttons">
            <Button 
              variant="primary" 
              size="large"
              onClick={handleApply}
            >
              {selectedOps.size > 0 
                ? `✅ Apply ${selectedOps.size} Operations` 
                : '⏭️ Skip & Continue'}
            </Button>
            
            {selectedOps.size > 0 && (
              <Button 
                variant="secondary"
                onClick={() => onSkip?.()}
              >
                Skip Preprocessing
              </Button>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}
