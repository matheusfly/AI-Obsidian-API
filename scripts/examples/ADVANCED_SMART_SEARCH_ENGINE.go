package main

import (
	"fmt"
	"math"
	"net/http"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"
)

// AdvancedSmartSearchEngine provides intelligent search capabilities
type AdvancedSmartSearchEngine struct {
	apiPipeline    *APIPipeline
	ollamaHost     string
	ollamaModel    string
	client         *http.Client
	cache          *SearchCache
	indexer        *ContentIndexer
	analyzer       *ContentAnalyzer
	ranker         *SearchRanker
	semanticEngine *SemanticSearchEngine
	mutex          sync.RWMutex
}

// SearchCache provides intelligent caching for search results
type SearchCache struct {
	results    map[string]*CachedSearchResult
	embeddings map[string][]float64
	ttl        time.Duration
	maxSize    int
	mutex      sync.RWMutex
}

// CachedSearchResult represents a cached search result
type CachedSearchResult struct {
	Results   []SearchResult
	Timestamp time.Time
	TTL       time.Duration
	QueryHash string
}

// ContentIndexer indexes vault content for fast searching
type ContentIndexer struct {
	index     map[string]*IndexedContent
	fileIndex map[string][]string
	wordIndex map[string][]string
	mutex     sync.RWMutex
}

// IndexedContent represents indexed content
type IndexedContent struct {
	File      string
	Content   string
	Words     []string
	Tags      []string
	Links     []string
	Headers   []string
	Metadata  map[string]interface{}
	Timestamp time.Time
}

// ContentAnalyzer analyzes content for better search
type ContentAnalyzer struct {
	stopWords map[string]bool
	stemmer   *Stemmer
}

// SearchRanker ranks search results by relevance
type SearchRanker struct {
	weights map[string]float64
}

// SemanticSearchEngine provides semantic search capabilities
type SemanticSearchEngine struct {
	ollamaHost  string
	ollamaModel string
	client      *http.Client
	embeddings  map[string][]float64
	mutex       sync.RWMutex
}

// SearchResult represents a search result with enhanced metadata
type SearchResult struct {
	File         string                 `json:"file"`
	Score        float64                `json:"score"`
	Snippet      string                 `json:"snippet"`
	Type         string                 `json:"type"`
	Relevance    float64                `json:"relevance"`
	Confidence   float64                `json:"confidence"`
	Metadata     map[string]interface{} `json:"metadata"`
	Highlights   []string               `json:"highlights"`
	Tags         []string               `json:"tags"`
	Links        []string               `json:"links"`
	Headers      []string               `json:"headers"`
	WordCount    int                    `json:"word_count"`
	LastModified time.Time              `json:"last_modified"`
}

// SearchQuery represents a search query with options
type SearchQuery struct {
	Query          string            `json:"query"`
	Type           string            `json:"type"` // "text", "semantic", "fuzzy", "regex"
	Filters        map[string]string `json:"filters"`
	SortBy         string            `json:"sort_by"` // "relevance", "date", "filename"
	MaxResults     int               `json:"max_results"`
	IncludeContent bool              `json:"include_content"`
	Highlight      bool              `json:"highlight"`
}

// NewAdvancedSmartSearchEngine creates a new advanced search engine
func NewAdvancedSmartSearchEngine(apiPipeline *APIPipeline, ollamaHost, ollamaModel string) *AdvancedSmartSearchEngine {
	return &AdvancedSmartSearchEngine{
		apiPipeline: apiPipeline,
		ollamaHost:  ollamaHost,
		ollamaModel: ollamaModel,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
		cache: &SearchCache{
			results:    make(map[string]*CachedSearchResult),
			embeddings: make(map[string][]float64),
			ttl:        10 * time.Minute,
			maxSize:    1000,
		},
		indexer: &ContentIndexer{
			index:     make(map[string]*IndexedContent),
			fileIndex: make(map[string][]string),
			wordIndex: make(map[string][]string),
		},
		analyzer: &ContentAnalyzer{
			stopWords: getStopWords(),
			stemmer:   NewStemmer(),
		},
		ranker: &SearchRanker{
			weights: map[string]float64{
				"filename": 0.3,
				"content":  0.4,
				"tags":     0.1,
				"headers":  0.1,
				"links":    0.05,
				"metadata": 0.05,
			},
		},
		semanticEngine: &SemanticSearchEngine{
			ollamaHost:  ollamaHost,
			ollamaModel: ollamaModel,
			client: &http.Client{
				Timeout: 30 * time.Second,
			},
			embeddings: make(map[string][]float64),
		},
	}
}

