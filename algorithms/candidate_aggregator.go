package algorithms

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// CandidateAggregator collects pages/streams from /vault/ and merges into candidate list
// Handles pagination for large vaults (client-side)
type CandidateAggregator struct {
	apiKey     string
	baseURL    string
	client     *http.Client
	httpClient interface{} // HTTP client wrapper for statistics tracking
	limit      int
}

// FileInfo represents a file from the vault
type FileInfo struct {
	Path     string                 `json:"path"`
	Name     string                 `json:"name"`
	Metadata map[string]interface{} `json:"metadata"`
	Content  string                 `json:"content,omitempty"`
	Size     int64                  `json:"size,omitempty"`
	Modified time.Time              `json:"modified,omitempty"`
}

// Candidate represents a search candidate with metadata
type Candidate struct {
	FileInfo
	MatchType      string  `json:"match_type"`
	MatchScore     float64 `json:"match_score"`
	RelevanceScore float64 `json:"relevance_score"`
}

// NewCandidateAggregator creates a new CandidateAggregator instance
func NewCandidateAggregator(apiKey, baseURL string) *CandidateAggregator {
	return &CandidateAggregator{
		apiKey:  apiKey,
		baseURL: baseURL,
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
		limit: 1000, // Default limit for large vaults
	}
}

// NewCandidateAggregatorWithClient creates a new CandidateAggregator with a shared HTTP client
func NewCandidateAggregatorWithClient(apiKey, baseURL string, client *http.Client) *CandidateAggregator {
	return &CandidateAggregator{
		apiKey:  apiKey,
		baseURL: baseURL,
		client:  client,
		limit:   1000, // Default limit for large vaults
	}
}

// NewCandidateAggregatorWithHTTPClient creates a new CandidateAggregator with a shared HTTP client wrapper
func NewCandidateAggregatorWithHTTPClient(httpClient interface{}) *CandidateAggregator {
	// This will be used to pass the full HTTP client wrapper
	return &CandidateAggregator{
		apiKey:  "",
		baseURL: "",
		client:  nil, // Will be set by the wrapper
		limit:   1000,
	}
}

// AggregateCandidates collects and processes vault files into candidates
func (ca *CandidateAggregator) AggregateCandidates(query string, limit int) ([]Candidate, error) {
	// Step 1: Call GET /vault/
	files, err := ca.getVaultFiles()
	if err != nil {
		return nil, fmt.Errorf("failed to get vault files: %w", err)
	}

	fmt.Printf("🔍 Found %d total files in vault\n", len(files))

	// Step 2: For large vaults, use a more intelligent search strategy
	var candidates []Candidate

	if len(files) > 500 {
		// For large vaults, search more intelligently
		candidates = ca.intelligentSearch(files, query, limit)
	} else {
		// For smaller vaults, process all files
		candidates = ca.processAllFiles(files, query, limit)
	}

	fmt.Printf("✅ Found %d relevant candidates for query '%s'\n", len(candidates), query)
	return candidates, nil
}

