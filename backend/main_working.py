# backend/main.py
"""
EchoBI v2.0 Backend API

This backend implements intelligent dataset analysis with:
- Dataset classification (Financial, Sales, Time-Series, Healthcare, Generic)
- Column profiling with statistics and quality metrics
- Data quality scoring across multiple dimensions
- Context-aware preprocessing pipelines
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import pandas as pd
import io
import plotly.express as px
import requests
import os
import uuid
from datetime import datetime

# Import core v2.0 modules
from core import ColumnProfiler, DatasetClassifier, QualityScorer

LM_STUDIO_API = os.getenv("LM_STUDIO_API", "http://localhost:1234/v1/chat/completions")

app = FastAPI(title="EchoBI v2.0 Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (replace with Redis/DB in production)
sessions = {}

def call_lmstudio(prompt: str):
    payload = {
        "model": "gpt-3.5",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    resp = requests.post(LM_STUDIO_API, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload dataset file and create a session.
    
    v2.0: Returns session_id without automatic classification.
    Classification happens in separate /analyze endpoint after user confirmation.
    """
    try:
        contents = await file.read()
        
        # Parse file based on extension
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        elif file.filename.endswith(".json"):
            df = pd.read_json(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV, XLSX, or JSON.")
        
        # Create session
        session_id = str(uuid.uuid4())
        
        # Store original dataframe (before any preprocessing)
        sessions[session_id] = {
            'original_df': df.copy(),
            'current_df': df.copy(),
            'filename': file.filename,
            'uploaded_at': datetime.now().isoformat(),
            'classification': None,
            'classification_confirmed': False,
            'preprocessing_history': []
        }
        
        # Return basic info
        return {
            "session_id": session_id,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "status": "uploaded",
            "message": "File uploaded successfully. Call /analyze to classify and profile the dataset."
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload error: {str(e)}")

@app.post("/api/v1/analyze/{session_id}")
async def analyze_dataset(session_id: str):
    """
    Analyze and classify dataset using v2.0 intelligence modules.
    
    Returns:
    - Dataset classification with confidence score
    - Column profiles with statistics
    - Quality assessment
    - Detected relationships
    
    NOTE: User must confirm classification before preprocessing.
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        df = session['current_df']
        
        # 1. Classify dataset
class ClassificationConfirmation(BaseModel):
    """Request body for classification confirmation."""
    session_id: str
    confirmed: bool
    override_type: Optional[str] = None  # User can manually select type


@app.post("/api/v1/confirm-classification")
async def confirm_classification(confirmation: ClassificationConfirmation):
    """
    User confirms or overrides dataset classification.
    
    v2.0 CRITICAL: This endpoint MUST be called before preprocessing.
    """
    if confirmation.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[confirmation.session_id]
    
    if not session.get('classification'):
        raise HTTPException(status_code=400, detail="Dataset not yet analyzed. Call /analyze first.")
    
    if confirmation.confirmed:
        session['classification_confirmed'] = True
        
        # If user provided override type, update classification
        if confirmation.override_type:
            session['classification']['type'] = confirmation.override_type
            session['classification']['confidence'] = 1.0  # User override is 100% confident
            session['classification']['description'] = f"Manually classified as {confirmation.override_type}"
        
        return {
            "status": "confirmed",
            "classification_type": session['classification']['type'],
            "message": f"Classification confirmed as {session['classification']['type']}. Ready for preprocessing.",
            "preprocessing_suggestions": session['classification']['suggestions']
        }
    else:
        # User rejected classification - provide options
        return {
            "status": "rejected",
            "message": "Classification rejected. Please select a dataset type manually.",
            "available_types": ["Financial", "Sales", "Time-Series", "Healthcare", "Generic"]
        }


# Legacy endpoints (v1.0 - kept for backward compatibility but deprecated)
@app.post("/chart")
async def generate_chart_legacy(csv: str):
    """DEPRECATED: Use v2.0 visualization recommendations instead."""
    try:
        df = pd.read_csv(io.StringIO(csv))
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

        if len(numeric_cols) >= 1 and len(cat_cols) >= 1:
            fig = px.bar(df, x=cat_cols[0], y=numeric_cols[0])
        elif len(numeric_cols) >= 2:
            fig = px.line(df, x=numeric_cols[0], y=numeric_cols[1])
        else:
            return {"error": "Not enough numeric/categorical columns for auto visualization."}

        return {"plotly_json": fig.to_json()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insights")
async def generate_insights_legacy(csv: str, chart_desc: str = ""):
    """DEPRECATED: Use v2.0 insights generation with domain context."""
        
        # Store classification in session
        session['classification'] = {
            'type': classification.type,
            'confidence': classification.confidence,
            'description': classification.description,
            'features': classification.features,
            'suggestions': classification.suggestions
        }
        
        # 2. Profile columns
        profiler = ColumnProfiler(df)
        column_profiles = profiler.profile_all_columns()
        
        # 3. Assess quality
        scorer = QualityScorer(df, column_profiles)
        quality_report = scorer.assess_quality()
        
        # 4. Detect relationships (basic correlations for now)
        correlations = []
        numeric_cols = [col for col, profile in column_profiles.items() 
                       if profile['type'] == 'numeric']
        
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.3:  # Only significant correlations
                        correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'value': float(corr_value)
                        })
        
        return {
            "session_id": session_id,
            "classification": session['classification'],
            "columns": column_profiles,
            "quality": {
                "overall": quality_report.overall_score,
                "breakdown": {
                    "completeness": quality_report.completeness,
                    "validity": quality_report.validity,
                    "consistency": quality_report.consistency,
                    "uniqueness": quality_report.uniqueness
                },
                "issues": quality_report.issues,
                "recommendations": quality_report.recommendations
            },
            "relationships": correlations,
            "summary": profiler.get_summary(),
            "status": "analyzed",
            "message": "Dataset analyzed. Please confirm classification before preprocessing."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/insights")
async def generate_insights(csv: str, chart_desc: str = ""):
    try:
        df = pd.read_csv(io.StringIO(csv))
        df_head = df.head(10).to_string()
        prompt = f"Summarize insights from this dataset:\n{chart_desc}\n\n{df_head}"
        ai_summary = call_lmstudio(prompt)
        return {"insights": ai_summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
