# backend.py
import io
import uuid
import pickle
import tempfile
import traceback
from typing import Dict, Any

import numpy as np
import pandas as pd
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scipy import stats
from gtts import gTTS
import uvicorn

# ---------------------------
# Configuration
# ---------------------------
LM_STUDIO_API = "http://localhost:1234/v1/chat/completions"
CHART_MODEL_PATH = "chart_recommender.pkl"  # ensure this exists in the same dir

app = FastAPI(title="ECHO-BI Backend (Phase 2)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for DataFrames (simple; replace with persistent storage for prod)
DATASTORE: Dict[str, pd.DataFrame] = {}

# Load XGBoost chart recommender
try:
    with open(CHART_MODEL_PATH, "rb") as f:
        CHART_MODEL = pickle.load(f)
except Exception as e:
    CHART_MODEL = None
    print("Warning: chart_recommender.pkl not found or failed to load:", e)


# ---------------------------
# Helpers
# ---------------------------
def df_to_preview_rows(df: pd.DataFrame, n: int = 8):
    return df.head(n).fillna("").to_dict(orient="records")


def make_features_for_recommender(df: pd.DataFrame) -> Dict[str, Any]:
    numeric = df.select_dtypes(include=["number"])
    categorical = df.select_dtypes(include=["object", "category", "bool"])
    num_numeric = numeric.shape[1]
    num_categorical = categorical.shape[1]
    row_count = df.shape[0]
    col_count = df.shape[1]
    # skewness - mean absolute skew of numeric columns (fill 0 if none)
    if num_numeric > 0:
        skewness = float(np.nanmean(numeric.skew().abs().replace([np.inf, -np.inf], np.nan).fillna(0)))
    else:
        skewness = 0.0
    return {
        "num_numeric": num_numeric,
        "num_categorical": num_categorical,
        "row_count": row_count,
        "col_count": col_count,
        "skewness": skewness,
    }


def call_lmstudio(prompt: str, model: str = "gpt-3.5", temperature: float = 0.2):
    try:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        r = requests.post(LM_STUDIO_API, json=payload, timeout=30)
        r.raise_for_status()
        j = r.json()
        return j["choices"][0]["message"]["content"]
    except Exception as e:
        traceback.print_exc()
        return f"LM Studio error: {e}"


# ---------------------------
# Request models
# ---------------------------
class RecommendRequest(BaseModel):
    dataset_id: str


class ChartDataRequest(BaseModel):
    dataset_id: str
    chart_type: str


class DatasetRequest(BaseModel):
    dataset_id: str


class AskRequest(BaseModel):
    dataset_id: str
    question: str


class TTSRequest(BaseModel):
    text: str


# ---------------------------
# Endpoints
# ---------------------------
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        ext = file.filename.lower().split(".")[-1]
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(content))
        elif ext in ("xls", "xlsx"):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Basic cleaning: dropna + dedupe (same as Streamlit prototype)
        df_clean = df.dropna().drop_duplicates().reset_index(drop=True)

        dataset_id = str(uuid.uuid4())
        DATASTORE[dataset_id] = df_clean

        resp = {
            "id": dataset_id,
            "previewRows": df_to_preview_rows(df_clean, n=8),
            "columns": list(df_clean.columns.astype(str)),
            "rowCount": int(df_clean.shape[0])
        }
        return JSONResponse(resp)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommend")
def recommend(req: RecommendRequest):
    dataset_id = req.dataset_id
    if dataset_id not in DATASTORE:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = DATASTORE[dataset_id]
    features = make_features_for_recommender(df)
    if CHART_MODEL is None:
        # Fallback heuristics if model missing
        if features["num_categorical"] >= 1 and features["num_numeric"] >= 1:
            chart_type = "bar"
            reason = "Fallback: has categorical and numeric columns."
        elif features["num_numeric"] >= 2:
            chart_type = "line"
            reason = "Fallback: multiple numeric columns; time/sequence trend likely."
        elif features["num_numeric"] == 1:
            chart_type = "histogram"
            reason = "Fallback: single numeric column; histogram useful."
        else:
            chart_type = "scatter"
            reason = "Fallback: default scatter."
    else:
        # Prepare vector; assumes model expects features in a known order
        # try to be flexible to handle both pandas and raw arrays
        try:
            # If model is scikit-like: accept a 2D array
            X = [[
                features["num_numeric"],
                features["num_categorical"],
                features["skewness"],
                features["row_count"],
                features["col_count"]
            ]]
            pred = CHART_MODEL.predict(X)
            # model might return index or string
            chart_type = str(pred[0])
            reason = "Predicted by chart_recommender.pkl"
        except Exception:
            chart_type = "bar"
            reason = "Model prediction failed; using bar fallback."

    return {"chart_type": chart_type, "reason": reason, "features": features}


