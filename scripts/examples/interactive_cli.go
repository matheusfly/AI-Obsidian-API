package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

// InteractiveCLI represents the interactive command-line interface
type InteractiveCLI struct {
	httpClient          *client.HTTPClient
	queryComposer       *algorithms.QueryComposer
	candidateAggregator *algorithms.CandidateAggregator
	bm25TFIDF           *algorithms.BM25TFIDF
	metadataBoost       *algorithms.MetadataBoost
	deduplicator        *algorithms.Deduplicator
	contextAssembler    *algorithms.ContextAssembler
	streamingMerger     *algorithms.StreamingMerger
	searchCount         int
	totalSearchTime     time.Duration
}

// NewInteractiveCLI creates a new interactive CLI instance
func NewInteractiveCLI(apiKey, baseURL string) *InteractiveCLI {
	cli := &InteractiveCLI{}

	// Initialize all components
	cli.httpClient = client.NewHTTPClient(apiKey, baseURL)
	cli.queryComposer = algorithms.NewQueryComposer()
	cli.candidateAggregator = algorithms.NewCandidateAggregatorWithClient(apiKey, baseURL, cli.httpClient.GetClient())
	cli.bm25TFIDF = algorithms.NewBM25TFIDF()
	cli.metadataBoost = algorithms.NewMetadataBoost()
	cli.deduplicator = algorithms.NewDeduplicator()
	cli.contextAssembler = algorithms.NewContextAssembler()
	cli.streamingMerger = algorithms.NewStreamingMerger()

	// Configure components
	cli.configureDefaults()

	return cli
}

// configureDefaults sets up default configuration
func (cli *InteractiveCLI) configureDefaults() {
	cli.candidateAggregator.SetLimit(1000)
	cli.metadataBoost.AddPathPattern("docs/", 1.5)
	cli.metadataBoost.AddTagBoost("important", 2.0)
	cli.deduplicator.SetSimilarityThreshold(0.9)
	cli.deduplicator.SetCanonicalStrategy("freshest")
	cli.contextAssembler.SetMaxTokens(4000)
	cli.contextAssembler.SetChunkSize(500)
	cli.streamingMerger.SetBufferSize(1024)
	cli.streamingMerger.SetDelimiter("\n")
	cli.streamingMerger.SetTimeout(30 * time.Second)
	cli.streamingMerger.OptimizeStreaming("default")
}

// Run starts the interactive CLI
func (cli *InteractiveCLI) Run() {
	cli.showWelcome()

	// Health check
	if !cli.performHealthCheck() {
		return
	}

	// Main menu loop
	for {
		cli.showMainMenu()
		choice := cli.getUserChoice()

		switch choice {
		case 1:
			cli.performSearch()
		case 2:
			cli.browseAllFiles()
		case 3:
			cli.showSearchStatistics()
		case 4:
			cli.showHelp()
		case 5:
			cli.showExitMessage()
			return
		default:
			fmt.Println("❌ Invalid choice. Please try again.")
		}

		fmt.Println("\nPress Enter to continue...")
		cli.waitForEnter()
	}
}

// showWelcome displays the welcome message
func (cli *InteractiveCLI) showWelcome() {
	fmt.Println("🚀 API-MCP-SIMBIOSIS INTERACTIVE SEARCH ENGINE")
	fmt.Println("==============================================")
	fmt.Println("Advanced search engine for Obsidian vaults")
	fmt.Println("Powered by 7 sophisticated algorithms")
	fmt.Println("")
}

// performHealthCheck checks API connectivity
func (cli *InteractiveCLI) performHealthCheck() bool {
	fmt.Println("🔍 Checking API connectivity...")

	health, err := cli.httpClient.HealthCheck()
	if err != nil {
		fmt.Printf("❌ API connection failed: %v\n", err)
		fmt.Println("Please check your API configuration and try again.")
		return false
	}

	fmt.Printf("✅ API Status: %s (%.3fs)\n", health.Status, health.ResponseTime.Seconds())
	fmt.Println("✅ Ready to search!")
	return true
}

// showMainMenu displays the main menu
func (cli *InteractiveCLI) showMainMenu() {
	fmt.Println("\n" + strings.Repeat("=", 50))
	fmt.Println("📋 MAIN MENU")
	fmt.Println(strings.Repeat("=", 50))
	fmt.Println("1. 🔍 Search Query")
	fmt.Println("2. 📁 Browse All Files")
	fmt.Println("3. 📊 Search Statistics")
	fmt.Println("4. ❓ Help")
	fmt.Println("5. 🚪 Exit")
	fmt.Println(strings.Repeat("=", 50))
}

