# backend/main.py - EchoBI v2.0 Backend API
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import pandas as pd
import io
import uuid
from datetime import datetime

from core import ColumnProfiler, DatasetClassifier, QualityScorer

app = FastAPI(title="EchoBI v2.0 Backend", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

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
        
        classifier = DatasetClassifier(df)
        classification = classifier.classify()
        
        session['classification'] = {
            'type': classification.type,
            'confidence': classification.confidence,
            'description': classification.description,
            'features': classification.features,
            'suggestions': classification.suggestions
        }
        
        profiler = ColumnProfiler(df)
        column_profiles = profiler.profile_all_columns()
        
        scorer = QualityScorer(df, column_profiles)
        quality_report = scorer.assess_quality()
        
        correlations = []
        numeric_cols = [col for col, profile in column_profiles.items() if profile['type'] == 'numeric']
        
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.3:
                        correlations.append({'column1': col1, 'column2': col2, 'value': float(corr_value)})
        
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
            "status": "analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
            session['classification']['type'] = confirmation.override_type
            session['classification']['confidence'] = 1.0
        
        return {"status": "confirmed", "classification_type": session['classification']['type']}
    else:
        return {"status": "rejected", "available_types": ["Financial", "Sales", "Time-Series", "Healthcare", "Generic"]}
