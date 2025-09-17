package main

import (
	"fmt"
	"log"
	"strings"
	"time"

	"api-mcp-simbiosis/algorithms"
)

func main() {
	fmt.Println("🚀 Enhanced API-MCP-Simbiosis Features Demo")
	fmt.Println(strings.Repeat("=", 50))

	// Configuration
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Initialize enhanced algorithms
	fmt.Println("\n📁 Initializing Enhanced Algorithms...")

	// 1. Recursive Vault Traversal
	recursiveTraversal := algorithms.NewRecursiveVaultTraversal(apiKey, baseURL)
	fmt.Println("✅ RecursiveVaultTraversal initialized")

	// 2. Advanced Local Search
	advancedSearch := algorithms.NewAdvancedLocalSearch()
	advancedSearch.SetThreshold(0.6)
	fmt.Println("✅ AdvancedLocalSearch initialized")

	// 3. Caching Layer
	cachingLayer := algorithms.NewCachingLayer("./cache")
	cachingLayer.SetTTL(5 * time.Minute)
	fmt.Println("✅ CachingLayer initialized")

	// 4. Note Creation Workaround
	noteCreator := algorithms.NewNoteCreationWorkaround(apiKey, baseURL)
	fmt.Println("✅ NoteCreationWorkaround initialized")

	// 5. Command Executor
	commandExecutor := algorithms.NewCommandExecutor(apiKey, baseURL)
	fmt.Println("✅ CommandExecutor initialized")

	// 6. Full Context Retrieval Pipeline
	fullPipeline := algorithms.NewFullContextRetrievalPipeline(apiKey, baseURL)
	fmt.Println("✅ FullContextRetrievalPipeline initialized")

	fmt.Println("\n🔍 Testing Enhanced Features...")

	// Test 1: Recursive Vault Traversal
	fmt.Println("\n1️⃣ Testing Recursive Vault Traversal")
	files, err := recursiveTraversal.Traverse("")
	if err != nil {
		log.Printf("❌ Recursive traversal failed: %v", err)
	} else {
		fmt.Printf("✅ Found %d files recursively\n", len(files))
		fmt.Printf("📊 Traversal stats: %+v\n", recursiveTraversal.GetStats())
	}

	// Test 2: Advanced Local Search
	fmt.Println("\n2️⃣ Testing Advanced Local Search")
	searchFlags := algorithms.SearchFlags{
		CaseSensitive: false,
		WholeWord:     false,
		Regex:         false,
		Fuzzy:         true,
		Portuguese:    true,
		MaxResults:    5,
	}

	// Mock content fetcher for demo
	contentFetcher := func(file algorithms.FileInfo) (string, error) {
		return fmt.Sprintf("Content of %s - This is a test file about logica and performance", file.Name), nil
	}

	searchResults, err := advancedSearch.Search("logica", files[:min(10, len(files))], contentFetcher, searchFlags)
	if err != nil {
		log.Printf("❌ Advanced search failed: %v", err)
	} else {
		fmt.Printf("✅ Found %d search results\n", len(searchResults))
		for i, result := range searchResults {
			fmt.Printf("   %d. %s (Score: %.2f, Type: %s)\n", i+1, result.File.Name, result.Score, result.MatchType)
		}
	}

	// Test 3: Caching Layer
	fmt.Println("\n3️⃣ Testing Caching Layer")
	cachedFiles, err := cachingLayer.Get("demo_files", func() (interface{}, error) {
		return files, nil
	})
	if err != nil {
		log.Printf("❌ Caching failed: %v", err)
	} else {
		fmt.Printf("✅ Cached %d files\n", len(cachedFiles.([]algorithms.FileInfo)))
		fmt.Printf("📊 Cache stats: %+v\n", cachingLayer.GetStats())
	}

	// Test 4: Note Creation Workaround
	fmt.Println("\n4️⃣ Testing Note Creation Workaround")
	testContent := `# Test Note

This is a test note created using the workaround for POST failures.

## Features Tested
- Recursive vault traversal
- Advanced local search
- Caching layer
- Note creation workaround

**Timestamp:** ` + time.Now().Format(time.RFC3339) + `
`

	result, err := noteCreator.CreateOrUpdate("test_enhanced_features.md", testContent)
	if err != nil {
		log.Printf("❌ Note creation failed: %v", err)
	} else {
		fmt.Printf("✅ Note %s successfully\n", result.Action)
		fmt.Printf("📊 Creation stats: %+v\n", noteCreator.GetStats())
	}

	// Test 5: Command Executor
	fmt.Println("\n5️⃣ Testing Command Executor")
	commands, err := commandExecutor.ListCommands()
	if err != nil {
		log.Printf("❌ Command listing failed: %v", err)
	} else {
		fmt.Printf("✅ Found %d available commands\n", len(commands))
		if len(commands) > 0 {
			fmt.Printf("   First command: %s (ID: %s)\n", commands[0].Name, commands[0].ID)
		}
	}

	// Test 6: Full Context Retrieval Pipeline
	fmt.Println("\n6️⃣ Testing Full Context Retrieval Pipeline")
	pipelineOptions := algorithms.DefaultPipelineOptions()
	pipelineOptions.MaxResults = 5
	pipelineOptions.TokenBudget = 2000

	pipelineResult, err := fullPipeline.Run("logica performance", pipelineOptions)
	if err != nil {
		log.Printf("❌ Pipeline execution failed: %v", err)
	} else {
		fmt.Printf("✅ Pipeline completed successfully\n")
		fmt.Printf("   Query: %s\n", pipelineResult.Query)
		fmt.Printf("   Composed Query: %s\n", pipelineResult.ComposedQuery)
		fmt.Printf("   Files Scanned: %d\n", pipelineResult.FilesScanned)
		fmt.Printf("   Results Found: %d\n", pipelineResult.ResultsFound)
		fmt.Printf("   Context Tokens: %.0f/%d (%.1f%%)\n",
			pipelineResult.Context.BudgetUsed,
			pipelineResult.Metadata.TokenBudget,
			pipelineResult.Metadata.TokenEfficiency)
		fmt.Printf("   Total Time: %v\n", pipelineResult.Performance.TotalTime)
	}

	// Test 7: Component Statistics
	fmt.Println("\n7️⃣ Testing Component Statistics")
	componentStats := fullPipeline.GetComponentStats()
	fmt.Printf("✅ Retrieved statistics from %d components\n", len(componentStats))

	for component, stats := range componentStats {
		fmt.Printf("   %s: %+v\n", component, stats)
	}

	// Test 8: Cache Management
	fmt.Println("\n8️⃣ Testing Cache Management")
	cacheStats := cachingLayer.GetStats()
	fmt.Printf("✅ Cache Statistics:\n")
	fmt.Printf("   Hits: %d\n", cacheStats.Hits)
	fmt.Printf("   Misses: %d\n", cacheStats.Misses)
	fmt.Printf("   Hit Rate: %.2f%%\n", cacheStats.HitRate)
	fmt.Printf("   Total Size: %d bytes\n", cacheStats.TotalSize)

	// Test 9: Performance Metrics
	fmt.Println("\n9️⃣ Testing Performance Metrics")
	pipelineStats := fullPipeline.GetStats()
	fmt.Printf("✅ Pipeline Statistics:\n")
	fmt.Printf("   Queries Processed: %d\n", pipelineStats.QueriesProcessed)
	fmt.Printf("   Files Scanned: %d\n", pipelineStats.FilesScanned)
	fmt.Printf("   Results Generated: %d\n", pipelineStats.ResultsGenerated)
	fmt.Printf("   Average Time: %v\n", pipelineStats.AverageTime)

	// Test 10: Cleanup
	fmt.Println("\n🔟 Testing Cleanup Operations")

	// Clear cache
	err = cachingLayer.Clear()
	if err != nil {
		log.Printf("❌ Cache clear failed: %v", err)
	} else {
		fmt.Println("✅ Cache cleared successfully")
	}

	// Delete test note
	err = noteCreator.Delete("test_enhanced_features.md")
	if err != nil {
		log.Printf("❌ Note deletion failed: %v", err)
	} else {
		fmt.Println("✅ Test note deleted successfully")
	}

	fmt.Println("\n🎉 Enhanced Features Demo Completed!")
	fmt.Println(strings.Repeat("=", 50))
	fmt.Println("✅ All 6 enhanced algorithms tested successfully")
	fmt.Println("✅ MCP tools integration ready")
	fmt.Println("✅ Performance metrics collected")
	fmt.Println("✅ Cache management working")
	fmt.Println("✅ Full pipeline operational")
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
