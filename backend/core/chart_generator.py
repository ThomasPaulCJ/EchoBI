"""
Chart Generator for EchoBI v2.0
Generates Plotly chart specifications from recommendations and data.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime


class ChartGenerator:
    """
    Generates Plotly chart JSON specifications.
    
    Takes visualization recommendations and data to create
    production-ready Plotly charts.
    """
    
    def __init__(self, df: pd.DataFrame, column_profiles: Dict[str, Any]):
        self.df = df
        self.column_profiles = column_profiles
        self.color_palette = [
            '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
            '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
        ]
    
    def generate_chart(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Plotly chart specification from recommendation."""
        chart_type = recommendation['chart_type']
        
        # Route to appropriate chart generator
        generators = {
            'bar': self._generate_bar_chart,
            'horizontal_bar': self._generate_horizontal_bar_chart,
            'line': self._generate_line_chart,
            'area': self._generate_area_chart,
            'scatter': self._generate_scatter_chart,
            'bubble': self._generate_bubble_chart,
            'pie': self._generate_pie_chart,
            'donut': self._generate_donut_chart,
            'histogram': self._generate_histogram,
            'box': self._generate_box_chart,
            'heatmap': self._generate_heatmap,
            'treemap': self._generate_treemap,
            'funnel': self._generate_funnel_chart,
            'waterfall': self._generate_waterfall_chart,
            'gauge': self._generate_gauge_chart,
            'indicator': self._generate_indicator,
            'table': self._generate_table
        }
        
        generator = generators.get(chart_type)
        if generator:
            return generator(recommendation)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
    def _generate_bar_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate bar chart."""
        config = rec['config']
        x_col = config['x_axis']
        y_cols = config.get('y_axis', [])
        agg = config.get('aggregation', 'count')
        
        if agg == 'count':
            # Count frequency
            counts = self.df[x_col].value_counts().reset_index()
            counts.columns = [x_col, 'count']
            
            return {
                'data': [{
                    'type': 'bar',
                    'x': counts[x_col].tolist(),
                    'y': counts['count'].tolist(),
                    'marker': {'color': self.color_palette[0]},
                    'name': f'Count of {x_col}'
                }],
                'layout': {
                    'title': rec['title'],
                    'xaxis': {'title': x_col},
                    'yaxis': {'title': 'Count'},
                    'hovermode': 'closest',
                    'template': 'plotly_white'
                }
            }
        elif y_cols and agg in ['mean', 'sum', 'median']:
            # Aggregate numeric column by category
            y_col = y_cols[0]
            if agg == 'mean':
                grouped = self.df.groupby(x_col)[y_col].mean().reset_index()
            elif agg == 'sum':
                grouped = self.df.groupby(x_col)[y_col].sum().reset_index()
            else:  # median
                grouped = self.df.groupby(x_col)[y_col].median().reset_index()
            
            return {
                'data': [{
                    'type': 'bar',
                    'x': grouped[x_col].tolist(),
                    'y': grouped[y_col].tolist(),
                    'marker': {'color': self.color_palette[0]},
                    'name': f'{agg.title()} {y_col}'
                }],
                'layout': {
                    'title': rec['title'],
                    'xaxis': {'title': x_col},
                    'yaxis': {'title': f'{agg.title()} of {y_col}'},
                    'hovermode': 'closest',
                    'template': 'plotly_white'
                }
            }
        
        return self._generate_default_chart(rec)
    
    def _generate_horizontal_bar_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate horizontal bar chart."""
        config = rec['config']
        x_col = config['x_axis']
        
        counts = self.df[x_col].value_counts().head(15).reset_index()
        counts.columns = [x_col, 'count']
        
        return {
            'data': [{
                'type': 'bar',
                'y': counts[x_col].tolist(),
                'x': counts['count'].tolist(),
                'orientation': 'h',
                'marker': {'color': self.color_palette[1]},
                'name': f'Count of {x_col}'
            }],
            'layout': {
                'title': rec['title'],
                'xaxis': {'title': 'Count'},
                'yaxis': {'title': x_col},
                'hovermode': 'closest',
                'template': 'plotly_white',
                'height': max(400, len(counts) * 30)
            }
        }
    
    def _generate_line_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate line chart."""
        config = rec['config']
        x_col = config['x_axis']
        y_cols = config.get('y_axis', [])
        
        if not y_cols:
            return self._generate_default_chart(rec)
        
        # Sort by x-axis (usually datetime)
        df_sorted = self.df.sort_values(x_col)
        
        traces = []
        for i, y_col in enumerate(y_cols[:5]):  # Max 5 lines
            traces.append({
                'type': 'scatter',
                'mode': 'lines',
                'x': df_sorted[x_col].astype(str).tolist(),
                'y': df_sorted[y_col].tolist(),
                'name': y_col,
                'line': {'color': self.color_palette[i % len(self.color_palette)]}
            })
        
        return {
            'data': traces,
            'layout': {
                'title': rec['title'],
                'xaxis': {'title': x_col},
                'yaxis': {'title': 'Value'},
                'hovermode': 'x unified',
                'template': 'plotly_white'
            }
        }
    
    def _generate_area_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate area chart."""
        config = rec['config']
        x_col = config['x_axis']
        y_cols = config.get('y_axis', [])
        
        if not y_cols:
            return self._generate_default_chart(rec)
        
        df_sorted = self.df.sort_values(x_col)
        y_col = y_cols[0]
        
        return {
            'data': [{
                'type': 'scatter',
                'mode': 'lines',
                'x': df_sorted[x_col].astype(str).tolist(),
                'y': df_sorted[y_col].tolist(),
                'fill': 'tozeroy',
                'fillcolor': 'rgba(59, 130, 246, 0.3)',
                'line': {'color': self.color_palette[0]},
                'name': y_col
            }],
            'layout': {
                'title': rec['title'],
                'xaxis': {'title': x_col},
                'yaxis': {'title': y_col},
                'hovermode': 'x unified',
                'template': 'plotly_white'
            }
        }
    
    def _generate_scatter_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scatter plot."""
        config = rec['config']
        x_col = config['x_axis']
        y_cols = config.get('y_axis', [])
        color_by = config.get('color_by')
        
        if not y_cols:
            return self._generate_default_chart(rec)
        
        y_col = y_cols[0]
        
        if color_by and color_by in self.df.columns:
            # Colored by category
            traces = []
            for i, category in enumerate(self.df[color_by].unique()[:10]):
                df_cat = self.df[self.df[color_by] == category]
                traces.append({
                    'type': 'scatter',
                    'mode': 'markers',
                    'x': df_cat[x_col].tolist(),
                    'y': df_cat[y_col].tolist(),
                    'name': str(category),
                    'marker': {
                        'color': self.color_palette[i % len(self.color_palette)],
                        'size': 8
                    }
                })
            
            return {
                'data': traces,
                'layout': {
                    'title': rec['title'],
                    'xaxis': {'title': x_col},
                    'yaxis': {'title': y_col},
                    'hovermode': 'closest',
                    'template': 'plotly_white'
                }
            }
        else:
            return {
                'data': [{
                    'type': 'scatter',
                    'mode': 'markers',
                    'x': self.df[x_col].tolist(),
                    'y': self.df[y_col].tolist(),
                    'marker': {'color': self.color_palette[0], 'size': 8},
                    'name': f'{x_col} vs {y_col}'
                }],
                'layout': {
                    'title': rec['title'],
                    'xaxis': {'title': x_col},
                    'yaxis': {'title': y_col},
                    'hovermode': 'closest',
                    'template': 'plotly_white'
                }
            }
    
    def _generate_bubble_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate bubble chart."""
        config = rec['config']
        x_col = config['x_axis']
        y_cols = config.get('y_axis', [])
        size_by = config.get('size_by')
        color_by = config.get('color_by')
        
        if not y_cols or not size_by:
            return self._generate_scatter_chart(rec)
        
        y_col = y_cols[0]
        
        return {
            'data': [{
                'type': 'scatter',
                'mode': 'markers',
                'x': self.df[x_col].tolist(),
                'y': self.df[y_col].tolist(),
                'marker': {
                    'size': self.df[size_by].tolist(),
                    'sizemode': 'diameter',
                    'sizeref': self.df[size_by].max() / 50,
                    'color': self.color_palette[0]
                },
                'text': self.df[color_by].tolist() if color_by else None,
                'name': 'Data points'
            }],
            'layout': {
                'title': rec['title'],
                'xaxis': {'title': x_col},
                'yaxis': {'title': y_col},
                'hovermode': 'closest',
                'template': 'plotly_white'
            }
        }
    
    def _generate_pie_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pie chart."""
        config = rec['config']
        x_col = config['x_axis']
        
        counts = self.df[x_col].value_counts().head(10)
        
        return {
            'data': [{
                'type': 'pie',
                'labels': counts.index.tolist(),
                'values': counts.values.tolist(),
                'marker': {'colors': self.color_palette},
                'textinfo': 'label+percent',
                'hoverinfo': 'label+value+percent'
            }],
            'layout': {
                'title': rec['title'],
                'template': 'plotly_white'
            }
        }
    
    def _generate_donut_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate donut chart."""
        pie_chart = self._generate_pie_chart(rec)
        pie_chart['data'][0]['hole'] = 0.4
        return pie_chart
    
    def _generate_histogram(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate histogram."""
        config = rec['config']
        x_col = config['x_axis']
        
        return {
            'data': [{
                'type': 'histogram',
                'x': self.df[x_col].dropna().tolist(),
                'marker': {'color': self.color_palette[0]},
                'name': x_col
            }],
            'layout': {
                'title': rec['title'],
                'xaxis': {'title': x_col},
                'yaxis': {'title': 'Frequency'},
                'template': 'plotly_white',
                'bargap': 0.1
            }
        }
    
    def _generate_box_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate box plot."""
        config = rec['config']
        x_col = config.get('x_axis')
        y_cols = config.get('y_axis', [])
        
        if y_cols and x_col:
            # Box plot by category
            y_col = y_cols[0]
            traces = []
            for i, category in enumerate(self.df[x_col].unique()[:10]):
                df_cat = self.df[self.df[x_col] == category]
                traces.append({
                    'type': 'box',
                    'y': df_cat[y_col].dropna().tolist(),
                    'name': str(category),
                    'marker': {'color': self.color_palette[i % len(self.color_palette)]}
                })
            
            return {
                'data': traces,
                'layout': {
                    'title': rec['title'],
                    'yaxis': {'title': y_col},
                    'template': 'plotly_white'
                }
            }
        elif x_col:
            # Single box plot
            return {
                'data': [{
                    'type': 'box',
                    'y': self.df[x_col].dropna().tolist(),
                    'name': x_col,
                    'marker': {'color': self.color_palette[0]}
                }],
                'layout': {
                    'title': rec['title'],
                    'yaxis': {'title': x_col},
                    'template': 'plotly_white'
                }
            }
        
        return self._generate_default_chart(rec)
    
    def _generate_heatmap(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate correlation heatmap."""
        config = rec['config']
        y_cols = config.get('y_axis', [])
        
        if y_cols:
            # Use specified columns
            corr_cols = y_cols
        else:
            # Use all numeric columns
            corr_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(corr_cols) < 2:
            return self._generate_default_chart(rec)
        
        corr_matrix = self.df[corr_cols].corr()
        
        return {
            'data': [{
                'type': 'heatmap',
                'z': corr_matrix.values.tolist(),
                'x': corr_matrix.columns.tolist(),
                'y': corr_matrix.columns.tolist(),
                'colorscale': 'RdBu',
                'zmid': 0,
                'text': corr_matrix.values.round(2).tolist(),
                'texttemplate': '%{text}',
                'textfont': {'size': 10},
                'hovertemplate': '%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>'
            }],
            'layout': {
                'title': rec['title'],
                'template': 'plotly_white',
                'height': max(400, len(corr_cols) * 40),
                'width': max(400, len(corr_cols) * 40)
            }
        }
    
    def _generate_treemap(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate treemap."""
        config = rec['config']
        group_by = config.get('group_by')
        y_cols = config.get('y_axis', [])
        agg = config.get('aggregation', 'sum')
        
        if not group_by:
            return self._generate_default_chart(rec)
        
        if y_cols:
            y_col = y_cols[0]
            if agg == 'sum':
                grouped = self.df.groupby(group_by)[y_col].sum().reset_index()
            else:
                grouped = self.df.groupby(group_by)[y_col].mean().reset_index()
        else:
            grouped = self.df[group_by].value_counts().reset_index()
            grouped.columns = [group_by, 'count']
            y_col = 'count'
        
        return {
            'data': [{
                'type': 'treemap',
                'labels': grouped[group_by].tolist(),
                'values': grouped[y_col].tolist(),
                'parents': [''] * len(grouped),
                'textinfo': 'label+value+percent parent',
                'marker': {'colors': self.color_palette}
            }],
            'layout': {
                'title': rec['title'],
                'template': 'plotly_white'
            }
        }
    
    def _generate_funnel_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate funnel chart."""
        config = rec['config']
        x_col = config['x_axis']
        y_cols = config.get('y_axis', [])
        
        if y_cols:
            y_col = y_cols[0]
            grouped = self.df.groupby(x_col)[y_col].sum().reset_index()
        else:
            grouped = self.df[x_col].value_counts().reset_index()
            grouped.columns = [x_col, 'count']
            y_col = 'count'
        
        return {
            'data': [{
                'type': 'funnel',
                'y': grouped[x_col].tolist(),
                'x': grouped[y_col].tolist(),
                'textinfo': 'value+percent initial',
                'marker': {'color': self.color_palette[0]}
            }],
            'layout': {
                'title': rec['title'],
                'template': 'plotly_white'
            }
        }
    
    def _generate_waterfall_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate waterfall chart."""
        config = rec['config']
        x_col = config.get('x_axis')
        y_cols = config.get('y_axis', [])
        
        if not x_col or not y_cols:
            return self._generate_default_chart(rec)
        
        df_sorted = self.df.sort_values(x_col).head(20)
        y_col = y_cols[0]
        
        return {
            'data': [{
                'type': 'waterfall',
                'x': df_sorted[x_col].astype(str).tolist(),
                'y': df_sorted[y_col].tolist(),
                'textposition': 'outside',
                'connector': {'line': {'color': 'rgb(63, 63, 63)'}},
                'increasing': {'marker': {'color': '#10b981'}},
                'decreasing': {'marker': {'color': '#ef4444'}},
                'totals': {'marker': {'color': '#3b82f6'}}
            }],
            'layout': {
                'title': rec['title'],
                'xaxis': {'title': x_col},
                'yaxis': {'title': y_col},
                'template': 'plotly_white'
            }
        }
    
    def _generate_gauge_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate gauge chart."""
        config = rec['config']
        y_cols = config.get('y_axis', [])
        agg = config.get('aggregation', 'sum')
        
        if not y_cols:
            return self._generate_default_chart(rec)
        
        y_col = y_cols[0]
        
        if agg == 'sum':
            value = self.df[y_col].sum()
        elif agg == 'mean':
            value = self.df[y_col].mean()
        else:
            value = self.df[y_col].sum()
        
        max_value = value * 1.5  # Set max to 150% of current value
        
        return {
            'data': [{
                'type': 'indicator',
                'mode': 'gauge+number',
                'value': float(value),
                'title': {'text': rec['title']},
                'gauge': {
                    'axis': {'range': [0, float(max_value)]},
                    'bar': {'color': self.color_palette[0]},
                    'steps': [
                        {'range': [0, max_value * 0.33], 'color': 'lightgray'},
                        {'range': [max_value * 0.33, max_value * 0.67], 'color': 'gray'}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': float(max_value * 0.9)
                    }
                }
            }],
            'layout': {
                'template': 'plotly_white',
                'height': 300
            }
        }
    
    def _generate_indicator(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate KPI indicator."""
        config = rec['config']
        y_cols = config.get('y_axis', [])
        agg = config.get('aggregation', 'sum')
        
        if not y_cols:
            return self._generate_default_chart(rec)
        
        y_col = y_cols[0]
        
        if agg == 'sum':
            value = self.df[y_col].sum()
        elif agg == 'mean':
            value = self.df[y_col].mean()
        elif agg == 'count':
            value = len(self.df)
        else:
            value = self.df[y_col].sum()
        
        return {
            'data': [{
                'type': 'indicator',
                'mode': 'number',
                'value': float(value),
                'title': {'text': rec['title']},
                'number': {'font': {'size': 48}}
            }],
            'layout': {
                'template': 'plotly_white',
                'height': 200
            }
        }
    
    def _generate_table(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data table."""
        # Sample first 100 rows
        df_sample = self.df.head(100)
        
        return {
            'data': [{
                'type': 'table',
                'header': {
                    'values': df_sample.columns.tolist(),
                    'fill': {'color': '#3b82f6'},
                    'font': {'color': 'white', 'size': 12},
                    'align': 'left'
                },
                'cells': {
                    'values': [df_sample[col].fillna('').astype(str).tolist() 
                              for col in df_sample.columns],
                    'fill': {'color': ['#f8f9fa', 'white']},
                    'align': 'left',
                    'font': {'size': 11}
                }
            }],
            'layout': {
                'title': rec['title'],
                'template': 'plotly_white',
                'height': 600
            }
        }
    
    def _generate_default_chart(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate default placeholder chart."""
        return {
            'data': [{
                'type': 'scatter',
                'x': [1, 2, 3],
                'y': [1, 2, 3],
                'mode': 'markers',
                'marker': {'size': 0}
            }],
            'layout': {
                'title': f"{rec['title']} (Configuration needed)",
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'template': 'plotly_white',
                'annotations': [{
                    'text': 'Chart configuration incomplete',
                    'xref': 'paper',
                    'yref': 'paper',
                    'x': 0.5,
                    'y': 0.5,
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            }
        }
