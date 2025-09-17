package algorithms

import (
	"math"
	"regexp"
	"strings"
	"time"
)

// MetadataBoost boosts scores using metadata (tag, path, updated_at)
// Prioritizes fresh/relevant files
type MetadataBoost struct {
	pathPatterns    map[string]float64
	tagBoosts       map[string]float64
	freshnessWeight float64
	pathWeight      float64
	tagWeight       float64
}

// BoostConfig represents configuration for metadata boosting
type BoostConfig struct {
	PathPatterns    map[string]float64
	TagBoosts       map[string]float64
	FreshnessWeight float64
	PathWeight      float64
	TagWeight       float64
	MaxAge          time.Duration
}

// NewMetadataBoost creates a new MetadataBoost instance
func NewMetadataBoost() *MetadataBoost {
	return &MetadataBoost{
		pathPatterns: map[string]float64{
			"docs/":      1.5, // Documentation files
			"guides/":    1.8, // Guide files
			"tutorials/": 1.7, // Tutorial files
			"examples/":  1.3, // Example files
			"src/":       1.2, // Source code
			"api/":       1.6, // API documentation
			"README":     2.0, // README files
			"CHANGELOG":  1.4, // Changelog files
			"LICENSE":    0.5, // License files (lower priority)
			"test":       0.8, // Test files (lower priority)
		},
		tagBoosts: map[string]float64{
			"important":     2.0,
			"critical":      2.5,
			"urgent":        2.2,
			"documentation": 1.8,
			"guide":         1.7,
			"tutorial":      1.6,
			"example":       1.4,
			"api":           1.6,
			"reference":     1.5,
			"deprecated":    0.3,
			"obsolete":      0.2,
		},
		freshnessWeight: 1.0,
		pathWeight:      1.0,
		tagWeight:       1.0,
	}
}

// BoostCandidates applies metadata boosting to candidates
func (mb *MetadataBoost) BoostCandidates(candidates []Candidate, query string) []Candidate {
	if len(candidates) == 0 {
		return candidates
	}

	// Calculate base scores if not already set
	for i := range candidates {
		if candidates[i].RelevanceScore == 0 {
			candidates[i].RelevanceScore = candidates[i].MatchScore
		}
	}

	// Apply metadata boosting
	for i := range candidates {
		boost := mb.calculateMetadataBoost(&candidates[i], query)
		candidates[i].RelevanceScore += boost
	}

	// Sort by boosted score (descending)
	mb.sortCandidatesByBoostedScore(candidates)

	return candidates
}

// GetStats returns statistics about the MetadataBoost algorithm
func (mb *MetadataBoost) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"freshness_weight": mb.freshnessWeight,
		"path_weight":      mb.pathWeight,
		"tag_weight":       mb.tagWeight,
	}
}

// calculateMetadataBoost calculates the metadata boost for a candidate
func (mb *MetadataBoost) calculateMetadataBoost(candidate *Candidate, query string) float64 {
	boost := 0.0

	// Path-based boosting
	pathBoost := mb.calculatePathBoost(candidate.Path)
	boost += pathBoost * mb.pathWeight

	// Tag-based boosting
	tagBoost := mb.calculateTagBoost(candidate.Metadata, query)
	boost += tagBoost * mb.tagWeight

	// Freshness boosting
	freshnessBoost := mb.calculateFreshnessBoost(candidate.Modified)
	boost += freshnessBoost * mb.freshnessWeight

	return boost
}

// calculatePathBoost calculates boost based on file path patterns
func (mb *MetadataBoost) calculatePathBoost(path string) float64 {
	pathLower := strings.ToLower(path)

	// Check for exact pattern matches
	for pattern, boost := range mb.pathPatterns {
		if strings.Contains(pathLower, strings.ToLower(pattern)) {
			return boost
		}
	}

	// Check for filename patterns
	filename := extractFilename(path)
	for pattern, boost := range mb.pathPatterns {
		if strings.Contains(strings.ToLower(filename), strings.ToLower(pattern)) {
			return boost
		}
	}

	// Default boost for unmatched paths
	return 1.0
}

// calculateTagBoost calculates boost based on tags and metadata
func (mb *MetadataBoost) calculateTagBoost(metadata map[string]interface{}, query string) float64 {
	boost := 0.0

	// Check for explicit tags
	if tags, exists := metadata["tags"]; exists {
		if tagList, ok := tags.([]string); ok {
			for _, tag := range tagList {
				if tagBoost, exists := mb.tagBoosts[strings.ToLower(tag)]; exists {
					boost += tagBoost
				}
			}
		} else if tagStr, ok := tags.(string); ok {
			// Handle comma-separated tags
			tagParts := strings.Split(tagStr, ",")
			for _, tag := range tagParts {
				tag = strings.TrimSpace(tag)
				if tagBoost, exists := mb.tagBoosts[strings.ToLower(tag)]; exists {
					boost += tagBoost
				}
			}
		}
	}

	// Check for query-relevant tags
	queryLower := strings.ToLower(query)
	for tag, tagBoost := range mb.tagBoosts {
		if strings.Contains(queryLower, tag) {
			boost += tagBoost * 0.5 // Partial boost for query relevance
		}
	}

	return boost
}

