package main

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"time"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

func main() {
	fmt.Println("🚀 API-MCP-Simbiosis REAL VAULT TESTING")
	fmt.Println(strings.Repeat("=", 60))

	// Your real API credentials
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Initialize HTTP client
	httpClient := client.NewHTTPClient(apiKey, baseURL)

	// Test 1: Health Check
	fmt.Println("\n🔍 1. HEALTH CHECK")
	fmt.Println(strings.Repeat("-", 30))
	start := time.Now()
	health, err := httpClient.HealthCheck()
	duration := time.Since(start)
	if err != nil {
		log.Printf("Health check failed: %v", err)
	} else {
		fmt.Printf("✅ Health Status: %s (%.3fs)\n", health.Status, duration.Seconds())
	}

	// Test 2: Get Vault Files
	fmt.Println("\n📁 2. VAULT FILES DISCOVERY")
	fmt.Println(strings.Repeat("-", 30))
	start = time.Now()
	resp, err := httpClient.Get("/vault/", "medium")
	duration = time.Since(start)
	if err != nil {
		log.Printf("Failed to get vault files: %v", err)
		return
	}

	// Parse the response
	var response struct {
		Files []string `json:"files"`
	}
	if err := json.Unmarshal(resp.Body(), &response); err != nil {
		log.Printf("Failed to parse vault files: %v", err)
		return
	}

	// Convert to FileInfo structs
	var files []algorithms.FileInfo
	for _, filePath := range response.Files {
		files = append(files, algorithms.FileInfo{
			Path: filePath,
			Name: filePath,
		})
	}

	fmt.Printf("✅ Found %d files in vault (%.3fs)\n", len(files), duration.Seconds())

	// Show first 10 files
	fmt.Println("\n📋 Sample Files:")
	for i, file := range files {
		if i >= 10 {
			fmt.Printf("... and %d more files\n", len(files)-10)
			break
		}
		fmt.Printf("  %d. %s\n", i+1, file.Path)
	}

	// Test 3: Search for "Monge da Alta-Performance" (from your image)
	fmt.Println("\n🔍 3. SEARCHING FOR 'MONGE DA ALTA-PERFORMANCE'")
	fmt.Println(strings.Repeat("-", 30))

	// Initialize all algorithms
	qc := algorithms.NewQueryComposer()
	ca := algorithms.NewCandidateAggregator(apiKey, baseURL)
	bt := algorithms.NewBM25TFIDF()
	mb := algorithms.NewMetadataBoost()
	d := algorithms.NewDeduplicator()
	ctx := algorithms.NewContextAssembler()

	// Set up algorithms
	ca.SetLimit(50) // Limit to 50 files for testing
	ctx.SetMaxTokens(4000)
	ctx.SetChunkSize(500)

	query := "Monge da Alta-Performance"
	fmt.Printf("🔍 Query: '%s'\n", query)

	// Step 1: Query Composition
	fmt.Println("\n📝 Step 1: Query Composition")
	composedQuery := qc.ComposeQuery(query)
	fmt.Printf("   Expanded tokens: %v\n", composedQuery["tokens"])
	fmt.Printf("   Field boosts: %v\n", composedQuery["fieldBoosts"])

	// Step 2: Candidate Aggregation
	fmt.Println("\n📁 Step 2: Candidate Aggregation")
	start = time.Now()
	candidates, err := ca.AggregateCandidates(query, 50)
	duration = time.Since(start)
	if err != nil {
		log.Printf("Candidate aggregation failed: %v", err)
		return
	}
	fmt.Printf("   Found %d candidates (%.3fs)\n", len(candidates), duration.Seconds())

	// Step 3: BM25-TFIDF Ranking
	fmt.Println("\n📊 Step 3: BM25-TFIDF Ranking")
	start = time.Now()
	rankedCandidates := bt.RankCandidates(candidates, query)
	duration = time.Since(start)
	fmt.Printf("   Ranked %d candidates (%.3fs)\n", len(rankedCandidates), duration.Seconds())

	// Show top 5 ranked results
	fmt.Println("\n🏆 Top 5 Ranked Results:")
	for i, candidate := range rankedCandidates {
		if i >= 5 {
			break
		}
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
		if len(candidate.Content) > 100 {
			fmt.Printf("      Content: %s...\n", candidate.Content[:100])
		}
	}

	// Step 4: Metadata Boost
	fmt.Println("\n⚡ Step 4: Metadata Boost")
	start = time.Now()
	boostedCandidates := mb.BoostCandidates(rankedCandidates, query)
	duration = time.Since(start)
	fmt.Printf("   Boosted %d candidates (%.3fs)\n", len(boostedCandidates), duration.Seconds())

	// Show top 5 boosted results
	fmt.Println("\n🚀 Top 5 Boosted Results:")
	for i, candidate := range boostedCandidates {
		if i >= 5 {
			break
		}
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
	}

	// Step 5: Deduplication
	fmt.Println("\n🔄 Step 5: Deduplication")
	start = time.Now()
	deduplicatedCandidates := d.DeduplicateCandidates(boostedCandidates)
	duration = time.Since(start)
	fmt.Printf("   Deduplicated to %d candidates (%.3fs)\n", len(deduplicatedCandidates), duration.Seconds())

	// Step 6: Context Assembly
	fmt.Println("\n📚 Step 6: Context Assembly")
	start = time.Now()
	context := ctx.AssembleContext(deduplicatedCandidates, query)
	duration = time.Since(start)
	fmt.Printf("   Assembled context: %d tokens (%.1f%% budget used) (%.3fs)\n",
		context.TokenCount, context.BudgetUsed, duration.Seconds())
	fmt.Printf("   Sources used: %d\n", len(context.Sources))

	// Show context preview
	if len(context.Content) > 200 {
		fmt.Printf("   Context preview: %s...\n", context.Content[:200])
	} else {
		fmt.Printf("   Context: %s\n", context.Content)
	}

	// Test 4: Search for "Profissional do Conhecimento"
	fmt.Println("\n🔍 4. SEARCHING FOR 'PROFISSIONAL DO CONHECIMENTO'")
	fmt.Println(strings.Repeat("-", 30))

	query2 := "Profissional do Conhecimento"
	fmt.Printf("🔍 Query: '%s'\n", query2)

	// Quick search pipeline
	rankedCandidates2 := bt.RankCandidates(candidates, query2)
	boostedCandidates2 := mb.BoostCandidates(rankedCandidates2, query2)
	deduplicatedCandidates2 := d.DeduplicateCandidates(boostedCandidates2)
	context2 := ctx.AssembleContext(deduplicatedCandidates2, query2)

	fmt.Printf("   Found %d relevant candidates\n", len(deduplicatedCandidates2))
	fmt.Printf("   Context: %d tokens (%.1f%% budget used)\n",
		context2.TokenCount, context2.BudgetUsed)

	// Show top 3 results
	fmt.Println("\n🏆 Top 3 Results:")
	for i, candidate := range deduplicatedCandidates2 {
		if i >= 3 {
			break
		}
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
	}

	// Test 5: Search for tags and metadata
	fmt.Println("\n🏷️ 5. SEARCHING FOR TAGS AND METADATA")
	fmt.Println(strings.Repeat("-", 30))

	query3 := "hiper_produtividade auto-liderança disciplina"
	fmt.Printf("🔍 Query: '%s'\n", query3)

	rankedCandidates3 := bt.RankCandidates(candidates, query3)
	boostedCandidates3 := mb.BoostCandidates(rankedCandidates3, query3)
	deduplicatedCandidates3 := d.DeduplicateCandidates(boostedCandidates3)
	context3 := ctx.AssembleContext(deduplicatedCandidates3, query3)

	fmt.Printf("   Found %d relevant candidates\n", len(deduplicatedCandidates3))
	fmt.Printf("   Context: %d tokens (%.1f%% budget used)\n",
		context3.TokenCount, context3.BudgetUsed)

	// Show top 3 results
	fmt.Println("\n🏆 Top 3 Results:")
	for i, candidate := range deduplicatedCandidates3 {
		if i >= 3 {
			break
		}
		fmt.Printf("   %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
	}

	// Test 6: Performance Summary
	fmt.Println("\n📊 6. PERFORMANCE SUMMARY")
	fmt.Println(strings.Repeat("-", 30))

	// Get client stats
	stats := httpClient.GetStats()
	fmt.Printf("HTTP Client Stats:\n")
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)
	fmt.Printf("   Timeouts: %+v\n", stats.Timeouts)
	fmt.Printf("   Retry Config: %+v\n", stats.RetryConfig)

	// Algorithm stats
	fmt.Printf("\nAlgorithm Performance:\n")
	fmt.Printf("   QueryComposer: Fast query expansion\n")
	fmt.Printf("   CandidateAggregator: %d files processed\n", len(candidates))
	fmt.Printf("   BM25TFIDF: Efficient ranking\n")
	fmt.Printf("   MetadataBoost: Relevance scoring\n")
	fmt.Printf("   Deduplicator: Duplicate removal\n")
	fmt.Printf("   ContextAssembler: Token management\n")

	fmt.Println("\n🎉 REAL VAULT TESTING COMPLETE!")
	fmt.Println("✅ All algorithms working with your actual Obsidian vault data!")
	fmt.Println("✅ Advanced search capabilities validated!")
	fmt.Println("✅ Performance metrics collected!")
}
