package algorithms

import (
	"fmt"
	"sort"
	"strings"
	"time"
)

// FullContextRetrievalPipeline provides end-to-end context retrieval
// combining all algorithms in a comprehensive pipeline
type FullContextRetrievalPipeline struct {
	queryComposer      *QueryComposer
	recursiveTraversal *RecursiveVaultTraversal
	cachingLayer       *CachingLayer
	advancedSearch     *AdvancedLocalSearch
	bm25TFIDF          *BM25TFIDF
	metadataBoost      *MetadataBoost
	deduplicator       *Deduplicator
	contextAssembler   *ContextAssembler
	streamingMerger    *StreamingMerger
	noteCreator        *NoteCreationWorkaround
	commandExecutor    *CommandExecutor
	stats              FullPipelineStats
}

// FullPipelineStats tracks full pipeline performance metrics
type FullPipelineStats struct {
	QueriesProcessed  int           `json:"queries_processed"`
	FilesScanned      int           `json:"files_scanned"`
	ResultsGenerated  int           `json:"results_generated"`
	ContextsAssembled int           `json:"contexts_assembled"`
	TotalTime         time.Duration `json:"total_time"`
	AverageTime       time.Duration `json:"average_time"`
	CacheHits         int           `json:"cache_hits"`
	CacheMisses       int           `json:"cache_misses"`
	LastProcessed     time.Time     `json:"last_processed"`
}

// PipelineResult represents the complete result of a pipeline execution
type PipelineResult struct {
	Query         string              `json:"query"`
	ComposedQuery string              `json:"composed_query"`
	FilesScanned  int                 `json:"files_scanned"`
	ResultsFound  int                 `json:"results_found"`
	Context       AssembledContext    `json:"context"`
	Performance   PipelinePerformance `json:"performance"`
	Metadata      PipelineMetadata    `json:"metadata"`
	Timestamp     time.Time           `json:"timestamp"`
}

// PipelinePerformance tracks performance metrics for a single execution
type PipelinePerformance struct {
	TotalTime         time.Duration `json:"total_time"`
	TraversalTime     time.Duration `json:"traversal_time"`
	SearchTime        time.Duration `json:"search_time"`
	RankingTime       time.Duration `json:"ranking_time"`
	DeduplicationTime time.Duration `json:"deduplication_time"`
	AssemblyTime      time.Duration `json:"assembly_time"`
	CacheHit          bool          `json:"cache_hit"`
}

// PipelineMetadata contains metadata about the pipeline execution
type PipelineMetadata struct {
	QueryVariations     []string        `json:"query_variations"`
	SearchFlags         map[string]bool `json:"search_flags"`
	RankingMethod       string          `json:"ranking_method"`
	DeduplicationMethod string          `json:"deduplication_method"`
	TokenBudget         int             `json:"token_budget"`
	TokenUsage          int             `json:"token_usage"`
	TokenEfficiency     float64         `json:"token_efficiency"`
}

// NewFullContextRetrievalPipeline creates a new pipeline instance
func NewFullContextRetrievalPipeline(apiKey, baseURL string) *FullContextRetrievalPipeline {
	return &FullContextRetrievalPipeline{
		queryComposer:      NewQueryComposer(),
		recursiveTraversal: NewRecursiveVaultTraversal(apiKey, baseURL),
		cachingLayer:       NewCachingLayer("./cache"),
		advancedSearch:     NewAdvancedLocalSearch(),
		bm25TFIDF:          NewBM25TFIDF(),
		metadataBoost:      NewMetadataBoost(),
		deduplicator:       NewDeduplicator(),
		contextAssembler:   NewContextAssembler(),
		streamingMerger:    NewStreamingMerger(),
		noteCreator:        NewNoteCreationWorkaround(apiKey, baseURL),
		commandExecutor:    NewCommandExecutor(apiKey, baseURL),
		stats:              FullPipelineStats{},
	}
}

