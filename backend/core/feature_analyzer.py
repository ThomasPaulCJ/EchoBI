"""
Feature Analyzer - Advanced feature importance and semantic analysis for EchoBI v2.0

This module provides sophisticated feature analysis including:
- Feature importance scoring
- Advanced semantic type detection
- Pattern recognition
- Business context inference
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import re
from collections import Counter


@dataclass
class Feature:
    """Represents an analyzed feature with importance and metadata."""
    name: str
    importance: float  # 0.0 to 1.0
    semantic_type: str
    business_context: Optional[str]
    patterns: List[str]
    recommendations: List[str]
    quality_issues: List[str]


class FeatureAnalyzer:
    """
    Analyzes features for importance, semantic types, and business context.
    
    Capabilities:
    - Feature importance scoring based on multiple criteria
    - Advanced semantic type detection
    - Pattern recognition in data
    - Business context inference
    - Quality issue identification
    """
    
    # Extended semantic type patterns
    SEMANTIC_PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$',
        'url': r'^https?://[^\s]+$',
        'ip_address': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
        'credit_card': r'^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$',
        'ssn': r'^\d{3}-\d{2}-\d{4}$',
        'zip_code': r'^\d{5}(-\d{4})?$',
        'isbn': r'^(?:ISBN(?:-1[03])?:?\s)?(?=[0-9X]{10}$|(?=(?:[0-9]+[-\s]){3})[-\s0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[-\s]){4})[-\s0-9]{17}$)(?:97[89][-\s]?)?[0-9]{1,5}[-\s]?[0-9]+[-\s]?[0-9]+[-\s]?[0-9X]$',
        'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        'hex_color': r'^#?([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})$',
        'mac_address': r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
    }
    
    # Business context keywords
    BUSINESS_CONTEXTS = {
        'customer': ['customer', 'client', 'user', 'account', 'member'],
        'product': ['product', 'item', 'sku', 'inventory', 'stock'],
        'transaction': ['transaction', 'order', 'purchase', 'payment', 'invoice'],
        'financial': ['amount', 'price', 'cost', 'revenue', 'profit', 'balance'],
        'temporal': ['date', 'time', 'timestamp', 'created', 'updated', 'modified'],
        'location': ['address', 'city', 'state', 'country', 'zip', 'location', 'region'],
        'identity': ['id', 'key', 'code', 'number', 'identifier'],
        'contact': ['email', 'phone', 'contact', 'address'],
        'measurement': ['weight', 'height', 'length', 'width', 'size', 'quantity'],
        'status': ['status', 'state', 'flag', 'active', 'enabled']
    }
    
    def __init__(self, df: pd.DataFrame, column_profiles: Dict[str, Dict[str, Any]], 
                 dataset_type: Optional[str] = None):
        """
        Initialize feature analyzer.
        
        Args:
            df: The dataframe to analyze
            column_profiles: Column profiles from ColumnProfiler
            dataset_type: Optional dataset type from DatasetClassifier
        """
        self.df = df
        self.column_profiles = column_profiles
        self.dataset_type = dataset_type
        self.features: List[Feature] = []
    
    def analyze_all_features(self) -> List[Feature]:
        """
        Analyze all features in the dataset.
        
        Returns:
            List of analyzed features with importance scores
        """
        self.features = []
        
        for col_name, profile in self.column_profiles.items():
            importance = self._calculate_importance(col_name, profile)
            semantic_type = self._detect_advanced_semantic_type(col_name, profile)
            business_context = self._infer_business_context(col_name, profile)
            patterns = self._detect_patterns(col_name, profile)
            recommendations = self._generate_recommendations(col_name, profile, patterns)
            quality_issues = self._identify_quality_issues(col_name, profile)
            
            self.features.append(Feature(
                name=col_name,
                importance=importance,
                semantic_type=semantic_type,
                business_context=business_context,
                patterns=patterns,
                recommendations=recommendations,
                quality_issues=quality_issues
            ))
        
        # Sort by importance
        self.features.sort(key=lambda f: f.importance, reverse=True)
        
        return self.features
    
    def _calculate_importance(self, col_name: str, profile: Dict[str, Any]) -> float:
        """
        Calculate feature importance based on multiple criteria.
        
        Criteria:
        - Uniqueness (high uniqueness = potential key)
        - Completeness (fewer missing values = more important)
        - Cardinality (moderate cardinality = good for analysis)
        - Semantic significance (IDs, keys, amounts)
        - Column name semantics
        """
        importance_score = 0.0
        
        # 1. Key/ID columns are highly important (25%)
        if profile.get('is_key', False) or profile.get('semantic_type') == 'identifier':
            importance_score += 0.25
        
        # 2. Completeness (20%) - more complete = more important
        completeness = 1.0 - profile.get('missing_percent', 0) / 100
        importance_score += completeness * 0.20
        
        # 3. Uniqueness factor (15%)
        uniqueness = profile.get('uniqueness', 0)
        if 0.7 <= uniqueness <= 1.0:  # High uniqueness (keys)
            importance_score += 0.15
        elif 0.1 <= uniqueness <= 0.7:  # Good variety
            importance_score += 0.10
        
        # 4. Semantic importance (20%)
        semantic_type = profile.get('semantic_type', '')
        if semantic_type in ['currency', 'percentage']:
            importance_score += 0.20
        elif semantic_type in ['identifier', 'email', 'phone']:
            importance_score += 0.15
        
        # 5. Column name importance (10%)
        name_lower = col_name.lower()
        important_keywords = ['id', 'amount', 'price', 'revenue', 'profit', 'customer', 
                             'user', 'date', 'time', 'status', 'type', 'category']
        if any(keyword in name_lower for keyword in important_keywords):
            importance_score += 0.10
        
        # 6. Data type importance (10%)
        col_type = profile.get('type', '')
        if col_type == 'numeric':
            importance_score += 0.10
        elif col_type == 'datetime':
            importance_score += 0.08
        elif col_type == 'categorical':
            # Categorical with good cardinality
            cardinality = profile.get('cardinality', 0)
            if 2 <= cardinality <= 50:
                importance_score += 0.05
        
        return min(importance_score, 1.0)
    
    def _detect_advanced_semantic_type(self, col_name: str, profile: Dict[str, Any]) -> str:
        """Detect advanced semantic types using pattern matching."""
        # Check if basic semantic type already detected
        existing_semantic = profile.get('semantic_type')
        if existing_semantic and existing_semantic != 'unknown':
            return existing_semantic
        
        # Sample values for pattern matching
        col_data = self.df[col_name].dropna()
        if len(col_data) == 0:
            return 'unknown'
        
        sample = col_data.head(100).astype(str)
        
        # Test each pattern
        for semantic_type, pattern in self.SEMANTIC_PATTERNS.items():
            try:
                matches = sample.str.match(pattern, case=False)
                # Convert to int to avoid numpy boolean subtract errors
                match_ratio = int(matches.sum()) / len(sample)
                
                if match_ratio > 0.7:  # 70% match threshold
                    return semantic_type
            except Exception:
                continue
        
        # Name-based inference
        name_lower = col_name.lower()
        
        if any(word in name_lower for word in ['email', 'e-mail', 'mail']):
            return 'email'
        elif any(word in name_lower for word in ['phone', 'tel', 'mobile', 'cell']):
            return 'phone'
        elif any(word in name_lower for word in ['url', 'link', 'website']):
            return 'url'
        elif any(word in name_lower for word in ['zip', 'postal', 'postcode']):
            return 'zip_code'
        elif any(word in name_lower for word in ['ssn', 'social']):
            return 'ssn'
        elif 'ip' in name_lower:
            return 'ip_address'
        elif any(word in name_lower for word in ['uuid', 'guid']):
            return 'uuid'
        elif 'color' in name_lower or 'colour' in name_lower:
            return 'hex_color'
        elif 'mac' in name_lower:
            return 'mac_address'
        
        return profile.get('type', 'unknown')
    
    def _infer_business_context(self, col_name: str, profile: Dict[str, Any]) -> Optional[str]:
        """Infer business context from column name and data."""
        name_lower = col_name.lower()
        
        # Check each business context
        for context, keywords in self.BUSINESS_CONTEXTS.items():
            if any(keyword in name_lower for keyword in keywords):
                return context
        
        # Check by semantic type
        semantic_type = profile.get('semantic_type', '')
        if semantic_type == 'currency':
            return 'financial'
        elif semantic_type in ['email', 'phone']:
            return 'contact'
        elif semantic_type == 'identifier':
            return 'identity'
        
        return None
    
    def _detect_patterns(self, col_name: str, profile: Dict[str, Any]) -> List[str]:
        """Detect patterns in the data."""
        patterns = []
        col_data = self.df[col_name].dropna()
        
        if len(col_data) == 0:
            return patterns
        
        col_type = profile.get('type', '')
        
        # Numeric patterns
        if col_type == 'numeric':
            # Convert .any() and .sum() to Python types
            if bool((col_data < 0).any()):
                patterns.append('contains_negative_values')
            zero_ratio = int((col_data == 0).sum()) / len(col_data)
            if zero_ratio > 0.1:
                patterns.append('many_zeros')
            
            # Check for outliers
            q1 = float(col_data.quantile(0.25))
            q3 = float(col_data.quantile(0.75))
            iqr = q3 - q1
            # Convert to int to avoid numpy boolean subtract errors
            outliers = int(((col_data < q1 - 1.5 * iqr) | (col_data > q3 + 1.5 * iqr)).sum())
            if outliers > 0:
                patterns.append(f'outliers_detected_{outliers}')
            
            # Check for rounding
            if bool((col_data % 1 == 0).all()):
                patterns.append('integer_values_only')
            
            # Check for specific increments
            unique_diffs = col_data.diff().dropna().unique()
            if len(unique_diffs) == 1 and not np.isnan(unique_diffs[0]):
                patterns.append(f'constant_increment_{unique_diffs[0]:.2f}')
        
        # Categorical patterns
        elif col_type == 'categorical':
            # Check for prefixes/suffixes
            str_data = col_data.astype(str)
            first_chars = str_data.str[0].value_counts()
            if len(first_chars) <= 5 and first_chars.iloc[0] / len(str_data) > 0.3:
                patterns.append(f'common_prefix_{first_chars.index[0]}')
            
            # Check for fixed length
            lengths = str_data.str.len()
            if lengths.nunique() == 1:
                patterns.append(f'fixed_length_{lengths.iloc[0]}')
            
            # Check for delimiters
            hyphen_ratio = int(str_data.str.contains('-').sum()) / len(str_data)
            if hyphen_ratio > 0.5:
                patterns.append('hyphen_delimited')
            underscore_ratio = int(str_data.str.contains('_').sum()) / len(str_data)
            if underscore_ratio > 0.5:
                patterns.append('underscore_delimited')
        
        # Datetime patterns
        elif col_type == 'datetime':
            try:
                dt_data = pd.to_datetime(col_data)
                
                # Check for weekday patterns
                weekday_dist = dt_data.dt.dayofweek.value_counts(normalize=True)
                if weekday_dist.max() > 0.3:
                    patterns.append('weekday_pattern')
                
                # Check for month patterns
                month_dist = dt_data.dt.month.value_counts(normalize=True)
                if month_dist.max() > 0.2:
                    patterns.append('seasonal_pattern')
                
                # Check for time patterns
                if hasattr(dt_data.dt, 'hour'):
                    hour_dist = dt_data.dt.hour.value_counts()
                    if len(hour_dist) <= 5:
                        patterns.append('specific_hours_only')
            except Exception:
                pass
        
        return patterns
    
    def _generate_recommendations(self, col_name: str, profile: Dict[str, Any], 
                                 patterns: List[str]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        col_type = profile.get('type', '')
        semantic_type = profile.get('semantic_type', '')
        
        # Missing values recommendations
        missing_pct = profile.get('missing_percent', 0)
        if missing_pct > 20:
            recommendations.append(f'High missing rate ({missing_pct:.1f}%) - consider imputation or removal')
        elif missing_pct > 5:
            recommendations.append(f'Moderate missing rate ({missing_pct:.1f}%) - review imputation strategy')
        
        # Uniqueness recommendations
        uniqueness = profile.get('uniqueness', 0)
        if uniqueness > 0.95 and not profile.get('is_key', False):
            recommendations.append('Very high uniqueness - consider as potential key/identifier')
        elif uniqueness < 0.01:
            recommendations.append('Very low uniqueness - consider dropping if not meaningful')
        
        # Type-specific recommendations
        if col_type == 'numeric':
            if 'outliers_detected' in str(patterns):
                recommendations.append('Outliers detected - review for data quality issues or cap/winsorize')
            if 'many_zeros' in patterns:
                recommendations.append('Many zero values - consider zero-inflation handling')
        
        elif col_type == 'categorical':
            cardinality = profile.get('cardinality', 0)
            if cardinality > 100:
                recommendations.append(f'High cardinality ({cardinality}) - consider grouping rare categories')
            elif cardinality == 2:
                recommendations.append('Binary categorical - good for encoding as 0/1')
        
        # Semantic type recommendations
        if semantic_type == 'email':
            recommendations.append('Email field - ensure privacy compliance (GDPR/CCPA)')
        elif semantic_type == 'phone':
            recommendations.append('Phone field - standardize format and ensure privacy compliance')
        elif semantic_type == 'currency':
            recommendations.append('Currency field - ensure consistent currency and decimal handling')
        
        return recommendations
    
    def _identify_quality_issues(self, col_name: str, profile: Dict[str, Any]) -> List[str]:
        """Identify data quality issues."""
        issues = []
        
        # Missing values
        missing_pct = profile.get('missing_percent', 0)
        if missing_pct > 50:
            issues.append(f'Critical: {missing_pct:.1f}% missing values')
        
        # Uniqueness issues
        uniqueness = profile.get('uniqueness', 0)
        total_count = profile.get('total_count', 0)
        if uniqueness == 0 and total_count > 1:
            issues.append('All values are identical - no variance')
        
        # Type-specific issues
        col_type = profile.get('type', '')
        if col_type == 'numeric':
            col_data = self.df[col_name].dropna()
            if len(col_data) > 0:
                # Convert .any() to bool to avoid numpy boolean subtract errors
                if bool(np.isinf(col_data).any()):
                    issues.append('Contains infinite values')
                if bool((col_data < 0).any()) and 'amount' in col_name.lower():
                    issues.append('Negative values in amount field')
        
        return issues
    
    def get_top_features(self, n: int = 10) -> List[Feature]:
        """Get top N most important features."""
        if not self.features:
            self.analyze_all_features()
        return self.features[:n]
    
    def get_features_by_context(self, context: str) -> List[Feature]:
        """Get features by business context."""
        if not self.features:
            self.analyze_all_features()
        return [f for f in self.features if f.business_context == context]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of feature analysis."""
        if not self.features:
            self.analyze_all_features()
        
        return {
            'total_features': len(self.features),
            'high_importance': len([f for f in self.features if f.importance > 0.7]),
            'medium_importance': len([f for f in self.features if 0.4 <= f.importance <= 0.7]),
            'low_importance': len([f for f in self.features if f.importance < 0.4]),
            'by_context': {
                context: len(self.get_features_by_context(context))
                for context in self.BUSINESS_CONTEXTS.keys()
                if len(self.get_features_by_context(context)) > 0
            },
            'total_quality_issues': sum(len(f.quality_issues) for f in self.features),
            'total_recommendations': sum(len(f.recommendations) for f in self.features)
        }
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert features to list of dictionaries for JSON serialization."""
        return [
            {
                'name': f.name,
                'importance': float(f.importance),
                'semantic_type': f.semantic_type,
                'business_context': f.business_context,
                'patterns': f.patterns,
                'recommendations': f.recommendations,
                'quality_issues': f.quality_issues
            }
            for f in self.features
        ]
