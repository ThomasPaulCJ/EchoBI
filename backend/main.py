# backend/main.py - EchoBI v2.0 Backend API
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import io
import uuid
from datetime import datetime
import sys
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Google Gemini for AI features
try:
    from google import genai
    from google.genai import types
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyCc2dgIAoDwCz5WtIcLppAudaR3j6OK_5o"
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
        client = None
except ImportError:
    GEMINI_AVAILABLE = False
    client = None

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core import (ColumnProfiler, DatasetClassifier, QualityScorer, RelationshipDetector, 
                  FeatureAnalyzer, get_pipeline, InsightGenerator, VisualizationRecommender,
                  ChartGenerator)

def convert_to_json_serializable(obj):
    """Convert numpy/pandas types to JSON-serializable Python types."""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_list()
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    return obj

app = FastAPI(title="EchoBI v2.0 Backend", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

sessions = {}

class ClassificationConfirmation(BaseModel):
    session_id: str
    confirmed: bool
    override_type: Optional[str] = None

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'original_df': df.copy(),
            'current_df': df.copy(),
            'filename': file.filename,
            'uploaded_at': datetime.now().isoformat(),
            'classification': None,
            'classification_confirmed': False
        }
        return {"session_id": session_id, "filename": file.filename, "rows": len(df), "columns": len(df.columns), "status": "uploaded"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/analyze/{session_id}")
async def analyze_dataset(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        df = session['current_df']
        
        # Classification
        try:
            classifier = DatasetClassifier(df)
            classification = classifier.classify()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")
        
        # Store classification with all domain scores for transparency
        session['classification'] = {
            'type': classification.type,
            'confidence': classification.confidence,
            'description': classification.description,
            'features': classification.features,
            'suggestions': classification.suggestions,
            'all_scores': classification.all_scores  # All domain scores for UI display
        }
        
        # Also store available types for manual override
        session['available_types'] = classifier.get_available_types()
        
        # Column profiling
        try:
            profiler = ColumnProfiler(df)
            column_profiles = profiler.profile_all_columns()
            session['column_profiles'] = column_profiles
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Column profiling error: {str(e)}")
        
        # Quality scoring
        try:
            scorer = QualityScorer(df, column_profiles)
            quality_report = scorer.assess_quality()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Quality scoring error: {str(e)}")
        
        # Store quality scores in session for AI summary generation
        session['quality_scores'] = {
            "overall": quality_report.overall_score,
            "dimensions": {
                "completeness": quality_report.completeness,
                "validity": quality_report.validity,
                "consistency": quality_report.consistency,
                "uniqueness": quality_report.uniqueness
            },
            "issues": quality_report.issues,
            "recommendations": quality_report.recommendations
        }
        
        # Correlations
        correlations = []
        try:
            numeric_cols = [col for col, profile in column_profiles.items() if profile['type'] == 'numeric']
            
            if len(numeric_cols) >= 2:
                # Ensure all numeric columns are actually numeric types
                numeric_df = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
                corr_matrix = numeric_df.corr()
                for i, col1 in enumerate(numeric_cols):
                    for col2 in numeric_cols[i+1:]:
                        corr_value = corr_matrix.loc[col1, col2]
                        if pd.notna(corr_value) and abs(corr_value) > 0.3:
                            correlations.append({'column1': col1, 'column2': col2, 'value': float(corr_value)})
        except Exception as e:
            # Non-critical, just log and continue
            print(f"Correlation calculation warning: {str(e)}")
        
        return {
            "session_id": session_id,
            "classification": convert_to_json_serializable(session['classification']),
            "columns": convert_to_json_serializable(column_profiles),
            "quality": convert_to_json_serializable({
                "overall": quality_report.overall_score,
                "breakdown": {
                    "completeness": quality_report.completeness,
                    "validity": quality_report.validity,
                    "consistency": quality_report.consistency,
                    "uniqueness": quality_report.uniqueness
                },
                "issues": quality_report.issues,
                "recommendations": quality_report.recommendations
            }),
            "relationships": correlations,
            "summary": convert_to_json_serializable(profiler.get_summary()),
            "status": "analyzed"
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analyze error: {str(e)}")

@app.post("/api/v1/confirm-classification")
async def confirm_classification(confirmation: ClassificationConfirmation):
    if confirmation.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[confirmation.session_id]
    
    if not session.get('classification'):
        raise HTTPException(status_code=400, detail="Dataset not analyzed yet")
    
    if confirmation.confirmed:
        session['classification_confirmed'] = True
        if confirmation.override_type:
            # Update classification with user's manual selection
            session['classification']['type'] = confirmation.override_type
            session['classification']['confidence'] = 1.0
            session['classification']['user_override'] = True
            session['classification']['description'] = f"Manually classified as {confirmation.override_type} by user."
        
        return {
            "status": "confirmed", 
            "classification_type": session['classification']['type'],
            "user_override": session['classification'].get('user_override', False)
        }
    else:
        # Return all available types for manual selection
        classifier = DatasetClassifier(session['current_df'])
        available_types = classifier.get_available_types()
        return {
            "status": "awaiting_selection", 
            "available_types": available_types,
            "current_type": session['classification']['type'],
            "current_confidence": session['classification']['confidence']
        }

@app.get("/api/v1/available-types")
async def get_available_types():
    """Get all available dataset classification types."""
    # Return all available types without needing a session
    return {
        "types": [
            {'type': 'Financial', 'description': 'Financial transactions, accounting, banking, investments'},
            {'type': 'Sales', 'description': 'Products, customers, orders, retail, e-commerce'},
            {'type': 'Time-Series', 'description': 'Temporal data, trends, forecasting, sequential'},
            {'type': 'Healthcare', 'description': 'Medical records, diagnoses, treatments, clinical data'},
            {'type': 'Marketing', 'description': 'Campaigns, leads, conversions, engagement metrics'},
            {'type': 'HR', 'description': 'Employees, payroll, attendance, workforce management'},
            {'type': 'Logistics', 'description': 'Shipping, inventory, warehouses, supply chain'},
            {'type': 'Generic', 'description': 'No specific domain - apply general analysis'},
        ]
    }

@app.get("/api/v1/relationships/{session_id}")
async def get_relationships(session_id: str):
    """Get detailed relationship analysis for the dataset."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        df = session['current_df']
        
        # Get column profiles (from previous analyze call or regenerate)
        if 'column_profiles' not in session:
            profiler = ColumnProfiler(df)
            column_profiles = profiler.profile_all_columns()
            session['column_profiles'] = column_profiles
        else:
            column_profiles = session['column_profiles']
        
        # Detect relationships
        relationship_detector = RelationshipDetector(df, column_profiles)
        relationships = relationship_detector.detect_all_relationships()
        
        # Analyze features
        dataset_type = session.get('classification', {}).get('type')
        feature_analyzer = FeatureAnalyzer(df, column_profiles, dataset_type)
        features = feature_analyzer.analyze_all_features()
        
        return {
            "session_id": session_id,
            "relationships": convert_to_json_serializable(relationship_detector.to_dict_list()),
            "relationship_summary": convert_to_json_serializable(relationship_detector.get_summary()),
            "features": convert_to_json_serializable(feature_analyzer.to_dict_list()),
            "feature_summary": convert_to_json_serializable(feature_analyzer.get_summary()),
            "top_features": convert_to_json_serializable(
                [f.__dict__ for f in feature_analyzer.get_top_features(10)]
            ),
            "status": "analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/preprocessing/suggestions/{session_id}")
async def get_preprocessing_suggestions(session_id: str):
    """Get preprocessing operation suggestions for the dataset."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        df = session['current_df']
        
        # Get or create column profiles
        if 'column_profiles' not in session:
            profiler = ColumnProfiler(df)
            column_profiles = profiler.profile_all_columns()
            session['column_profiles'] = column_profiles
        else:
            column_profiles = session['column_profiles']
        
        # Get dataset type
        dataset_type = session.get('classification', {}).get('type', 'Generic')
        
        # Get appropriate pipeline
        pipeline = get_pipeline(dataset_type, df, column_profiles)
        suggestions = pipeline.suggest_operations()
        
        # Store pipeline in session for later use
        session['preprocessing_pipeline'] = pipeline
        
        return {
            "session_id": session_id,
            "dataset_type": dataset_type,
            "suggestions": convert_to_json_serializable([
                {
                    "operation_id": op.operation_id,
                    "operation_type": op.operation_type,
                    "column": op.column,
                    "description": op.description,
                    "parameters": op.parameters
                }
                for op in suggestions
            ]),
            "total_suggestions": len(suggestions),
            "status": "suggestions_ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/preprocessing/comparison/{session_id}")
async def get_preprocessing_comparison(session_id: str):
    """
    Get before/after comparison of preprocessing.
    Shows what changed between original and preprocessed data.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        original_df = session.get('original_df')
        current_df = session.get('current_df')
        
        if original_df is None or current_df is None:
            raise HTTPException(status_code=400, detail="Dataset not found")
        
        # Get comparison data if already computed
        comparison = session.get('preprocessing_comparison')
        audit_trail = session.get('audit_trail', [])
        
        # If no comparison exists, compute it
        if not comparison:
            comparison = {
                'before': {
                    'rows': len(original_df),
                    'columns': len(original_df.columns),
                    'missing_cells': int(original_df.isna().sum().sum()),
                    'missing_percent': float(original_df.isna().sum().sum() / (len(original_df) * len(original_df.columns)) * 100) if len(original_df) > 0 else 0,
                    'duplicate_rows': int(original_df.duplicated().sum()),
                    'column_list': list(original_df.columns)
                },
                'after': {
                    'rows': len(current_df),
                    'columns': len(current_df.columns),
                    'missing_cells': int(current_df.isna().sum().sum()),
                    'missing_percent': float(current_df.isna().sum().sum() / (len(current_df) * len(current_df.columns)) * 100) if len(current_df) > 0 else 0,
                    'duplicate_rows': int(current_df.duplicated().sum()),
                    'column_list': list(current_df.columns)
                },
                'changes': {
                    'rows_removed': len(original_df) - len(current_df),
                    'columns_added': len(current_df.columns) - len(original_df.columns),
                    'missing_cells_fixed': int(original_df.isna().sum().sum()) - int(current_df.isna().sum().sum()),
                    'duplicates_removed': int(original_df.duplicated().sum()) - int(current_df.duplicated().sum())
                }
            }
        
        # Compute per-column quality comparison
        column_comparison = []
        for col in original_df.columns:
            if col in current_df.columns:
                orig_missing = int(original_df[col].isna().sum())
                curr_missing = int(current_df[col].isna().sum())
                column_comparison.append({
                    'column': col,
                    'before_missing': orig_missing,
                    'after_missing': curr_missing,
                    'missing_fixed': orig_missing - curr_missing,
                    'before_missing_pct': float(orig_missing / len(original_df) * 100) if len(original_df) > 0 else 0,
                    'after_missing_pct': float(curr_missing / len(current_df) * 100) if len(current_df) > 0 else 0
                })
        
        return {
            "session_id": session_id,
            "preprocessing_applied": session.get('preprocessing_applied', False),
            "operations_count": len(audit_trail),
            "comparison": convert_to_json_serializable(comparison),
            "column_comparison": convert_to_json_serializable(column_comparison),
            "audit_trail": convert_to_json_serializable(audit_trail),
            "status": "comparison_ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PreprocessingRequest(BaseModel):
    session_id: str
    operation_ids: List[str]
    preview_only: bool = True

@app.post("/api/v1/preprocess")
async def preprocess_dataset(request: PreprocessingRequest):
    """Preview or apply preprocessing operations."""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[request.session_id]
        
        # Get or create pipeline
        if 'preprocessing_pipeline' not in session:
            df = session['current_df']
            column_profiles = session.get('column_profiles', {})
            dataset_type = session.get('classification', {}).get('type', 'Generic')
            pipeline = get_pipeline(dataset_type, df, column_profiles)
            pipeline.suggest_operations()
            session['preprocessing_pipeline'] = pipeline
        else:
            pipeline = session['preprocessing_pipeline']
        
        if request.preview_only:
            # Get preview without applying
            preview = pipeline.get_preview(request.operation_ids)
            return {
                "session_id": request.session_id,
                "mode": "preview",
                "preview": convert_to_json_serializable(preview),
                "status": "preview_ready"
            }
        else:
            # Apply operations
            operations_to_apply = [
                op for op in pipeline.suggested_operations 
                if op.operation_id in request.operation_ids
            ]
            
            audit_entries = []
            for op in operations_to_apply:
                _, audit_entry = pipeline.apply_operation(op)
                audit_entries.append(audit_entry)
            
            # Update session with preprocessed data
            session['current_df'] = pipeline.current_df
            session['preprocessing_applied'] = True
            
            # Store audit trail in session for AI summary
            session['audit_trail'] = convert_to_json_serializable(pipeline.get_audit_trail())
            
            # Store before/after comparison data for reporting
            original_df = pipeline.original_df
            current_df = pipeline.current_df
            session['preprocessing_comparison'] = {
                'before': {
                    'rows': len(original_df),
                    'columns': len(original_df.columns),
                    'missing_cells': int(original_df.isna().sum().sum()),
                    'missing_percent': float(original_df.isna().sum().sum() / (len(original_df) * len(original_df.columns)) * 100) if len(original_df) > 0 else 0,
                    'duplicate_rows': int(original_df.duplicated().sum()),
                    'column_list': list(original_df.columns)
                },
                'after': {
                    'rows': len(current_df),
                    'columns': len(current_df.columns),
                    'missing_cells': int(current_df.isna().sum().sum()),
                    'missing_percent': float(current_df.isna().sum().sum() / (len(current_df) * len(current_df.columns)) * 100) if len(current_df) > 0 else 0,
                    'duplicate_rows': int(current_df.duplicated().sum()),
                    'column_list': list(current_df.columns)
                },
                'changes': {
                    'rows_removed': len(original_df) - len(current_df),
                    'columns_added': len(current_df.columns) - len(original_df.columns),
                    'missing_cells_fixed': int(original_df.isna().sum().sum()) - int(current_df.isna().sum().sum()),
                    'duplicates_removed': int(original_df.duplicated().sum()) - int(current_df.duplicated().sum())
                }
            }
            
            return {
                "session_id": request.session_id,
                "mode": "applied",
                "operations_applied": len(operations_to_apply),
                "audit_trail": session['audit_trail'],
                "before_shape": list(pipeline.original_df.shape),
                "after_shape": list(pipeline.current_df.shape),
                "comparison": session['preprocessing_comparison'],
                "status": "preprocessing_complete"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RollbackRequest(BaseModel):
    session_id: str
    operation_id: Optional[str] = None

@app.post("/api/v1/preprocess/rollback")
async def rollback_preprocessing(request: RollbackRequest):
    """Rollback preprocessing operations."""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[request.session_id]
        
        if 'preprocessing_pipeline' not in session:
            raise HTTPException(status_code=400, detail="No preprocessing operations to rollback")
        
        pipeline = session['preprocessing_pipeline']
        pipeline.rollback(request.operation_id)
        
        # Update session
        session['current_df'] = pipeline.current_df
        session['preprocessing_applied'] = False
        
        return {
            "session_id": request.session_id,
            "rolled_back": True,
            "operation_id": request.operation_id,
            "current_shape": list(pipeline.current_df.shape),
            "status": "rollback_complete"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/download/{session_id}")
async def download_dataset(session_id: str, format: str = "csv"):
    """
    Download the current (preprocessed) dataset.
    
    Args:
        session_id: The session ID
        format: Output format - 'csv' or 'xlsx'
    
    Returns:
        StreamingResponse with the dataset file
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        df = session['current_df']
        original_filename = session.get('filename', 'dataset')
        
        # Remove extension from original filename
        base_filename = os.path.splitext(original_filename)[0]
        
        # Add preprocessed suffix if preprocessing was applied
        if session.get('preprocessing_applied', False):
            base_filename = f"{base_filename}_preprocessed"
        
        # Create file buffer
        buffer = io.BytesIO()
        
        if format.lower() == 'xlsx':
            df.to_excel(buffer, index=False, engine='openpyxl')
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"{base_filename}.xlsx"
        else:
            # Default to CSV
            csv_data = df.to_csv(index=False)
            buffer.write(csv_data.encode('utf-8'))
            media_type = "text/csv"
            filename = f"{base_filename}.csv"
        
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/insights/{session_id}")
async def get_insights(session_id: str, use_ai: bool = False):
    """
    Generate insights for the dataset.
    
    Combines statistical analysis with optional AI enhancement to provide
    actionable insights about data quality, patterns, and recommendations.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        df = session['current_df']
        
        # Get or create column profiles
        if 'column_profiles' not in session:
            profiler = ColumnProfiler(df)
            column_profiles = profiler.profile_all_columns()
            session['column_profiles'] = column_profiles
        else:
            column_profiles = session['column_profiles']
        
        # Get dataset type
        dataset_type = session.get('classification', {}).get('type', 'Generic')
        
        # Generate insights
        insight_generator = InsightGenerator(
            df, 
            column_profiles, 
            dataset_type,
            use_ai=use_ai,
            ai_config={'enabled': use_ai}
        )
        insights = insight_generator.generate_insights()
        
        # Store insights in session
        session['insights'] = insights
        session['recommendations'] = insight_generator.recommendations
        
        # Get summary
        summary = insight_generator.get_summary()
        
        return {
            "session_id": session_id,
            "dataset_type": dataset_type,
            "insights": convert_to_json_serializable([
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
                for i in insights
            ]),
            "recommendations": convert_to_json_serializable(insight_generator.recommendations),
            "summary": convert_to_json_serializable(summary),
            "ai_enabled": use_ai,
            "status": "insights_ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/visualizations/recommendations/{session_id}")
async def get_visualization_recommendations(session_id: str):
    """
    Get intelligent chart recommendations based on data characteristics.
    
    Analyzes data types, relationships, and domain context to suggest
    the most appropriate visualizations.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        df = session['current_df']
        
        # Get or create column profiles
        if 'column_profiles' not in session:
            profiler = ColumnProfiler(df)
            column_profiles = profiler.profile_all_columns()
            session['column_profiles'] = column_profiles
        else:
            column_profiles = session['column_profiles']
        
        # Get dataset type
        dataset_type = session.get('classification', {}).get('type', 'Generic')
        
        # Get relationships if available
        relationships = session.get('relationships', [])
        
        # Get insights if available
        insights = []
        if 'insights' in session:
            insights = [
                {
                    'insight_id': i.insight_id,
                    'category': i.category,
                    'visualization_type': i.visualization_type
                }
                for i in session['insights']
                if hasattr(i, 'visualization_type') and i.visualization_type
            ]
        
        # Generate visualization recommendations
        viz_recommender = VisualizationRecommender(
            df,
            column_profiles,
            dataset_type,
            relationships=relationships,
            insights=insights
        )
        recommendations = viz_recommender.generate_recommendations()
        
        # Store recommendations in session
        session['visualization_recommendations'] = recommendations
        
        return {
            "session_id": session_id,
            "dataset_type": dataset_type,
            "recommendations": convert_to_json_serializable(viz_recommender.to_dict_list()),
            "summary": convert_to_json_serializable(viz_recommender.get_summary()),
            "total_recommendations": len(recommendations),
            "high_priority_count": len([r for r in recommendations if r.priority == 1]),
            "status": "recommendations_ready"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/visualizations/generate")
async def generate_visualization(request: Dict[str, Any]):
    """
    Generate Plotly chart specification from recommendation.
    
    Request body:
    {
        "session_id": "abc123",
        "chart_id": "chart_1",  // Optional: use specific recommendation
        "chart_type": "bar",     // Optional: override chart type
        "config": {...}          // Optional: custom configuration
    }
    
    Returns Plotly JSON specification ready for rendering.
    """
    session_id = request.get("session_id")
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        df = session['current_df']
        
        # Get or create column profiles
        if 'column_profiles' not in session:
            profiler = ColumnProfiler(df)
            column_profiles = profiler.profile_all_columns()
            session['column_profiles'] = column_profiles
        else:
            column_profiles = session['column_profiles']
        
        # Create chart generator
        generator = ChartGenerator(df, column_profiles)
        
        # Get recommendation
        chart_id = request.get("chart_id")
        if chart_id:
            # Use specific recommendation from session
            recommendations = session.get("visualization_recommendations", [])
            recommendation = next(
                (r for r in recommendations if r.chart_id == chart_id),
                None
            )
            if not recommendation:
                raise HTTPException(status_code=404, detail="Chart recommendation not found")
            
            # Build config dict from recommendation attributes
            rec_dict = {
                'chart_id': recommendation.chart_id,
                'chart_type': recommendation.chart_type.value if hasattr(recommendation.chart_type, 'value') else recommendation.chart_type,
                'title': recommendation.title,
                'config': {
                    'x_axis': recommendation.x_axis,
                    'y_axis': recommendation.y_axis,
                    'color_by': recommendation.color_by,
                    'size_by': recommendation.size_by,
                    'group_by': recommendation.group_by,
                    'aggregation': recommendation.aggregation
                }
            }
            
            # Allow overrides
            if "chart_type" in request:
                rec_dict["chart_type"] = request["chart_type"]
            if "config" in request:
                rec_dict["config"].update(request["config"])
        else:
            # Build recommendation from request
            if "chart_type" not in request or "config" not in request:
                raise HTTPException(
                    status_code=400,
                    detail="Either chart_id or both chart_type and config must be provided"
                )
            
            rec_dict = {
                "chart_id": "custom",
                "chart_type": request["chart_type"],
                "title": request.get("title", "Custom Chart"),
                "config": request["config"]
            }
        
        # Generate chart
        chart_spec = generator.generate_chart(rec_dict)
        
        return {
            "chart_id": rec_dict["chart_id"],
            "chart_type": rec_dict["chart_type"],
            "title": rec_dict["title"],
            "plotly_spec": convert_to_json_serializable(chart_spec),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(e)}")


# ============================================
# Chat with Dataset API
# ============================================

class ChatMessage(BaseModel):
    session_id: str
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    response: str
    context_used: List[str]
    suggestions: List[str]

def build_dataset_context(session: dict) -> str:
    """Build a comprehensive context string from the session data."""
    context_parts = []
    
    # Basic dataset info
    df = session.get('current_df')
    if df is not None:
        context_parts.append(f"## Dataset Overview")
        context_parts.append(f"- Filename: {session.get('filename', 'Unknown')}")
        context_parts.append(f"- Rows: {len(df)}")
        context_parts.append(f"- Columns: {len(df.columns)}")
        context_parts.append(f"- Column names: {', '.join(df.columns.tolist())}")
        
        # Data types
        dtypes_summary = df.dtypes.value_counts().to_dict()
        dtypes_str = ', '.join([f"{k}: {v}" for k, v in dtypes_summary.items()])
        context_parts.append(f"- Data types: {dtypes_str}")
    
    # Classification info
    classification = session.get('classification')
    if classification:
        context_parts.append(f"\n## Dataset Classification")
        context_parts.append(f"- Type: {classification.get('type', 'Unknown')}")
        context_parts.append(f"- Confidence: {classification.get('confidence', 0):.1%}")
        context_parts.append(f"- Description: {classification.get('description', 'N/A')}")
        if classification.get('features'):
            context_parts.append(f"- Key features: {', '.join(classification.get('features', []))}")
        if classification.get('all_scores'):
            scores = classification['all_scores']
            context_parts.append(f"- Domain scores: {', '.join([f'{k}: {v:.2f}' for k, v in scores.items()])}")
    
    # Column profiles
    column_profiles = session.get('column_profiles', {})
    if column_profiles:
        context_parts.append(f"\n## Column Analysis")
        for col_name, profile in list(column_profiles.items())[:10]:  # Limit to first 10 columns
            if isinstance(profile, dict):
                col_type = profile.get('semantic_type', profile.get('dtype', 'unknown'))
                missing = profile.get('missing_count', 0)
                missing_pct = profile.get('missing_percentage', 0)
                context_parts.append(f"- {col_name}: {col_type}, {missing} missing ({missing_pct:.1f}%)")
    
    # Preprocessing history
    audit_trail = session.get('audit_trail', [])
    if audit_trail:
        context_parts.append(f"\n## Preprocessing Steps Applied")
        for i, operation in enumerate(audit_trail, 1):
            op_type = operation.get('operation', 'Unknown')
            op_detail = operation.get('details', '')
            context_parts.append(f"{i}. {op_type}: {op_detail}")
    
    # Quality information
    quality_scores = session.get('quality_scores', {})
    if quality_scores:
        context_parts.append(f"\n## Data Quality")
        context_parts.append(f"- Overall score: {quality_scores.get('overall', 0):.1%}")
        if quality_scores.get('dimensions'):
            for dim, score in quality_scores['dimensions'].items():
                context_parts.append(f"- {dim}: {score:.1%}")
    
    # Insights summary
    insights = session.get('insights', [])
    if insights:
        context_parts.append(f"\n## Key Insights ({len(insights)} total)")
        for insight in insights[:5]:  # First 5 insights
            if hasattr(insight, 'title'):
                context_parts.append(f"- {insight.title}")
            elif isinstance(insight, dict):
                context_parts.append(f"- {insight.get('title', 'Untitled insight')}")
    
    return '\n'.join(context_parts)


def generate_ai_chat_response(message: str, context: str, conversation_history: list = None, df: pd.DataFrame = None) -> dict:
    """Generate an AI-powered response using Google Gemini."""
    
    # Build the prompt
    system_prompt = """You are EchoBI Assistant, an expert data analyst AI that helps users understand their datasets. 
You have access to detailed information about the user's uploaded dataset including:
- Dataset overview (rows, columns, types)
- Classification (what type of data it is)
- Column analysis (each column's type, missing data, statistics)
- Preprocessing steps applied
- Data quality scores
- Key insights discovered

Your role is to:
1. Answer questions about the dataset clearly and accurately
2. Explain classification decisions and confidence scores
3. Describe preprocessing steps and why they were applied
4. Help users understand data quality issues
5. Provide actionable recommendations for data analysis
6. Suggest relevant follow-up questions

Be conversational, helpful, and concise. Use markdown formatting for clarity.
When discussing numbers, be specific and cite the actual values from the context.
If you don't have information to answer a question, say so and suggest what the user can do."""

    # Build the full prompt
    full_prompt = f"""{system_prompt}

## Dataset Context:
{context}
"""
    
    # Add sample data if available
    if df is not None and len(df) > 0:
        sample_data = df.head(5).to_string()
        full_prompt += f"\n## Sample Data (first 5 rows):\n{sample_data}\n"
    
    # Add conversation history
    if conversation_history:
        full_prompt += "\n## Previous Conversation:\n"
        for msg in conversation_history[-6:]:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            full_prompt += f"{role}: {msg.get('content', '')}\n"
    
    # Add current user message
    full_prompt += f"\n## Current Question:\nUser: {message}\n\nAssistant:"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=full_prompt
        )
        ai_response = response.text
        
        # Generate smart suggestions based on the conversation
        suggestions = generate_smart_suggestions(message, context)
        
        return {
            "response": ai_response,
            "context_used": ["gemini_ai"],
            "suggestions": suggestions,
            "ai_powered": True
        }
    except Exception as e:
        print(f"Gemini API error: {e}")
        # Fallback to rule-based response
        return generate_fallback_response(message, context, conversation_history)


def generate_smart_suggestions(message: str, context: str) -> list:
    """Generate contextually relevant follow-up suggestions."""
    message_lower = message.lower()
    suggestions = []
    
    # Based on what was asked, suggest related questions
    if any(word in message_lower for word in ['dataset', 'overview', 'about']):
        suggestions = ["What's the data quality?", "Show me the classification", "Describe the columns"]
    elif any(word in message_lower for word in ['classif', 'type']):
        suggestions = ["Why this classification?", "What are the confidence scores?", "Show column analysis"]
    elif any(word in message_lower for word in ['column', 'variable', 'field']):
        suggestions = ["Which columns have missing data?", "Show numeric columns", "What preprocessing is needed?"]
    elif any(word in message_lower for word in ['quality', 'score']):
        suggestions = ["How to improve quality?", "Show missing data details", "What issues exist?"]
    elif any(word in message_lower for word in ['preprocess', 'clean']):
        suggestions = ["What was cleaned?", "Show the audit trail", "What's the data quality now?"]
    elif any(word in message_lower for word in ['insight', 'pattern', 'trend']):
        suggestions = ["Show more insights", "What visualizations?", "Explain correlations"]
    else:
        suggestions = ["Tell me about the dataset", "Show data quality", "What insights were found?", "Describe the columns"]
    
    return suggestions[:4]


def generate_fallback_response(message: str, context: str, conversation_history: list = None) -> dict:
    """Fallback rule-based response when AI is unavailable."""
    message_lower = message.lower()
    
    response_parts = []
    context_used = []
    suggestions = []
    
    # Determine what the user is asking about
    if any(word in message_lower for word in ['what', 'describe', 'overview', 'about', 'summary', 'tell me']):
        if any(word in message_lower for word in ['dataset', 'data', 'file']):
            response_parts.append("📊 **Dataset Overview**\n")
            response_parts.append(context.split('\n## Dataset Classification')[0] if '## Dataset Classification' in context else context[:500])
            context_used.append("dataset_overview")
            suggestions.extend(["What is the data quality?", "Show classification details", "What preprocessing was applied?"])
    
    if any(word in message_lower for word in ['classif', 'type', 'domain', 'category']):
        if '## Dataset Classification' in context:
            start = context.find('## Dataset Classification')
            end = context.find('\n## Column', start)
            classification_section = context[start:end] if end > start else context[start:start+500]
            response_parts.append("🏷️ **Classification Details**\n")
            response_parts.append(classification_section)
            context_used.append("classification")
            suggestions.extend(["Why was this type chosen?", "Confidence scores?", "Change classification?"])
    
    if any(word in message_lower for word in ['column', 'variable', 'field', 'attribute']):
        if '## Column Analysis' in context:
            start = context.find('## Column Analysis')
            end = context.find('\n## ', start + 20)
            column_section = context[start:end] if end > start else context[start:start+800]
            response_parts.append("📋 **Column Analysis**\n")
            response_parts.append(column_section)
            context_used.append("column_analysis")
            suggestions.extend(["Missing data?", "Data types?", "Numeric columns?"])
    
    if any(word in message_lower for word in ['quality', 'score']):
        if '## Data Quality' in context:
            start = context.find('## Data Quality')
            end = context.find('\n## ', start + 15)
            quality_section = context[start:end] if end > start else context[start:start+500]
            response_parts.append("✅ **Data Quality**\n")
            response_parts.append(quality_section)
            context_used.append("quality")
            suggestions.extend(["Improve quality?", "What issues?", "Missing data?"])
    
    if any(word in message_lower for word in ['insight', 'finding', 'pattern']):
        if '## Key Insights' in context:
            start = context.find('## Key Insights')
            end = context.find('\n## ', start + 15)
            insights_section = context[start:end] if end > start else context[start:start+500]
            response_parts.append("💡 **Key Insights**\n")
            response_parts.append(insights_section)
            context_used.append("insights")
            suggestions.extend(["More insights?", "Visualizations?", "Explain insight?"])
    
    if any(word in message_lower for word in ['help', 'how', 'what can']):
        response_parts.append("""🤖 **I can help you with:**

**📊 Dataset:** "What is this dataset about?"
**🏷️ Classification:** "What type of data is this?"
**📋 Columns:** "Describe the columns"
**✅ Quality:** "What is the data quality?"
**⚙️ Preprocessing:** "What was applied?"
**💡 Insights:** "Show me the insights"
""")
        context_used.append("help")
        suggestions.extend(["About the dataset", "Data quality", "Preprocessing applied"])
    
    # Default response if nothing matched
    if not response_parts:
        response_parts.append(f"I understand you're asking about: '{message}'\n\n")
        lines = context.split('\n')[:15]
        response_parts.append('\n'.join(lines))
        context_used.append("general")
        suggestions.extend(["About the dataset", "Classification", "Columns", "Insights"])
    
    return {
        "response": '\n'.join(response_parts),
        "context_used": context_used,
        "suggestions": suggestions[:4],
        "ai_powered": False
    }


@app.post("/api/v1/chat")
async def chat_with_dataset(chat_message: ChatMessage):
    """
    Chat with your dataset - AI-powered Q&A about the data, classification, 
    preprocessing steps, insights, and more.
    """
    session_id = chat_message.session_id
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a dataset first.")
    
    try:
        session = sessions[session_id]
        df = session.get('current_df')
        
        # Build context from session data
        context = build_dataset_context(session)
        
        # Store context in session for reference
        session['chat_context'] = context
        
        # Generate response - try Gemini AI first, fallback to rule-based
        if GEMINI_AVAILABLE and client:
            result = generate_ai_chat_response(
                chat_message.message,
                context,
                chat_message.conversation_history,
                df
            )
        else:
            result = generate_fallback_response(
                chat_message.message,
                context,
                chat_message.conversation_history
            )
        
        # Store chat history in session
        if 'chat_history' not in session:
            session['chat_history'] = []
        session['chat_history'].append({
            'user': chat_message.message,
            'assistant': result['response'],
            'timestamp': datetime.now().isoformat(),
            'ai_powered': result.get('ai_powered', False)
        })
        
        return {
            "response": result['response'],
            "context_used": result['context_used'],
            "suggestions": result['suggestions'],
            "ai_powered": result.get('ai_powered', False),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.get("/api/v1/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get the chat history for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "history": session.get('chat_history', []),
        "status": "success"
    }


@app.delete("/api/v1/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear the chat history for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions[session_id]['chat_history'] = []
    return {"message": "Chat history cleared", "status": "success"}


# ============================================
# AI Summary Endpoints
# ============================================

def generate_ai_dataset_summary(session: dict) -> str:
    """Generate an AI-powered executive summary of the dataset using Gemini."""
    df = session.get('current_df')
    original_df = session.get('original_df')
    classification = session.get('classification', {})
    column_profiles = session.get('column_profiles', {})
    quality_scores = session.get('quality_scores', {})
    insights = session.get('insights', [])
    audit_trail = session.get('audit_trail', [])
    
    # Determine if this is preprocessed or original data
    is_preprocessed = bool(audit_trail) or session.get('preprocessing_applied', False)
    data_state = "PREPROCESSED (CLEANED)" if is_preprocessed else "ORIGINAL (UNPROCESSED)"
    
    # Build context for AI
    rows = len(df) if df is not None else 0
    cols = len(df.columns) if df is not None else 0
    col_names = ', '.join(df.columns.tolist()) if df is not None else 'Unknown'
    
    # Count missing values
    total_missing = 0
    missing_pct = 0
    if df is not None:
        total_missing = int(df.isnull().sum().sum())
        total_cells = df.size
        missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
    
    # Get quality score and breakdown
    overall_quality = quality_scores.get('overall', 0) if isinstance(quality_scores, dict) else 0
    quality_dimensions = quality_scores.get('dimensions', {}) if isinstance(quality_scores, dict) else {}
    quality_issues = quality_scores.get('issues', []) if isinstance(quality_scores, dict) else []
    quality_recommendations = quality_scores.get('recommendations', []) if isinstance(quality_scores, dict) else []
    
    # Build quality score explanation
    quality_breakdown = f"""
QUALITY SCORE BREAKDOWN:
- Overall Score: {overall_quality:.1%}
- Completeness: {quality_dimensions.get('completeness', 0):.1%} (non-null values)
- Validity: {quality_dimensions.get('validity', 0):.1%} (correct data types and formats)
- Consistency: {quality_dimensions.get('consistency', 0):.1%} (uniform formatting)
- Uniqueness: {quality_dimensions.get('uniqueness', 0):.1%} (appropriate duplication levels)

Quality Issues Detected:
"""
    if quality_issues:
        for issue in quality_issues[:5]:
            quality_breakdown += f"- {issue}\n"
    else:
        quality_breakdown += "- No significant quality issues detected\n"
    
    quality_breakdown += "\nRecommendations to Achieve 100% Quality:\n"
    if quality_recommendations:
        for rec in quality_recommendations[:5]:
            quality_breakdown += f"- {rec}\n"
    else:
        quality_breakdown += "- Data quality is excellent. No improvements needed.\n"
    
    # Simple preprocessing status (no detailed steps - those belong in preprocessing tab)
    preprocessing_status = ""
    if is_preprocessed and audit_trail:
        original_rows = len(original_df) if original_df is not None else rows
        original_missing = int(original_df.isna().sum().sum()) if original_df is not None else total_missing
        
        preprocessing_status = f"""
PREPROCESSING STATUS:
- Data State: This is the CLEANED/PREPROCESSED version of the dataset
- Original State: {original_rows:,} rows, {original_missing:,} missing values
- Current State: {rows:,} rows, {total_missing:,} missing values
- Total Operations Applied: {len(audit_trail)}
- Note: View detailed preprocessing steps in the 'Data Quality & Preprocessing' tab
"""
    else:
        preprocessing_status = "\nPREPROCESSING STATUS: This is the ORIGINAL/UNPROCESSED dataset as uploaded. No cleaning operations have been applied yet.\n"
    
    # Build column statistics
    col_stats = ""
    numeric_cols = []
    categorical_cols = []
    date_cols = []
    
    if df is not None:
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = int(df[col].isnull().sum())
            unique = int(df[col].nunique())
            
            if df[col].dtype in ['int64', 'float64']:
                numeric_cols.append(col)
                col_stats += f"- {col}: numeric, min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}, {missing} missing, {unique} unique values\n"
            elif 'datetime' in dtype:
                date_cols.append(col)
                col_stats += f"- {col}: date/time, {missing} missing, {unique} unique values\n"
            else:
                categorical_cols.append(col)
                top_val = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 'N/A'
                col_stats += f"- {col}: categorical, top value='{top_val}', {missing} missing, {unique} unique values\n"
    
    # Build insights summary
    insights_text = ""
    if insights:
        for i, insight in enumerate(insights[:5], 1):
            if isinstance(insight, dict):
                title = insight.get('title', 'Finding')
                desc = insight.get('description', '')[:100]
                severity = insight.get('severity', 'low')
                insights_text += f"{i}. [{severity.upper()}] {title}: {desc}\n"
    
    # Sample data
    sample_data = ""
    if df is not None and len(df) > 0:
        sample_data = df.head(3).to_string()
    
    prompt = f"""You are a senior data analyst writing a comprehensive executive summary for business stakeholders.

**CRITICAL: DATA STATE INDICATOR**
DATA STATE: {data_state}
{preprocessing_status}

DATASET OVERVIEW:
- Filename: {session.get('filename', 'Unknown')}
- Classification: {classification.get('type', 'Unknown')} ({classification.get('confidence', 0):.0%} confidence)
- Description: {classification.get('description', 'N/A')}
- Total Records: {rows:,} rows
- Total Columns: {cols} columns
- Column Names: {col_names}

{quality_breakdown}

DATA QUALITY METRICS:
- Total Missing Values: {total_missing:,} ({missing_pct:.1f}% of all cells)
- Numeric Columns: {len(numeric_cols)}
- Categorical Columns: {len(categorical_cols)}
- Date/Time Columns: {len(date_cols)}

COLUMN STATISTICS:
{col_stats}

KEY INSIGHTS DISCOVERED ({len(insights)} total):
{insights_text if insights_text else "No significant insights detected yet."}

SAMPLE DATA (first 3 rows):
{sample_data}

Write a detailed, flowing executive summary in 3-4 well-written paragraphs (NO bullet points, NO headers, NO markdown formatting, NO asterisks). The summary should:

1. First paragraph: START by clearly stating whether this is the ORIGINAL/UNPROCESSED data or the CLEANED/PREPROCESSED version. Then describe what this dataset contains, its business purpose, the type of data (financial, sales, etc.), and key columns/fields available.

2. Second paragraph: Discuss current data quality in COMPREHENSIVE detail:
   - Start with the overall quality score percentage
   - EXPLAIN what factors are affecting the quality score - mention the breakdown by dimension (completeness, validity, consistency, uniqueness)
   - If the quality score is not 100%, CLEARLY EXPLAIN why it's not perfect - what specific issues were detected
   - Provide SPECIFIC RECOMMENDATIONS on what needs to be done to achieve 100% quality
   - If this is preprocessed data, mention that cleaning was applied but DO NOT list the detailed steps here

3. Third paragraph: Highlight the most important insights and patterns discovered in the data. Mention specific findings with numbers.

4. Fourth paragraph: Provide actionable recommendations for analysis and next steps.

CRITICAL INSTRUCTION ON QUALITY SCORE:
- You MUST explain WHY the quality score is not 100% if it's less than 100%
- Reference the specific dimension scores (completeness, validity, consistency, uniqueness)
- List the detected quality issues clearly
- Provide actionable recommendations to reach 100% quality
- Be specific - don't just say "good quality", explain what's preventing it from being perfect

IMPORTANT: You MUST clearly state at the beginning whether you are analyzing the original unprocessed data or the cleaned/preprocessed version. However, DO NOT list detailed preprocessing steps in this summary - those belong in the Data Quality & Preprocessing section.

Write in clear, professional prose suitable for C-level executives. Be specific with numbers and findings. Do not use any bullet points, lists, or markdown formatting."""

    # Try AI first
    if GEMINI_AVAILABLE and client:
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini AI error: {e}")
    
    # Fallback to paragraph summary
    dataset_type = classification.get('type', 'Generic')
    quality_label = "excellent" if overall_quality > 0.9 else "good" if overall_quality > 0.75 else "moderate" if overall_quality > 0.5 else "needs attention"
    
    # Build quality explanation
    quality_explanation = f"The overall data quality score is {overall_quality:.1%}"
    if overall_quality < 1.0:
        dimension_issues = []
        if quality_dimensions.get('completeness', 1) < 1.0:
            dimension_issues.append(f"completeness at {quality_dimensions.get('completeness', 0):.1%}")
        if quality_dimensions.get('validity', 1) < 1.0:
            dimension_issues.append(f"validity at {quality_dimensions.get('validity', 0):.1%}")
        if quality_dimensions.get('consistency', 1) < 1.0:
            dimension_issues.append(f"consistency at {quality_dimensions.get('consistency', 0):.1%}")
        if quality_dimensions.get('uniqueness', 1) < 1.0:
            dimension_issues.append(f"uniqueness at {quality_dimensions.get('uniqueness', 0):.1%}")
        
        if dimension_issues:
            quality_explanation += f", with {', '.join(dimension_issues)}. "
        
        if quality_issues:
            quality_explanation += f"Key issues include: {'; '.join(quality_issues[:3])}. "
        
        if quality_recommendations:
            quality_explanation += f"To achieve 100% quality: {'; '.join(quality_recommendations[:3])}."
    else:
        quality_explanation += " (perfect data quality across all dimensions)."
    
    fallback = f"**DATA STATE: {data_state}** "
    
    if is_preprocessed:
        fallback += f"This analysis is based on the cleaned and preprocessed version of the data. "
        if audit_trail:
            fallback += f"{len(audit_trail)} preprocessing operations were applied to improve data quality. For detailed preprocessing steps, please see the Data Quality & Preprocessing tab. "
    else:
        fallback += f"This analysis is based on the original, unprocessed dataset as uploaded. "
    
    fallback += f"This {dataset_type} dataset contains {rows:,} records across {cols} columns, including {len(numeric_cols)} numeric fields, {len(categorical_cols)} categorical fields, and {len(date_cols)} date/time fields. "
    fallback += f"The columns available are: {col_names}. "
    
    fallback += f"\n\n{quality_explanation} There are {total_missing:,} missing values representing {missing_pct:.1f}% of the data. "
    
    if insights:
        fallback += f"\n\nOur analysis has discovered {len(insights)} insights. "
        high_priority = len([i for i in insights if isinstance(i, dict) and i.get('severity') == 'high'])
        if high_priority:
            fallback += f"Of these, {high_priority} are high-priority findings that warrant immediate attention. "
    
    fallback += "\n\nWe recommend exploring the visualizations in the Dashboard tab to better understand distributions and relationships, and addressing any data quality issues before proceeding with advanced analysis."
    
    return fallback


def generate_ai_preprocessing_summary(session: dict) -> str:
    """Generate an AI-powered summary of preprocessing steps with before/after comparison."""
    df = session.get('current_df')
    original_df = session.get('original_df')
    classification = session.get('classification', {})
    
    # Get audit trail - check both session and pipeline
    audit_trail = session.get('audit_trail', [])
    
    # Also check preprocessing_pipeline if audit_trail is empty
    if not audit_trail and 'preprocessing_pipeline' in session:
        pipeline = session['preprocessing_pipeline']
        if hasattr(pipeline, 'get_audit_trail'):
            audit_trail = pipeline.get_audit_trail()
            # Store it in session for future use
            session['audit_trail'] = audit_trail
    
    # Get comparison data
    comparison = session.get('preprocessing_comparison', {})
    
    if not audit_trail:
        # Check if preprocessing was supposed to happen
        if session.get('preprocessing_applied'):
            return "Preprocessing was marked as applied, but no specific operations were recorded. This may indicate automatic preprocessing was performed. Check the Data Quality section for changes between original and current data."
        return "No preprocessing steps have been applied yet. The data is currently in its original uploaded form. You can apply cleaning and transformation operations from the Preprocessing tab to prepare your data for analysis."
    
    # Calculate before/after stats
    original_rows = len(original_df) if original_df is not None else 0
    current_rows = len(df) if df is not None else 0
    rows_changed = original_rows - current_rows
    
    # Calculate original vs current missing values
    original_missing = int(original_df.isna().sum().sum()) if original_df is not None else 0
    current_missing = int(df.isna().sum().sum()) if df is not None else 0
    missing_fixed = original_missing - current_missing
    
    # Calculate duplicates
    original_duplicates = int(original_df.duplicated().sum()) if original_df is not None else 0
    current_duplicates = int(df.duplicated().sum()) if df is not None else 0
    duplicates_removed = original_duplicates - current_duplicates
    
    # Build detailed operations list for AI (handle both formats)
    ops_text = ""
    for i, op in enumerate(audit_trail, 1):
        # Handle the new format from preprocessing engine
        if isinstance(op, dict):
            op_type = op.get('operation_type', op.get('operation', 'Unknown'))
            description = op.get('description', op.get('details', 'N/A'))
            column = op.get('column', '')
            values_changed = op.get('values_changed', 0)
            params = op.get('parameters', {})
            
            ops_text += f"{i}. {op_type}"
            if column:
                ops_text += f" on column '{column}'"
            ops_text += f": {description}"
            if values_changed > 0:
                ops_text += f" ({values_changed:,} values changed)"
            if params:
                param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
                ops_text += f" [Parameters: {param_str}]"
            ops_text += "\n"
        else:
            ops_text += f"{i}. {str(op)}\n"
    
    # Build comparison summary
    comparison_text = f"""
BEFORE/AFTER COMPARISON:
- Original dataset: {original_rows:,} rows, {len(original_df.columns) if original_df is not None else 0} columns
- After preprocessing: {current_rows:,} rows, {len(df.columns) if df is not None else 0} columns
- Missing values: {original_missing:,} → {current_missing:,} ({missing_fixed:,} fixed)
- Duplicate rows: {original_duplicates:,} → {current_duplicates:,} ({duplicates_removed:,} removed)
- Net row change: {rows_changed:,} rows {'removed' if rows_changed > 0 else 'added' if rows_changed < 0 else 'unchanged'}
"""
    
    prompt = f"""You are a data engineer explaining data preprocessing to a non-technical business user.

Dataset Type: {classification.get('type', 'Generic')}

{comparison_text}

Detailed Operations Performed ({len(audit_trail)} total):
{ops_text}

Write a comprehensive, clear, flowing 3-4 paragraph summary (NO bullet points, NO headers, NO markdown) explaining:

1. First paragraph: Describe what the original data looked like - specific issues found (missing values, duplicates, data quality problems, formatting issues). Use exact numbers from the before state.

2. Second paragraph: Explain in detail EVERY preprocessing step that was performed. List each operation by name, what column it affected, what it did, and why it was necessary. Be comprehensive - don't skip any steps.

3. Third paragraph: Show the improvement with specific before/after numbers. Compare rows, missing values, duplicates, and quality metrics. Demonstrate the transformation clearly.

4. Fourth paragraph: Describe what the cleaned data now looks like and confirm it's ready for reliable analysis and visualization.

IMPORTANT: You MUST describe ALL {len(audit_trail)} preprocessing operations in detail. Don't summarize or skip steps. Business users need to understand exactly what was done to their data for transparency and trust.

Be specific with numbers and operation names. Write in simple, conversational prose that anyone can understand."""

    # Try AI first
    if GEMINI_AVAILABLE and client:
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini preprocessing error: {e}")
    
    # Fallback paragraph with before/after comparison
    dataset_type = classification.get('type', 'dataset')
    original_cols = len(original_df.columns) if original_df is not None else 0
    current_cols = len(df.columns) if df is not None else 0
    
    fallback = f"We applied {len(audit_trail)} preprocessing operation(s) to clean your {dataset_type} dataset. "
    fallback += f"The original data contained {original_rows:,} rows and {original_cols} columns, with {original_missing:,} missing values and {original_duplicates:,} duplicate rows. "
    
    if missing_fixed > 0 or duplicates_removed > 0 or rows_changed != 0:
        fallback += "After preprocessing: "
        changes = []
        if missing_fixed > 0:
            changes.append(f"{missing_fixed:,} missing values were handled")
        if duplicates_removed > 0:
            changes.append(f"{duplicates_removed:,} duplicate rows were removed")
        if rows_changed > 0:
            changes.append(f"dataset reduced from {original_rows:,} to {current_rows:,} rows")
        elif rows_changed < 0:
            changes.append(f"dataset expanded from {original_rows:,} to {current_rows:,} rows (new columns added)")
        if current_cols != original_cols:
            changes.append(f"columns changed from {original_cols} to {current_cols}")
        fallback += ", ".join(changes) + ". "
    
    fallback += f"The cleaned dataset now has {current_rows:,} rows, {current_cols} columns, {current_missing:,} missing values, and {current_duplicates:,} duplicates. "
    fallback += "Your data has been successfully cleaned and is ready for analysis and visualization."
    
    return fallback


@app.get("/api/v1/ai-summary/dataset/{session_id}")
async def get_ai_dataset_summary(session_id: str):
    """
    Generate an executive summary of the dataset.
    Provides comprehensive statistical analysis.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        summary = generate_ai_dataset_summary(session)
        
        # Cache the summary
        session['ai_dataset_summary'] = summary
        return {
            "session_id": session_id,
            "summary": summary,
            "ai_powered": True,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ai-summary/preprocessing/{session_id}")
async def get_ai_preprocessing_summary(session_id: str):
    """
    Generate a summary of preprocessing steps.
    Explains what transformations were applied.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        summary = generate_ai_preprocessing_summary(session)
        
        if summary:
            # Cache the summary
            session['ai_preprocessing_summary'] = summary
            return {
                "session_id": session_id,
                "summary": summary,
                "ai_powered": True,
                "steps_count": len(session.get('audit_trail', [])),
                "status": "success"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate AI summary")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

