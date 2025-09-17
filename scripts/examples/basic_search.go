package main

import (
	"fmt"
	"log"
	"strings"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

func main() {
	fmt.Println("🚀 API-MCP-Simbiosis Advanced Search Engine Demo")
	fmt.Println(strings.Repeat("=", 50))

	// Configuration
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"
	query := "monge alta performance"

	// Initialize HTTP client
	httpClient := client.NewHTTPClient(apiKey, baseURL)

	// Health check
	fmt.Println("🔍 Performing health check...")
	health, err := httpClient.HealthCheck()
	if err != nil {
		log.Fatalf("Health check failed: %v", err)
	}
	fmt.Printf("Health Status: %s (%.3fs)\n", health.Status, health.ResponseTime.Seconds())

	if health.Status != "healthy" {
		fmt.Println("⚠️ API is not healthy, but continuing with demo...")
	}

	// Initialize algorithms
	queryComposer := algorithms.NewQueryComposer()
	candidateAggregator := algorithms.NewCandidateAggregator(apiKey, baseURL)
	bm25TFIDF := algorithms.NewBM25TFIDF()
	metadataBoost := algorithms.NewMetadataBoost()
	deduplicator := algorithms.NewDeduplicator()
	contextAssembler := algorithms.NewContextAssembler()

	fmt.Printf("\n🔍 Searching for: '%s'\n", query)
	fmt.Println(strings.Repeat("-", 30))

	// Step 1: Compose query
	fmt.Println("1. Composing query...")
	composedQuery := queryComposer.ComposeQuery(query)
	fmt.Printf("   Expanded tokens: %v\n", composedQuery["tokens"])

	// Step 2: Aggregate candidates
	fmt.Println("2. Aggregating candidates...")
	candidates, err := candidateAggregator.AggregateCandidates(query, 50)
	if err != nil {
		log.Fatalf("Failed to aggregate candidates: %v", err)
	}
	fmt.Printf("   Found %d candidates\n", len(candidates))

	if len(candidates) == 0 {
		fmt.Println("❌ No candidates found. Exiting demo.")
		return
	}

	// Step 3: Rank with BM25/TF-IDF
	fmt.Println("3. Ranking with BM25/TF-IDF...")
	rankedCandidates := bm25TFIDF.RankCandidates(candidates, query)
	fmt.Printf("   Ranked %d candidates\n", len(rankedCandidates))

	// Step 4: Apply metadata boosting
	fmt.Println("4. Applying metadata boosting...")
	boostedCandidates := metadataBoost.BoostCandidates(rankedCandidates, query)
	fmt.Printf("   Boosted %d candidates\n", len(boostedCandidates))

	// Step 5: Deduplicate
	fmt.Println("5. Deduplicating results...")
	deduplicatedCandidates := deduplicator.DeduplicateCandidates(boostedCandidates)
	fmt.Printf("   Deduplicated to %d candidates\n", len(deduplicatedCandidates))

	// Step 6: Assemble context
	fmt.Println("6. Assembling context...")
	context := contextAssembler.AssembleContext(deduplicatedCandidates, query)
	fmt.Printf("   Assembled context: %d tokens, %d chunks\n",
		context.TokenCount, context.ChunkCount)

	// Display results
	fmt.Println("\n📊 SEARCH RESULTS")
	fmt.Println(strings.Repeat("=", 50))

	if len(deduplicatedCandidates) > 0 {
		fmt.Printf("Top %d results:\n", min(5, len(deduplicatedCandidates)))
		for i, candidate := range deduplicatedCandidates[:min(5, len(deduplicatedCandidates))] {
			fmt.Printf("\n%d. %s\n", i+1, candidate.Name)
			fmt.Printf("   Path: %s\n", candidate.Path)
			fmt.Printf("   Match Type: %s\n", candidate.MatchType)
			fmt.Printf("   Score: %.3f\n", candidate.RelevanceScore)
			if !candidate.Modified.IsZero() {
				fmt.Printf("   Modified: %s\n", candidate.Modified.Format("2006-01-02 15:04:05"))
			}
		}
	}

	// Display context preview
	if context.Content != "" {
		fmt.Println("\n📝 CONTEXT PREVIEW")
		fmt.Println(strings.Repeat("-", 30))
		preview := context.Content
		if len(preview) > 500 {
			preview = preview[:500] + "..."
		}
		fmt.Println(preview)
	}

	// Display statistics
	fmt.Println("\n📈 STATISTICS")
	fmt.Println(strings.Repeat("-", 30))
	fmt.Printf("Query Composition: %d expanded tokens\n", len(composedQuery["tokens"].([]string)))
	fmt.Printf("Candidates Found: %d\n", len(candidates))
	fmt.Printf("After Ranking: %d\n", len(rankedCandidates))
	fmt.Printf("After Boosting: %d\n", len(boostedCandidates))
	fmt.Printf("After Deduplication: %d\n", len(deduplicatedCandidates))
	fmt.Printf("Context Tokens: %d (%.1f%%)\n",
		context.TokenCount, context.BudgetUsed)
	fmt.Printf("Sources Used: %d\n", len(context.Sources))

	// Display algorithm stats
	fmt.Println("\n🔧 ALGORITHM STATISTICS")
	fmt.Println(strings.Repeat("-", 30))

	// Query composer stats
	queryStats := queryComposer.GetQueryStats(query)
	fmt.Printf("Query Composer: %d tokens expanded\n", queryStats["token_count"])

	// BM25/TF-IDF stats
	bm25Stats := bm25TFIDF.GetRankingStats(rankedCandidates, query)
	fmt.Printf("BM25/TF-IDF: Avg score %.3f, Max score %.3f\n",
		bm25Stats["avg_score"], bm25Stats["max_score"])

	// Metadata boost stats
	boostStats := metadataBoost.GetBoostStats(boostedCandidates)
	fmt.Printf("Metadata Boost: Avg boost %.3f, Max boost %.3f\n",
		boostStats["avg_boost"], boostStats["max_boost"])

	// Deduplication stats
	dedupStats := deduplicator.GetDeduplicationStats(candidates, deduplicatedCandidates)
	fmt.Printf("Deduplication: %d duplicates removed\n", dedupStats.DuplicatesFound)

	// Context assembler stats
	contextStats := contextAssembler.GetContextStats(context)
	fmt.Printf("Context Assembly: %.1f%% efficiency\n", contextStats["efficiency"])

	fmt.Println("\n✅ Demo completed successfully!")
	fmt.Println("🎯 Advanced search engine algorithms are working!")
}

// Helper function to get minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