// Search performs an advanced search with multiple algorithms
func (se *AdvancedSmartSearchEngine) Search(query *SearchQuery) ([]SearchResult, error) {
	start := time.Now()

	// Check cache first
	if cached, found := se.cache.Get(query.Query); found {
		return cached.Results, nil
	}

	// Perform search based on type
	var results []SearchResult
	var err error

	switch query.Type {
	case "semantic":
		results, err = se.performSemanticSearch(query)
	case "fuzzy":
		results, err = se.performFuzzySearch(query)
	case "regex":
		results, err = se.performRegexSearch(query)
	default:
		results, err = se.performTextSearch(query)
	}

	if err != nil {
		return nil, err
	}

	// Rank and sort results
	results = se.ranker.RankResults(results, query)

	// Apply filters
	results = se.applyFilters(results, query.Filters)

	// Limit results
	if query.MaxResults > 0 && len(results) > query.MaxResults {
		results = results[:query.MaxResults]
	}

	// Cache results
	se.cache.Set(query.Query, results)

	// Record metrics
	duration := time.Since(start)
	se.recordSearchMetrics(query, len(results), duration)

	return results, nil
}

// performTextSearch performs traditional text search
func (se *AdvancedSmartSearchEngine) performTextSearch(query *SearchQuery) ([]SearchResult, error) {
	// Get all files from vault
	result := se.apiPipeline.ListVaultFiles("")
	if !result.Success {
		return nil, result.Error
	}

	var results []SearchResult
	queryLower := strings.ToLower(query.Query)
	queryWords := se.analyzer.Tokenize(query.Query)

	// Search through files
	for _, file := range se.getFileList(result.Data) {
		if strings.HasSuffix(file, "/") {
			continue // Skip directories
		}

		// Check filename match
		if strings.Contains(strings.ToLower(file), queryLower) {
			results = append(results, SearchResult{
				File:       file,
				Score:      0.9,
				Type:       "filename",
				Relevance:  0.9,
				Confidence: 0.9,
			})
		}

		// Check content for markdown files
		if strings.HasSuffix(strings.ToLower(file), ".md") {
			contentResult := se.apiPipeline.ReadVaultFile(file)
			if contentResult.Success {
				content := se.getContentString(contentResult.Data)
				contentLower := strings.ToLower(content)

				if strings.Contains(contentLower, queryLower) {
					score := se.calculateTextScore(content, queryWords)
					snippet := se.extractSnippet(content, queryLower)
					highlights := se.extractHighlights(content, queryWords)

					results = append(results, SearchResult{
						File:       file,
						Score:      score,
						Snippet:    snippet,
						Type:       "content",
						Relevance:  score,
						Confidence: score,
						Highlights: highlights,
						WordCount:  len(strings.Fields(content)),
					})
				}
			}
		}
	}

	return results, nil
}

// performSemanticSearch performs semantic search using AI embeddings
func (se *AdvancedSmartSearchEngine) performSemanticSearch(query *SearchQuery) ([]SearchResult, error) {
	// Generate query embedding
	queryEmbedding, err := se.semanticEngine.GenerateEmbedding(query.Query)
	if err != nil {
		return nil, fmt.Errorf("failed to generate query embedding: %v", err)
	}

	// Get all files and their embeddings
	files, err := se.getAllFilesWithEmbeddings()
	if err != nil {
		return nil, err
	}

	var results []SearchResult

	for file, embedding := range files {
		similarity := se.calculateCosineSimilarity(queryEmbedding, embedding)

		if similarity > 0.3 { // Threshold for semantic similarity
			results = append(results, SearchResult{
				File:       file,
				Score:      similarity,
				Type:       "semantic",
				Relevance:  similarity,
				Confidence: similarity,
				Metadata: map[string]interface{}{
					"similarity":  similarity,
					"search_type": "semantic",
				},
			})
		}
	}

	return results, nil
}

