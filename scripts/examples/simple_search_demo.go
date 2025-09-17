package main

import (
	"fmt"
	"strings"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

func main() {
	fmt.Println("🔍 SIMPLE SEARCH TEST")
	fmt.Println("====================")
	
	// Configuration
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"
	
	// Initialize components
	httpClient := client.NewHTTPClient(apiKey, baseURL)
	candidateAggregator := algorithms.NewCandidateAggregator(apiKey, baseURL)
	
	// Health check
	fmt.Println("🔍 Health check...")
	health, err := httpClient.HealthCheck()
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	fmt.Printf("✅ API Status: %s (%.3fs)\n", health.Status, health.ResponseTime.Seconds())
	
	// Test with simple queries that should match common files
	testQueries := []string{
		"AGENTS",
		"README",
		"API",
		"test",
		"md",
		"", // Empty query to get all files
	}
	
	for _, query := range testQueries {
		fmt.Printf("\n🔍 Testing query: '%s'\n", query)
		
		candidates, err := candidateAggregator.AggregateCandidates(query, 10)
		if err != nil {
			fmt.Printf("❌ Failed: %v\n", err)
			continue
		}
		
		fmt.Printf("✅ Found %d candidates\n", len(candidates))
		
		// Show candidates
		for i, candidate := range candidates {
			if i >= 5 {
				break
			}
			fmt.Printf("   %d. %s\n", i+1, candidate.Name)
		}
		
		// Check if we found any files with "monge" in the name
		for _, candidate := range candidates {
			if strings.Contains(strings.ToLower(candidate.Name), "monge") {
				fmt.Printf("🎯 Found Monge file: %s\n", candidate.Name)
			}
		}
	}
	
	// Test with empty query to get all files
	fmt.Println("\n🔍 Testing with empty query (get all files)...")
	candidates, err := candidateAggregator.AggregateCandidates("", 20)
	if err != nil {
		fmt.Printf("❌ Failed: %v\n", err)
		return
	}
	
	fmt.Printf("✅ Found %d total files\n", len(candidates))
	
	// Look for files containing "monge" or "performance"
	fmt.Println("\n🔍 Searching for files containing 'monge' or 'performance'...")
	for _, candidate := range candidates {
		name := strings.ToLower(candidate.Name)
		if strings.Contains(name, "monge") || strings.Contains(name, "performance") {
			fmt.Printf("🎯 Found: %s\n", candidate.Name)
		}
	}
	
	// Show all file names for debugging
	fmt.Println("\n📋 All files in vault:")
	for i, candidate := range candidates {
		if i >= 10 {
			fmt.Printf("   ... and %d more files\n", len(candidates)-10)
			break
		}
		fmt.Printf("   %d. %s\n", i+1, candidate.Name)
	}
}
