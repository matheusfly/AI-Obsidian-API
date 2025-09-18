package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

// RealDataTestSuite represents a comprehensive test suite using real vault data
type RealDataTestSuite struct {
	baseURL        string
	token          string
	client         *http.Client
	results        []TestResult
	realFiles      []string
	realTestFile   string
	realSearchData map[string][]SearchResult
}

// TestResult represents the result of a test
type TestResult struct {
	TestName string `json:"test_name"`
	Status   string `json:"status"`
	Message  string `json:"message"`
	Duration int64  `json:"duration_ms"`
	Details  string `json:"details,omitempty"`
	Data     interface{} `json:"data,omitempty"`
}

// SearchResult represents a search result
type SearchResult struct {
	File    string  `json:"file"`
	Score   float64 `json:"score"`
	Snippet string  `json:"snippet"`
	Type    string  `json:"type"`
}

// NewRealDataTestSuite creates a new real data test suite
func NewRealDataTestSuite(baseURL, token string) *RealDataTestSuite {
	return &RealDataTestSuite{
		baseURL:        baseURL,
		token:          token,
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
		results:        make([]TestResult, 0),
		realFiles:      make([]string, 0),
		realSearchData: make(map[string][]SearchResult),
	}
}

// makeRequest makes an authenticated request
func (ts *RealDataTestSuite) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, ts.baseURL+path, body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+ts.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	return ts.client.Do(req)
}

// addResult adds a test result
func (ts *RealDataTestSuite) addResult(testName, status, message, details string, duration int64, data interface{}) {
	ts.results = append(ts.results, TestResult{
		TestName: testName,
		Status:   status,
		Message:  message,
		Duration: duration,
		Details:  details,
		Data:     data,
	})
}

