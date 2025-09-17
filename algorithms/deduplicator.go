package algorithms

import (
	"crypto/md5"
	"encoding/hex"
	"math"
	"strings"
)

// Deduplicator performs fuzzy deduplication and canonicalization of candidates
// Removes near-duplicates and keeps canonical versions
type Deduplicator struct {
	similarityThreshold float64
	hashLength          int
	canonicalStrategy   string
}

// DuplicateInfo represents information about duplicate detection
type DuplicateInfo struct {
	Hash        string
	Similarity  float64
	IsDuplicate bool
	Canonical   bool
	Reason      string
}

// DeduplicationStats represents statistics about the deduplication process
type DeduplicationStats struct {
	OriginalCount     int
	DeduplicatedCount int
	DuplicatesFound   int
	SimilarityScores  []float64
}

// NewDeduplicator creates a new Deduplicator instance
func NewDeduplicator() *Deduplicator {
	return &Deduplicator{
		similarityThreshold: 0.9,        // 90% similarity threshold
		hashLength:          100,        // First 100 chars for hash
		canonicalStrategy:   "freshest", // freshest, shortest, longest
	}
}

// DeduplicateCandidates removes duplicates from candidates list
func (d *Deduplicator) DeduplicateCandidates(candidates []Candidate) []Candidate {
	if len(candidates) == 0 {
		return candidates
	}

	// Step 1: Sort candidates by modification time (freshest first)
	d.sortCandidatesByFreshness(candidates)

	// Step 2: Process candidates and remove duplicates
	var unique []Candidate
	seen := make(map[string]bool)

	for _, candidate := range candidates {
		// Generate hash for content comparison
		hash := d.generateContentHash(candidate)

		// Check if we've seen a similar hash
		if d.isDuplicate(hash, seen, candidate, unique) {
			continue // Skip duplicate
		}

		// Add to unique list and mark as seen
		unique = append(unique, candidate)
		seen[hash] = true
	}

	return unique
}

// generateContentHash generates a hash for content comparison
func (d *Deduplicator) generateContentHash(candidate Candidate) string {
	// Use filename + content prefix for hash
	content := candidate.Name + " " + candidate.Path

	// Add content prefix if available
	if len(candidate.Content) > 0 {
		contentPrefix := candidate.Content
		if len(contentPrefix) > d.hashLength {
			contentPrefix = contentPrefix[:d.hashLength]
		}
		content += " " + contentPrefix
	}

	// Generate MD5 hash
	hasher := md5.New()
	hasher.Write([]byte(content))
	return hex.EncodeToString(hasher.Sum(nil))
}

// isDuplicate checks if a candidate is a duplicate
func (d *Deduplicator) isDuplicate(hash string, seen map[string]bool, candidate Candidate, unique []Candidate) bool {
	// Check exact hash match
	if seen[hash] {
		return true
	}

	// Check fuzzy similarity with existing unique candidates
	for _, existing := range unique {
		similarity := d.calculateSimilarity(candidate, existing)
		if similarity >= d.similarityThreshold {
			return true
		}
	}

	return false
}

// calculateSimilarity calculates similarity between two candidates
func (d *Deduplicator) calculateSimilarity(candidate1, candidate2 Candidate) float64 {
	// Calculate multiple similarity metrics
	nameSim := d.calculateStringSimilarity(candidate1.Name, candidate2.Name)
	pathSim := d.calculateStringSimilarity(candidate1.Path, candidate2.Path)
	contentSim := d.calculateStringSimilarity(candidate1.Content, candidate2.Content)

	// Weighted average
	weights := map[string]float64{
		"name":    0.3,
		"path":    0.2,
		"content": 0.5,
	}

	similarity := nameSim*weights["name"] + pathSim*weights["path"] + contentSim*weights["content"]
	return similarity
}

// calculateStringSimilarity calculates Levenshtein-based similarity
func (d *Deduplicator) calculateStringSimilarity(s1, s2 string) float64 {
	if s1 == s2 {
		return 1.0
	}

	if len(s1) == 0 || len(s2) == 0 {
		return 0.0
	}

	// Calculate Levenshtein distance
	distance := d.levenshteinDistance(s1, s2)

	// Convert to similarity (0-1)
	maxLen := math.Max(float64(len(s1)), float64(len(s2)))
	similarity := 1.0 - (float64(distance) / maxLen)

	return similarity
}

// levenshteinDistance calculates the Levenshtein distance between two strings
func (d *Deduplicator) levenshteinDistance(s1, s2 string) int {
	r1, r2 := []rune(s1), []rune(s2)
	rows := len(r1) + 1
	cols := len(r2) + 1

	// Create distance matrix
	dist := make([][]int, rows)
	for i := range dist {
		dist[i] = make([]int, cols)
	}

	// Initialize first row and column
	for i := 1; i < rows; i++ {
		dist[i][0] = i
	}
	for j := 1; j < cols; j++ {
		dist[0][j] = j
	}

	// Fill the matrix
	for i := 1; i < rows; i++ {
		for j := 1; j < cols; j++ {
			cost := 0
			if r1[i-1] != r2[j-1] {
				cost = 1
			}

			dist[i][j] = minInt(
				minInt(dist[i-1][j]+1, dist[i][j-1]+1), // deletion, insertion
				dist[i-1][j-1]+cost,                    // substitution
			)
		}
	}

	return dist[rows-1][cols-1]
}

