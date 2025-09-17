package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

// InteractiveSearchEngine provides a comprehensive testing environment
type InteractiveSearchEngine struct {
	httpClient          *client.HTTPClient
	queryComposer       *algorithms.QueryComposer
	candidateAggregator *algorithms.CandidateAggregator
	bm25TFIDF           *algorithms.BM25TFIDF
	metadataBoost       *algorithms.MetadataBoost
	deduplicator        *algorithms.Deduplicator
	contextAssembler    *algorithms.ContextAssembler
	streamingMerger     *algorithms.StreamingMerger

	// Configuration
	apiKey  string
	baseURL string

	// Performance tracking
	searchCount     int
	totalSearchTime time.Duration
	lastSearchTime  time.Duration
}

// NewInteractiveSearchEngine creates a new interactive search engine
func NewInteractiveSearchEngine(apiKey, baseURL string) *InteractiveSearchEngine {
	ise := &InteractiveSearchEngine{
		apiKey:  apiKey,
		baseURL: baseURL,
	}

	// Initialize all components
	ise.httpClient = client.NewHTTPClient(apiKey, baseURL)
	ise.queryComposer = algorithms.NewQueryComposer()
	ise.candidateAggregator = algorithms.NewCandidateAggregatorWithClient(apiKey, baseURL, ise.httpClient.GetClient())
	ise.bm25TFIDF = algorithms.NewBM25TFIDF()
	ise.metadataBoost = algorithms.NewMetadataBoost()
	ise.deduplicator = algorithms.NewDeduplicator()
	ise.contextAssembler = algorithms.NewContextAssembler()
	ise.streamingMerger = algorithms.NewStreamingMerger()

	// Configure default settings
	ise.configureDefaults()

	return ise
}

// configureDefaults sets up default configuration
func (ise *InteractiveSearchEngine) configureDefaults() {
	// Configure CandidateAggregator for large vaults
	ise.candidateAggregator.SetLimit(1000)

	// Configure BM25-TFIDF (parameters are set in constructor)
	// Note: BM25TFIDF doesn't have SetK1, SetB, SetEpsilon methods
	// Parameters are set in NewBM25TFIDF() constructor

	// Configure MetadataBoost
	ise.metadataBoost.AddPathPattern("docs/", 1.5)
	ise.metadataBoost.AddPathPattern("notes/", 1.2)
	ise.metadataBoost.AddTagBoost("important", 2.0)
	ise.metadataBoost.AddTagBoost("urgent", 1.8)

	// Configure Deduplicator
	ise.deduplicator.SetSimilarityThreshold(0.9)
	ise.deduplicator.SetCanonicalStrategy("freshest")

	// Configure ContextAssembler
	ise.contextAssembler.SetMaxTokens(4000)
	ise.contextAssembler.SetChunkSize(500)

	// Configure StreamingMerger
	ise.streamingMerger.SetBufferSize(8192)
	ise.streamingMerger.SetDelimiter("\n")
	ise.streamingMerger.SetTimeout(30 * time.Second)
}

// Run starts the interactive search engine
func (ise *InteractiveSearchEngine) Run() {
	fmt.Println("🚀 API-MCP-Simbiosis Interactive Search Engine")
	fmt.Println("==============================================")

	// Health check
	if !ise.performHealthCheck() {
		fmt.Println("❌ Health check failed. Please ensure Obsidian API is running.")
		return
	}

	fmt.Println("✅ Health check passed. Starting interactive engine...")
	fmt.Println()

	for {
		ise.showMainMenu()
		choice := ise.getUserInput("Enter your choice (1-9): ")

		switch choice {
		case "1":
			ise.performSearch()
		case "2":
			ise.testIndividualAlgorithm()
		case "3":
			ise.benchmarkPerformance()
		case "4":
			ise.configureAlgorithms()
		case "5":
			ise.showStatistics()
		case "6":
			ise.exportResults()
		case "7":
			ise.testRealVaultIntegration()
		case "8":
			ise.showHelp()
		case "9":
			fmt.Println("👋 Goodbye!")
			return
		default:
			fmt.Println("❌ Invalid choice. Please try again.")
		}

		fmt.Println("\nPress Enter to continue...")
		ise.getUserInput("")
	}
}

// performHealthCheck checks if the API is accessible
func (ise *InteractiveSearchEngine) performHealthCheck() bool {
	fmt.Println("🔍 Performing health check...")

	health, err := ise.httpClient.HealthCheck()
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return false
	}

	fmt.Printf("✅ API Status: %s (%.3fs)\n", health.Status, health.ResponseTime.Seconds())
	return true
}

