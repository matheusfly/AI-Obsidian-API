package algorithms

import (
	"math"
	"strings"
	"unicode"
)

// ProximityMatcher scores query terms based on their closeness in note content
type ProximityMatcher struct {
	threshold      float64 // Minimum distance threshold for boosting
	proximityBoost float64 // Boost factor for proximity matches
	maxDistance    int     // Maximum distance to consider for proximity
}

// ProximityResult represents the result of proximity matching
type ProximityResult struct {
	Score        float64          `json:"score"`
	AvgDistance  float64          `json:"avg_distance"`
	TermCount    int              `json:"term_count"`
	HasProximity bool             `json:"has_proximity"`
	Positions    map[string][]int `json:"positions"`
}

// NewProximityMatcher creates a new ProximityMatcher instance
func NewProximityMatcher(threshold, proximityBoost float64, maxDistance int) *ProximityMatcher {
	return &ProximityMatcher{
		threshold:      threshold,
		proximityBoost: proximityBoost,
		maxDistance:    maxDistance,
	}
}

// CalculateProximityScore calculates proximity score for query terms in content
func (pm *ProximityMatcher) CalculateProximityScore(content, query string) *ProximityResult {
	// Normalize and tokenize
	terms := pm.tokenizeQuery(query)
	words := pm.tokenizeContent(content)

	if len(terms) == 0 || len(words) == 0 {
		return &ProximityResult{
			Score:        0.0,
			AvgDistance:  math.Inf(1),
			TermCount:    0,
			HasProximity: false,
			Positions:    make(map[string][]int),
		}
	}

	// Find positions of each term
	positions := make(map[string][]int)
	for i, word := range words {
		for _, term := range terms {
			if pm.isMatch(word, term) {
				positions[term] = append(positions[term], i)
			}
		}
	}

	// Check if all terms are found
	if len(positions) < len(terms) {
		return &ProximityResult{
			Score:        0.0,
			AvgDistance:  math.Inf(1),
			TermCount:    len(positions),
			HasProximity: false,
			Positions:    positions,
		}
	}

	// Calculate average pairwise distance
	avgDistance := pm.calculateAverageDistance(positions, terms)

	// Calculate proximity score
	score := pm.calculateScore(avgDistance)

	return &ProximityResult{
		Score:        score,
		AvgDistance:  avgDistance,
		TermCount:    len(terms),
		HasProximity: avgDistance < pm.threshold,
		Positions:    positions,
	}
}

// tokenizeQuery tokenizes the query into terms
func (pm *ProximityMatcher) tokenizeQuery(query string) []string {
	// Convert to lowercase and split by whitespace
	terms := strings.Fields(strings.ToLower(query))

	// Filter out very short terms (less than 2 characters)
	var filteredTerms []string
	for _, term := range terms {
		if len(term) >= 2 {
			filteredTerms = append(filteredTerms, term)
		}
	}

	return filteredTerms
}

// tokenizeContent tokenizes content into words
func (pm *ProximityMatcher) tokenizeContent(content string) []string {
	// Convert to lowercase
	content = strings.ToLower(content)

	// Split by whitespace and punctuation
	var words []string
	var current strings.Builder

	for _, r := range content {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			current.WriteRune(r)
		} else {
			if current.Len() > 0 {
				words = append(words, current.String())
				current.Reset()
			}
		}
	}

	// Add the last word if any
	if current.Len() > 0 {
		words = append(words, current.String())
	}

	return words
}

// isMatch checks if a word matches a term (exact or fuzzy)
func (pm *ProximityMatcher) isMatch(word, term string) bool {
	// Exact match
	if word == term {
		return true
	}

	// Fuzzy match for typos (simple Levenshtein distance)
	if pm.levenshteinDistance(word, term) <= 1 && len(word) >= 3 {
		return true
	}

	// Prefix match for partial words
	if len(term) >= 3 && strings.HasPrefix(word, term) {
		return true
	}

	return false
}

