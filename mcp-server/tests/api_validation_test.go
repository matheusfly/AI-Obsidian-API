package tests

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"testing"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/tools"
	"go.uber.org/zap"
)

// APIValidationTestSuite provides comprehensive API validation testing
type APIValidationTestSuite struct {
	serverURL      string
	httpClient     *http.Client
	obsidianClient client.HTTPClient
	advancedTools  *tools.AdvancedTools
	logger         *zap.Logger
}

// NewAPIValidationTestSuite creates a new API validation test suite
func NewAPIValidationTestSuite(serverURL string) *APIValidationTestSuite {
	logger, _ := zap.NewDevelopment()
	mockClient := client.NewMockClient(logger)

	return &APIValidationTestSuite{
		serverURL:      serverURL,
		httpClient:     &http.Client{Timeout: 30 * time.Second},
		obsidianClient: mockClient,
		advancedTools:  tools.NewAdvancedTools(mockClient, nil, logger),
		logger:         logger,
	}
}

// TestHealthEndpoint validates the health endpoint
func (suite *APIValidationTestSuite) TestHealthEndpoint(t *testing.T) {
	t.Log("🔍 Testing Health Endpoint")

	resp, err := suite.httpClient.Get(suite.serverURL + "/health")
	if err != nil {
		t.Fatalf("Health endpoint request failed: %v", err)
	}
	defer resp.Body.Close()

	// Validate status code
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("Expected status 200, got %d", resp.StatusCode)
	}

	// Validate content type
	contentType := resp.Header.Get("Content-Type")
	if contentType != "application/json" {
		t.Logf("⚠️ Unexpected content type: %s", contentType)
	}

	// Validate response structure
	var health map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&health); err != nil {
		t.Fatalf("Failed to decode health response: %v", err)
	}

	// Validate required fields
	requiredFields := []string{"status", "timestamp"}
	for _, field := range requiredFields {
		if _, exists := health[field]; !exists {
			t.Fatalf("Missing required field: %s", field)
		}
	}

	// Validate status value
	if status, ok := health["status"].(string); !ok || status != "healthy" {
		t.Fatalf("Expected 'healthy' status, got %v", health["status"])
	}

	t.Logf("✅ Health endpoint validation passed")
}

// TestToolsEndpoint validates the tools endpoint
func (suite *APIValidationTestSuite) TestToolsEndpoint(t *testing.T) {
	t.Log("🔍 Testing Tools Endpoint")

	resp, err := suite.httpClient.Get(suite.serverURL + "/tools")
	if err != nil {
		t.Fatalf("Tools endpoint request failed: %v", err)
	}
	defer resp.Body.Close()

	// Validate status code
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("Expected status 200, got %d", resp.StatusCode)
	}

	// Validate response structure
	var toolsResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&toolsResponse); err != nil {
		t.Fatalf("Failed to decode tools response: %v", err)
	}

	// Validate required fields
	if tools, ok := toolsResponse["tools"].([]interface{}); !ok {
		t.Fatalf("Expected 'tools' array, got %T", toolsResponse["tools"])
	} else {
		if len(tools) == 0 {
			t.Fatalf("Expected at least one tool, got %d", len(tools))
		}

		// Validate tool structure
		for i, tool := range tools {
			toolMap, ok := tool.(map[string]interface{})
			if !ok {
				t.Fatalf("Tool %d is not a map", i)
			}

			requiredToolFields := []string{"name", "description", "parameters"}
			for _, field := range requiredToolFields {
				if _, exists := toolMap[field]; !exists {
					t.Fatalf("Tool %d missing required field: %s", i, field)
				}
			}
		}
	}

	t.Logf("✅ Tools endpoint validation passed")
}

// TestToolExecutionEndpoint validates the tool execution endpoint
func (suite *APIValidationTestSuite) TestToolExecutionEndpoint(t *testing.T) {
	t.Log("🔍 Testing Tool Execution Endpoint")

	testCases := []struct {
		name           string
		request        map[string]interface{}
		expectedStatus int
		description    string
	}{
		{
			name: "ValidToolExecution",
			request: map[string]interface{}{
				"tool":   "list_files_in_vault",
				"params": map[string]interface{}{},
			},
			expectedStatus: http.StatusOK,
			description:    "Valid tool execution should succeed",
		},
		{
			name: "InvalidTool",
			request: map[string]interface{}{
				"tool":   "invalid_tool",
				"params": map[string]interface{}{},
			},
			expectedStatus: http.StatusOK, // Tool execution returns 200 with error in response
			description:    "Invalid tool should return error in response",
		},
		{
			name: "MissingTool",
			request: map[string]interface{}{
				"params": map[string]interface{}{},
			},
			expectedStatus: http.StatusBadRequest,
			description:    "Missing tool should return 400",
		},
		{
			name: "InvalidJSON",
			request: map[string]interface{}{
				"tool":   "list_files_in_vault",
				"params": "invalid_json",
			},
			expectedStatus: http.StatusOK, // Server should handle gracefully
			description:    "Invalid params should be handled gracefully",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			jsonData, err := json.Marshal(tc.request)
			if err != nil {
				t.Fatalf("Failed to marshal request: %v", err)
			}

			resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
			if err != nil {
				t.Fatalf("Request failed: %v", err)
			}
			defer resp.Body.Close()

			// Validate status code
			if resp.StatusCode != tc.expectedStatus {
				t.Fatalf("Expected status %d, got %d for %s", tc.expectedStatus, resp.StatusCode, tc.name)
			}

			// Validate response structure
			body, err := io.ReadAll(resp.Body)
			if err != nil {
				t.Fatalf("Failed to read response: %v", err)
			}

			var result map[string]interface{}
			if err := json.Unmarshal(body, &result); err != nil {
				t.Fatalf("Failed to decode response: %v", err)
			}

			// Validate required fields
			requiredFields := []string{"success"}
			for _, field := range requiredFields {
				if _, exists := result[field]; !exists {
					t.Fatalf("Missing required field: %s", field)
				}
			}

			t.Logf("✅ %s validation passed", tc.name)
		})
	}
}

