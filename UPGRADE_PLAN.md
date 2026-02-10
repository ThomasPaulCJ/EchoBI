# EchoBI Upgrade Plan v2.0

## 🎯 Project Vision

Transform EchoBI from a basic data upload/visualization tool into an **intelligent, no-code data preprocessing and insights platform** that automatically analyzes, classifies, and processes datasets with zero code intervention while maintaining full transparency and user control.

---

## 📋 Confirmed Requirements

| Requirement | Decision |
|-------------|----------|
| **Dataset Types** | Financial, Sales/Retail, Time-Series, Healthcare (minimum), Generic fallback |
| **Classification Approach** | Hybrid (rule-based first, ML enhancement later) |
| **User Control** | Both modes: Fully automatic AND confirmation mode |
| **Transparency** | Full audit trail with before/after per operation |
| **Timeline** | 4 weeks for full system |
| **Development Order** | Professional UI → Powerful Backend → UI Integration |
| **LLM Strategy** | Both: LLM insights + Statistical fallback when unavailable |
| **User Confirmation** | Always confirm dataset classification before proceeding |

---

## 🏗️ System Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EchoBI v2.0 Pipeline                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐   │
│  │  UPLOAD  │───▶│   ANALYZE    │───▶│   CONFIRM   │───▶│  PREPROCESS  │   │
│  │  Dataset │    │  & Classify  │    │  with User  │    │  (Smart)     │   │
│  └──────────┘    └──────────────┘    └─────────────┘    └──────────────┘   │
│                                                                    │        │
│                                                                    ▼        │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐   │
│  │ DASHBOARD│◀───│  VISUALIZE   │◀───│   INSIGHTS  │◀───│   FEATURES   │   │
│  │  Display │    │  (Smart)     │    │  (AI + Stat)│    │  & Quality   │   │
│  └──────────┘    └──────────────┘    └─────────────┘    └──────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Backend Module Architecture

```
backend/
├── main.py                         # FastAPI entry point & router registration
├── config.py                       # Configuration management
├── requirements.txt                # Dependencies
│
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py              # File upload handling
│   │   ├── analyze.py             # Dataset analysis & classification
│   │   ├── preprocess.py          # Preprocessing operations
│   │   ├── insights.py            # AI & statistical insights
│   │   └── visualize.py           # Chart generation
│   └── schemas/
│       ├── __init__.py
│       ├── dataset.py             # Dataset-related schemas
│       ├── analysis.py            # Analysis result schemas
│       ├── preprocessing.py       # Preprocessing schemas
│       └── insights.py            # Insight schemas
│
├── core/
│   ├── __init__.py
│   ├── dataset_classifier.py      # Dataset type detection (Hybrid)
│   ├── column_profiler.py         # Column-level analysis
│   ├── relationship_detector.py   # Column relationships
│   ├── quality_scorer.py          # Data quality assessment
│   └── feature_analyzer.py        # Feature importance
│
├── preprocessing/
│   ├── __init__.py
│   ├── base.py                    # Base preprocessor interface
│   ├── strategy_selector.py       # Preprocessing strategy selection
│   ├── operations/
│   │   ├── __init__.py
│   │   ├── missing_values.py      # Missing value strategies
│   │   ├── outliers.py            # Outlier detection & handling
│   │   ├── encoding.py            # Categorical encoding
│   │   ├── scaling.py             # Feature scaling
│   │   ├── datetime.py            # DateTime processing
│   │   └── text.py                # Text cleaning
│   └── pipelines/
│       ├── __init__.py
│       ├── financial.py           # Financial dataset pipeline
│       ├── sales.py               # Sales/Retail pipeline
│       ├── timeseries.py          # Time-series pipeline
│       ├── healthcare.py          # Healthcare pipeline
│       └── generic.py             # Generic fallback pipeline
│
├── insights/
│   ├── __init__.py
│   ├── generator.py               # Main insight generator
│   ├── statistical.py             # Statistical insights (fallback)
│   ├── llm_insights.py            # LLM-based insights
│   └── templates/
│       ├── financial.py           # Financial prompts
│       ├── sales.py               # Sales prompts
│       ├── timeseries.py          # Time-series prompts
│       ├── healthcare.py          # Healthcare prompts
│       └── generic.py             # Generic prompts
│
├── visualization/
│   ├── __init__.py
│   ├── recommender.py             # Chart recommendation engine
│   └── generators/
│       ├── __init__.py
│       ├── distribution.py        # Distribution charts
│       ├── correlation.py         # Correlation charts
│       ├── timeseries.py          # Time-series charts
│       └── comparison.py          # Comparison charts
│
├── storage/
│   ├── __init__.py
│   └── session.py                 # Session-based data storage
│
└── utils/
    ├── __init__.py
    ├── validators.py              # Data validators
    ├── statistics.py              # Statistical utilities
    └── audit.py                   # Audit trail management
```