// levenshteinDistance calculates the Levenshtein distance between two strings
func (pm *ProximityMatcher) levenshteinDistance(s1, s2 string) int {
	if len(s1) == 0 {
		return len(s2)
	}
	if len(s2) == 0 {
		return len(s1)
	}

	rows := len(s1) + 1
	cols := len(s2) + 1

	d := make([][]int, rows)
	for i := range d {
		d[i] = make([]int, cols)
	}

	// Initialize first row and column
	for i := 0; i < rows; i++ {
		d[i][0] = i
	}
	for j := 0; j < cols; j++ {
		d[0][j] = j
	}

	// Fill the matrix
	for i := 1; i < rows; i++ {
		for j := 1; j < cols; j++ {
			cost := 0
			if s1[i-1] != s2[j-1] {
				cost = 1
			}
			d[i][j] = minIntProximity(
				minIntProximity(d[i-1][j]+1, d[i][j-1]+1), // deletion, insertion
				d[i-1][j-1]+cost,                          // substitution
			)
		}
	}

	return d[rows-1][cols-1]
}

// calculateAverageDistance calculates the average pairwise distance between terms
func (pm *ProximityMatcher) calculateAverageDistance(positions map[string][]int, terms []string) float64 {
	if len(terms) < 2 {
		return 0.0
	}

	var totalDistance float64
	pairCount := 0

	// Calculate distance between consecutive terms
	for i := 0; i < len(terms)-1; i++ {
		term1 := terms[i]
		term2 := terms[i+1]

		pos1 := positions[term1]
		pos2 := positions[term2]

		if len(pos1) == 0 || len(pos2) == 0 {
			continue
		}

		// Find minimum distance between any pair of positions
		minDist := math.Inf(1)
		for _, p1 := range pos1 {
			for _, p2 := range pos2 {
				dist := math.Abs(float64(p1 - p2))
				if dist < minDist {
					minDist = dist
				}
			}
		}

		if minDist != math.Inf(1) {
			totalDistance += minDist
			pairCount++
		}
	}

	if pairCount == 0 {
		return math.Inf(1)
	}

	return totalDistance / float64(pairCount)
}

// calculateScore calculates the proximity score based on average distance
func (pm *ProximityMatcher) calculateScore(avgDistance float64) float64 {
	if avgDistance == math.Inf(1) {
		return 0.0
	}

	// Score decreases as distance increases
	// Score = 1 / (1 + distance) for distances within threshold
	if avgDistance <= pm.threshold {
		return pm.proximityBoost / (1.0 + avgDistance)
	}

	// Reduced score for distances beyond threshold
	return pm.proximityBoost / (1.0 + avgDistance*2.0)
}

// BoostCandidate applies proximity boosting to a search candidate
func (pm *ProximityMatcher) BoostCandidate(candidate Candidate, query string) Candidate {
	// Calculate proximity score
	result := pm.CalculateProximityScore(candidate.Content, query)

	// Apply proximity boost to match score
	if result.HasProximity {
		candidate.MatchScore += result.Score
	}

	// Add proximity metadata
	if candidate.Metadata == nil {
		candidate.Metadata = make(map[string]interface{})
	}
	candidate.Metadata["proximity_score"] = result.Score
	candidate.Metadata["proximity_distance"] = result.AvgDistance
	candidate.Metadata["proximity_terms"] = result.TermCount

	return candidate
}

// BoostCandidates applies proximity boosting to multiple candidates
func (pm *ProximityMatcher) BoostCandidates(candidates []Candidate, query string) []Candidate {
	boostedCandidates := make([]Candidate, len(candidates))

	for i, candidate := range candidates {
		boostedCandidates[i] = pm.BoostCandidate(candidate, query)
	}

	return boostedCandidates
}

// GetStats returns statistics about the ProximityMatcher
func (pm *ProximityMatcher) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"threshold":       pm.threshold,
		"proximity_boost": pm.proximityBoost,
		"max_distance":    pm.maxDistance,
	}
}

// minIntProximity returns the minimum of two integers (for proximity matcher)
func minIntProximity(a, b int) int {
	if a < b {
		return a
	}
	return b
}
