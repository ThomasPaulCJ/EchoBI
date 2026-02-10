// src/components/ChartView.jsx
import React from "react";
import Plot from "react-plotly.js";

export default function ChartView({ figure }) {
  if (!figure) return null;

  // Backend sends Plotly JSON - parse if needed
  const plotData = typeof figure === "string" ? JSON.parse(figure) : figure;

  return (
    <div>
      <h3 className="section-title">Visualization</h3>
      <Plot
        data={plotData.data}
        layout={{
          ...plotData.layout,
          autosize: true,
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: {
            family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
            color: "#1e293b",
          },
        }}
        config={{ responsive: true, displayModeBar: true }}
        style={{ width: "100%", height: "500px" }}
      />
    </div>
  );
}
