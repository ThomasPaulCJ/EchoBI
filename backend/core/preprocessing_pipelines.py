"""
Domain-Specific Preprocessing Pipelines for EchoBI v2.0

Provides specialized preprocessing for different dataset types:
- Financial: Currency normalization, transaction validation
- Sales: Product/customer data cleaning
- Time-Series: Temporal ordering, frequency handling
- Healthcare: Medical code validation, PHI handling
- Generic: Standard cleaning operations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from .preprocessing_engine import PreprocessingEngine, PreprocessingOperation
import re


class FinancialPipeline(PreprocessingEngine):
    """Preprocessing pipeline for financial datasets."""
    
    def suggest_operations(self) -> List[PreprocessingOperation]:
        """Generate financial-specific preprocessing suggestions."""
        suggestions = super().suggest_operations()
        operation_counter = len(suggestions)
        
        # Currency normalization
        for col_name, profile in self.column_profiles.items():
            if profile.get('semantic_type') == 'currency':
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="normalize_currency",
                    column=col_name,
                    description=f"Normalize currency format in {col_name}",
                    parameters={"remove_symbols": True, "decimal_places": 2}
                ))
                operation_counter += 1
        
        # Transaction date validation
        for col_name, profile in self.column_profiles.items():
            if profile.get('type') == 'datetime' and 'transaction' in col_name.lower():
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="validate_transaction_dates",
                    column=col_name,
                    description=f"Validate transaction dates in {col_name}",
                    parameters={"remove_future": True, "min_year": 2000}
                ))
                operation_counter += 1
        
        # Negative amount handling
        for col_name, profile in self.column_profiles.items():
            if profile.get('semantic_type') == 'currency' and 'amount' in col_name.lower():
                col_data = self.current_df[col_name].dropna()
                # Convert .any() to bool to avoid numpy boolean subtract errors
                if len(col_data) > 0 and bool((col_data < 0).any()):
                    suggestions.append(PreprocessingOperation(
                        operation_id=f"op_{operation_counter}",
                        operation_type="handle_negative_amounts",
                        column=col_name,
                        description=f"Review negative amounts in {col_name}",
                        parameters={"method": "flag", "absolute": False}
                    ))
                    operation_counter += 1
        
        return suggestions


class SalesPipeline(PreprocessingEngine):
    """Preprocessing pipeline for sales/retail datasets."""
    
    def suggest_operations(self) -> List[PreprocessingOperation]:
        """Generate sales-specific preprocessing suggestions."""
        suggestions = super().suggest_operations()
        operation_counter = len(suggestions)
        
        # Product ID standardization
        for col_name, profile in self.column_profiles.items():
            if 'product' in col_name.lower() and 'id' in col_name.lower():
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="standardize_product_ids",
                    column=col_name,
                    description=f"Standardize product IDs in {col_name}",
                    parameters={"uppercase": True, "remove_spaces": True}
                ))
                operation_counter += 1
        
        # Quantity validation
        for col_name, profile in self.column_profiles.items():
            if profile.get('type') == 'numeric' and any(kw in col_name.lower() for kw in ['quantity', 'qty', 'units']):
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="validate_quantities",
                    column=col_name,
                    description=f"Validate quantities in {col_name}",
                    parameters={"min_value": 0, "remove_zeros": False}
                ))
                operation_counter += 1
        
        # Customer email validation
        for col_name, profile in self.column_profiles.items():
            if profile.get('semantic_type') == 'email':
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="validate_emails",
                    column=col_name,
                    description=f"Validate email formats in {col_name}",
                    parameters={"remove_invalid": False, "flag_invalid": True}
                ))
                operation_counter += 1
        
        return suggestions


class TimeSeriesPipeline(PreprocessingEngine):
    """Preprocessing pipeline for time-series datasets."""
    
    def suggest_operations(self) -> List[PreprocessingOperation]:
        """Generate time-series specific preprocessing suggestions."""
        suggestions = super().suggest_operations()
        operation_counter = len(suggestions)
        
        # Temporal ordering
        datetime_cols = [col for col, profile in self.column_profiles.items() 
                        if profile.get('type') == 'datetime']
        
        if datetime_cols:
            primary_date_col = datetime_cols[0]
            suggestions.append(PreprocessingOperation(
                operation_id=f"op_{operation_counter}",
                operation_type="sort_by_datetime",
                column=primary_date_col,
                description=f"Sort dataset by {primary_date_col}",
                parameters={"ascending": True}
            ))
            operation_counter += 1
            
            # Fill missing timestamps
            suggestions.append(PreprocessingOperation(
                operation_id=f"op_{operation_counter}",
                operation_type="fill_missing_timestamps",
                column=primary_date_col,
                description=f"Fill missing timestamps in {primary_date_col}",
                parameters={"method": "forward_fill", "frequency": "infer"}
            ))
            operation_counter += 1
        
        # Smooth outliers in time series
        for col_name, profile in self.column_profiles.items():
            if profile.get('type') == 'numeric':
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="smooth_timeseries",
                    column=col_name,
                    description=f"Apply smoothing to {col_name}",
                    parameters={"method": "rolling_mean", "window": 3}
                ))
                operation_counter += 1
        
        return suggestions


class HealthcarePipeline(PreprocessingEngine):
    """Preprocessing pipeline for healthcare datasets."""
    
    def suggest_operations(self) -> List[PreprocessingOperation]:
        """Generate healthcare-specific preprocessing suggestions."""
        suggestions = super().suggest_operations()
        operation_counter = len(suggestions)
        
        # Patient ID anonymization
        for col_name, profile in self.column_profiles.items():
            if any(kw in col_name.lower() for kw in ['patient', 'ssn', 'mrn', 'medical_record']):
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="anonymize_patient_ids",
                    column=col_name,
                    description=f"Anonymize patient identifiers in {col_name}",
                    parameters={"method": "hash", "salt": "random"}
                ))
                operation_counter += 1
        
        # Medical code validation
        for col_name, profile in self.column_profiles.items():
            if any(kw in col_name.lower() for kw in ['icd', 'cpt', 'diagnosis', 'procedure']):
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="validate_medical_codes",
                    column=col_name,
                    description=f"Validate medical codes in {col_name}",
                    parameters={"code_type": "ICD10", "flag_invalid": True}
                ))
                operation_counter += 1
        
        # Age validation
        for col_name, profile in self.column_profiles.items():
            if 'age' in col_name.lower() and profile.get('type') == 'numeric':
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="validate_ages",
                    column=col_name,
                    description=f"Validate ages in {col_name}",
                    parameters={"min_age": 0, "max_age": 120}
                ))
                operation_counter += 1
        
        return suggestions


class GenericPipeline(PreprocessingEngine):
    """Generic preprocessing pipeline for unclassified datasets."""
    
    def suggest_operations(self) -> List[PreprocessingOperation]:
        """Generate generic preprocessing suggestions."""
        suggestions = super().suggest_operations()
        operation_counter = len(suggestions)
        
        # Remove duplicate rows
        # Convert to int to avoid numpy boolean subtract errors
        if int(self.current_df.duplicated().sum()) > 0:
            suggestions.append(PreprocessingOperation(
                operation_id=f"op_{operation_counter}",
                operation_type="remove_duplicates",
                column=None,
                description="Remove duplicate rows from dataset",
                parameters={}
            ))
            operation_counter += 1
        
        # Drop columns with too many missing values
        for col_name, profile in self.column_profiles.items():
            missing_pct = profile.get('missing_percent', 0)
            if missing_pct > 80:
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="drop_column",
                    column=col_name,
                    description=f"Drop {col_name} (>{missing_pct:.0f}% missing)",
                    parameters={"reason": "high_missing"}
                ))
                operation_counter += 1
        
        # Drop constant columns
        for col_name, profile in self.column_profiles.items():
            if profile.get('uniqueness', 1.0) == 0:
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="drop_column",
                    column=col_name,
                    description=f"Drop {col_name} (constant value)",
                    parameters={"reason": "constant"}
                ))
                operation_counter += 1
        
        return suggestions


def get_pipeline(dataset_type: str, df: pd.DataFrame, 
                column_profiles: Dict[str, Dict[str, Any]]) -> PreprocessingEngine:
    """
    Factory function to get appropriate preprocessing pipeline.
    
    Args:
        dataset_type: Type of dataset (Financial, Sales, Time-Series, Healthcare, Generic)
        df: Dataframe to preprocess
        column_profiles: Column profiles from ColumnProfiler
    
    Returns:
        Appropriate preprocessing pipeline instance
    """
    pipelines = {
        'Financial': FinancialPipeline,
        'Sales': SalesPipeline,
        'Time-Series': TimeSeriesPipeline,
        'Healthcare': HealthcarePipeline,
        'Generic': GenericPipeline
    }
    
    pipeline_class = pipelines.get(dataset_type, GenericPipeline)
    return pipeline_class(df, dataset_type, column_profiles)