// getUserChoice gets user input for menu choice
func (cli *InteractiveCLI) getUserChoice() int {
	fmt.Print("Enter your choice (1-5): ")

	scanner := bufio.NewScanner(os.Stdin)
	if !scanner.Scan() {
		return 0
	}

	choice, err := strconv.Atoi(strings.TrimSpace(scanner.Text()))
	if err != nil {
		return 0
	}

	return choice
}

// performSearch handles the search functionality
func (cli *InteractiveCLI) performSearch() {
	fmt.Println("\n🔍 SEARCH QUERY")
	fmt.Println(strings.Repeat("-", 30))

	fmt.Print("Enter your search query: ")
	scanner := bufio.NewScanner(os.Stdin)
	if !scanner.Scan() {
		fmt.Println("❌ Failed to read input")
		return
	}

	query := strings.TrimSpace(scanner.Text())
	if query == "" {
		fmt.Println("❌ Query cannot be empty")
		return
	}

	// Get search limit
	fmt.Print("Maximum results (default 20): ")
	if !scanner.Scan() {
		fmt.Println("❌ Failed to read input")
		return
	}

	limitStr := strings.TrimSpace(scanner.Text())
	limit := 20
	if limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 {
			limit = l
		}
	}

	// Perform search
	cli.executeSearch(query, limit)
}

// executeSearch runs the complete search pipeline
func (cli *InteractiveCLI) executeSearch(query string, limit int) {
	fmt.Printf("\n🔍 Searching for: '%s'\n", query)
	fmt.Println("⏳ Processing...")

	startTime := time.Now()

	// Step 1: Query composition
	composedQuery := cli.queryComposer.ComposeQuery(query)
	fmt.Printf("📝 Step 1: Query composition - %v\n", composedQuery["tokens"])

	// Step 2: Candidate aggregation
	candidates, err := cli.candidateAggregator.AggregateCandidates(query, limit)
	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}
	fmt.Printf("📄 Step 2: Candidate aggregation - %d candidates\n", len(candidates))

	if len(candidates) == 0 {
		fmt.Println("❌ No results found")
		return
	}

	// Step 3: BM25-TFIDF ranking
	rankedCandidates := cli.bm25TFIDF.RankCandidates(candidates, query)
	fmt.Printf("📊 Step 3: BM25-TFIDF ranking - %d candidates\n", len(rankedCandidates))

	// Step 4: Metadata boost
	boostedCandidates := cli.metadataBoost.BoostCandidates(rankedCandidates, query)
	fmt.Printf("⚡ Step 4: Metadata boost - %d candidates\n", len(boostedCandidates))

	// Step 5: Deduplication
	deduplicatedCandidates := cli.deduplicator.DeduplicateCandidates(boostedCandidates)
	fmt.Printf("🔄 Step 5: Deduplication - %d candidates\n", len(deduplicatedCandidates))

	// Step 6: Context assembly
	context := cli.contextAssembler.AssembleContext(deduplicatedCandidates, query)
	fmt.Printf("📚 Step 6: Context assembly - %d tokens (%.1f%% budget)\n",
		context.TokenCount, context.BudgetUsed)

	duration := time.Since(startTime)
	fmt.Printf("\n🎉 Search completed in %.3fs\n", duration.Seconds())

	// Update statistics
	cli.searchCount++
	cli.totalSearchTime += duration

	// Show results
	cli.displaySearchResults(deduplicatedCandidates, context)
}

// displaySearchResults shows the search results
func (cli *InteractiveCLI) displaySearchResults(candidates []algorithms.Candidate, context algorithms.AssembledContext) {
	fmt.Println("\n🏆 SEARCH RESULTS:")
	fmt.Println(strings.Repeat("-", 50))

	for i, candidate := range candidates {
		if i >= 20 { // Limit display to 20 results
			fmt.Printf("... and %d more results\n", len(candidates)-20)
			break
		}

		fmt.Printf("%2d. %s (Score: %.3f, Type: %s)\n",
			i+1, candidate.Name, candidate.MatchScore, candidate.MatchType)

		// Show content preview for content matches
		if candidate.MatchType == "content" && len(candidate.Content) > 0 {
			preview := candidate.Content
			if len(preview) > 100 {
				preview = preview[:100] + "..."
			}
			fmt.Printf("    📄 %s\n", preview)
		}
	}

	// Show context preview
	if len(context.Content) > 0 {
		fmt.Println("\n📄 CONTEXT PREVIEW:")
		fmt.Println(strings.Repeat("-", 30))
		preview := context.Content
		if len(preview) > 500 {
			preview = preview[:500] + "..."
		}
		fmt.Println(preview)
	}
}

