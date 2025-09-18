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

type SmartSearchResult struct {
	File    string  `json:"file"`
	Score   float64 `json:"score"`
	Snippet string  `json:"snippet"`
	Type    string  `json:"type"`
}

type SmartSearchEngine struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
}

func NewSmartSearchEngine(apiKey, baseURL string) *SmartSearchEngine {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	return &SmartSearchEngine{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Transport: tr, Timeout: 10 * time.Second},
	}
}

func (sse *SmartSearchEngine) SmartSearch(query string) ([]SmartSearchResult, error) {
	startTime := time.Now()

	fmt.Printf("🧠 Smart search: %s\n", query)

	// Get comprehensive file list
	files, err := sse.getComprehensiveFiles()
	if err != nil {
		return nil, err
	}

	fmt.Printf("📁 Scanning %d files...\n", len(files))

	var results []SmartSearchResult
	queryLower := strings.ToLower(query)

	// Multi-phase search
	// Phase 1: Filename matches (highest priority)
	for _, file := range files {
		fileName := strings.ToLower(file)
		if strings.Contains(fileName, queryLower) {
			score := sse.calculateScore(file, queryLower)
			results = append(results, SmartSearchResult{
				File:    file,
				Score:   score,
				Snippet: fmt.Sprintf("📁 %s", file),
				Type:    "filename",
			})
		}
	}

	// Phase 2: Content search (medium priority)
	contentResults, err := sse.searchContent(files, queryLower)
	if err != nil {
		fmt.Printf("⚠️ Content search failed: %v\n", err)
	} else {
		results = append(results, contentResults...)
	}

	// Sort by score
	results = sse.sortByScore(results)

	// Remove duplicates
	results = sse.removeDuplicates(results)

	// Limit to top 15 results
	if len(results) > 15 {
		results = results[:15]
	}

	duration := time.Since(startTime)
	fmt.Printf("⚡ Smart search completed in %v | Found %d results\n", duration, len(results))

	return results, nil
}

func (sse *SmartSearchEngine) getComprehensiveFiles() ([]string, error) {
	var allFiles []string

	// Start with root directory
	err := sse.getFilesRecursive("", &allFiles)
	if err != nil {
		return nil, err
	}

	return allFiles, nil
}

func (sse *SmartSearchEngine) getFilesRecursive(path string, allFiles *[]string) error {
	var url string
	if path == "" {
		url = sse.baseURL + "/vault/"
	} else {
		url = sse.baseURL + "/vault/" + path + "/"
	}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return err
	}

	req.Header.Add("Authorization", "Bearer "+sse.apiKey)
	resp, err := sse.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	var response struct {
		Files []string `json:"files"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return err
	}

	for _, file := range response.Files {
		fullPath := file
		if path != "" {
			fullPath = path + "/" + file
		}

		// Add file to results
		*allFiles = append(*allFiles, fullPath)

		// If it's a directory, recurse into it
		if strings.HasSuffix(file, "/") {
			dirPath := strings.TrimSuffix(fullPath, "/")
			err := sse.getFilesRecursive(dirPath, allFiles)
			if err != nil {
				fmt.Printf("⚠️ Failed to scan directory %s: %v\n", dirPath, err)
				// Continue with other directories
			}
		}
	}

	return nil
}

func (sse *SmartSearchEngine) calculateScore(file, query string) float64 {
	fileName := strings.ToLower(file)

	// Exact match gets highest score
	if fileName == query {
		return 1.0
	}

	// Starts with query gets high score
	if strings.HasPrefix(fileName, query) {
		return 0.9
	}

	// Contains query gets medium score
	if strings.Contains(fileName, query) {
		return 0.7
	}

	return 0.5
}

func (sse *SmartSearchEngine) searchContent(files []string, queryLower string) ([]SmartSearchResult, error) {
	var results []SmartSearchResult

	// Limit content search to first 20 files to avoid timeout
	maxFiles := 20
	if len(files) > maxFiles {
		files = files[:maxFiles]
	}

	for _, file := range files {
		// Skip directories
		if strings.HasSuffix(file, "/") {
			continue
		}

		// Skip non-markdown files
		if !strings.HasSuffix(strings.ToLower(file), ".md") {
			continue
		}

		content, err := sse.getFileContent(file)
		if err != nil {
			continue // Skip files that can't be read
		}

		contentLower := strings.ToLower(content)
		if strings.Contains(contentLower, queryLower) {
			// Find snippet around the match
			snippet := sse.extractSnippet(content, queryLower)
			score := sse.calculateContentScore(contentLower, queryLower)

			results = append(results, SmartSearchResult{
				File:    file,
				Score:   score,
				Snippet: snippet,
				Type:    "content",
			})
		}
	}

	return results, nil
}

func (sse *SmartSearchEngine) getFileContent(file string) (string, error) {
	url := sse.baseURL + "/vault/" + file
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", err
	}

	req.Header.Add("Authorization", "Bearer "+sse.apiKey)
	resp, err := sse.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	var response struct {
		Content string `json:"content"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return "", err
	}

	return response.Content, nil
}

