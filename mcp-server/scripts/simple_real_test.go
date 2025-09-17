package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

func main() {
	fmt.Println("🔍 Simple Real Data Test")
	fmt.Println("========================")
	fmt.Println("Testing MCP Server with real Obsidian vault data")
	fmt.Println()

	client := &http.Client{Timeout: 10 * time.Second}
	serverURL := "http://localhost:3011"

	// Test 1: Health Check
	fmt.Println("1. Testing Health Check...")
	resp, err := client.Get(serverURL + "/health")
	if err != nil {
		fmt.Printf("❌ FAILED: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	var health map[string]interface{}
	json.Unmarshal(body, &health)
	
	fmt.Printf("Status: %s\n", health["status"])
	fmt.Printf("Mode: %s\n", health["mode"])
	fmt.Printf("Mock Mode: %v\n", health["mock_mode"])
	
	if health["mode"] == "real" {
		fmt.Println("✅ Server is running in REAL MODE")
	} else {
		fmt.Println("❌ Server is running in MOCK MODE")
	}

	// Test 2: List Files
	fmt.Println("\n2. Testing List Files...")
	requestBody := map[string]interface{}{
		"tool":   "list_files_in_vault",
		"params": map[string]interface{}{},
	}
	jsonBody, _ := json.Marshal(requestBody)

	resp, err = client.Post(serverURL+"/tools/execute", "application/json", bytes.NewReader(jsonBody))
	if err != nil {
		fmt.Printf("❌ FAILED: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(body, &result)

	if result["success"].(bool) {
		fmt.Printf("✅ SUCCESS: %s\n", result["message"])
		if data, ok := result["data"].([]interface{}); ok {
			fmt.Printf("Found %d files:\n", len(data))
			for i, file := range data {
				if i < 5 { // Show first 5 files
					if fileMap, ok := file.(map[string]interface{}); ok {
						name := fileMap["name"]
						fileType := fileMap["type"]
						fmt.Printf("  - %s [%s]\n", name, fileType)
					}
				}
			}
			if len(data) > 5 {
				fmt.Printf("  ... and %d more files\n", len(data)-5)
			}
		}
	} else {
		fmt.Printf("❌ FAILED: %s\n", result["error"])
	}

	// Test 3: Search
	fmt.Println("\n3. Testing Search...")
	searchBody := map[string]interface{}{
		"tool": "search_vault",
		"params": map[string]interface{}{
			"query": "AGENTS",
			"limit": 5,
		},
	}
	jsonBody, _ = json.Marshal(searchBody)

	resp, err = client.Post(serverURL+"/tools/execute", "application/json", bytes.NewReader(jsonBody))
	if err != nil {
		fmt.Printf("❌ FAILED: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ = ioutil.ReadAll(resp.Body)
	json.Unmarshal(body, &result)

	if result["success"].(bool) {
		fmt.Printf("✅ SUCCESS: %s\n", result["message"])
		if data, ok := result["data"].([]interface{}); ok {
			fmt.Printf("Found %d search results:\n", len(data))
			for _, searchResult := range data {
				if resultMap, ok := searchResult.(map[string]interface{}); ok {
					path := resultMap["path"]
					score := resultMap["score"]
					fmt.Printf("  - %s (score: %.2f)\n", path, score)
				}
			}
		}
	} else {
		fmt.Printf("❌ FAILED: %s\n", result["error"])
	}

	fmt.Println("\n✅ Simple Real Data Test Complete!")
}