// performFuzzySearch performs fuzzy string matching
func (se *AdvancedSmartSearchEngine) performFuzzySearch(query *SearchQuery) ([]SearchResult, error) {
	// Get all files
	result := se.apiPipeline.ListVaultFiles("")
	if !result.Success {
		return nil, result.Error
	}

	var results []SearchResult
	queryLower := strings.ToLower(query.Query)

	for _, file := range se.getFileList(result.Data) {
		if strings.HasSuffix(file, "/") {
			continue
		}

		// Calculate fuzzy match score
		score := se.calculateFuzzyScore(file, queryLower)
		if score > 0.5 {
			results = append(results, SearchResult{
				File:       file,
				Score:      score,
				Type:       "fuzzy",
				Relevance:  score,
				Confidence: score,
				Metadata: map[string]interface{}{
					"fuzzy_score": score,
					"search_type": "fuzzy",
				},
			})
		}

		// Check content for markdown files
		if strings.HasSuffix(strings.ToLower(file), ".md") {
			contentResult := se.apiPipeline.ReadVaultFile(file)
			if contentResult.Success {
				content := se.getContentString(contentResult.Data)
				contentScore := se.calculateFuzzyScore(content, queryLower)

				if contentScore > 0.3 {
					results = append(results, SearchResult{
						File:       file,
						Score:      contentScore,
						Snippet:    se.extractSnippet(content, queryLower),
						Type:       "fuzzy_content",
						Relevance:  contentScore,
						Confidence: contentScore,
						Metadata: map[string]interface{}{
							"fuzzy_score": contentScore,
							"search_type": "fuzzy_content",
						},
					})
				}
			}
		}
	}

	return results, nil
}

// performRegexSearch performs regex pattern matching
func (se *AdvancedSmartSearchEngine) performRegexSearch(query *SearchQuery) ([]SearchResult, error) {
	// Compile regex pattern
	pattern, err := regexp.Compile(query.Query)
	if err != nil {
		return nil, fmt.Errorf("invalid regex pattern: %v", err)
	}

	// Get all files
	result := se.apiPipeline.ListVaultFiles("")
	if !result.Success {
		return nil, result.Error
	}

	var results []SearchResult

	for _, file := range se.getFileList(result.Data) {
		if strings.HasSuffix(file, "/") {
			continue
		}

		// Check filename match
		if pattern.MatchString(file) {
			results = append(results, SearchResult{
				File:       file,
				Score:      1.0,
				Type:       "regex_filename",
				Relevance:  1.0,
				Confidence: 1.0,
				Metadata: map[string]interface{}{
					"pattern":     query.Query,
					"search_type": "regex",
				},
			})
		}

		// Check content for markdown files
		if strings.HasSuffix(strings.ToLower(file), ".md") {
			contentResult := se.apiPipeline.ReadVaultFile(file)
			if contentResult.Success {
				content := se.getContentString(contentResult.Data)

				if pattern.MatchString(content) {
					matches := pattern.FindAllString(content, -1)
					results = append(results, SearchResult{
						File:       file,
						Score:      float64(len(matches)),
						Snippet:    se.extractRegexSnippet(content, pattern),
						Type:       "regex_content",
						Relevance:  float64(len(matches)),
						Confidence: 1.0,
						Highlights: matches,
						Metadata: map[string]interface{}{
							"pattern":     query.Query,
							"matches":     len(matches),
							"search_type": "regex_content",
						},
					})
				}
			}
		}
	}

	return results, nil
}

// Helper methods
func (se *AdvancedSmartSearchEngine) getFileList(data interface{}) []string {
	if files, ok := data.([]string); ok {
		return files
	}
	if result, ok := data.(map[string]interface{}); ok {
		if files, ok := result["files"].([]interface{}); ok {
			var fileList []string
			for _, file := range files {
				if fileStr, ok := file.(string); ok {
					fileList = append(fileList, fileStr)
				}
			}
			return fileList
		}
	}
	return []string{}
}

func (se *AdvancedSmartSearchEngine) getContentString(data interface{}) string {
	if content, ok := data.(string); ok {
		return content
	}
	return ""
}

func (se *AdvancedSmartSearchEngine) calculateTextScore(content string, queryWords []string) float64 {
	contentLower := strings.ToLower(content)
	score := 0.0

	for _, word := range queryWords {
		wordLower := strings.ToLower(word)
		count := strings.Count(contentLower, wordLower)
		if count > 0 {
			score += float64(count) * 0.1
		}
	}

	// Normalize score
	if score > 1.0 {
		score = 1.0
	}

	return score
}

func (se *AdvancedSmartSearchEngine) calculateFuzzyScore(text, query string) float64 {
	// Simple Levenshtein distance-based fuzzy matching
	distance := se.levenshteinDistance(strings.ToLower(text), strings.ToLower(query))
	maxLen := math.Max(float64(len(text)), float64(len(query)))

	if maxLen == 0 {
		return 1.0
	}

	return 1.0 - (float64(distance) / maxLen)
}

