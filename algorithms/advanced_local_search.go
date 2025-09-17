package algorithms

import (
	"math"
	"regexp"
	"sort"
	"strings"
	"time"
)

// AdvancedLocalSearch emulates native search with fuzzy, regex, case-sensitive,
// whole-word, and Portuguese variations using local processing on fetched contents
type AdvancedLocalSearch struct {
	variations map[string][]string
	threshold  float64
	timeout    time.Duration
}

// SearchFlags defines search behavior options
type SearchFlags struct {
	CaseSensitive bool
	WholeWord     bool
	Regex         bool
	Fuzzy         bool
	Portuguese    bool
	MaxResults    int
}

// SearchResult represents a search result with scoring
type SearchResult struct {
	File      FileInfo `json:"file"`
	Score     float64  `json:"score"`
	MatchType string   `json:"match_type"`
	MatchText string   `json:"match_text"`
	Variation string   `json:"variation"`
	Context   string   `json:"context"`
}

// NewAdvancedLocalSearch creates a new AdvancedLocalSearch instance
func NewAdvancedLocalSearch() *AdvancedLocalSearch {
	return &AdvancedLocalSearch{
		variations: make(map[string][]string),
		threshold:  0.6,
		timeout:    30 * time.Second,
	}
}

// Search performs advanced local search with multiple matching strategies
func (als *AdvancedLocalSearch) Search(query string, files []FileInfo, contentFetcher func(FileInfo) (string, error), flags SearchFlags) ([]SearchResult, error) {
	if flags.MaxResults <= 0 {
		flags.MaxResults = 10
	}

	// Generate query variations
	variations := als.generateVariations(query, flags)

	results := make([]SearchResult, 0)
	startTime := time.Now()

	for _, file := range files {
		// Check timeout
		if time.Since(startTime) > als.timeout {
			break
		}

		content, err := contentFetcher(file)
		if err != nil {
			continue // Skip files that can't be read
		}

		// Search for each variation
		for _, variation := range variations {
			matches := als.findMatches(content, variation, flags)
			for _, match := range matches {
				results = append(results, SearchResult{
					File:      file,
					Score:     match.Score,
					MatchType: match.MatchType,
					MatchText: match.MatchText,
					Variation: variation,
					Context:   match.Context,
				})
			}
		}
	}

	// Sort by score (descending) and then by modified time (descending)
	sort.Slice(results, func(i, j int) bool {
		if results[i].Score == results[j].Score {
			return results[i].File.Modified.After(results[j].File.Modified)
		}
		return results[i].Score > results[j].Score
	})

	// Limit results
	if len(results) > flags.MaxResults {
		results = results[:flags.MaxResults]
	}

	return results, nil
}

// generateVariations creates search variations including Portuguese translations
func (als *AdvancedLocalSearch) generateVariations(query string, flags SearchFlags) []string {
	variations := []string{query}

	if flags.Portuguese {
		// Add Portuguese variations
		portugueseVariations := als.getPortugueseVariations(query)
		variations = append(variations, portugueseVariations...)
	}

	// Add case variations if not case sensitive
	if !flags.CaseSensitive {
		variations = append(variations, strings.ToLower(query))
		variations = append(variations, strings.ToUpper(query))
		variations = append(variations, strings.Title(query))
	}

	// Remove duplicates
	unique := make(map[string]bool)
	finalVariations := make([]string, 0)
	for _, v := range variations {
		if !unique[v] {
			unique[v] = true
			finalVariations = append(finalVariations, v)
		}
	}

	return finalVariations
}

// getPortugueseVariations returns Portuguese language variations
func (als *AdvancedLocalSearch) getPortugueseVariations(query string) []string {
	variations := make([]string, 0)
	queryLower := strings.ToLower(query)

	// Common Portuguese word variations
	portugueseMap := map[string][]string{
		"alta":            {"alto", "elevada", "superior", "máxima"},
		"performance":     {"desempenho", "rendimento", "eficiência"},
		"logica":          {"lógica", "raciocínio", "pensamento"},
		"computacao":      {"computação", "informática", "tecnologia"},
		"desenvolvimento": {"desenvolvimento", "criação", "construção"},
		"algoritmo":       {"algoritmo", "procedimento", "método"},
		"dados":           {"dados", "informações", "registros"},
		"analise":         {"análise", "exame", "estudo"},
		"resultado":       {"resultado", "consequência", "efeito"},
		"processo":        {"processo", "procedimento", "método"},
	}

	for key, values := range portugueseMap {
		if strings.Contains(queryLower, key) {
			for _, value := range values {
				newQuery := strings.Replace(queryLower, key, value, -1)
				variations = append(variations, newQuery)
			}
		}
	}

	return variations
}

// Match represents a single match result
type Match struct {
	Score     float64
	MatchType string
	MatchText string
	Context   string
}

// findMatches finds all matches in content using different strategies
func (als *AdvancedLocalSearch) findMatches(content, variation string, flags SearchFlags) []Match {
	matches := make([]Match, 0)

	// Exact match
	if exactMatch := als.findExactMatch(content, variation, flags); exactMatch != nil {
		matches = append(matches, *exactMatch)
	}

	// Regex match
	if flags.Regex {
		if regexMatch := als.findRegexMatch(content, variation); regexMatch != nil {
			matches = append(matches, *regexMatch)
		}
	}

	// Whole word match
	if flags.WholeWord {
		if wholeWordMatch := als.findWholeWordMatch(content, variation, flags); wholeWordMatch != nil {
			matches = append(matches, *wholeWordMatch)
		}
	}

	// Fuzzy match
	if flags.Fuzzy {
		if fuzzyMatch := als.findFuzzyMatch(content, variation); fuzzyMatch != nil {
			matches = append(matches, *fuzzyMatch)
		}
	}

	return matches
}

