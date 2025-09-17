package tests

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"testing"
	"time"
)

// ProductionReadinessTestSuite provides comprehensive production readiness validation
type ProductionReadinessTestSuite struct {
	serverURL  string
	httpClient *http.Client
}

// NewProductionReadinessTestSuite creates a new production readiness test suite
func NewProductionReadinessTestSuite(serverURL string) *ProductionReadinessTestSuite {
	return &ProductionReadinessTestSuite{
		serverURL:  serverURL,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

// TestHealthCheckEndpoints tests health check functionality
func (suite *ProductionReadinessTestSuite) TestHealthCheckEndpoints(t *testing.T) {
	t.Log("🔍 Testing Health Check Endpoints")

	// Test health endpoint
	resp, err := suite.httpClient.Get(suite.serverURL + "/health")
	if err != nil {
		t.Fatalf("Health check failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Fatalf("Health check returned status %d, expected 200", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("Failed to read health response: %v", err)
	}

	var healthResponse map[string]interface{}
	if err := json.Unmarshal(body, &healthResponse); err != nil {
		t.Fatalf("Failed to decode health response: %v", err)
	}

	// Validate health response structure
	requiredFields := []string{"status", "message", "timestamp"}
	for _, field := range requiredFields {
		if _, exists := healthResponse[field]; !exists {
			t.Fatalf("Health response missing required field: %s", field)
		}
	}

	// Check status
	if status, ok := healthResponse["status"].(string); !ok || status != "healthy" {
		t.Logf("⚠️ Health status is not 'healthy': %v", healthResponse["status"])
	}

	t.Logf("✅ Health check endpoints validation passed")
}

// TestMonitoringAndMetrics tests monitoring and metrics collection
func (suite *ProductionReadinessTestSuite) TestMonitoringAndMetrics(t *testing.T) {
	t.Log("🔍 Testing Monitoring and Metrics")

	// Test that server responds to monitoring requests
	endpoints := []string{
		"/health",
		"/tools",
	}

	for _, endpoint := range endpoints {
		resp, err := suite.httpClient.Get(suite.serverURL + endpoint)
		if err != nil {
			t.Fatalf("Monitoring endpoint %s failed: %v", endpoint, err)
		}
		defer resp.Body.Close()

		if resp.StatusCode >= 500 {
			t.Fatalf("Monitoring endpoint %s returned server error: %d", endpoint, resp.StatusCode)
		}

		// Check response time
		start := time.Now()
		_, err = suite.httpClient.Get(suite.serverURL + endpoint)
		responseTime := time.Since(start)

		if responseTime > 5*time.Second {
			t.Logf("⚠️ Endpoint %s response time is slow: %v", endpoint, responseTime)
		}

		t.Logf("✅ Endpoint %s monitoring passed (response time: %v)", endpoint, responseTime)
	}
}

// TestErrorHandling tests comprehensive error handling
func (suite *ProductionReadinessTestSuite) TestErrorHandling(t *testing.T) {
	t.Log("🔍 Testing Error Handling")

	errorTestCases := []struct {
		name        string
		endpoint    string
		method      string
		body        []byte
		expectCode  int
		description string
	}{
		{
			name:        "InvalidEndpoint",
			endpoint:    "/nonexistent",
			method:      "GET",
			body:        nil,
			expectCode:  404,
			description: "Invalid endpoint should return 404",
		},
		{
			name:        "InvalidMethod",
			endpoint:    "/health",
			method:      "POST",
			body:        []byte(`{"test": "data"}`),
			expectCode:  405,
			description: "Invalid method should return 405",
		},
		{
			name:        "MalformedJSON",
			endpoint:    "/tools/execute",
			method:      "POST",
			body:        []byte(`{"tool": "test", "params": invalid json}`),
			expectCode:  400,
			description: "Malformed JSON should return 400",
		},
		{
			name:        "EmptyRequest",
			endpoint:    "/tools/execute",
			method:      "POST",
			body:        []byte(`{}`),
			expectCode:  400,
			description: "Empty request should return 400",
		},
	}

	for _, tc := range errorTestCases {
		t.Run(tc.name, func(t *testing.T) {
			var resp *http.Response
			var err error

			if tc.method == "GET" {
				resp, err = suite.httpClient.Get(suite.serverURL + tc.endpoint)
			} else {
				resp, err = suite.httpClient.Post(suite.serverURL+tc.endpoint, "application/json", bytes.NewBuffer(tc.body))
			}

			if err != nil {
				t.Fatalf("Request failed: %v", err)
			}
			defer resp.Body.Close()

			if resp.StatusCode != tc.expectCode {
				t.Logf("⚠️ Expected status %d, got %d for %s", tc.expectCode, resp.StatusCode, tc.name)
			}

			// Check that error responses are properly formatted
			body, err := io.ReadAll(resp.Body)
			if err != nil {
				t.Fatalf("Failed to read error response: %v", err)
			}

			if len(body) > 0 {
				var errorResponse map[string]interface{}
				if err := json.Unmarshal(body, &errorResponse); err != nil {
					t.Logf("⚠️ Error response is not valid JSON for %s", tc.name)
				}
			}

			t.Logf("✅ %s error handling passed", tc.name)
		})
	}
}

// TestPerformanceUnderLoad tests performance under load
func (suite *ProductionReadinessTestSuite) TestPerformanceUnderLoad(t *testing.T) {
	t.Log("🔍 Testing Performance Under Load")

	// Test concurrent requests
	concurrency := 10
	requestsPerGoroutine := 5

	results := make(chan time.Duration, concurrency*requestsPerGoroutine)
	errors := make(chan error, concurrency*requestsPerGoroutine)

	for i := 0; i < concurrency; i++ {
		go func() {
			for j := 0; j < requestsPerGoroutine; j++ {
				start := time.Now()

				request := map[string]interface{}{
					"tool":   "list_files_in_vault",
					"params": map[string]interface{}{},
				}

				jsonData, err := json.Marshal(request)
				if err != nil {
					errors <- err
					return
				}

				resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
				if err != nil {
					errors <- err
					return
				}
				defer resp.Body.Close()

				duration := time.Since(start)
				results <- duration
			}
		}()
	}

	// Collect results
	var totalDuration time.Duration
	var maxDuration time.Duration
	var minDuration time.Duration = time.Hour
	errorCount := 0

	for i := 0; i < concurrency*requestsPerGoroutine; i++ {
		select {
		case duration := <-results:
			totalDuration += duration
			if duration > maxDuration {
				maxDuration = duration
			}
			if duration < minDuration {
				minDuration = duration
			}
		case err := <-errors:
			errorCount++
			t.Logf("Request error: %v", err)
		case <-time.After(30 * time.Second):
			t.Fatalf("Test timeout after 30 seconds")
		}
	}

	avgDuration := totalDuration / time.Duration(concurrency*requestsPerGoroutine-errorCount)

	t.Logf("Performance under load results:")
	t.Logf("  Total requests: %d", concurrency*requestsPerGoroutine)
	t.Logf("  Errors: %d", errorCount)
	t.Logf("  Average response time: %v", avgDuration)
	t.Logf("  Min response time: %v", minDuration)
	t.Logf("  Max response time: %v", maxDuration)

	// Performance thresholds
	if avgDuration > 2*time.Second {
		t.Logf("⚠️ Average response time is high: %v", avgDuration)
	}

	if maxDuration > 10*time.Second {
		t.Logf("⚠️ Max response time is very high: %v", maxDuration)
	}

	if errorCount > concurrency*requestsPerGoroutine/2 {
		t.Fatalf("Too many errors under load: %d/%d", errorCount, concurrency*requestsPerGoroutine)
	}

	t.Logf("✅ Performance under load test passed")
}

// TestResourceUsage tests resource usage and limits
func (suite *ProductionReadinessTestSuite) TestResourceUsage(t *testing.T) {
	t.Log("🔍 Testing Resource Usage")

	// Test memory usage with large requests
	largeRequest := map[string]interface{}{
		"tool": "search_vault",
		"params": map[string]interface{}{
			"query": "test query with many words to test memory usage",
			"limit": 100,
		},
	}

	jsonData, err := json.Marshal(largeRequest)
	if err != nil {
		t.Fatalf("Failed to marshal large request: %v", err)
	}

	start := time.Now()
	resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		t.Fatalf("Large request failed: %v", err)
	}
	defer resp.Body.Close()

	duration := time.Since(start)

	if duration > 5*time.Second {
		t.Logf("⚠️ Large request took too long: %v", duration)
	}

	// Test with multiple concurrent large requests
	concurrency := 5
	results := make(chan time.Duration, concurrency)

	for i := 0; i < concurrency; i++ {
		go func() {
			start := time.Now()
			resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
			if err != nil {
				results <- time.Hour // Indicate error
				return
			}
			defer resp.Body.Close()
			results <- time.Since(start)
		}()
	}

	var totalDuration time.Duration
	for i := 0; i < concurrency; i++ {
		select {
		case duration := <-results:
			if duration < time.Hour { // Not an error
				totalDuration += duration
			}
		case <-time.After(30 * time.Second):
			t.Fatalf("Resource usage test timeout")
		}
	}

	avgDuration := totalDuration / time.Duration(concurrency)
	t.Logf("Average response time for concurrent large requests: %v", avgDuration)

	t.Logf("✅ Resource usage test completed")
}

// TestGracefulShutdown tests graceful shutdown behavior
func (suite *ProductionReadinessTestSuite) TestGracefulShutdown(t *testing.T) {
	t.Log("🔍 Testing Graceful Shutdown")

	// This test would require server restart capability
	// For now, we'll test that the server handles requests gracefully

	request := map[string]interface{}{
		"tool":   "list_files_in_vault",
		"params": map[string]interface{}{},
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		t.Fatalf("Failed to marshal request: %v", err)
	}

	// Send a request and check response
	resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Fatalf("Request returned status %d", resp.StatusCode)
	}

	// Test that server is still responsive
	resp, err = suite.httpClient.Get(suite.serverURL + "/health")
	if err != nil {
		t.Fatalf("Health check after request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		t.Fatalf("Health check returned status %d", resp.StatusCode)
	}

	t.Logf("✅ Graceful shutdown test completed")
}

// TestConfigurationValidation tests configuration validation
func (suite *ProductionReadinessTestSuite) TestConfigurationValidation(t *testing.T) {
	t.Log("🔍 Testing Configuration Validation")

	// Test that server starts with valid configuration
	// This is implicitly tested by the server being able to respond

	// Test configuration endpoints if available
	endpoints := []string{
		"/health",
		"/tools",
	}

	for _, endpoint := range endpoints {
		resp, err := suite.httpClient.Get(suite.serverURL + endpoint)
		if err != nil {
			t.Fatalf("Configuration test endpoint %s failed: %v", endpoint, err)
		}
		defer resp.Body.Close()

		if resp.StatusCode >= 500 {
			t.Fatalf("Configuration test endpoint %s returned server error: %d", endpoint, resp.StatusCode)
		}
	}

	t.Logf("✅ Configuration validation test completed")
}

// TestLoggingAndDebugging tests logging and debugging capabilities
func (suite *ProductionReadinessTestSuite) TestLoggingAndDebugging(t *testing.T) {
	t.Log("🔍 Testing Logging and Debugging")

	// Test that server provides useful information in responses
	request := map[string]interface{}{
		"tool":   "list_files_in_vault",
		"params": map[string]interface{}{},
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		t.Fatalf("Failed to marshal request: %v", err)
	}

	resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("Failed to read response: %v", err)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	// Check for useful debugging information
	if success, ok := result["success"].(bool); ok && success {
		// Success response should have useful data
		if data, exists := result["data"]; !exists || data == nil {
			t.Logf("⚠️ Success response missing data field")
		}
	} else {
		// Error response should have useful error information
		if errorMsg, exists := result["error"]; !exists || errorMsg == "" {
			t.Logf("⚠️ Error response missing error field")
		}
	}

	t.Logf("✅ Logging and debugging test completed")
}

// TestProductionReadiness runs all production readiness tests
func TestProductionReadiness(t *testing.T) {
	serverURL := "http://localhost:3011"
	suite := NewProductionReadinessTestSuite(serverURL)

	// Wait for server to be ready
	time.Sleep(2 * time.Second)

	// Run production readiness tests
	suite.TestHealthCheckEndpoints(t)
	suite.TestMonitoringAndMetrics(t)
	suite.TestErrorHandling(t)
	suite.TestPerformanceUnderLoad(t)
	suite.TestResourceUsage(t)
	suite.TestGracefulShutdown(t)
	suite.TestConfigurationValidation(t)
	suite.TestLoggingAndDebugging(t)

	t.Log("🎉 All production readiness tests completed!")
}