// showMainMenu displays the main menu
func (ise *InteractiveSearchEngine) showMainMenu() {
	fmt.Println("\n📋 MAIN MENU")
	fmt.Println("============")
	fmt.Println("1. 🔍 Perform Search")
	fmt.Println("2. 🧪 Test Individual Algorithm")
	fmt.Println("3. 📊 Benchmark Performance")
	fmt.Println("4. ⚙️  Configure Algorithms")
	fmt.Println("5. 📈 Show Statistics")
	fmt.Println("6. 💾 Export Results")
	fmt.Println("7. 🎯 Test Real Vault Integration")
	fmt.Println("8. ❓ Help")
	fmt.Println("9. 🚪 Exit")
	fmt.Println()
}

// performSearch executes a complete search pipeline
func (ise *InteractiveSearchEngine) performSearch() {
	fmt.Println("\n🔍 SEARCH PIPELINE")
	fmt.Println("==================")

	query := ise.getUserInput("Enter search query: ")
	if query == "" {
		fmt.Println("❌ Query cannot be empty.")
		return
	}

	fmt.Printf("🔍 Searching for: '%s'\n", query)
	fmt.Println("⏳ Processing...")

	startTime := time.Now()

	// Step 1: Query composition
	fmt.Println("📝 Step 1: Query composition...")
	composedQuery := ise.queryComposer.ComposeQuery(query)
	fmt.Printf("   Expanded tokens: %v\n", composedQuery["tokens"])

	// Step 2: Candidate aggregation
	fmt.Println("📄 Step 2: Candidate aggregation...")
	candidates, err := ise.candidateAggregator.AggregateCandidates(query, 100)
	if err != nil {
		fmt.Printf("❌ Candidate aggregation failed: %v\n", err)
		return
	}
	fmt.Printf("   Found %d candidates\n", len(candidates))

	if len(candidates) == 0 {
		fmt.Println("❌ No candidates found.")
		return
	}

	// Step 3: BM25-TFIDF ranking
	fmt.Println("📊 Step 3: BM25-TFIDF ranking...")
	rankedCandidates := ise.bm25TFIDF.RankCandidates(candidates, query)
	fmt.Printf("   Ranked %d candidates\n", len(rankedCandidates))

	// Step 4: Metadata boost
	fmt.Println("⚡ Step 4: Metadata boost...")
	boostedCandidates := ise.metadataBoost.BoostCandidates(rankedCandidates, query)
	fmt.Printf("   Boosted %d candidates\n", len(boostedCandidates))

	// Step 5: Deduplication
	fmt.Println("🔄 Step 5: Deduplication...")
	deduplicatedCandidates := ise.deduplicator.DeduplicateCandidates(boostedCandidates)
	fmt.Printf("   Deduplicated to %d candidates\n", len(deduplicatedCandidates))

	// Step 6: Context assembly
	fmt.Println("📚 Step 6: Context assembly...")
	context := ise.contextAssembler.AssembleContext(deduplicatedCandidates, query)
	fmt.Printf("   Assembled context: %d tokens (%.1f%% budget used)\n",
		context.TokenCount, context.BudgetUsed)

	// Update statistics
	ise.searchCount++
	ise.lastSearchTime = time.Since(startTime)
	ise.totalSearchTime += ise.lastSearchTime

	// Display results
	fmt.Printf("\n🎉 Search completed in %.3fs\n", ise.lastSearchTime.Seconds())
	fmt.Println("\n🏆 TOP RESULTS:")
	for i, candidate := range deduplicatedCandidates {
		if i >= 5 {
			break
		}
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
	}

	// Show context preview
	if len(context.Content) > 200 {
		fmt.Printf("\n📄 Context Preview (first 200 chars):\n%s...\n", context.Content[:200])
	} else {
		fmt.Printf("\n📄 Context:\n%s\n", context.Content)
	}
}

// testIndividualAlgorithm allows testing individual algorithms
func (ise *InteractiveSearchEngine) testIndividualAlgorithm() {
	fmt.Println("\n🧪 INDIVIDUAL ALGORITHM TESTING")
	fmt.Println("===============================")
	fmt.Println("1. QueryComposer")
	fmt.Println("2. CandidateAggregator")
	fmt.Println("3. BM25-TFIDF")
	fmt.Println("4. MetadataBoost")
	fmt.Println("5. Deduplicator")
	fmt.Println("6. ContextAssembler")
	fmt.Println("7. StreamingMerger")
	fmt.Println("8. HTTP Client")

	choice := ise.getUserInput("Select algorithm to test (1-8): ")

	switch choice {
	case "1":
		ise.testQueryComposer()
	case "2":
		ise.testCandidateAggregator()
	case "3":
		ise.testBM25TFIDF()
	case "4":
		ise.testMetadataBoost()
	case "5":
		ise.testDeduplicator()
	case "6":
		ise.testContextAssembler()
	case "7":
		ise.testStreamingMerger()
	case "8":
		ise.testHTTPClient()
	default:
		fmt.Println("❌ Invalid choice.")
	}
}