// intelligentSearch performs intelligent search for large vaults
func (ca *CandidateAggregator) intelligentSearch(files []FileInfo, query string, limit int) []Candidate {
	var candidates []Candidate

	// Special handling for empty query (Browse All Files)
	if query == "" {
		fmt.Println("📁 Phase 1: Loading all files...")
		for i, file := range files {
			if limit > 0 && i >= limit {
				break
			}
			candidate := &Candidate{
				FileInfo:       file,
				MatchType:      "all",
				MatchScore:     1.0,
				RelevanceScore: 1.0,
			}
			candidates = append(candidates, *candidate)
		}
		return candidates
	}

	// Phase 1: Search filenames first (fastest)
	fmt.Println("📝 Phase 1: Searching filenames...")
	for _, file := range files {
		if ca.matchesQuery(file.Name, query) {
			candidate := &Candidate{
				FileInfo:       file,
				MatchType:      "filename",
				MatchScore:     1.0,
				RelevanceScore: 2.0,
			}
			candidates = append(candidates, *candidate)
		}
	}

	// Phase 2: Search file paths
	fmt.Println("📁 Phase 2: Searching file paths...")
	for _, file := range files {
		if ca.matchesQuery(file.Path, query) {
			// Check if already added as filename match
			alreadyAdded := false
			for _, existing := range candidates {
				if existing.Path == file.Path {
					alreadyAdded = true
					break
				}
			}

			if !alreadyAdded {
				candidate := &Candidate{
					FileInfo:       file,
					MatchType:      "path",
					MatchScore:     0.8,
					RelevanceScore: 1.5,
				}
				candidates = append(candidates, *candidate)
			}
		}
	}

	// Phase 3: Search file contents (most expensive, do last)
	fmt.Println("📄 Phase 3: Searching file contents...")
	contentSearched := 0
	maxContentSearch := limit * 10 // Increased limit for better results

	for _, file := range files {
		if contentSearched >= maxContentSearch {
			break
		}

		// Skip if already found in filename/path
		alreadyFound := false
		for _, existing := range candidates {
			if existing.Path == file.Path {
				alreadyFound = true
				break
			}
		}

		if alreadyFound {
			continue
		}

		// Search content for more candidates (less restrictive)
		content, err := ca.getFileContent(file.Path)
		if err != nil {
			continue // Skip files we can't read
		}

		file.Content = content
		if ca.matchesQuery(content, query) {
			candidate := &Candidate{
				FileInfo:       file,
				MatchType:      "content",
				MatchScore:     ca.calculateContentScore(content, query),
				RelevanceScore: 1.0,
			}
			candidates = append(candidates, *candidate)
		}
		contentSearched++
	}

	// Sort by relevance score and apply final limit
	candidates = ca.sortCandidatesByRelevance(candidates)
	if limit > 0 && len(candidates) > limit {
		candidates = candidates[:limit]
	}

	return candidates
}

// processAllFiles processes all files for smaller vaults
func (ca *CandidateAggregator) processAllFiles(files []FileInfo, query string, limit int) []Candidate {
	var candidates []Candidate

	for _, file := range files {
		if limit > 0 && len(candidates) >= limit*2 {
			break
		}

		candidate, err := ca.processFile(file, query)
		if err != nil {
			continue // Skip problematic files
		}
		if candidate != nil {
			candidates = append(candidates, *candidate)
		}
	}

	// Sort by relevance score and apply final limit
	candidates = ca.sortCandidatesByRelevance(candidates)
	if limit > 0 && len(candidates) > limit {
		candidates = candidates[:limit]
	}

	return candidates
}

// isLikelyCandidate determines if a file is likely to contain the query
func (ca *CandidateAggregator) isLikelyCandidate(file FileInfo, queryLower string) bool {
	// Check if filename contains any part of the query
	fileNameLower := strings.ToLower(file.Name)
	filePathLower := strings.ToLower(file.Path)

	// Check for partial matches
	queryWords := strings.Fields(queryLower)
	for _, word := range queryWords {
		if len(word) > 2 && (strings.Contains(fileNameLower, word) || strings.Contains(filePathLower, word)) {
			return true
		}
	}

	// Check for common file types that might contain the content
	ext := getFileExtension(file.Name)
	contentTypes := map[string]bool{
		"md": true, "txt": true, "rst": true, "org": true,
		"py": true, "js": true, "ts": true, "go": true,
		"json": true, "yaml": true, "yml": true,
	}

	return contentTypes[ext]
}

// sortCandidatesByRelevance sorts candidates by relevance score
func (ca *CandidateAggregator) sortCandidatesByRelevance(candidates []Candidate) []Candidate {
	// Simple bubble sort by relevance score (descending)
	n := len(candidates)
	for i := 0; i < n-1; i++ {
		for j := 0; j < n-i-1; j++ {
			if candidates[j].RelevanceScore < candidates[j+1].RelevanceScore {
				candidates[j], candidates[j+1] = candidates[j+1], candidates[j]
			}
		}
	}
	return candidates
}