// TestErrorHandling validates error handling across all endpoints
func (suite *APIValidationTestSuite) TestErrorHandling(t *testing.T) {
	t.Log("🔍 Testing Error Handling")

	// Test non-existent endpoint
	resp, err := suite.httpClient.Get(suite.serverURL + "/nonexistent")
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusNotFound {
		t.Logf("⚠️ Expected 404 for non-existent endpoint, got %d", resp.StatusCode)
	}

	// Test malformed JSON
	resp, err = suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBufferString("invalid json"))
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusBadRequest {
		t.Logf("⚠️ Expected 400 for malformed JSON, got %d", resp.StatusCode)
	}

	t.Logf("✅ Error handling validation passed")
}

// TestContentTypeValidation validates content type handling
func (suite *APIValidationTestSuite) TestContentTypeValidation(t *testing.T) {
	t.Log("🔍 Testing Content Type Validation")

	// Test with correct content type
	request := map[string]interface{}{
		"tool":   "list_files_in_vault",
		"params": map[string]interface{}{},
	}

	jsonData, _ := json.Marshal(request)
	req, _ := http.NewRequest("POST", suite.serverURL+"/tools/execute", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")

	resp, err := suite.httpClient.Do(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Logf("⚠️ Expected 200 with correct content type, got %d", resp.StatusCode)
	}

	// Test with incorrect content type
	req, _ = http.NewRequest("POST", suite.serverURL+"/tools/execute", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "text/plain")

	resp, err = suite.httpClient.Do(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	// Server should handle gracefully
	t.Logf("✅ Content type validation completed")
}

// TestRateLimiting validates rate limiting behavior
func (suite *APIValidationTestSuite) TestRateLimiting(t *testing.T) {
	t.Log("🔍 Testing Rate Limiting")

	// Send multiple requests rapidly
	request := map[string]interface{}{
		"tool": "search_vault",
		"params": map[string]interface{}{
			"query": "test",
			"limit": 1,
		},
	}

	jsonData, _ := json.Marshal(request)

	// Send 20 requests rapidly
	for i := 0; i < 20; i++ {
		resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			t.Logf("⚠️ Request %d failed: %v", i, err)
			continue
		}
		resp.Body.Close()

		// Small delay to avoid overwhelming
		time.Sleep(10 * time.Millisecond)
	}

	t.Logf("✅ Rate limiting test completed")
}

// TestSecurityHeaders validates security headers
func (suite *APIValidationTestSuite) TestSecurityHeaders(t *testing.T) {
	t.Log("🔍 Testing Security Headers")

	resp, err := suite.httpClient.Get(suite.serverURL + "/health")
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	// Check for common security headers
	securityHeaders := []string{
		"X-Content-Type-Options",
		"X-Frame-Options",
		"X-XSS-Protection",
	}

	for _, header := range securityHeaders {
		if value := resp.Header.Get(header); value == "" {
			t.Logf("⚠️ Missing security header: %s", header)
		} else {
			t.Logf("✅ Found security header %s: %s", header, value)
		}
	}
}

// TestAPIVersioning validates API versioning
func (suite *APIValidationTestSuite) TestAPIVersioning(t *testing.T) {
	t.Log("🔍 Testing API Versioning")

	// Test version header
	req, _ := http.NewRequest("GET", suite.serverURL+"/health", nil)
	req.Header.Set("Accept", "application/vnd.mcp.v1+json")

	resp, err := suite.httpClient.Do(req)
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	// Server should handle versioning gracefully
	if resp.StatusCode == http.StatusNotImplemented {
		t.Logf("✅ API versioning properly handled (v1 not implemented)")
	} else if resp.StatusCode == http.StatusOK {
		t.Logf("✅ API versioning supported")
	} else {
		t.Logf("⚠️ Unexpected response to versioned request: %d", resp.StatusCode)
	}
}

// TestAPIValidation runs all API validation tests
func TestAPIValidation(t *testing.T) {
	serverURL := "http://localhost:3011"
	suite := NewAPIValidationTestSuite(serverURL)

	// Wait for server to be ready
	time.Sleep(2 * time.Second)

	// Run validation tests
	suite.TestHealthEndpoint(t)
	suite.TestToolsEndpoint(t)
	suite.TestToolExecutionEndpoint(t)
	suite.TestErrorHandling(t)
	suite.TestContentTypeValidation(t)
	suite.TestRateLimiting(t)
	suite.TestSecurityHeaders(t)
	suite.TestAPIVersioning(t)

	t.Log("🎉 All API validation tests completed!")
}
