package algorithms

import (
	"math"
	"strings"
)

// BM25TFIDF implements BM25-lite and TF-IDF ranking algorithms
// Ranks candidates by term frequency on text fields only
type BM25TFIDF struct {
	k1 float64 // BM25 parameter for term frequency saturation
	b  float64 // BM25 parameter for length normalization
}

// TermFrequency represents term frequency data
type TermFrequency struct {
	Term      string
	Frequency int
	TF        float64 // Term frequency
	IDF       float64 // Inverse document frequency
	Score     float64 // Final BM25/TF-IDF score
}

// DocumentStats represents document statistics
type DocumentStats struct {
	Length     int
	AvgLength  float64
	TermCounts map[string]int
}

// NewBM25TFIDF creates a new BM25TFIDF instance
func NewBM25TFIDF() *BM25TFIDF {
	return &BM25TFIDF{
		k1: 1.2,  // Standard BM25 parameter
		b:  0.75, // Standard BM25 parameter
	}
}

// RankCandidates ranks candidates using BM25-lite algorithm
func (bt *BM25TFIDF) RankCandidates(candidates []Candidate, query string) []Candidate {
	if len(candidates) == 0 {
		return candidates
	}

	// Step 1: Build inverted index
	index := bt.buildInvertedIndex(candidates)

	// Step 2: Calculate document statistics
	docStats := bt.calculateDocumentStats(candidates)

	// Step 3: Process query terms
	queryTerms := bt.tokenizeQuery(query)

	// Step 4: Calculate scores for each candidate
	for i := range candidates {
		candidates[i].RelevanceScore = bt.calculateBM25Score(
			&candidates[i],
			queryTerms,
			index,
			docStats,
			len(candidates),
		)
	}

	// Step 5: Sort by score (descending)
	bt.sortCandidatesByScore(candidates)

	return candidates
}

// GetStats returns statistics about the BM25TFIDF algorithm
func (bt *BM25TFIDF) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"k1": bt.k1,
		"b":  bt.b,
	}
}

// buildInvertedIndex creates an inverted index from candidates
func (bt *BM25TFIDF) buildInvertedIndex(candidates []Candidate) map[string][]int {
	index := make(map[string][]int)

	for i, candidate := range candidates {
		// Index filename
		terms := bt.tokenizeText(candidate.Name)
		for _, term := range terms {
			if _, exists := index[term]; !exists {
				index[term] = []int{}
			}
			index[term] = append(index[term], i)
		}

		// Index content
		terms = bt.tokenizeText(candidate.Content)
		for _, term := range terms {
			if _, exists := index[term]; !exists {
				index[term] = []int{}
			}
			index[term] = append(index[term], i)
		}
	}

	return index
}

// calculateDocumentStats calculates statistics for all documents
func (bt *BM25TFIDF) calculateDocumentStats(candidates []Candidate) DocumentStats {
	totalLength := 0
	termCounts := make(map[string]int)

	for _, candidate := range candidates {
		docLength := len(candidate.Name) + len(candidate.Content)
		totalLength += docLength

		// Count terms in this document
		terms := bt.tokenizeText(candidate.Name + " " + candidate.Content)
		for _, term := range terms {
			termCounts[term]++
		}
	}

	avgLength := float64(totalLength) / float64(len(candidates))

	return DocumentStats{
		Length:     totalLength,
		AvgLength:  avgLength,
		TermCounts: termCounts,
	}
}

// calculateBM25Score calculates BM25 score for a candidate
func (bt *BM25TFIDF) calculateBM25Score(
	candidate *Candidate,
	queryTerms []string,
	index map[string][]int,
	docStats DocumentStats,
	totalDocs int,
) float64 {
	score := 0.0
	docLength := float64(len(candidate.Name) + len(candidate.Content))

	for _, term := range queryTerms {
		// Calculate term frequency in this document
		tf := bt.calculateTermFrequency(candidate, term)

		// Calculate document frequency
		df := float64(len(index[term]))

		// Calculate IDF
		idf := bt.calculateIDF(df, float64(totalDocs))

		// Calculate BM25 score component
		if tf > 0 {
			// BM25 formula: IDF * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (docLength / avgLength)))
			numerator := tf * (bt.k1 + 1)
			denominator := tf + bt.k1*(1-bt.b+bt.b*(docLength/docStats.AvgLength))
			bm25Component := idf * (numerator / denominator)
			score += bm25Component
		}
	}

	return score
}