// calculateFreshnessBoost calculates boost based on file modification time
func (mb *MetadataBoost) calculateFreshnessBoost(modified time.Time) float64 {
	if modified.IsZero() {
		return 0.0
	}

	now := time.Now()
	age := now.Sub(modified)

	// Calculate freshness score (1.0 for very recent, decreasing with age)
	daysOld := age.Hours() / 24

	// Exponential decay: score = e^(-age/365) for 1-year half-life
	freshnessScore := math.Exp(-daysOld / 365.0)

	// Cap the boost at 1.0
	if freshnessScore > 1.0 {
		freshnessScore = 1.0
	}

	return freshnessScore
}

// sortCandidatesByBoostedScore sorts candidates by boosted relevance score
func (mb *MetadataBoost) sortCandidatesByBoostedScore(candidates []Candidate) {
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

// SetBoostConfig allows customization of boost parameters
func (mb *MetadataBoost) SetBoostConfig(config BoostConfig) {
	if config.PathPatterns != nil {
		mb.pathPatterns = config.PathPatterns
	}
	if config.TagBoosts != nil {
		mb.tagBoosts = config.TagBoosts
	}
	if config.FreshnessWeight > 0 {
		mb.freshnessWeight = config.FreshnessWeight
	}
	if config.PathWeight > 0 {
		mb.pathWeight = config.PathWeight
	}
	if config.TagWeight > 0 {
		mb.tagWeight = config.TagWeight
	}
}

// AddPathPattern adds a custom path pattern with boost value
func (mb *MetadataBoost) AddPathPattern(pattern string, boost float64) {
	mb.pathPatterns[pattern] = boost
}

// AddTagBoost adds a custom tag with boost value
func (mb *MetadataBoost) AddTagBoost(tag string, boost float64) {
	mb.tagBoosts[strings.ToLower(tag)] = boost
}

// GetBoostStats returns statistics about the boosting process
func (mb *MetadataBoost) GetBoostStats(candidates []Candidate) map[string]interface{} {
	if len(candidates) == 0 {
		return map[string]interface{}{
			"candidate_count": 0,
			"avg_boost":       0.0,
			"max_boost":       0.0,
		}
	}

	totalBoost := 0.0
	maxBoost := 0.0

	for _, candidate := range candidates {
		// Calculate individual boost
		boost := mb.calculateMetadataBoost(&candidate, "")
		totalBoost += boost

		if boost > maxBoost {
			maxBoost = boost
		}
	}

	avgBoost := totalBoost / float64(len(candidates))

	return map[string]interface{}{
		"candidate_count": len(candidates),
		"avg_boost":       avgBoost,
		"max_boost":       maxBoost,
		"total_boost":     totalBoost,
		"path_patterns":   len(mb.pathPatterns),
		"tag_boosts":      len(mb.tagBoosts),
		"weights": map[string]float64{
			"freshness": mb.freshnessWeight,
			"path":      mb.pathWeight,
			"tag":       mb.tagWeight,
		},
	}
}

// CalculateRelevanceScore calculates a comprehensive relevance score
func (mb *MetadataBoost) CalculateRelevanceScore(candidate *Candidate, query string) float64 {
	// Start with base match score
	score := candidate.MatchScore

	// Add metadata boost
	boost := mb.calculateMetadataBoost(candidate, query)
	score += boost

	// Apply query-specific adjustments
	queryAdjustment := mb.calculateQueryAdjustment(candidate, query)
	score += queryAdjustment

	return score
}

// calculateQueryAdjustment calculates query-specific score adjustments
func (mb *MetadataBoost) calculateQueryAdjustment(candidate *Candidate, query string) float64 {
	adjustment := 0.0
	queryLower := strings.ToLower(query)

	// Boost for exact filename matches
	if strings.Contains(strings.ToLower(candidate.Name), queryLower) {
		adjustment += 0.5
	}

	// Boost for path matches
	if strings.Contains(strings.ToLower(candidate.Path), queryLower) {
		adjustment += 0.3
	}

	// Boost for content matches (if available)
	if len(candidate.Content) > 0 && strings.Contains(strings.ToLower(candidate.Content), queryLower) {
		adjustment += 0.2
	}

	return adjustment
}

// Helper functions

// extractFilename extracts the filename from a path
func extractFilename(path string) string {
	if idx := strings.LastIndex(path, "/"); idx != -1 {
		return path[idx+1:]
	}
	if idx := strings.LastIndex(path, "\\"); idx != -1 {
		return path[idx+1:]
	}
	return path
}

// isRecentFile checks if a file was modified recently
func isRecentFile(modified time.Time, threshold time.Duration) bool {
	if modified.IsZero() {
		return false
	}

	return time.Since(modified) < threshold
}

// getFileType returns the file type based on extension
func getFileType(filename string) string {
	if idx := strings.LastIndex(filename, "."); idx != -1 && idx < len(filename)-1 {
		return strings.ToLower(filename[idx+1:])
	}
	return "unknown"
}

// matchesPattern checks if text matches a regex pattern
func matchesPattern(text, pattern string) bool {
	matched, err := regexp.MatchString(pattern, text)
	return err == nil && matched
}
