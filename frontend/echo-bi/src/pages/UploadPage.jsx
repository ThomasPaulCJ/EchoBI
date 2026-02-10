// src/pages/UploadPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Button, Badge, Loader } from "../components/common";
import { UploadZone, UploadProgress, FileInfoCard, UploadError } from "../components/upload";
import { PreprocessingConfirmation } from "../components/preprocessing";
import PreviewTable from "../components/PreviewTable";
import { uploadFile, analyzeDataset, confirmClassification, downloadDataset } from "../services/api";
import sessionService from "../services/sessionService";
import "./UploadPage.css";

// Available dataset types with descriptions
const AVAILABLE_TYPES = [
  { type: 'Financial', description: 'Financial transactions, accounting, banking, investments', icon: '💰' },
  { type: 'Sales', description: 'Products, customers, orders, retail, e-commerce', icon: '🛒' },
  { type: 'Time-Series', description: 'Temporal data, trends, forecasting, sequential', icon: '📈' },
  { type: 'Healthcare', description: 'Medical records, diagnoses, treatments, clinical data', icon: '🏥' },
  { type: 'Marketing', description: 'Campaigns, leads, conversions, engagement metrics', icon: '📢' },
  { type: 'HR', description: 'Employees, payroll, attendance, workforce management', icon: '👥' },
  { type: 'Logistics', description: 'Shipping, inventory, warehouses, supply chain', icon: '🚚' },
  { type: 'Generic', description: 'No specific domain - apply general analysis', icon: '📊' },
];

