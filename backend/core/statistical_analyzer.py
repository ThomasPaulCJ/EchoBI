"""
Statistical Analyzer for EchoBI v2.0
Provides statistical analysis and pattern detection as fallback for AI insights.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from scipy import stats


@dataclass
class StatisticalInsight:
    """Data class for statistical insight."""
    insight_id: str
    category: str  # trend, anomaly, correlation, distribution, summary
    title: str
    description: str
    severity: str  # high, medium, low
    confidence: float  # 0-1
    affected_columns: List[str]
    statistical_evidence: Dict[str, Any]
    visualization_hint: Optional[str] = None
    action_items: Optional[List[str]] = None


class StatisticalAnalyzer:
    """
    Analyzes datasets using statistical methods to generate insights.
    
    Provides fallback insights when AI is unavailable or for validation.
    """
    
    def __init__(self, df: pd.DataFrame, column_profiles: Dict[str, Any], dataset_type: str):
        self.df = df
        self.column_profiles = column_profiles
        self.dataset_type = dataset_type
        self.insights: List[StatisticalInsight] = []
        self.numeric_columns = [col for col, profile in column_profiles.items() 
                               if profile.get('type') == 'numeric']
        self.categorical_columns = [col for col, profile in column_profiles.items() 
                                   if profile.get('type') == 'categorical']
        self.datetime_columns = [col for col, profile in column_profiles.items() 
                                if profile.get('type') == 'datetime']
    
    def analyze_all(self) -> List[StatisticalInsight]:
        """Run all statistical analyses and generate insights."""
        self.insights = []
        
        # Run different analysis types
        self._analyze_distributions()
        self._detect_outliers()
        self._analyze_correlations()
        self._detect_trends()
        self._analyze_missing_patterns()
        self._analyze_categorical_balance()
        self._detect_anomalies()
        
        # Domain-specific analyses
        if self.dataset_type == 'Financial':
            self._analyze_financial_patterns()
        elif self.dataset_type == 'Time-Series':
            self._analyze_temporal_patterns()
        elif self.dataset_type == 'Sales':
            self._analyze_sales_patterns()
        
        return self.insights
    
    def _analyze_distributions(self):
        """Analyze distribution characteristics of numeric columns."""
        for col in self.numeric_columns[:5]:  # Limit to top 5
            try:
                data = self.df[col].dropna()
                if len(data) < 10:
                    continue
                
                # Test for normality
                _, p_value = stats.normaltest(data)
                skewness = stats.skew(data)
                kurtosis = stats.kurtosis(data)
                
                if p_value < 0.05:  # Not normal
                    if abs(skewness) > 1:
                        direction = "right" if skewness > 0 else "left"
                        self.insights.append(StatisticalInsight(
                            insight_id=f"dist_{col}_{len(self.insights)}",
                            category="distribution",
                            title=f"{col} shows {direction}-skewed distribution",
                            description=f"The column '{col}' has a skewness of {skewness:.2f}, "
                                      f"indicating a {direction}-skewed distribution. "
                                      f"Consider log transformation or outlier treatment.",
                            severity="medium",
                            confidence=0.85,
                            affected_columns=[col],
                            statistical_evidence={
                                "skewness": float(skewness),
                                "kurtosis": float(kurtosis),
                                "p_value": float(p_value),
                                "test": "normaltest"
                            },
                            visualization_hint="histogram",
                            action_items=[
                                "Consider log transformation for right-skewed data",
                                "Review outliers that may be causing skew",
                                "Use robust statistics (median) instead of mean"
                            ]
                        ))
            except Exception:
                continue
    
    def _detect_outliers(self):
        """Detect outliers using IQR method."""
        outlier_summary = []
        
        for col in self.numeric_columns[:5]:
            try:
                data = self.df[col].dropna()
                if len(data) < 10:
                    continue
                
                q1 = data.quantile(0.25)
                q3 = data.quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = data[(data < lower_bound) | (data > upper_bound)]
                outlier_percent = (len(outliers) / len(data)) * 100
                
                if outlier_percent > 5:  # More than 5% outliers
                    outlier_summary.append({
                        'column': col,
                        'count': len(outliers),
                        'percent': outlier_percent,
                        'lower_bound': lower_bound,
                        'upper_bound': upper_bound
                    })
            except Exception:
                continue
        
        if outlier_summary:
            total_outliers = sum(item['count'] for item in outlier_summary)
            self.insights.append(StatisticalInsight(
                insight_id=f"outliers_{len(self.insights)}",
                category="anomaly",
                title=f"Outliers detected in {len(outlier_summary)} numeric columns",
                description=f"Found {total_outliers} outlier values across "
                          f"{len(outlier_summary)} columns using IQR method. "
                          f"These may represent data entry errors, anomalies, or legitimate extreme values.",
                severity="high" if len(outlier_summary) > 3 else "medium",
                confidence=0.90,
                affected_columns=[item['column'] for item in outlier_summary],
                statistical_evidence={
                    "outlier_details": outlier_summary,
                    "method": "IQR",
                    "total_outliers": total_outliers
                },
                visualization_hint="boxplot",
                action_items=[
                    "Review outliers to determine if they are errors or valid extreme values",
                    "Consider capping outliers at IQR bounds",
                    "Use robust statistics less affected by outliers"
                ]
            ))
    
    def _analyze_correlations(self):
        """Analyze correlations between numeric columns."""
        if len(self.numeric_columns) < 2:
            return
        
        try:
            # Calculate correlation matrix
            corr_matrix = self.df[self.numeric_columns].corr()
            
            # Find strong correlations (|r| > 0.7)
            strong_corrs = []
            for i, col1 in enumerate(self.numeric_columns):
                for j, col2 in enumerate(self.numeric_columns):
                    if i < j:  # Avoid duplicates
                        corr_value = corr_matrix.loc[col1, col2]
                        if abs(corr_value) > 0.7:
                            strong_corrs.append({
                                'col1': col1,
                                'col2': col2,
                                'correlation': corr_value
                            })
            
            if strong_corrs:
                # Sort by absolute correlation
                strong_corrs.sort(key=lambda x: abs(x['correlation']), reverse=True)
                top_corr = strong_corrs[0]
                
                direction = "positive" if top_corr['correlation'] > 0 else "negative"
                self.insights.append(StatisticalInsight(
                    insight_id=f"corr_{len(self.insights)}",
                    category="correlation",
                    title=f"Strong {direction} correlation: {top_corr['col1']} and {top_corr['col2']}",
                    description=f"Detected a strong {direction} correlation (r={top_corr['correlation']:.3f}) "
                              f"between {top_corr['col1']} and {top_corr['col2']}. "
                              f"This suggests these variables move together.",
                    severity="medium",
                    confidence=0.88,
                    affected_columns=[top_corr['col1'], top_corr['col2']],
                    statistical_evidence={
                        "correlation_coefficient": float(top_corr['correlation']),
                        "method": "pearson",
                        "all_strong_correlations": strong_corrs[:5]  # Top 5
                    },
                    visualization_hint="scatter",
                    action_items=[
                        "Consider using one variable as a predictor for the other",
                        "Check for potential multicollinearity in modeling",
                        "Investigate the causal relationship between these variables"
                    ]
                ))
        except Exception:
            pass
    
    def _detect_trends(self):
        """Detect trends in time-series or sequential data."""
        if not self.datetime_columns and not self.numeric_columns:
            return
        
        # If we have datetime column, analyze trends over time
        if self.datetime_columns:
            datetime_col = self.datetime_columns[0]
            try:
                df_sorted = self.df.sort_values(datetime_col)
                
                for numeric_col in self.numeric_columns[:3]:
                    data = df_sorted[numeric_col].dropna()
                    if len(data) < 10:
                        continue
                    
                    # Simple linear trend analysis
                    x = np.arange(len(data))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, data)
                    
                    if p_value < 0.05 and abs(r_value) > 0.5:  # Significant trend
                        trend_direction = "increasing" if slope > 0 else "decreasing"
                        self.insights.append(StatisticalInsight(
                            insight_id=f"trend_{numeric_col}_{len(self.insights)}",
                            category="trend",
                            title=f"{numeric_col} shows {trend_direction} trend over time",
                            description=f"The column '{numeric_col}' exhibits a statistically significant "
                                      f"{trend_direction} trend (R²={r_value**2:.3f}, p<0.05). "
                                      f"The trend slope is {slope:.4f} per time unit.",
                            severity="medium",
                            confidence=0.85,
                            affected_columns=[numeric_col, datetime_col],
                            statistical_evidence={
                                "slope": float(slope),
                                "r_squared": float(r_value ** 2),
                                "p_value": float(p_value),
                                "direction": trend_direction
                            },
                            visualization_hint="line",
                            action_items=[
                                f"Monitor the {trend_direction} trend in {numeric_col}",
                                "Consider forecasting future values based on this trend",
                                "Investigate factors driving this trend"
                            ]
                        ))
            except Exception:
                pass
    
    def _analyze_missing_patterns(self):
        """Analyze patterns in missing data."""
        missing_summary = []
        
        for col, profile in self.column_profiles.items():
            missing_percent = profile.get('missing_percent', 0)
            if missing_percent > 10:  # More than 10% missing
                missing_summary.append({
                    'column': col,
                    'missing_count': int(profile.get('missing_count', 0)),
                    'missing_percent': missing_percent
                })
        
        if missing_summary:
            missing_summary.sort(key=lambda x: x['missing_percent'], reverse=True)
            worst_col = missing_summary[0]
            
            self.insights.append(StatisticalInsight(
                insight_id=f"missing_{len(self.insights)}",
                category="summary",
                title=f"Significant missing data in {len(missing_summary)} columns",
                description=f"Column '{worst_col['column']}' has {worst_col['missing_percent']:.1f}% "
                          f"missing values. Total of {len(missing_summary)} columns have >10% missing data. "
                          f"Consider imputation or column removal.",
                severity="high" if worst_col['missing_percent'] > 50 else "medium",
                confidence=1.0,
                affected_columns=[item['column'] for item in missing_summary],
                statistical_evidence={
                    "missing_details": missing_summary,
                    "total_affected_columns": len(missing_summary)
                },
                visualization_hint="heatmap",
                action_items=[
                    "Review columns with >50% missing - consider dropping",
                    "Apply appropriate imputation strategy (mean, median, mode, forward-fill)",
                    "Investigate why data is missing (MCAR, MAR, MNAR)"
                ]
            ))
    
    def _analyze_categorical_balance(self):
        """Analyze class balance in categorical columns."""
        for col in self.categorical_columns[:5]:
            try:
                value_counts = self.df[col].value_counts()
                if len(value_counts) < 2:
                    continue
                
                # Calculate imbalance ratio - convert to int to avoid boolean array issues
                max_count = int(value_counts.max())
                min_count = int(value_counts.min())
                imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
                
                if imbalance_ratio > 10:  # Highly imbalanced
                    self.insights.append(StatisticalInsight(
                        insight_id=f"balance_{col}_{len(self.insights)}",
                        category="distribution",
                        title=f"Class imbalance detected in {col}",
                        description=f"The column '{col}' shows significant class imbalance "
                                  f"(ratio: {imbalance_ratio:.1f}:1). "
                                  f"Most common value: '{value_counts.index[0]}' "
                                  f"({value_counts.iloc[0]} occurrences).",
                        severity="medium",
                        confidence=0.90,
                        affected_columns=[col],
                        statistical_evidence={
                            "imbalance_ratio": float(imbalance_ratio),
                            "unique_values": len(value_counts),
                            "most_common": str(value_counts.index[0]),
                            "least_common": str(value_counts.index[-1])
                        },
                        visualization_hint="bar",
                        action_items=[
                            "Consider stratified sampling if using for modeling",
                            "Apply class balancing techniques (SMOTE, undersampling)",
                            "Use appropriate metrics (F1, precision-recall) instead of accuracy"
                        ]
                    ))
            except Exception:
                continue
    
    def _detect_anomalies(self):
        """Detect anomalies using Z-score method."""
        for col in self.numeric_columns[:3]:
            try:
                data = self.df[col].dropna()
                if len(data) < 30:
                    continue
                
                z_scores = np.abs(stats.zscore(data))
                anomalies = data[z_scores > 3]
                
                if len(anomalies) > 0:
                    anomaly_percent = (len(anomalies) / len(data)) * 100
                    if anomaly_percent > 1:  # More than 1% anomalies
                        self.insights.append(StatisticalInsight(
                            insight_id=f"anomaly_{col}_{len(self.insights)}",
                            category="anomaly",
                            title=f"Anomalous values detected in {col}",
                            description=f"Found {len(anomalies)} anomalous values ({anomaly_percent:.2f}%) "
                                      f"in '{col}' using Z-score method (|Z| > 3). "
                                      f"These values deviate significantly from the mean.",
                            severity="medium",
                            confidence=0.80,
                            affected_columns=[col],
                            statistical_evidence={
                                "anomaly_count": len(anomalies),
                                "anomaly_percent": float(anomaly_percent),
                                "method": "zscore",
                                "threshold": 3
                            },
                            visualization_hint="scatter",
                            action_items=[
                                "Investigate these anomalies for data quality issues",
                                "Consider removing or flagging anomalous records",
                                "Check if anomalies represent important events"
                            ]
                        ))
            except Exception:
                continue
    
    def _analyze_financial_patterns(self):
        """Domain-specific analysis for financial datasets."""
        # Look for currency columns
        currency_cols = [col for col in self.numeric_columns 
                        if any(keyword in col.lower() for keyword in ['price', 'amount', 'balance', 'cost', 'revenue'])]
        
        if currency_cols:
            for col in currency_cols[:2]:
                try:
                    data = self.df[col].dropna()
                    # Convert to int to avoid numpy boolean subtract errors
                    negative_count = int((data < 0).sum())
                    negative_percent = (negative_count / len(data)) * 100 if len(data) > 0 else 0
                    
                    if negative_percent > 5:
                        self.insights.append(StatisticalInsight(
                            insight_id=f"fin_{col}_{len(self.insights)}",
                            category="summary",
                            title=f"Negative values in financial column {col}",
                            description=f"Found {negative_count} negative values ({negative_percent:.1f}%) "
                                      f"in '{col}'. Review if these represent refunds, debits, or data errors.",
                            severity="medium",
                            confidence=0.85,
                            affected_columns=[col],
                            statistical_evidence={
                                "negative_count": int(negative_count),
                                "negative_percent": float(negative_percent),
                                "min_value": float(data.min()),
                                "mean_value": float(data.mean())
                            },
                            action_items=[
                                "Verify if negative values are intentional (refunds, debits)",
                                "Consider separating positive and negative transactions",
                                "Flag potentially erroneous negative values"
                            ]
                        ))
                except Exception:
                    continue
    
    def _analyze_temporal_patterns(self):
        """Domain-specific analysis for time-series datasets."""
        if not self.datetime_columns:
            return
        
        datetime_col = self.datetime_columns[0]
        try:
            df_sorted = self.df.sort_values(datetime_col)
            dates = pd.to_datetime(df_sorted[datetime_col])
            
            # Check for gaps in time series
            time_diffs = dates.diff()
            median_diff = time_diffs.median()
            
            # Find gaps larger than 2x median
            large_gaps = time_diffs[time_diffs > 2 * median_diff].dropna()
            
            if len(large_gaps) > 0:
                self.insights.append(StatisticalInsight(
                    insight_id=f"temporal_{len(self.insights)}",
                    category="trend",
                    title=f"Gaps detected in time series data",
                    description=f"Found {len(large_gaps)} gaps in the time series that are larger "
                              f"than expected. Median interval: {median_diff}, largest gap: {large_gaps.max()}.",
                    severity="medium",
                    confidence=0.80,
                    affected_columns=[datetime_col],
                    statistical_evidence={
                        "gap_count": len(large_gaps),
                        "median_interval": str(median_diff),
                        "max_gap": str(large_gaps.max())
                    },
                    visualization_hint="line",
                    action_items=[
                        "Review time periods with missing data",
                        "Consider forward-fill or interpolation for gaps",
                        "Investigate why data collection stopped during gaps"
                    ]
                ))
        except Exception:
            pass
    
    def _analyze_sales_patterns(self):
        """Domain-specific analysis for sales datasets."""
        # Look for quantity or amount columns
        quantity_cols = [col for col in self.numeric_columns 
                        if any(keyword in col.lower() for keyword in ['quantity', 'qty', 'amount', 'sales'])]
        
        if quantity_cols:
            for col in quantity_cols[:2]:
                try:
                    data = self.df[col].dropna()
                    # Convert to int to avoid numpy boolean subtract errors
                    zero_count = int((data == 0).sum())
                    zero_percent = (zero_count / len(data)) * 100 if len(data) > 0 else 0
                    
                    if zero_percent > 5:
                        self.insights.append(StatisticalInsight(
                            insight_id=f"sales_{col}_{len(self.insights)}",
                            category="summary",
                            title=f"Zero values in sales column {col}",
                            description=f"Found {zero_count} zero values ({zero_percent:.1f}%) in '{col}'. "
                                      f"These may represent cancelled orders or placeholders.",
                            severity="low",
                            confidence=0.75,
                            affected_columns=[col],
                            statistical_evidence={
                                "zero_count": int(zero_count),
                                "zero_percent": float(zero_percent)
                            },
                            action_items=[
                                "Filter out zero-quantity records if appropriate",
                                "Investigate why zeros appear in the dataset",
                                "Separate completed vs. cancelled transactions"
                            ]
                        ))
                except Exception:
                    continue
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all insights."""
        if not self.insights:
            self.analyze_all()
        
        return {
            "total_insights": len(self.insights),
            "by_category": {
                "trend": len([i for i in self.insights if i.category == "trend"]),
                "anomaly": len([i for i in self.insights if i.category == "anomaly"]),
                "correlation": len([i for i in self.insights if i.category == "correlation"]),
                "distribution": len([i for i in self.insights if i.category == "distribution"]),
                "summary": len([i for i in self.insights if i.category == "summary"])
            },
            "by_severity": {
                "high": len([i for i in self.insights if i.severity == "high"]),
                "medium": len([i for i in self.insights if i.severity == "medium"]),
                "low": len([i for i in self.insights if i.severity == "low"])
            },
            "high_confidence_insights": len([i for i in self.insights if i.confidence > 0.85])
        }
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Export insights as list of dictionaries."""
        return [
            {
                "insight_id": insight.insight_id,
                "category": insight.category,
                "title": insight.title,
                "description": insight.description,
                "severity": insight.severity,
                "confidence": insight.confidence,
                "affected_columns": insight.affected_columns,
                "statistical_evidence": insight.statistical_evidence,
                "visualization_hint": insight.visualization_hint,
                "action_items": insight.action_items or []
            }
            for insight in self.insights
        ]
