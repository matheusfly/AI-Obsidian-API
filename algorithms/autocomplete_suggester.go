package algorithms

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"sort"
	"strings"
	"time"
)

// TrieNode represents a node in the trie data structure
type TrieNode struct {
	Children map[rune]*TrieNode
	IsEnd    bool
	Freq     int
	Modified time.Time
	Paths    []string // File paths containing this term
}

// AutocompleteSuggester provides type-ahead suggestions by scanning vault metadata
type AutocompleteSuggester struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
	trie       *TrieNode
	cache      map[string][]string
	lastUpdate time.Time
	cacheTTL   time.Duration
}

// Suggestion represents an autocomplete suggestion
type Suggestion struct {
	Text     string    `json:"text"`
	Score    float64   `json:"score"`
	Freq     int       `json:"freq"`
	Modified time.Time `json:"modified"`
	Paths    []string  `json:"paths"`
}

// NewAutocompleteSuggester creates a new AutocompleteSuggester instance
func NewAutocompleteSuggester(apiKey, baseURL string) *AutocompleteSuggester {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	return &AutocompleteSuggester{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Transport: tr, Timeout: 30 * time.Second},
		trie:       &TrieNode{Children: make(map[rune]*TrieNode)},
		cache:      make(map[string][]string),
		cacheTTL:   5 * time.Minute,
	}
}

// BuildTrie builds a prefix tree from vault metadata
func (as *AutocompleteSuggester) BuildTrie() error {
	// Check cache first
	if time.Since(as.lastUpdate) < as.cacheTTL && as.trie != nil {
		return nil
	}

	// Fetch vault listing
	files, err := as.getVaultFiles()
	if err != nil {
		return fmt.Errorf("failed to get vault files: %w", err)
	}

	// Reset trie
	as.trie = &TrieNode{Children: make(map[rune]*TrieNode)}

	// Build trie from file metadata
	for _, file := range files {
		if err := as.indexFile(file); err != nil {
			continue // Skip files that can't be indexed
		}
	}

	as.lastUpdate = time.Now()
	return nil
}

// indexFile indexes a single file in the trie
func (as *AutocompleteSuggester) indexFile(filePath string) error {
	// Extract filename and path components
	fileName := strings.TrimSuffix(filePath, ".md")
	pathParts := strings.Split(filePath, "/")

	// Index filename
	as.insertTerm(fileName, filePath)

	// Index path components
	for _, part := range pathParts {
		if part != "" && part != ".md" {
			as.insertTerm(part, filePath)
		}
	}

	// Try to get file content for tag extraction
	content, err := as.getFileContent(filePath)
	if err != nil {
		return err
	}

	// Extract tags from content
	tags := as.extractTags(content)
	for _, tag := range tags {
		as.insertTerm(tag, filePath)
	}

	return nil
}

// insertTerm inserts a term into the trie
func (as *AutocompleteSuggester) insertTerm(term, filePath string) {
	term = strings.ToLower(term)
	node := as.trie

	for _, ch := range term {
		if node.Children[ch] == nil {
			node.Children[ch] = &TrieNode{Children: make(map[rune]*TrieNode)}
		}
		node = node.Children[ch]
	}

	node.IsEnd = true
	node.Freq++
	node.Paths = append(node.Paths, filePath)

	// Update modification time (simplified - use current time)
	node.Modified = time.Now()
}

// extractTags extracts tags from markdown content
func (as *AutocompleteSuggester) extractTags(content string) []string {
	var tags []string
	lines := strings.Split(content, "\n")

	for _, line := range lines {
		line = strings.TrimSpace(line)
		// Look for #tag patterns
		if strings.HasPrefix(line, "#") {
			tag := strings.TrimPrefix(line, "#")
			tag = strings.TrimSpace(tag)
			if tag != "" {
				tags = append(tags, tag)
			}
		}
	}

	return tags
}

