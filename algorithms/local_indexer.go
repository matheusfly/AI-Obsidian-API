package algorithms

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// LocalIndexer builds a persistent local index from vault data for sub-second queries
type LocalIndexer struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
	indexPath  string
	index      map[string][]IndexEntry
	lastUpdate time.Time
	cacheTTL   time.Duration
	stats      IndexStats
}

// IndexEntry represents an entry in the local index
type IndexEntry struct {
	Path     string    `json:"path"`
	Pos      []int     `json:"pos"`
	Modified time.Time `json:"modified"`
	Size     int64     `json:"size"`
	Title    string    `json:"title"`
	Tags     []string  `json:"tags"`
}

// IndexStats tracks indexing statistics
type IndexStats struct {
	TotalFiles   int           `json:"total_files"`
	IndexedFiles int           `json:"indexed_files"`
	TotalTerms   int           `json:"total_terms"`
	IndexSize    int64         `json:"index_size"`
	LastUpdate   time.Time     `json:"last_update"`
	BuildTime    time.Duration `json:"build_time"`
	QueryTime    time.Duration `json:"query_time"`
}

// NewLocalIndexer creates a new LocalIndexer instance
func NewLocalIndexer(apiKey, baseURL, indexPath string) *LocalIndexer {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	return &LocalIndexer{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Transport: tr, Timeout: 30 * time.Second},
		indexPath:  indexPath,
		index:      make(map[string][]IndexEntry),
		cacheTTL:   10 * time.Minute,
		stats:      IndexStats{},
	}
}

// BuildIndex builds the local index from vault data
func (li *LocalIndexer) BuildIndex() error {
	startTime := time.Now()

	// Check if index is fresh
	if time.Since(li.lastUpdate) < li.cacheTTL && len(li.index) > 0 {
		return nil
	}

	// Load existing index if available
	if err := li.loadIndex(); err != nil {
		// Index doesn't exist or is corrupted, rebuild
		li.index = make(map[string][]IndexEntry)
	}

	// Get all files from vault
	files, err := li.getVaultFiles()
	if err != nil {
		return fmt.Errorf("failed to get vault files: %w", err)
	}

	// Index each file
	indexedCount := 0
	for _, filePath := range files {
		if strings.HasSuffix(filePath, ".md") {
			if err := li.indexFile(filePath); err != nil {
				continue // Skip files that can't be indexed
			}
			indexedCount++
		}
	}

	// Save index to disk
	if err := li.saveIndex(); err != nil {
		return fmt.Errorf("failed to save index: %w", err)
	}

	// Update statistics
	li.updateStats(len(files), indexedCount, time.Since(startTime))
	li.lastUpdate = time.Now()

	return nil
}

// indexFile indexes a single file
func (li *LocalIndexer) indexFile(filePath string) error {
	// Get file content
	content, err := li.getFileContent(filePath)
	if err != nil {
		return fmt.Errorf("failed to get file content: %w", err)
	}

	// Extract metadata
	title := li.extractTitle(filePath, content)
	tags := li.extractTags(content)
	modified := time.Now() // Simplified - would get from file metadata

	// Tokenize content
	words := li.tokenizeContent(content)

	// Index each word
	for i, word := range words {
		word = strings.ToLower(word)
		if len(word) >= 2 { // Only index words with 2+ characters
			entry := IndexEntry{
				Path:     filePath,
				Pos:      []int{i},
				Modified: modified,
				Size:     int64(len(content)),
				Title:    title,
				Tags:     tags,
			}

			li.index[word] = append(li.index[word], entry)
		}
	}

	return nil
}

// extractTitle extracts the title from file path and content
func (li *LocalIndexer) extractTitle(filePath, content string) string {
	// Use filename as title
	fileName := filepath.Base(filePath)
	title := strings.TrimSuffix(fileName, ".md")

	// Try to extract title from content (first heading)
	lines := strings.Split(content, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "# ") {
			title = strings.TrimPrefix(line, "# ")
			break
		}
	}

	return title
}

