package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

func main() {
	fmt.Println("🧪 Testing MCP Server Tool Execution")
	fmt.Println("====================================")

	// Test data
	testCases := []struct {
		name   string
		tool   string
		params map[string]interface{}
	}{
		{
			name: "List Files",
			tool: "list_files_in_vault",
			params: map[string]interface{}{},
		},
		{
			name: "Read Note",
			tool: "read_note",
			params: map[string]interface{}{
				"filename": "test-note.md",
			},
		},
		{
			name: "Search Vault",
			tool: "search_vault",
			params: map[string]interface{}{
				"query": "test",
				"limit": 5,
			},
		},
		{
			name: "Semantic Search",
			tool: "semantic_search",
			params: map[string]interface{}{
				"query": "demo",
				"top_k": 3,
			},
		},
		{
			name: "Create Note",
			tool: "create_note",
			params: map[string]interface{}{
				"path":    "test-created-note.md",
				"content": "# Test Created Note\n\nThis note was created via MCP server.",
			},
		},
	}

	// Test each tool
	for i, testCase := range testCases {
		fmt.Printf("\n%d. Testing %s...\n", i+1, testCase.name)
		
		// Prepare request
		request := map[string]interface{}{
			"tool":   testCase.tool,
			"params": testCase.params,
		}
		
		jsonData, err := json.Marshal(request)
		if err != nil {
			fmt.Printf("❌ Failed to marshal request: %v\n", err)
			continue
		}
		
		// Make HTTP request
		resp, err := http.Post("http://localhost:3011/tools/execute", "application/json", bytes.NewBuffer(jsonData))
		if err != nil {
			fmt.Printf("❌ HTTP request failed: %v\n", err)
			continue
		}
		defer resp.Body.Close()
		
		// Read response
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			fmt.Printf("❌ Failed to read response: %v\n", err)
			continue
		}
		
		// Parse response
		var result map[string]interface{}
		if err := json.Unmarshal(body, &result); err != nil {
			fmt.Printf("❌ Failed to parse response: %v\n", err)
			fmt.Printf("Raw response: %s\n", string(body))
			continue
		}
		
		// Display result
		success, ok := result["success"].(bool)
		if ok && success {
			fmt.Printf("✅ Success: %v\n", result["message"])
		} else {
			fmt.Printf("❌ Failed: %v\n", result["error"])
		}
		
		// Show data if available
		if data, ok := result["data"]; ok && data != nil {
			fmt.Printf("   Data: %+v\n", data)
		}
	}

	fmt.Println("\n🎉 Tool execution testing completed!")
}
