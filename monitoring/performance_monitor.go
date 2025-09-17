package monitoring

import (
	"fmt"
	"sync"
	"time"
)

// PerformanceMonitor tracks and analyzes performance metrics
type PerformanceMonitor struct {
	metrics    map[string]*Metric
	mutex      sync.RWMutex
	startTime  time.Time
	thresholds map[string]time.Duration
}

// Metric represents a performance metric
type Metric struct {
	Name        string
	Count       int64
	TotalTime   time.Duration
	MinTime     time.Duration
	MaxTime     time.Duration
	AvgTime     time.Duration
	LastTime    time.Duration
	LastUpdated time.Time
	Errors      int64
	SuccessRate float64
}

// PerformanceReport represents a comprehensive performance report
type PerformanceReport struct {
	Timestamp     time.Time
	Uptime        time.Duration
	TotalMetrics  int
	OverallHealth string
	Metrics       map[string]*Metric
	Recommendations []string
}

// NewPerformanceMonitor creates a new PerformanceMonitor instance
func NewPerformanceMonitor() *PerformanceMonitor {
	return &PerformanceMonitor{
		metrics: make(map[string]*Metric),
		startTime: time.Now(),
		thresholds: map[string]time.Duration{
			"api_call":     1 * time.Second,
			"search":       2 * time.Second,
			"file_operation": 5 * time.Second,
			"context_assembly": 3 * time.Second,
		},
	}
}

// StartTimer starts timing an operation
func (pm *PerformanceMonitor) StartTimer(operation string) func() {
	start := time.Now()
	return func() {
		pm.RecordMetric(operation, time.Since(start), false)
	}
}

// RecordMetric records a performance metric
func (pm *PerformanceMonitor) RecordMetric(operation string, duration time.Duration, isError bool) {
	pm.mutex.Lock()
	defer pm.mutex.Unlock()
	
	metric, exists := pm.metrics[operation]
	if !exists {
		metric = &Metric{
			Name: operation,
			MinTime: duration,
			MaxTime: duration,
		}
		pm.metrics[operation] = metric
	}
	
	// Update metric
	metric.Count++
	metric.TotalTime += duration
	metric.LastTime = duration
	metric.LastUpdated = time.Now()
	
	if duration < metric.MinTime {
		metric.MinTime = duration
	}
	if duration > metric.MaxTime {
		metric.MaxTime = duration
	}
	
	if isError {
		metric.Errors++
	}
	
	// Calculate averages
	if metric.Count > 0 {
		metric.AvgTime = metric.TotalTime / time.Duration(metric.Count)
		metric.SuccessRate = float64(metric.Count-metric.Errors) / float64(metric.Count) * 100
	}
}

// GetMetric returns a specific metric
func (pm *PerformanceMonitor) GetMetric(operation string) *Metric {
	pm.mutex.RLock()
	defer pm.mutex.RUnlock()
	
	if metric, exists := pm.metrics[operation]; exists {
		// Return a copy to avoid race conditions
		return &Metric{
			Name:        metric.Name,
			Count:       metric.Count,
			TotalTime:   metric.TotalTime,
			MinTime:     metric.MinTime,
			MaxTime:     metric.MaxTime,
			AvgTime:     metric.AvgTime,
			LastTime:    metric.LastTime,
			LastUpdated: metric.LastUpdated,
			Errors:      metric.Errors,
			SuccessRate: metric.SuccessRate,
		}
	}
	return nil
}

// GetAllMetrics returns all metrics
func (pm *PerformanceMonitor) GetAllMetrics() map[string]*Metric {
	pm.mutex.RLock()
	defer pm.mutex.RUnlock()
	
	metrics := make(map[string]*Metric)
	for name, metric := range pm.metrics {
		metrics[name] = &Metric{
			Name:        metric.Name,
			Count:       metric.Count,
			TotalTime:   metric.TotalTime,
			MinTime:     metric.MinTime,
			MaxTime:     metric.MaxTime,
			AvgTime:     metric.AvgTime,
			LastTime:    metric.LastTime,
			LastUpdated: metric.LastUpdated,
			Errors:      metric.Errors,
			SuccessRate: metric.SuccessRate,
		}
	}
	return metrics
}

// GenerateReport generates a comprehensive performance report
func (pm *PerformanceMonitor) GenerateReport() *PerformanceReport {
	pm.mutex.RLock()
	defer pm.mutex.RUnlock()
	
	report := &PerformanceReport{
		Timestamp:    time.Now(),
		Uptime:       time.Since(pm.startTime),
		TotalMetrics: len(pm.metrics),
		Metrics:      pm.GetAllMetrics(),
		Recommendations: []string{},
	}
	
	// Analyze overall health
	report.OverallHealth = pm.analyzeOverallHealth()
	
	// Generate recommendations
	report.Recommendations = pm.generateRecommendations()
	
	return report
}

