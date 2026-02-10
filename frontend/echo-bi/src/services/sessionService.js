// src/services/sessionService.js
// Session persistence service using localStorage

const SESSION_KEY = 'echobi_session';

export const sessionService = {
  // Save session data
  saveSession(data) {
    const sessionData = {
      sessionId: data.sessionId,
      fileName: data.fileName,
      uploadedAt: data.uploadedAt || new Date().toISOString(),
      classification: data.classification || null,
      classificationConfirmed: data.classificationConfirmed || false,
      preprocessingComplete: data.preprocessingComplete || false,
      preprocessingResult: data.preprocessingResult || null,
      preprocessingSkipped: data.preprocessingSkipped || false,
      preprocessingOperations: data.preprocessingOperations || [],
      auditTrail: data.auditTrail || [],
      preview: data.preview || null,
      summary: data.summary || null,
      quality: data.quality || null,
      columns: data.columns || null,
      relationships: data.relationships || null
    };
    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    return sessionData;
  },

  // Get current session
  getSession() {
    const stored = localStorage.getItem(SESSION_KEY);
    if (!stored) return null;
    
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  },

  // Update specific session fields
  updateSession(updates) {
    const current = this.getSession();
    if (!current) return null;
    
    const updated = { ...current, ...updates };
    localStorage.setItem(SESSION_KEY, JSON.stringify(updated));
    return updated;
  },

  // Check if session exists and is valid
  hasValidSession() {
    const session = this.getSession();
    return session && session.sessionId;
  },

  // Get session ID
  getSessionId() {
    const session = this.getSession();
    return session?.sessionId || null;
  },

  // Check if classification is confirmed
  isClassificationConfirmed() {
    const session = this.getSession();
    return session?.classificationConfirmed || false;
  },

  // Confirm classification
  confirmClassification() {
    return this.updateSession({ classificationConfirmed: true });
  },

  // Mark preprocessing as complete
  markPreprocessingComplete() {
    return this.updateSession({ preprocessingComplete: true });
  },

  // Get preprocessing info
  getPreprocessingInfo() {
    const session = this.getSession();
    if (!session) return null;
    return {
      complete: session.preprocessingComplete || false,
      skipped: session.preprocessingSkipped || false,
      result: session.preprocessingResult || null,
      operations: session.preprocessingOperations || [],
      auditTrail: session.auditTrail || []
    };
  },

  // Clear session
  clearSession() {
    localStorage.removeItem(SESSION_KEY);
  },

  // Get workflow status
  getWorkflowStatus() {
    const session = this.getSession();
    if (!session) {
      return {
        step: 0,
        label: 'No Dataset',
        canAccessAnalysis: false,
        canAccessPreprocessing: false,
        canAccessInsights: false,
        canAccessDashboard: false
      };
    }

    if (!session.classificationConfirmed) {
      return {
        step: 1,
        label: 'Awaiting Classification Confirmation',
        canAccessAnalysis: true,
        canAccessPreprocessing: false,
        canAccessInsights: false,
        canAccessDashboard: false
      };
    }

    if (!session.preprocessingComplete) {
      return {
        step: 2,
        label: 'Ready for Preprocessing',
        canAccessAnalysis: true,
        canAccessPreprocessing: true,
        canAccessInsights: false,
        canAccessDashboard: false
      };
    }

    return {
      step: 3,
      label: 'Ready for Analysis',
      canAccessAnalysis: true,
      canAccessPreprocessing: true,
      canAccessInsights: true,
      canAccessDashboard: true
    };
  }
};

export default sessionService;