// sortCandidatesByFreshness sorts candidates by modification time (freshest first)
func (d *Deduplicator) sortCandidatesByFreshness(candidates []Candidate) {
	// Simple bubble sort for small datasets
	n := len(candidates)
	for i := 0; i < n-1; i++ {
		for j := 0; j < n-i-1; j++ {
			// Compare modification times (freshest first)
			if candidates[j].Modified.Before(candidates[j+1].Modified) {
				candidates[j], candidates[j+1] = candidates[j+1], candidates[j]
			}
		}
	}
}

// SetSimilarityThreshold sets the similarity threshold for duplicate detection
func (d *Deduplicator) SetSimilarityThreshold(threshold float64) {
	if threshold >= 0.0 && threshold <= 1.0 {
		d.similarityThreshold = threshold
	}
}

// SetCanonicalStrategy sets the strategy for choosing canonical versions
func (d *Deduplicator) SetCanonicalStrategy(strategy string) {
	validStrategies := []string{"freshest", "shortest", "longest", "highest_score"}
	for _, valid := range validStrategies {
		if strategy == valid {
			d.canonicalStrategy = strategy
			break
		}
	}
}

// GetDeduplicationStats returns statistics about the deduplication process
func (d *Deduplicator) GetDeduplicationStats(original, deduplicated []Candidate) DeduplicationStats {
	originalCount := len(original)
	deduplicatedCount := len(deduplicated)
	duplicatesFound := originalCount - deduplicatedCount

	// Calculate similarity scores for analysis
	var similarityScores []float64
	for i := 0; i < len(original)-1; i++ {
		for j := i + 1; j < len(original); j++ {
			similarity := d.calculateSimilarity(original[i], original[j])
			similarityScores = append(similarityScores, similarity)
		}
	}

	return DeduplicationStats{
		OriginalCount:     originalCount,
		DeduplicatedCount: deduplicatedCount,
		DuplicatesFound:   duplicatesFound,
		SimilarityScores:  similarityScores,
	}
}

// AnalyzeDuplicates analyzes potential duplicates in a candidate list
func (d *Deduplicator) AnalyzeDuplicates(candidates []Candidate) []DuplicateInfo {
	var duplicates []DuplicateInfo

	for i := 0; i < len(candidates)-1; i++ {
		for j := i + 1; j < len(candidates); j++ {
			similarity := d.calculateSimilarity(candidates[i], candidates[j])

			if similarity >= d.similarityThreshold {
				duplicateInfo := DuplicateInfo{
					Hash:        d.generateContentHash(candidates[i]),
					Similarity:  similarity,
					IsDuplicate: true,
					Canonical:   false,
					Reason:      "High similarity detected",
				}

				// Determine canonical version
				if d.isCanonical(candidates[i], candidates[j]) {
					duplicateInfo.Canonical = true
				}

				duplicates = append(duplicates, duplicateInfo)
			}
		}
	}

	return duplicates
}

// isCanonical determines if a candidate is canonical based on strategy
func (d *Deduplicator) isCanonical(candidate1, candidate2 Candidate) bool {
	switch d.canonicalStrategy {
	case "freshest":
		return candidate1.Modified.After(candidate2.Modified)
	case "shortest":
		return len(candidate1.Path) < len(candidate2.Path)
	case "longest":
		return len(candidate1.Path) > len(candidate2.Path)
	case "highest_score":
		return candidate1.RelevanceScore > candidate2.RelevanceScore
	default:
		return candidate1.Modified.After(candidate2.Modified) // Default to freshest
	}
}

// Helper functions

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// normalizeText normalizes text for comparison
func normalizeText(text string) string {
	// Convert to lowercase and remove extra whitespace
	normalized := strings.ToLower(text)
	normalized = strings.TrimSpace(normalized)
	normalized = strings.ReplaceAll(normalized, "\n", " ")
	normalized = strings.ReplaceAll(normalized, "\t", " ")

	// Remove multiple spaces
	for strings.Contains(normalized, "  ") {
		normalized = strings.ReplaceAll(normalized, "  ", " ")
	}

	return normalized
}

// calculateJaccardSimilarity calculates Jaccard similarity between two sets
func calculateJaccardSimilarity(set1, set2 map[string]bool) float64 {
	intersection := 0
	union := len(set1)

	for key := range set2 {
		if set1[key] {
			intersection++
		} else {
			union++
		}
	}

	if union == 0 {
		return 0.0
	}

	return float64(intersection) / float64(union)
}

// GetStats returns statistics about the Deduplicator algorithm
func (d *Deduplicator) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"similarity_threshold": d.similarityThreshold,
		"canonical_strategy":   d.canonicalStrategy,
	}
}
