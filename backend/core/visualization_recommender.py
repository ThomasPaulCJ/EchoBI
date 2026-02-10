"""
Visualization Recommender for EchoBI v2.0
Intelligently recommends chart types based on data characteristics.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum


class ChartType(Enum):
    """Supported chart types."""
    BAR = "bar"
    HORIZONTAL_BAR = "horizontal_bar"
    LINE = "line"
    AREA = "area"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    PIE = "pie"
    DONUT = "donut"
    HISTOGRAM = "histogram"
    BOX = "box"
    VIOLIN = "violin"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"
    FUNNEL = "funnel"
    WATERFALL = "waterfall"
    GAUGE = "gauge"
    INDICATOR = "indicator"
    TABLE = "table"


@dataclass
class ChartRecommendation:
    """Data class for chart recommendation."""
    chart_id: str
    chart_type: str
    title: str
    description: str
    priority: int  # 1=highest
    confidence: float  # 0-1
    x_axis: Optional[str] = None
    y_axis: Optional[List[str]] = None
    color_by: Optional[str] = None
    size_by: Optional[str] = None
    group_by: Optional[str] = None
    aggregation: Optional[str] = None  # sum, mean, count, etc.
    reasoning: Optional[str] = None
    use_case: Optional[str] = None


class VisualizationRecommender:
    """
    Recommends appropriate visualizations based on data characteristics.
    
    Considers column types, data distribution, relationships, and domain context.
    """
    
    def __init__(
        self, 
        df: pd.DataFrame, 
        column_profiles: Dict[str, Any],
        dataset_type: str,
        relationships: Optional[List[Dict[str, Any]]] = None,
        insights: Optional[List[Dict[str, Any]]] = None
    ):
        self.df = df
        self.column_profiles = column_profiles
        self.dataset_type = dataset_type
        self.relationships = relationships or []
        self.insights = insights or []
        
        # Categorize columns
        self.numeric_columns = [col for col, profile in column_profiles.items() 
                               if profile.get('type') == 'numeric']
        self.categorical_columns = [col for col, profile in column_profiles.items() 
                                   if profile.get('type') == 'categorical']
        self.datetime_columns = [col for col, profile in column_profiles.items() 
                                if profile.get('type') == 'datetime']
        
        self.recommendations: List[ChartRecommendation] = []
    
    def generate_recommendations(self) -> List[ChartRecommendation]:
        """Generate all chart recommendations."""
        self.recommendations = []
        
        # Basic univariate visualizations
        self._recommend_single_numeric()
        self._recommend_single_categorical()
        
        # Bivariate visualizations
        self._recommend_numeric_vs_numeric()
        self._recommend_categorical_vs_numeric()
        self._recommend_time_series()
        
        # Multivariate visualizations
        self._recommend_correlation_heatmap()
        self._recommend_multivariate()
        
        # Domain-specific recommendations
        if self.dataset_type == 'Financial':
            self._recommend_financial_charts()
        elif self.dataset_type == 'Sales':
            self._recommend_sales_charts()
        elif self.dataset_type == 'Time-Series':
            self._recommend_timeseries_charts()
        
        # KPI/Summary visualizations
        self._recommend_kpi_charts()
        
        # Sort by priority and confidence
        self.recommendations.sort(key=lambda x: (x.priority, -x.confidence))
        
        return self.recommendations
    
    def _recommend_single_numeric(self):
        """Recommend charts for single numeric columns."""
        for col in self.numeric_columns[:5]:  # Top 5
            profile = self.column_profiles[col]
            
            # Histogram for distribution
            self.recommendations.append(ChartRecommendation(
                chart_id=f"hist_{col}",
                chart_type=ChartType.HISTOGRAM.value,
                title=f"Distribution of {col}",
                description=f"Shows the frequency distribution of {col} values",
                priority=2,
                confidence=0.90,
                x_axis=col,
                reasoning="Histogram is ideal for visualizing the distribution of a single numeric variable",
                use_case="Understanding data distribution and identifying patterns"
            ))
            
            # Box plot for outlier detection
            if profile.get('uniqueness', 0) > 0.1:  # Not too many identical values
                self.recommendations.append(ChartRecommendation(
                    chart_id=f"box_{col}",
                    chart_type=ChartType.BOX.value,
                    title=f"Box Plot of {col}",
                    description=f"Displays quartiles and outliers in {col}",
                    priority=3,
                    confidence=0.85,
                    x_axis=col,
                    reasoning="Box plots effectively show median, quartiles, and outliers",
                    use_case="Identifying outliers and understanding data spread"
                ))
    
    def _recommend_single_categorical(self):
        """Recommend charts for single categorical columns."""
        for col in self.categorical_columns[:5]:
            profile = self.column_profiles[col]
            unique_count = profile.get('unique_count', 0)
            
            if unique_count <= 10:
                # Bar chart for categories
                self.recommendations.append(ChartRecommendation(
                    chart_id=f"bar_{col}",
                    chart_type=ChartType.BAR.value,
                    title=f"Count by {col}",
                    description=f"Shows the frequency of each {col} category",
                    priority=1,
                    confidence=0.95,
                    x_axis=col,
                    y_axis=["count"],
                    aggregation="count",
                    reasoning="Bar charts are excellent for comparing categorical data",
                    use_case="Comparing frequencies across categories"
                ))
                
                # Pie chart if few categories
                if unique_count <= 6:
                    self.recommendations.append(ChartRecommendation(
                        chart_id=f"pie_{col}",
                        chart_type=ChartType.PIE.value,
                        title=f"Distribution of {col}",
                        description=f"Shows proportional distribution of {col}",
                        priority=3,
                        confidence=0.80,
                        x_axis=col,
                        aggregation="count",
                        reasoning="Pie charts work well for showing parts of a whole with few categories",
                        use_case="Showing percentage breakdown"
                    ))
            elif unique_count <= 20:
                # Horizontal bar for many categories
                self.recommendations.append(ChartRecommendation(
                    chart_id=f"hbar_{col}",
                    chart_type=ChartType.HORIZONTAL_BAR.value,
                    title=f"Top Categories in {col}",
                    description=f"Shows the most common {col} values",
                    priority=2,
                    confidence=0.85,
                    x_axis=col,
                    y_axis=["count"],
                    aggregation="count",
                    reasoning="Horizontal bars are better for longer category names",
                    use_case="Ranking categories by frequency"
                ))
    
    def _recommend_numeric_vs_numeric(self):
        """Recommend charts for numeric vs numeric relationships."""
        if len(self.numeric_columns) < 2:
            return
        
        # Find correlated pairs from relationships
        correlated_pairs = [
            r for r in self.relationships 
            if r.get('type') == 'correlation' and abs(r.get('strength', 0)) > 0.5
        ]
        
        if correlated_pairs:
            for pair in correlated_pairs[:3]:  # Top 3
                col1, col2 = pair['column1'], pair['column2']
                strength = pair.get('strength', 0)
                
                self.recommendations.append(ChartRecommendation(
                    chart_id=f"scatter_{col1}_{col2}",
                    chart_type=ChartType.SCATTER.value,
                    title=f"{col1} vs {col2}",
                    description=f"Shows relationship between {col1} and {col2} (r={strength:.2f})",
                    priority=1,
                    confidence=0.90,
                    x_axis=col1,
                    y_axis=[col2],
                    reasoning=f"Strong correlation ({strength:.2f}) suggests meaningful relationship",
                    use_case="Analyzing correlation and trends"
                ))
        else:
            # Default: first two numeric columns
            if len(self.numeric_columns) >= 2:
                col1, col2 = self.numeric_columns[0], self.numeric_columns[1]
                self.recommendations.append(ChartRecommendation(
                    chart_id=f"scatter_{col1}_{col2}",
                    chart_type=ChartType.SCATTER.value,
                    title=f"{col1} vs {col2}",
                    description=f"Explore relationship between {col1} and {col2}",
                    priority=2,
                    confidence=0.75,
                    x_axis=col1,
                    y_axis=[col2],
                    reasoning="Scatter plots reveal relationships between numeric variables",
                    use_case="Exploring potential correlations"
                ))
    
    def _recommend_categorical_vs_numeric(self):
        """Recommend charts for categorical vs numeric relationships."""
        if not self.categorical_columns or not self.numeric_columns:
            return
        
        for cat_col in self.categorical_columns[:3]:
            cat_profile = self.column_profiles[cat_col]
            unique_count = cat_profile.get('unique_count', 0)
            
            if unique_count > 20:
                continue  # Too many categories
            
            for num_col in self.numeric_columns[:2]:
                # Bar chart with aggregation
                self.recommendations.append(ChartRecommendation(
                    chart_id=f"bar_{cat_col}_{num_col}",
                    chart_type=ChartType.BAR.value,
                    title=f"Average {num_col} by {cat_col}",
                    description=f"Compare {num_col} across {cat_col} categories",
                    priority=1,
                    confidence=0.88,
                    x_axis=cat_col,
                    y_axis=[num_col],
                    aggregation="mean",
                    reasoning="Bar charts effectively compare numeric values across categories",
                    use_case="Comparing metrics across groups"
                ))
                
                # Box plot for distribution comparison
                if unique_count <= 10:
                    self.recommendations.append(ChartRecommendation(
                        chart_id=f"box_{cat_col}_{num_col}",
                        chart_type=ChartType.BOX.value,
                        title=f"{num_col} Distribution by {cat_col}",
                        description=f"Compare {num_col} distributions across {cat_col}",
                        priority=2,
                        confidence=0.82,
                        x_axis=cat_col,
                        y_axis=[num_col],
                        reasoning="Box plots show distribution differences across groups",
                        use_case="Comparing distributions and identifying outliers by category"
                    ))
    
    def _recommend_time_series(self):
        """Recommend time-series visualizations."""
        if not self.datetime_columns:
            return
        
        datetime_col = self.datetime_columns[0]
        
        for num_col in self.numeric_columns[:3]:
            # Line chart for trend
            self.recommendations.append(ChartRecommendation(
                chart_id=f"line_{datetime_col}_{num_col}",
                chart_type=ChartType.LINE.value,
                title=f"{num_col} Over Time",
                description=f"Shows how {num_col} changes over {datetime_col}",
                priority=1,
                confidence=0.95,
                x_axis=datetime_col,
                y_axis=[num_col],
                reasoning="Line charts are ideal for showing trends over time",
                use_case="Identifying trends and patterns over time"
            ))
            
            # Area chart for cumulative view
            self.recommendations.append(ChartRecommendation(
                chart_id=f"area_{datetime_col}_{num_col}",
                chart_type=ChartType.AREA.value,
                title=f"{num_col} Trend Over Time",
                description=f"Area chart showing {num_col} evolution",
                priority=2,
                confidence=0.85,
                x_axis=datetime_col,
                y_axis=[num_col],
                reasoning="Area charts emphasize magnitude of change over time",
                use_case="Visualizing cumulative trends"
            ))
    
    def _recommend_correlation_heatmap(self):
        """Recommend correlation heatmap for multiple numeric columns."""
        if len(self.numeric_columns) >= 3:
            self.recommendations.append(ChartRecommendation(
                chart_id="heatmap_correlation",
                chart_type=ChartType.HEATMAP.value,
                title="Correlation Heatmap",
                description=f"Shows correlations between {len(self.numeric_columns)} numeric columns",
                priority=2,
                confidence=0.90,
                y_axis=self.numeric_columns,
                reasoning="Heatmaps efficiently display many correlations at once",
                use_case="Identifying correlated variables for analysis"
            ))
    
    def _recommend_multivariate(self):
        """Recommend multivariate visualizations."""
        if len(self.numeric_columns) >= 3 and self.categorical_columns:
            num_cols = self.numeric_columns[:3]
            cat_col = self.categorical_columns[0]
            
            # Bubble chart (3 numeric + 1 categorical)
            self.recommendations.append(ChartRecommendation(
                chart_id=f"bubble_{num_cols[0]}_{num_cols[1]}_{num_cols[2]}",
                chart_type=ChartType.BUBBLE.value,
                title=f"{num_cols[0]} vs {num_cols[1]} (sized by {num_cols[2]})",
                description=f"Multi-dimensional view with {cat_col} coloring",
                priority=3,
                confidence=0.75,
                x_axis=num_cols[0],
                y_axis=[num_cols[1]],
                size_by=num_cols[2],
                color_by=cat_col,
                reasoning="Bubble charts can display 4 dimensions simultaneously",
                use_case="Complex multi-variable analysis"
            ))
    
    def _recommend_financial_charts(self):
        """Financial domain-specific chart recommendations."""
        # Look for amount/balance columns
        amount_cols = [col for col in self.numeric_columns 
                      if any(kw in col.lower() for kw in ['amount', 'balance', 'revenue', 'cost', 'profit'])]
        
        if amount_cols and self.datetime_columns:
            datetime_col = self.datetime_columns[0]
            amount_col = amount_cols[0]
            
            # Waterfall chart for financial flow
            self.recommendations.append(ChartRecommendation(
                chart_id=f"waterfall_{amount_col}",
                chart_type=ChartType.WATERFALL.value,
                title=f"{amount_col} Flow Analysis",
                description=f"Shows cumulative effect of {amount_col} changes",
                priority=1,
                confidence=0.85,
                x_axis=datetime_col,
                y_axis=[amount_col],
                reasoning="Waterfall charts are perfect for financial flow analysis",
                use_case="Tracking cumulative financial changes"
            ))
        
        # Gauge for current metrics
        if amount_cols:
            self.recommendations.append(ChartRecommendation(
                chart_id=f"gauge_{amount_cols[0]}",
                chart_type=ChartType.GAUGE.value,
                title=f"Current {amount_cols[0]}",
                description=f"KPI gauge for {amount_cols[0]}",
                priority=2,
                confidence=0.80,
                y_axis=[amount_cols[0]],
                aggregation="sum",
                reasoning="Gauges provide at-a-glance KPI monitoring",
                use_case="Dashboard KPI display"
            ))
    
    def _recommend_sales_charts(self):
        """Sales domain-specific chart recommendations."""
        # Look for quantity/sales columns
        sales_cols = [col for col in self.numeric_columns 
                     if any(kw in col.lower() for kw in ['quantity', 'sales', 'revenue', 'units'])]
        
        if sales_cols and self.categorical_columns:
            sales_col = sales_cols[0]
            cat_col = self.categorical_columns[0]
            
            # Treemap for hierarchical sales
            self.recommendations.append(ChartRecommendation(
                chart_id=f"treemap_{cat_col}_{sales_col}",
                chart_type=ChartType.TREEMAP.value,
                title=f"{sales_col} by {cat_col}",
                description=f"Hierarchical view of {sales_col} distribution",
                priority=2,
                confidence=0.82,
                group_by=cat_col,
                y_axis=[sales_col],
                aggregation="sum",
                reasoning="Treemaps show hierarchical contribution effectively",
                use_case="Product/category performance analysis"
            ))
            
            # Funnel chart if appropriate column names
            if 'stage' in cat_col.lower() or 'step' in cat_col.lower():
                self.recommendations.append(ChartRecommendation(
                    chart_id=f"funnel_{cat_col}_{sales_col}",
                    chart_type=ChartType.FUNNEL.value,
                    title=f"Sales Funnel by {cat_col}",
                    description=f"Conversion funnel showing {sales_col} drop-off",
                    priority=1,
                    confidence=0.88,
                    x_axis=cat_col,
                    y_axis=[sales_col],
                    reasoning="Funnel charts ideal for conversion analysis",
                    use_case="Analyzing sales pipeline conversion"
                ))
    
    def _recommend_timeseries_charts(self):
        """Time-series domain-specific recommendations."""
        if not self.datetime_columns or not self.numeric_columns:
            return
        
        datetime_col = self.datetime_columns[0]
        
        # Multi-line chart for comparing multiple metrics
        if len(self.numeric_columns) >= 2:
            self.recommendations.append(ChartRecommendation(
                chart_id=f"multiline_{datetime_col}",
                chart_type=ChartType.LINE.value,
                title="Multi-Metric Time Series",
                description=f"Compare {len(self.numeric_columns)} metrics over time",
                priority=1,
                confidence=0.90,
                x_axis=datetime_col,
                y_axis=self.numeric_columns[:5],  # Max 5 lines
                reasoning="Multiple lines enable metric comparison",
                use_case="Comparing multiple time-based trends"
            ))
    
    def _recommend_kpi_charts(self):
        """Recommend KPI/summary visualizations."""
        # Indicator cards for key metrics
        for num_col in self.numeric_columns[:3]:
            self.recommendations.append(ChartRecommendation(
                chart_id=f"indicator_{num_col}",
                chart_type=ChartType.INDICATOR.value,
                title=f"Total {num_col}",
                description=f"Key metric display for {num_col}",
                priority=3,
                confidence=0.85,
                y_axis=[num_col],
                aggregation="sum",
                reasoning="Indicators provide quick metric summaries",
                use_case="Dashboard overview"
            ))
        
        # Table for detailed data view
        self.recommendations.append(ChartRecommendation(
            chart_id="table_detailed",
            chart_type=ChartType.TABLE.value,
            title="Detailed Data Table",
            description="Complete tabular view of the dataset",
            priority=4,
            confidence=1.0,
            reasoning="Tables provide complete data access",
            use_case="Detailed data exploration"
        ))
    
    def get_recommendations_by_priority(self, max_priority: int = 2) -> List[ChartRecommendation]:
        """Get high-priority recommendations."""
        if not self.recommendations:
            self.generate_recommendations()
        return [r for r in self.recommendations if r.priority <= max_priority]
    
    def get_recommendations_by_type(self, chart_type: str) -> List[ChartRecommendation]:
        """Get recommendations for specific chart type."""
        if not self.recommendations:
            self.generate_recommendations()
        return [r for r in self.recommendations if r.chart_type == chart_type]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of recommendations."""
        if not self.recommendations:
            self.generate_recommendations()
        
        return {
            "total_recommendations": len(self.recommendations),
            "by_priority": {
                "high": len([r for r in self.recommendations if r.priority == 1]),
                "medium": len([r for r in self.recommendations if r.priority == 2]),
                "low": len([r for r in self.recommendations if r.priority >= 3])
            },
            "by_type": {
                chart_type: len([r for r in self.recommendations if r.chart_type == chart_type])
                for chart_type in set(r.chart_type for r in self.recommendations)
            },
            "high_confidence_count": len([r for r in self.recommendations if r.confidence > 0.85]),
            "dataset_type": self.dataset_type
        }
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Export recommendations as list of dictionaries."""
        return [
            {
                "chart_id": rec.chart_id,
                "chart_type": rec.chart_type,
                "title": rec.title,
                "description": rec.description,
                "priority": rec.priority,
                "confidence": rec.confidence,
                "config": {
                    "x_axis": rec.x_axis,
                    "y_axis": rec.y_axis,
                    "color_by": rec.color_by,
                    "size_by": rec.size_by,
                    "group_by": rec.group_by,
                    "aggregation": rec.aggregation
                },
                "reasoning": rec.reasoning,
                "use_case": rec.use_case
            }
            for rec in self.recommendations
        ]
