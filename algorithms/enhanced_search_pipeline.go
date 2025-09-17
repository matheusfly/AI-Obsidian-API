package algorithms

import (
	"fmt"
	"sort"
	"strings"
	"time"
)

// EnhancedSearchPipeline integrates all advanced search techniques
type EnhancedSearchPipeline struct {
	// Core components
	autocompleteSuggester *AutocompleteSuggester
	proximityMatcher      *ProximityMatcher
	batchParallelFetcher  *BatchParallelFetcher
	queryRewriter         *QueryRewriter
	localIndexer          *LocalIndexer

	// Existing components
	candidateAggregator *CandidateAggregator
	bm25TFIDF           *BM25TFIDF
	metadataBoost       *MetadataBoost
	deduplicator        *Deduplicator
	contextAssembler    *ContextAssembler

	// Configuration
	config PipelineConfig
	stats  PipelineStats
}

// PipelineConfig holds configuration for the enhanced pipeline
type PipelineConfig struct {
	EnableAutocomplete   bool    `json:"enable_autocomplete"`
	EnableProximity      bool    `json:"enable_proximity"`
	EnableParallelFetch  bool    `json:"enable_parallel_fetch"`
	EnableQueryRewriting bool    `json:"enable_query_rewriting"`
	EnableLocalIndexing  bool    `json:"enable_local_indexing"`
	ProximityThreshold   float64 `json:"proximity_threshold"`
	ProximityBoost       float64 `json:"proximity_boost"`
	BatchSize            int     `json:"batch_size"`
	MaxRetries           int     `json:"max_retries"`
	CacheTTL             int     `json:"cache_ttl_minutes"`
	MaxSuggestions       int     `json:"max_suggestions"`
	MaxResults           int     `json:"max_results"`
}

// PipelineStats tracks pipeline performance statistics
type PipelineStats struct {
	TotalQueries        int           `json:"total_queries"`
	SuccessfulQueries   int           `json:"successful_queries"`
	AverageQueryTime    time.Duration `json:"average_query_time"`
	AverageResultsCount int           `json:"average_results_count"`
	AutocompleteHits    int           `json:"autocomplete_hits"`
	ProximityMatches    int           `json:"proximity_matches"`
	QueryRewrites       int           `json:"query_rewrites"`
	IndexHits           int           `json:"index_hits"`
	ParallelFetchTime   time.Duration `json:"parallel_fetch_time"`
	LastQueryTime       time.Duration `json:"last_query_time"`
}

// EnhancedSearchResult represents an enhanced search result
type EnhancedSearchResult struct {
	File           string                 `json:"file"`
	Score          float64                `json:"score"`
	Snippet        string                 `json:"snippet"`
	Type           string                 `json:"type"`
	Context        string                 `json:"context"`
	Metadata       map[string]interface{} `json:"metadata"`
	ProximityScore float64                `json:"proximity_score"`
	RewrittenQuery string                 `json:"rewritten_query,omitempty"`
	Suggestions    []string               `json:"suggestions,omitempty"`
}

// NewEnhancedSearchPipeline creates a new enhanced search pipeline
func NewEnhancedSearchPipeline(apiKey, baseURL string, config PipelineConfig) *EnhancedSearchPipeline {
	// Initialize components
	autocompleteSuggester := NewAutocompleteSuggester(apiKey, baseURL)
	proximityMatcher := NewProximityMatcher(config.ProximityThreshold, config.ProximityBoost, 10)
	batchParallelFetcher := NewBatchParallelFetcher(apiKey, baseURL, config.BatchSize, config.MaxRetries)
	queryRewriter := NewQueryRewriter("pt") // Portuguese by default
	localIndexer := NewLocalIndexer(apiKey, baseURL, "./cache/local_index.json")

	// Initialize existing components
	candidateAggregator := NewCandidateAggregator(apiKey, baseURL)
	bm25TFIDF := NewBM25TFIDF()
	metadataBoost := NewMetadataBoost()
	deduplicator := NewDeduplicator()
	contextAssembler := NewContextAssembler()

	return &EnhancedSearchPipeline{
		autocompleteSuggester: autocompleteSuggester,
		proximityMatcher:      proximityMatcher,
		batchParallelFetcher:  batchParallelFetcher,
		queryRewriter:         queryRewriter,
		localIndexer:          localIndexer,
		candidateAggregator:   candidateAggregator,
		bm25TFIDF:             bm25TFIDF,
		metadataBoost:         metadataBoost,
		deduplicator:          deduplicator,
		contextAssembler:      contextAssembler,
		config:                config,
		stats:                 PipelineStats{},
	}
}

