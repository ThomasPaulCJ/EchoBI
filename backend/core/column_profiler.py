"""
ColumnProfiler - Analyzes dataset columns for type detection, statistics, and quality metrics.

This module provides comprehensive column profiling capabilities:
- Automatic type detection (numeric, categorical, datetime, boolean)
- Semantic type detection (currency, email, ID, etc.)
- Statistical analysis (mean, median, mode, std, min, max, quantiles)
- Distribution analysis (skewness, kurtosis)
- Quality metrics (completeness, uniqueness, validity)
- Top values and frequency distributions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class ColumnProfiler:
    """Profiles individual columns and entire datasets."""
    
    # Semantic type patterns
    CURRENCY_PATTERNS = [r'price', r'cost', r'amount', r'revenue', r'sales', r'salary', r'fee', r'balance']
    ID_PATTERNS = [r'id$', r'_id$', r'^id_', r'identifier', r'key$', r'code$']
    EMAIL_PATTERN = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    PHONE_PATTERN = r'^\+?[\d\s\-\(\)]{10,}$'
    DATE_KEYWORDS = ['date', 'time', 'timestamp', 'datetime', 'day', 'month', 'year']
    
    def __init__(self, df: pd.DataFrame):
        """Initialize profiler with a dataframe."""
        self.df = df
        self.profiles = {}
    
    def profile_all_columns(self) -> Dict[str, Dict[str, Any]]:
        """Profile all columns in the dataframe."""
        self.profiles = {}
        for column in self.df.columns:
            self.profiles[column] = self.profile_column(column)
        return self.profiles
    
    def profile_column(self, column: str) -> Dict[str, Any]:
        """Profile a single column with comprehensive statistics."""
        series = self.df[column]
        
        # Convert counts to int to avoid numpy boolean subtract errors
        missing_count = int(series.isna().sum())
        unique_count = int(series.nunique())
        
        profile = {
            'name': column,
            'type': self._detect_type(series),
            'semantic_type': self._detect_semantic_type(column, series),
            'is_key': self._is_potential_key(series),
            'total_count': len(series),
            'missing_count': missing_count,
            'missing_percent': missing_count / len(series) if len(series) > 0 else 0,
            'unique_count': unique_count,
            'uniqueness': unique_count / len(series) if len(series) > 0 else 0,
            'has_nulls': bool(series.isna().any()),
        }
        
        # Type-specific statistics
        if profile['type'] == 'numeric':
            profile.update(self._numeric_statistics(series))
        elif profile['type'] == 'categorical':
            profile.update(self._categorical_statistics(series))
        elif profile['type'] == 'datetime':
            profile.update(self._datetime_statistics(series))
        elif profile['type'] == 'boolean':
            profile.update(self._boolean_statistics(series))
        
        return profile
    
    def _detect_type(self, series: pd.Series) -> str:
        """Detect the primary type of a column."""
        # Remove nulls for type detection
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 'unknown'
        
        # Check for boolean
        if non_null.dtype == bool or set(non_null.unique()).issubset({0, 1, True, False, 'true', 'false', 'True', 'False'}):
            return 'boolean'
        
        # Check for numeric
        if pd.api.types.is_numeric_dtype(non_null):
            return 'numeric'
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(non_null):
            return 'datetime'
        
        # Try to parse as datetime
        if non_null.dtype == object:
            try:
                pd.to_datetime(non_null.head(100))
                return 'datetime'
            except (ValueError, TypeError):
                pass
        
        # Default to categorical
        return 'categorical'
    
    def _detect_semantic_type(self, column_name: str, series: pd.Series) -> Optional[str]:
        """Detect semantic type based on column name and values."""
        column_lower = column_name.lower()
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return None
        
        # Check for ID
        for pattern in self.ID_PATTERNS:
            if re.search(pattern, column_lower):
                return 'identifier'
        
        # Check for currency
        for pattern in self.CURRENCY_PATTERNS:
            if re.search(pattern, column_lower):
                return 'currency'
        
        # Check for email
        if non_null.dtype == object:
            sample = non_null.head(20).astype(str)
            # Convert to int to avoid numpy boolean subtract errors
            if int(sample.str.match(self.EMAIL_PATTERN).sum()) / len(sample) > 0.8:
                return 'email'
            
            # Check for phone
            if int(sample.str.match(self.PHONE_PATTERN).sum()) / len(sample) > 0.8:
                return 'phone'
        
        # Check for date keywords
        for keyword in self.DATE_KEYWORDS:
            if keyword in column_lower:
                return 'temporal'
        
        return None
    
    def _is_potential_key(self, series: pd.Series) -> bool:
        """Check if column could be a primary key."""
        non_null = series.dropna()
        if len(non_null) == 0:
            return False
        
        # Must be unique and have no nulls - convert to int/bool for comparisons
        return int(series.nunique()) == len(series) and not bool(series.isna().any())
    
    def _numeric_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for numeric columns."""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return {}
        
        stats = {
            'mean': float(non_null.mean()),
            'median': float(non_null.median()),
            'mode': float(non_null.mode().iloc[0]) if len(non_null.mode()) > 0 else None,
            'std': float(non_null.std()),
            'min': float(non_null.min()),
            'max': float(non_null.max()),
            'q25': float(non_null.quantile(0.25)),
            'q75': float(non_null.quantile(0.75)),
            'skewness': float(non_null.skew()) if len(non_null) > 2 else None,
            'kurtosis': float(non_null.kurtosis()) if len(non_null) > 3 else None,
        }
        
        # Detect outliers using IQR method
        iqr = stats['q75'] - stats['q25']
        lower_bound = stats['q25'] - 1.5 * iqr
        upper_bound = stats['q75'] + 1.5 * iqr
        outliers = non_null[(non_null < lower_bound) | (non_null > upper_bound)]
        stats['outlier_count'] = len(outliers)
        stats['outlier_percent'] = len(outliers) / len(non_null)
        
        return stats
    
    def _categorical_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for categorical columns."""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return {}
        
        value_counts = non_null.value_counts()
        top_values = []
        
        for value, count in value_counts.head(10).items():
            top_values.append({
                'value': str(value),
                'count': int(count),
                'percent': float(count / len(non_null))
            })
        
        return {
            'mode': str(value_counts.index[0]) if len(value_counts) > 0 else None,
            'mode_frequency': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            'top_values': top_values,
            'cardinality': len(value_counts),
        }
    
    def _datetime_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for datetime columns."""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return {}
        
        # Try to convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(non_null):
            try:
                non_null = pd.to_datetime(non_null)
            except:
                return {}
        
        return {
            'min_date': non_null.min().isoformat() if hasattr(non_null.min(), 'isoformat') else str(non_null.min()),
            'max_date': non_null.max().isoformat() if hasattr(non_null.max(), 'isoformat') else str(non_null.max()),
            'date_range_days': (non_null.max() - non_null.min()).days if hasattr(non_null.max() - non_null.min(), 'days') else None,
        }
    
    def _boolean_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for boolean columns."""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return {}
        
        # Convert to boolean if needed
        if non_null.dtype != bool:
            non_null = non_null.astype(bool)
        
        # Convert to int to avoid numpy boolean subtract error
        true_count = int(non_null.sum())
        false_count = len(non_null) - true_count
        
        return {
            'true_count': true_count,
            'false_count': false_count,
            'true_percent': float(true_count / len(non_null)),
            'false_percent': float(false_count / len(non_null)),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall dataset summary."""
        if not self.profiles:
            self.profile_all_columns()
        
        numeric_cols = [col for col, profile in self.profiles.items() if profile['type'] == 'numeric']
        categorical_cols = [col for col, profile in self.profiles.items() if profile['type'] == 'categorical']
        datetime_cols = [col for col, profile in self.profiles.items() if profile['type'] == 'datetime']
        
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'numeric_columns': len(numeric_cols),
            'categorical_columns': len(categorical_cols),
            'datetime_columns': len(datetime_cols),
            'columns_with_nulls': sum(1 for p in self.profiles.values() if p['has_nulls']),
            'potential_keys': [col for col, profile in self.profiles.items() if profile['is_key']],
        }