// findExactMatch finds exact string matches
func (als *AdvancedLocalSearch) findExactMatch(content, variation string, flags SearchFlags) *Match {
	searchContent := content
	searchVariation := variation

	if !flags.CaseSensitive {
		searchContent = strings.ToLower(content)
		searchVariation = strings.ToLower(variation)
	}

	if strings.Contains(searchContent, searchVariation) {
		score := 1.0
		if !flags.CaseSensitive {
			score = 0.9 // Slightly lower score for case-insensitive matches
		}

		context := als.extractContext(content, variation, 50)
		return &Match{
			Score:     score,
			MatchType: "exact",
			MatchText: variation,
			Context:   context,
		}
	}

	return nil
}

// findRegexMatch finds regex pattern matches
func (als *AdvancedLocalSearch) findRegexMatch(content, pattern string) *Match {
	regex, err := regexp.Compile(pattern)
	if err != nil {
		return nil
	}

	matches := regex.FindAllString(content, -1)
	if len(matches) > 0 {
		score := 0.8 // Regex matches get slightly lower score
		context := als.extractContext(content, matches[0], 50)
		return &Match{
			Score:     score,
			MatchType: "regex",
			MatchText: matches[0],
			Context:   context,
		}
	}

	return nil
}

// findWholeWordMatch finds whole word matches
func (als *AdvancedLocalSearch) findWholeWordMatch(content, variation string, flags SearchFlags) *Match {
	searchContent := content
	searchVariation := variation

	if !flags.CaseSensitive {
		searchContent = strings.ToLower(content)
		searchVariation = strings.ToLower(variation)
	}

	// Add word boundaries
	pattern := "\\b" + regexp.QuoteMeta(searchVariation) + "\\b"
	regex, err := regexp.Compile(pattern)
	if err != nil {
		return nil
	}

	matches := regex.FindAllString(searchContent, -1)
	if len(matches) > 0 {
		score := 0.85 // Whole word matches get good score
		context := als.extractContext(content, variation, 50)
		return &Match{
			Score:     score,
			MatchType: "whole_word",
			MatchText: variation,
			Context:   context,
		}
	}

	return nil
}

// findFuzzyMatch finds fuzzy matches using Levenshtein distance
func (als *AdvancedLocalSearch) findFuzzyMatch(content, variation string) *Match {
	words := strings.Fields(content)
	bestMatch := ""
	bestScore := 0.0

	for _, word := range words {
		similarity := als.calculateSimilarity(word, variation)
		if similarity > bestScore && similarity >= als.threshold {
			bestScore = similarity
			bestMatch = word
		}
	}

	if bestMatch != "" {
		context := als.extractContext(content, bestMatch, 50)
		return &Match{
			Score:     bestScore,
			MatchType: "fuzzy",
			MatchText: bestMatch,
			Context:   context,
		}
	}

	return nil
}

// calculateSimilarity calculates similarity between two strings using Levenshtein distance
func (als *AdvancedLocalSearch) calculateSimilarity(s1, s2 string) float64 {
	s1 = strings.ToLower(s1)
	s2 = strings.ToLower(s2)

	if s1 == s2 {
		return 1.0
	}

	distance := als.levenshteinDistance(s1, s2)
	maxLen := math.Max(float64(len(s1)), float64(len(s2)))

	if maxLen == 0 {
		return 0.0
	}

	return 1.0 - (float64(distance) / maxLen)
}

// levenshteinDistance calculates the Levenshtein distance between two strings
func (als *AdvancedLocalSearch) levenshteinDistance(s1, s2 string) int {
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
			d[i][j] = minThree(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+cost)
		}
	}

	return d[rows-1][cols-1]
}

// minInt returns the minimum of two integers
func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// minThree returns the minimum of three integers
func minThree(a, b, c int) int {
	return minInt(a, minInt(b, c))
}

// extractContext extracts context around a match
func (als *AdvancedLocalSearch) extractContext(content, match string, contextSize int) string {
	index := strings.Index(strings.ToLower(content), strings.ToLower(match))
	if index == -1 {
		return ""
	}

	start := index - contextSize
	if start < 0 {
		start = 0
	}

	end := index + len(match) + contextSize
	if end > len(content) {
		end = len(content)
	}

	context := content[start:end]
	if start > 0 {
		context = "..." + context
	}
	if end < len(content) {
		context = context + "..."
	}

	return context
}

// SetThreshold sets the fuzzy matching threshold
func (als *AdvancedLocalSearch) SetThreshold(threshold float64) {
	als.threshold = threshold
}

// SetTimeout sets the search timeout
func (als *AdvancedLocalSearch) SetTimeout(timeout time.Duration) {
	als.timeout = timeout
}

// GetStats returns search statistics
func (als *AdvancedLocalSearch) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"Threshold":  als.threshold,
		"Timeout":    als.timeout,
		"Variations": len(als.variations),
	}
}