### Frontend Structure

```
frontend/echo-bi/src/
├── main.jsx
├── App.jsx
├── App.css
├── index.css
│
├── components/
│   ├── layout/
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   ├── Footer.jsx
│   │   └── MainLayout.jsx
│   │
│   ├── upload/
│   │   ├── UploadZone.jsx         # Drag & drop upload
│   │   ├── FileInfo.jsx           # File metadata display
│   │   └── UploadProgress.jsx     # Upload progress indicator
│   │
│   ├── analysis/
│   │   ├── DatasetClassification.jsx    # Classification result & confirmation
│   │   ├── ColumnProfile.jsx            # Column-level details
│   │   ├── QualityScore.jsx             # Data quality metrics
│   │   └── RelationshipView.jsx         # Column relationships
│   │
│   ├── preprocessing/
│   │   ├── PreprocessingWizard.jsx      # Step-by-step wizard
│   │   ├── OperationCard.jsx            # Individual operation display
│   │   ├── BeforeAfterView.jsx          # Before/after comparison
│   │   ├── AuditTrail.jsx               # Full operation history
│   │   └── PreprocessingConfirm.jsx     # User confirmation modal
│   │
│   ├── insights/
│   │   ├── InsightCard.jsx              # Individual insight display
│   │   ├── StatisticalSummary.jsx       # Statistical overview
│   │   ├── AIInsights.jsx               # LLM-generated insights
│   │   └── Recommendations.jsx          # Action recommendations
│   │
│   ├── visualization/
│   │   ├── ChartContainer.jsx           # Chart wrapper
│   │   ├── ChartSelector.jsx            # Chart type selection
│   │   ├── InteractiveChart.jsx         # Plotly chart component
│   │   └── ChartExport.jsx              # Export functionality
│   │
│   ├── dashboard/
│   │   ├── Dashboard.jsx                # Main dashboard view
│   │   ├── MetricCard.jsx               # KPI metric display
│   │   └── SummaryPanel.jsx             # Dataset summary
│   │
│   └── common/
│       ├── Button.jsx
│       ├── Card.jsx
│       ├── Modal.jsx
│       ├── Loader.jsx
│       ├── ProgressBar.jsx
│       ├── Tooltip.jsx
│       ├── Badge.jsx
│       └── Table.jsx
│
├── pages/
│   ├── HomePage.jsx
│   ├── UploadPage.jsx
│   ├── AnalysisPage.jsx
│   ├── PreprocessingPage.jsx
│   ├── InsightsPage.jsx
│   └── DashboardPage.jsx
│
├── services/
│   ├── api.js                     # API service layer
│   ├── upload.js                  # Upload-specific API
│   ├── analysis.js                # Analysis API
│   ├── preprocessing.js           # Preprocessing API
│   └── insights.js                # Insights API
│
├── hooks/
│   ├── useDataset.js              # Dataset state management
│   ├── useAnalysis.js             # Analysis state
│   ├── usePreprocessing.js        # Preprocessing state
│   └── useInsights.js             # Insights state
│
├── context/
│   ├── DatasetContext.jsx         # Global dataset state
│   └── UIContext.jsx              # UI state (theme, etc.)
│
├── utils/
│   ├── formatters.js              # Data formatters
│   ├── validators.js              # Client-side validation
│   └── constants.js               # App constants
│
└── styles/
    ├── variables.css              # CSS variables
    ├── components/                # Component-specific styles
    └── pages/                     # Page-specific styles
```

---

## 📅 4-Week Development Schedule

### Week 1: Professional Frontend Foundation

**Days 1-2: Design System & Layout**
- [ ] Create comprehensive CSS design system (colors, typography, spacing, shadows)
- [ ] Build reusable component library (Button, Card, Modal, Table, Badge, etc.)
- [ ] Implement responsive MainLayout with Header, Sidebar, Footer
- [ ] Set up routing structure for all pages

**Days 3-4: Upload & File Handling UI**
- [ ] Build drag-and-drop UploadZone component
- [ ] Create upload progress indicator with animations
- [ ] Design file information display card
- [ ] Implement upload error handling UI

