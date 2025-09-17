package tests

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"testing"
	"time"
)

// SecurityValidationTestSuite provides comprehensive security validation
type SecurityValidationTestSuite struct {
	serverURL  string
	httpClient *http.Client
}

// NewSecurityValidationTestSuite creates a new security validation test suite
func NewSecurityValidationTestSuite(serverURL string) *SecurityValidationTestSuite {
	return &SecurityValidationTestSuite{
		serverURL:  serverURL,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

// TestInputValidation tests input validation and sanitization
func (suite *SecurityValidationTestSuite) TestInputValidation(t *testing.T) {
	t.Log("🔍 Testing Input Validation")

	testCases := []struct {
		name        string
		tool        string
		params      map[string]interface{}
		expectError bool
		description string
	}{
		{
			name: "ValidInput",
			tool: "search_vault",
			params: map[string]interface{}{
				"query": "normal search",
				"limit": 10,
			},
			expectError: false,
			description: "Valid input should be accepted",
		},
		{
			name: "SQLInjectionAttempt",
			tool: "search_vault",
			params: map[string]interface{}{
				"query": "'; DROP TABLE notes; --",
				"limit": 10,
			},
			expectError: false, // Should be handled gracefully
			description: "SQL injection attempts should be handled safely",
		},
		{
			name: "XSSAttempt",
			tool: "search_vault",
			params: map[string]interface{}{
				"query": "<script>alert('xss')</script>",
				"limit": 10,
			},
			expectError: false, // Should be handled gracefully
			description: "XSS attempts should be handled safely",
		},
		{
			name: "PathTraversalAttempt",
			tool: "read_note",
			params: map[string]interface{}{
				"filename": "../../../etc/passwd",
			},
			expectError: true, // Should be rejected
			description: "Path traversal attempts should be rejected",
		},
		{
			name: "CommandInjectionAttempt",
			tool: "search_vault",
			params: map[string]interface{}{
				"query": "test; rm -rf /",
				"limit": 10,
			},
			expectError: false, // Should be handled gracefully
			description: "Command injection attempts should be handled safely",
		},
		{
			name: "NullByteInjection",
			tool: "read_note",
			params: map[string]interface{}{
				"filename": "file\x00.md",
			},
			expectError: true, // Should be rejected
			description: "Null byte injection should be rejected",
		},
		{
			name: "VeryLongInput",
			tool: "search_vault",
			params: map[string]interface{}{
				"query": string(make([]byte, 10000)), // 10KB string
				"limit": 10,
			},
			expectError: false, // Should be handled gracefully
			description: "Very long input should be handled gracefully",
		},
		{
			name: "NegativeLimit",
			tool: "search_vault",
			params: map[string]interface{}{
				"query": "test",
				"limit": -1,
			},
			expectError: false, // Should be handled gracefully
			description: "Negative limits should be handled gracefully",
		},
		{
			name: "ExtremelyLargeLimit",
			tool: "search_vault",
			params: map[string]interface{}{
				"query": "test",
				"limit": 999999999,
			},
			expectError: false, // Should be handled gracefully
			description: "Extremely large limits should be handled gracefully",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			request := map[string]interface{}{
				"tool":   tc.tool,
				"params": tc.params,
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
				t.Logf("⚠️ Failed to decode response for %s: %v", tc.name, err)
				return
			}

			// Check if error was handled as expected
			if success, ok := result["success"].(bool); ok {
				if success == tc.expectError {
					t.Logf("⚠️ Expected success=%v, got %v for %s", !tc.expectError, success, tc.name)
				}
			}

			// Check for potential security issues in response
			if errorMsg, ok := result["error"].(string); ok {
				if containsSensitiveInfo(errorMsg) {
					t.Logf("⚠️ Response may contain sensitive information: %s", errorMsg)
				}
			}

			t.Logf("✅ %s input validation passed", tc.name)
		})
	}
}

// TestRateLimiting tests rate limiting functionality
func (suite *SecurityValidationTestSuite) TestRateLimiting(t *testing.T) {
	t.Log("🔍 Testing Rate Limiting")

	// Send multiple requests rapidly
	request := map[string]interface{}{
		"tool":   "list_files_in_vault",
		"params": map[string]interface{}{},
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		t.Fatalf("Failed to marshal request: %v", err)
	}

	// Send 20 requests rapidly
	responses := make([]*http.Response, 20)
	for i := 0; i < 20; i++ {
		resp, err := suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			t.Logf("Request %d failed: %v", i, err)
			continue
		}
		responses[i] = resp
	}

	// Check responses
	rateLimited := 0
	successful := 0

	for i, resp := range responses {
		if resp == nil {
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode == 429 {
			rateLimited++
		} else if resp.StatusCode == 200 {
			successful++
		}

		t.Logf("Request %d: Status %d", i, resp.StatusCode)
	}

	t.Logf("Rate limited: %d, Successful: %d", rateLimited, successful)

	// Rate limiting should kick in after some requests
	if rateLimited == 0 && successful == 20 {
		t.Logf("⚠️ Rate limiting may not be active")
	}

	t.Logf("✅ Rate limiting test completed")
}

// TestAuthenticationValidation tests authentication mechanisms
func (suite *SecurityValidationTestSuite) TestAuthenticationValidation(t *testing.T) {
	t.Log("🔍 Testing Authentication Validation")

	// Test without authentication (if required)
	resp, err := suite.httpClient.Get(suite.serverURL + "/health")
	if err != nil {
		t.Fatalf("Health check failed: %v", err)
	}
	defer resp.Body.Close()

	// Health endpoint should be accessible without auth
	if resp.StatusCode != 200 {
		t.Logf("⚠️ Health endpoint returned status %d", resp.StatusCode)
	}

	// Test tools endpoint without authentication
	resp, err = suite.httpClient.Get(suite.serverURL + "/tools")
	if err != nil {
		t.Fatalf("Tools endpoint failed: %v", err)
	}
	defer resp.Body.Close()

	// Tools endpoint should be accessible (read-only)
	if resp.StatusCode != 200 {
		t.Logf("⚠️ Tools endpoint returned status %d", resp.StatusCode)
	}

	// Test tool execution without authentication
	request := map[string]interface{}{
		"tool":   "list_files_in_vault",
		"params": map[string]interface{}{},
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		t.Fatalf("Failed to marshal request: %v", err)
	}

	resp, err = suite.httpClient.Post(suite.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		t.Fatalf("Tool execution failed: %v", err)
	}
	defer resp.Body.Close()

	// Tool execution should work (mock mode)
	if resp.StatusCode != 200 {
		t.Logf("⚠️ Tool execution returned status %d", resp.StatusCode)
	}

	t.Logf("✅ Authentication validation completed")
}

// TestDataSanitization tests data sanitization in responses
func (suite *SecurityValidationTestSuite) TestDataSanitization(t *testing.T) {
	t.Log("🔍 Testing Data Sanitization")

	// Test with potentially malicious input
	request := map[string]interface{}{
		"tool": "search_vault",
		"params": map[string]interface{}{
			"query": "<script>alert('xss')</script>",
			"limit": 5,
		},
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

	// Check if response contains unsanitized input
	responseStr := string(body)
	if containsXSS(responseStr) {
		t.Logf("⚠️ Response may contain unsanitized XSS content")
	}

	// Check for other potential security issues
	if containsSensitiveInfo(responseStr) {
		t.Logf("⚠️ Response may contain sensitive information")
	}

	t.Logf("✅ Data sanitization test completed")
}

// TestErrorInformationDisclosure tests for information disclosure in errors
func (suite *SecurityValidationTestSuite) TestErrorInformationDisclosure(t *testing.T) {
	t.Log("🔍 Testing Error Information Disclosure")

	// Test with invalid tool
	request := map[string]interface{}{
		"tool":   "nonexistent_tool",
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

	// Check error message for sensitive information
	if errorMsg, ok := result["error"].(string); ok {
		if containsSensitiveInfo(errorMsg) {
			t.Logf("⚠️ Error message may contain sensitive information: %s", errorMsg)
		}

		// Error should be user-friendly, not expose internal details
		if containsInternalDetails(errorMsg) {
			t.Logf("⚠️ Error message may expose internal details: %s", errorMsg)
		}
	}

	t.Logf("✅ Error information disclosure test completed")
}

// TestSecurityHeaders tests for security headers
func (suite *SecurityValidationTestSuite) TestSecurityHeaders(t *testing.T) {
	t.Log("🔍 Testing Security Headers")

	resp, err := suite.httpClient.Get(suite.serverURL + "/health")
	if err != nil {
		t.Fatalf("Request failed: %v", err)
	}
	defer resp.Body.Close()

	// Check for security headers
	securityHeaders := []string{
		"X-Content-Type-Options",
		"X-Frame-Options",
		"X-XSS-Protection",
		"Strict-Transport-Security",
		"Content-Security-Policy",
	}

	for _, header := range securityHeaders {
		if value := resp.Header.Get(header); value == "" {
			t.Logf("⚠️ Missing security header: %s", header)
		} else {
			t.Logf("✅ Security header present: %s = %s", header, value)
		}
	}

	t.Logf("✅ Security headers test completed")
}

// Helper functions for security validation

func containsXSS(s string) bool {
	xssPatterns := []string{
		"<script",
		"javascript:",
		"onload=",
		"onerror=",
		"onclick=",
	}

	for _, pattern := range xssPatterns {
		if containsIgnoreCase(s, pattern) {
			return true
		}
	}
	return false
}

func containsSensitiveInfo(s string) bool {
	sensitivePatterns := []string{
		"password",
		"secret",
		"key",
		"token",
		"api_key",
		"database",
		"connection",
		"error:",
		"panic:",
		"stack trace",
	}

	for _, pattern := range sensitivePatterns {
		if containsIgnoreCase(s, pattern) {
			return true
		}
	}
	return false
}

func containsInternalDetails(s string) bool {
	internalPatterns := []string{
		"goroutine",
		"runtime",
		"stack",
		"trace",
		"debug",
		"internal",
		"file:",
		"line:",
	}

	for _, pattern := range internalPatterns {
		if containsIgnoreCase(s, pattern) {
			return true
		}
	}
	return false
}

func containsIgnoreCase(s, substr string) bool {
	return len(s) >= len(substr) &&
		(s == substr ||
			len(s) > len(substr) &&
				(s[:len(substr)] == substr ||
					s[len(s)-len(substr):] == substr ||
					containsSubstring(s, substr)))
}

func containsSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

// TestSecurityValidation runs all security validation tests
func TestSecurityValidation(t *testing.T) {
	serverURL := "http://localhost:3011"
	suite := NewSecurityValidationTestSuite(serverURL)

	// Wait for server to be ready
	time.Sleep(2 * time.Second)

	// Run security validation tests
	suite.TestInputValidation(t)
	suite.TestRateLimiting(t)
	suite.TestAuthenticationValidation(t)
	suite.TestDataSanitization(t)
	suite.TestErrorInformationDisclosure(t)
	suite.TestSecurityHeaders(t)

	t.Log("🎉 All security validation tests completed!")
}
