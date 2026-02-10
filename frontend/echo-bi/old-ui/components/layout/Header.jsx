// src/components/layout/Header.jsx
import React from "react";
import "./Header.css";

export default function Header() {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-brand">
          <span className="header-logo">📊</span>
          <h1 className="header-title">EchoBI</h1>
          <span className="header-version">v2.0</span>
        </div>
        <nav className="header-nav">
          {/* Navigation will be added with routing */}
        </nav>
      </div>
    </header>
  );
}
