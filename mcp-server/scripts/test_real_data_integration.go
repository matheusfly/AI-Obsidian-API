package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

type ToolExecutionRequest struct {
	Tool   string                 `json:"tool"`
	Params map[string]interface{} `json:"params"`
}

type ToolExecutionResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data"`
	Error   string      `json:"error"`
	Message string      `json:"message"`
}

type HealthResponse struct {
	Status  string `json:"status"`
	Message string `json:"message"`
}

type ToolsResponse struct {
	Tools []map[string]interface{} `json:"tools"`
}

func main() {
	serverURL := "http://localhost:3010"
	client := &http.Client{Timeout: 30 * time.Second}

	fmt.Println("🧪 Testing Real Data Integration with Obsidian Vault")
	fmt.Println("==================================================")
	fmt.Println()

	// Test 1: Health Check
	fmt.Println("1. Testing Health Check...")
	resp, err := client.Get(serverURL + "/health")
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read health response: %v\n", err)
		return
	}

	var health HealthResponse
	if err := json.Unmarshal(body, &health); err != nil {
		fmt.Printf("❌ Failed to parse health response: %v\n", err)
		return
	}

	fmt.Printf("✅ Health Status: %s\n", health.Status)
	fmt.Printf("   Message: %s\n", health.Message)
	fmt.Println()

	// Test 2: List Available Tools
	fmt.Println("2. Testing Tool List...")
	resp, err = client.Get(serverURL + "/tools/list")
	if err != nil {
		fmt.Printf("❌ Tool list failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, err = io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read tools response: %v\n", err)
		return
	}

	var tools ToolsResponse
	if err := json.Unmarshal(body, &tools); err != nil {
		fmt.Printf("❌ Failed to parse tools response: %v\n", err)
		return
	}

	fmt.Printf("✅ Available Tools (%d):\n", len(tools.Tools))
	for i, tool := range tools.Tools {
		if name, ok := tool["name"].(string); ok {
			fmt.Printf("   %d. %s\n", i+1, name)
		}
	}
	fmt.Println()

	// Test 3: List Files in Vault
	fmt.Println("3. Testing List Files in Vault...")
	request := ToolExecutionRequest{
		Tool:   "list_files_in_vault",
		Params: map[string]interface{}{},
	}

	result := executeTool(client, serverURL, request)
	if result.Success {
		fmt.Printf("✅ Listed files successfully\n")
		if data, ok := result.Data.([]interface{}); ok {
			fmt.Printf("   Found %d files/folders\n", len(data))
			// Show first few files
			for i, file := range data {
				if i >= 3 { // Show only first 3
					fmt.Printf("   ... and %d more\n", len(data)-3)
					break
				}
				if fileMap, ok := file.(map[string]interface{}); ok {
					if name, ok := fileMap["name"].(string); ok {
						fmt.Printf("   - %s\n", name)
					}
				}
			}
		}
	} else {
		fmt.Printf("❌ List files failed: %s\n", result.Error)
	}
	fmt.Println()

	// Test 4: Search Vault
	fmt.Println("4. Testing Search Vault...")
	request = ToolExecutionRequest{
		Tool: "search_vault",
		Params: map[string]interface{}{
			"query": "test",
			"limit": 5,
		},
	}

	result = executeTool(client, serverURL, request)
	if result.Success {
		fmt.Printf("✅ Search completed successfully\n")
		if data, ok := result.Data.([]interface{}); ok {
			fmt.Printf("   Found %d results\n", len(data))
			for i, item := range data {
				if i >= 2 { // Show only first 2
					break
				}
				if itemMap, ok := item.(map[string]interface{}); ok {
					if path, ok := itemMap["path"].(string); ok {
						fmt.Printf("   - %s\n", path)
					}
				}
			}
		}
	} else {
		fmt.Printf("❌ Search failed: %s\n", result.Error)
	}
	fmt.Println()

	// Test 5: Create Test Note
	fmt.Println("5. Testing Create Note...")
	testContent := `# Real Data Integration Test

This note was created by the MCP server to test real data integration.

## Test Details
- Created: ` + time.Now().Format("2006-01-02 15:04:05") + `
- Server: MCP Real Data Integration
- Purpose: Verify Obsidian API connectivity

## Features Tested
- Real API calls (no mock data)
- File creation
- Content management

## Tags
#test #mcp #real-data #integration
`

	request = ToolExecutionRequest{
		Tool: "create_note",
		Params: map[string]interface{}{
			"path":    "MCP-Real-Data-Test.md",
			"content": testContent,
		},
	}

	result = executeTool(client, serverURL, request)
	if result.Success {
		fmt.Printf("✅ Note created successfully\n")
		if data, ok := result.Data.(map[string]interface{}); ok {
			if path, ok := data["path"].(string); ok {
				fmt.Printf("   Created: %s\n", path)
			}
		}
	} else {
		fmt.Printf("❌ Create note failed: %s\n", result.Error)
	}
	fmt.Println()

	// Test 6: Read Test Note
	fmt.Println("6. Testing Read Note...")
	request = ToolExecutionRequest{
		Tool: "read_note",
		Params: map[string]interface{}{
			"filename": "MCP-Real-Data-Test.md",
		},
	}

	result = executeTool(client, serverURL, request)
	if result.Success {
		fmt.Printf("✅ Note read successfully\n")
		if data, ok := result.Data.(map[string]interface{}); ok {
			if content, ok := data["content"].(string); ok {
				fmt.Printf("   Content length: %d characters\n", len(content))
				// Show first 100 characters
				if len(content) > 100 {
					fmt.Printf("   Preview: %s...\n", content[:100])
				} else {
					fmt.Printf("   Content: %s\n", content)
				}
			}
		}
	} else {
		fmt.Printf("❌ Read note failed: %s\n", result.Error)
	}
	fmt.Println()

	// Test 7: Semantic Search
	fmt.Println("7. Testing Semantic Search...")
	request = ToolExecutionRequest{
		Tool: "semantic_search",
		Params: map[string]interface{}{
			"query": "integration test",
			"top_k": 3,
		},
	}

	result = executeTool(client, serverURL, request)
	if result.Success {
		fmt.Printf("✅ Semantic search completed\n")
		if data, ok := result.Data.(map[string]interface{}); ok {
			if results, ok := data["results"].([]interface{}); ok {
				fmt.Printf("   Found %d semantic results\n", len(results))
			}
		}
	} else {
		fmt.Printf("❌ Semantic search failed: %s\n", result.Error)
	}
	fmt.Println()

	fmt.Println("🎉 Real Data Integration Test Complete!")
	fmt.Println("=====================================")
	fmt.Println("All tests have been executed against the real Obsidian vault.")
	fmt.Println("No mock data was used - all operations used live API calls.")
}

func executeTool(client *http.Client, serverURL string, request ToolExecutionRequest) ToolExecutionResponse {
	jsonData, err := json.Marshal(request)
	if err != nil {
		return ToolExecutionResponse{Success: false, Error: fmt.Sprintf("Failed to marshal request: %v", err)}
	}

	resp, err := client.Post(serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return ToolExecutionResponse{Success: false, Error: fmt.Sprintf("Failed to execute tool: %v", err)}
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return ToolExecutionResponse{Success: false, Error: fmt.Sprintf("Failed to read response: %v", err)}
	}

	var result ToolExecutionResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return ToolExecutionResponse{Success: false, Error: fmt.Sprintf("Failed to parse response: %v", err)}
	}

	return result
}
