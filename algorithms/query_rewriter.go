package algorithms

import (
	"strings"
	"time"
)

// QueryRewriter automatically refines queries with expansions, corrections, and alternatives
type QueryRewriter struct {
	synonyms    map[string][]string
	corrections map[string]string
	expansions  map[string][]string
	language    string
	stats       RewriteStats
}

// RewriteStats tracks query rewriting statistics
type RewriteStats struct {
	TotalRewrites      int           `json:"total_rewrites"`
	SuccessfulRewrites int           `json:"successful_rewrites"`
	AverageTime        time.Duration `json:"average_time"`
	SynonymMatches     int           `json:"synonym_matches"`
	CorrectionMatches  int           `json:"correction_matches"`
	ExpansionMatches   int           `json:"expansion_matches"`
}

// RewriteResult represents the result of query rewriting
type RewriteResult struct {
	OriginalQuery  string   `json:"original_query"`
	RewrittenQuery string   `json:"rewritten_query"`
	Confidence     float64  `json:"confidence"`
	Changes        []string `json:"changes"`
	Reason         string   `json:"reason"`
}

// NewQueryRewriter creates a new QueryRewriter instance
func NewQueryRewriter(language string) *QueryRewriter {
	qr := &QueryRewriter{
		synonyms:    make(map[string][]string),
		corrections: make(map[string]string),
		expansions:  make(map[string][]string),
		language:    language,
		stats:       RewriteStats{},
	}

	// Initialize with default data
	qr.initializeDefaultData()

	return qr
}

// initializeDefaultData initializes the rewriter with default synonym and correction data
func (qr *QueryRewriter) initializeDefaultData() {
	// Portuguese synonyms
	qr.synonyms["ciencia"] = []string{"science", "ciência", "conhecimento", "saber"}
	qr.synonyms["dados"] = []string{"data", "informação", "informacoes", "dados"}
	qr.synonyms["logica"] = []string{"logic", "lógica", "raciocínio", "raciocinio"}
	qr.synonyms["profissional"] = []string{"professional", "trabalho", "carreira", "ocupação"}
	qr.synonyms["conhecimento"] = []string{"knowledge", "saber", "ciência", "ciencia"}
	qr.synonyms["agents"] = []string{"agentes", "agentes", "automação", "automatizacao"}

	// English synonyms
	qr.synonyms["science"] = []string{"ciência", "ciencia", "knowledge", "research"}
	qr.synonyms["data"] = []string{"dados", "information", "informação", "facts"}
	qr.synonyms["logic"] = []string{"lógica", "logica", "reasoning", "rational"}
	qr.synonyms["professional"] = []string{"profissional", "career", "work", "business"}
	qr.synonyms["knowledge"] = []string{"conhecimento", "saber", "science", "ciência"}
	qr.synonyms["agents"] = []string{"agentes", "automation", "ai", "artificial intelligence"}

	// Common typos and corrections
	qr.corrections["ciencia"] = "ciência"
	qr.corrections["logica"] = "lógica"
	qr.corrections["profissional"] = "profissional"
	qr.corrections["conhecimento"] = "conhecimento"
	qr.corrections["informacao"] = "informação"
	qr.corrections["informacoes"] = "informações"
	qr.corrections["raciocinio"] = "raciocínio"
	qr.corrections["automatizacao"] = "automação"

	// Expansions for common terms
	qr.expansions["ciencia"] = []string{"ciência", "science", "conhecimento científico", "pesquisa científica"}
	qr.expansions["dados"] = []string{"data", "informação", "dados estruturados", "big data"}
	qr.expansions["logica"] = []string{"lógica", "logic", "raciocínio lógico", "pensamento lógico"}
	qr.expansions["profissional"] = []string{"professional", "carreira profissional", "desenvolvimento profissional"}
	qr.expansions["conhecimento"] = []string{"knowledge", "saber", "conhecimento técnico", "conhecimento prático"}
}

