// src/components/layout/Header.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Header.css";

export default function Header({ onMenuClick }) {
  const location = useLocation();
  
  const navItems = [
    { path: "/", label: "Home", icon: "🏠" },
    { path: "/upload", label: "Upload", icon: "📤" },
    { path: "/analysis", label: "Analysis", icon: "🔍" },
    { path: "/insights", label: "Insights", icon: "💡" },
    { path: "/dashboard", label: "Dashboard", icon: "📊" },
  ];

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <button className="header-menu-btn" onClick={onMenuClick} title="Menu">
            <span className="menu-icon">☰</span>
          </button>
          <Link to="/" className="header-logo">
            <div className="header-logo-icon">
              <span>E</span>
            </div>
            <span className="header-logo-text">EchoBI</span>
            <span className="header-version">v2.0</span>
          </Link>
        </div>
        
        <nav className="header-nav">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`header-nav-link ${location.pathname === item.path ? "active" : ""}`}
            >
              <span className="header-nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
        
        <div className="header-actions">
          <div className="header-user">
            <div className="header-user-avatar">U</div>
          </div>
        </div>
      </div>
    </header>
  );
}