// extractTags extracts tags from markdown content
func (li *LocalIndexer) extractTags(content string) []string {
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

// tokenizeContent tokenizes content into words
func (li *LocalIndexer) tokenizeContent(content string) []string {
	// Convert to lowercase
	content = strings.ToLower(content)

	// Split by whitespace and punctuation
	var words []string
	var current strings.Builder

	for _, r := range content {
		if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') {
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

// QueryIndex queries the local index for terms
func (li *LocalIndexer) QueryIndex(query string) ([]IndexEntry, error) {
	startTime := time.Now()

	// Ensure index is built
	if err := li.BuildIndex(); err != nil {
		return nil, fmt.Errorf("failed to build index: %w", err)
	}

	// Tokenize query
	terms := li.tokenizeContent(query)

	// Find entries for each term
	var results []IndexEntry
	seen := make(map[string]bool)

	for _, term := range terms {
		if entries, exists := li.index[term]; exists {
			for _, entry := range entries {
				key := entry.Path + ":" + term
				if !seen[key] {
					results = append(results, entry)
					seen[key] = true
				}
			}
		}
	}

	// Update query time
	li.stats.QueryTime = time.Since(startTime)

	return results, nil
}

// saveIndex saves the index to disk
func (li *LocalIndexer) saveIndex() error {
	// Create directory if it doesn't exist
	dir := filepath.Dir(li.indexPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create directory: %w", err)
	}

	// Marshal index to JSON
	data, err := json.MarshalIndent(li.index, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal index: %w", err)
	}

	// Write to file
	if err := os.WriteFile(li.indexPath, data, 0644); err != nil {
		return fmt.Errorf("failed to write index file: %w", err)
	}

	return nil
}

// loadIndex loads the index from disk
func (li *LocalIndexer) loadIndex() error {
	// Check if file exists
	if _, err := os.Stat(li.indexPath); os.IsNotExist(err) {
		return fmt.Errorf("index file does not exist")
	}

	// Read file
	data, err := os.ReadFile(li.indexPath)
	if err != nil {
		return fmt.Errorf("failed to read index file: %w", err)
	}

	// Unmarshal JSON
	if err := json.Unmarshal(data, &li.index); err != nil {
		return fmt.Errorf("failed to unmarshal index: %w", err)
	}

	return nil
}

// getVaultFiles gets all files from the vault
func (li *LocalIndexer) getVaultFiles() ([]string, error) {
	url := li.baseURL + "/vault/"
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+li.apiKey)
	resp, err := li.httpClient.Do(req)
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
func (li *LocalIndexer) getFileContent(filePath string) (string, error) {
	url := li.baseURL + "/vault/" + filePath
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+li.apiKey)
	resp, err := li.httpClient.Do(req)
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

// updateStats updates the indexing statistics
func (li *LocalIndexer) updateStats(totalFiles, indexedFiles int, buildTime time.Duration) {
	totalTerms := 0
	for _, entries := range li.index {
		totalTerms += len(entries)
	}

	li.stats = IndexStats{
		TotalFiles:   totalFiles,
		IndexedFiles: indexedFiles,
		TotalTerms:   totalTerms,
		IndexSize:    int64(len(li.index)),
		LastUpdate:   li.lastUpdate,
		BuildTime:    buildTime,
	}
}

// GetStats returns the current indexing statistics
func (li *LocalIndexer) GetStats() IndexStats {
	return li.stats
}

// ClearIndex clears the local index
func (li *LocalIndexer) ClearIndex() error {
	li.index = make(map[string][]IndexEntry)
	li.lastUpdate = time.Time{}

	// Remove index file if it exists
	if _, err := os.Stat(li.indexPath); !os.IsNotExist(err) {
		return os.Remove(li.indexPath)
	}

	return nil
}

// SetCacheTTL sets the cache TTL for the index
func (li *LocalIndexer) SetCacheTTL(ttl time.Duration) {
	li.cacheTTL = ttl
}
