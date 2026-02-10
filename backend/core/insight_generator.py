"""
Insight Generator for EchoBI v2.0
Generates insights using statistical analysis with optional AI enhancement.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from .statistical_analyzer import StatisticalAnalyzer, StatisticalInsight


@dataclass
class Insight:
    """Unified insight data class."""
    insight_id: str
    source: str  # statistical, ai, hybrid
    category: str  # trend, anomaly, correlation, distribution, summary, recommendation
    title: str
    description: str
    severity: str  # high, medium, low
    confidence: float  # 0-1
    affected_columns: List[str]
    evidence: Dict[str, Any]
    visualization_type: Optional[str] = None
    action_items: Optional[List[str]] = None
    timestamp: Optional[str] = None


class InsightGenerator:
    """
    Main insight generation engine for EchoBI v2.0.
    
    Combines statistical analysis with optional AI enhancement to generate
    actionable insights about datasets.
    """
    
    def __init__(
        self, 
        df: pd.DataFrame, 
        column_profiles: Dict[str, Any],
        dataset_type: str,
        use_ai: bool = False,
        ai_config: Optional[Dict[str, Any]] = None
    ):
        self.df = df
        self.column_profiles = column_profiles
        self.dataset_type = dataset_type
        self.use_ai = use_ai
        self.ai_config = ai_config or {}
        
        # Initialize statistical analyzer
        self.stat_analyzer = StatisticalAnalyzer(df, column_profiles, dataset_type)
        
        # Storage for all insights
        self.insights: List[Insight] = []
        self.recommendations: List[Dict[str, Any]] = []
    
    def generate_insights(self) -> List[Insight]:
        """Generate all insights (statistical + optional AI)."""
        # Always generate statistical insights (reliable fallback)
        statistical_insights = self._generate_statistical_insights()
        
        # Optionally enhance with AI insights
        if self.use_ai and self.ai_config.get('enabled', False):
            ai_insights = self._generate_ai_insights()
            self.insights.extend(ai_insights)
        
        # Generate recommendations based on insights
        self.recommendations = self._generate_recommendations()
        
        return self.insights
    
    def _generate_statistical_insights(self) -> List[Insight]:
        """Generate insights using statistical analysis."""
        stat_insights = self.stat_analyzer.analyze_all()
        
        # Convert StatisticalInsight to unified Insight format
        unified_insights = []
        for stat_insight in stat_insights:
            unified_insights.append(Insight(
                insight_id=stat_insight.insight_id,
                source="statistical",
                category=stat_insight.category,
                title=stat_insight.title,
                description=stat_insight.description,
                severity=stat_insight.severity,
                confidence=stat_insight.confidence,
                affected_columns=stat_insight.affected_columns,
                evidence=stat_insight.statistical_evidence,
                visualization_type=stat_insight.visualization_hint,
                action_items=stat_insight.action_items,
                timestamp=datetime.now().isoformat()
            ))
        
        self.insights = unified_insights
        return unified_insights
    
    def _generate_ai_insights(self) -> List[Insight]:
        """
        Generate AI-enhanced insights.
        
        This is a placeholder for future AI integration (GPT-4, Claude, etc.)
        In v2.0, we focus on statistical insights with AI-ready architecture.
        """
        ai_insights = []
        
        # Placeholder for AI insight generation
        # In production, this would:
        # 1. Prepare domain-specific prompt with dataset context
        # 2. Call LLM API with dataset statistics and samples
        # 3. Parse LLM response into structured insights
        # 4. Validate insights against data
        # 5. Merge with statistical insights
        
        # Example AI insight structure:
        # ai_insights.append(Insight(
        #     insight_id=f"ai_{len(self.insights)}",
        #     source="ai",
        #     category="recommendation",
        #     title="AI-suggested data transformation",
        #     description="Based on pattern analysis...",
        #     severity="medium",
        #     confidence=0.75,
        #     affected_columns=[],
        #     evidence={"model": "gpt-4", "prompt_version": "v1.0"},
        #     action_items=[]
        # ))
        
        return ai_insights
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on insights."""
        recommendations = []
        
        # Group insights by severity
        high_severity = [i for i in self.insights if i.severity == "high"]
        medium_severity = [i for i in self.insights if i.severity == "medium"]
        
        # Data quality recommendations
        if high_severity:
            recommendations.append({
                "priority": 1,
                "category": "data_quality",
                "title": "Address high-severity data quality issues",
                "description": f"Found {len(high_severity)} critical issues that should be addressed immediately.",
                "actions": [
                    "Review missing data patterns and apply appropriate imputation",
                    "Investigate outliers and anomalies",
                    "Validate data integrity"
                ],
                "affected_insights": [i.insight_id for i in high_severity]
            })
        
        # Preprocessing recommendations based on dataset type
        if self.dataset_type == "Financial":
            recommendations.extend(self._get_financial_recommendations())
        elif self.dataset_type == "Time-Series":
            recommendations.extend(self._get_timeseries_recommendations())
        elif self.dataset_type == "Sales":
            recommendations.extend(self._get_sales_recommendations())
        
        # Modeling recommendations
        numeric_cols = len([c for c in self.column_profiles.values() if c.get('type') == 'numeric'])
        if numeric_cols >= 3:
            recommendations.append({
                "priority": 3,
                "category": "modeling",
                "title": "Dataset suitable for predictive modeling",
                "description": f"With {numeric_cols} numeric features, this dataset may be suitable "
                             f"for regression or classification models.",
                "actions": [
                    "Define prediction target variable",
                    "Split data into training and testing sets",
                    "Consider feature engineering based on insights"
                ],
                "affected_insights": []
            })
        
        # Visualization recommendations
        viz_insights = [i for i in self.insights if i.visualization_type]
        if viz_insights:
            recommended_charts = list(set([i.visualization_type for i in viz_insights]))
            recommendations.append({
                "priority": 4,
                "category": "visualization",
                "title": "Recommended visualizations",
                "description": f"Based on insights, {len(recommended_charts)} chart types are recommended.",
                "actions": [
                    f"Create {chart_type} chart" for chart_type in recommended_charts[:5]
                ],
                "affected_insights": [i.insight_id for i in viz_insights]
            })
        
        return recommendations
    
    def _get_financial_recommendations(self) -> List[Dict[str, Any]]:
        """Financial dataset-specific recommendations."""
        recs = []
        
        # Check for currency columns
        currency_cols = [col for col, profile in self.column_profiles.items() 
                        if any(keyword in col.lower() for keyword in ['price', 'amount', 'balance', 'cost'])]
        
        if currency_cols:
            recs.append({
                "priority": 2,
                "category": "preprocessing",
                "title": "Normalize financial columns",
                "description": "Detected currency/financial columns that may benefit from normalization.",
                "actions": [
                    "Apply currency normalization (remove symbols, standardize format)",
                    "Check for negative values and validate",
                    "Consider inflation adjustment for historical data"
                ],
                "affected_insights": []
            })
        
        return recs
    
    def _get_timeseries_recommendations(self) -> List[Dict[str, Any]]:
        """Time-series dataset-specific recommendations."""
        recs = []
        
        datetime_cols = [col for col, profile in self.column_profiles.items() 
                        if profile.get('type') == 'datetime']
        
        if datetime_cols:
            recs.append({
                "priority": 2,
                "category": "preprocessing",
                "title": "Time-series preprocessing required",
                "description": "Apply time-series specific transformations for better analysis.",
                "actions": [
                    "Ensure data is sorted by datetime",
                    "Check for and handle missing time intervals",
                    "Consider resampling to regular intervals",
                    "Extract time-based features (day of week, month, etc.)"
                ],
                "affected_insights": []
            })
        
        return recs
    
    def _get_sales_recommendations(self) -> List[Dict[str, Any]]:
        """Sales dataset-specific recommendations."""
        recs = []
        
        # Look for customer/product identifiers
        id_cols = [col for col, profile in self.column_profiles.items() 
                  if profile.get('is_key', False) or 'id' in col.lower()]
        
        if id_cols:
            recs.append({
                "priority": 2,
                "category": "preprocessing",
                "title": "Sales data enrichment opportunities",
                "description": "Enhance sales dataset with derived metrics.",
                "actions": [
                    "Calculate RFM scores (Recency, Frequency, Monetary)",
                    "Identify customer segments",
                    "Analyze product categories and SKU patterns",
                    "Compute sales velocity metrics"
                ],
                "affected_insights": []
            })
        
        return recs
    
    def get_insights_by_category(self, category: str) -> List[Insight]:
        """Get insights filtered by category."""
        return [i for i in self.insights if i.category == category]
    
    def get_insights_by_severity(self, severity: str) -> List[Insight]:
        """Get insights filtered by severity."""
        return [i for i in self.insights if i.severity == severity]
    
    def get_high_confidence_insights(self, threshold: float = 0.85) -> List[Insight]:
        """Get insights with confidence above threshold."""
        return [i for i in self.insights if i.confidence >= threshold]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of insight generation results."""
        if not self.insights:
            self.generate_insights()
        
        return {
            "total_insights": len(self.insights),
            "by_source": {
                "statistical": len([i for i in self.insights if i.source == "statistical"]),
                "ai": len([i for i in self.insights if i.source == "ai"]),
                "hybrid": len([i for i in self.insights if i.source == "hybrid"])
            },
            "by_category": {
                "trend": len([i for i in self.insights if i.category == "trend"]),
                "anomaly": len([i for i in self.insights if i.category == "anomaly"]),
                "correlation": len([i for i in self.insights if i.category == "correlation"]),
                "distribution": len([i for i in self.insights if i.category == "distribution"]),
                "summary": len([i for i in self.insights if i.category == "summary"]),
                "recommendation": len([i for i in self.insights if i.category == "recommendation"])
            },
            "by_severity": {
                "high": len([i for i in self.insights if i.severity == "high"]),
                "medium": len([i for i in self.insights if i.severity == "medium"]),
                "low": len([i for i in self.insights if i.severity == "low"])
            },
            "high_confidence_count": len([i for i in self.insights if i.confidence > 0.85]),
            "recommendations_count": len(self.recommendations),
            "dataset_type": self.dataset_type,
            "ai_enabled": self.use_ai
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export complete insight generation results."""
        return {
            "insights": [
                {
                    "insight_id": i.insight_id,
                    "source": i.source,
                    "category": i.category,
                    "title": i.title,
                    "description": i.description,
                    "severity": i.severity,
                    "confidence": i.confidence,
                    "affected_columns": i.affected_columns,
                    "evidence": i.evidence,
                    "visualization_type": i.visualization_type,
                    "action_items": i.action_items or [],
                    "timestamp": i.timestamp
                }
                for i in self.insights
            ],
            "recommendations": self.recommendations,
            "summary": self.get_summary()
        }