// TestRealVaultConnection tests real vault connection and data retrieval
func (ts *RealDataTestSuite) TestRealVaultConnection() {
	start := time.Now()

	resp, err := ts.makeRequest("GET", "/vault/", nil)
	duration := time.Since(start).Milliseconds()

	if err != nil {
		ts.addResult("Real Vault Connection", "FAIL", fmt.Sprintf("Connection failed: %v", err), "", duration, nil)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		ts.addResult("Real Vault Connection", "FAIL", fmt.Sprintf("HTTP %d", resp.StatusCode), "", duration, nil)
		return
	}

	var response struct {
		Files []string `json:"files"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		ts.addResult("Real Vault Connection", "FAIL", fmt.Sprintf("JSON decode failed: %v", err), "", duration, nil)
		return
	}

	// Store real files for other tests
	ts.realFiles = response.Files
	
	// Find a real test file
	for _, file := range response.Files {
		if !strings.HasSuffix(file, "/") && strings.HasSuffix(strings.ToLower(file), ".md") {
			ts.realTestFile = file
			break
		}
	}

	ts.addResult("Real Vault Connection", "PASS", 
		fmt.Sprintf("Connected successfully, found %d real files", len(response.Files)), 
		fmt.Sprintf("Test file: %s", ts.realTestFile), duration, response.Files)
}

// TestRealFileReading tests reading real files from vault
func (ts *RealDataTestSuite) TestRealFileReading() {
	start := time.Now()

	if ts.realTestFile == "" {
		ts.addResult("Real File Reading", "SKIP", "No markdown files found in vault", "", time.Since(start).Milliseconds(), nil)
		return
	}

	// Read the real test file
	resp, err := ts.makeRequest("GET", "/vault/"+url.PathEscape(ts.realTestFile), nil)
	duration := time.Since(start).Milliseconds()

	if err != nil {
		ts.addResult("Real File Reading", "FAIL", fmt.Sprintf("Failed to read real file '%s': %v", ts.realTestFile, err), "", duration, nil)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		ts.addResult("Real File Reading", "FAIL", fmt.Sprintf("Failed to read real file '%s': HTTP %d", ts.realTestFile, resp.StatusCode), "", duration, nil)
		return
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		ts.addResult("Real File Reading", "FAIL", fmt.Sprintf("Failed to read file body '%s': %v", ts.realTestFile, err), "", duration, nil)
		return
	}

	content := string(body)
	fileData := map[string]interface{}{
		"filename": ts.realTestFile,
		"size": len(content),
		"preview": content[:min(200, len(content))],
	}

	ts.addResult("Real File Reading", "PASS", 
		fmt.Sprintf("Successfully read real file '%s' (%d characters)", ts.realTestFile, len(content)), 
		"Real vault data successfully accessed", duration, fileData)
}

// TestRealSearchFunctionality tests search with real vault data
func (ts *RealDataTestSuite) TestRealSearchFunctionality() {
	start := time.Now()

	// Test with real search terms that should exist in the vault
	searchTerms := []string{"logica", "matematica", "dados", "programacao", "computacao", "filosofia", "ciencia"}
	successCount := 0
	var searchResults []SearchResult

	for _, term := range searchTerms {
		results := ts.performRealSearch(term)
		if len(results) > 0 {
			successCount++
			ts.realSearchData[term] = results
			searchResults = append(searchResults, results...)
		}
	}

	duration := time.Since(start).Milliseconds()

	searchData := map[string]interface{}{
		"total_searches": len(searchTerms),
		"successful_searches": successCount,
		"total_results": len(searchResults),
		"search_terms": searchTerms,
		"results": ts.realSearchData,
	}

	if successCount == len(searchTerms) {
		ts.addResult("Real Search Functionality", "PASS", 
			fmt.Sprintf("All %d search terms found real results", len(searchTerms)), 
			fmt.Sprintf("Total results: %d", len(searchResults)), duration, searchData)
	} else if successCount > 0 {
		ts.addResult("Real Search Functionality", "PARTIAL", 
			fmt.Sprintf("%d/%d search terms found real results", successCount, len(searchTerms)), 
			fmt.Sprintf("Total results: %d", len(searchResults)), duration, searchData)
	} else {
		ts.addResult("Real Search Functionality", "FAIL", 
			"No search terms found real results", 
			"Check if vault contains expected content", duration, searchData)
	}
}

// performRealSearch performs a real search through vault files
func (ts *RealDataTestSuite) performRealSearch(query string) []SearchResult {
	var results []SearchResult
	queryLower := strings.ToLower(query)

	// Search through real files
	for _, file := range ts.realFiles {
		if strings.HasSuffix(file, "/") {
			// Directory - search recursively
			subResp, err := ts.makeRequest("GET", "/vault/"+url.PathEscape(file), nil)
			if err != nil {
				continue
			}

			var subResponse struct {
				Files []string `json:"files"`
			}

			if err := json.NewDecoder(subResp.Body).Decode(&subResponse); err != nil {
				subResp.Body.Close()
				continue
			}
			subResp.Body.Close()

			for _, subFile := range subResponse.Files {
				if strings.HasSuffix(subFile, "/") {
					continue // Skip subdirectories
				}

				fullPath := file + subFile

				// Check filename match
				if strings.Contains(strings.ToLower(subFile), queryLower) {
					results = append(results, SearchResult{
						File:    fullPath,
						Score:   0.9,
						Snippet: fmt.Sprintf("📁 Filename match: %s", subFile),
						Type:    "filename",
					})
				}

				// Check content match for markdown files
				if strings.HasSuffix(strings.ToLower(subFile), ".md") {
					contentResp, err := ts.makeRequest("GET", "/vault/"+url.PathEscape(fullPath), nil)
					if err != nil {
						continue
					}

					if contentResp.StatusCode == http.StatusOK {
						body, err := io.ReadAll(contentResp.Body)
						contentResp.Body.Close()
						if err == nil && strings.Contains(strings.ToLower(string(body)), queryLower) {
							snippet := ts.extractSnippet(string(body), queryLower)
							score := ts.calculateContentScore(string(body), queryLower)
							results = append(results, SearchResult{
								File:    fullPath,
								Score:   score,
								Snippet: snippet,
								Type:    "content",
							})
						}
					}
				}
			}
		} else {
			// File in root directory
			if strings.Contains(strings.ToLower(file), queryLower) {
				results = append(results, SearchResult{
					File:    file,
					Score:   0.9,
					Snippet: fmt.Sprintf("📁 Filename match: %s", file),
					Type:    "filename",
				})
			}

			// Check content match for markdown files
			if strings.HasSuffix(strings.ToLower(file), ".md") {
				contentResp, err := ts.makeRequest("GET", "/vault/"+url.PathEscape(file), nil)
				if err != nil {
					continue
				}

				if contentResp.StatusCode == http.StatusOK {
					body, err := io.ReadAll(contentResp.Body)
					contentResp.Body.Close()
					if err == nil && strings.Contains(strings.ToLower(string(body)), queryLower) {
						snippet := ts.extractSnippet(string(body), queryLower)
						score := ts.calculateContentScore(string(body), queryLower)
						results = append(results, SearchResult{
							File:    file,
							Score:   score,
							Snippet: snippet,
							Type:    "content",
						})
					}
				}
			}
		}
	}

	return results
}

// extractSnippet extracts a snippet around the search term
func (ts *RealDataTestSuite) extractSnippet(content, query string) string {
	contentLower := strings.ToLower(content)
	queryLower := strings.ToLower(query)

	index := strings.Index(contentLower, queryLower)
	if index == -1 {
		return "Content match found"
	}

	start := max(0, index-50)
	end := min(len(content), index+len(query)+50)

	snippet := content[start:end]
	if start > 0 {
		snippet = "..." + snippet
	}
	if end < len(content) {
		snippet = snippet + "..."
	}

	return snippet
}

// calculateContentScore calculates relevance score for content matches
func (ts *RealDataTestSuite) calculateContentScore(content, query string) float64 {
	count := strings.Count(strings.ToLower(content), strings.ToLower(query))
	if count == 0 {
		return 0.0
	}

	baseScore := 0.6
	if count > 1 {
		baseScore += 0.1 * float64(count-1)
	}
	if baseScore > 0.9 {
		baseScore = 0.9
	}

	return baseScore
}

// TestRealVaultStatistics tests real vault statistics
func (ts *RealDataTestSuite) TestRealVaultStatistics() {
	start := time.Now()

	fileCount := len(ts.realFiles)
	directoryCount := 0
	noteCount := 0
	otherCount := 0

	for _, file := range ts.realFiles {
		if strings.HasSuffix(file, "/") {
			directoryCount++
		} else if strings.HasSuffix(strings.ToLower(file), ".md") {
			noteCount++
		} else {
			otherCount++
		}
	}

	duration := time.Since(start).Milliseconds()

	stats := map[string]interface{}{
		"total_files": fileCount,
		"directories": directoryCount,
		"notes": noteCount,
		"other_files": otherCount,
		"vault_path": "D:\\Nomade Milionario",
		"api_endpoint": ts.baseURL,
	}

	ts.addResult("Real Vault Statistics", "PASS", 
		fmt.Sprintf("Analyzed %d real files (%d directories, %d notes, %d other)", fileCount, directoryCount, noteCount, otherCount), 
		"Real vault data successfully analyzed", duration, stats)
}

// TestRealContentAnalysis tests real content analysis
func (ts *RealDataTestSuite) TestRealContentAnalysis() {
	start := time.Now()

	if ts.realTestFile == "" {
		ts.addResult("Real Content Analysis", "SKIP", "No test file available", "", time.Since(start).Milliseconds(), nil)
		return
	}

	// Read the real test file for analysis
	resp, err := ts.makeRequest("GET", "/vault/"+url.PathEscape(ts.realTestFile), nil)
	if err != nil {
		ts.addResult("Real Content Analysis", "FAIL", fmt.Sprintf("Failed to read file: %v", err), "", time.Since(start).Milliseconds(), nil)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		ts.addResult("Real Content Analysis", "FAIL", fmt.Sprintf("Failed to read file body: %v", err), "", time.Since(start).Milliseconds(), nil)
		return
	}

	content := string(body)
	
	// Analyze content
	wordCount := len(strings.Fields(content))
	lineCount := len(strings.Split(content, "\n"))
	charCount := len(content)
	
	// Check for common patterns
	hasLinks := strings.Contains(content, "[["])
	hasTags := strings.Contains(content, "#")
	hasHeaders := strings.Contains(content, "# ")
	
	duration := time.Since(start).Milliseconds()

	analysis := map[string]interface{}{
		"filename": ts.realTestFile,
		"word_count": wordCount,
		"line_count": lineCount,
		"char_count": charCount,
		"has_links": hasLinks,
		"has_tags": hasTags,
		"has_headers": hasHeaders,
		"preview": content[:min(300, len(content))],
	}

	ts.addResult("Real Content Analysis", "PASS", 
		fmt.Sprintf("Analyzed real file '%s' (%d words, %d lines, %d chars)", ts.realTestFile, wordCount, lineCount, charCount), 
		fmt.Sprintf("Links: %v, Tags: %v, Headers: %v", hasLinks, hasTags, hasHeaders), duration, analysis)
}

// TestRealAPIIntegration tests real API integration
func (ts *RealDataTestSuite) TestRealAPIIntegration() {
	start := time.Now()

	// Test multiple API endpoints
	endpoints := []string{"/vault/", "/vault/1- Notas Indice/", "/vault/2- Notas De Leitura/"}
	successCount := 0
	var endpointResults []map[string]interface{}

	for _, endpoint := range endpoints {
		resp, err := ts.makeRequest("GET", endpoint, nil)
		if err != nil {
			endpointResults = append(endpointResults, map[string]interface{}{
				"endpoint": endpoint,
				"status": "error",
				"error": err.Error(),
			})
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode == http.StatusOK {
			successCount++
			endpointResults = append(endpointResults, map[string]interface{}{
				"endpoint": endpoint,
				"status": "success",
				"status_code": resp.StatusCode,
			})
		} else {
			endpointResults = append(endpointResults, map[string]interface{}{
				"endpoint": endpoint,
				"status": "failed",
				"status_code": resp.StatusCode,
			})
		}
	}

	duration := time.Since(start).Milliseconds()

	integrationData := map[string]interface{}{
		"endpoints_tested": len(endpoints),
		"successful_endpoints": successCount,
		"endpoint_results": endpointResults,
	}

	if successCount == len(endpoints) {
		ts.addResult("Real API Integration", "PASS", 
			fmt.Sprintf("All %d API endpoints working", len(endpoints)), 
			"Real API integration fully functional", duration, integrationData)
	} else if successCount > 0 {
		ts.addResult("Real API Integration", "PARTIAL", 
			fmt.Sprintf("%d/%d API endpoints working", successCount, len(endpoints)), 
			"Some API endpoints may not exist", duration, integrationData)
	} else {
		ts.addResult("Real API Integration", "FAIL", 
			"No API endpoints working", 
			"Check API configuration", duration, integrationData)
	}
}

// TestRealDataConsistency tests real data consistency
func (ts *RealDataTestSuite) TestRealDataConsistency() {
	start := time.Now()

	// Test that we can consistently access the same data
	consistencyTests := 3
	successCount := 0
	var consistencyResults []map[string]interface{}

	for i := 0; i < consistencyTests; i++ {
		resp, err := ts.makeRequest("GET", "/vault/", nil)
		if err != nil {
			consistencyResults = append(consistencyResults, map[string]interface{}{
				"test": i + 1,
				"status": "error",
				"error": err.Error(),
			})
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode == http.StatusOK {
			var response struct {
				Files []string `json:"files"`
			}

			if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
				consistencyResults = append(consistencyResults, map[string]interface{}{
					"test": i + 1,
					"status": "decode_error",
					"error": err.Error(),
				})
				continue
			}

			if len(response.Files) == len(ts.realFiles) {
				successCount++
				consistencyResults = append(consistencyResults, map[string]interface{}{
					"test": i + 1,
					"status": "success",
					"file_count": len(response.Files),
				})
			} else {
				consistencyResults = append(consistencyResults, map[string]interface{}{
					"test": i + 1,
					"status": "inconsistent",
					"file_count": len(response.Files),
					"expected": len(ts.realFiles),
				})
			}
		} else {
			consistencyResults = append(consistencyResults, map[string]interface{}{
				"test": i + 1,
				"status": "http_error",
				"status_code": resp.StatusCode,
			})
		}
	}

	duration := time.Since(start).Milliseconds()

	consistencyData := map[string]interface{}{
		"tests_run": consistencyTests,
		"successful_tests": successCount,
		"test_results": consistencyResults,
		"baseline_file_count": len(ts.realFiles),
	}

	if successCount == consistencyTests {
		ts.addResult("Real Data Consistency", "PASS", 
			fmt.Sprintf("All %d consistency tests passed", consistencyTests), 
			"Real data access is consistent", duration, consistencyData)
	} else if successCount > 0 {
		ts.addResult("Real Data Consistency", "PARTIAL", 
			fmt.Sprintf("%d/%d consistency tests passed", successCount, consistencyTests), 
			"Some data consistency issues detected", duration, consistencyData)
	} else {
		ts.addResult("Real Data Consistency", "FAIL", 
			"No consistency tests passed", 
			"Data access is inconsistent", duration, consistencyData)
	}
}

// RunAllRealDataTests runs all real data tests
func (ts *RealDataTestSuite) RunAllRealDataTests() {
	fmt.Println("🧪 REAL DATA COMPREHENSIVE TEST SUITE")
	fmt.Println("=====================================")
	fmt.Printf("🔗 Testing Real Obsidian Vault: %s\n", ts.baseURL)
	fmt.Printf("📁 Vault Path: D:\\Nomade Milionario\n")
	fmt.Printf("🔑 Using token: %s...\n", ts.token[:8])
	fmt.Println()
	fmt.Println("🎯 Testing with REAL vault data - no mock data!")
	fmt.Println()

	// Run all tests
	ts.TestRealVaultConnection()
	ts.TestRealFileReading()
	ts.TestRealSearchFunctionality()
	ts.TestRealVaultStatistics()
	ts.TestRealContentAnalysis()
	ts.TestRealAPIIntegration()
	ts.TestRealDataConsistency()

	// Print results
	fmt.Println("📊 REAL DATA TEST RESULTS")
	fmt.Println("=========================")

	passed := 0
	failed := 0
	skipped := 0

	for _, result := range ts.results {
		status := "❌"
		if result.Status == "PASS" {
			status = "✅"
			passed++
		} else if result.Status == "SKIP" {
			status = "⏭️"
			skipped++
		} else {
			failed++
		}

		fmt.Printf("%s %s: %s (%dms)\n", status, result.TestName, result.Message, result.Duration)
		if result.Details != "" {
			fmt.Printf("   Details: %s\n", result.Details)
		}
	}

	fmt.Println()
	fmt.Printf("📈 SUMMARY: %d passed, %d failed, %d skipped\n", passed, failed, skipped)
	fmt.Printf("📁 Real files processed: %d\n", len(ts.realFiles))
	fmt.Printf("🔍 Search terms tested: %d\n", len(ts.realSearchData))

	if failed == 0 {
		fmt.Println("🎉 ALL REAL DATA TESTS PASSED! System is fully functional with real vault data.")
	} else {
		fmt.Printf("⚠️ %d tests failed. Please review the issues above.\n", failed)
	}

	// Save detailed results to JSON
	ts.saveResultsToJSON()
}

// saveResultsToJSON saves test results to JSON file
func (ts *RealDataTestSuite) saveResultsToJSON() {
	results := map[string]interface{}{
		"timestamp": time.Now().Format("2006-01-02 15:04:05"),
		"vault_path": "D:\\Nomade Milionario",
		"api_endpoint": ts.baseURL,
		"total_tests": len(ts.results),
		"test_results": ts.results,
		"real_files_count": len(ts.realFiles),
		"search_data": ts.realSearchData,
	}

	jsonData, err := json.MarshalIndent(results, "", "  ")
	if err != nil {
		fmt.Printf("⚠️ Failed to save results to JSON: %v\n", err)
		return
	}

	// Save to file
	err = os.WriteFile("real_data_test_results.json", jsonData, 0644)
	if err != nil {
		fmt.Printf("⚠️ Failed to write results file: %v\n", err)
		return
	}

	fmt.Printf("💾 Detailed results saved to: real_data_test_results.json\n")
}

// Helper functions
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func main() {
	// Configuration
	obsidianBaseURL := "https://127.0.0.1:27124"
	obsidianToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	// Create and run real data test suite
	testSuite := NewRealDataTestSuite(obsidianBaseURL, obsidianToken)
	testSuite.RunAllRealDataTests()
}