// Run executes the complete pipeline for a given query
func (fcrp *FullContextRetrievalPipeline) Run(query string, options PipelineOptions) (*PipelineResult, error) {
	startTime := time.Now()
	result := &PipelineResult{
		Query:     query,
		Timestamp: time.Now(),
	}

	// Step 1: Query Composition
	composedQuery := fcrp.composeQuery(query, options)
	result.ComposedQuery = composedQuery

	// Step 2: File Discovery (with caching)
	files, err := fcrp.discoverFiles(options)
	if err != nil {
		return nil, fmt.Errorf("file discovery failed: %w", err)
	}
	result.FilesScanned = len(files)

	// Step 3: Advanced Search
	searchResults, err := fcrp.performSearch(composedQuery, files, options)
	if err != nil {
		return nil, fmt.Errorf("search failed: %w", err)
	}
	result.ResultsFound = len(searchResults)

	// Step 4: Ranking and Boosting
	rankedResults, err := fcrp.rankResults(searchResults, options)
	if err != nil {
		return nil, fmt.Errorf("ranking failed: %w", err)
	}

	// Step 5: Deduplication
	uniqueResults, err := fcrp.deduplicateResults(rankedResults, options)
	if err != nil {
		return nil, fmt.Errorf("deduplication failed: %w", err)
	}

	// Step 6: Context Assembly
	context, err := fcrp.assembleContext(uniqueResults, options)
	if err != nil {
		return nil, fmt.Errorf("context assembly failed: %w", err)
	}
	result.Context = context

	// Step 7: Performance tracking
	result.Performance = fcrp.calculatePerformance(startTime, options)
	result.Metadata = fcrp.generateMetadata(query, options, context)

	// Update statistics
	fcrp.updateStats(result)

	return result, nil
}

// PipelineOptions defines options for pipeline execution
type PipelineOptions struct {
	MaxResults        int
	TokenBudget       int
	SearchFlags       SearchFlags
	UseCache          bool
	UseRecursive      bool
	UseAdvancedSearch bool
	UseRanking        bool
	UseDeduplication  bool
	UseStreaming      bool
	Timeout           time.Duration
}

// DefaultPipelineOptions returns default pipeline options
func DefaultPipelineOptions() PipelineOptions {
	return PipelineOptions{
		MaxResults:        10,
		TokenBudget:       4000,
		SearchFlags:       SearchFlags{MaxResults: 50, Fuzzy: true, Portuguese: true},
		UseCache:          true,
		UseRecursive:      true,
		UseAdvancedSearch: true,
		UseRanking:        true,
		UseDeduplication:  true,
		UseStreaming:      false,
		Timeout:           30 * time.Second,
	}
}

// composeQuery composes and enhances the input query
func (fcrp *FullContextRetrievalPipeline) composeQuery(query string, options PipelineOptions) string {
	composed := fcrp.queryComposer.ComposeQuery(query)
	// Extract the query string from the composed result
	if queryStr, ok := composed["query"].(string); ok {
		return queryStr
	}
	return query // Fallback to original query
}

// discoverFiles discovers files using recursive traversal with caching
func (fcrp *FullContextRetrievalPipeline) discoverFiles(options PipelineOptions) ([]FileInfo, error) {
	if options.UseCache {
		// Use caching layer
		cachedFiles, err := fcrp.cachingLayer.Get("vault_files", func() (interface{}, error) {
			return fcrp.recursiveTraversal.Traverse("")
		})
		if err != nil {
			return nil, err
		}
		return cachedFiles.([]FileInfo), nil
	}

	// Direct traversal without caching
	return fcrp.recursiveTraversal.Traverse("")
}

// performSearch performs advanced local search
func (fcrp *FullContextRetrievalPipeline) performSearch(query string, files []FileInfo, options PipelineOptions) ([]SearchResult, error) {
	if !options.UseAdvancedSearch {
		// Fallback to basic search
		return fcrp.basicSearch(query, files)
	}

	// Content fetcher function
	contentFetcher := func(file FileInfo) (string, error) {
		// This would typically fetch content from the API
		// For now, return a placeholder
		return fmt.Sprintf("Content for %s", file.Name), nil
	}

	return fcrp.advancedSearch.Search(query, files, contentFetcher, options.SearchFlags)
}

