// src/components/layout/Footer.jsx
import React from "react";
import "./Footer.css";

export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <p className="footer-text">
          © 2026 EchoBI v2.0 - Intelligent No-Code Data Analytics Platform
        </p>
        <div className="footer-links">
          <a href="#docs" className="footer-link">Documentation</a>
          <a href="#support" className="footer-link">Support</a>
          <a href="#about" className="footer-link">About</a>
        </div>
      </div>
    </footer>
  );
}