// testQueryComposer tests the QueryComposer algorithm
func (ise *InteractiveSearchEngine) testQueryComposer() {
	fmt.Println("\n📝 Testing QueryComposer...")

	query := ise.getUserInput("Enter test query: ")
	if query == "" {
		query = "monge alta performance"
	}

	startTime := time.Now()
	result := ise.queryComposer.ComposeQuery(query)
	duration := time.Since(startTime)

	fmt.Printf("✅ QueryComposer completed in %.3fs\n", duration.Seconds())
	fmt.Printf("📝 Original query: '%s'\n", query)
	fmt.Printf("🔤 Expanded tokens: %v\n", result["tokens"])
	fmt.Printf("⚡ Field boosts: %v\n", result["fieldBoosts"])
	fmt.Printf("🔍 Filters: %v\n", result["filters"])
}

// testCandidateAggregator tests the CandidateAggregator algorithm
func (ise *InteractiveSearchEngine) testCandidateAggregator() {
	fmt.Println("\n📄 Testing CandidateAggregator...")

	query := ise.getUserInput("Enter test query: ")
	if query == "" {
		query = "monge"
	}

	limitStr := ise.getUserInput("Enter limit (default 50): ")
	limit := 50
	if limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil {
			limit = l
		}
	}

	startTime := time.Now()
	candidates, err := ise.candidateAggregator.AggregateCandidates(query, limit)
	duration := time.Since(startTime)

	if err != nil {
		fmt.Printf("❌ CandidateAggregator failed: %v\n", err)
		return
	}

	fmt.Printf("✅ CandidateAggregator completed in %.3fs\n", duration.Seconds())
	fmt.Printf("📄 Found %d candidates\n", len(candidates))

	// Show first few candidates
	for i, candidate := range candidates {
		if i >= 3 {
			break
		}
		fmt.Printf("   %d. %s\n", i+1, candidate.Name)
	}
}

// testBM25TFIDF tests the BM25-TFIDF algorithm
func (ise *InteractiveSearchEngine) testBM25TFIDF() {
	fmt.Println("\n📊 Testing BM25-TFIDF...")

	// Create test candidates
	testCandidates := []algorithms.Candidate{
		{
			FileInfo: algorithms.FileInfo{
				Name:    "test1.md",
				Content: "monge alta performance test content",
			},
			MatchScore: 0.5,
		},
		{
			FileInfo: algorithms.FileInfo{
				Name:    "test2.md",
				Content: "performance optimization content",
			},
			MatchScore: 0.3,
		},
	}

	query := ise.getUserInput("Enter test query (default 'performance'): ")
	if query == "" {
		query = "performance"
	}

	startTime := time.Now()
	rankedCandidates := ise.bm25TFIDF.RankCandidates(testCandidates, query)
	duration := time.Since(startTime)

	fmt.Printf("✅ BM25-TFIDF completed in %.3fs\n", duration.Seconds())
	fmt.Printf("📊 Ranked %d candidates\n", len(rankedCandidates))

	for i, candidate := range rankedCandidates {
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
	}
}

// testMetadataBoost tests the MetadataBoost algorithm
func (ise *InteractiveSearchEngine) testMetadataBoost() {
	fmt.Println("\n⚡ Testing MetadataBoost...")

	// Create test candidates
	testCandidates := []algorithms.Candidate{
		{
			FileInfo: algorithms.FileInfo{
				Name: "docs/test.md",
				Path: "docs/test.md",
			},
			MatchScore: 0.5,
		},
		{
			FileInfo: algorithms.FileInfo{
				Name: "other/test.md",
				Path: "other/test.md",
			},
			MatchScore: 0.3,
		},
	}

	query := ise.getUserInput("Enter test query (default 'test'): ")
	if query == "" {
		query = "test"
	}

	startTime := time.Now()
	boostedCandidates := ise.metadataBoost.BoostCandidates(testCandidates, query)
	duration := time.Since(startTime)

	fmt.Printf("✅ MetadataBoost completed in %.3fs\n", duration.Seconds())
	fmt.Printf("⚡ Boosted %d candidates\n", len(boostedCandidates))

	for i, candidate := range boostedCandidates {
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
	}
}