// browseAllFiles shows all files in the vault
func (cli *InteractiveCLI) browseAllFiles() {
	fmt.Println("\n📁 BROWSING ALL FILES")
	fmt.Println(strings.Repeat("-", 30))

	fmt.Println("⏳ Loading vault files...")
	startTime := time.Now()

	candidates, err := cli.candidateAggregator.AggregateCandidates("", 100)
	if err != nil {
		fmt.Printf("❌ Failed to load files: %v\n", err)
		return
	}

	duration := time.Since(startTime)
	fmt.Printf("✅ Loaded %d files in %.3fs\n", len(candidates), duration.Seconds())

	// Show files in groups
	pageSize := 20
	totalPages := (len(candidates) + pageSize - 1) / pageSize

	for page := 0; page < totalPages; page++ {
		start := page * pageSize
		end := start + pageSize
		if end > len(candidates) {
			end = len(candidates)
		}

		fmt.Printf("\n📄 Files %d-%d of %d:\n", start+1, end, len(candidates))
		for i := start; i < end; i++ {
			candidate := candidates[i]
			fmt.Printf("   %3d. %s\n", i+1, candidate.Name)
		}

		if page < totalPages-1 {
			fmt.Print("\nPress Enter for next page (or 'q' to quit): ")
			scanner := bufio.NewScanner(os.Stdin)
			if !scanner.Scan() {
				break
			}
			if strings.TrimSpace(scanner.Text()) == "q" {
				break
			}
		}
	}
}

// showSearchStatistics displays search statistics
func (cli *InteractiveCLI) showSearchStatistics() {
	fmt.Println("\n📊 SEARCH STATISTICS")
	fmt.Println(strings.Repeat("-", 30))

	fmt.Printf("Total searches performed: %d\n", cli.searchCount)

	if cli.searchCount > 0 {
		avgTime := cli.totalSearchTime / time.Duration(cli.searchCount)
		fmt.Printf("Average search time: %.3fs\n", avgTime.Seconds())
		fmt.Printf("Total search time: %.3fs\n", cli.totalSearchTime.Seconds())
	}

	// HTTP Client Statistics
	fmt.Println("\n🌐 HTTP Client Statistics:")
	stats := cli.httpClient.GetStats()
	fmt.Printf("Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	// Vault Statistics
	fmt.Println("\n📁 Vault Statistics:")
	vaultStats, err := cli.candidateAggregator.GetVaultStats()
	if err != nil {
		fmt.Printf("❌ Failed to get vault stats: %v\n", err)
	} else {
		fmt.Printf("Total files: %v\n", vaultStats["total_files"])
		fmt.Printf("Total size: %v bytes\n", vaultStats["total_size"])
		fmt.Printf("File types: %v\n", vaultStats["file_types"])
	}
}

// showHelp displays help information
func (cli *InteractiveCLI) showHelp() {
	fmt.Println("\n❓ HELP & USAGE")
	fmt.Println(strings.Repeat("-", 30))

	fmt.Println("🔍 SEARCH QUERY:")
	fmt.Println("  • Enter any search term or phrase")
	fmt.Println("  • Supports partial matches and variations")
	fmt.Println("  • Searches filenames, paths, and content")
	fmt.Println("  • Results are ranked by relevance")

	fmt.Println("\n📁 BROWSE ALL FILES:")
	fmt.Println("  • Shows all files in your vault")
	fmt.Println("  • Paginated display for large vaults")
	fmt.Println("  • Navigate with Enter or 'q' to quit")

	fmt.Println("\n📊 SEARCH STATISTICS:")
	fmt.Println("  • View search performance metrics")
	fmt.Println("  • HTTP client status")
	fmt.Println("  • Vault information")

	fmt.Println("\n💡 TIPS:")
	fmt.Println("  • Use specific terms for better results")
	fmt.Println("  • Try different variations of your query")
	fmt.Println("  • Check file types in statistics")
	fmt.Println("  • Use 'q' to quit browsing")
}

// showExitMessage displays the exit message
func (cli *InteractiveCLI) showExitMessage() {
	fmt.Println("\n🎉 THANK YOU FOR USING API-MCP-SIMBIOSIS!")
	fmt.Println("==========================================")
	fmt.Printf("Total searches performed: %d\n", cli.searchCount)
	if cli.searchCount > 0 {
		avgTime := cli.totalSearchTime / time.Duration(cli.searchCount)
		fmt.Printf("Average search time: %.3fs\n", avgTime.Seconds())
	}
	fmt.Println("✅ Search engine powered by 7 advanced algorithms")
	fmt.Println("🚀 Happy searching!")
}

// waitForEnter waits for user to press Enter
func (cli *InteractiveCLI) waitForEnter() {
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
}

// main function
func main() {
	// Configuration - these should be set via environment variables or config file
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Create and run the interactive CLI
	cli := NewInteractiveCLI(apiKey, baseURL)
	cli.Run()
}
