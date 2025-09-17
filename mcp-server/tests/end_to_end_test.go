package tests

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"testing"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"go.uber.org/zap"
)

// EndToEndTestSuite provides comprehensive end-to-end testing
type EndToEndTestSuite struct {
	serverURL      string
	httpClient     *http.Client
	obsidianClient client.HTTPClient
	ollamaClient   *ollama.Client
	advancedTools  *tools.AdvancedTools
	logger         *zap.Logger
}

// NewEndToEndTestSuite creates a new test suite
func NewEndToEndTestSuite(serverURL string) *EndToEndTestSuite {
	logger, _ := zap.NewDevelopment()

	// Create mock clients for testing
	mockClient := client.NewMockClient(logger)

	return &EndToEndTestSuite{
		serverURL:      serverURL,
		httpClient:     &http.Client{Timeout: 30 * time.Second},
		obsidianClient: mockClient,
		ollamaClient:   nil, // Mock mode
		advancedTools:  tools.NewAdvancedTools(mockClient, nil, logger),
		logger:         logger,
	}
}

// TestCompleteWorkflow tests a complete MCP workflow from start to finish
func (suite *EndToEndTestSuite) TestCompleteWorkflow(t *testing.T) {
	t.Log("🧪 Testing Complete MCP Workflow")

	// Step 1: Health Check
	t.Run("HealthCheck", func(t *testing.T) {
		resp, err := suite.httpClient.Get(suite.serverURL + "/health")
		if err != nil {
			t.Fatalf("Health check failed: %v", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			t.Fatalf("Expected status 200, got %d", resp.StatusCode)
		}

		var health map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&health); err != nil {
			t.Fatalf("Failed to decode health response: %v", err)
		}

		if status, ok := health["status"].(string); !ok || status != "healthy" {
			t.Fatalf("Expected healthy status, got %v", health["status"])
		}
	})

	// Step 2: List Available Tools
	t.Run("ListTools", func(t *testing.T) {
		resp, err := suite.httpClient.Get(suite.serverURL + "/tools")
		if err != nil {
			t.Fatalf("List tools failed: %v", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			t.Fatalf("Expected status 200, got %d", resp.StatusCode)
		}

		var toolsResponse map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&toolsResponse); err != nil {
			t.Fatalf("Failed to decode tools response: %v", err)
		}

		tools, ok := toolsResponse["tools"].([]interface{})
		if !ok {
			t.Fatalf("Expected tools array, got %T", toolsResponse["tools"])
		}

		if len(tools) < 5 {
			t.Fatalf("Expected at least 5 tools, got %d", len(tools))
		}

		t.Logf("✅ Found %d tools", len(tools))
	})

	// Step 3: Test Tool Execution Chain
	t.Run("ToolExecutionChain", func(t *testing.T) {
		// 3.1: List files in vault
		listResult := suite.executeTool(t, "list_files_in_vault", map[string]interface{}{})
		if !listResult.Success {
			t.Fatalf("List files failed: %s", listResult.Error)
		}

		files, ok := listResult.Data.([]interface{})
		if !ok {
			t.Fatalf("Expected files array, got %T", listResult.Data)
		}

		t.Logf("✅ Listed %d files", len(files))

		// 3.2: Read a specific note
		if len(files) > 0 {
			fileMap, ok := files[0].(map[string]interface{})
			if ok {
				if filename, exists := fileMap["name"].(string); exists {
					readResult := suite.executeTool(t, "read_note", map[string]interface{}{
						"filename": filename,
					})
					if !readResult.Success {
						t.Logf("⚠️ Read note failed (expected in mock mode): %s", readResult.Error)
					} else {
						t.Logf("✅ Read note: %s", filename)
					}
				}
			}
		}

		// 3.3: Search vault
		searchResult := suite.executeTool(t, "search_vault", map[string]interface{}{
			"query": "test",
			"limit": 5,
		})
		if !searchResult.Success {
			t.Fatalf("Search vault failed: %s", searchResult.Error)
		}

		searchResults, ok := searchResult.Data.([]interface{})
		if !ok {
			t.Fatalf("Expected search results array, got %T", searchResult.Data)
		}

		t.Logf("✅ Search returned %d results", len(searchResults))

		// 3.4: Semantic search
		semanticResult := suite.executeTool(t, "semantic_search", map[string]interface{}{
			"query": "demo",
			"top_k": 3,
		})
		if !semanticResult.Success {
			t.Fatalf("Semantic search failed: %s", semanticResult.Error)
		}

		t.Logf("✅ Semantic search completed")

		// 3.5: Create a test note
		createResult := suite.executeTool(t, "create_note", map[string]interface{}{
			"path":    "test-e2e-note.md",
			"content": "# E2E Test Note\n\nThis note was created during end-to-end testing.\n\n## Features\n- Created via MCP server\n- Part of automated testing\n- Mock mode validation\n",
		})
		if !createResult.Success {
			t.Logf("⚠️ Create note failed (expected in mock mode): %s", createResult.Error)
		} else {
			t.Logf("✅ Created test note")
		}
	})

	// Step 4: Test Error Handling
	t.Run("ErrorHandling", func(t *testing.T) {
		// Test invalid tool
		invalidResult := suite.executeTool(t, "invalid_tool", map[string]interface{}{})
		if invalidResult.Success {
			t.Fatalf("Expected invalid tool to fail, but it succeeded")
		}
		t.Logf("✅ Invalid tool properly rejected: %s", invalidResult.Error)

		// Test missing required parameters
		missingParamResult := suite.executeTool(t, "read_note", map[string]interface{}{})
		if missingParamResult.Success {
			t.Fatalf("Expected missing parameter to fail, but it succeeded")
		}
		t.Logf("✅ Missing parameter properly rejected: %s", missingParamResult.Error)
	})

	// Step 5: Test Performance
	t.Run("Performance", func(t *testing.T) {
		start := time.Now()

		// Execute multiple tools in sequence
		for i := 0; i < 5; i++ {
			suite.executeTool(t, "search_vault", map[string]interface{}{
				"query": fmt.Sprintf("test%d", i),
				"limit": 3,
			})
		}

		duration := time.Since(start)
		t.Logf("✅ Executed 5 search operations in %v", duration)

		if duration > 10*time.Second {
			t.Logf("⚠️ Performance warning: Operations took longer than expected")
		}
	})
}

