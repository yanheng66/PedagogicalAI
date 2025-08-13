import React, { useState, useEffect } from 'react';
import performanceMonitor from '../utils/performanceMonitor';

const PerformanceDashboard = ({ isVisible = false, position = 'bottom-right' }) => {
  const [metrics, setMetrics] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (!isVisible) return;

    const updateMetrics = () => {
      setMetrics(performanceMonitor.getSummary());
    };

    // Update metrics every 2 seconds
    const interval = setInterval(updateMetrics, 2000);
    updateMetrics(); // Initial update

    return () => clearInterval(interval);
  }, [isVisible]);

  if (!isVisible || !metrics) return null;

  const positionStyles = {
    'bottom-right': { bottom: '20px', right: '20px' },
    'bottom-left': { bottom: '20px', left: '20px' },
    'top-right': { top: '20px', right: '20px' },
    'top-left': { top: '20px', left: '20px' }
  };

  const baseStyle = {
    position: 'fixed',
    zIndex: 9999,
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    color: 'white',
    borderRadius: '8px',
    padding: '12px',
    fontSize: '12px',
    fontFamily: 'monospace',
    minWidth: '200px',
    maxWidth: '300px',
    border: '1px solid #333',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
    ...positionStyles[position]
  };

  const getColorForTime = (timeStr) => {
    const time = parseFloat(timeStr);
    if (time < 100) return '#22c55e'; // Green
    if (time < 300) return '#f59e0b'; // Yellow
    return '#ef4444'; // Red
  };

  return (
    <div style={baseStyle}>
      <div 
        style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          cursor: 'pointer',
          marginBottom: isExpanded ? '8px' : '0'
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span style={{ fontWeight: 'bold' }}>⚡ Performance</span>
        <span>{isExpanded ? '▼' : '▶'}</span>
      </div>

      {isExpanded && (
        <div>
          <div style={{ marginBottom: '8px' }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>🌐 API Calls</div>
            <div>Total: {metrics.apiCalls.total}</div>
            <div>Recent: {metrics.apiCalls.recent}</div>
            <div style={{ color: getColorForTime(metrics.apiCalls.averageTime) }}>
              Avg: {metrics.apiCalls.averageTime}
            </div>
          </div>

          <div style={{ marginBottom: '8px' }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>🎨 Renders</div>
            <div>Total: {metrics.componentRenders.total}</div>
            <div>Recent: {metrics.componentRenders.recent}</div>
            <div style={{ color: getColorForTime(metrics.componentRenders.averageTime) }}>
              Avg: {metrics.componentRenders.averageTime}
            </div>
          </div>

          <div style={{ marginBottom: '8px' }}>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>📄 Page Loads</div>
            <div>Count: {metrics.pageLoads}</div>
          </div>

          <div style={{ 
            borderTop: '1px solid #333', 
            paddingTop: '8px', 
            marginTop: '8px',
            display: 'flex',
            gap: '8px'
          }}>
            <button
              onClick={(e) => {
                e.stopPropagation();
                performanceMonitor.showDashboard();
              }}
              style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '10px',
                cursor: 'pointer'
              }}
            >
              Show Details
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                console.clear();
                console.log('🧹 Performance console cleared');
              }}
              style={{
                backgroundColor: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                padding: '4px 8px',
                fontSize: '10px',
                cursor: 'pointer'
              }}
            >
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceDashboard; 