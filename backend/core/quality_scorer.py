"""
QualityScorer - Evaluates dataset quality across multiple dimensions.

This module assesses data quality through:
- Completeness: Percentage of non-null values
- Validity: Conformance to expected types and patterns
- Consistency: Uniformity of formats and values
- Uniqueness: Appropriate levels of duplication

Each dimension is scored 0.0 to 1.0, and an overall quality score is computed.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class QualityReport:
    """Comprehensive quality assessment report."""
    overall_score: float  # 0.0 to 1.0
    completeness: float
    validity: float
    consistency: float
    uniqueness: float
    issues: List[str]  # List of detected quality issues
    recommendations: List[str]  # Recommended actions


class QualityScorer:
    """Assesses data quality across multiple dimensions."""
    
    def __init__(self, df: pd.DataFrame, column_profiles: Dict[str, Dict[str, Any]] = None):
        """Initialize scorer with dataframe and optional column profiles."""
        self.df = df
        self.column_profiles = column_profiles or {}
    
    def assess_quality(self) -> QualityReport:
        """Perform comprehensive quality assessment."""
        completeness = self._assess_completeness()
        validity = self._assess_validity()
        consistency = self._assess_consistency()
        uniqueness = self._assess_uniqueness()
        
        # Calculate overall score (weighted average)
        overall = (
            completeness * 0.30 +  # 30% weight on completeness
            validity * 0.30 +       # 30% weight on validity
            consistency * 0.25 +    # 25% weight on consistency
            uniqueness * 0.15       # 15% weight on uniqueness
        )
        
        # Collect issues and recommendations
        issues = self._identify_issues(completeness, validity, consistency, uniqueness)
        recommendations = self._generate_recommendations(issues, completeness, validity, consistency, uniqueness)
        
        return QualityReport(
            overall_score=overall,
            completeness=completeness,
            validity=validity,
            consistency=consistency,
            uniqueness=uniqueness,
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_completeness(self) -> float:
        """Assess data completeness (0.0 to 1.0)."""
        if len(self.df) == 0:
            return 0.0
        
        # Calculate percentage of non-null values across all cells
        # Convert to int to avoid numpy boolean subtract errors
        total_cells = int(self.df.size)
        null_cells = int(self.df.isna().sum().sum())
        non_null_cells = total_cells - null_cells
        completeness = non_null_cells / total_cells if total_cells > 0 else 0.0
        
        return float(completeness)
    
    def _assess_validity(self) -> float:
        """Assess data validity (conformance to expected types/patterns)."""
        if len(self.df) == 0:
            return 0.0
        
        validity_scores = []
        
        for column in self.df.columns:
            series = self.df[column].dropna()
            if len(series) == 0:
                continue
            
            col_validity = 1.0
            
            # Check for type consistency
            if series.dtype == object:
                # For object columns, check if values can be parsed consistently
                # Try to infer if it should be numeric or datetime
                numeric_parse_success = 0
                for val in series.head(100):
                    try:
                        float(str(val))
                        numeric_parse_success += 1
                    except (ValueError, TypeError):
                        pass
                
                # If most values look numeric but column is object, mark as validity issue
                if numeric_parse_success / min(len(series), 100) > 0.8:
                    col_validity *= 0.8  # Could be numeric but stored as object
            
            # Check for outliers in numeric columns (skip boolean columns)
            if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
                # Convert quantiles to float to avoid numpy boolean issues
                q1 = float(series.quantile(0.25))
                q3 = float(series.quantile(0.75))
                iqr = q3 - q1
                outlier_mask = (series < q1 - 3 * iqr) | (series > q3 + 3 * iqr)
                outlier_count = int(outlier_mask.sum())
                outlier_ratio = outlier_count / len(series)
                
                # Penalize heavily for extreme outliers (>5% of data)
                if outlier_ratio > 0.05:
                    col_validity *= (1 - outlier_ratio * 0.5)
            
            # Check for invalid patterns (e.g., negative values in age/count columns)
            # Skip boolean columns
            if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
                col_lower = column.lower()
                if any(keyword in col_lower for keyword in ['age', 'count', 'quantity', 'qty']):
                    # Convert to int to avoid numpy boolean subtract errors
                    negative_count = int((series < 0).sum())
                    if negative_count > 0:
                        col_validity *= max(0.5, 1 - negative_count / len(series))
            
            validity_scores.append(col_validity)
        
        return float(np.mean(validity_scores)) if validity_scores else 1.0
    
    def _assess_consistency(self) -> float:
        """Assess data consistency (format uniformity)."""
        if len(self.df) == 0:
            return 0.0
        
        consistency_scores = []
        
        for column in self.df.columns:
            series = self.df[column].dropna()
            if len(series) == 0:
                continue
            
            col_consistency = 1.0
            
            # Check string format consistency
            if series.dtype == object:
                # Check for mixed case
                if len(series) > 0:
                    str_series = series.astype(str)
                    # Convert .any() results to bool to avoid numpy boolean subtract errors
                    has_upper = bool(str_series.str.isupper().any())
                    has_lower = bool(str_series.str.islower().any())
                    has_title = bool(str_series.str.istitle().any())
                    
                    # Penalize if mixed casing patterns exist
                    case_patterns = sum([has_upper, has_lower, has_title])
                    if case_patterns > 1:
                        col_consistency *= 0.9
                    
                    # Check for leading/trailing whitespace
                    has_whitespace = bool((str_series.str.len() != str_series.str.strip().str.len()).any())
                    if has_whitespace:
                        col_consistency *= 0.95
                    
                    # Check for consistent delimiters in IDs or codes
                    if any(keyword in column.lower() for keyword in ['id', 'code', 'key']):
                        # Sample values to check for delimiter consistency
                        sample = str_series.head(50)
                        has_dash = bool(sample.str.contains('-', regex=False).any())
                        has_underscore = bool(sample.str.contains('_', regex=False).any())
                        has_space = bool(sample.str.contains(' ', regex=False).any())
                        
                        delimiter_patterns = sum([has_dash, has_underscore, has_space])
                        if delimiter_patterns > 1:
                            col_consistency *= 0.85
            
            # Check numeric format consistency (decimal places)
            # Skip boolean columns
            if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
                if series.dtype == float:
                    # Check for consistent decimal places
                    decimal_places = series.apply(lambda x: len(str(x).split('.')[-1]) if '.' in str(x) else 0)
                    decimal_std = float(decimal_places.std()) if len(decimal_places) > 1 else 0.0
                    if decimal_std > 2:  # High variance in decimal places
                        col_consistency *= 0.95
            
            consistency_scores.append(col_consistency)
        
        return float(np.mean(consistency_scores)) if consistency_scores else 1.0
    
    def _assess_uniqueness(self) -> float:
        """Assess appropriateness of uniqueness levels."""
        if len(self.df) == 0:
            return 0.0
        
        uniqueness_scores = []
        
        for column in self.df.columns:
            series = self.df[column].dropna()
            if len(series) == 0:
                continue
            
            col_uniqueness = 1.0
            # Convert nunique to int to avoid numpy boolean subtract errors
            nunique = int(series.nunique())
            uniqueness_ratio = nunique / len(series)
            col_lower = column.lower()
            
            # Check if ID columns are truly unique
            if any(keyword in col_lower for keyword in ['id', '_id', 'key', 'identifier']):
                if uniqueness_ratio < 0.99:  # ID should be nearly 100% unique
                    col_uniqueness *= uniqueness_ratio
            
            # Check for suspicious duplication in non-categorical columns
            # Skip boolean columns
            elif pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
                # Numeric columns shouldn't have too much duplication (unless counts/flags)
                if uniqueness_ratio < 0.1 and len(series) > 100:
                    # Unless it's a flag/status column
                    if nunique > 2:  # Not a binary flag
                        col_uniqueness *= 0.8
            
            # Check for over-duplication in categorical columns
            elif series.dtype == object:
                # Categorical shouldn't be all unique (would be an ID)
                if uniqueness_ratio > 0.95 and len(series) > 100:
                    col_uniqueness *= 0.9
            
            uniqueness_scores.append(col_uniqueness)
        
        return float(np.mean(uniqueness_scores)) if uniqueness_scores else 1.0
    
    def _identify_issues(self, completeness: float, validity: float, 
                        consistency: float, uniqueness: float) -> List[str]:
        """Identify specific quality issues."""
        issues = []
        
        # Completeness issues
        if completeness < 0.7:
            missing_pct = (1 - completeness) * 100
            issues.append(f"Significant missing data: {missing_pct:.1f}% of values are null")
        
        # Find columns with high null rates
        for column in self.df.columns:
            null_count = int(self.df[column].isna().sum())
            null_pct = null_count / len(self.df)
            if null_pct > 0.3:
                issues.append(f"Column '{column}' has {null_pct*100:.1f}% missing values")
        
        # Validity issues
        if validity < 0.8:
            issues.append("Data validity concerns: some values may be outliers or incorrect types")
        
        # Consistency issues
        if consistency < 0.85:
            issues.append("Format inconsistencies detected: mixed casing, whitespace, or delimiter patterns")
        
        # Uniqueness issues
        if uniqueness < 0.8:
            issues.append("Uniqueness issues: potential problems with ID columns or unexpected duplication")
        
        # Check for duplicated rows
        dup_rows = int(self.df.duplicated().sum())
        if dup_rows > 0:
            dup_pct = (dup_rows / len(self.df)) * 100
            issues.append(f"{dup_rows} duplicate rows found ({dup_pct:.1f}% of dataset)")
        
        return issues
    
    def _generate_recommendations(self, issues: List[str], completeness: float, 
                                 validity: float, consistency: float, 
                                 uniqueness: float) -> List[str]:
        """Generate recommendations based on quality assessment."""
        recommendations = []
        
        # Completeness recommendations
        if completeness < 0.9:
            recommendations.append("Address missing data using appropriate imputation strategies")
            if completeness < 0.7:
                recommendations.append("Consider removing columns with >50% missing values")
        
        # Validity recommendations
        if validity < 0.9:
            recommendations.append("Investigate and handle outliers in numeric columns")
            recommendations.append("Validate data types and convert where appropriate")
        
        # Consistency recommendations
        if consistency < 0.9:
            recommendations.append("Standardize text formats (case, whitespace, delimiters)")
            recommendations.append("Apply consistent formatting to ID and code columns")
        
        # Uniqueness recommendations
        if uniqueness < 0.9:
            recommendations.append("Verify uniqueness constraints on ID columns")
            recommendations.append("Remove or investigate duplicate records")
        
        # General recommendations
        if any([completeness < 0.8, validity < 0.8, consistency < 0.8, uniqueness < 0.8]):
            recommendations.append("Perform thorough data cleaning before analysis")
            recommendations.append("Document all data quality issues for stakeholders")
        
        return recommendations