// analyzeOverallHealth analyzes the overall system health
func (pm *PerformanceMonitor) analyzeOverallHealth() string {
	if len(pm.metrics) == 0 {
		return "No data available"
	}
	
	totalOperations := int64(0)
	totalErrors := int64(0)
	slowOperations := 0
	
	for _, metric := range pm.metrics {
		totalOperations += metric.Count
		totalErrors += metric.Errors
		
		// Check if operation is slow
		if threshold, exists := pm.thresholds[metric.Name]; exists {
			if metric.AvgTime > threshold {
				slowOperations++
			}
		}
	}
	
	if totalOperations == 0 {
		return "No operations recorded"
	}
	
	errorRate := float64(totalErrors) / float64(totalOperations) * 100
	slowRate := float64(slowOperations) / float64(len(pm.metrics)) * 100
	
	if errorRate < 5 && slowRate < 20 {
		return "Excellent"
	} else if errorRate < 10 && slowRate < 40 {
		return "Good"
	} else if errorRate < 20 && slowRate < 60 {
		return "Fair"
	} else {
		return "Poor"
	}
}

// generateRecommendations generates performance recommendations
func (pm *PerformanceMonitor) generateRecommendations() []string {
	var recommendations []string
	
	for name, metric := range pm.metrics {
		// Check for high error rates
		if metric.SuccessRate < 90 {
			recommendations = append(recommendations, 
				fmt.Sprintf("High error rate for %s: %.1f%% success", name, metric.SuccessRate))
		}
		
		// Check for slow operations
		if threshold, exists := pm.thresholds[name]; exists {
			if metric.AvgTime > threshold {
				recommendations = append(recommendations, 
					fmt.Sprintf("Slow operation %s: %.3fs avg (threshold: %.3fs)", 
						name, metric.AvgTime.Seconds(), threshold.Seconds()))
			}
		}
		
		// Check for high variance
		if metric.MaxTime > metric.MinTime*10 {
			recommendations = append(recommendations, 
				fmt.Sprintf("High variance in %s: %.3fs min, %.3fs max", 
					name, metric.MinTime.Seconds(), metric.MaxTime.Seconds()))
		}
	}
	
	// Add general recommendations
	if len(recommendations) == 0 {
		recommendations = append(recommendations, "Performance is within acceptable limits")
	}
	
	return recommendations
}

// SetThreshold sets a performance threshold for an operation
func (pm *PerformanceMonitor) SetThreshold(operation string, threshold time.Duration) {
	pm.mutex.Lock()
	defer pm.mutex.Unlock()
	pm.thresholds[operation] = threshold
}

// GetThreshold returns the threshold for an operation
func (pm *PerformanceMonitor) GetThreshold(operation string) time.Duration {
	pm.mutex.RLock()
	defer pm.mutex.RUnlock()
	
	if threshold, exists := pm.thresholds[operation]; exists {
		return threshold
	}
	return 5 * time.Second // Default threshold
}

// Reset resets all metrics
func (pm *PerformanceMonitor) Reset() {
	pm.mutex.Lock()
	defer pm.mutex.Unlock()
	
	pm.metrics = make(map[string]*Metric)
	pm.startTime = time.Now()
}

// GetStats returns basic statistics
func (pm *PerformanceMonitor) GetStats() map[string]interface{} {
	pm.mutex.RLock()
	defer pm.mutex.RUnlock()
	
	totalOperations := int64(0)
	totalErrors := int64(0)
	totalTime := time.Duration(0)
	
	for _, metric := range pm.metrics {
		totalOperations += metric.Count
		totalErrors += metric.Errors
		totalTime += metric.TotalTime
	}
	
	avgTime := time.Duration(0)
	if totalOperations > 0 {
		avgTime = totalTime / time.Duration(totalOperations)
	}
	
	return map[string]interface{}{
		"uptime":           time.Since(pm.startTime),
		"total_operations": totalOperations,
		"total_errors":     totalErrors,
		"error_rate":       float64(totalErrors) / float64(totalOperations) * 100,
		"avg_response_time": avgTime,
		"metrics_count":    len(pm.metrics),
		"overall_health":   pm.analyzeOverallHealth(),
	}
}

// MonitorHTTPClient monitors HTTP client performance
func (pm *PerformanceMonitor) MonitorHTTPClient(client interface{}) {
	// This would integrate with the HTTP client to monitor requests
	// For now, it's a placeholder for future integration
}

// MonitorSearchEngine monitors search engine performance
func (pm *PerformanceMonitor) MonitorSearchEngine(operation string, duration time.Duration, success bool) {
	pm.RecordMetric("search_"+operation, duration, !success)
}

// MonitorAlgorithm monitors algorithm performance
func (pm *PerformanceMonitor) MonitorAlgorithm(algorithm string, duration time.Duration, success bool) {
	pm.RecordMetric("algorithm_"+algorithm, duration, !success)
}

// ExportMetrics exports metrics in a structured format
func (pm *PerformanceMonitor) ExportMetrics() map[string]interface{} {
	report := pm.GenerateReport()
	
	return map[string]interface{}{
		"timestamp":     report.Timestamp,
		"uptime":        report.Uptime,
		"overall_health": report.OverallHealth,
		"metrics":       report.Metrics,
		"recommendations": report.Recommendations,
		"stats":         pm.GetStats(),
	}
}