// RewriteQuery rewrites a query with expansions, corrections, and alternatives
func (qr *QueryRewriter) RewriteQuery(query string) *RewriteResult {
	startTime := time.Now()

	originalQuery := query
	rewrittenQuery := query
	var changes []string
	confidence := 1.0
	reason := "no changes needed"

	// Tokenize query
	tokens := qr.tokenizeQuery(query)

	// Apply corrections first
	correctedTokens := qr.applyCorrections(tokens)
	if len(correctedTokens) != len(tokens) || !qr.tokensEqual(tokens, correctedTokens) {
		rewrittenQuery = strings.Join(correctedTokens, " ")
		changes = append(changes, "applied corrections")
		confidence = 0.9
		reason = "applied spelling corrections"
		tokens = correctedTokens
	}

	// Apply synonym expansion
	expandedTokens := qr.applySynonymExpansion(tokens)
	if len(expandedTokens) > len(tokens) {
		rewrittenQuery = strings.Join(expandedTokens, " ")
		changes = append(changes, "applied synonym expansion")
		confidence = 0.8
		reason = "expanded with synonyms"
		tokens = expandedTokens
	}

	// Apply term expansion
	expandedQuery := qr.applyTermExpansion(rewrittenQuery)
	if expandedQuery != rewrittenQuery {
		rewrittenQuery = expandedQuery
		changes = append(changes, "applied term expansion")
		confidence = 0.7
		reason = "expanded with related terms"
	}

	// Update statistics
	qr.updateStats(time.Since(startTime), len(changes) > 0)

	return &RewriteResult{
		OriginalQuery:  originalQuery,
		RewrittenQuery: rewrittenQuery,
		Confidence:     confidence,
		Changes:        changes,
		Reason:         reason,
	}
}

// tokenizeQuery tokenizes the query into terms
func (qr *QueryRewriter) tokenizeQuery(query string) []string {
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

// applyCorrections applies spelling corrections to tokens
func (qr *QueryRewriter) applyCorrections(tokens []string) []string {
	corrected := make([]string, len(tokens))

	for i, token := range tokens {
		if correction, exists := qr.corrections[token]; exists {
			corrected[i] = correction
		} else {
			corrected[i] = token
		}
	}

	return corrected
}

// applySynonymExpansion applies synonym expansion to tokens
func (qr *QueryRewriter) applySynonymExpansion(tokens []string) []string {
	var expanded []string

	for _, token := range tokens {
		expanded = append(expanded, token)

		if synonyms, exists := qr.synonyms[token]; exists {
			// Add first few synonyms
			for i, synonym := range synonyms {
				if i < 2 { // Limit to 2 synonyms per term
					expanded = append(expanded, synonym)
				}
			}
		}
	}

	return expanded
}

// applyTermExpansion applies term expansion to the query
func (qr *QueryRewriter) applyTermExpansion(query string) string {
	tokens := qr.tokenizeQuery(query)
	var expanded []string

	for _, token := range tokens {
		expanded = append(expanded, token)

		if expansions, exists := qr.expansions[token]; exists {
			// Add first expansion
			if len(expansions) > 0 {
				expanded = append(expanded, expansions[0])
			}
		}
	}

	return strings.Join(expanded, " ")
}

// tokensEqual checks if two token slices are equal
func (qr *QueryRewriter) tokensEqual(tokens1, tokens2 []string) bool {
	if len(tokens1) != len(tokens2) {
		return false
	}

	for i, token := range tokens1 {
		if token != tokens2[i] {
			return false
		}
	}

	return true
}

// updateStats updates the rewriting statistics
func (qr *QueryRewriter) updateStats(duration time.Duration, successful bool) {
	qr.stats.TotalRewrites++

	if successful {
		qr.stats.SuccessfulRewrites++
	}

	// Update average time
	totalTime := qr.stats.AverageTime * time.Duration(qr.stats.TotalRewrites-1)
	qr.stats.AverageTime = (totalTime + duration) / time.Duration(qr.stats.TotalRewrites)
}

// AddSynonym adds a synonym to the rewriter
func (qr *QueryRewriter) AddSynonym(term string, synonyms []string) {
	qr.synonyms[term] = synonyms
}

// AddCorrection adds a correction to the rewriter
func (qr *QueryRewriter) AddCorrection(incorrect, correct string) {
	qr.corrections[incorrect] = correct
}

// AddExpansion adds an expansion to the rewriter
func (qr *QueryRewriter) AddExpansion(term string, expansions []string) {
	qr.expansions[term] = expansions
}

// GetStats returns the current rewriting statistics
func (qr *QueryRewriter) GetStats() RewriteStats {
	return qr.stats
}

// ResetStats resets the rewriting statistics
func (qr *QueryRewriter) ResetStats() {
	qr.stats = RewriteStats{}
}
