// src/components/common/Button.jsx
import React from "react";
import "./Button.css";

export default function Button({ 
  children, 
  onClick, 
  variant = "primary", 
  size = "medium",
  disabled = false,
  loading = false,
  icon = null,
  fullWidth = false,
  type = "button"
}) {
  const className = [
    "btn",
    `btn-${variant}`,
    `btn-${size}`,
    fullWidth && "btn-full-width",
    loading && "btn-loading",
  ].filter(Boolean).join(" ");

  return (
    <button 
      className={className}
      onClick={onClick}
      disabled={disabled || loading}
      type={type}
    >
      {loading && <span className="btn-spinner"></span>}
      {icon && !loading && <span className="btn-icon">{icon}</span>}
      <span className="btn-text">{children}</span>
    </button>
  );
}