**Days 5-7: Analysis & Classification UI**
- [ ] Design DatasetClassification confirmation modal
- [ ] Build ColumnProfile component with expandable details
- [ ] Create QualityScore visualization (gauges, progress bars)
- [ ] Implement RelationshipView for column correlations
- [ ] Add user confirmation flow for classification

---

### Week 2: Backend Intelligence Core

**Days 1-2: Dataset Analysis Engine**
- [ ] Implement ColumnProfiler (type detection, statistics, distributions)
- [ ] Build DatasetClassifier (rule-based detection for Financial, Sales, Time-Series, Healthcare)
- [ ] Create QualityScorer (completeness, validity, consistency metrics)
- [ ] Implement confidence scoring for classifications

**Days 3-4: Relationship & Feature Analysis**
- [ ] Build RelationshipDetector (correlations, key detection)
- [ ] Implement FeatureAnalyzer (importance scoring)
- [ ] Create column semantic type detection (currency, date, ID, etc.)
- [ ] Add hierarchy detection logic

**Days 5-7: Preprocessing Engine**
- [ ] Design preprocessing operation interfaces
- [ ] Implement missing value strategies (mean, median, mode, forward-fill, domain-specific)
- [ ] Build outlier detection (IQR, Z-score, domain-specific thresholds)
- [ ] Create encoding operations (one-hot, label, ordinal)
- [ ] Implement scaling operations (standard, min-max, robust)
- [ ] Build audit trail system for all operations

---

### Week 3: Smart Preprocessing Pipelines & Insights

**Days 1-3: Domain-Specific Pipelines**
- [ ] Implement Financial preprocessing pipeline
  - Currency normalization
  - Financial ratio calculations
  - Fraud pattern detection
  - Time-series decomposition for financial data
- [ ] Implement Sales/Retail preprocessing pipeline
  - Seasonality handling
  - Customer segmentation prep
  - RFM score preparation
  - Inventory normalization
- [ ] Implement Time-Series preprocessing pipeline
  - Datetime parsing and validation
  - Resampling operations
  - Lag feature generation
  - Rolling statistics
- [ ] Implement Healthcare preprocessing pipeline
  - Medical code validation
  - Age/date validation
  - Missing value imputation (medical context)
- [ ] Implement Generic fallback pipeline

**Days 4-5: Insight Generation**
- [ ] Build statistical insight generator (fallback mode)
- [ ] Implement LLM insight generator with domain-specific prompts
- [ ] Create insight templates for each dataset type
- [ ] Build anomaly detection and reporting
- [ ] Implement recommendation engine

**Days 6-7: Visualization Intelligence**
- [ ] Build chart recommendation engine
- [ ] Implement distribution chart generators
- [ ] Create correlation visualization
- [ ] Build time-series specific charts
- [ ] Add comparison chart generators

---

### Week 4: Integration, Polish & Testing

**Days 1-2: Frontend-Backend Integration**
- [ ] Connect all frontend components to backend APIs
- [ ] Implement proper error handling and loading states
- [ ] Build preprocessing wizard with step-by-step flow
- [ ] Create before/after comparison views
- [ ] Implement audit trail display

**Days 3-4: User Experience Polish**
- [ ] Add animations and transitions
- [ ] Implement tooltips and help text
- [ ] Create onboarding flow
- [ ] Add keyboard shortcuts
- [ ] Implement dark/light mode toggle
- [ ] Mobile responsiveness testing

**Days 5-6: Testing & Validation**
- [ ] Test with sample Financial datasets
- [ ] Test with sample Sales datasets
- [ ] Test with sample Time-Series datasets
- [ ] Test with sample Healthcare datasets
- [ ] Edge case testing (empty files, huge files, malformed data)
- [ ] Performance optimization

**Day 7: Documentation & Deployment Prep**
- [ ] Update all documentation
- [ ] Create user guide
- [ ] Prepare deployment scripts
- [ ] Final bug fixes

---

## 🔧 Technical Specifications

### Dataset Type Classification Rules

#### Financial Dataset Detection
```python
FINANCIAL_INDICATORS = {
    "column_patterns": [
        r"(?i)(price|cost|revenue|profit|margin|balance|debit|credit)",
        r"(?i)(amount|total|subtotal|tax|fee|charge|payment)",
        r"(?i)(stock|share|dividend|interest|rate|yield)",
        r"(?i)(account|invoice|transaction|transfer)"
    ],
    "value_patterns": [
        r"^\$[\d,]+\.?\d*$",  # Currency format
        r"^[\d,]+\.\d{2}$"   # Decimal money format
    ],
    "required_confidence": 0.7
}
```

