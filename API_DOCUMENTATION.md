# EchoBI v2.0 - API Documentation

**Version:** 2.0.0  
**Base URL:** `http://localhost:8000/api/v1`  
**Content-Type:** `application/json`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Upload Endpoints](#upload-endpoints)
3. [Analysis Endpoints](#analysis-endpoints)
4. [Insights Endpoints](#insights-endpoints)
5. [Visualization Endpoints](#visualization-endpoints)
6. [Error Handling](#error-handling)
7. [Status Codes](#status-codes)
8. [Examples](#examples)

---

## Authentication

**Current Version:** No authentication required (development mode)

**Production:** Will require API key authentication
```http
Authorization: Bearer <your-api-key>
```

---

## Upload Endpoints

### 1. Upload Dataset

Upload a CSV or Excel file for analysis.

**Endpoint:** `POST /api/v1/upload`

**Request:**
```http
POST /api/v1/upload
Content-Type: multipart/form-data

file: <binary-file-data>
```

**Response:**
```json
{
  "session_id": "74465fba-dc8e-4009-a057-2f8a00...",
  "status": "uploaded",
  "timestamp": "2026-01-18T10:30:00Z"
}
```

**Parameters:**
- `file` (required): CSV or Excel file (max 100MB)

**Status Codes:**
- `200 OK`: File uploaded successfully
- `400 Bad Request`: Invalid file format or size
- `500 Internal Server Error`: Upload failed

---

## Analysis Endpoints

### 2. Analyze Dataset

Analyze the uploaded dataset and classify it.

**Endpoint:** `POST /api/v1/analyze/{session_id}`

**Request:**
```http
POST /api/v1/analyze/74465fba-dc8e-4009-a057-2f8a00...
Content-Type: application/json
```

**Response:**
```json
{
  "session_id": "74465fba-dc8e-4009-a057-2f8a00...",
  "status": "analyzed",
  "classification": {
    "type": "Time-Series",
    "confidence": 0.90,
    "reasons": [
      "Contains temporal column: date",
      "Regular time intervals detected",
      "Temporal patterns in amount"
    ]
  },
  "quality": {
    "completeness": 0.95,
    "uniqueness": 0.88,
    "validity": 0.92
  },
  "columns": {
    "date": {
      "type": "datetime",
      "missing_count": 0,
      "unique_count": 200
    },
    "amount": {
      "type": "numeric",
      "missing_count": 5,
      "mean": 125.43,
      "std": 45.67
    }
  }
}
```

**Status Codes:**
- `200 OK`: Analysis complete
- `404 Not Found`: Session not found
- `500 Internal Server Error`: Analysis failed

---

### 3. Detect Relationships

Detect correlations and relationships between columns.

**Endpoint:** `GET /api/v1/relationships/{session_id}`

**Request:**
```http
GET /api/v1/relationships/74465fba-dc8e-4009-a057-2f8a00...
```

**Response:**
```json
{
  "relationships": [
    {
      "column1": "amount",
      "column2": "quantity",
      "correlation": 0.85,
      "type": "positive_correlation",
      "strength": "strong"
    },
    {
      "column1": "date",
      "column2": "amount",
      "relationship_type": "temporal_trend",
      "trend": "increasing"
    }
  ],
  "total_relationships": 2
}
```

**Status Codes:**
- `200 OK`: Relationships detected
- `404 Not Found`: Session not found

---

## Insights Endpoints

### 4. Generate Insights

Generate statistical and AI-powered insights from the data.

**Endpoint:** `GET /api/v1/insights`

**Query Parameters:**
- `session_id` (required): Session identifier
- `use_ai` (optional): Use AI insights (true/false, default: false)

**Request:**
```http
GET /api/v1/insights?session_id=74465fba-dc8e-4009-a057-2f8a00...&use_ai=true
```

**Response:**
```json
{
  "insights": [
    {
      "id": "insight-1",
      "category": "trend",
      "severity": "high",
      "title": "Strong Upward Trend in Revenue",
      "description": "Revenue shows a consistent upward trend over the past 6 months with 15% month-over-month growth.",
      "confidence": 0.92,
      "evidence": {
        "mean": 125430.50,
        "trend_slope": 15.3,
        "r_squared": 0.89,
        "p_value": 0.001
      },
      "actions": [
        "Investigate factors driving growth",
        "Forecast future revenue",
        "Allocate resources accordingly"
      ]
    },
    {
      "id": "insight-2",
      "category": "anomaly",
      "severity": "medium",
      "title": "Outliers Detected in Transaction Amounts",
      "description": "5 transactions exceed 3 standard deviations from the mean, potentially indicating fraud or data errors.",
      "confidence": 0.78,
      "evidence": {
        "outlier_count": 5,
        "threshold": 450.50,
        "max_value": 850.00
      },
      "actions": [
        "Review flagged transactions",
        "Verify data quality"
      ]
    }
  ],
  "recommendations": [
    {
      "id": "rec-1",
      "title": "Create Time-Series Visualization",
      "description": "Visualize revenue trends with a line chart over time.",
      "priority": "high",
      "chart_type": "line"
    }
  ],
  "summary": {
    "total_insights": 2,
    "high_severity": 1,
    "medium_severity": 1,
    "low_severity": 0,
    "total_recommendations": 1
  }
}
```

**Status Codes:**
- `200 OK`: Insights generated
- `404 Not Found`: Session not found
- `500 Internal Server Error`: Insight generation failed

---

## Visualization Endpoints

### 5. Get Visualization Recommendations

Get smart chart recommendations based on data characteristics.

**Endpoint:** `GET /api/v1/visualizations/recommendations`

**Query Parameters:**
- `session_id` (required): Session identifier

**Request:**
```http
GET /api/v1/visualizations/recommendations?session_id=74465fba-dc8e-4009-a057-2f8a00...
```

**Response:**
```json
{
  "recommendations": [
    {
      "chart_id": "chart-1",
      "chart_type": "line",
      "priority": "high",
      "title": "Revenue Over Time",
      "description": "Track revenue trends across months",
      "config": {
        "x_axis": "date",
        "y_axis": "amount",
        "aggregation": "sum",
        "time_interval": "month"
      },
      "reasoning": "Time-series data detected with temporal patterns",
      "suitability_score": 0.95
    },
    {
      "chart_id": "chart-2",
      "chart_type": "bar",
      "priority": "high",
      "title": "Revenue by Category",
      "description": "Compare revenue across different categories",
      "config": {
        "x_axis": "category",
        "y_axis": "amount",
        "aggregation": "sum",
        "sort": "desc"
      },
      "reasoning": "Categorical dimension suitable for comparison",
      "suitability_score": 0.88
    }
  ],
  "summary": {
    "total_recommendations": 24,
    "high_priority": 9,
    "medium_priority": 10,
    "low_priority": 5,
    "chart_types": ["line", "bar", "scatter", "pie", "area", "box", "histogram", "heatmap", "indicator", "table"]
  }
}
```

**Status Codes:**
- `200 OK`: Recommendations generated
- `404 Not Found`: Session not found

---

### 6. Generate Chart

Generate a Plotly chart specification.

**Endpoint:** `POST /api/v1/visualizations/generate`

**Request:**
```http
POST /api/v1/visualizations/generate
Content-Type: application/json

{
  "session_id": "74465fba-dc8e-4009-a057-2f8a00...",
  "chart_id": "chart-1",
  "chart_type": "line",
  "config": {
    "x_axis": "date",
    "y_axis": "amount",
    "aggregation": "sum",
    "time_interval": "month"
  }
}
```

**Response:**
```json
{
  "chart_id": "chart-1",
  "chart_type": "line",
  "title": "Revenue Over Time",
  "plotly_spec": {
    "data": [
      {
        "type": "scatter",
        "mode": "lines+markers",
        "x": ["2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"],
        "y": [12543, 14235, 15678, 17234, 19567, 21234],
        "name": "Revenue",
        "line": {
          "color": "#3b82f6",
          "width": 2
        },
        "marker": {
          "size": 8,
          "color": "#3b82f6"
        }
      }
    ],
    "layout": {
      "title": {
        "text": "Revenue Over Time",
        "font": {
          "size": 18,
          "family": "Inter, system-ui, sans-serif"
        }
      },
      "xaxis": {
        "title": "Date",
        "showgrid": true,
        "gridcolor": "#e5e7eb"
      },
      "yaxis": {
        "title": "Revenue ($)",
        "showgrid": true,
        "gridcolor": "#e5e7eb"
      },
      "plot_bgcolor": "#ffffff",
      "paper_bgcolor": "#ffffff",
      "margin": {
        "l": 60,
        "r": 40,
        "t": 80,
        "b": 60
      },
      "hovermode": "x unified"
    },
    "config": {
      "displayModeBar": true,
      "displaylogo": false,
      "modeBarButtonsToRemove": ["lasso2d", "select2d"],
      "toImageButtonOptions": {
        "format": "png",
        "filename": "echobi_chart",
        "height": 600,
        "width": 1000
      }
    }
  }
}
```

**Status Codes:**
- `200 OK`: Chart generated
- `400 Bad Request`: Invalid chart configuration
- `404 Not Found`: Session not found
- `500 Internal Server Error`: Chart generation failed

---

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-01-18T10:30:00Z"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `SESSION_NOT_FOUND` | Session ID not found or expired |
| `INVALID_FILE_FORMAT` | Unsupported file format |
| `FILE_TOO_LARGE` | File exceeds 100MB limit |
| `ANALYSIS_FAILED` | Dataset analysis failed |
| `INSIGHT_GENERATION_FAILED` | Could not generate insights |
| `CHART_GENERATION_FAILED` | Could not create chart |
| `INVALID_CONFIGURATION` | Chart configuration invalid |

---

## Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200 OK` | Success | Request completed successfully |
| `201 Created` | Created | New resource created |
| `400 Bad Request` | Client Error | Invalid request parameters |
| `404 Not Found` | Not Found | Resource doesn't exist |
| `500 Internal Server Error` | Server Error | Unexpected server error |
| `503 Service Unavailable` | Unavailable | Service temporarily unavailable |

---

## Examples

### Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Step 1: Upload file
with open("sales_data.csv", "rb") as f:
    response = requests.post(f"{BASE_URL}/upload", files={"file": f})
    session_id = response.json()["session_id"]

# Step 2: Analyze dataset
response = requests.post(f"{BASE_URL}/analyze/{session_id}")
analysis = response.json()
print(f"Dataset Type: {analysis['classification']['type']}")

# Step 3: Get insights
response = requests.get(f"{BASE_URL}/insights", params={
    "session_id": session_id,
    "use_ai": True
})
insights = response.json()
print(f"Total Insights: {insights['summary']['total_insights']}")

# Step 4: Get visualization recommendations
response = requests.get(f"{BASE_URL}/visualizations/recommendations", params={
    "session_id": session_id
})
recommendations = response.json()
print(f"Total Recommendations: {recommendations['summary']['total_recommendations']}")

# Step 5: Generate top 5 charts
for rec in recommendations['recommendations'][:5]:
    response = requests.post(f"{BASE_URL}/visualizations/generate", json={
        "session_id": session_id,
        "chart_id": rec['chart_id'],
        "chart_type": rec['chart_type'],
        "config": rec['config']
    })
    chart = response.json()
    print(f"Generated: {chart['title']}")
```

### JavaScript/Frontend Example

```javascript
import api from './services/api';

// Upload and analyze workflow
async function analyzeData(file) {
  try {
    // Step 1: Upload
    const uploadResponse = await api.uploadFile(file);
    const sessionId = uploadResponse.session_id;
    
    // Step 2: Analyze
    const analysis = await api.analyzeDataset(sessionId);
    console.log('Dataset Type:', analysis.classification.type);
    
    // Step 3: Get insights
    const insights = await api.getInsights(sessionId, true);
    console.log('Total Insights:', insights.summary.total_insights);
    
    // Step 4: Get visualizations
    const viz = await api.getVisualizationRecommendations(sessionId);
    console.log('Recommendations:', viz.summary.total_recommendations);
    
    // Step 5: Generate chart
    const chartRec = viz.recommendations[0];
    const chart = await api.generateChart(
      sessionId,
      chartRec.chart_id,
      chartRec.chart_type,
      chartRec.config
    );
    
    return { sessionId, analysis, insights, viz, chart };
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

---

## Rate Limiting

**Current:** No rate limiting (development)

**Production:** 
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## Versioning

**Current Version:** v1 (api/v1)

**Future Versions:** Will be backward compatible
- v2 will be available at `/api/v2`
- v1 will remain supported for 12 months after v2 release

---

## Support

**Documentation:** See USER_GUIDE.md for usage examples  
**Issues:** Report on GitHub  
**Contact:** support@echobi.com

---

**Last Updated:** January 18, 2026  
**API Version:** 1.0.0  
**EchoBI Version:** 2.0.0
