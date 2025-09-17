package main

import (
	"encoding/json"
	"fmt"
	"log"

	"api-mcp-simbiosis/client"
)

func main() {
	fmt.Println("🔍 DEBUG: Vault Response Structure")
	fmt.Println("==================================")

	// Your real API credentials
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Initialize HTTP client
	httpClient := client.NewHTTPClient(apiKey, baseURL)

	// Get vault response
	resp, err := httpClient.Get("/vault/", "medium")
	if err != nil {
		log.Printf("Failed to get vault files: %v", err)
		return
	}

	fmt.Printf("Status Code: %d\n", resp.StatusCode())
	fmt.Printf("Response Headers: %+v\n", resp.Header())
	fmt.Printf("Response Body (first 500 chars): %s\n", string(resp.Body())[:min(500, len(resp.Body()))])

	// Try to parse as generic interface
	var response interface{}
	if err := json.Unmarshal(resp.Body(), &response); err != nil {
		log.Printf("Failed to parse as interface: %v", err)
		return
	}

	fmt.Printf("\nParsed Response Type: %T\n", response)
	fmt.Printf("Parsed Response: %+v\n", response)
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