#### Sales/Retail Dataset Detection
```python
SALES_INDICATORS = {
    "column_patterns": [
        r"(?i)(product|item|sku|quantity|qty|order)",
        r"(?i)(customer|buyer|client|store|region)",
        r"(?i)(sales|revenue|discount|promotion)",
        r"(?i)(category|brand|supplier|vendor)"
    ],
    "structure_patterns": {
        "has_product_id": True,
        "has_quantity": True,
        "has_price": True
    },
    "required_confidence": 0.7
}
```

#### Time-Series Dataset Detection
```python
TIMESERIES_INDICATORS = {
    "column_patterns": [
        r"(?i)(date|time|timestamp|datetime|period)",
        r"(?i)(year|month|day|hour|minute|second)",
        r"(?i)(quarter|week|fiscal)"
    ],
    "structure_patterns": {
        "has_datetime_index": True,
        "sorted_by_time": True,
        "regular_intervals": True
    },
    "required_confidence": 0.6
}
```

#### Healthcare Dataset Detection
```python
HEALTHCARE_INDICATORS = {
    "column_patterns": [
        r"(?i)(patient|diagnosis|treatment|prescription)",
        r"(?i)(icd|cpt|ndc|procedure|symptom)",
        r"(?i)(blood|pressure|heart|rate|bmi|weight|height)",
        r"(?i)(hospital|clinic|physician|nurse|doctor)"
    ],
    "value_patterns": [
        r"^[A-Z]\d{2}\.?\d*$",  # ICD codes
        r"^\d{5}$"              # CPT codes
    ],
    "required_confidence": 0.7
}
```

### Preprocessing Operation Registry

| Operation | Applicable Types | Parameters |
|-----------|------------------|------------|
| `drop_nulls` | All | threshold (%) |
| `impute_mean` | Numeric | column_list |
| `impute_median` | Numeric | column_list |
| `impute_mode` | Categorical | column_list |
| `impute_forward_fill` | Time-Series | column_list |
| `impute_domain_specific` | Healthcare, Financial | strategy_map |
| `remove_outliers_iqr` | Numeric | multiplier (default 1.5) |
| `remove_outliers_zscore` | Numeric | threshold (default 3) |
| `cap_outliers` | Numeric | lower_percentile, upper_percentile |
| `encode_onehot` | Categorical | column_list |
| `encode_label` | Categorical | column_list |
| `encode_ordinal` | Ordinal | column_list, order_map |
| `scale_standard` | Numeric | column_list |
| `scale_minmax` | Numeric | column_list |
| `scale_robust` | Numeric | column_list |
| `parse_datetime` | DateTime | column_list, format |
| `extract_datetime_features` | DateTime | column_list, features |
| `generate_lag_features` | Time-Series | column_list, lags |
| `calculate_rolling_stats` | Time-Series | column_list, windows, stats |
| `normalize_currency` | Financial | column_list, target_currency |
| `calculate_ratios` | Financial | ratio_definitions |

### API Endpoints Specification

#### Upload & Analysis
```
POST /api/v1/upload
  Request: multipart/form-data (file)
  Response: {
    session_id: string,
    filename: string,
    file_size: number,
    status: "uploaded"
  }

POST /api/v1/analyze/{session_id}
  Response: {
    classification: {
      type: "financial" | "sales" | "timeseries" | "healthcare" | "generic",
      confidence: number,
      indicators_found: string[],
      requires_confirmation: boolean
    },
    columns: [{
      name: string,
      dtype: string,
      semantic_type: string,
      null_percentage: number,
      unique_count: number,
      sample_values: any[],
      statistics: {...}
    }],
    quality_score: {
      overall: number,
      completeness: number,
      validity: number,
      consistency: number
    },
    relationships: [{
      column1: string,
      column2: string,
      correlation: number,
      relationship_type: string
    }],
    row_count: number,
    column_count: number
  }

POST /api/v1/confirm-classification/{session_id}
  Request: { confirmed_type: string }
  Response: { status: "confirmed", preprocessing_suggestions: [...] }
```