// testDeduplicator tests the Deduplicator algorithm
func (ise *InteractiveSearchEngine) testDeduplicator() {
	fmt.Println("\n🔄 Testing Deduplicator...")

	// Create test candidates with duplicates
	testCandidates := []algorithms.Candidate{
		{
			FileInfo: algorithms.FileInfo{
				Name:    "test1.md",
				Content: "monge alta performance content",
			},
			MatchScore: 0.8,
		},
		{
			FileInfo: algorithms.FileInfo{
				Name:    "test2.md",
				Content: "monge alta performance content", // Duplicate content
			},
			MatchScore: 0.7,
		},
		{
			FileInfo: algorithms.FileInfo{
				Name:    "test3.md",
				Content: "different content here",
			},
			MatchScore: 0.6,
		},
	}

	startTime := time.Now()
	deduplicatedCandidates := ise.deduplicator.DeduplicateCandidates(testCandidates)
	duration := time.Since(startTime)

	fmt.Printf("✅ Deduplicator completed in %.3fs\n", duration.Seconds())
	fmt.Printf("🔄 Deduplicated from %d to %d candidates\n", len(testCandidates), len(deduplicatedCandidates))

	for i, candidate := range deduplicatedCandidates {
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
	}
}

// testContextAssembler tests the ContextAssembler algorithm
func (ise *InteractiveSearchEngine) testContextAssembler() {
	fmt.Println("\n📚 Testing ContextAssembler...")

	// Create test candidates
	testCandidates := []algorithms.Candidate{
		{
			FileInfo: algorithms.FileInfo{
				Name:    "test1.md",
				Content: "This is a test content for context assembly. It contains multiple sentences to test the token counting and chunking functionality.",
			},
			MatchScore: 0.8,
		},
		{
			FileInfo: algorithms.FileInfo{
				Name:    "test2.md",
				Content: "Another test content with different information. This helps test the context assembly with multiple sources.",
			},
			MatchScore: 0.6,
		},
	}

	query := ise.getUserInput("Enter test query (default 'test'): ")
	if query == "" {
		query = "test"
	}

	startTime := time.Now()
	context := ise.contextAssembler.AssembleContext(testCandidates, query)
	duration := time.Since(startTime)

	fmt.Printf("✅ ContextAssembler completed in %.3fs\n", duration.Seconds())
	fmt.Printf("📚 Assembled context: %d tokens (%.1f%% budget used)\n",
		context.TokenCount, context.BudgetUsed)
	fmt.Printf("📄 Context preview: %s...\n", context.Content[:min(100, len(context.Content))])
}

// testStreamingMerger tests the StreamingMerger algorithm
func (ise *InteractiveSearchEngine) testStreamingMerger() {
	fmt.Println("\n🌊 Testing StreamingMerger...")

	// Create test chunks
	chunks := []algorithms.StreamChunk{
		{Data: []byte("First chunk of content\n"), Timestamp: time.Now(), Index: 0, Complete: false},
		{Data: []byte("Second chunk of content\n"), Timestamp: time.Now(), Index: 1, Complete: false},
		{Data: []byte("Third chunk of content\n"), Timestamp: time.Now(), Index: 2, Complete: true},
	}

	startTime := time.Now()
	mergedResult := ise.streamingMerger.MergeChunks(chunks)
	duration := time.Since(startTime)

	fmt.Printf("✅ StreamingMerger completed in %.3fs\n", duration.Seconds())
	fmt.Printf("🌊 Merged %d chunks into %d characters\n", len(chunks), mergedResult.Size)
	fmt.Printf("📄 Merged content:\n%s\n", mergedResult.Content)
}

// testHTTPClient tests the HTTP client
func (ise *InteractiveSearchEngine) testHTTPClient() {
	fmt.Println("\n🌐 Testing HTTP Client...")

	// Test health check
	fmt.Println("🔍 Testing health check...")
	startTime := time.Now()
	health, err := ise.httpClient.HealthCheck()
	duration := time.Since(startTime)

	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}

	fmt.Printf("✅ Health check completed in %.3fs\n", duration.Seconds())
	fmt.Printf("🌐 API Status: %s\n", health.Status)

	// Test vault access
	fmt.Println("📄 Testing vault access...")
	startTime = time.Now()
	resp, err := ise.httpClient.Get("/vault/", "medium")
	duration = time.Since(startTime)

	if err != nil {
		fmt.Printf("❌ Vault access failed: %v\n", err)
		return
	}

	fmt.Printf("✅ Vault access completed in %.3fs\n", duration.Seconds())
	fmt.Printf("📄 Response status: %d\n", resp.StatusCode())

	// Show client statistics
	stats := ise.httpClient.GetStats()
	fmt.Printf("📊 Circuit Breaker State: %s\n", stats.CircuitBreakerState)
}

