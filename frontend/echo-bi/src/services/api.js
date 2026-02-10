// src/services/api.js
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/api/v1/upload`, { method: "POST", body: form });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed: ${res.statusText}`);
  }
  
  return res.json();
}

export async function analyzeDataset(sessionId) {
  const res = await fetch(`${BASE}/api/v1/analyze/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analysis failed: ${res.statusText}`);
  }
  
  return res.json();
}

export async function confirmClassification(sessionId, confirmed = true, overrideType = null) {
  const res = await fetch(`${BASE}/api/v1/confirm-classification`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      confirmed: confirmed,
      override_type: overrideType
    })
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Classification confirmation failed: ${res.statusText}`);
  }
  
  return res.json();
}

export async function getAvailableTypes() {
  const res = await fetch(`${BASE}/api/v1/available-types`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch available types: ${res.statusText}`);
  }
  
  return res.json();
}

export async function getInsights(sessionId, useAI = false) {
  const res = await fetch(`${BASE}/api/v1/insights/${sessionId}?use_ai=${useAI}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch insights: ${res.statusText}`);
  }
  
  return res.json();
}

export async function getVisualizationRecommendations(sessionId) {
  const res = await fetch(`${BASE}/api/v1/visualizations/recommendations/${sessionId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch recommendations: ${res.statusText}`);
  }
  
  return res.json();
}

export async function generateChart(sessionId, chartId = null, chartType = null, config = null) {
  const payload = { session_id: sessionId };
  
  if (chartId) {
    payload.chart_id = chartId;
  }
  if (chartType) {
    payload.chart_type = chartType;
  }
  if (config) {
    payload.config = config;
  }
  
  const res = await fetch(`${BASE}/api/v1/visualizations/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chart generation failed: ${res.statusText}`);
  }
  
  return res.json();
}

// Get preprocessing suggestions
export async function getPreprocessingSuggestions(sessionId) {
  const res = await fetch(`${BASE}/api/v1/preprocessing/suggestions/${sessionId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch preprocessing suggestions: ${res.statusText}`);
  }
  
  return res.json();
}

// Preview preprocessing operations (dry run)
export async function previewPreprocessing(sessionId, operationIds) {
  const res = await fetch(`${BASE}/api/v1/preprocess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      operation_ids: operationIds,
      preview_only: true
    })
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Preprocessing preview failed: ${res.statusText}`);
  }
  
  return res.json();
}

// Apply preprocessing operations
export async function applyPreprocessing(sessionId, operationIds) {
  const res = await fetch(`${BASE}/api/v1/preprocess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      operation_ids: operationIds,
      preview_only: false
    })
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Preprocessing failed: ${res.statusText}`);
  }
  
  return res.json();
}

// Rollback preprocessing
export async function rollbackPreprocessing(sessionId, operationId = null) {
  const res = await fetch(`${BASE}/api/v1/preprocess/rollback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      operation_id: operationId
    })
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Rollback failed: ${res.statusText}`);
  }
  
  return res.json();
}

// Get analysis data (includes column profiles with missing data stats)
export async function getAnalysisData(sessionId) {
  const res = await fetch(`${BASE}/api/v1/analyze/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch analysis data: ${res.statusText}`);
  }
  
  return res.json();
}

// Chat API functions
export async function sendChatMessage(sessionId, message, conversationHistory = []) {
  const res = await fetch(`${BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
      conversation_history: conversationHistory
    })
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chat request failed: ${res.statusText}`);
  }
  
  return res.json();
}

export async function getChatHistory(sessionId) {
  const res = await fetch(`${BASE}/api/v1/chat/history/${sessionId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch chat history: ${res.statusText}`);
  }
  
  return res.json();
}

export async function clearChatHistory(sessionId) {
  const res = await fetch(`${BASE}/api/v1/chat/history/${sessionId}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to clear chat history: ${res.statusText}`);
  }
  
  return res.json();
}

// ============================================
// AI Summary Functions
// ============================================

export async function getAIDatasetSummary(sessionId) {
  const res = await fetch(`${BASE}/api/v1/ai-summary/dataset/${sessionId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to generate AI dataset summary: ${res.statusText}`);
  }
  
  return res.json();
}

export async function getAIPreprocessingSummary(sessionId) {
  const res = await fetch(`${BASE}/api/v1/ai-summary/preprocessing/${sessionId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to generate AI preprocessing summary: ${res.statusText}`);
  }
  
  return res.json();
}

// Get preprocessing comparison (before/after data quality)
export async function getPreprocessingComparison(sessionId) {
  const res = await fetch(`${BASE}/api/v1/preprocessing/comparison/${sessionId}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" }
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch preprocessing comparison: ${res.statusText}`);
  }
  
  return res.json();
}

// ============================================
// Download Functions
// ============================================

export async function downloadDataset(sessionId, format = 'csv') {
  const res = await fetch(`${BASE}/api/v1/download/${sessionId}?format=${format}`, {
    method: "GET"
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to download dataset: ${res.statusText}`);
  }
  
  // Get filename from Content-Disposition header
  const contentDisposition = res.headers.get('Content-Disposition');
  let filename = `dataset.${format}`;
  if (contentDisposition) {
    const match = contentDisposition.match(/filename=(.+)/);
    if (match) {
      filename = match[1];
    }
  }
  
  // Create blob and trigger download
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
  
  return { success: true, filename };
}

// Legacy functions for backward compatibility
export async function generateInsights(csv, chart_desc = "") {
  const res = await fetch(`${BASE}/insights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ csv, chart_desc }),
  });
  return res.json();
}
