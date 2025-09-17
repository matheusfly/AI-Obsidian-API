package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"
)

// QuickSearchResult represents a quick search result
type QuickSearchResult struct {
	File    string  `json:"file"`
	Score   float64 `json:"score"`
	Snippet string  `json:"snippet"`
	Type    string  `json:"type"`
}

// QuickSearchEngine provides ultra-fast search
type QuickSearchEngine struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
}

// NewQuickSearchEngine creates a new quick search engine
func NewQuickSearchEngine(apiKey, baseURL string) *QuickSearchEngine {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	return &QuickSearchEngine{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Transport: tr, Timeout: 5 * time.Second},
	}
}

// QuickSearch performs ultra-fast search
func (qse *QuickSearchEngine) QuickSearch(query string) ([]QuickSearchResult, error) {
	startTime := time.Now()

	fmt.Printf("🔍 Quick search: '%s'\n", query)

	// Get files (increased limit for better coverage)
	files, err := qse.getFiles(200)
	if err != nil {
		return nil, err
	}

	fmt.Printf("📁 Retrieved %d files for search\n", len(files))

	// Debug: Show first few files
	if len(files) > 0 {
		fmt.Printf("🔍 Sample files: %s, %s, %s\n", files[0], files[1], files[2])
	}

	var results []QuickSearchResult
	queryLower := strings.ToLower(query)

	// More aggressive filename search
	for _, file := range files {
		fileLower := strings.ToLower(file)
		// Check for exact match, partial match, or word boundary match
		if strings.Contains(fileLower, queryLower) ||
			strings.Contains(fileLower, strings.ReplaceAll(queryLower, " ", "")) ||
			qse.isRelevantMatch(fileLower, queryLower) {
			highlighted := strings.Replace(file, query, "🔍"+query+"🔍", -1)
			results = append(results, QuickSearchResult{
				File:    file,
				Score:   1.0,
				Snippet: fmt.Sprintf("📁 %s", highlighted),
				Type:    "filename",
			})
		}
	}

	duration := time.Since(startTime)
	fmt.Printf("⚡ Completed in %v | Found %d results\n", duration, len(results))

	return results, nil
}

// getFiles gets a limited number of files by recursively scanning directories
func (qse *QuickSearchEngine) getFiles(limit int) ([]string, error) {
	// Get top-level files and directories
	url := qse.baseURL + "/vault/"
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Add("Authorization", "Bearer "+qse.apiKey)
	resp, err := qse.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	var response struct {
		Files []string `json:"files"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	// Recursively scan directories to get actual files
	var allFiles []string
	for _, filePath := range response.Files {
		if strings.HasSuffix(filePath, "/") {
			// This is a directory, scan it recursively
			dirFiles, err := qse.scanDirectory(filePath, limit-len(allFiles))
			if err != nil {
				continue // Skip directories we can't scan
			}
			allFiles = append(allFiles, dirFiles...)
		} else {
			// This is a file, add it directly
			allFiles = append(allFiles, filePath)
		}

		// Stop if we've reached the limit
		if len(allFiles) >= limit {
			break
		}
	}

	// Limit the results
	if len(allFiles) > limit {
		allFiles = allFiles[:limit]
	}

	return allFiles, nil
}

// scanDirectory recursively scans a directory for files
func (qse *QuickSearchEngine) scanDirectory(dirPath string, maxFiles int) ([]string, error) {
	var files []string

	// Remove trailing slash for the API call
	cleanPath := strings.TrimSuffix(dirPath, "/")

	req, err := http.NewRequest("GET", qse.baseURL+"/vault/"+cleanPath+"/", nil)
	if err != nil {
		return nil, err
	}

	req.Header.Add("Authorization", "Bearer "+qse.apiKey)
	resp, err := qse.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return files, nil // Directory might not exist, return empty
	}

	var response struct {
		Files []string `json:"files"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	// Process each file/directory in this directory
	for _, filePath := range response.Files {
		if len(files) >= maxFiles {
			break
		}

		fullPath := cleanPath + "/" + filePath

		if strings.HasSuffix(filePath, "/") {
			// This is a subdirectory, scan it recursively
			subFiles, err := qse.scanDirectory(fullPath+"/", maxFiles-len(files))
			if err != nil {
				continue // Skip subdirectories we can't scan
			}
			files = append(files, subFiles...)
		} else {
			// This is a file, add it directly
			files = append(files, fullPath)
		}
	}

	return files, nil
}

// isRelevantMatch checks if a file is relevant to the query using fuzzy matching
func (qse *QuickSearchEngine) isRelevantMatch(file, query string) bool {
	// Split query into words
	queryWords := strings.Fields(query)
	fileWords := strings.Fields(strings.ReplaceAll(file, "-", " "))
	fileWords = append(fileWords, strings.Fields(strings.ReplaceAll(file, "_", " "))...)

	// Check if any query word is contained in any file word
	for _, qWord := range queryWords {
		for _, fWord := range fileWords {
			if len(qWord) >= 3 && len(fWord) >= 3 {
				// Check for partial word matches
				if strings.Contains(fWord, qWord) || strings.Contains(qWord, fWord) {
					return true
				}
			}
		}
	}
	return false
}

// DisplayResults displays quick search results
func (qse *QuickSearchEngine) DisplayResults(results []QuickSearchResult) {
	if len(results) == 0 {
		fmt.Printf("❌ No results found\n")
		return
	}

	fmt.Printf("\n📋 RESULTS:\n")
	fmt.Printf("===========\n")

	for i, result := range results {
		fmt.Printf("%d. %s\n", i+1, result.Snippet)
	}
	fmt.Printf("\n")
}

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("Usage: go run search_test.go <query>\n")
		fmt.Printf("Example: go run search_test.go agents\n")
		return
	}

	query := os.Args[1]
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	engine := NewQuickSearchEngine(apiKey, baseURL)

	results, err := engine.QuickSearch(query)
	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	engine.DisplayResults(results)
}