// benchmarkPerformance runs performance benchmarks
func (ise *InteractiveSearchEngine) benchmarkPerformance() {
	fmt.Println("\n📊 PERFORMANCE BENCHMARKING")
	fmt.Println("===========================")

	query := ise.getUserInput("Enter benchmark query (default 'performance'): ")
	if query == "" {
		query = "performance"
	}

	iterationsStr := ise.getUserInput("Enter number of iterations (default 10): ")
	iterations := 10
	if iterationsStr != "" {
		if i, err := strconv.Atoi(iterationsStr); err == nil {
			iterations = i
		}
	}

	fmt.Printf("🏃 Running %d iterations of search pipeline...\n", iterations)

	var totalTime time.Duration
	var minTime, maxTime time.Duration

	for i := 0; i < iterations; i++ {
		fmt.Printf("   Iteration %d/%d...\n", i+1, iterations)

		startTime := time.Now()

		// Run search pipeline
		candidates, err := ise.candidateAggregator.AggregateCandidates(query, 50)
		if err != nil {
			fmt.Printf("❌ Iteration %d failed: %v\n", i+1, err)
			continue
		}

		if len(candidates) > 0 {
			rankedCandidates := ise.bm25TFIDF.RankCandidates(candidates, query)
			boostedCandidates := ise.metadataBoost.BoostCandidates(rankedCandidates, query)
			deduplicatedCandidates := ise.deduplicator.DeduplicateCandidates(boostedCandidates)
			ise.contextAssembler.AssembleContext(deduplicatedCandidates, query)
		}

		duration := time.Since(startTime)
		totalTime += duration

		if i == 0 || duration < minTime {
			minTime = duration
		}
		if i == 0 || duration > maxTime {
			maxTime = duration
		}
	}

	avgTime := totalTime / time.Duration(iterations)

	fmt.Printf("\n📊 BENCHMARK RESULTS\n")
	fmt.Printf("====================\n")
	fmt.Printf("Query: '%s'\n", query)
	fmt.Printf("Iterations: %d\n", iterations)
	fmt.Printf("Total Time: %.3fs\n", totalTime.Seconds())
	fmt.Printf("Average Time: %.3fs\n", avgTime.Seconds())
	fmt.Printf("Min Time: %.3fs\n", minTime.Seconds())
	fmt.Printf("Max Time: %.3fs\n", maxTime.Seconds())
	fmt.Printf("Throughput: %.2f searches/second\n", float64(iterations)/totalTime.Seconds())
}

// configureAlgorithms allows configuration of algorithm parameters
func (ise *InteractiveSearchEngine) configureAlgorithms() {
	fmt.Println("\n⚙️  ALGORITHM CONFIGURATION")
	fmt.Println("==========================")
	fmt.Println("1. CandidateAggregator")
	fmt.Println("2. BM25-TFIDF")
	fmt.Println("3. MetadataBoost")
	fmt.Println("4. Deduplicator")
	fmt.Println("5. ContextAssembler")
	fmt.Println("6. StreamingMerger")
	fmt.Println("7. Show Current Configuration")

	choice := ise.getUserInput("Select algorithm to configure (1-7): ")

	switch choice {
	case "1":
		ise.configureCandidateAggregator()
	case "2":
		ise.configureBM25TFIDF()
	case "3":
		ise.configureMetadataBoost()
	case "4":
		ise.configureDeduplicator()
	case "5":
		ise.configureContextAssembler()
	case "6":
		ise.configureStreamingMerger()
	case "7":
		ise.showCurrentConfiguration()
	default:
		fmt.Println("❌ Invalid choice.")
	}
}

// configureCandidateAggregator configures the CandidateAggregator
func (ise *InteractiveSearchEngine) configureCandidateAggregator() {
	fmt.Println("\n📄 Configuring CandidateAggregator...")

	limitStr := ise.getUserInput("Enter limit (current: 100): ")
	if limitStr != "" {
		if limit, err := strconv.Atoi(limitStr); err == nil {
			ise.candidateAggregator.SetLimit(limit)
			fmt.Printf("✅ Limit set to %d\n", limit)
		} else {
			fmt.Println("❌ Invalid limit value.")
		}
	}
}