func (se *AdvancedSmartSearchEngine) levenshteinDistance(s1, s2 string) int {
	r1, r2 := []rune(s1), []rune(s2)
	rows := len(r1) + 1
	cols := len(r2) + 1

	d := make([][]int, rows)
	for i := range d {
		d[i] = make([]int, cols)
	}

	for i := 1; i < rows; i++ {
		d[i][0] = i
	}
	for j := 1; j < cols; j++ {
		d[0][j] = j
	}

	for i := 1; i < rows; i++ {
		for j := 1; j < cols; j++ {
			cost := 0
			if r1[i-1] != r2[j-1] {
				cost = 1
			}
			d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+cost)
		}
	}

	return d[rows-1][cols-1]
}

func (se *AdvancedSmartSearchEngine) extractSnippet(content, query string) string {
	contentLower := strings.ToLower(content)
	queryLower := strings.ToLower(query)

	index := strings.Index(contentLower, queryLower)
	if index == -1 {
		return content[:min(200, len(content))]
	}

	start := max(0, index-100)
	end := min(len(content), index+len(query)+100)

	snippet := content[start:end]
	if start > 0 {
		snippet = "..." + snippet
	}
	if end < len(content) {
		snippet = snippet + "..."
	}

	return snippet
}

func (se *AdvancedSmartSearchEngine) extractRegexSnippet(content string, pattern *regexp.Regexp) string {
	matches := pattern.FindAllStringIndex(content, 1)
	if len(matches) == 0 {
		return content[:min(200, len(content))]
	}

	start := max(0, matches[0][0]-100)
	end := min(len(content), matches[0][1]+100)

	snippet := content[start:end]
	if start > 0 {
		snippet = "..." + snippet
	}
	if end < len(content) {
		snippet = snippet + "..."
	}

	return snippet
}

func (se *AdvancedSmartSearchEngine) extractHighlights(content string, queryWords []string) []string {
	var highlights []string
	contentLower := strings.ToLower(content)

	for _, word := range queryWords {
		wordLower := strings.ToLower(word)
		index := strings.Index(contentLower, wordLower)
		if index != -1 {
			start := max(0, index-20)
			end := min(len(content), index+len(word)+20)
			highlight := content[start:end]
			highlights = append(highlights, highlight)
		}
	}

	return highlights
}

func (se *AdvancedSmartSearchEngine) applyFilters(results []SearchResult, filters map[string]string) []SearchResult {
	if len(filters) == 0 {
		return results
	}

	var filtered []SearchResult
	for _, result := range results {
		include := true

		for key, value := range filters {
			switch key {
			case "type":
				if result.Type != value {
					include = false
				}
			case "min_score":
				if result.Score < parseFloat(value) {
					include = false
				}
			case "file_extension":
				if !strings.HasSuffix(result.File, value) {
					include = false
				}
			}

			if !include {
				break
			}
		}

		if include {
			filtered = append(filtered, result)
		}
	}

	return filtered
}

func (se *AdvancedSmartSearchEngine) recordSearchMetrics(query *SearchQuery, resultCount int, duration time.Duration) {
	// Record search metrics for analytics
	metrics := map[string]interface{}{
		"query":        query.Query,
		"type":         query.Type,
		"result_count": resultCount,
		"duration_ms":  duration.Milliseconds(),
		"timestamp":    time.Now(),
	}

	// In a real implementation, this would be sent to an analytics system
	fmt.Printf("🔍 Search metrics: %+v\n", metrics)
}

// Cache methods
func (sc *SearchCache) Get(query string) (*CachedSearchResult, bool) {
	sc.mutex.RLock()
	defer sc.mutex.RUnlock()

	result, exists := sc.results[query]
	if !exists {
		return nil, false
	}

	// Check if expired
	if time.Since(result.Timestamp) > result.TTL {
		delete(sc.results, query)
		return nil, false
	}

	return result, true
}

func (sc *SearchCache) Set(query string, results []SearchResult) {
	sc.mutex.Lock()
	defer sc.mutex.Unlock()

	// Check size limit
	if len(sc.results) >= sc.maxSize {
		// Remove oldest entry
		var oldestQuery string
		var oldestTime time.Time
		for q, r := range sc.results {
			if oldestQuery == "" || r.Timestamp.Before(oldestTime) {
				oldestQuery = q
				oldestTime = r.Timestamp
			}
		}
		delete(sc.results, oldestQuery)
	}

	sc.results[query] = &CachedSearchResult{
		Results:   results,
		Timestamp: time.Now(),
		TTL:       sc.ttl,
		QueryHash: fmt.Sprintf("%x", query),
	}
}

// Content Analyzer methods
func (ca *ContentAnalyzer) Tokenize(text string) []string {
	words := strings.Fields(strings.ToLower(text))
	var tokens []string

	for _, word := range words {
		// Remove punctuation
		word = regexp.MustCompile(`[^\w]`).ReplaceAllString(word, "")
		if word != "" && !ca.stopWords[word] {
			tokens = append(tokens, word)
		}
	}

	return tokens
}

