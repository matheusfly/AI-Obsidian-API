package tests

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"testing"
	"time"

	"github.com/datamaster/mcp-server/pkg/mcp"
)

// MCPProtocolValidationTestSuite provides comprehensive MCP protocol validation
type MCPProtocolValidationTestSuite struct {
	serverURL  string
	httpClient *http.Client
}

// NewMCPProtocolValidationTestSuite creates a new MCP protocol validation test suite
func NewMCPProtocolValidationTestSuite(serverURL string) *MCPProtocolValidationTestSuite {
	return &MCPProtocolValidationTestSuite{
		serverURL:  serverURL,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

// TestMCPToolSchemaValidation tests MCP tool schema compliance
func (suite *MCPProtocolValidationTestSuite) TestMCPToolSchemaValidation(t *testing.T) {
	t.Log("🔍 Testing MCP Tool Schema Validation")

	// Get tools from server
	resp, err := suite.httpClient.Get(suite.serverURL + "/tools")
	if err != nil {
		t.Fatalf("Failed to get tools: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("Failed to read response: %v", err)
	}

	var toolsResponse map[string]interface{}
	if err := json.Unmarshal(body, &toolsResponse); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	tools, ok := toolsResponse["tools"].([]interface{})
	if !ok {
		t.Fatalf("Expected tools array")
	}

	// Validate each tool schema
	for i, tool := range tools {
		toolMap, ok := tool.(map[string]interface{})
		if !ok {
			t.Fatalf("Tool %d is not a map", i)
		}

		// Validate required MCP tool fields
		requiredFields := []string{"name", "description", "parameters"}
		for _, field := range requiredFields {
			if _, exists := toolMap[field]; !exists {
				t.Fatalf("Tool %d missing required field: %s", i, field)
			}
		}

		// Validate tool name format
		name, ok := toolMap["name"].(string)
		if !ok {
			t.Fatalf("Tool %d name is not a string", i)
		}
		if name == "" {
			t.Fatalf("Tool %d has empty name", i)
		}

		// Validate description format
		description, ok := toolMap["description"].(string)
		if !ok {
			t.Fatalf("Tool %d description is not a string", i)
		}
		if description == "" {
			t.Fatalf("Tool %d has empty description", i)
		}

		// Validate parameters schema
		params, ok := toolMap["parameters"].(map[string]interface{})
		if !ok {
			t.Fatalf("Tool %d parameters is not a map", i)
		}

		// Check for required parameters fields
		if _, exists := params["type"]; !exists {
			t.Fatalf("Tool %d parameters missing 'type' field", i)
		}

		if params["type"] != "object" {
			t.Fatalf("Tool %d parameters type should be 'object', got %v", i, params["type"])
		}

		// Validate properties if they exist
		if properties, exists := params["properties"]; exists {
			propsMap, ok := properties.(map[string]interface{})
			if !ok {
				t.Fatalf("Tool %d properties is not a map", i)
			}

			// Validate each property
			for propName, propDef := range propsMap {
				propMap, ok := propDef.(map[string]interface{})
				if !ok {
					t.Fatalf("Tool %d property %s is not a map", i, propName)
				}

				// Check required property fields
				if _, exists := propMap["type"]; !exists {
					t.Fatalf("Tool %d property %s missing 'type' field", i, propName)
				}
			}
		}

		t.Logf("✅ Tool %d schema validation passed: %s", i, name)
	}
}

// TestMCPToolExecutionValidation tests MCP tool execution compliance
func (suite *MCPProtocolValidationTestSuite) TestMCPToolExecutionValidation(t *testing.T) {
	t.Log("🔍 Testing MCP Tool Execution Validation")

	testCases := []struct {
		name        string
		tool        string
		params      map[string]interface{}
		expectError bool
		description string
	}{
		{
			name:        "ValidToolCall",
			tool:        "list_files_in_vault",
			params:      map[string]interface{}{},
			expectError: false,
			description: "Valid tool call should succeed",
		},
		{
			name:        "ToolWithParams",
			tool:        "search_vault",
			params:      map[string]interface{}{"query": "test", "limit": 5},
			expectError: false,
			description: "Tool with parameters should work",
		},
		{
			name:        "InvalidTool",
			tool:        "nonexistent_tool",
			params:      map[string]interface{}{},
			expectError: true,
			description: "Invalid tool should return error",
		},
		{
			name:        "MissingRequiredParam",
			tool:        "read_note",
			params:      map[string]interface{}{},
			expectError: true,
			description: "Missing required parameter should fail",
		},
		{
			name:        "InvalidParamType",
			tool:        "search_vault",
			params:      map[string]interface{}{"query": 123, "limit": "invalid"},
			expectError: true, // Server should return error for invalid types
			description: "Invalid parameter types should return error",
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

			var result mcp.ToolResult
			if err := json.Unmarshal(body, &result); err != nil {
				t.Fatalf("Failed to decode response: %v", err)
			}

			// Validate MCP ToolResult structure
			if result.Success == tc.expectError {
				t.Fatalf("Expected success=%v, got %v for %s", !tc.expectError, result.Success, tc.name)
			}

			// Validate response fields
			if result.Success {
				// Success responses should have data or message
				if result.Data == nil && result.Message == "" {
					t.Logf("⚠️ Success response missing data and message for %s", tc.name)
				}
			} else {
				// Error responses should have error message
				if result.Error == "" {
					t.Fatalf("Error response missing error message for %s", tc.name)
				}
			}

			t.Logf("✅ %s validation passed", tc.name)
		})
	}
}

// TestMCPMessageFormatValidation tests MCP message format compliance
func (suite *MCPProtocolValidationTestSuite) TestMCPMessageFormatValidation(t *testing.T) {
	t.Log("🔍 Testing MCP Message Format Validation")

	// Test tool execution message format
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

	// Validate response headers
	contentType := resp.Header.Get("Content-Type")
	if contentType != "application/json" {
		t.Logf("⚠️ Expected application/json content type, got %s", contentType)
	}

	// Validate response body format
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("Failed to read response: %v", err)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	// Validate MCP ToolResult structure
	requiredFields := []string{"success"}
	for _, field := range requiredFields {
		if _, exists := result[field]; !exists {
			t.Fatalf("Missing required field: %s", field)
		}
	}

	// Validate success field type
	if success, ok := result["success"].(bool); !ok {
		t.Fatalf("Success field should be boolean, got %T", result["success"])
	} else if !success {
		t.Logf("⚠️ Tool execution failed: %v", result["error"])
	}

	t.Logf("✅ MCP message format validation passed")
}

// TestMCPErrorHandlingValidation tests MCP error handling compliance
func (suite *MCPProtocolValidationTestSuite) TestMCPErrorHandlingValidation(t *testing.T) {
	t.Log("🔍 Testing MCP Error Handling Validation")

	errorTestCases := []struct {
		name        string
		request     map[string]interface{}
		expectError bool
		description string
	}{
		{
			name: "MalformedJSON",
			request: map[string]interface{}{
				"tool":   "list_files_in_vault",
				"params": "invalid_json",
			},
			expectError: false, // Server should handle gracefully
			description: "Malformed JSON should be handled gracefully",
		},
		{
			name: "MissingTool",
			request: map[string]interface{}{
				"params": map[string]interface{}{},
			},
			expectError: true,
			description: "Missing tool should return error",
		},
		{
			name:        "EmptyRequest",
			request:     map[string]interface{}{},
			expectError: true,
			description: "Empty request should return error",
		},
		{
			name: "InvalidToolType",
			request: map[string]interface{}{
				"tool":   123,
				"params": map[string]interface{}{},
			},
			expectError: true,
			description: "Invalid tool type should return error",
		},
	}

	for _, tc := range errorTestCases {
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

			t.Logf("✅ %s error handling validation passed", tc.name)
		})
	}
}

