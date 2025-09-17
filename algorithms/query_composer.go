package algorithms

import (
	"strings"
	"time"
)

// QueryComposer constructs optimal queries for highest-quality results
// Expands synonyms, boosts fields, and tunes parameters/filters
type QueryComposer struct {
	synonyms    map[string][]string
	fieldBoosts map[string]float64
	filters     map[string]interface{}
}

// NewQueryComposer creates a new QueryComposer instance
func NewQueryComposer() *QueryComposer {
	return &QueryComposer{
		synonyms: map[string][]string{
			"performance":    {"desempenho", "rendimento", "eficiencia"},
			"knowledge":      {"conhecimento", "sabedoria", "informacao"},
			"search":         {"busca", "pesquisa", "procura"},
			"algorithm":      {"algoritmo", "metodo", "tecnica"},
			"optimization":   {"otimizacao", "melhoria", "aperfeicoamento"},
			"analysis":       {"analise", "exame", "estudo"},
			"implementation": {"implementacao", "execucao", "desenvolvimento"},
			"integration":    {"integracao", "conexao", "vinculacao"},
		},
		fieldBoosts: map[string]float64{
			"name":    2.0, // Filename matches are most important
			"content": 1.0, // Content matches are baseline
			"path":    1.5, // Path matches are moderately important
			"tags":    1.8, // Tag matches are very important
		},
		filters: map[string]interface{}{
			"file_pattern": "*.md",
			"min_modified": time.Now().AddDate(0, 0, -30), // Last 30 days
		},
	}
}

// ComposeQuery processes a raw query and returns optimized query parameters
func (qc *QueryComposer) ComposeQuery(query string) map[string]interface{} {
	// Step 1: Tokenize query
	tokens := qc.tokenize(query)

	// Step 2: Expand synonyms
	expandedTokens := qc.expandSynonyms(tokens)

	// Step 3: Boost fields
	boostedQuery := qc.boostFields(expandedTokens)

	// Step 4: Add filters
	filters := qc.buildFilters()

	return map[string]interface{}{
		"query":   boostedQuery,
		"filters": filters,
		"tokens":  expandedTokens,
		"boost":   qc.fieldBoosts,
	}
}

// tokenize splits query into individual tokens
func (qc *QueryComposer) tokenize(query string) []string {
	// Simple tokenization - split by spaces and clean
	words := strings.Fields(strings.ToLower(query))
	var tokens []string

	for _, word := range words {
		// Remove punctuation and clean
		clean := strings.Trim(word, ".,!?;:")
		if len(clean) > 1 { // Ignore single characters
			tokens = append(tokens, clean)
		}
	}

	return tokens
}

// expandSynonyms expands query tokens with synonyms
func (qc *QueryComposer) expandSynonyms(tokens []string) []string {
	var expanded []string

	for _, token := range tokens {
		expanded = append(expanded, token) // Add original token

		// Add synonyms if available
		if synonyms, exists := qc.synonyms[token]; exists {
			expanded = append(expanded, synonyms...)
		}
	}

	return expanded
}

// boostFields applies field-specific boosting to the query
func (qc *QueryComposer) boostFields(tokens []string) map[string]interface{} {
	return map[string]interface{}{
		"tokens": tokens,
		"boosts": qc.fieldBoosts,
	}
}

// buildFilters constructs filter parameters
func (qc *QueryComposer) buildFilters() map[string]interface{} {
	return map[string]interface{}{
		"file_pattern": qc.filters["file_pattern"],
		"min_modified": qc.filters["min_modified"],
		"max_results":  100, // Limit results for performance
	}
}

// AddCustomSynonym adds a custom synonym mapping
func (qc *QueryComposer) AddCustomSynonym(term string, synonyms []string) {
	qc.synonyms[term] = synonyms
}

// SetFieldBoost adjusts the boost value for a specific field
func (qc *QueryComposer) SetFieldBoost(field string, boost float64) {
	qc.fieldBoosts[field] = boost
}

// GetQueryStats returns statistics about the composed query
func (qc *QueryComposer) GetQueryStats(query string) map[string]interface{} {
	composed := qc.ComposeQuery(query)
	tokens := composed["tokens"].([]string)

	return map[string]interface{}{
		"original_query":  query,
		"token_count":     len(tokens),
		"expanded_tokens": tokens,
		"field_boosts":    qc.fieldBoosts,
		"filters":         composed["filters"],
	}
}

// GetExpandedQuery returns the expanded query string
func (qc *QueryComposer) GetExpandedQuery() string {
	// This is a simplified implementation
	// In a real implementation, this would return the expanded query
	return "expanded query"
}

// GetStats returns general statistics about the QueryComposer
func (qc *QueryComposer) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"synonyms_count": len(qc.synonyms),
		"field_boosts":   qc.fieldBoosts,
		"filters":        qc.filters,
	}
}