// Search performs an enhanced search with all optimizations
func (esp *EnhancedSearchPipeline) Search(query string) ([]EnhancedSearchResult, error) {
	startTime := time.Now()

	fmt.Printf("🚀 Enhanced search: '%s'\n", query)

	// Step 1: Get autocomplete suggestions if enabled
	var suggestions []string
	if esp.config.EnableAutocomplete {
		suggestionResults, err := esp.autocompleteSuggester.GetSuggestions(query, esp.config.MaxSuggestions)
		if err == nil && len(suggestionResults) > 0 {
			for _, suggestion := range suggestionResults {
				suggestions = append(suggestions, suggestion.Text)
			}
			esp.stats.AutocompleteHits++
		}
	}

	// Step 2: Rewrite query if enabled
	rewrittenQuery := query
	if esp.config.EnableQueryRewriting {
		rewriteResult := esp.queryRewriter.RewriteQuery(query)
		if rewriteResult.RewrittenQuery != query {
			rewrittenQuery = rewriteResult.RewrittenQuery
			esp.stats.QueryRewrites++
			fmt.Printf("📝 Query rewritten: '%s' -> '%s'\n", query, rewrittenQuery)
		}
	}

	// Step 3: Try local index first if enabled
	var candidates []Candidate
	if esp.config.EnableLocalIndexing {
		indexResults, err := esp.localIndexer.QueryIndex(rewrittenQuery)
		if err == nil && len(indexResults) > 0 {
			// Convert index results to candidates
			candidates = esp.convertIndexResultsToCandidates(indexResults)
			esp.stats.IndexHits++
			fmt.Printf("📚 Found %d results from local index\n", len(candidates))
		}
	}

	// Step 4: If no index results, use traditional aggregation
	if len(candidates) == 0 {
		var err error
		candidates, err = esp.candidateAggregator.AggregateCandidates(rewrittenQuery, esp.config.MaxResults*2)
		if err != nil {
			return nil, fmt.Errorf("failed to aggregate candidates: %w", err)
		}
		fmt.Printf("🔍 Found %d candidates from aggregation\n", len(candidates))
	}

	// Step 5: Parallel fetch content if enabled
	if esp.config.EnableParallelFetch && len(candidates) > 0 {
		paths := make([]string, len(candidates))
		for i, candidate := range candidates {
			paths[i] = candidate.Path
		}

		fetchStart := time.Now()
		fetchResults, err := esp.batchParallelFetcher.FetchFilesWithProgress(paths, func(completed, total int) {
			fmt.Printf("📥 Fetching content: %d/%d\n", completed, total)
		})
		if err == nil {
			// Update candidates with fetched content
			for i, candidate := range candidates {
				if result, exists := fetchResults[candidate.Path]; exists && result.Success {
					candidate.Content = result.Content
					candidates[i] = candidate
				}
			}
			esp.stats.ParallelFetchTime = time.Since(fetchStart)
		}
	}

	// Step 6: Apply BM25 ranking
	rankedCandidates := esp.bm25TFIDF.RankCandidates(candidates, rewrittenQuery)

	// Step 7: Apply proximity boosting if enabled
	if esp.config.EnableProximity {
		boostedCandidates := esp.proximityMatcher.BoostCandidates(rankedCandidates, rewrittenQuery)
		rankedCandidates = boostedCandidates
		esp.stats.ProximityMatches++
	}

	// Step 8: Apply metadata boosting
	boostedCandidates := esp.metadataBoost.BoostCandidates(rankedCandidates, rewrittenQuery)

	// Step 9: Deduplicate results
	uniqueCandidates := esp.deduplicator.DeduplicateCandidates(boostedCandidates)

	// Step 10: Convert to search results
	results := esp.convertCandidatesToResults(uniqueCandidates, rewrittenQuery, suggestions)

	// Step 11: Sort by score
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	// Step 12: Limit results
	if len(results) > esp.config.MaxResults {
		results = results[:esp.config.MaxResults]
	}

	// Update statistics
	esp.updateStats(time.Since(startTime), len(results))

	fmt.Printf("⚡ Enhanced search completed in %v | Found %d results\n", time.Since(startTime), len(results))

	return results, nil
}

// convertIndexResultsToCandidates converts index results to candidates
func (esp *EnhancedSearchPipeline) convertIndexResultsToCandidates(indexResults []IndexEntry) []Candidate {
	var candidates []Candidate

	for _, entry := range indexResults {
		candidate := Candidate{
			FileInfo: FileInfo{
				Path:    entry.Path,
				Content: "", // Will be fetched later
				Metadata: map[string]interface{}{
					"title":    entry.Title,
					"tags":     entry.Tags,
					"modified": entry.Modified,
					"size":     entry.Size,
				},
			},
			MatchScore: 1.0, // Default score
		}
		candidates = append(candidates, candidate)
	}

	return candidates
}