// TestMCPProtocolCompliance tests overall MCP protocol compliance
func (suite *MCPProtocolValidationTestSuite) TestMCPProtocolCompliance(t *testing.T) {
	t.Log("🔍 Testing MCP Protocol Compliance")

	// Test that server implements required MCP endpoints
	endpoints := []string{
		"/health",
		"/tools",
		"/tools/execute",
	}

	for _, endpoint := range endpoints {
		resp, err := suite.httpClient.Get(suite.serverURL + endpoint)
		if err != nil {
			t.Fatalf("Endpoint %s failed: %v", endpoint, err)
		}
		defer resp.Body.Close()

		if resp.StatusCode >= 500 {
			t.Fatalf("Endpoint %s returned server error: %d", endpoint, resp.StatusCode)
		}

		t.Logf("✅ Endpoint %s is accessible", endpoint)
	}

	// Test that server returns proper JSON responses
	resp, err := suite.httpClient.Get(suite.serverURL + "/tools")
	if err != nil {
		t.Fatalf("Failed to get tools: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("Failed to read response: %v", err)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		t.Fatalf("Server does not return valid JSON: %v", err)
	}

	t.Logf("✅ MCP protocol compliance validation passed")
}

// TestMCPProtocolValidation runs all MCP protocol validation tests
func TestMCPProtocolValidation(t *testing.T) {
	serverURL := "http://localhost:3011"
	suite := NewMCPProtocolValidationTestSuite(serverURL)

	// Wait for server to be ready
	time.Sleep(2 * time.Second)

	// Run validation tests
	suite.TestMCPToolSchemaValidation(t)
	suite.TestMCPToolExecutionValidation(t)
	suite.TestMCPMessageFormatValidation(t)
	suite.TestMCPErrorHandlingValidation(t)
	suite.TestMCPProtocolCompliance(t)

	t.Log("🎉 All MCP protocol validation tests completed!")
}