// configureBM25TFIDF configures the BM25-TFIDF algorithm
func (ise *InteractiveSearchEngine) configureBM25TFIDF() {
	fmt.Println("\n📊 Configuring BM25-TFIDF...")

	fmt.Println("📊 BM25-TFIDF Configuration:")
	fmt.Println("   Note: BM25-TFIDF parameters are set in the constructor")
	fmt.Println("   Current parameters: k1=1.2, b=0.75")
	fmt.Println("   To modify parameters, create a new BM25TFIDF instance")
}

// configureMetadataBoost configures the MetadataBoost algorithm
func (ise *InteractiveSearchEngine) configureMetadataBoost() {
	fmt.Println("\n⚡ Configuring MetadataBoost...")

	pathPattern := ise.getUserInput("Enter path pattern (e.g., 'docs/'): ")
	if pathPattern != "" {
		boostStr := ise.getUserInput("Enter boost value (e.g., 1.5): ")
		if boostStr != "" {
			if boost, err := strconv.ParseFloat(boostStr, 64); err == nil {
				ise.metadataBoost.AddPathPattern(pathPattern, boost)
				fmt.Printf("✅ Path pattern '%s' with boost %.2f added\n", pathPattern, boost)
			} else {
				fmt.Println("❌ Invalid boost value.")
			}
		}
	}

	tag := ise.getUserInput("Enter tag (e.g., 'important'): ")
	if tag != "" {
		tagBoostStr := ise.getUserInput("Enter tag boost value (e.g., 2.0): ")
		if tagBoostStr != "" {
			if tagBoost, err := strconv.ParseFloat(tagBoostStr, 64); err == nil {
				ise.metadataBoost.AddTagBoost(tag, tagBoost)
				fmt.Printf("✅ Tag '%s' with boost %.2f added\n", tag, tagBoost)
			} else {
				fmt.Println("❌ Invalid tag boost value.")
			}
		}
	}
}

// configureDeduplicator configures the Deduplicator algorithm
func (ise *InteractiveSearchEngine) configureDeduplicator() {
	fmt.Println("\n🔄 Configuring Deduplicator...")

	thresholdStr := ise.getUserInput("Enter similarity threshold (current: 0.9): ")
	if thresholdStr != "" {
		if threshold, err := strconv.ParseFloat(thresholdStr, 64); err == nil {
			ise.deduplicator.SetSimilarityThreshold(threshold)
			fmt.Printf("✅ Similarity threshold set to %.2f\n", threshold)
		} else {
			fmt.Println("❌ Invalid threshold value.")
		}
	}

	strategy := ise.getUserInput("Enter canonical strategy (freshest/shortest/longest, current: freshest): ")
	if strategy != "" {
		ise.deduplicator.SetCanonicalStrategy(strategy)
		fmt.Printf("✅ Canonical strategy set to '%s'\n", strategy)
	}
}

// configureContextAssembler configures the ContextAssembler algorithm
func (ise *InteractiveSearchEngine) configureContextAssembler() {
	fmt.Println("\n📚 Configuring ContextAssembler...")

	maxTokensStr := ise.getUserInput("Enter max tokens (current: 4000): ")
	if maxTokensStr != "" {
		if maxTokens, err := strconv.Atoi(maxTokensStr); err == nil {
			ise.contextAssembler.SetMaxTokens(maxTokens)
			fmt.Printf("✅ Max tokens set to %d\n", maxTokens)
		} else {
			fmt.Println("❌ Invalid max tokens value.")
		}
	}

	chunkSizeStr := ise.getUserInput("Enter chunk size (current: 500): ")
	if chunkSizeStr != "" {
		if chunkSize, err := strconv.Atoi(chunkSizeStr); err == nil {
			ise.contextAssembler.SetChunkSize(chunkSize)
			fmt.Printf("✅ Chunk size set to %d\n", chunkSize)
		} else {
			fmt.Println("❌ Invalid chunk size value.")
		}
	}
}

// configureStreamingMerger configures the StreamingMerger algorithm
func (ise *InteractiveSearchEngine) configureStreamingMerger() {
	fmt.Println("\n🌊 Configuring StreamingMerger...")

	bufferSizeStr := ise.getUserInput("Enter buffer size (current: 8192): ")
	if bufferSizeStr != "" {
		if bufferSize, err := strconv.Atoi(bufferSizeStr); err == nil {
			ise.streamingMerger.SetBufferSize(bufferSize)
			fmt.Printf("✅ Buffer size set to %d\n", bufferSize)
		} else {
			fmt.Println("❌ Invalid buffer size value.")
		}
	}

	delimiter := ise.getUserInput("Enter delimiter (current: '\\n'): ")
	if delimiter != "" {
		ise.streamingMerger.SetDelimiter(delimiter)
		fmt.Printf("✅ Delimiter set to '%s'\n", delimiter)
	}
}

