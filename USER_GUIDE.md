# EchoBI v2.0 - User Guide

**Welcome to EchoBI** - Your intelligent, no-code analytics platform for self-service data exploration, visualization, and insights generation.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Uploading Data](#uploading-data)
3. [Understanding Insights](#understanding-insights)
4. [Creating Visualizations](#creating-visualizations)
5. [Interpreting Results](#interpreting-results)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Safari, Firefox, Edge)
- CSV or Excel file with your data
- No coding knowledge required!

### Accessing EchoBI
1. Open your browser and navigate to `http://localhost:5173`
2. You'll see the EchoBI homepage with the upload interface

---

## Uploading Data

### Step 1: Prepare Your Data

**Supported Formats:**
- CSV (.csv)
- Excel (.xlsx, .xls)

**Data Requirements:**
- Minimum 10 rows recommended
- Column headers in first row
- Clean data (minimal missing values)

**Supported Data Types:**
- **Financial:** Transactions, accounting, revenue
- **Sales/Retail:** Products, customers, orders
- **Time-Series:** Temporal data with dates
- **Healthcare:** Medical records, diagnoses
- **Generic:** Any structured data

### Step 2: Upload Your File

1. Click the **"Choose File"** button or drag-and-drop your file
2. EchoBI will automatically:
   - Analyze your dataset
   - Classify the data type
   - Profile all columns
   - Generate quality scores
3. Review the preview table showing your data
4. Click **"View Insights"** or **"View Visualizations"**

### What Happens Behind the Scenes?

EchoBI performs:
- **Dataset Classification:** Identifies whether your data is financial, sales, time-series, healthcare, or generic
- **Column Profiling:** Analyzes data types, distributions, missing values, outliers
- **Quality Assessment:** Scores data completeness and quality
- **Relationship Detection:** Finds correlations and patterns
- **Preprocessing:** Cleans data with full audit trail

---

## Understanding Insights

### Insights Page Overview

The Insights page displays AI-generated and statistical insights from your data.

### Components

#### 1. Summary Dashboard (Top Cards)
- **Total Insights:** Number of insights generated
- **High Priority:** Critical findings requiring attention
- **Recommendations:** Actionable suggestions
- **Categories:** Types of insights (trend, anomaly, correlation, distribution)

#### 2. Filters
- **Category Filter:** Show insights by type (trends, anomalies, correlations, etc.)
- **Severity Filter:** Filter by priority (high, medium, low)

#### 3. Insight Cards

Each insight card shows:
- **📊 Icon:** Visual indicator of insight type
- **Title:** Clear description of the finding
- **Description:** Detailed explanation
- **Confidence:** How confident EchoBI is in this finding (0-100%)
- **Evidence:** Statistical data supporting the insight
- **Action Items:** Recommended next steps

**Example Insight:**
```
📈 Trend Detected in Sales

Description: "Revenue shows a strong upward trend over the past 6 months with 
15% month-over-month growth."

Confidence: 92%

Evidence:
- Mean: $125,430
- Trend Slope: +15.3%
- R-squared: 0.89

Actions:
✓ Investigate factors driving growth
✓ Forecast future revenue
```

#### 4. Recommendations Section

Shows actionable recommendations such as:
- Best visualizations for your data
- Data quality improvements
- Further analysis suggestions

---

## Creating Visualizations

### Dashboard Page Overview

The Dashboard page helps you create professional charts and visualizations.

### Step 1: Generate Charts

**Option A: Bulk Generation**
- Click **"Generate Top Charts"** to create the 10 most recommended visualizations automatically

**Option B: Individual Generation**
- Browse the "Recommended Visualizations" list
- Click **"Generate Chart"** on any recommendation

### Step 2: Explore Charts

Each generated chart includes:
- **Interactive Plotly Chart:** Zoom, pan, hover for details
- **Chart Controls:** Fullscreen, download PNG
- **Configuration:** View axes, aggregations, filters used

### Step 3: Filter and Organize

Use filters to:
- **Priority:** Show only high/medium/low priority charts
- **Chart Type:** Filter by bar, line, pie, scatter, etc.

### Supported Chart Types

| Chart Type | Best For | Example |
|------------|----------|---------|
| **Bar Chart** | Comparing categories | Sales by product |
| **Line Chart** | Trends over time | Revenue over months |
| **Pie Chart** | Composition/proportions | Market share |
| **Scatter Plot** | Correlations | Price vs. demand |
| **Area Chart** | Cumulative trends | Total customers over time |
| **Box Plot** | Distributions/outliers | Price distribution |
| **Histogram** | Frequency distribution | Age distribution |
| **Heatmap** | Correlations matrix | Feature relationships |
| **Indicator** | Single KPI | Total revenue |
| **Table** | Detailed data view | Top 10 customers |

---

## Interpreting Results

### Understanding Classification

EchoBI automatically classifies your dataset:

**Financial Data:**
- Contains currency, transactions, accounting terms
- Examples: Revenue, expenses, profit

**Sales/Retail Data:**
- Contains products, customers, orders
- Examples: Product sales, customer purchases

**Time-Series Data:**
- Contains temporal patterns, dates
- Examples: Daily metrics, monthly trends

**Healthcare Data:**
- Contains medical terms, diagnoses
- Examples: Patient records, treatment data

**Generic Data:**
- Any structured data not fitting above categories

### Understanding Confidence Scores

- **90-100%:** Very high confidence, trust this insight
- **75-89%:** High confidence, generally reliable
- **60-74%:** Medium confidence, verify with domain knowledge
- **< 60%:** Low confidence, investigate further

### Understanding Evidence

Evidence grids show:
- **Statistical measures:** Mean, median, standard deviation
- **Trend metrics:** Slope, R-squared, correlation
- **Quality metrics:** Missing values, outliers, completeness

---

## Best Practices

### Data Preparation

✅ **Do:**
- Use clear column names (e.g., "Total_Revenue" not "Col1")
- Include date columns in ISO format (YYYY-MM-DD)
- Remove extra header rows
- Keep data in tabular format

❌ **Don't:**
- Upload files with merged cells
- Include summary rows at the bottom
- Use special characters in column names
- Upload completely empty columns

### Using Insights

✅ **Do:**
- Read insight descriptions carefully
- Check confidence scores
- Review evidence data
- Combine AI insights with your domain knowledge

❌ **Don't:**
- Blindly trust low-confidence insights
- Ignore statistical evidence
- Skip verification of critical findings

### Creating Visualizations

✅ **Do:**
- Start with recommended charts
- Use appropriate chart types for your data
- Generate multiple views of the same data
- Download charts for presentations

❌ **Don't:**
- Force inappropriate chart types
- Overcomplicate visualizations
- Ignore chart recommendations

---

## Troubleshooting

### Upload Issues

**Problem:** File won't upload
- **Solution:** Check file format (CSV/Excel only), file size (<100MB), file not corrupted

**Problem:** Preview table looks wrong
- **Solution:** Ensure first row contains headers, check for proper CSV delimiter, verify encoding (UTF-8)

### Insight Generation Issues

**Problem:** No insights generated
- **Solution:** Dataset may be too small (<10 rows), data quality too low, or no clear patterns detected

**Problem:** Insights don't make sense
- **Solution:** Check data quality, verify column types correctly detected, review evidence data

### Visualization Issues

**Problem:** Charts not displaying
- **Solution:** Check browser console for errors, ensure JavaScript enabled, try refreshing page

**Problem:** Wrong chart type recommended
- **Solution:** Data classification may be incorrect, manually select different chart type

### Performance Issues

**Problem:** Slow analysis
- **Solution:** Large datasets (>10,000 rows) take longer, close other browser tabs, check internet connection

**Problem:** Charts load slowly
- **Solution:** Reduce number of charts generated at once, simplify chart configurations

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl/Cmd + U** | Upload new file |
| **Ctrl/Cmd + I** | Navigate to Insights |
| **Ctrl/Cmd + V** | Navigate to Visualizations |
| **Esc** | Close fullscreen chart |

---

## Data Privacy & Security

- **No Cloud Storage:** All data processed locally on your machine
- **Session-Based:** Data discarded after session ends
- **No Data Collection:** EchoBI doesn't collect or store your data
- **Open Source:** Full transparency in data handling

---

## Getting Help

### Documentation
- **Installation Guide:** `DEPLOYMENT_GUIDE.md`
- **API Documentation:** `API_DOCUMENTATION.md`
- **Developer Guide:** `UPGRADE_PLAN.md`

### Support
- **Issues:** Report bugs on GitHub
- **Questions:** Check FAQ in documentation
- **Feature Requests:** Submit via GitHub Issues

---

## Quick Reference

### Workflow Summary
```
1. Upload data → 2. Review preview → 3. View insights → 4. Create visualizations → 5. Download results
```

### Key Terms

- **Dataset Classification:** Automatic identification of data type
- **Column Profiling:** Statistical analysis of each column
- **Insight:** AI-generated finding from your data
- **Recommendation:** Suggested action or visualization
- **Confidence Score:** Reliability measure (0-100%)
- **Evidence:** Statistical data supporting insights
- **Audit Trail:** Record of all data transformations

---

**Need More Help?** Check the full documentation in the `docs/` folder or visit the GitHub repository.

**Happy Analyzing! 📊**