// Search Ranker methods
func (sr *SearchRanker) RankResults(results []SearchResult, query *SearchQuery) []SearchResult {
	// Calculate final scores based on weights
	for i := range results {
		results[i].Score = sr.calculateFinalScore(results[i])
	}

	// Sort by score
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	return results
}

func (sr *SearchRanker) calculateFinalScore(result SearchResult) float64 {
	score := 0.0

	// Apply weights based on result type
	switch result.Type {
	case "filename":
		score = result.Relevance * sr.weights["filename"]
	case "content":
		score = result.Relevance * sr.weights["content"]
	case "semantic":
		score = result.Relevance * sr.weights["content"]
	case "fuzzy":
		score = result.Relevance * 0.7
	case "regex":
		score = result.Relevance * 0.8
	}

	// Boost score for high confidence
	score *= (1.0 + result.Confidence*0.2)

	return math.Min(score, 1.0)
}

// Semantic Search Engine methods
func (sse *SemanticSearchEngine) GenerateEmbedding(text string) ([]float64, error) {
	// This would integrate with Ollama/DeepSeek to generate embeddings
	// For now, return a mock embedding
	return []float64{0.1, 0.2, 0.3, 0.4, 0.5}, nil
}

func (sse *SemanticSearchEngine) calculateCosineSimilarity(a, b []float64) float64 {
	if len(a) != len(b) {
		return 0.0
	}

	var dotProduct, normA, normB float64
	for i := range a {
		dotProduct += a[i] * b[i]
		normA += a[i] * a[i]
		normB += b[i] * b[i]
	}

	if normA == 0 || normB == 0 {
		return 0.0
	}

	return dotProduct / (math.Sqrt(normA) * math.Sqrt(normB))
}

// Helper functions
func getStopWords() map[string]bool {
	return map[string]bool{
		"a": true, "an": true, "and": true, "are": true, "as": true, "at": true,
		"be": true, "by": true, "for": true, "from": true, "has": true, "he": true,
		"in": true, "is": true, "it": true, "its": true, "of": true, "on": true,
		"that": true, "the": true, "to": true, "was": true, "will": true, "with": true,
	}
}

func NewStemmer() *Stemmer {
	return &Stemmer{}
}

type Stemmer struct{}

func (s *Stemmer) Stem(word string) string {
	// Simple stemming implementation
	// In a real implementation, this would use Porter stemming or similar
	return word
}

func (se *AdvancedSmartSearchEngine) getAllFilesWithEmbeddings() (map[string][]float64, error) {
	// This would get all files and their embeddings
	// For now, return empty map
	return make(map[string][]float64), nil
}

func parseFloat(s string) float64 {
	// Simple float parsing
	// In a real implementation, use strconv.ParseFloat
	return 0.0
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// Demo function
func demoAdvancedSmartSearchEngine() {
	fmt.Println("🔍 ADVANCED SMART SEARCH ENGINE DEMO")
	fmt.Println("====================================")

	// Create API pipeline
	apiPipeline := NewAPIPipeline("obsidian-vault", "https://127.0.0.1:27124",
		"b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")

	// Create search engine
	searchEngine := NewAdvancedSmartSearchEngine(apiPipeline, "http://localhost:11434", "deepseek-r1:8b")

	// Test different search types
	queries := []*SearchQuery{
		{
			Query:      "logica",
			Type:       "text",
			MaxResults: 5,
		},
		{
			Query:      "matematica",
			Type:       "fuzzy",
			MaxResults: 3,
		},
		{
			Query:      ".*\\.md$",
			Type:       "regex",
			MaxResults: 10,
		},
	}

	for i, query := range queries {
		fmt.Printf("\n🔍 Test %d: %s search for '%s'\n", i+1, query.Type, query.Query)

		results, err := searchEngine.Search(query)
		if err != nil {
			fmt.Printf("❌ Search failed: %v\n", err)
			continue
		}

		fmt.Printf("✅ Found %d results:\n", len(results))
		for j, result := range results {
			fmt.Printf("   %d. %s (Score: %.2f, Type: %s)\n", j+1, result.File, result.Score, result.Type)
			if result.Snippet != "" {
				fmt.Printf("      %s\n", result.Snippet)
			}
		}
	}

	fmt.Println("\n🎉 Advanced Smart Search Engine demo completed!")
}

func main() {
	demoAdvancedSmartSearchEngine()
}
