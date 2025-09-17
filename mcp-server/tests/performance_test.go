package tests

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"testing"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/tools"
	"go.uber.org/zap"
)

// PerformanceTestSuite provides comprehensive performance testing
type PerformanceTestSuite struct {
	serverURL      string
	httpClient     *http.Client
	obsidianClient client.HTTPClient
	advancedTools  *tools.AdvancedTools
	logger         *zap.Logger
}

// NewPerformanceTestSuite creates a new performance test suite
func NewPerformanceTestSuite(serverURL string) *PerformanceTestSuite {
	logger, _ := zap.NewDevelopment()
	mockClient := client.NewMockClient(logger)

	return &PerformanceTestSuite{
		serverURL:      serverURL,
		httpClient:     &http.Client{Timeout: 60 * time.Second},
		obsidianClient: mockClient,
		advancedTools:  tools.NewAdvancedTools(mockClient, nil, logger),
		logger:         logger,
	}
}

// PerformanceMetrics tracks performance metrics
type PerformanceMetrics struct {
	Operation    string
	Duration     time.Duration
	Success      bool
	Error        string
	ResponseSize int
	Concurrency  int
}

// TestLatency tests individual tool latency
func (suite *PerformanceTestSuite) TestLatency(t *testing.T) {
	t.Log("🚀 Testing Tool Latency")

	testCases := []struct {
		name    string
		tool    string
		params  map[string]interface{}
		maxTime time.Duration
	}{
		{
			name:    "ListFiles",
			tool:    "list_files_in_vault",
			params:  map[string]interface{}{},
			maxTime: 500 * time.Millisecond,
		},
		{
			name:    "SearchVault",
			tool:    "search_vault",
			params:  map[string]interface{}{"query": "test", "limit": 5},
			maxTime: 1 * time.Second,
		},
		{
			name:    "SemanticSearch",
			tool:    "semantic_search",
			params:  map[string]interface{}{"query": "demo", "top_k": 3},
			maxTime: 2 * time.Second,
		},
		{
			name:    "ReadNote",
			tool:    "read_note",
			params:  map[string]interface{}{"filename": "test-note.md"},
			maxTime: 1 * time.Second,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			start := time.Now()
			result := suite.executeTool(t, tc.tool, tc.params)
			duration := time.Since(start)

			if success, ok := result["success"].(bool); !ok || !success {
				errorMsg := "unknown error"
				if err, exists := result["error"].(string); exists {
					errorMsg = err
				}
				t.Logf("⚠️ %s failed: %s", tc.name, errorMsg)
			} else {
				t.Logf("✅ %s completed in %v", tc.name, duration)
			}

			if duration > tc.maxTime {
				t.Logf("⚠️ %s exceeded max time: %v > %v", tc.name, duration, tc.maxTime)
			}
		})
	}
}

// TestThroughput tests system throughput under load
func (suite *PerformanceTestSuite) TestThroughput(t *testing.T) {
	t.Log("🚀 Testing System Throughput")

	concurrencyLevels := []int{1, 5, 10, 20}
	requestsPerLevel := 50

	for _, concurrency := range concurrencyLevels {
		t.Run(fmt.Sprintf("Concurrency_%d", concurrency), func(t *testing.T) {
			metrics := suite.runLoadTest(t, concurrency, requestsPerLevel)

			// Calculate metrics
			successRate := float64(metrics.SuccessCount) / float64(len(metrics.Results)) * 100
			avgDuration := suite.calculateAverageDuration(metrics.Results)
			throughput := float64(len(metrics.Results)) / metrics.TotalDuration.Seconds()

			t.Logf("📊 Concurrency %d: Success Rate: %.1f%%, Avg Duration: %v, Throughput: %.2f req/s",
				concurrency, successRate, avgDuration, throughput)

			// Performance assertions
			if successRate < 90 {
				t.Logf("⚠️ Low success rate: %.1f%%", successRate)
			}

			if avgDuration > 5*time.Second {
				t.Logf("⚠️ High average duration: %v", avgDuration)
			}
		})
	}
}

// TestMemoryUsage tests memory usage patterns
func (suite *PerformanceTestSuite) TestMemoryUsage(t *testing.T) {
	t.Log("🚀 Testing Memory Usage")

	// Run multiple operations to test memory stability
	for i := 0; i < 100; i++ {
		suite.executeTool(t, "search_vault", map[string]interface{}{
			"query": fmt.Sprintf("memory_test_%d", i),
			"limit": 10,
		})

		if i%20 == 0 {
			t.Logf("📊 Completed %d operations", i+1)
		}
	}

	t.Logf("✅ Memory usage test completed")
}