// getVaultFiles retrieves all files from the vault (recursively)
func (ca *CandidateAggregator) getVaultFiles() ([]FileInfo, error) {
	// First get the top-level files and directories
	req, err := http.NewRequest("GET", ca.baseURL+"/vault/", nil)
	if err != nil {
		return nil, err
	}

	req.Header.Add("Authorization", "Bearer "+ca.apiKey)
	req.Header.Add("Accept", "application/json")

	resp, err := ca.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("vault request failed with status: %d", resp.StatusCode)
	}

	// Parse the response structure
	var response struct {
		Files []string `json:"files"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	// Convert to FileInfo structs and scan directories recursively
	var allFiles []FileInfo
	for _, filePath := range response.Files {
		fileInfo := FileInfo{
			Path: filePath,
			Name: filePath,
		}

		// Check if this is a directory (ends with /)
		if strings.HasSuffix(filePath, "/") {
			// This is a directory, scan it recursively
			dirFiles, err := ca.scanDirectory(filePath)
			if err != nil {
				fmt.Printf("⚠️  Warning: Failed to scan directory %s: %v\n", filePath, err)
				// Still add the directory itself
				allFiles = append(allFiles, fileInfo)
			} else {
				// Add all files from the directory
				allFiles = append(allFiles, dirFiles...)
			}
		} else {
			// This is a file, add it directly
			allFiles = append(allFiles, fileInfo)
		}
	}

	fmt.Printf("🔍 Scanned vault: %d top-level items, %d total files found\n", len(response.Files), len(allFiles))
	return allFiles, nil
}

// scanDirectory recursively scans a directory for files
func (ca *CandidateAggregator) scanDirectory(dirPath string) ([]FileInfo, error) {
	var files []FileInfo

	// Remove trailing slash for the API call
	cleanPath := strings.TrimSuffix(dirPath, "/")

	req, err := http.NewRequest("GET", ca.baseURL+"/vault/"+cleanPath+"/", nil)
	if err != nil {
		return nil, err
	}

	req.Header.Add("Authorization", "Bearer "+ca.apiKey)
	req.Header.Add("Accept", "application/json")

	resp, err := ca.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		// Directory might not exist or be accessible, return empty
		return files, nil
	}

	// Parse the response structure
	var response struct {
		Files []string `json:"files"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	// Process each file/directory in this directory
	for _, filePath := range response.Files {
		fullPath := cleanPath + "/" + filePath
		fileInfo := FileInfo{
			Path: fullPath,
			Name: filePath,
		}

		// Check if this is a subdirectory
		if strings.HasSuffix(filePath, "/") {
			// This is a subdirectory, scan it recursively
			subFiles, err := ca.scanDirectory(fullPath + "/")
			if err != nil {
				fmt.Printf("⚠️  Warning: Failed to scan subdirectory %s: %v\n", fullPath, err)
				// Still add the subdirectory itself
				files = append(files, fileInfo)
			} else {
				// Add all files from the subdirectory
				files = append(files, subFiles...)
			}
		} else {
			// This is a file, add it directly
			files = append(files, fileInfo)
		}
	}

	return files, nil
}

// processFile processes a single file into a candidate
func (ca *CandidateAggregator) processFile(file FileInfo, query string) (*Candidate, error) {
	candidate := &Candidate{
		FileInfo:       file,
		MatchType:      "none",
		MatchScore:     0.0,
		RelevanceScore: 0.0,
	}

	// If query is empty, return all files
	if query == "" {
		candidate.MatchType = "all"
		candidate.MatchScore = 0.5
		candidate.RelevanceScore = 0.5
		return candidate, nil
	}

	// Check if file matches query in filename
	if ca.matchesQuery(file.Name, query) {
		candidate.MatchType = "filename"
		candidate.MatchScore = 1.0
		candidate.RelevanceScore = 2.0 // High relevance for filename matches
		return candidate, nil
	}

	// Check if file matches query in path
	if ca.matchesQuery(file.Path, query) {
		candidate.MatchType = "path"
		candidate.MatchScore = 0.8
		candidate.RelevanceScore = 1.5 // Medium-high relevance for path matches
		return candidate, nil
	}

	// For content search, we need to get the file content
	content, err := ca.getFileContent(file.Path)
	if err != nil {
		return nil, err // Skip files we can't read
	}

	candidate.Content = content

	// Check if content matches query
	if ca.matchesQuery(content, query) {
		candidate.MatchType = "content"
		candidate.MatchScore = ca.calculateContentScore(content, query)
		candidate.RelevanceScore = 1.0 // Base relevance for content matches
		return candidate, nil
	}

	// No match found
	return nil, nil
}

