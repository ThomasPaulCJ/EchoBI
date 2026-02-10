// src/pages/HomePage.jsx
import React from "react";
import { Card } from "../components/common";
import "./HomePage.css";

export default function HomePage() {
  return (
    <div className="home-page">
      <div className="home-hero">
        <h1 className="home-title">Welcome to EchoBI v2.0</h1>
        <p className="home-subtitle">
          Intelligent No-Code Data Analytics Platform
        </p>
        <p className="home-description">
          Upload your dataset and let EchoBI automatically classify, preprocess, 
          and generate insights tailored to your data type.
        </p>
      </div>

      <div className="home-features">
        <Card title="📤 Smart Upload" hoverable>
          <p>Upload CSV, Excel, or JSON files. Automatic format detection and validation.</p>
        </Card>

        <Card title="🔍 Dataset Classification" hoverable>
          <p>Automatically identifies Financial, Sales, Time-Series, Healthcare, or Generic datasets.</p>
        </Card>

        <Card title="⚙️ Domain-Specific Preprocessing" hoverable>
          <p>Intelligent preprocessing pipelines tailored to your dataset type with full audit trail.</p>
        </Card>

        <Card title="💡 AI-Powered Insights" hoverable>
          <p>Context-aware insights combining statistical analysis with AI explanations.</p>
        </Card>

        <Card title="📊 Smart Visualizations" hoverable>
          <p>Recommended charts based on data characteristics and domain context.</p>
        </Card>

        <Card title="✅ User Confirmation" hoverable>
          <p>Review and approve all preprocessing steps before they're applied.</p>
        </Card>
      </div>
    </div>
  );
}