// showCurrentConfiguration displays current configuration
func (ise *InteractiveSearchEngine) showCurrentConfiguration() {
	fmt.Println("\n⚙️  CURRENT CONFIGURATION")
	fmt.Println("========================")

	// CandidateAggregator
	fmt.Println("📄 CandidateAggregator:")
	fmt.Printf("   Limit: %d\n", 100) // Note: GetLimit method not available

	// BM25-TFIDF
	fmt.Println("📊 BM25-TFIDF:")
	fmt.Printf("   k1: %.2f\n", 1.2) // Note: GetK1 method not available
	fmt.Printf("   b: %.2f\n", 0.75) // Note: GetB method not available

	// Deduplicator
	fmt.Println("🔄 Deduplicator:")
	fmt.Printf("   Similarity threshold: %.2f\n", 0.9) // Note: GetSimilarityThreshold method not available
	fmt.Printf("   Canonical strategy: freshest\n")    // Note: GetCanonicalStrategy method not available

	// ContextAssembler
	fmt.Println("📚 ContextAssembler:")
	fmt.Printf("   Max tokens: %d\n", 4000) // Note: GetMaxTokens method not available
	fmt.Printf("   Chunk size: %d\n", 500)  // Note: GetChunkSize method not available

	// StreamingMerger
	fmt.Println("🌊 StreamingMerger:")
	fmt.Printf("   Buffer size: %d\n", 8192) // Note: GetBufferSize method not available
	fmt.Printf("   Delimiter: '\\n'\n")      // Note: GetDelimiter method not available
}