@app.post("/api/chartdata")
def chartdata(req: ChartDataRequest):
    dataset_id = req.dataset_id
    chart_type = req.chart_type
    if dataset_id not in DATASTORE:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = DATASTORE[dataset_id]
    try:
        numeric = df.select_dtypes(include=["number"])
        categorical = df.select_dtypes(include=["object", "category", "bool"])

        if chart_type == "bar":
            if categorical.shape[1] == 0 or numeric.shape[1] == 0:
                raise HTTPException(status_code=400, detail="Need at least 1 categorical and 1 numeric column for bar chart")
            x = categorical.columns[0]
            y = numeric.columns[0]
            agg = df.groupby(x)[y].sum().reset_index().rename(columns={x: "x", y: "y"})
            chart_data = agg.to_dict(orient="records")
            return {"chartData": chart_data}

        if chart_type == "line":
            # line: pick two numeric columns or use index
            if numeric.shape[1] >= 2:
                x = numeric.columns[0]
                y = numeric.columns[1]
                chart_data = df[[x, y]].rename(columns={x: "x", y: "y"}).dropna().to_dict(orient="records")
            elif numeric.shape[1] == 1 and categorical.shape[1] >= 1:
                x = categorical.columns[0]
                y = numeric.columns[0]
                chart_data = df.groupby(x)[y].sum().reset_index().rename(columns={x: "x", y: "y"}).to_dict(orient="records")
            else:
                raise HTTPException(status_code=400, detail="Not enough numeric columns for line chart")
            return {"chartData": chart_data}

        if chart_type == "scatter":
            if numeric.shape[1] < 2:
                raise HTTPException(status_code=400, detail="Need at least 2 numeric columns for scatter")
            x = numeric.columns[0]
            y = numeric.columns[1]
            chart_data = df[[x, y]].rename(columns={x: "x", y: "y"}).dropna().to_dict(orient="records")
            return {"chartData": chart_data}

        if chart_type == "histogram":
            if numeric.shape[1] == 0:
                raise HTTPException(status_code=400, detail="Need numeric column for histogram")
            col = numeric.columns[0]
            vals = df[col].dropna().values
            counts, bins = np.histogram(vals, bins='auto')
            bins_center = (bins[:-1] + bins[1:]) / 2
            chart_data = [{"bin": float(bins_center[i]), "count": int(counts[i])} for i in range(len(counts))]
            return {"chartData": chart_data}

        # default: return first few rows
        return {"chartData": df.head(200).fillna("").to_dict(orient="records")}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/insights")
def insights(req: DatasetRequest):
    dataset_id = req.dataset_id
    if dataset_id not in DATASTORE:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = DATASTORE[dataset_id]

    try:
        sample = df.head(10).to_string()
        prompt = f"Summarize insights from this dataset. Provide top 5 observations, notable correlations, and any anomalies. Data preview:\n\n{sample}"
        summary = call_lmstudio(prompt)
        # also compute basic correlation matrix for numeric columns
        numeric = df.select_dtypes(include=["number"])
        corr = None
        if numeric.shape[1] >= 2:
            corr_df = numeric.corr().round(3)
            corr = corr_df.to_dict()
        return {"summary": summary, "correlations": corr}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/outliers")
def outliers(req: DatasetRequest):
    dataset_id = req.dataset_id
    if dataset_id not in DATASTORE:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = DATASTORE[dataset_id]
    numeric = df.select_dtypes(include=["number"])
    if numeric.shape[1] == 0:
        return {"outlierRows": []}
    try:
        zscores = np.abs(stats.zscore(numeric.fillna(numeric.mean())))
        # zscores may be 1D if single column; normalize to 2D
        if zscores.ndim == 1:
            zscores = zscores.reshape(-1, 1)
        outlier_mask = (zscores > 3).any(axis=1)
        outliers_df = df.loc[outlier_mask]
        return {"outlierRows": outliers_df.head(200).fillna("").to_dict(orient="records")}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask")
def ask(req: AskRequest):
    dataset_id = req.dataset_id
    question = req.question
    if dataset_id not in DATASTORE:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = DATASTORE[dataset_id]
    try:
        sample = df.head(12).to_string()
        prompt = f"You are an analytics assistant. Answer this question based on the data preview below. If you need more info, ask for it. Data preview:\n\n{sample}\n\nQuestion: {question}"
        ans = call_lmstudio(prompt)
        return {"answer": ans}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts")
def tts(req: TTSRequest):
    text = req.text
    if not text:
        raise HTTPException(status_code=400, detail="Text required")
    try:
        tts = gTTS(text)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp.name)
        mp3_bytes = open(tmp.name, "rb").read()
        return StreamingResponse(io.BytesIO(mp3_bytes), media_type="audio/mpeg")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Simple health
@app.get("/api/health")
def health():
    return {"status": "ok", "datasets_loaded": len(DATASTORE)}


if __name__ == "__main__":
    # dev mode
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