#### Preprocessing
```
GET /api/v1/preprocessing/suggestions/{session_id}
  Response: {
    recommended_pipeline: string[],
    operations: [{
      id: string,
      name: string,
      description: string,
      affected_columns: string[],
      estimated_impact: {...}
    }]
  }

POST /api/v1/preprocess/{session_id}
  Request: {
    mode: "automatic" | "confirmation",
    operations: string[] | null  // null for automatic
  }
  Response: {
    status: "completed" | "pending_confirmation",
    audit_trail: [{
      operation: string,
      timestamp: string,
      before_stats: {...},
      after_stats: {...},
      rows_affected: number,
      columns_affected: string[]
    }],
    before_summary: {...},
    after_summary: {...}
  }

POST /api/v1/preprocess/confirm/{session_id}
  Request: { approved: boolean }
  Response: { status: "applied" | "reverted" }
```

#### Insights & Visualization
```
GET /api/v1/insights/{session_id}
  Query: { mode: "statistical" | "ai" | "both" }
  Response: {
    statistical_insights: [{
      type: string,
      title: string,
      description: string,
      data: {...}
    }],
    ai_insights: string | null,
    recommendations: string[],
    anomalies: [{
      column: string,
      type: string,
      description: string,
      severity: "low" | "medium" | "high"
    }]
  }

GET /api/v1/visualizations/{session_id}
  Response: {
    recommended_charts: [{
      type: string,
      title: string,
      description: string,
      columns: string[],
      priority: number
    }]
  }

POST /api/v1/visualizations/{session_id}/generate
  Request: { chart_type: string, columns: string[], options: {...} }
  Response: { plotly_json: string }
```

---

## ⚠️ Risk Mitigation Strategies

### Dataset Misclassification
- **Mitigation**: Always require user confirmation before proceeding
- **UI**: Clear display of classification confidence and detected indicators
- **Fallback**: Generic pipeline with safe operations if uncertain

### Preprocessing Side Effects
- **Mitigation**: Full audit trail with before/after stats
- **UI**: Confirmation mode by default, show impact preview
- **Recovery**: Keep original data, allow revert operations

### Large Dataset Performance
- **Mitigation**: Sampling for initial analysis (max 10,000 rows)
- **UI**: Progress indicators for long operations
- **Backend**: Chunked processing for large files

### LLM Unavailability
- **Mitigation**: Statistical insights fallback always available
- **UI**: Clear indicator of insight source (AI vs Statistical)
- **Validation**: Never show LLM-generated numbers without verification

### Domain Knowledge Gaps
- **Mitigation**: Extensible preprocessing rules architecture
- **UI**: Allow user to add custom preprocessing steps
- **Future**: Plugin system for domain experts

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Dataset Classification Accuracy | > 85% |
| User Confirmation Rate | > 95% (users should feel confident) |
| Preprocessing Quality (measured by downstream task improvement) | > 20% improvement |
| Insight Relevance Score | > 4/5 user rating |
| System Uptime | > 99% |
| Average Processing Time (1MB dataset) | < 10 seconds |
| UI Responsiveness | < 200ms for all interactions |

---

## 🔄 Future Enhancements (Post v2.0)

1. **ML-based Classification**: Train models on labeled datasets for better accuracy
2. **Custom Pipeline Builder**: Visual drag-and-drop preprocessing pipeline creation
3. **Collaboration Features**: Share datasets and insights with team
4. **Scheduled Processing**: Automated preprocessing for recurring data sources
5. **API Integration**: Connect to databases, APIs, cloud storage
6. **Export Options**: Export to various formats, BI tools, notebooks
7. **Version Control**: Track dataset versions and preprocessing history
8. **Anomaly Alerting**: Real-time alerts for data quality issues

---

## 📝 Notes

- This plan assumes dedicated development time
- Timeline is aggressive; adjust based on actual velocity
- Prioritize core functionality over polish in early iterations
- User testing should happen throughout, not just at the end
- Keep instructions file updated with architectural changes

---

**Plan Created**: January 16, 2026  
**Plan Version**: 1.0  
**Status**: CONFIRMED - Ready for Implementation

---

## ✅ Approval Checklist

- [x] Dataset Types: Financial, Sales, Time-Series, Healthcare, Generic
- [x] User Confirmation: Required for classification
- [x] Hybrid Approach: Rules first, ML enhancement later
- [x] Both Modes: Automatic + Confirmation
- [x] Full Audit Trail: Before/after per operation
- [x] Timeline: 4 weeks
- [x] Development Order: UI → Backend → Integration
- [x] LLM Strategy: Both (AI + Statistical fallback)
