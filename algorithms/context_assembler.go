package algorithms

import (
	"fmt"
	"strings"
	"time"
)

// ContextAssembler assembles final context within token budget
// Selects snippets + provenance for LLM prompt
type ContextAssembler struct {
	maxTokens        int
	chunkSize        int
	provenanceFormat string
	priorityOrder    []string
}

// ContextChunk represents a chunk of content with metadata
type ContextChunk struct {
	Content     string
	Source      string
	Modified    time.Time
	Score       float64
	TokenCount  int
	ChunkIndex  int
	TotalChunks int
}

// AssembledContext represents the final assembled context
type AssembledContext struct {
	Content         string
	TokenCount      int
	ChunkCount      int
	Sources         []string
	Provenance      []ContextChunk
	BudgetUsed      float64
	BudgetRemaining int
}

// NewContextAssembler creates a new ContextAssembler instance
func NewContextAssembler() *ContextAssembler {
	return &ContextAssembler{
		maxTokens:        4000, // Default token budget
		chunkSize:        500,  // Default chunk size in tokens
		provenanceFormat: "[Source: %s, modified: %s, score: %.2f]",
		priorityOrder:    []string{"filename", "path", "content"},
	}
}

// AssembleContext assembles context from ranked candidates within token budget
func (ca *ContextAssembler) AssembleContext(candidates []Candidate, query string) AssembledContext {
	if len(candidates) == 0 {
		return AssembledContext{
			Content:         "",
			TokenCount:      0,
			ChunkCount:      0,
			Sources:         []string{},
			Provenance:      []ContextChunk{},
			BudgetUsed:      0.0,
			BudgetRemaining: ca.maxTokens,
		}
	}

	var contextChunks []ContextChunk
	var sources []string
	totalTokens := 0

	// Step 1: Process candidates in priority order
	for _, candidate := range candidates {
		if totalTokens >= ca.maxTokens {
			break // Budget exhausted
		}

		// Create chunks from candidate content
		chunks := ca.createChunksFromCandidate(candidate, query)

		// Add chunks that fit within budget
		for _, chunk := range chunks {
			if totalTokens+chunk.TokenCount <= ca.maxTokens {
				contextChunks = append(contextChunks, chunk)
				totalTokens += chunk.TokenCount

				// Add source if not already present
				if !containsString(sources, chunk.Source) {
					sources = append(sources, chunk.Source)
				}
			} else {
				break // Budget exceeded
			}
		}
	}

	// Step 2: Assemble final context
	content := ca.buildContextContent(contextChunks)

	// Step 3: Calculate budget usage
	budgetUsed := float64(totalTokens) / float64(ca.maxTokens) * 100.0
	budgetRemaining := ca.maxTokens - totalTokens

	return AssembledContext{
		Content:         content,
		TokenCount:      totalTokens,
		ChunkCount:      len(contextChunks),
		Sources:         sources,
		Provenance:      contextChunks,
		BudgetUsed:      budgetUsed,
		BudgetRemaining: budgetRemaining,
	}
}

// createChunksFromCandidate creates chunks from a candidate
func (ca *ContextAssembler) createChunksFromCandidate(candidate Candidate, query string) []ContextChunk {
	var chunks []ContextChunk

	// Determine content to chunk based on match type
	var content string
	var source string

	switch candidate.MatchType {
	case "filename":
		content = fmt.Sprintf("File: %s\nPath: %s", candidate.Name, candidate.Path)
		source = candidate.Path
	case "path":
		content = fmt.Sprintf("Path: %s\nFile: %s", candidate.Path, candidate.Name)
		source = candidate.Path
	case "content":
		content = candidate.Content
		source = candidate.Path
	default:
		content = fmt.Sprintf("File: %s\nPath: %s\nContent: %s",
			candidate.Name, candidate.Path, candidate.Content)
		source = candidate.Path
	}

	// Split content into chunks
	textChunks := ca.splitIntoChunks(content, ca.chunkSize)

	for i, textChunk := range textChunks {
		tokenCount := ca.estimateTokenCount(textChunk)

		chunk := ContextChunk{
			Content:     textChunk,
			Source:      source,
			Modified:    candidate.Modified,
			Score:       candidate.RelevanceScore,
			TokenCount:  tokenCount,
			ChunkIndex:  i + 1,
			TotalChunks: len(textChunks),
		}

		chunks = append(chunks, chunk)
	}

	return chunks
}

// splitIntoChunks splits text into chunks of specified token size
func (ca *ContextAssembler) splitIntoChunks(text string, maxTokens int) []string {
	if len(text) == 0 {
		return []string{}
	}

	// Simple word-based chunking
	words := strings.Fields(text)
	var chunks []string
	var currentChunk []string
	currentTokens := 0

	for _, word := range words {
		wordTokens := ca.estimateTokenCount(word)

		if currentTokens+wordTokens > maxTokens && len(currentChunk) > 0 {
			// Start new chunk
			chunks = append(chunks, strings.Join(currentChunk, " "))
			currentChunk = []string{word}
			currentTokens = wordTokens
		} else {
			currentChunk = append(currentChunk, word)
			currentTokens += wordTokens
		}
	}

	// Add remaining chunk
	if len(currentChunk) > 0 {
		chunks = append(chunks, strings.Join(currentChunk, " "))
	}

	return chunks
}

