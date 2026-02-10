// src/components/common/Loader.jsx
import React from "react";
import "./Loader.css";

export default function Loader({ size = "medium", text = null, fullPage = false }) {
  const content = (
    <div className="loader-container">
      <div className={`loader loader-${size}`}></div>
      {text && <p className="loader-text">{text}</p>}
    </div>
  );

  if (fullPage) {
    return (
      <div className="loader-fullpage">
        {content}
      </div>
    );
  }

  return content;
}
