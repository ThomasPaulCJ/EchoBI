import React from 'react';
import Plot from 'react-plotly.js';
import { Card } from '../common';
import './ChartCard.css';

const ChartCard = ({ 
  chart, 
  onFullscreen, 
  onDownload,
  showControls = true 
}) => {
  if (!chart || !chart.plotly_spec) {
    return (
      <Card className="chart-card">
        <div className="chart-error">
          <p>Chart data not available</p>
        </div>
      </Card>
    );
  }

  const { data, layout } = chart.plotly_spec;

  // Ensure layout has responsive settings
  const responsiveLayout = {
    ...layout,
    autosize: true,
    margin: { t: 60, r: 40, b: 60, l: 60 },
    ...layout
  };

  const handleDownloadPNG = () => {
    if (onDownload) {
      onDownload(chart);
    }
  };

  const handleFullscreen = () => {
    if (onFullscreen) {
      onFullscreen(chart);
    }
  };

  return (
    <Card className="chart-card">
      <div className="chart-header">
        <div className="chart-title-section">
          <h3 className="chart-title">{chart.title}</h3>
          <span className="chart-type-badge">{chart.chart_type}</span>
        </div>
        {showControls && (
          <div className="chart-controls">
            <button 
              className="chart-control-btn"
              onClick={handleFullscreen}
              title="Fullscreen"
            >
              ⛶
            </button>
            <button 
              className="chart-control-btn"
              onClick={handleDownloadPNG}
              title="Download"
            >
              ⬇
            </button>
          </div>
        )}
      </div>
      
      <div className="chart-container">
        <Plot
          data={data}
          layout={responsiveLayout}
          config={{
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            toImageButtonOptions: {
              format: 'png',
              filename: chart.title.replace(/\s+/g, '_').toLowerCase(),
              height: 800,
              width: 1200,
              scale: 2
            }
          }}
          style={{ width: '100%', height: '100%' }}
          useResizeHandler={true}
        />
      </div>
    </Card>
  );
};

export default ChartCard;