// convertCandidatesToResults converts candidates to search results
func (esp *EnhancedSearchPipeline) convertCandidatesToResults(candidates []Candidate, query string, suggestions []string) []EnhancedSearchResult {
	var results []EnhancedSearchResult

	for _, candidate := range candidates {
		// Extract snippet
		snippet := esp.extractSnippet(candidate.Content, query)

		// Determine result type
		resultType := "content"
		if strings.Contains(strings.ToLower(candidate.Path), strings.ToLower(query)) {
			resultType = "filename"
		}

		// Get proximity score from metadata
		proximityScore := 0.0
		if score, exists := candidate.Metadata["proximity_score"]; exists {
			if s, ok := score.(float64); ok {
				proximityScore = s
			}
		}

		result := EnhancedSearchResult{
			File:           candidate.Path,
			Score:          candidate.MatchScore,
			Snippet:        snippet,
			Type:           resultType,
			Context:        "Enhanced search result",
			Metadata:       candidate.Metadata,
			ProximityScore: proximityScore,
			Suggestions:    suggestions,
		}

		results = append(results, result)
	}

	return results
}

// extractSnippet extracts a relevant snippet from content
func (esp *EnhancedSearchPipeline) extractSnippet(content, query string) string {
	if content == "" {
		return "📄 Content match"
	}

	contentLower := strings.ToLower(content)
	queryLower := strings.ToLower(query)

	// Find first occurrence of query
	index := strings.Index(contentLower, queryLower)
	if index == -1 {
		return "📄 Content match"
	}

	// Extract snippet around the match
	start := index - 100
	if start < 0 {
		start = 0
	}

	end := index + len(query) + 100
	if end > len(content) {
		end = len(content)
	}

	snippet := content[start:end]
	highlighted := strings.Replace(snippet, query, "🔍"+query+"🔍", -1)

	return fmt.Sprintf("📄 ...%s...", highlighted)
}

// updateStats updates the pipeline statistics
func (esp *EnhancedSearchPipeline) updateStats(queryTime time.Duration, resultCount int) {
	esp.stats.TotalQueries++
	esp.stats.SuccessfulQueries++
	esp.stats.LastQueryTime = queryTime

	// Update average query time
	totalTime := esp.stats.AverageQueryTime * time.Duration(esp.stats.TotalQueries-1)
	esp.stats.AverageQueryTime = (totalTime + queryTime) / time.Duration(esp.stats.TotalQueries)

	// Update average results count
	totalResults := esp.stats.AverageResultsCount * (esp.stats.TotalQueries - 1)
	esp.stats.AverageResultsCount = (totalResults + resultCount) / esp.stats.TotalQueries
}

// GetSuggestions gets autocomplete suggestions for a query
func (esp *EnhancedSearchPipeline) GetSuggestions(query string) ([]string, error) {
	if !esp.config.EnableAutocomplete {
		return []string{}, nil
	}

	suggestions, err := esp.autocompleteSuggester.GetSuggestions(query, esp.config.MaxSuggestions)
	if err != nil {
		return []string{}, err
	}

	var result []string
	for _, suggestion := range suggestions {
		result = append(result, suggestion.Text)
	}

	return result, nil
}

// GetStats returns the current pipeline statistics
func (esp *EnhancedSearchPipeline) GetStats() PipelineStats {
	return esp.stats
}

// GetComponentStats returns statistics from all components
func (esp *EnhancedSearchPipeline) GetComponentStats() map[string]interface{} {
	return map[string]interface{}{
		"autocomplete":   esp.autocompleteSuggester.GetStats(),
		"proximity":      esp.proximityMatcher.GetStats(),
		"parallel_fetch": esp.batchParallelFetcher.GetStats(),
		"query_rewriter": esp.queryRewriter.GetStats(),
		"local_indexer":  esp.localIndexer.GetStats(),
		"pipeline":       esp.stats,
	}
}

// SetConfig updates the pipeline configuration
func (esp *EnhancedSearchPipeline) SetConfig(config PipelineConfig) {
	esp.config = config

	// Update component configurations
	esp.proximityMatcher.threshold = config.ProximityThreshold
	esp.proximityMatcher.proximityBoost = config.ProximityBoost
	esp.batchParallelFetcher.SetBatchSize(config.BatchSize)
	esp.batchParallelFetcher.SetMaxRetries(config.MaxRetries)
	esp.localIndexer.SetCacheTTL(time.Duration(config.CacheTTL) * time.Minute)
}

// ClearCache clears all caches
func (esp *EnhancedSearchPipeline) ClearCache() {
	esp.autocompleteSuggester.ClearCache()
	esp.localIndexer.ClearIndex()
	esp.batchParallelFetcher.ResetStats()
	esp.queryRewriter.ResetStats()
}