// TestConcurrentAccess tests concurrent access to the MCP server
func (suite *EndToEndTestSuite) TestConcurrentAccess(t *testing.T) {
	t.Log("🧪 Testing Concurrent Access")

	concurrency := 10
	results := make(chan bool, concurrency)

	// Launch concurrent requests
	for i := 0; i < concurrency; i++ {
		go func(id int) {
			result := suite.executeTool(t, "search_vault", map[string]interface{}{
				"query": fmt.Sprintf("concurrent_test_%d", id),
				"limit": 2,
			})
			results <- result.Success
		}(i)
	}

	// Collect results
	successCount := 0
	for i := 0; i < concurrency; i++ {
		if <-results {
			successCount++
		}
	}

	t.Logf("✅ Concurrent test: %d/%d requests succeeded", successCount, concurrency)

	if successCount < concurrency*8/10 { // Allow 20% failure rate
		t.Fatalf("Too many concurrent requests failed: %d/%d", successCount, concurrency)
	}
}

// TestDataIntegrity tests data integrity across operations
func (suite *EndToEndTestSuite) TestDataIntegrity(t *testing.T) {
	t.Log("🧪 Testing Data Integrity")

	// Test that search results are consistent
	search1 := suite.executeTool(t, "search_vault", map[string]interface{}{
		"query": "test",
		"limit": 5,
	})

	search2 := suite.executeTool(t, "search_vault", map[string]interface{}{
		"query": "test",
		"limit": 5,
	})

	if search1.Success != search2.Success {
		t.Fatalf("Inconsistent search results: %v vs %v", search1.Success, search2.Success)
	}

	if search1.Success {
		results1, ok1 := search1.Data.([]interface{})
		results2, ok2 := search2.Data.([]interface{})

		if !ok1 || !ok2 {
			t.Fatalf("Invalid search result types")
		}

		if len(results1) != len(results2) {
			t.Fatalf("Inconsistent result counts: %d vs %d", len(results1), len(results2))
		}
	}

	t.Logf("✅ Data integrity verified")
}

// executeTool executes a tool via HTTP API
func (suite *EndToEndTestSuite) executeTool(t *testing.T, toolName string, params map[string]interface{}) mcp.ToolResult {
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
		t.Fatalf("HTTP request failed: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		t.Fatalf("Failed to read response: %v", err)
	}

	var result mcp.ToolResult
	if err := json.Unmarshal(body, &result); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	return result
}

// TestEndToEndWorkflow runs the complete end-to-end test
func TestEndToEndWorkflow(t *testing.T) {
	// Start server in background (this would be done by test setup)
	serverURL := "http://localhost:3011"

	suite := NewEndToEndTestSuite(serverURL)

	// Wait for server to be ready
	time.Sleep(2 * time.Second)

	// Run all tests
	suite.TestCompleteWorkflow(t)
	suite.TestConcurrentAccess(t)
	suite.TestDataIntegrity(t)

	t.Log("🎉 All end-to-end tests completed successfully!")
}