// getFileContent retrieves the content of a specific file
func (ca *CandidateAggregator) getFileContent(filePath string) (string, error) {
	req, err := http.NewRequest("GET", ca.baseURL+"/vault/"+filePath, nil)
	if err != nil {
		return "", err
	}

	req.Header.Add("Authorization", "Bearer "+ca.apiKey)

	resp, err := ca.client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("file request failed with status: %d", resp.StatusCode)
	}

	var result struct {
		Content string `json:"content"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		// If JSON decode fails, try reading as plain text
		body := make([]byte, resp.ContentLength)
		if _, err := resp.Body.Read(body); err != nil {
			return "", err
		}
		return string(body), nil
	}

	return result.Content, nil
}

// matchesQuery checks if text contains the query (case-insensitive)
func (ca *CandidateAggregator) matchesQuery(text, query string) bool {
	if len(text) == 0 || len(query) == 0 {
		return false
	}

	textLower := strings.ToLower(text)
	queryLower := strings.ToLower(query)

	// Exact match
	if strings.Contains(textLower, queryLower) {
		return true
	}

	// Partial word matches for better results
	queryWords := strings.Fields(queryLower)
	if len(queryWords) > 1 {
		// For multi-word queries, check if all words are present
		allWordsFound := true
		for _, word := range queryWords {
			if len(word) > 2 && !strings.Contains(textLower, word) {
				allWordsFound = false
				break
			}
		}
		if allWordsFound {
			return true
		}
	}

	// Check for partial matches (useful for typos and variations)
	if len(query) > 3 {
		// Check if query is contained in any word
		words := strings.Fields(textLower)
		for _, word := range words {
			if len(word) > 3 && strings.Contains(word, queryLower) {
				return true
			}
		}
	}

	return false
}

// calculateContentScore calculates a score based on query frequency in content
func (ca *CandidateAggregator) calculateContentScore(content, query string) float64 {
	if len(content) == 0 || len(query) == 0 {
		return 0.0
	}

	// Simple frequency-based scoring
	contentLower := strings.ToLower(content)
	queryLower := strings.ToLower(query)

	count := strings.Count(contentLower, queryLower)
	if count == 0 {
		return 0.0
	}

	// Normalize by content length and cap at 1.0
	score := float64(count) / float64(len(content)) * 1000
	if score > 1.0 {
		score = 1.0
	}

	return score
}

// SetLimit sets the maximum number of files to process
func (ca *CandidateAggregator) SetLimit(limit int) {
	ca.limit = limit
}

// GetVaultStats returns statistics about the vault
func (ca *CandidateAggregator) GetVaultStats() (map[string]interface{}, error) {
	files, err := ca.getVaultFiles()
	if err != nil {
		return nil, err
	}

	totalFiles := len(files)
	totalSize := int64(0)
	fileTypes := make(map[string]int)

	for _, file := range files {
		totalSize += file.Size

		// Extract file extension
		if ext := getFileExtension(file.Name); ext != "" {
			fileTypes[ext]++
		} else {
			fileTypes["no_extension"]++
		}
	}

	return map[string]interface{}{
		"total_files": totalFiles,
		"total_size":  totalSize,
		"file_types":  fileTypes,
		"timestamp":   time.Now(),
	}, nil
}

// Helper functions

// containsIgnoreCase checks if s contains substr (case-insensitive)
func containsIgnoreCase(s, substr string) bool {
	return len(s) >= len(substr) &&
		strings.Contains(strings.ToLower(s), strings.ToLower(substr))
}

// getFileExtension extracts the file extension from a filename
func getFileExtension(filename string) string {
	if idx := strings.LastIndex(filename, "."); idx != -1 && idx < len(filename)-1 {
		return filename[idx+1:]
	}
	return ""
}