// GetSuggestions returns autocomplete suggestions for a prefix
func (as *AutocompleteSuggester) GetSuggestions(prefix string, limit int) ([]Suggestion, error) {
	// Check cache first
	if cached, exists := as.cache[prefix]; exists && time.Since(as.lastUpdate) < as.cacheTTL {
		suggestions := make([]Suggestion, len(cached))
		for i, text := range cached {
			suggestions[i] = Suggestion{Text: text, Score: 1.0}
		}
		return suggestions, nil
	}

	// Build trie if needed
	if err := as.BuildTrie(); err != nil {
		return nil, fmt.Errorf("failed to build trie: %w", err)
	}

	// Find suggestions
	suggestions := as.findSuggestions(prefix, limit)

	// Cache results
	cached := make([]string, len(suggestions))
	for i, suggestion := range suggestions {
		cached[i] = suggestion.Text
	}
	as.cache[prefix] = cached

	return suggestions, nil
}

// findSuggestions finds suggestions starting with the given prefix
func (as *AutocompleteSuggester) findSuggestions(prefix string, limit int) []Suggestion {
	prefix = strings.ToLower(prefix)
	node := as.trie

	// Navigate to prefix node
	for _, ch := range prefix {
		if node.Children[ch] == nil {
			return []Suggestion{} // No suggestions for this prefix
		}
		node = node.Children[ch]
	}

	// Collect all words from this node
	var suggestions []Suggestion
	as.collectSuggestions(node, prefix, &suggestions)

	// Sort by score (frequency * freshness)
	sort.Slice(suggestions, func(i, j int) bool {
		return suggestions[i].Score > suggestions[j].Score
	})

	// Limit results
	if len(suggestions) > limit {
		suggestions = suggestions[:limit]
	}

	return suggestions
}

// collectSuggestions recursively collects suggestions from trie nodes
func (as *AutocompleteSuggester) collectSuggestions(node *TrieNode, current string, suggestions *[]Suggestion) {
	if node.IsEnd {
		// Calculate score based on frequency and freshness
		freshness := 1.0
		if !node.Modified.IsZero() {
			hoursSinceModified := time.Since(node.Modified).Hours()
			freshness = 1.0 / (1.0 + hoursSinceModified/24.0) // Decay over days
		}

		score := float64(node.Freq) * freshness

		*suggestions = append(*suggestions, Suggestion{
			Text:     current,
			Score:    score,
			Freq:     node.Freq,
			Modified: node.Modified,
			Paths:    node.Paths,
		})
	}

	// Recursively collect from children
	for ch, child := range node.Children {
		as.collectSuggestions(child, current+string(ch), suggestions)
	}
}

// getVaultFiles gets all files from the vault
func (as *AutocompleteSuggester) getVaultFiles() ([]string, error) {
	url := as.baseURL + "/vault/"
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+as.apiKey)
	resp, err := as.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	var response struct {
		Files []string `json:"files"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	return response.Files, nil
}

// getFileContent gets the content of a specific file
func (as *AutocompleteSuggester) getFileContent(filePath string) (string, error) {
	url := as.baseURL + "/vault/" + filePath
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+as.apiKey)
	resp, err := as.httpClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("file request failed with status %d", resp.StatusCode)
	}

	var fileResponse struct {
		Content string `json:"content"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&fileResponse); err != nil {
		return "", fmt.Errorf("failed to decode file response: %w", err)
	}

	return fileResponse.Content, nil
}

// GetStats returns statistics about the AutocompleteSuggester
func (as *AutocompleteSuggester) GetStats() map[string]interface{} {
	return map[string]interface{}{
		"cache_size":  len(as.cache),
		"last_update": as.lastUpdate,
		"cache_ttl":   as.cacheTTL,
		"trie_built":  as.trie != nil,
	}
}

// ClearCache clears the suggestion cache
func (as *AutocompleteSuggester) ClearCache() {
	as.cache = make(map[string][]string)
	as.trie = &TrieNode{Children: make(map[rune]*TrieNode)}
	as.lastUpdate = time.Time{}
}
