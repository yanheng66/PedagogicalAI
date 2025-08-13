# Performance Monitoring Guide

This project now includes comprehensive performance monitoring for both frontend and backend components.

## 🚀 Features

### Backend Performance Monitoring
- **API Response Time Tracking**: All API endpoints automatically log response times
- **Color-coded Console Output**: Green (<100ms), Yellow (100-500ms), Red (>500ms)
- **Performance Headers**: Each response includes `X-Process-Time` header for client-side analysis

### Frontend Performance Monitoring
- **Page Load Metrics**: DNS lookup, TCP connection, DOM processing times
- **API Call Tracking**: Automatic monitoring of all API requests
- **Component Render Times**: Track React component performance
- **Real-time Dashboard**: Optional visual performance dashboard

## 📊 How to Use

### 1. Backend Monitoring

**Automatic Logging**: When you run your backend server, you'll see colored performance logs:

```bash
uvicorn api_server_enhanced:app --host 0.0.0.0 --port 8000 --reload
```

Example output:
```
[PERF] POST /api/step1 - 200 - 0.245s
[PERF] POST /api/step1/confirm - 200 - 0.156s
```

### 2. Frontend Monitoring

#### Browser Console
Open your browser's developer console (F12) to see:
- 📊 Page load performance breakdown
- 🌐 API call timings (client + server)
- 🎨 Component render times
- ⏱️ Custom performance measurements

#### Performance Dashboard (Optional)
- **Development Mode**: Automatically visible
- **Production**: Add `?perf=true` to URL (e.g., `http://localhost:3000?perf=true`)

The dashboard shows:
- API call statistics
- Component render metrics
- Page load counts
- Performance trends

### 3. Using Performance Hooks in Components

```javascript
import usePerformance from '../hooks/usePerformance';

function MyComponent() {
  const { startRender, startMeasure, endMeasure, performantFetch } = usePerformance('MyComponent');
  startRender(); // Track component render time

  const handleApiCall = async () => {
    // Use enhanced fetch for automatic API tracking
    const response = await performantFetch('/api/endpoint', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  };

  const handleComplexOperation = () => {
    const measureName = startMeasure('complex-operation');
    // ... do complex work ...
    endMeasure(measureName);
  };

  return <div>My Component</div>;
}
```

### 4. Manual Performance Tracking

```javascript
import performanceMonitor from '../utils/performanceMonitor';

// Manual measurements
performanceMonitor.startMeasure('custom-operation');
// ... do work ...
performanceMonitor.endMeasure('custom-operation');

// View performance dashboard
performanceMonitor.showDashboard();

// Get performance summary
const summary = performanceMonitor.getSummary();
console.log(summary);
```

## 🎯 Performance Targets

### Good Performance Indicators
- **API Calls**: < 200ms total time
- **Page Load**: < 2 seconds
- **Component Renders**: < 16ms (60 FPS)
- **Server Processing**: < 100ms

### Warning Indicators
- **API Calls**: 200-500ms
- **Component Renders**: 16-50ms
- **Server Processing**: 100-500ms

### Poor Performance Indicators
- **API Calls**: > 500ms
- **Component Renders**: > 50ms
- **Server Processing**: > 500ms

## 🔧 Advanced Usage

### Performance Dashboard Controls
- **Click to expand/collapse** the dashboard
- **Show Details button**: Opens detailed console dashboard
- **Clear button**: Clears performance console logs

### Console Commands
Access the global performance monitor via browser console:

```javascript
// Show detailed dashboard
window.perfMonitor.showDashboard();

// Get current metrics
window.perfMonitor.getSummary();

// Clear all collected data
window.perfMonitor.apiCalls.length = 0;
window.perfMonitor.componentRenders.length = 0;
```

### Customizing Thresholds
Edit the color thresholds in `performanceMonitor.js`:

```javascript
// Current thresholds
const isGood = time < 100;
const isWarning = time < 500;
// Anything above 500ms is considered poor
```

## 🚨 Troubleshooting

### High API Response Times
1. Check server logs for specific slow endpoints
2. Look for database query optimization opportunities
3. Consider caching for frequently accessed data

### Slow Component Renders
1. Check for unnecessary re-renders
2. Use React.memo for expensive components
3. Optimize state management

### Large Bundle Sizes
1. Use Chrome DevTools Network tab
2. Look for large JavaScript/CSS files
3. Consider code splitting

## 📈 Monitoring Best Practices

1. **Regular Monitoring**: Check performance metrics during development
2. **Performance Budgets**: Set and maintain performance targets
3. **Continuous Integration**: Monitor performance in CI/CD pipeline
4. **Real User Monitoring**: Track performance in production
5. **Progressive Enhancement**: Ensure app works well on slower devices

## 🔄 Disable Monitoring

### Development
Set `showPerformanceDashboard` to `false` in `App.js`

### Production
The dashboard is automatically hidden unless `?perf=true` is in the URL

### Complete Removal
1. Remove imports from `App.js` and `LessonPage.js`
2. Replace `performantFetch` calls with regular `fetch`
3. Remove the performance monitoring files 