// calculateTermFrequency calculates term frequency in a document
func (bt *BM25TFIDF) calculateTermFrequency(candidate *Candidate, term string) float64 {
	text := strings.ToLower(candidate.Name + " " + candidate.Content)
	termLower := strings.ToLower(term)

	count := strings.Count(text, termLower)
	if count == 0 {
		return 0.0
	}

	// Return raw count (BM25 handles normalization)
	return float64(count)
}

// calculateIDF calculates inverse document frequency
func (bt *BM25TFIDF) calculateIDF(df, totalDocs float64) float64 {
	if df == 0 {
		return 0.0
	}

	// IDF = log((N - df + 0.5) / (df + 0.5))
	// Where N is total documents, df is document frequency
	return math.Log((totalDocs - df + 0.5) / (df + 0.5))
}

// tokenizeQuery tokenizes the search query
func (bt *BM25TFIDF) tokenizeQuery(query string) []string {
	return bt.tokenizeText(query)
}

// tokenizeText tokenizes text into terms
func (bt *BM25TFIDF) tokenizeText(text string) []string {
	// Simple tokenization - split by spaces and clean
	words := strings.Fields(strings.ToLower(text))
	var terms []string

	for _, word := range words {
		// Remove punctuation and clean
		clean := strings.Trim(word, ".,!?;:()[]{}")
		if len(clean) > 1 { // Ignore single characters
			terms = append(terms, clean)
		}
	}

	return terms
}

// sortCandidatesByScore sorts candidates by relevance score (descending)
func (bt *BM25TFIDF) sortCandidatesByScore(candidates []Candidate) {
	// Simple bubble sort for small datasets
	n := len(candidates)
	for i := 0; i < n-1; i++ {
		for j := 0; j < n-i-1; j++ {
			if candidates[j].RelevanceScore < candidates[j+1].RelevanceScore {
				candidates[j], candidates[j+1] = candidates[j+1], candidates[j]
			}
		}
	}
}

// CalculateTFIDF calculates traditional TF-IDF score
func (bt *BM25TFIDF) CalculateTFIDF(candidate *Candidate, query string, allCandidates []Candidate) float64 {
	queryTerms := bt.tokenizeQuery(query)
	score := 0.0

	for _, term := range queryTerms {
		// Calculate TF (Term Frequency)
		tf := bt.calculateTermFrequency(candidate, term)

		// Calculate IDF (Inverse Document Frequency)
		df := bt.calculateDocumentFrequency(term, allCandidates)
		idf := bt.calculateIDF(df, float64(len(allCandidates)))

		// TF-IDF = TF * IDF
		score += tf * idf
	}

	return score
}

// calculateDocumentFrequency calculates how many documents contain a term
func (bt *BM25TFIDF) calculateDocumentFrequency(term string, candidates []Candidate) float64 {
	count := 0
	termLower := strings.ToLower(term)

	for _, candidate := range candidates {
		text := strings.ToLower(candidate.Name + " " + candidate.Content)
		if strings.Contains(text, termLower) {
			count++
		}
	}

	return float64(count)
}

// SetParameters allows customization of BM25 parameters
func (bt *BM25TFIDF) SetParameters(k1, b float64) {
	bt.k1 = k1
	bt.b = b
}

// GetRankingStats returns statistics about the ranking process
func (bt *BM25TFIDF) GetRankingStats(candidates []Candidate, query string) map[string]interface{} {
	queryTerms := bt.tokenizeQuery(query)

	return map[string]interface{}{
		"query_terms":     queryTerms,
		"candidate_count": len(candidates),
		"bm25_params": map[string]float64{
			"k1": bt.k1,
			"b":  bt.b,
		},
		"avg_score": bt.calculateAverageScore(candidates),
		"max_score": bt.calculateMaxScore(candidates),
	}
}

// calculateAverageScore calculates the average relevance score
func (bt *BM25TFIDF) calculateAverageScore(candidates []Candidate) float64 {
	if len(candidates) == 0 {
		return 0.0
	}

	sum := 0.0
	for _, candidate := range candidates {
		sum += candidate.RelevanceScore
	}

	return sum / float64(len(candidates))
}

// calculateMaxScore calculates the maximum relevance score
func (bt *BM25TFIDF) calculateMaxScore(candidates []Candidate) float64 {
	if len(candidates) == 0 {
		return 0.0
	}

	max := candidates[0].RelevanceScore
	for _, candidate := range candidates {
		if candidate.RelevanceScore > max {
			max = candidate.RelevanceScore
		}
	}

	return max
}
