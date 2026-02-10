"""
Relationship Detector - Advanced relationship and correlation detection for EchoBI v2.0

This module provides sophisticated relationship detection including:
- Numeric correlations (Pearson, Spearman)
- Categorical associations (Cramér's V, chi-square)
- Foreign key detection
- Hierarchical relationships
- Functional dependencies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from scipy import stats
from itertools import combinations


@dataclass
class Relationship:
    """Represents a detected relationship between columns."""
    column1: str
    column2: str
    type: str  # 'correlation', 'association', 'foreign_key', 'hierarchy', 'functional_dependency'
    strength: float  # 0.0 to 1.0
    direction: Optional[str] = None  # 'positive', 'negative', 'bidirectional', None
    details: Optional[Dict[str, Any]] = None
    confidence: float = 1.0


class RelationshipDetector:
    """
    Detects and analyzes relationships between columns in a dataset.
    
    Capabilities:
    - Numeric correlations (Pearson, Spearman)
    - Categorical associations (Cramér's V)
    - Primary/foreign key relationships
    - Hierarchical dependencies
    - Functional dependencies
    """
    
    def __init__(self, df: pd.DataFrame, column_profiles: Dict[str, Dict[str, Any]]):
        """
        Initialize relationship detector.
        
        Args:
            df: The dataframe to analyze
            column_profiles: Column profiles from ColumnProfiler
        """
        self.df = df
        self.column_profiles = column_profiles
        self.relationships: List[Relationship] = []
        
        # Categorize columns by type
        self.numeric_cols = [col for col, profile in column_profiles.items() 
                            if profile.get('type') == 'numeric']
        self.categorical_cols = [col for col, profile in column_profiles.items() 
                                if profile.get('type') == 'categorical']
        self.datetime_cols = [col for col, profile in column_profiles.items() 
                             if profile.get('type') == 'datetime']
    
    def detect_all_relationships(self) -> List[Relationship]:
        """
        Detect all types of relationships in the dataset.
        
        Returns:
            List of detected relationships
        """
        self.relationships = []
        
        # Numeric correlations
        if len(self.numeric_cols) >= 2:
            self.relationships.extend(self._detect_numeric_correlations())
        
        # Categorical associations
        if len(self.categorical_cols) >= 2:
            self.relationships.extend(self._detect_categorical_associations())
        
        # Foreign key relationships
        self.relationships.extend(self._detect_foreign_keys())
        
        # Hierarchical relationships
        self.relationships.extend(self._detect_hierarchies())
        
        # Functional dependencies
        self.relationships.extend(self._detect_functional_dependencies())
        
        # Mixed type relationships (numeric-categorical)
        self.relationships.extend(self._detect_mixed_relationships())
        
        return self.relationships
    
    def _detect_numeric_correlations(self) -> List[Relationship]:
        """Detect correlations between numeric columns."""
        correlations = []
        
        # Pearson correlation
        try:
            corr_matrix = self.df[self.numeric_cols].corr(method='pearson')
            
            for col1, col2 in combinations(self.numeric_cols, 2):
                corr_value = corr_matrix.loc[col1, col2]
                
                if pd.notna(corr_value) and abs(corr_value) > 0.3:
                    # Calculate p-value for significance
                    _, p_value = stats.pearsonr(
                        self.df[col1].dropna(),
                        self.df[col2].dropna()
                    )
                    
                    correlations.append(Relationship(
                        column1=col1,
                        column2=col2,
                        type='correlation',
                        strength=abs(corr_value),
                        direction='positive' if corr_value > 0 else 'negative',
                        details={
                            'method': 'pearson',
                            'value': float(corr_value),
                            'p_value': float(p_value),
                            'significant': p_value < 0.05,
                            'interpretation': self._interpret_correlation(abs(corr_value))
                        },
                        confidence=1.0 - p_value if p_value < 0.05 else 0.5
                    ))
        except Exception as e:
            pass  # Skip if correlation calculation fails
        
        # Spearman correlation (for non-linear relationships)
        try:
            spearman_matrix = self.df[self.numeric_cols].corr(method='spearman')
            
            for col1, col2 in combinations(self.numeric_cols, 2):
                spearman_value = spearman_matrix.loc[col1, col2]
                pearson_value = corr_matrix.loc[col1, col2] if col1 in corr_matrix.columns else 0
                
                # If Spearman is significantly higher than Pearson, there's a non-linear relationship
                if pd.notna(spearman_value) and abs(spearman_value) > 0.4:
                    if abs(spearman_value) - abs(pearson_value) > 0.15:
                        _, p_value = stats.spearmanr(
                            self.df[col1].dropna(),
                            self.df[col2].dropna()
                        )
                        
                        correlations.append(Relationship(
                            column1=col1,
                            column2=col2,
                            type='correlation',
                            strength=abs(spearman_value),
                            direction='positive' if spearman_value > 0 else 'negative',
                            details={
                                'method': 'spearman',
                                'value': float(spearman_value),
                                'p_value': float(p_value),
                                'non_linear': True,
                                'interpretation': 'Non-linear monotonic relationship'
                            },
                            confidence=1.0 - p_value if p_value < 0.05 else 0.5
                        ))
        except Exception:
            pass
        
        return correlations
    
    def _detect_categorical_associations(self) -> List[Relationship]:
        """Detect associations between categorical columns using Cramér's V."""
        associations = []
        
        for col1, col2 in combinations(self.categorical_cols, 2):
            try:
                # Create contingency table
                contingency = pd.crosstab(self.df[col1], self.df[col2])
                
                # Chi-square test
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
                
                # Cramér's V
                n = contingency.sum().sum()
                min_dim = min(contingency.shape) - 1
                cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
                
                if cramers_v > 0.3 and p_value < 0.05:
                    associations.append(Relationship(
                        column1=col1,
                        column2=col2,
                        type='association',
                        strength=cramers_v,
                        direction='bidirectional',
                        details={
                            'method': 'cramers_v',
                            'value': float(cramers_v),
                            'chi2': float(chi2),
                            'p_value': float(p_value),
                            'significant': p_value < 0.05,
                            'interpretation': self._interpret_association(cramers_v)
                        },
                        confidence=1.0 - p_value
                    ))
            except Exception:
                continue
        
        return associations
    
    def _detect_foreign_keys(self) -> List[Relationship]:
        """Detect potential foreign key relationships."""
        foreign_keys = []
        
        # Look for columns that might be foreign keys
        # Characteristics: high uniqueness in one table, referenced values in another
        
        for col1 in self.categorical_cols:
            profile1 = self.column_profiles[col1]
            
            # Potential primary key: high uniqueness
            if profile1.get('uniqueness', 0) > 0.95:
                for col2 in self.categorical_cols:
                    if col1 == col2:
                        continue
                    
                    profile2 = self.column_profiles[col2]
                    
                    # Check if col2 values are subset of col1 values
                    values1 = set(self.df[col1].dropna().unique())
                    values2 = set(self.df[col2].dropna().unique())
                    
                    if values2.issubset(values1) and len(values2) > 0:
                        overlap_ratio = len(values2) / len(values1) if len(values1) > 0 else 0
                        
                        if overlap_ratio > 0.3:  # At least 30% overlap
                            foreign_keys.append(Relationship(
                                column1=col2,  # Foreign key
                                column2=col1,  # Primary key
                                type='foreign_key',
                                strength=overlap_ratio,
                                direction='references',
                                details={
                                    'foreign_key': col2,
                                    'primary_key': col1,
                                    'overlap_ratio': overlap_ratio,
                                    'interpretation': f'{col2} references {col1}'
                                },
                                confidence=overlap_ratio
                            ))
        
        return foreign_keys
    
    def _detect_hierarchies(self) -> List[Relationship]:
        """Detect hierarchical relationships (e.g., category -> subcategory)."""
        hierarchies = []
        
        for col1, col2 in combinations(self.categorical_cols, 2):
            try:
                # Check if col1 groups col2 (one-to-many relationship)
                grouped = self.df.groupby(col1)[col2].nunique()
                avg_children = grouped.mean()
                max_children = grouped.max()
                
                # Check reverse direction
                grouped_reverse = self.df.groupby(col2)[col1].nunique()
                # Convert to int to avoid numpy boolean subtract errors
                parent_uniqueness = int((grouped_reverse == 1).sum()) / len(grouped_reverse)
                
                # Hierarchy detected if:
                # - Each col1 value maps to multiple col2 values (one-to-many)
                # - Each col2 value maps to exactly one col1 value (many-to-one)
                if avg_children > 1.5 and parent_uniqueness > 0.8:
                    hierarchies.append(Relationship(
                        column1=col1,  # Parent
                        column2=col2,  # Child
                        type='hierarchy',
                        strength=min(parent_uniqueness, avg_children / max_children),
                        direction='parent_to_child',
                        details={
                            'parent': col1,
                            'child': col2,
                            'avg_children_per_parent': float(avg_children),
                            'parent_uniqueness': float(parent_uniqueness),
                            'interpretation': f'{col1} is parent of {col2} (one-to-many)'
                        },
                        confidence=parent_uniqueness
                    ))
            except Exception:
                continue
        
        return hierarchies
    
    def _detect_functional_dependencies(self) -> List[Relationship]:
        """Detect functional dependencies (X -> Y, where X determines Y)."""
        dependencies = []
        
        # Test if column A uniquely determines column B
        for col1, col2 in combinations(self.categorical_cols + self.numeric_cols, 2):
            if col1 == col2:
                continue
            
            try:
                # Group by col1 and check if col2 is constant within each group
                grouped = self.df.groupby(col1)[col2].nunique()
                # Convert to int to avoid numpy boolean subtract errors
                dependency_ratio = int((grouped == 1).sum()) / len(grouped) if len(grouped) > 0 else 0
                
                if dependency_ratio > 0.95:  # 95% functional dependency
                    dependencies.append(Relationship(
                        column1=col1,
                        column2=col2,
                        type='functional_dependency',
                        strength=dependency_ratio,
                        direction='determines',
                        details={
                            'determinant': col1,
                            'dependent': col2,
                            'dependency_ratio': float(dependency_ratio),
                            'interpretation': f'{col1} functionally determines {col2}'
                        },
                        confidence=dependency_ratio
                    ))
            except Exception:
                continue
        
        return dependencies
    
    def _detect_mixed_relationships(self) -> List[Relationship]:
        """Detect relationships between numeric and categorical columns."""
        mixed_relationships = []
        
        for num_col in self.numeric_cols:
            for cat_col in self.categorical_cols:
                try:
                    # ANOVA F-test to check if categorical variable affects numeric variable
                    groups = [group[num_col].dropna() for name, group in self.df.groupby(cat_col)]
                    
                    if len(groups) >= 2 and all(len(g) > 0 for g in groups):
                        f_stat, p_value = stats.f_oneway(*groups)
                        
                        if p_value < 0.05:  # Significant relationship
                            # Calculate effect size (eta-squared)
                            grand_mean = self.df[num_col].mean()
                            ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
                            ss_total = ((self.df[num_col] - grand_mean)**2).sum()
                            eta_squared = ss_between / ss_total if ss_total > 0 else 0
                            
                            mixed_relationships.append(Relationship(
                                column1=cat_col,
                                column2=num_col,
                                type='categorical_numeric',
                                strength=eta_squared,
                                direction='affects',
                                details={
                                    'method': 'ANOVA',
                                    'f_statistic': float(f_stat),
                                    'p_value': float(p_value),
                                    'eta_squared': float(eta_squared),
                                    'interpretation': f'{cat_col} significantly affects {num_col}',
                                    'effect_size': self._interpret_effect_size(eta_squared)
                                },
                                confidence=1.0 - p_value
                            ))
                except Exception:
                    continue
        
        return mixed_relationships
    
    def _interpret_correlation(self, abs_corr: float) -> str:
        """Interpret correlation strength."""
        if abs_corr >= 0.7:
            return 'Strong correlation'
        elif abs_corr >= 0.5:
            return 'Moderate correlation'
        elif abs_corr >= 0.3:
            return 'Weak correlation'
        else:
            return 'Very weak correlation'
    
    def _interpret_association(self, cramers_v: float) -> str:
        """Interpret Cramér's V association strength."""
        if cramers_v >= 0.5:
            return 'Strong association'
        elif cramers_v >= 0.3:
            return 'Moderate association'
        elif cramers_v >= 0.1:
            return 'Weak association'
        else:
            return 'Very weak association'
    
    def _interpret_effect_size(self, eta_squared: float) -> str:
        """Interpret eta-squared effect size."""
        if eta_squared >= 0.14:
            return 'Large effect'
        elif eta_squared >= 0.06:
            return 'Medium effect'
        elif eta_squared >= 0.01:
            return 'Small effect'
        else:
            return 'Negligible effect'
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all detected relationships."""
        if not self.relationships:
            self.detect_all_relationships()
        
        return {
            'total_relationships': len(self.relationships),
            'by_type': {
                'correlations': len([r for r in self.relationships if r.type == 'correlation']),
                'associations': len([r for r in self.relationships if r.type == 'association']),
                'foreign_keys': len([r for r in self.relationships if r.type == 'foreign_key']),
                'hierarchies': len([r for r in self.relationships if r.type == 'hierarchy']),
                'functional_dependencies': len([r for r in self.relationships if r.type == 'functional_dependency']),
                'mixed_relationships': len([r for r in self.relationships if r.type == 'categorical_numeric'])
            },
            'strong_relationships': len([r for r in self.relationships if r.strength > 0.7]),
            'moderate_relationships': len([r for r in self.relationships if 0.4 <= r.strength <= 0.7]),
            'weak_relationships': len([r for r in self.relationships if r.strength < 0.4])
        }
    
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert relationships to list of dictionaries for JSON serialization."""
        return [
            {
                'column1': r.column1,
                'column2': r.column2,
                'type': r.type,
                'strength': float(r.strength),
                'direction': r.direction,
                'details': r.details,
                'confidence': float(r.confidence)
            }
            for r in self.relationships
        ]