// buildContextContent builds the final context content with provenance
func (ca *ContextAssembler) buildContextContent(chunks []ContextChunk) string {
	if len(chunks) == 0 {
		return ""
	}

	var content strings.Builder

	// Add header
	content.WriteString("# Search Results Context\n\n")
	content.WriteString(fmt.Sprintf("Query processed with %d chunks from %d sources\n\n",
		len(chunks), len(getUniqueSources(chunks))))

	// Add chunks with provenance
	for i, chunk := range chunks {
		provenance := fmt.Sprintf(ca.provenanceFormat,
			chunk.Source,
			chunk.Modified.Format("2006-01-02 15:04:05"),
			chunk.Score)

		content.WriteString(fmt.Sprintf("## Chunk %d/%d\n", chunk.ChunkIndex, chunk.TotalChunks))
		content.WriteString(fmt.Sprintf("%s\n\n", provenance))
		content.WriteString(chunk.Content)
		content.WriteString("\n\n---\n\n")

		// Add separator between chunks
		if i < len(chunks)-1 {
			content.WriteString("\n")
		}
	}

	// Add footer
	content.WriteString(fmt.Sprintf("\n*Context assembled with %d tokens from %d sources*",
		ca.calculateTotalTokens(chunks), len(getUniqueSources(chunks))))

	return content.String()
}

// estimateTokenCount estimates token count for text (rough approximation)
func (ca *ContextAssembler) estimateTokenCount(text string) int {
	// Rough estimation: 1 token ≈ 4 characters for English text
	// This is a simplified approximation
	charCount := len(text)
	tokenCount := charCount / 4

	// Minimum of 1 token
	if tokenCount < 1 {
		tokenCount = 1
	}

	return tokenCount
}

// calculateTotalTokens calculates total tokens across all chunks
func (ca *ContextAssembler) calculateTotalTokens(chunks []ContextChunk) int {
	total := 0
	for _, chunk := range chunks {
		total += chunk.TokenCount
	}
	return total
}

// SetMaxTokens sets the maximum token budget
func (ca *ContextAssembler) SetMaxTokens(maxTokens int) {
	if maxTokens > 0 {
		ca.maxTokens = maxTokens
	}
}

// SetChunkSize sets the chunk size in tokens
func (ca *ContextAssembler) SetChunkSize(chunkSize int) {
	if chunkSize > 0 {
		ca.chunkSize = chunkSize
	}
}

// SetProvenanceFormat sets the format for provenance information
func (ca *ContextAssembler) SetProvenanceFormat(format string) {
	ca.provenanceFormat = format
}

// GetContextStats returns statistics about the context assembly
func (ca *ContextAssembler) GetContextStats(context AssembledContext) map[string]interface{} {
	return map[string]interface{}{
		"token_count":      context.TokenCount,
		"chunk_count":      context.ChunkCount,
		"source_count":     len(context.Sources),
		"budget_used":      context.BudgetUsed,
		"budget_remaining": context.BudgetRemaining,
		"max_tokens":       ca.maxTokens,
		"chunk_size":       ca.chunkSize,
		"efficiency":       ca.calculateEfficiency(context),
	}
}

// calculateEfficiency calculates the efficiency of context assembly
func (ca *ContextAssembler) calculateEfficiency(context AssembledContext) float64 {
	if context.TokenCount == 0 {
		return 0.0
	}

	// Efficiency = (useful tokens / total tokens) * 100
	// This is a simplified calculation
	return float64(context.TokenCount) / float64(ca.maxTokens) * 100.0
}

// OptimizeContext optimizes context assembly for better results
func (ca *ContextAssembler) OptimizeContext(candidates []Candidate, query string) AssembledContext {
	// Sort candidates by relevance score (highest first)
	ca.sortCandidatesByScore(candidates)

	// Assemble context with optimized parameters
	return ca.AssembleContext(candidates, query)
}

// sortCandidatesByScore sorts candidates by relevance score
func (ca *ContextAssembler) sortCandidatesByScore(candidates []Candidate) {
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

// Helper functions

// containsString checks if a slice contains a string
func containsString(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

// getUniqueSources gets unique sources from chunks
func getUniqueSources(chunks []ContextChunk) []string {
	var sources []string
	seen := make(map[string]bool)

	for _, chunk := range chunks {
		if !seen[chunk.Source] {
			sources = append(sources, chunk.Source)
			seen[chunk.Source] = true
		}
	}

	return sources
}

// truncateText truncates text to fit within token limit
func (ca *ContextAssembler) truncateText(text string, maxTokens int) string {
	if ca.estimateTokenCount(text) <= maxTokens {
		return text
	}

	// Simple truncation - keep first part
	words := strings.Fields(text)
	var truncated []string
	currentTokens := 0

	for _, word := range words {
		wordTokens := ca.estimateTokenCount(word)
		if currentTokens+wordTokens > maxTokens {
			break
		}
		truncated = append(truncated, word)
		currentTokens += wordTokens
	}

	return strings.Join(truncated, " ") + "..."
}

// GetStats returns statistics about the ContextAssembler algorithm
func (ca *ContextAssembler) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"max_tokens":        ca.maxTokens,
		"chunk_size":        ca.chunkSize,
		"provenance_format": ca.provenanceFormat,
	}
}
