// src/components/layout/Footer.jsx
import React from "react";
import { Link } from "react-router-dom";
import "./Footer.css";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-left">
          <div className="footer-logo">
            <div className="footer-logo-icon">E</div>
            <span>EchoBI</span>
          </div>
          <span className="footer-copyright">
            © 2026 EchoBI. Intelligent Analytics.
          </span>
        </div>
        
        <div className="footer-center">
          <div className="footer-links">
            <a href="#docs" className="footer-link">Documentation</a>
            <a href="#support" className="footer-link">Support</a>
            <Link to="/about" className="footer-link">About</Link>
          </div>
          <div className="footer-team">
            Manu Mathew • Thomas Paul CJ • Vidhusankar CH • Nayif Nazar
          </div>
        </div>
        
        <div className="footer-right">
          <div className="footer-status">
            <span className="footer-status-dot"></span>
            <span>All Systems Operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