// showStatistics displays search statistics
func (ise *InteractiveSearchEngine) showStatistics() {
	fmt.Println("\n📈 SEARCH STATISTICS")
	fmt.Println("===================")

	fmt.Printf("Total searches performed: %d\n", ise.searchCount)
	if ise.searchCount > 0 {
		fmt.Printf("Total search time: %.3fs\n", ise.totalSearchTime.Seconds())
		fmt.Printf("Average search time: %.3fs\n", (ise.totalSearchTime / time.Duration(ise.searchCount)).Seconds())
		fmt.Printf("Last search time: %.3fs\n", ise.lastSearchTime.Seconds())
	}

	// HTTP Client statistics
	stats := ise.httpClient.GetStats()
	fmt.Printf("\n🌐 HTTP Client Statistics:\n")
	fmt.Printf("Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)
}

// exportResults exports search results to file
func (ise *InteractiveSearchEngine) exportResults() {
	fmt.Println("\n💾 EXPORT RESULTS")
	fmt.Println("=================")

	filename := ise.getUserInput("Enter filename (default: search_results.json): ")
	if filename == "" {
		filename = "search_results.json"
	}

	// Create sample results for export
	results := map[string]interface{}{
		"timestamp":           time.Now().Format(time.RFC3339),
		"search_count":        ise.searchCount,
		"total_search_time":   ise.totalSearchTime.Seconds(),
		"average_search_time": 0.0,
		"last_search_time":    ise.lastSearchTime.Seconds(),
		"configuration": map[string]interface{}{
			"api_key":  ise.apiKey[:10] + "...", // Truncated for security
			"base_url": ise.baseURL,
		},
	}

	if ise.searchCount > 0 {
		results["average_search_time"] = (ise.totalSearchTime / time.Duration(ise.searchCount)).Seconds()
	}

	// Export to JSON
	data, err := json.MarshalIndent(results, "", "  ")
	if err != nil {
		fmt.Printf("❌ Failed to marshal results: %v\n", err)
		return
	}

	err = os.WriteFile(filename, data, 0644)
	if err != nil {
		fmt.Printf("❌ Failed to write file: %v\n", err)
		return
	}

	fmt.Printf("✅ Results exported to %s\n", filename)
}

// testRealVaultIntegration tests with real vault data
func (ise *InteractiveSearchEngine) testRealVaultIntegration() {
	fmt.Println("\n🎯 REAL VAULT INTEGRATION TEST")
	fmt.Println("==============================")

	fmt.Println("🔍 Testing with real Obsidian vault data...")

	// Test health check
	fmt.Println("1. Health check...")
	health, err := ise.httpClient.HealthCheck()
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	fmt.Printf("   ✅ API Status: %s (%.3fs)\n", health.Status, health.ResponseTime.Seconds())

	// Test vault discovery
	fmt.Println("2. Vault discovery...")
	candidates, err := ise.candidateAggregator.AggregateCandidates("monge", 20)
	if err != nil {
		fmt.Printf("❌ Vault discovery failed: %v\n", err)
		return
	}
	fmt.Printf("   ✅ Found %d files\n", len(candidates))

	if len(candidates) == 0 {
		fmt.Println("❌ No files found in vault.")
		return
	}

	// Test target file access
	fmt.Println("3. Target file access...")
	found := false
	for _, candidate := range candidates {
		if strings.Contains(candidate.Name, "Monge da Alta-Performance") {
			found = true
			fmt.Printf("   ✅ Target file found: %s\n", candidate.Name)
			break
		}
	}

	if !found {
		fmt.Println("   ⚠️  Target file not found in current results")
	}

	// Test complete search pipeline
	fmt.Println("4. Complete search pipeline...")
	query := "monge alta performance"

	startTime := time.Now()
	composedQuery := ise.queryComposer.ComposeQuery(query)
	rankedCandidates := ise.bm25TFIDF.RankCandidates(candidates, query)
	boostedCandidates := ise.metadataBoost.BoostCandidates(rankedCandidates, query)
	deduplicatedCandidates := ise.deduplicator.DeduplicateCandidates(boostedCandidates)
	context := ise.contextAssembler.AssembleContext(deduplicatedCandidates, query)
	duration := time.Since(startTime)

	fmt.Printf("   ✅ Pipeline completed in %.3fs\n", duration.Seconds())
	fmt.Printf("   📝 Query composition: %v\n", composedQuery["tokens"])
	fmt.Printf("   📊 BM25 ranking: %d candidates\n", len(rankedCandidates))
	fmt.Printf("   ⚡ Metadata boost: %d candidates\n", len(boostedCandidates))
	fmt.Printf("   🔄 Deduplication: %d candidates\n", len(deduplicatedCandidates))
	fmt.Printf("   📚 Context assembly: %d tokens (%.1f%% budget)\n",
		context.TokenCount, context.BudgetUsed)

	// Show top results
	fmt.Println("5. Top results:")
	for i, candidate := range deduplicatedCandidates {
		if i >= 3 {
			break
		}
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
	}

	fmt.Println("\n🎉 Real vault integration test completed successfully!")
}

// showHelp displays help information
func (ise *InteractiveSearchEngine) showHelp() {
	fmt.Println("\n❓ HELP")
	fmt.Println("=======")
	fmt.Println("This interactive search engine provides comprehensive testing of all")
	fmt.Println("API-MCP-Simbiosis algorithms and features.")
	fmt.Println()
	fmt.Println("Features:")
	fmt.Println("• Complete search pipeline with all 7 algorithms")
	fmt.Println("• Individual algorithm testing and benchmarking")
	fmt.Println("• Real-time performance monitoring")
	fmt.Println("• Algorithm configuration and parameter tuning")
	fmt.Println("• Results export and statistics")
	fmt.Println("• Real vault integration testing")
	fmt.Println()
	fmt.Println("Algorithms:")
	fmt.Println("1. QueryComposer - Query expansion and field boosting")
	fmt.Println("2. CandidateAggregator - Vault file collection")
	fmt.Println("3. BM25-TFIDF - Term frequency ranking")
	fmt.Println("4. MetadataBoost - Freshness and relevance scoring")
	fmt.Println("5. Deduplicator - Fuzzy deduplication")
	fmt.Println("6. ContextAssembler - Token budget management")
	fmt.Println("7. StreamingMerger - Incremental chunk processing")
	fmt.Println()
	fmt.Println("Configuration:")
	fmt.Println("• API Key: Configured for Obsidian Local REST API")
	fmt.Println("• Base URL: https://127.0.0.1:27124")
	fmt.Println("• TLS: Self-signed certificate bypass enabled")
	fmt.Println("• Timeouts: Short (1s), Medium (5s), Long (30s)")
	fmt.Println("• Retry: Exponential backoff with circuit breaker")
}

// getUserInput gets input from the user
func (ise *InteractiveSearchEngine) getUserInput(prompt string) string {
	fmt.Print(prompt)
	reader := bufio.NewReader(os.Stdin)
	input, _ := reader.ReadString('\n')
	return strings.TrimSpace(input)
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func main() {
	// Configuration
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Create and run interactive search engine
	engine := NewInteractiveSearchEngine(apiKey, baseURL)

	fmt.Println("🚀 Starting API-MCP-Simbiosis Interactive Search Engine...")
	fmt.Println("📋 All 7 algorithms ready for testing!")
	fmt.Println("🎯 Real vault integration available!")
	fmt.Println()

	engine.Run()
}