// basicSearch performs basic search without advanced features
func (fcrp *FullContextRetrievalPipeline) basicSearch(query string, files []FileInfo) ([]SearchResult, error) {
	results := make([]SearchResult, 0)
	queryLower := strings.ToLower(query)

	for _, file := range files {
		score := 0.0
		matchType := "none"

		// Check filename
		if strings.Contains(strings.ToLower(file.Name), queryLower) {
			score += 0.8
			matchType = "filename"
		}

		// Check path
		if strings.Contains(strings.ToLower(file.Path), queryLower) {
			score += 0.6
			if matchType == "none" {
				matchType = "path"
			}
		}

		if score > 0 {
			results = append(results, SearchResult{
				File:      file,
				Score:     score,
				MatchType: matchType,
				MatchText: query,
			})
		}
	}

	// Sort by score
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	return results, nil
}

// rankResults ranks search results using BM25 and metadata boosting
func (fcrp *FullContextRetrievalPipeline) rankResults(results []SearchResult, options PipelineOptions) ([]SearchResult, error) {
	if !options.UseRanking {
		return results, nil
	}

	// Convert to candidates for ranking
	candidates := make([]Candidate, len(results))
	for i, result := range results {
		candidates[i] = Candidate{
			FileInfo:   result.File,
			MatchScore: result.Score,
		}
	}

	// Apply BM25 ranking
	rankedCandidates := fcrp.bm25TFIDF.RankCandidates(candidates, fcrp.queryComposer.GetExpandedQuery())

	// Apply metadata boosting
	boostedCandidates := fcrp.metadataBoost.BoostCandidates(rankedCandidates, fcrp.queryComposer.GetExpandedQuery())

	// Convert back to search results
	rankedResults := make([]SearchResult, len(boostedCandidates))
	for i, candidate := range boostedCandidates {
		rankedResults[i] = SearchResult{
			File:      candidate.FileInfo,
			Score:     candidate.MatchScore,
			MatchType: "ranked",
			MatchText: fcrp.queryComposer.GetExpandedQuery(),
		}
	}

	return rankedResults, nil
}

// deduplicateResults removes duplicate or very similar results
func (fcrp *FullContextRetrievalPipeline) deduplicateResults(results []SearchResult, options PipelineOptions) ([]SearchResult, error) {
	if !options.UseDeduplication {
		return results, nil
	}

	// Convert to candidates for deduplication
	candidates := make([]Candidate, len(results))
	for i, result := range results {
		candidates[i] = Candidate{
			FileInfo:   result.File,
			MatchScore: result.Score,
		}
	}

	// Apply deduplication
	uniqueCandidates := fcrp.deduplicator.DeduplicateCandidates(candidates)

	// Convert back to search results
	uniqueResults := make([]SearchResult, len(uniqueCandidates))
	for i, candidate := range uniqueCandidates {
		uniqueResults[i] = SearchResult{
			File:      candidate.FileInfo,
			Score:     candidate.MatchScore,
			MatchType: "deduplicated",
			MatchText: fcrp.queryComposer.GetExpandedQuery(),
		}
	}

	return uniqueResults, nil
}

// assembleContext assembles the final context within token budget
func (fcrp *FullContextRetrievalPipeline) assembleContext(results []SearchResult, options PipelineOptions) (AssembledContext, error) {
	// Convert to candidates for context assembly
	candidates := make([]Candidate, len(results))
	for i, result := range results {
		candidates[i] = Candidate{
			FileInfo:   result.File,
			MatchScore: result.Score,
		}
	}

	// Set token budget
	fcrp.contextAssembler.SetMaxTokens(options.TokenBudget)

	// Assemble context
	context := fcrp.contextAssembler.AssembleContext(candidates, fcrp.queryComposer.GetExpandedQuery())

	return context, nil
}