func (sse *SmartSearchEngine) extractSnippet(content, query string) string {
	contentLower := strings.ToLower(content)
	queryLower := strings.ToLower(query)

	// Find the first occurrence
	index := strings.Index(contentLower, queryLower)
	if index == -1 {
		return "📄 Content match found"
	}

	// Extract 100 characters around the match
	start := index - 50
	if start < 0 {
		start = 0
	}
	end := index + len(queryLower) + 50
	if end > len(content) {
		end = len(content)
	}

	snippet := content[start:end]
	// Clean up the snippet
	snippet = strings.ReplaceAll(snippet, "\n", " ")
	snippet = strings.ReplaceAll(snippet, "\r", " ")
	snippet = strings.TrimSpace(snippet)

	if len(snippet) > 100 {
		snippet = snippet[:100] + "..."
	}

	return fmt.Sprintf("📄 %s", snippet)
}

func (sse *SmartSearchEngine) calculateContentScore(contentLower, queryLower string) float64 {
	// Count occurrences
	count := strings.Count(contentLower, queryLower)
	if count == 0 {
		return 0.0
	}

	// Base score from filename match
	baseScore := 0.6

	// Boost for multiple occurrences
	if count > 1 {
		baseScore += 0.1 * float64(count-1)
	}

	// Cap at 0.9 to keep filename matches higher
	if baseScore > 0.9 {
		baseScore = 0.9
	}

	return baseScore
}

func (sse *SmartSearchEngine) removeDuplicates(results []SmartSearchResult) []SmartSearchResult {
	seen := make(map[string]bool)
	var unique []SmartSearchResult

	for _, result := range results {
		if !seen[result.File] {
			seen[result.File] = true
			unique = append(unique, result)
		}
	}

	return unique
}

func (sse *SmartSearchEngine) sortByScore(results []SmartSearchResult) []SmartSearchResult {
	// Simple bubble sort by score (descending)
	n := len(results)
	for i := 0; i < n-1; i++ {
		for j := 0; j < n-i-1; j++ {
			if results[j].Score < results[j+1].Score {
				results[j], results[j+1] = results[j+1], results[j]
			}
		}
	}
	return results
}

func (sse *SmartSearchEngine) DisplayResults(results []SmartSearchResult) {
	if len(results) == 0 {
		fmt.Printf("❌ No results found\n")
		return
	}

	fmt.Printf("\n📋 SMART SEARCH RESULTS:\n")
	fmt.Printf("========================\n")

	for i, result := range results {
		fmt.Printf("%d. %s (Score: %.2f, Type: %s)\n", i+1, result.Snippet, result.Score, result.Type)
	}
	fmt.Printf("\n")
}

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("Usage: go run smart_search.go <query>\n")
		fmt.Printf("Example: go run smart_search.go logica\n")
		return
	}

	query := os.Args[1]
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	engine := NewSmartSearchEngine(apiKey, baseURL)

	results, err := engine.SmartSearch(query)
	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	engine.DisplayResults(results)
}
