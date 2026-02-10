// src/components/layout/Sidebar.jsx
import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import "./Sidebar.css";

export default function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  
  const navSections = [
    {
      title: "Main",
      items: [
        { path: "/", icon: "🏠", label: "Home" },
        { path: "/upload", icon: "📤", label: "Upload" },
        { path: "/analysis", icon: "🔍", label: "Analysis" },
      ]
    },
    {
      title: "Data",
      items: [
        { path: "/preprocessing", icon: "⚙️", label: "Preprocessing" },
        { path: "/insights", icon: "💡", label: "Insights" },
        { path: "/dashboard", icon: "📊", label: "Dashboard" },
      ]
    },
    {
      title: "Tools",
      items: [
        { path: "/chat", icon: "💬", label: "Chat" },
        { path: "/about", icon: "ℹ️", label: "About" },
      ]
    }
  ];

  return (
    <>
      <div 
        className={`sidebar-overlay ${isOpen ? "visible" : ""}`} 
        onClick={onClose}
      ></div>
      <aside className={`sidebar ${isOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">E</div>
            <span className="sidebar-logo-text">EchoBI</span>
          </div>
          <button 
            className="sidebar-close-btn"
            onClick={onClose}
            title="Close sidebar"
          >
            ✕
          </button>
        </div>
        
        <nav className="sidebar-nav">
          {navSections.map((section, idx) => (
            <div key={idx} className="sidebar-nav-section">
              <div className="sidebar-nav-section-title">{section.title}</div>
              {section.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => 
                    `sidebar-nav-item ${isActive ? "active" : ""}`
                  }
                  onClick={onClose}
                >
                  <span className="sidebar-nav-icon">{item.icon}</span>
                  <span className="sidebar-nav-label">{item.label}</span>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        
        <div className="sidebar-footer">
          <div className="sidebar-footer-content">
            <div className="sidebar-footer-badge">
              <span className="sidebar-footer-badge-dot"></span>
              <span>System Online</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
