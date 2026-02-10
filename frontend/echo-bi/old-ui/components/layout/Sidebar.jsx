// src/components/layout/Sidebar.jsx
import React from "react";
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}
      <aside className={`sidebar ${isOpen ? "sidebar-open" : ""}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">Navigation</h2>
          <button className="sidebar-close" onClick={onClose} aria-label="Close sidebar">
            ×
          </button>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" className="sidebar-link" onClick={onClose}>
            🏠 Home
          </NavLink>
          <NavLink to="/upload" className="sidebar-link" onClick={onClose}>
            📤 Upload Dataset
          </NavLink>
          <NavLink to="/analysis" className="sidebar-link" onClick={onClose}>
            🔍 Analysis
          </NavLink>
          <NavLink to="/preprocessing" className="sidebar-link" onClick={onClose}>
            ⚙️ Preprocessing
          </NavLink>
          <NavLink to="/insights" className="sidebar-link" onClick={onClose}>
            💡 Insights
          </NavLink>
          <NavLink to="/dashboard" className="sidebar-link" onClick={onClose}>
            📊 Dashboard
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-info">
            <small>EchoBI v2.0</small>
            <small>No-code Analytics</small>
          </div>
        </div>
      </aside>
    </>
  );
}
