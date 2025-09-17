package main

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"api-mcp-simbiosis/client"
)

func main() {
	fmt.Println("🔍 TESTING SPECIFIC FILE ACCESS")
	fmt.Println("===============================")

	// Your real API credentials
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Initialize HTTP client
	httpClient := client.NewHTTPClient(apiKey, baseURL)

	// Test getting a specific file - let's try the "--OBJETIVOS/" directory
	fmt.Println("\n📁 Testing directory access:")
	testPaths := []string{
		"--OBJETIVOS/",
		"--OBJETIVOS/Monge da Alta-Performance.md",
		"AGENTS.md",
		"Api_obsidian_methods.md",
	}

	for _, path := range testPaths {
		fmt.Printf("\n🔍 Testing path: %s\n", path)

		resp, err := httpClient.Get("/vault/"+path, "medium")
		if err != nil {
			fmt.Printf("   ❌ Error: %v\n", err)
			continue
		}

		fmt.Printf("   ✅ Status: %d\n", resp.StatusCode())

		if resp.StatusCode() == 200 {
			body := string(resp.Body())
			if len(body) > 200 {
				fmt.Printf("   📄 Content preview: %s...\n", body[:200])
			} else {
				fmt.Printf("   📄 Content: %s\n", body)
			}

			// Try to parse as JSON to see structure
			var jsonData interface{}
			if err := json.Unmarshal(resp.Body(), &jsonData); err == nil {
				fmt.Printf("   📊 JSON Structure: %T\n", jsonData)
			}
		}
	}

	// Test searching for files that might contain our target content
	fmt.Println("\n🔍 SEARCHING FOR RELEVANT FILES")
	fmt.Println("===============================")

	// Get all files first
	resp, err := httpClient.Get("/vault/", "medium")
	if err != nil {
		log.Printf("Failed to get vault files: %v", err)
		return
	}

	var response struct {
		Files []string `json:"files"`
	}
	if err := json.Unmarshal(resp.Body(), &response); err != nil {
		log.Printf("Failed to parse vault files: %v", err)
		return
	}

	// Search for files that might contain our target content
	searchTerms := []string{
		"Monge",
		"Alta-Performance",
		"Profissional",
		"Conhecimento",
		"hiper_produtividade",
		"auto-liderança",
		"disciplina",
	}

	fmt.Printf("Found %d total files\n", len(response.Files))
	fmt.Println("\n🔍 Files matching search terms:")

	for _, term := range searchTerms {
		fmt.Printf("\n📝 Searching for '%s':\n", term)
		matches := 0
		for _, file := range response.Files {
			if strings.Contains(strings.ToLower(file), strings.ToLower(term)) {
				fmt.Printf("   ✅ %s\n", file)
				matches++
			}
		}
		if matches == 0 {
			fmt.Printf("   ❌ No matches found\n")
		}
	}

	// Test getting content from a markdown file
	fmt.Println("\n📄 TESTING MARKDOWN FILE CONTENT")
	fmt.Println("================================")

	// Try to get content from a markdown file
	markdownFiles := []string{
		"AGENTS.md",
		"Api_obsidian_methods.md",
	}

	for _, file := range markdownFiles {
		fmt.Printf("\n🔍 Getting content for: %s\n", file)

		resp, err := httpClient.Get("/vault/"+file, "medium")
		if err != nil {
			fmt.Printf("   ❌ Error: %v\n", err)
			continue
		}

		if resp.StatusCode() == 200 {
			body := string(resp.Body())
			fmt.Printf("   ✅ Content length: %d characters\n", len(body))
			if len(body) > 300 {
				fmt.Printf("   📄 Content preview:\n%s\n", body[:300])
			} else {
				fmt.Printf("   📄 Full content:\n%s\n", body)
			}
		} else {
			fmt.Printf("   ❌ Status: %d\n", resp.StatusCode())
		}
	}

	fmt.Println("\n🎉 SPECIFIC FILE TESTING COMPLETE!")
}
