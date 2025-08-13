/**
 * Performance monitoring utility for the React frontend
 * Tracks page loads, API calls, and component performance
 */

class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.apiCalls = [];
    this.pageLoads = [];
    this.componentRenders = [];
    
    // Initialize performance observers
    this.initializeObservers();
    
    // Track initial page load
    this.trackPageLoad();
  }

  initializeObservers() {
    // Track API calls and other network requests
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            this.processPerformanceEntry(entry);
          });
        });
        
        // Observe different types of performance entries
        observer.observe({ entryTypes: ['measure', 'navigation', 'resource'] });
        
        console.log('🚀 Performance monitoring initialized');
      } catch (error) {
        console.warn('Performance monitoring not available:', error);
      }
    }
  }

  processPerformanceEntry(entry) {
    const timestamp = new Date().toISOString();
    
    switch (entry.entryType) {
      case 'navigation':
        this.pageLoads.push({
          timestamp,
          type: 'page_load',
          loadTime: entry.loadEventEnd - entry.loadEventStart,
          domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
          totalTime: entry.loadEventEnd - entry.fetchStart,
          transferSize: entry.transferSize || 0
        });
        break;
        
      case 'resource':
        // Track API calls (requests to our backend)
        if (entry.name.includes('/api/')) {
          this.apiCalls.push({
            timestamp,
            url: entry.name,
            duration: entry.duration,
            transferSize: entry.transferSize || 0,
            responseEnd: entry.responseEnd,
            responseStart: entry.responseStart
          });
        }
        break;
        
      case 'measure':
        // Track custom measurements
        this.metrics.set(entry.name, {
          timestamp,
          duration: entry.duration,
          startTime: entry.startTime
        });
        break;
    }
  }

  trackPageLoad() {
    // Track when the page is fully loaded
    if (document.readyState === 'complete') {
      this.logPageLoadMetrics();
    } else {
      window.addEventListener('load', () => {
        this.logPageLoadMetrics();
      });
    }
  }

  logPageLoadMetrics() {
    const navigation = performance.getEntriesByType('navigation')[0];
    if (navigation) {
      const metrics = {
        'DNS Lookup': navigation.domainLookupEnd - navigation.domainLookupStart,
        'TCP Connection': navigation.connectEnd - navigation.connectStart,
        'Request': navigation.responseStart - navigation.requestStart,
        'Response': navigation.responseEnd - navigation.responseStart,
        'DOM Processing': navigation.domComplete - navigation.domLoading,
        'Total Load Time': navigation.loadEventEnd - navigation.navigationStart
      };

      console.group('📊 Page Load Performance');
      Object.entries(metrics).forEach(([key, value]) => {
        const color = value < 100 ? '#22c55e' : value < 300 ? '#f59e0b' : '#ef4444';
        console.log(`%c${key}: ${value.toFixed(2)}ms`, `color: ${color}; font-weight: bold`);
      });
      console.groupEnd();
    }
  }

  // Manual performance tracking methods
  startMeasure(name) {
    performance.mark(`${name}-start`);
  }

  endMeasure(name) {
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    const measure = performance.getEntriesByName(name, 'measure')[0];
    if (measure) {
      console.log(`⏱️ ${name}: ${measure.duration.toFixed(2)}ms`);
    }
  }

  // Track component render times
  trackComponentRender(componentName, renderTime) {
    this.componentRenders.push({
      timestamp: new Date().toISOString(),
      component: componentName,
      renderTime: renderTime
    });
    
    const color = renderTime < 16 ? '#22c55e' : renderTime < 50 ? '#f59e0b' : '#ef4444';
    console.log(`%c🎨 ${componentName} rendered: ${renderTime.toFixed(2)}ms`, 
                `color: ${color}; font-weight: bold`);
  }

  // Get performance summary
  getSummary() {
    const recentApiCalls = this.apiCalls.slice(-10);
    const avgApiTime = recentApiCalls.length > 0 
      ? recentApiCalls.reduce((sum, call) => sum + call.duration, 0) / recentApiCalls.length 
      : 0;

    const recentRenders = this.componentRenders.slice(-20);
    const avgRenderTime = recentRenders.length > 0
      ? recentRenders.reduce((sum, render) => sum + render.renderTime, 0) / recentRenders.length
      : 0;

    return {
      apiCalls: {
        total: this.apiCalls.length,
        recent: recentApiCalls.length,
        averageTime: avgApiTime.toFixed(2) + 'ms'
      },
      componentRenders: {
        total: this.componentRenders.length,
        recent: recentRenders.length,
        averageTime: avgRenderTime.toFixed(2) + 'ms'
      },
      pageLoads: this.pageLoads.length
    };
  }

  // Display performance dashboard in console
  showDashboard() {
    const summary = this.getSummary();
    
    console.group('🎯 Performance Dashboard');
    console.table(summary);
    
    if (this.apiCalls.length > 0) {
      console.group('🌐 Recent API Calls');
      console.table(this.apiCalls.slice(-5).map(call => ({
        URL: call.url.split('/api/')[1],
        Duration: call.duration.toFixed(2) + 'ms',
        Size: (call.transferSize / 1024).toFixed(2) + 'KB',
        Time: new Date(call.timestamp).toLocaleTimeString()
      })));
      console.groupEnd();
    }
    
    console.groupEnd();
  }

  // Enhanced fetch wrapper that automatically tracks API performance
  async enhancedFetch(url, options = {}) {
    const startTime = performance.now();
    
    try {
      const response = await fetch(url, options);
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      // Get server processing time from header if available
      const serverTime = response.headers.get('X-Process-Time');
      
      // Log the API call performance
      const method = options.method || 'GET';
      const color = duration < 200 ? '#22c55e' : duration < 500 ? '#f59e0b' : '#ef4444';
      
      console.log(
        `%c🌐 ${method} ${url.split('/api/')[1] || url} - ${duration.toFixed(2)}ms total` +
        (serverTime ? `, ${(parseFloat(serverTime) * 1000).toFixed(2)}ms server` : ''),
        `color: ${color}; font-weight: bold`
      );
      
      return response;
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      console.error(`❌ API Error: ${url} - ${duration.toFixed(2)}ms - ${error.message}`);
      throw error;
    }
  }
}

// Create global instance
const performanceMonitor = new PerformanceMonitor();

// Make it available globally for debugging
window.perfMonitor = performanceMonitor;

export default performanceMonitor; 