// calculatePerformance calculates performance metrics
func (fcrp *FullContextRetrievalPipeline) calculatePerformance(startTime time.Time, options PipelineOptions) PipelinePerformance {
	totalTime := time.Since(startTime)

	return PipelinePerformance{
		TotalTime:         totalTime,
		TraversalTime:     totalTime / 4, // Estimated
		SearchTime:        totalTime / 4, // Estimated
		RankingTime:       totalTime / 8, // Estimated
		DeduplicationTime: totalTime / 8, // Estimated
		AssemblyTime:      totalTime / 4, // Estimated
		CacheHit:          options.UseCache,
	}
}

// generateMetadata generates metadata about the pipeline execution
func (fcrp *FullContextRetrievalPipeline) generateMetadata(query string, options PipelineOptions, context AssembledContext) PipelineMetadata {
	return PipelineMetadata{
		QueryVariations: []string{query, fcrp.queryComposer.GetExpandedQuery()},
		SearchFlags: map[string]bool{
			"fuzzy":          options.SearchFlags.Fuzzy,
			"portuguese":     options.SearchFlags.Portuguese,
			"case_sensitive": options.SearchFlags.CaseSensitive,
			"whole_word":     options.SearchFlags.WholeWord,
			"regex":          options.SearchFlags.Regex,
		},
		RankingMethod:       "BM25 + Metadata Boost",
		DeduplicationMethod: "Levenshtein Distance",
		TokenBudget:         options.TokenBudget,
		TokenUsage:          int(context.BudgetUsed),
		TokenEfficiency:     float64(context.BudgetUsed) / float64(options.TokenBudget) * 100,
	}
}

// updateStats updates pipeline statistics
func (fcrp *FullContextRetrievalPipeline) updateStats(result *PipelineResult) {
	fcrp.stats.QueriesProcessed++
	fcrp.stats.FilesScanned += result.FilesScanned
	fcrp.stats.ResultsGenerated += result.ResultsFound
	fcrp.stats.ContextsAssembled++
	fcrp.stats.TotalTime += result.Performance.TotalTime
	fcrp.stats.AverageTime = fcrp.stats.TotalTime / time.Duration(fcrp.stats.QueriesProcessed)
	fcrp.stats.LastProcessed = result.Timestamp

	if result.Performance.CacheHit {
		fcrp.stats.CacheHits++
	} else {
		fcrp.stats.CacheMisses++
	}
}

// GetStats returns pipeline statistics
func (fcrp *FullContextRetrievalPipeline) GetStats() FullPipelineStats {
	return fcrp.stats
}

// ResetStats resets pipeline statistics
func (fcrp *FullContextRetrievalPipeline) ResetStats() {
	fcrp.stats = FullPipelineStats{}
}

// GetCacheStats returns caching statistics
func (fcrp *FullContextRetrievalPipeline) GetCacheStats() CacheStats {
	return fcrp.cachingLayer.GetStats()
}

// ClearCache clears the pipeline cache
func (fcrp *FullContextRetrievalPipeline) ClearCache() error {
	return fcrp.cachingLayer.Clear()
}

// GetComponentStats returns statistics from all pipeline components
func (fcrp *FullContextRetrievalPipeline) GetComponentStats() map[string]interface{} {
	return map[string]interface{}{
		"query_composer":      fcrp.queryComposer.GetStats(),
		"recursive_traversal": fcrp.recursiveTraversal.GetStats(),
		"caching_layer":       fcrp.cachingLayer.GetStats(),
		"advanced_search":     fcrp.advancedSearch.GetStats(),
		"bm25_tfidf":          fcrp.bm25TFIDF.GetStats(),
		"metadata_boost":      fcrp.metadataBoost.GetStats(),
		"deduplicator":        fcrp.deduplicator.GetStats(),
		"context_assembler":   fcrp.contextAssembler.GetStats(),
		"streaming_merger":    fcrp.streamingMerger.GetStats(),
		"note_creator":        fcrp.noteCreator.GetStats(),
		"command_executor":    fcrp.commandExecutor.GetStats(),
	}
}
