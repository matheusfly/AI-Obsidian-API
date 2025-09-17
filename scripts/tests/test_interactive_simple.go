package main

import (
	"fmt"
	"time"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

func main() {
	fmt.Println("🔧 INTERACTIVE SEARCH ENGINE TEST")
	fmt.Println("=================================")

	// Configuration
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Initialize components manually
	httpClient := client.NewHTTPClient(apiKey, baseURL)
	queryComposer := algorithms.NewQueryComposer()
	candidateAggregator := algorithms.NewCandidateAggregatorWithClient(apiKey, baseURL, httpClient.GetClient())
	bm25TFIDF := algorithms.NewBM25TFIDF()
	metadataBoost := algorithms.NewMetadataBoost()
	deduplicator := algorithms.NewDeduplicator()
	contextAssembler := algorithms.NewContextAssembler()

	fmt.Println("🔍 Initial HTTP Client Statistics:")
	stats := httpClient.GetStats()
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	// Test health check
	fmt.Println("\n🔍 Testing health check...")
	health, err := httpClient.HealthCheck()
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	fmt.Printf("✅ API Status: %s (%.3fs)\n", health.Status, health.ResponseTime.Seconds())

	fmt.Println("📊 HTTP Client Statistics after health check:")
	stats = httpClient.GetStats()
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	// Test search pipeline
	fmt.Println("\n🔍 Testing search pipeline with 'logica'...")
	startTime := time.Now()

	// Step 1: Query composition
	composedQuery := queryComposer.ComposeQuery("logica")
	fmt.Printf("   📝 Step 1: Query composition - %v\n", composedQuery["tokens"])

	// Step 2: Candidate aggregation
	candidates, err := candidateAggregator.AggregateCandidates("logica", 10)
	if err != nil {
		fmt.Printf("   ❌ Candidate aggregation failed: %v\n", err)
		return
	}
	fmt.Printf("   📄 Step 2: Candidate aggregation - %d candidates\n", len(candidates))

	// Step 3: BM25-TFIDF ranking
	rankedCandidates := bm25TFIDF.RankCandidates(candidates, "logica")
	fmt.Printf("   📊 Step 3: BM25-TFIDF ranking - %d candidates\n", len(rankedCandidates))

	// Step 4: Metadata boost
	boostedCandidates := metadataBoost.BoostCandidates(rankedCandidates, "logica")
	fmt.Printf("   ⚡ Step 4: Metadata boost - %d candidates\n", len(boostedCandidates))

	// Step 5: Deduplication
	deduplicatedCandidates := deduplicator.DeduplicateCandidates(boostedCandidates)
	fmt.Printf("   🔄 Step 5: Deduplication - %d candidates\n", len(deduplicatedCandidates))

	// Step 6: Context assembly
	context := contextAssembler.AssembleContext(deduplicatedCandidates, "logica")
	fmt.Printf("   📚 Step 6: Context assembly - %d tokens (%.1f%% budget)\n",
		context.TokenCount, context.BudgetUsed)

	totalDuration := time.Since(startTime)
	fmt.Printf("   🎉 Complete pipeline completed in %.3fs\n", totalDuration.Seconds())

	fmt.Println("📊 HTTP Client Statistics after search pipeline:")
	stats = httpClient.GetStats()
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	// Show results
	fmt.Println("\n🏆 Search Results:")
	for i, candidate := range deduplicatedCandidates {
		if i >= 5 {
			break
		}
		fmt.Printf("   %d. %s (Score: %.3f, Type: %s)\n", i+1, candidate.Name, candidate.MatchScore, candidate.MatchType)
	}

	fmt.Println("\n🎉 INTERACTIVE SEARCH ENGINE TEST COMPLETE!")
	fmt.Println("✅ All components are working!")
	fmt.Println("✅ Search pipeline is functional!")
	fmt.Println("✅ HTTP client statistics are being tracked!")
}
