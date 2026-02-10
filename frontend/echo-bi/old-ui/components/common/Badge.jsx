// src/components/common/Badge.jsx
import React from "react";
import "./Badge.css";

export default function Badge({ 
  children, 
  variant = "default",
  size = "medium",
  rounded = false
}) {
  const className = [
    "badge",
    `badge-${variant}`,
    `badge-${size}`,
    rounded && "badge-rounded"
  ].filter(Boolean).join(" ");

  return (
    <span className={className}>
      {children}
    </span>
  );
}
