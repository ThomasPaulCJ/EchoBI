"""
Preprocessing Engine - Domain-specific data preprocessing for EchoBI v2.0

This module provides intelligent preprocessing with:
- Domain-specific transformation pipelines
- Audit trail for all operations
- Before/after state tracking
- User confirmation workflow
- Reversible operations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import copy


@dataclass
class PreprocessingOperation:
    """Represents a single preprocessing operation."""
    operation_id: str
    operation_type: str
    column: Optional[str]
    description: str
    parameters: Dict[str, Any]
    applied: bool = False
    timestamp: Optional[str] = None
    before_stats: Optional[Dict[str, Any]] = None
    after_stats: Optional[Dict[str, Any]] = None


@dataclass
class AuditEntry:
    """Audit trail entry for preprocessing."""
    timestamp: str
    operation_id: str
    operation_type: str
    column: Optional[str]
    description: str
    rows_affected: int
    values_changed: int
    before_sample: List[Any] = field(default_factory=list)
    after_sample: List[Any] = field(default_factory=list)


class PreprocessingEngine:
    """
    Base preprocessing engine with audit trail and rollback capabilities.
    
    Features:
    - Track all preprocessing operations
    - Before/after statistics
    - Reversible transformations
    - User confirmation workflow
    """
    
    def __init__(self, df: pd.DataFrame, dataset_type: str, column_profiles: Dict[str, Dict[str, Any]]):
        """
        Initialize preprocessing engine.
        
        Args:
            df: Original dataframe
            dataset_type: Dataset classification type
            column_profiles: Column profiles from ColumnProfiler
        """
        self.original_df = df.copy()
        self.current_df = df.copy()
        self.dataset_type = dataset_type
        self.column_profiles = column_profiles
        
        self.operations: List[PreprocessingOperation] = []
        self.audit_trail: List[AuditEntry] = []
        self.suggested_operations: List[PreprocessingOperation] = []
        
    def suggest_operations(self) -> List[PreprocessingOperation]:
        """Generate preprocessing operation suggestions based on data quality."""
        suggestions = []
        operation_counter = 0
        
        for col_name, profile in self.column_profiles.items():
            col_type = profile.get('type', 'unknown')
            missing_pct = profile.get('missing_percent', 0)
            
            # Missing value handling
            if missing_pct > 0:
                if col_type == 'numeric':
                    suggestions.append(PreprocessingOperation(
                        operation_id=f"op_{operation_counter}",
                        operation_type="impute_numeric",
                        column=col_name,
                        description=f"Impute missing values in {col_name} using median",
                        parameters={"method": "median"}
                    ))
                    operation_counter += 1
                elif col_type == 'categorical':
                    suggestions.append(PreprocessingOperation(
                        operation_id=f"op_{operation_counter}",
                        operation_type="impute_categorical",
                        column=col_name,
                        description=f"Impute missing values in {col_name} using mode",
                        parameters={"method": "mode"}
                    ))
                    operation_counter += 1
            
            # Outlier handling for numeric columns
            if col_type == 'numeric':
                col_data = self.current_df[col_name].dropna()
                if len(col_data) > 0:
                    q1 = float(col_data.quantile(0.25))
                    q3 = float(col_data.quantile(0.75))
                    iqr = q3 - q1
                    # Convert to int to avoid numpy boolean subtract errors
                    outliers = int(((col_data < q1 - 1.5 * iqr) | (col_data > q3 + 1.5 * iqr)).sum())
                    
                    if outliers > 0:
                        suggestions.append(PreprocessingOperation(
                            operation_id=f"op_{operation_counter}",
                            operation_type="handle_outliers",
                            column=col_name,
                            description=f"Cap outliers in {col_name} using IQR method",
                            parameters={"method": "iqr", "multiplier": 1.5}
                        ))
                        operation_counter += 1
            
            # Standardization for numeric columns
            if col_type == 'numeric' and profile.get('semantic_type') not in ['currency', 'percentage']:
                suggestions.append(PreprocessingOperation(
                    operation_id=f"op_{operation_counter}",
                    operation_type="standardize",
                    column=col_name,
                    description=f"Standardize {col_name} (z-score normalization)",
                    parameters={"method": "zscore"}
                ))
                operation_counter += 1
            
            # Encoding for categorical columns
            if col_type == 'categorical':
                cardinality = profile.get('cardinality', 0)
                if cardinality == 2:
                    suggestions.append(PreprocessingOperation(
                        operation_id=f"op_{operation_counter}",
                        operation_type="encode_binary",
                        column=col_name,
                        description=f"Binary encode {col_name}",
                        parameters={"method": "binary"}
                    ))
                    operation_counter += 1
                elif 2 < cardinality <= 10:
                    suggestions.append(PreprocessingOperation(
                        operation_id=f"op_{operation_counter}",
                        operation_type="encode_onehot",
                        column=col_name,
                        description=f"One-hot encode {col_name}",
                        parameters={"method": "onehot"}
                    ))
                    operation_counter += 1
                elif cardinality > 10:
                    suggestions.append(PreprocessingOperation(
                        operation_id=f"op_{operation_counter}",
                        operation_type="encode_label",
                        column=col_name,
                        description=f"Label encode {col_name} (high cardinality)",
                        parameters={"method": "label"}
                    ))
                    operation_counter += 1
        
        self.suggested_operations = suggestions
        return suggestions
    
    def apply_operation(self, operation: PreprocessingOperation) -> Tuple[pd.DataFrame, AuditEntry]:
        """
        Apply a single preprocessing operation.
        
        Returns:
            Tuple of (modified dataframe, audit entry)
        """
        before_df = self.current_df.copy()
        column = operation.column
        
        # Capture before stats
        if column:
            before_stats = self._get_column_stats(column, before_df)
            before_sample = before_df[column].dropna().head(5).tolist()
        else:
            before_stats = self._get_dataframe_stats(before_df)
            before_sample = []
        
        # Apply operation
        if operation.operation_type == "impute_numeric":
            self.current_df = self._impute_numeric(column, operation.parameters["method"])
        elif operation.operation_type == "impute_categorical":
            self.current_df = self._impute_categorical(column, operation.parameters["method"])
        elif operation.operation_type == "handle_outliers":
            self.current_df = self._handle_outliers(column, operation.parameters)
        elif operation.operation_type == "standardize":
            self.current_df = self._standardize(column, operation.parameters["method"])
        elif operation.operation_type == "encode_binary":
            self.current_df = self._encode_binary(column)
        elif operation.operation_type == "encode_onehot":
            self.current_df = self._encode_onehot(column)
        elif operation.operation_type == "encode_label":
            self.current_df = self._encode_label(column)
        elif operation.operation_type == "remove_duplicates":
            self.current_df = self._remove_duplicates()
        elif operation.operation_type == "drop_column":
            self.current_df = self._drop_column(column)
        # Domain-specific operations (handled by subclasses but provide defaults)
        elif operation.operation_type == "normalize_currency":
            self.current_df = self._normalize_currency(column, operation.parameters)
        elif operation.operation_type == "validate_transaction_dates":
            self.current_df = self._validate_dates(column, operation.parameters)
        elif operation.operation_type == "handle_negative_amounts":
            self.current_df = self._handle_negative_values(column, operation.parameters)
        elif operation.operation_type in ["standardize_product_ids", "validate_quantities", 
                                          "validate_emails", "sort_by_datetime", 
                                          "fill_missing_timestamps", "smooth_timeseries",
                                          "anonymize_patient_ids", "validate_medical_codes", 
                                          "validate_ages"]:
            # These are domain-specific - for now, pass through
            pass
        else:
            raise ValueError(f"Unknown operation type: {operation.operation_type}")
        
        # Capture after stats
        if column and column in self.current_df.columns:
            after_stats = self._get_column_stats(column, self.current_df)
            after_sample = self.current_df[column].dropna().head(5).tolist()
        else:
            after_stats = self._get_dataframe_stats(self.current_df)
            after_sample = []
        
        # Calculate impact
        rows_affected = len(before_df) - len(self.current_df) if len(before_df) != len(self.current_df) else len(before_df)
        values_changed = 0
        if column and column in before_df.columns and column in self.current_df.columns:
            # Convert to int to avoid numpy boolean subtract errors
            values_changed = int((before_df[column] != self.current_df[column]).sum())
        
        # Mark operation as applied
        operation.applied = True
        operation.timestamp = datetime.now().isoformat()
        operation.before_stats = before_stats
        operation.after_stats = after_stats
        self.operations.append(operation)
        
        # Create audit entry
        audit_entry = AuditEntry(
            timestamp=operation.timestamp,
            operation_id=operation.operation_id,
            operation_type=operation.operation_type,
            column=column,
            description=operation.description,
            rows_affected=rows_affected,
            values_changed=values_changed,
            before_sample=before_sample[:5],
            after_sample=after_sample[:5]
        )
        self.audit_trail.append(audit_entry)
        
        return self.current_df, audit_entry
    
    def _impute_numeric(self, column: str, method: str) -> pd.DataFrame:
        """Impute missing numeric values."""
        df = self.current_df.copy()
        if method == "mean":
            df[column].fillna(df[column].mean(), inplace=True)
        elif method == "median":
            df[column].fillna(df[column].median(), inplace=True)
        elif method == "mode":
            df[column].fillna(df[column].mode()[0], inplace=True)
        elif method == "zero":
            df[column].fillna(0, inplace=True)
        return df
    
    def _impute_categorical(self, column: str, method: str) -> pd.DataFrame:
        """Impute missing categorical values."""
        df = self.current_df.copy()
        if method == "mode":
            mode_value = df[column].mode()[0] if len(df[column].mode()) > 0 else "Unknown"
            df[column].fillna(mode_value, inplace=True)
        elif method == "unknown":
            df[column].fillna("Unknown", inplace=True)
        return df
    
    def _handle_outliers(self, column: str, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Handle outliers using IQR or other methods."""
        df = self.current_df.copy()
        method = parameters.get("method", "iqr")
        
        if method == "iqr":
            multiplier = parameters.get("multiplier", 1.5)
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - multiplier * iqr
            upper_bound = q3 + multiplier * iqr
            
            # Cap outliers
            df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        
        elif method == "zscore":
            threshold = parameters.get("threshold", 3)
            mean = df[column].mean()
            std = df[column].std()
            lower_bound = mean - threshold * std
            upper_bound = mean + threshold * std
            df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def _standardize(self, column: str, method: str) -> pd.DataFrame:
        """Standardize numeric column."""
        df = self.current_df.copy()
        if method == "zscore":
            df[column] = (df[column] - df[column].mean()) / df[column].std()
        elif method == "minmax":
            df[column] = (df[column] - df[column].min()) / (df[column].max() - df[column].min())
        return df
    
    def _encode_binary(self, column: str) -> pd.DataFrame:
        """Binary encode column (0/1)."""
        df = self.current_df.copy()
        unique_values = df[column].unique()
        if len(unique_values) == 2:
            df[f"{column}_encoded"] = (df[column] == unique_values[0]).astype(int)
        return df
    
    def _encode_onehot(self, column: str) -> pd.DataFrame:
        """One-hot encode column."""
        df = self.current_df.copy()
        dummies = pd.get_dummies(df[column], prefix=column)
        df = pd.concat([df, dummies], axis=1)
        return df
    
    def _encode_label(self, column: str) -> pd.DataFrame:
        """Label encode column."""
        df = self.current_df.copy()
        unique_values = df[column].unique()
        label_map = {val: idx for idx, val in enumerate(unique_values)}
        df[f"{column}_encoded"] = df[column].map(label_map)
        return df
    
    def _remove_duplicates(self) -> pd.DataFrame:
        """Remove duplicate rows."""
        return self.current_df.drop_duplicates()
    
    def _drop_column(self, column: str) -> pd.DataFrame:
        """Drop a column."""
        df = self.current_df.copy()
        return df.drop(columns=[column])
    
    def _normalize_currency(self, column: str, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Normalize currency values (remove symbols, format decimals)."""
        df = self.current_df.copy()
        if parameters.get("remove_symbols", True):
            # Remove common currency symbols
            df[column] = df[column].astype(str).str.replace('$', '').str.replace(',', '').str.replace('€', '')
            df[column] = pd.to_numeric(df[column], errors='coerce')
        
        if parameters.get("decimal_places"):
            decimal_places = parameters["decimal_places"]
            df[column] = df[column].round(decimal_places)
        
        return df
    
    def _validate_dates(self, column: str, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Validate and clean date values."""
        df = self.current_df.copy()
        try:
            df[column] = pd.to_datetime(df[column], errors='coerce')
            
            if parameters.get("remove_future", False):
                today = pd.Timestamp.now()
                df = df[df[column] <= today]
            
            if parameters.get("min_year"):
                min_date = pd.Timestamp(year=parameters["min_year"], month=1, day=1)
                df = df[df[column] >= min_date]
        except Exception:
            pass
        
        return df
    
    def _handle_negative_values(self, column: str, parameters: Dict[str, Any]) -> pd.DataFrame:
        """Handle negative values in numeric columns."""
        df = self.current_df.copy()
        method = parameters.get("method", "flag")
        
        if method == "absolute":
            df[column] = df[column].abs()
        elif method == "flag":
            df[f"{column}_is_negative"] = (df[column] < 0).astype(int)
        elif method == "remove":
            df = df[df[column] >= 0]
        
        return df
    
    def _get_column_stats(self, column: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Get statistics for a column."""
        if column not in df.columns:
            return {}
        
        col_data = df[column]
        # Convert counts to int to avoid numpy boolean subtract errors
        missing_count = int(col_data.isna().sum())
        unique_count = int(col_data.nunique())
        stats = {
            "count": len(col_data),
            "missing": missing_count,
            "missing_percent": missing_count / len(col_data) * 100 if len(col_data) > 0 else 0,
            "unique": unique_count
        }
        
        if pd.api.types.is_numeric_dtype(col_data):
            stats.update({
                "mean": float(col_data.mean()) if not col_data.isna().all() else None,
                "median": float(col_data.median()) if not col_data.isna().all() else None,
                "std": float(col_data.std()) if not col_data.isna().all() else None,
                "min": float(col_data.min()) if not col_data.isna().all() else None,
                "max": float(col_data.max()) if not col_data.isna().all() else None
            })
        
        return stats
    
    def _get_dataframe_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get overall dataframe statistics."""
        # Convert counts to int to avoid numpy boolean subtract errors
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "missing_cells": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum())
        }
    
    def rollback(self, operation_id: Optional[str] = None):
        """Rollback to original state or to before a specific operation."""
        if operation_id:
            # Rollback to before specific operation
            # For simplicity, reset to original and reapply operations up to that point
            self.current_df = self.original_df.copy()
            operations_to_keep = [op for op in self.operations if op.operation_id != operation_id]
            self.operations = []
            self.audit_trail = []
            for op in operations_to_keep:
                self.apply_operation(op)
        else:
            # Complete rollback
            self.current_df = self.original_df.copy()
            self.operations = []
            self.audit_trail = []
    
    def get_preview(self, operation_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get preview of what operations would do.
        
        Args:
            operation_ids: List of operation IDs to preview (None = all suggested)
        """
        # Create temporary copy
        temp_engine = PreprocessingEngine(self.original_df, self.dataset_type, self.column_profiles)
        
        operations_to_apply = self.suggested_operations if not operation_ids else [
            op for op in self.suggested_operations if op.operation_id in operation_ids
        ]
        
        preview_audit = []
        for op in operations_to_apply:
            _, audit_entry = temp_engine.apply_operation(op)
            # Convert AuditEntry to dict for JSON serialization
            preview_audit.append({
                "timestamp": audit_entry.timestamp,
                "operation_id": audit_entry.operation_id,
                "operation_type": audit_entry.operation_type,
                "column": audit_entry.column,
                "description": audit_entry.description,
                "rows_affected": audit_entry.rows_affected,
                "values_changed": audit_entry.values_changed,
                "before_sample": audit_entry.before_sample,
                "after_sample": audit_entry.after_sample
            })
        
        return {
            "original_shape": list(self.original_df.shape),
            "preview_shape": list(temp_engine.current_df.shape),
            "operations_applied": len(operations_to_apply),
            "audit_trail": preview_audit,
            "before_stats": self._get_dataframe_stats(self.original_df),
            "after_stats": self._get_dataframe_stats(temp_engine.current_df)
        }
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get audit trail as list of dictionaries."""
        return [
            {
                "timestamp": entry.timestamp,
                "operation_id": entry.operation_id,
                "operation_type": entry.operation_type,
                "column": entry.column,
                "description": entry.description,
                "rows_affected": entry.rows_affected,
                "values_changed": entry.values_changed,
                "before_sample": entry.before_sample,
                "after_sample": entry.after_sample
            }
            for entry in self.audit_trail
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Export engine state as dictionary."""
        return {
            "dataset_type": self.dataset_type,
            "original_shape": self.original_df.shape,
            "current_shape": self.current_df.shape,
            "operations_applied": len(self.operations),
            "suggested_operations": len(self.suggested_operations),
            "audit_trail": self.get_audit_trail()
        }
