import { useEffect, useRef } from 'react';
import performanceMonitor from '../utils/performanceMonitor';

/**
 * React hook for tracking component performance
 * @param {string} componentName - Name of the component to track
 * @param {Object} options - Configuration options
 * @returns {Object} Performance tracking utilities
 */
export const usePerformance = (componentName, options = {}) => {
  const renderStartTime = useRef(null);
  const mountTime = useRef(null);
  
  // Track component mount time
  useEffect(() => {
    mountTime.current = performance.now();
    
    return () => {
      // Track component unmount
      const unmountTime = performance.now();
      const lifetimeMs = unmountTime - mountTime.current;
      
      if (options.trackUnmount) {
        console.log(`🔄 ${componentName} lifetime: ${lifetimeMs.toFixed(2)}ms`);
      }
    };
  }, [componentName, options.trackUnmount]);

  // Track render performance
  useEffect(() => {
    if (renderStartTime.current) {
      const renderTime = performance.now() - renderStartTime.current;
      performanceMonitor.trackComponentRender(componentName, renderTime);
      renderStartTime.current = null;
    }
  });

  // Start render timing (call this at the beginning of your component)
  const startRender = () => {
    renderStartTime.current = performance.now();
  };

  // Manual performance tracking
  const startMeasure = (operationName) => {
    const fullName = `${componentName}-${operationName}`;
    performanceMonitor.startMeasure(fullName);
    return fullName;
  };

  const endMeasure = (measureName) => {
    performanceMonitor.endMeasure(measureName);
  };

  // Enhanced fetch that tracks API performance
  const performantFetch = performanceMonitor.enhancedFetch.bind(performanceMonitor);

  return {
    startRender,
    startMeasure,
    endMeasure,
    performantFetch
  };
};

/**
 * Higher-order component for automatic performance tracking
 * @param {React.Component} WrappedComponent 
 * @param {string} componentName 
 * @returns {React.Component}
 */
export const withPerformanceTracking = (WrappedComponent, componentName) => {
  return function PerformanceTrackedComponent(props) {
    const { startRender } = usePerformance(componentName || WrappedComponent.name);
    
    // Start render timing
    startRender();
    
    return <WrappedComponent {...props} />;
  };
};

export default usePerformance; 