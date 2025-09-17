package main

import (
	"fmt"
	"strings"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

func main() {
	fmt.Println("🔍 LOGICA SEARCH TEST")
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

	// Test with "logica" query
	query := "logica"
	fmt.Printf("\n🔍 Testing query: '%s'\n", query)

	candidates, err := candidateAggregator.AggregateCandidates(query, 50)
	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	fmt.Printf("✅ Found %d candidates\n", len(candidates))

	// Show all candidates
	for i, candidate := range candidates {
		fmt.Printf("   %d. %s (Score: %.3f, Type: %s)\n", i+1, candidate.Name, candidate.MatchScore, candidate.MatchType)

		// Show content preview for content matches
		if candidate.MatchType == "content" && len(candidate.Content) > 0 {
			preview := candidate.Content
			if len(preview) > 200 {
				preview = preview[:200] + "..."
			}
			fmt.Printf("      Content preview: %s\n", preview)
		}
	}

	// Test with variations
	variations := []string{"LOGICA", "logica", "Logica", "logicas", "logical", "Logico"}

	for _, variation := range variations {
		fmt.Printf("\n🔍 Testing variation: '%s'\n", variation)

		candidates, err := candidateAggregator.AggregateCandidates(variation, 20)
		if err != nil {
			fmt.Printf("❌ Search failed: %v\n", err)
			continue
		}

		fmt.Printf("✅ Found %d candidates\n", len(candidates))

		// Show first few candidates
		for i, candidate := range candidates {
			if i >= 3 {
				break
			}
			fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
		}
	}

	// Test with partial matches
	fmt.Println("\n🔍 Testing partial matches...")
	partialQueries := []string{"log", "logic", "logi"}

	for _, partial := range partialQueries {
		fmt.Printf("\n🔍 Testing partial: '%s'\n", partial)

		candidates, err := candidateAggregator.AggregateCandidates(partial, 10)
		if err != nil {
			fmt.Printf("❌ Search failed: %v\n", err)
			continue
		}

		fmt.Printf("✅ Found %d candidates\n", len(candidates))

		// Show first few candidates
		for i, candidate := range candidates {
			if i >= 3 {
				break
			}
			fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
		}
	}

	// Test with all files to see what's available
	fmt.Println("\n🔍 Testing with empty query (all files)...")
	allCandidates, err := candidateAggregator.AggregateCandidates("", 100)
	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	fmt.Printf("✅ Found %d total files\n", len(allCandidates))

	// Look for files that might contain "logica"
	fmt.Println("\n🔍 Looking for files that might contain 'logica'...")
	for _, candidate := range allCandidates {
		name := strings.ToLower(candidate.Name)
		path := strings.ToLower(candidate.Path)

		if strings.Contains(name, "logica") || strings.Contains(path, "logica") ||
			strings.Contains(name, "logic") || strings.Contains(path, "logic") ||
			strings.Contains(name, "logico") || strings.Contains(path, "logico") {
			fmt.Printf("🎯 Found potential match: %s\n", candidate.Name)
		}
	}
}