export default function UploadPage() {
  const navigate = useNavigate();
  
  // File selection state
  const [selectedFile, setSelectedFile] = useState(null);
  
  // Upload status states
  // Steps: idle → uploading → classifying → awaiting_confirmation → selecting_type → awaiting_preprocessing → preprocessing_apply → complete
  const [currentStep, setCurrentStep] = useState('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  
  // Data states
  const [uploadedData, setUploadedData] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [classification, setClassification] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [preprocessingResult, setPreprocessingResult] = useState(null);
  const [downloading, setDownloading] = useState(false);
  
  // Manual type selection state
  const [selectedManualType, setSelectedManualType] = useState(null);

  // Load existing session on mount
  useEffect(() => {
    const existingSession = sessionService.getSession();
    if (existingSession && existingSession.sessionId) {
      setSessionId(existingSession.sessionId);
      setClassification(existingSession.classification);
      setUploadedData(existingSession.preview);
      setAnalysisResult({
        classification: existingSession.classification,
        quality: existingSession.quality,
        columns: existingSession.columns
      });
      
      if (existingSession.classificationConfirmed) {
        setCurrentStep('complete');
      } else if (existingSession.classification) {
        setCurrentStep('awaiting_confirmation');
      }
    }
  }, []);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
    setCurrentStep('idle');
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setError(null);
    setCurrentStep('uploading');
    setStatusMessage('Uploading file to server...');
    setUploadProgress(0);

    try {
      // Step 1: Upload file
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 15, 40));
      }, 200);

      const uploadResponse = await uploadFile(selectedFile);
      clearInterval(progressInterval);
      setUploadProgress(50);
      
      const newSessionId = uploadResponse.session_id;
      setSessionId(newSessionId);

      if (uploadResponse.preview) {
        setUploadedData(uploadResponse.preview);
      }

      // Step 2: Run classification
      setCurrentStep('classifying');
      setStatusMessage('Running dataset classification engine...');
      setUploadProgress(60);

      const analysisResponse = await analyzeDataset(newSessionId);
      setUploadProgress(90);
      
      setAnalysisResult(analysisResponse);
      setClassification(analysisResponse.classification);

      // Save to session storage
      sessionService.saveSession({
        sessionId: newSessionId,
        fileName: selectedFile.name,
        classification: analysisResponse.classification,
        preview: uploadResponse.preview,
        summary: uploadResponse.summary,
        quality: analysisResponse.quality,
        columns: analysisResponse.columns,
        relationships: analysisResponse.relationships,
        classificationConfirmed: false
      });

      setUploadProgress(100);
      setCurrentStep('awaiting_confirmation');
      setStatusMessage('Classification complete! Please confirm or adjust the detected dataset type.');

    } catch (err) {
      setError(err.message || 'Upload failed');
      setCurrentStep('idle');
      console.error("Upload error:", err);
    }
  };

  const handleConfirmClassification = async (overrideType = null) => {
    // Update local classification if overridden
    if (overrideType) {
      const updatedClassification = {
        ...classification,
        type: overrideType,
        confidence: 1.0,
        user_override: true,
        description: `Manually classified as ${overrideType} by user.`
      };
      setClassification(updatedClassification);
      sessionService.updateSession({ classification: updatedClassification });
    }

    try {
      // Call backend to confirm classification (with optional override)
      if (sessionId) {
        await confirmClassification(sessionId, true, overrideType);
      }
    } catch (err) {
      console.warn('Classification confirmation API error:', err);
      // Continue anyway - session service handles local state
    }

    sessionService.confirmClassification();

    // Move to preprocessing confirmation step
    setCurrentStep('awaiting_preprocessing');
    setStatusMessage('Review and confirm preprocessing operations for your dataset.');
  };

  // Handle preprocessing completion
  const handlePreprocessingComplete = (result) => {
    setPreprocessingResult(result);
    
    // Save preprocessing result to session
    sessionService.updateSession({
      preprocessingResult: result,
      preprocessingSkipped: result.skipped,
      preprocessingOperations: result.operations || [],
      auditTrail: result.auditTrail || []
    });
    sessionService.markPreprocessingComplete();
    
    setCurrentStep('complete');
    setStatusMessage('Dataset ready! You can now explore insights and visualizations.');
  };

  // Handle preprocessing skip
  const handlePreprocessingSkip = () => {
    setPreprocessingResult({ skipped: true, operations: [] });
    sessionService.updateSession({
      preprocessingResult: { skipped: true },
      preprocessingSkipped: true,
      preprocessingOperations: []
    });
    sessionService.markPreprocessingComplete();
    
    setCurrentStep('complete');
    setStatusMessage('Dataset ready! You can now explore insights and visualizations.');
  };

  const handleRejectClassification = () => {
    // Show manual type selection UI
    setCurrentStep('selecting_type');
    setSelectedManualType(null);
    setStatusMessage('Select the correct dataset type below:');
  };

  const handleManualTypeSelect = (type) => {
    setSelectedManualType(type);
  };

  const handleConfirmManualType = async () => {
    if (selectedManualType) {
      await handleConfirmClassification(selectedManualType);
    }
  };

  const handleCancelManualSelection = () => {
    setCurrentStep('awaiting_confirmation');
    setSelectedManualType(null);
    setStatusMessage('Classification complete! Please confirm or adjust the detected dataset type.');
  };

  const handleClearSession = () => {
    sessionService.clearSession();
    setSelectedFile(null);
    setUploadedData(null);
    setSessionId(null);
    setClassification(null);
    setAnalysisResult(null);
    setSelectedManualType(null);
    setCurrentStep('idle');
    setStatusMessage('');
    setUploadProgress(0);
    setError(null);
  };

  const handleDownload = async (format = 'csv') => {
    if (!sessionId) return;
    
    try {
      setDownloading(true);
      await downloadDataset(sessionId, format);
    } catch (err) {
      console.error('Download error:', err);
      setError(`Download failed: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const getStepNumber = () => {
    switch (currentStep) {
      case 'uploading': return 1;
      case 'classifying': return 2;
      case 'awaiting_confirmation': 
      case 'selecting_type': return 3;
      case 'awaiting_preprocessing':
      case 'preprocessing_apply': return 4;
      case 'complete': return 5;
      default: return 0;
    }
  };

  const getDatasetTypeIcon = (type) => {
    const typeInfo = AVAILABLE_TYPES.find(t => t.type === type);
    return typeInfo?.icon || '📊';
  };

  return (
    <div className="upload-page">
      <h1 className="page-title">Upload Dataset</h1>
      
      {/* Workflow Progress Indicator */}
      {currentStep !== 'idle' && (
        <Card className="workflow-progress-card">
          <div className="workflow-steps">
            <div className={`workflow-step ${getStepNumber() >= 1 ? 'active' : ''} ${getStepNumber() > 1 ? 'completed' : ''}`}>
              <div className="step-number">1</div>
              <div className="step-label">Upload</div>
            </div>
            <div className="step-connector"></div>
            <div className={`workflow-step ${getStepNumber() >= 2 ? 'active' : ''} ${getStepNumber() > 2 ? 'completed' : ''}`}>
              <div className="step-number">2</div>
              <div className="step-label">Classify</div>
            </div>
            <div className="step-connector"></div>
            <div className={`workflow-step ${getStepNumber() >= 3 ? 'active' : ''} ${getStepNumber() > 3 ? 'completed' : ''}`}>
              <div className="step-number">3</div>
              <div className="step-label">Confirm</div>
            </div>
            <div className="step-connector"></div>
            <div className={`workflow-step ${getStepNumber() >= 4 ? 'active' : ''} ${getStepNumber() > 4 ? 'completed' : ''}`}>
              <div className="step-number">4</div>
              <div className="step-label">Preprocess</div>
            </div>
            <div className="step-connector"></div>
            <div className={`workflow-step ${getStepNumber() >= 5 ? 'active' : ''}`}>
              <div className="step-number">5</div>
              <div className="step-label">Ready</div>
            </div>
          </div>
          {statusMessage && (
            <div className="workflow-status">
              {(currentStep === 'uploading' || currentStep === 'classifying' || currentStep === 'preprocessing_apply') && (
                <Loader size="small" />
              )}
              <span>{statusMessage}</span>
            </div>
          )}
        </Card>
      )}

      {/* Upload Section */}
      {currentStep !== 'complete' && currentStep !== 'awaiting_confirmation' && currentStep !== 'selecting_type' && (
        <Card title="📤 Upload File">
          <UploadZone 
            onFileSelect={handleFileSelect}
            isUploading={currentStep === 'uploading' || currentStep === 'classifying'}
          />

          {selectedFile && currentStep === 'idle' && (
            <div className="upload-actions">
              <Button 
                variant="primary" 
                onClick={handleUpload}
                size="large"
              >
                Upload & Analyze
              </Button>
            </div>
          )}

          {(currentStep === 'uploading' || currentStep === 'classifying') && (
            <div className="upload-progress-container">
              <UploadProgress 
                progress={uploadProgress}
                status={currentStep}
              />
            </div>
          )}
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="error-card">
          <div className="error-content">
            <span className="error-icon">❌</span>
            <div className="error-text">
              <strong>Upload Failed</strong>
              <p>{error}</p>
            </div>
            <Button variant="primary" onClick={handleUpload}>
              Retry
            </Button>
          </div>
        </Card>
      )}

      {/* Classification Confirmation Section */}
      {currentStep === 'awaiting_confirmation' && classification && (
        <Card title="🔍 Dataset Classification" className="classification-card">
          <div className="classification-result">
            <div className="classification-header">
              <div className="classification-type">
                <span className="type-icon">{getDatasetTypeIcon(classification.type)}</span>
                <div className="type-info">
                  <h3>Detected Type: {classification.type}</h3>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{ width: `${(classification.confidence || 0.85) * 100}%` }}
                    ></div>
                  </div>
                  <span className="confidence-label">
                    Confidence: {((classification.confidence || 0.85) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <Badge variant={classification.confidence > 0.8 ? 'success' : 'warning'}>
                {classification.confidence > 0.8 ? 'High Confidence' : 'Medium Confidence'}
              </Badge>
            </div>

            {classification.reasons && classification.reasons.length > 0 && (
              <div className="classification-reasons">
                <h4>Detection Reasons:</h4>
                <ul>
                  {classification.reasons.map((reason, idx) => (
                    <li key={idx}>✓ {reason}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="classification-actions">
              <p className="confirmation-prompt">
                <strong>Please confirm this classification to proceed with domain-specific preprocessing:</strong>
              </p>
              <div className="action-buttons">
                <Button 
                  variant="primary" 
                  onClick={() => handleConfirmClassification(null)}
                  size="large"
                >
                  ✅ Confirm Classification
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={handleRejectClassification}
                >
                  🔄 Choose Different Type
                </Button>
              </div>
              <div className="start-over-section">
                <Button 
                  variant="danger" 
                  onClick={handleClearSession}
                  size="small"
                >
                  🗑️ Remove Dataset & Start Over
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Manual Type Selection Section */}
      {currentStep === 'selecting_type' && (
        <Card title="📋 Select Dataset Type" className="type-selection-card">
          <div className="type-selection-content">
            <p className="selection-prompt">
              The classifier detected <strong>{classification?.type}</strong>, but you can select a different type below:
            </p>
            
            {/* All Scores Display */}
            {classification?.all_scores && (
              <div className="all-scores-section">
                <h4>Classification Scores by Domain:</h4>
                <div className="scores-grid">
                  {Object.entries(classification.all_scores)
                    .sort(([,a], [,b]) => b - a)
                    .map(([domain, score]) => (
                      <div key={domain} className={`score-item ${domain === classification.type ? 'detected' : ''}`}>
                        <span className="score-domain">{getDatasetTypeIcon(domain)} {domain}</span>
                        <div className="score-bar-container">
                          <div className="score-bar" style={{ width: `${score * 100}%` }}></div>
                        </div>
                        <span className="score-value">{(score * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                </div>
              </div>
            )}
            
            <div className="type-grid">
              {AVAILABLE_TYPES.map((typeInfo) => (
                <div 
                  key={typeInfo.type}
                  className={`type-option ${selectedManualType === typeInfo.type ? 'selected' : ''} ${typeInfo.type === classification?.type ? 'original' : ''}`}
                  onClick={() => handleManualTypeSelect(typeInfo.type)}
                >
                  <div className="type-option-icon">{typeInfo.icon}</div>
                  <div className="type-option-info">
                    <h4>{typeInfo.type}</h4>
                    <p>{typeInfo.description}</p>
                  </div>
                  {typeInfo.type === classification?.type && (
                    <Badge variant="warning" className="original-badge">Detected</Badge>
                  )}
                  {selectedManualType === typeInfo.type && (
                    <span className="selected-check">✓</span>
                  )}
                </div>
              ))}
            </div>
            
            <div className="selection-actions">
              <Button 
                variant="primary" 
                onClick={handleConfirmManualType}
                disabled={!selectedManualType}
                size="large"
              >
                ✅ Confirm {selectedManualType || 'Selection'}
              </Button>
              <Button 
                variant="secondary" 
                onClick={handleCancelManualSelection}
              >
                ← Back to Auto-Detection
              </Button>
            </div>
            <div className="start-over-section">
              <Button 
                variant="danger" 
                onClick={handleClearSession}
                size="small"
              >
                🗑️ Remove Dataset & Start Over
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Preprocessing Confirmation Section */}
      {currentStep === 'awaiting_preprocessing' && sessionId && (
        <PreprocessingConfirmation
          sessionId={sessionId}
          datasetType={classification?.type || 'Generic'}
          columns={analysisResult?.columns || {}}
          quality={analysisResult?.quality || {}}
          onComplete={handlePreprocessingComplete}
          onSkip={handlePreprocessingSkip}
        />
      )}

      {/* Data Preview */}
      {uploadedData && (
        <Card title="👀 Data Preview">
          <PreviewTable data={uploadedData} />
        </Card>
      )}

      {/* Success State */}
      {currentStep === 'complete' && (
        <Card title="✅ Dataset Ready" className="success-card">
          <div className="success-content">
            <div className="success-icon">🎉</div>
            <div className="success-text">
              <h3>Your dataset is ready for analysis!</h3>
              <p>Classification confirmed and preprocessing complete. You can now explore insights and create visualizations.</p>
              {classification && (
                <Badge variant="success">
                  {getDatasetTypeIcon(classification.type)} {classification.type} Dataset
                </Badge>
              )}
            </div>
          </div>

          {/* Download Section */}
          <div className="download-section">
            <h4>📥 Download Preprocessed Dataset</h4>
            <p className="download-description">
              Download your cleaned and preprocessed dataset in your preferred format.
            </p>
            <div className="download-buttons">
              <Button 
                variant="secondary"
                onClick={() => handleDownload('csv')}
                disabled={downloading}
              >
                {downloading ? '⏳ Downloading...' : '📄 Download CSV'}
              </Button>
              <Button 
                variant="secondary"
                onClick={() => handleDownload('xlsx')}
                disabled={downloading}
              >
                {downloading ? '⏳ Downloading...' : '📊 Download Excel'}
              </Button>
            </div>
          </div>
          
          <div className="next-steps">
            <h4>What would you like to do next?</h4>
            <div className="next-buttons">
              <Button 
                variant="primary" 
                onClick={() => navigate('/analysis')}
                size="large"
              >
                📊 View Analysis Details
              </Button>
              <Button 
                variant="primary" 
                onClick={() => navigate('/insights')}
                size="large"
              >
                💡 View Insights
              </Button>
              <Button 
                variant="secondary" 
                onClick={() => navigate('/dashboard')}
                size="large"
              >
                📈 View Visualizations
              </Button>
            </div>
            <div className="new-upload-option">
              <Button 
                variant="danger" 
                onClick={handleClearSession}
                size="small"
              >
                🗑️ Clear & Upload New Dataset
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* File Info */}
      {selectedFile && currentStep === 'idle' && (
        <FileInfoCard file={selectedFile} />
      )}
    </div>
  );
}
