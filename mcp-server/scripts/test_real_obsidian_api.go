package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

const (
	obsidianAPIURL = "http://localhost:27124"
	apiToken       = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
)

func main() {
	fmt.Println("🔍 Testing Real Obsidian API Integration")
	fmt.Println("========================================")
	fmt.Printf("API URL: %s\n", obsidianAPIURL)
	fmt.Printf("Vault Path: D:\\Nomade Milionario\n")
	fmt.Println()

	client := &http.Client{Timeout: 10 * time.Second}

	// Test 1: Health Check
	fmt.Println("1. Testing API Health...")
	testHealth(client)

	// Test 2: List Vault Files
	fmt.Println("\n2. Testing Vault Files List...")
	testListFiles(client)

	// Test 3: Search Vault
	fmt.Println("\n3. Testing Vault Search...")
	testSearchVault(client)

	// Test 4: Read Specific Note
	fmt.Println("\n4. Testing Read Note...")
	testReadNote(client)

	// Test 5: Create Note
	fmt.Println("\n5. Testing Create Note...")
	testCreateNote(client)

	fmt.Println("\n✅ Real Obsidian API Testing Complete!")
}

func testHealth(client *http.Client) {
	req, _ := http.NewRequest("GET", obsidianAPIURL+"/health", nil)
	req.Header.Set("Authorization", "Bearer "+apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Printf("Status: %d\n", resp.StatusCode)
	fmt.Printf("Response: %s\n", string(body))
}

func testListFiles(client *http.Client) {
	req, _ := http.NewRequest("GET", obsidianAPIURL+"/vault/", nil)
	req.Header.Set("Authorization", "Bearer "+apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ List files failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Printf("Status: %d\n", resp.StatusCode)

	if resp.StatusCode == 200 {
		var files []map[string]interface{}
		json.Unmarshal(body, &files)
		fmt.Printf("✅ Found %d files/folders\n", len(files))
		for i, file := range files {
			if i < 5 { // Show first 5 files
				name := file["name"]
				path := file["path"]
				fileType := file["type"]
				fmt.Printf("  - %s (%s) [%s]\n", name, path, fileType)
			}
		}
		if len(files) > 5 {
			fmt.Printf("  ... and %d more files\n", len(files)-5)
		}
	} else {
		fmt.Printf("❌ Error: %s\n", string(body))
	}
}

func testSearchVault(client *http.Client) {
	searchQuery := map[string]interface{}{
		"query": "nomade",
		"limit": 5,
	}
	jsonBody, _ := json.Marshal(searchQuery)

	req, _ := http.NewRequest("POST", obsidianAPIURL+"/vault/search", bytes.NewBuffer(jsonBody))
	req.Header.Set("Authorization", "Bearer "+apiToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Printf("Status: %d\n", resp.StatusCode)

	if resp.StatusCode == 200 {
		var results []map[string]interface{}
		json.Unmarshal(body, &results)
		fmt.Printf("✅ Found %d search results\n", len(results))
		for i, result := range results {
			if i < 3 { // Show first 3 results
				path := result["path"]
				score := result["score"]
				fmt.Printf("  - %s (score: %.2f)\n", path, score)
			}
		}
	} else {
		fmt.Printf("❌ Error: %s\n", string(body))
	}
}

func testReadNote(client *http.Client) {
	// Try to read a common note file
	notePath := "README.md"
	req, _ := http.NewRequest("GET", obsidianAPIURL+"/vault/"+notePath, nil)
	req.Header.Set("Authorization", "Bearer "+apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Read note failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Printf("Status: %d\n", resp.StatusCode)

	if resp.StatusCode == 200 {
		var note map[string]interface{}
		json.Unmarshal(body, &note)
		content := note["content"]
		length := note["length"]
		fmt.Printf("✅ Read note: %s (%v characters)\n", notePath, length)
		fmt.Printf("Content preview: %.100s...\n", content)
	} else {
		fmt.Printf("❌ Error: %s\n", string(body))
	}
}

func testCreateNote(client *http.Client) {
	noteData := map[string]interface{}{
		"content": "# MCP Test Note\n\nThis note was created by the MCP server test.\n\n## Test Details\n- Created: " + time.Now().Format("2006-01-02 15:04:05") + "\n- Purpose: Testing real Obsidian API integration\n- Status: Success\n\n## Tags\n#mcp #test #api",
	}
	jsonBody, _ := json.Marshal(noteData)

	notePath := "MCP-Test-Real-API.md"
	req, _ := http.NewRequest("POST", obsidianAPIURL+"/vault/"+notePath, bytes.NewBuffer(jsonBody))
	req.Header.Set("Authorization", "Bearer "+apiToken)
	req.Header.Set("Content-Type", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Create note failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Printf("Status: %d\n", resp.StatusCode)

	if resp.StatusCode == 200 || resp.StatusCode == 201 {
		var result map[string]interface{}
		json.Unmarshal(body, &result)
		fmt.Printf("✅ Created note: %s\n", notePath)
		fmt.Printf("Response: %s\n", string(body))
	} else {
		fmt.Printf("❌ Error: %s\n", string(body))
	}
}