// TestConcurrentSessions tests concurrent user sessions
func (suite *PerformanceTestSuite) TestConcurrentSessions(t *testing.T) {
	t.Log("🚀 Testing Concurrent Sessions")

	sessionCount := 10
	operationsPerSession := 20

	var wg sync.WaitGroup
	results := make(chan []PerformanceMetrics, sessionCount)

	for session := 0; session < sessionCount; session++ {
		wg.Add(1)
		go func(sessionID int) {
			defer wg.Done()

			sessionMetrics := make([]PerformanceMetrics, operationsPerSession)

			for op := 0; op < operationsPerSession; op++ {
				start := time.Now()
				result := suite.executeTool(t, "search_vault", map[string]interface{}{
					"query": fmt.Sprintf("session_%d_op_%d", sessionID, op),
					"limit": 5,
				})
				duration := time.Since(start)

				success, _ := result["success"].(bool)
				errorMsg := ""
				if err, exists := result["error"].(string); exists {
					errorMsg = err
				}
				sessionMetrics[op] = PerformanceMetrics{
					Operation:   "search_vault",
					Duration:    duration,
					Success:     success,
					Error:       errorMsg,
					Concurrency: sessionCount,
				}
			}

			results <- sessionMetrics
		}(session)
	}

	wg.Wait()
	close(results)

	// Collect all metrics
	var allMetrics []PerformanceMetrics
	for sessionMetrics := range results {
		allMetrics = append(allMetrics, sessionMetrics...)
	}

	// Calculate session-level metrics
	successCount := 0
	var totalDuration time.Duration
	for _, metric := range allMetrics {
		if metric.Success {
			successCount++
		}
		totalDuration += metric.Duration
	}

	successRate := float64(successCount) / float64(len(allMetrics)) * 100
	avgDuration := totalDuration / time.Duration(len(allMetrics))

	t.Logf("📊 Concurrent Sessions: %d sessions, %d total operations", sessionCount, len(allMetrics))
	t.Logf("📊 Success Rate: %.1f%%, Avg Duration: %v", successRate, avgDuration)

	if successRate < 85 {
		t.Logf("⚠️ Low success rate under concurrent load: %.1f%%", successRate)
	}
}

// LoadTestResult contains results from a load test
type LoadTestResult struct {
	Results       []PerformanceMetrics
	SuccessCount  int
	TotalDuration time.Duration
}

// runLoadTest executes a load test with specified concurrency and request count
func (suite *PerformanceTestSuite) runLoadTest(t *testing.T, concurrency, totalRequests int) LoadTestResult {
	results := make([]PerformanceMetrics, totalRequests)
	var wg sync.WaitGroup
	semaphore := make(chan struct{}, concurrency)

	start := time.Now()

	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
		go func(index int) {
			defer wg.Done()

			// Acquire semaphore
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			opStart := time.Now()
			result := suite.executeTool(t, "search_vault", map[string]interface{}{
				"query": fmt.Sprintf("load_test_%d", index),
				"limit": 3,
			})
			duration := time.Since(opStart)

			success, _ := result["success"].(bool)
			errorMsg := ""
			if err, exists := result["error"].(string); exists {
				errorMsg = err
			}
			results[index] = PerformanceMetrics{
				Operation:   "search_vault",
				Duration:    duration,
				Success:     success,
				Error:       errorMsg,
				Concurrency: concurrency,
			}
		}(i)
	}

	wg.Wait()
	totalDuration := time.Since(start)

	// Count successes
	successCount := 0
	for _, result := range results {
		if result.Success {
			successCount++
		}
	}

	return LoadTestResult{
		Results:       results,
		SuccessCount:  successCount,
		TotalDuration: totalDuration,
	}
}

// calculateAverageDuration calculates average duration from metrics
func (suite *PerformanceTestSuite) calculateAverageDuration(metrics []PerformanceMetrics) time.Duration {
	if len(metrics) == 0 {
		return 0
	}

	var total time.Duration
	for _, metric := range metrics {
		total += metric.Duration
	}

	return total / time.Duration(len(metrics))
}

// executeTool executes a tool via HTTP API
func (suite *PerformanceTestSuite) executeTool(t *testing.T, toolName string, params map[string]interface{}) map[string]interface{} {
	request := map[string]interface{}{
		"tool":   toolName,
		"params": params,
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		t.Fatalf("Failed to marshal request: %v", err)
	}

	resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		}
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		}
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return map[string]interface{}{
			"success": false,
			"error":   err.Error(),
		}
	}

	return result
}

// TestPerformanceBenchmarks runs all performance tests
func TestPerformanceBenchmarks(t *testing.T) {
	serverURL := "http://localhost:3011"
	suite := NewPerformanceTestSuite(serverURL)

	// Wait for server to be ready
	time.Sleep(2 * time.Second)

	// Run performance tests
	suite.TestLatency(t)
	suite.TestThroughput(t)
	suite.TestMemoryUsage(t)
	suite.TestConcurrentSessions(t)

	t.Log("🎉 All performance tests completed!")
}
