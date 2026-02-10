// src/pages/HomePage.jsx
import React from "react";
import { Link } from "react-router-dom";
import "./HomePage.css";

export default function HomePage() {
  const features = [
    {
      icon: "📤",
      title: "Smart Upload",
      description: "Upload CSV, Excel, or JSON files with automatic format detection and validation.",
      iconClass: ""
    },
    {
      icon: "🔍",
      title: "Dataset Classification",
      description: "Automatically identifies Financial, Sales, Time-Series, Healthcare, or Generic datasets.",
      iconClass: "feature-icon-info"
    },
    {
      icon: "⚙️",
      title: "Domain-Specific Preprocessing",
      description: "Intelligent preprocessing pipelines tailored to your dataset type with full audit trail.",
      iconClass: "feature-icon-warning"
    },
    {
      icon: "💡",
      title: "AI-Powered Insights",
      description: "Context-aware insights combining statistical analysis with AI explanations.",
      iconClass: "feature-icon-success"
    },
    {
      icon: "📊",
      title: "Smart Visualizations",
      description: "Recommended charts based on data characteristics and domain context.",
      iconClass: "feature-icon-accent"
    },
    {
      icon: "✅",
      title: "User Confirmation",
      description: "Review and approve all preprocessing steps before they're applied.",
      iconClass: "feature-icon-success"
    }
  ];

  const steps = [
    { number: 1, title: "Upload", description: "Drag & drop your dataset" },
    { number: 2, title: "Analyze", description: "AI classifies your data" },
    { number: 3, title: "Process", description: "Smart preprocessing" },
    { number: 4, title: "Insights", description: "Generate visualizations" }
  ];

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-background"></div>
        <div className="hero-grid"></div>
        
        <div className="hero-content">
          <div className="hero-badge">
            <span className="hero-badge-dot"></span>
            <span>Now with AI-Powered Analytics</span>
          </div>
          
          <h1 className="hero-title">
            Transform Data into
            <span className="hero-title-gradient"> Actionable Insights</span>
          </h1>
          
          <p className="hero-subtitle">
            EchoBI is an intelligent no-code analytics platform that automatically 
            classifies, preprocesses, and generates insights from your data.
          </p>
          
          <div className="hero-actions">
            <Link to="/upload" className="btn btn-primary btn-lg">
              Get Started
            </Link>
            <a href="#features" className="btn btn-secondary btn-lg">
              Learn More
            </a>
          </div>
          
          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat-value">5+</div>
              <div className="hero-stat-label">Dataset Types</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">100%</div>
              <div className="hero-stat-label">No-Code</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-value">AI</div>
              <div className="hero-stat-label">Powered</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="features-header">
          <h2 className="features-title">Powerful Features</h2>
          <p className="features-subtitle">
            Everything you need to analyze and understand your data
          </p>
        </div>
        
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className={`feature-icon ${feature.iconClass}`}>
                {feature.icon}
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="how-it-works-header">
          <h2 className="how-it-works-title">How It Works</h2>
          <p className="how-it-works-subtitle">
            Four simple steps to transform your data
          </p>
        </div>
        
        <div className="steps-container">
          {steps.map((step, index) => (
            <div key={index} className="step-card">
              <div className="step-number">{step.number}</div>
              <h3 className="step-title">{step.title}</h3>
              <p className="step-description">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-card">
          <div className="cta-content">
            <h2 className="cta-title">Ready to get started?</h2>
            <p className="cta-subtitle">
              Upload your dataset now and experience intelligent analytics
            </p>
            <div className="cta-actions">
              <Link to="/upload" className="cta-btn-white">
                Upload Dataset
              </Link>
              <a href="#features" className="cta-btn-outline">
                View Features
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
