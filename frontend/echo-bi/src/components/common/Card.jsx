// src/components/common/Card.jsx
import React from "react";
import "./Card.css";

export default function Card({ 
  children, 
  title = null,
  subtitle = null,
  footer = null,
  padding = "normal",
  hoverable = false,
  className = ""
}) {
  const cardClassName = [
    "card-component",
    `card-padding-${padding}`,
    hoverable && "card-hoverable",
    className
  ].filter(Boolean).join(" ");

  return (
    <div className={cardClassName}>
      {(title || subtitle) && (
        <div className="card-header">
          {title && <h3 className="card-title">{title}</h3>}
          {subtitle && <p className="card-subtitle">{subtitle}</p>}
        </div>
      )}
      <div className="card-body">
        {children}
      </div>
      {footer && (
        <div className="card-footer">
          {footer}
        </div>
      )}
    </div>
  );
}
