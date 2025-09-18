package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// TestSuite represents a comprehensive test suite
type TestSuite struct {
	baseURL string
	token   string
	client  *http.Client
	results []TestResult
}

// TestResult represents the result of a test
type TestResult struct {
	TestName string `json:"test_name"`
	Status   string `json:"status"`
	Message  string `json:"message"`
	Duration int64  `json:"duration_ms"`
	Details  string `json:"details,omitempty"`
}

// NewTestSuite creates a new test suite
func NewTestSuite(baseURL, token string) *TestSuite {
	return &TestSuite{
		baseURL: baseURL,
		token:   token,
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
		results: make([]TestResult, 0),
	}
}

// makeRequest makes an authenticated request
func (ts *TestSuite) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
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
func (ts *TestSuite) addResult(testName, status, message, details string, duration int64) {
	ts.results = append(ts.results, TestResult{
		TestName: testName,
		Status:   status,
		Message:  message,
		Duration: duration,
		Details:  details,
	})
}

// TestObsidianAPIConnection tests basic API connectivity
func (ts *TestSuite) TestObsidianAPIConnection() {
	start := time.Now()

	resp, err := ts.makeRequest("GET", "/vault/", nil)
	duration := time.Since(start).Milliseconds()

	if err != nil {
		ts.addResult("Obsidian API Connection", "FAIL", fmt.Sprintf("Connection failed: %v", err), "", duration)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		ts.addResult("Obsidian API Connection", "FAIL", fmt.Sprintf("HTTP %d", resp.StatusCode), "", duration)
		return
	}

	var response struct {
		Files []string `json:"files"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		ts.addResult("Obsidian API Connection", "FAIL", fmt.Sprintf("JSON decode failed: %v", err), "", duration)
		return
	}

	ts.addResult("Obsidian API Connection", "PASS", fmt.Sprintf("Connected successfully, found %d files", len(response.Files)), "", duration)
}

// TestFileListing tests file listing functionality
func (ts *TestSuite) TestFileListing() {
	start := time.Now()

	resp, err := ts.makeRequest("GET", "/vault/", nil)
	duration := time.Since(start).Milliseconds()

	if err != nil {
		ts.addResult("File Listing", "FAIL", fmt.Sprintf("Request failed: %v", err), "", duration)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		ts.addResult("File Listing", "FAIL", fmt.Sprintf("HTTP %d", resp.StatusCode), "", duration)
		return
	}

	var response struct {
		Files []string `json:"files"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		ts.addResult("File Listing", "FAIL", fmt.Sprintf("JSON decode failed: %v", err), "", duration)
		return
	}

	fileCount := len(response.Files)
	directoryCount := 0
	noteCount := 0

	for _, file := range response.Files {
		if strings.HasSuffix(file, "/") {
			directoryCount++
		} else if strings.HasSuffix(strings.ToLower(file), ".md") {
			noteCount++
		}
	}

	ts.addResult("File Listing", "PASS", fmt.Sprintf("Listed %d files (%d directories, %d notes)", fileCount, directoryCount, noteCount), "", duration)
}

// TestFileReading tests file reading functionality
func (ts *TestSuite) TestFileReading() {
	start := time.Now()

	// First get a list of files
	resp, err := ts.makeRequest("GET", "/vault/", nil)
	if err != nil {
		ts.addResult("File Reading", "FAIL", fmt.Sprintf("Failed to get file list: %v", err), "", time.Since(start).Milliseconds())
		return
	}
	defer resp.Body.Close()

	var response struct {
		Files []string `json:"files"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		ts.addResult("File Reading", "FAIL", fmt.Sprintf("Failed to decode file list: %v", err), "", time.Since(start).Milliseconds())
		return
	}

	// Find a markdown file to test reading
	var testFile string
	for _, file := range response.Files {
		if !strings.HasSuffix(file, "/") && strings.HasSuffix(strings.ToLower(file), ".md") {
			testFile = file
			break
		}
	}

	if testFile == "" {
		ts.addResult("File Reading", "SKIP", "No markdown files found to test", "", time.Since(start).Milliseconds())
		return
	}

	// Test reading the file
	fileResp, err := ts.makeRequest("GET", "/vault/"+url.PathEscape(testFile), nil)
	duration := time.Since(start).Milliseconds()

	if err != nil {
		ts.addResult("File Reading", "FAIL", fmt.Sprintf("Failed to read file '%s': %v", testFile, err), "", duration)
		return
	}
	defer fileResp.Body.Close()

	if fileResp.StatusCode != http.StatusOK {
		ts.addResult("File Reading", "FAIL", fmt.Sprintf("Failed to read file '%s': HTTP %d", testFile, fileResp.StatusCode), "", duration)
		return
	}

	body, err := io.ReadAll(fileResp.Body)
	if err != nil {
		ts.addResult("File Reading", "FAIL", fmt.Sprintf("Failed to read file body '%s': %v", testFile, err), "", duration)
		return
	}

	content := string(body)
	ts.addResult("File Reading", "PASS", fmt.Sprintf("Successfully read file '%s' (%d characters)", testFile, len(content)), "", duration)
}

// TestSearchFunctionality tests search functionality
func (ts *TestSuite) TestSearchFunctionality() {
	start := time.Now()

	// Test search terms
	searchTerms := []string{"logica", "matematica", "dados", "programacao", "computacao"}
	successCount := 0

	for _, term := range searchTerms {
		// Get all files first
		resp, err := ts.makeRequest("GET", "/vault/", nil)
		if err != nil {
			continue
		}

		var response struct {
			Files []string `json:"files"`
		}

		if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
			resp.Body.Close()
			continue
		}
		resp.Body.Close()

		// Search through files
		found := false
		for _, file := range response.Files {
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
					if strings.Contains(strings.ToLower(subFile), strings.ToLower(term)) {
						found = true
						break
					}

					// Check content for markdown files
					if strings.HasSuffix(strings.ToLower(subFile), ".md") {
						contentResp, err := ts.makeRequest("GET", "/vault/"+url.PathEscape(file+subFile), nil)
						if err != nil {
							continue
						}

						if contentResp.StatusCode == http.StatusOK {
							body, err := io.ReadAll(contentResp.Body)
							contentResp.Body.Close()
							if err == nil && strings.Contains(strings.ToLower(string(body)), strings.ToLower(term)) {
								found = true
								break
							}
						}
					}
				}
			} else {
				// File in root directory
				if strings.Contains(strings.ToLower(file), strings.ToLower(term)) {
					found = true
					break
				}

				// Check content for markdown files
				if strings.HasSuffix(strings.ToLower(file), ".md") {
					contentResp, err := ts.makeRequest("GET", "/vault/"+url.PathEscape(file), nil)
					if err != nil {
						continue
					}

					if contentResp.StatusCode == http.StatusOK {
						body, err := io.ReadAll(contentResp.Body)
						contentResp.Body.Close()
						if err == nil && strings.Contains(strings.ToLower(string(body)), strings.ToLower(term)) {
							found = true
							break
						}
					}
				}
			}

			if found {
				break
			}
		}

		if found {
			successCount++
		}
	}

	duration := time.Since(start).Milliseconds()

	if successCount == len(searchTerms) {
		ts.addResult("Search Functionality", "PASS", fmt.Sprintf("All %d search terms found results", len(searchTerms)), "", duration)
	} else if successCount > 0 {
		ts.addResult("Search Functionality", "PARTIAL", fmt.Sprintf("%d/%d search terms found results", successCount, len(searchTerms)), "", duration)
	} else {
		ts.addResult("Search Functionality", "FAIL", "No search terms found results", "", duration)
	}
}

// TestMCPServerConnection tests MCP server connectivity
func (ts *TestSuite) TestMCPServerConnection() {
	start := time.Now()

	mcpClient := &http.Client{
		Timeout: 10 * time.Second,
	}

	resp, err := mcpClient.Get("http://localhost:3010/health")
	duration := time.Since(start).Milliseconds()

	if err != nil {
		ts.addResult("MCP Server Connection", "FAIL", fmt.Sprintf("Connection failed: %v", err), "", duration)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		ts.addResult("MCP Server Connection", "FAIL", fmt.Sprintf("HTTP %d", resp.StatusCode), "", duration)
		return
	}

	ts.addResult("MCP Server Connection", "PASS", "MCP server is running and accessible", "", duration)
}

// TestMCPServerTools tests MCP server tools
func (ts *TestSuite) TestMCPServerTools() {
	start := time.Now()

	mcpClient := &http.Client{
		Timeout: 30 * time.Second,
	}

	// Test initialize
	initReq := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      1,
		"method":  "initialize",
		"params":  map[string]interface{}{},
	}

	initBody, _ := json.Marshal(initReq)
	resp, err := mcpClient.Post("http://localhost:3010/mcp", "application/json", strings.NewReader(string(initBody)))
	duration := time.Since(start).Milliseconds()

	if err != nil {
		ts.addResult("MCP Server Tools", "FAIL", fmt.Sprintf("Initialize request failed: %v", err), "", duration)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		ts.addResult("MCP Server Tools", "FAIL", fmt.Sprintf("Initialize HTTP %d", resp.StatusCode), "", duration)
		return
	}

	var initResponse map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&initResponse); err != nil {
		ts.addResult("MCP Server Tools", "FAIL", fmt.Sprintf("Initialize response decode failed: %v", err), "", duration)
		return
	}

	// Test tools/list
	toolsReq := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      2,
		"method":  "tools/list",
		"params":  map[string]interface{}{},
	}

	toolsBody, _ := json.Marshal(toolsReq)
	toolsResp, err := mcpClient.Post("http://localhost:3010/mcp", "application/json", strings.NewReader(string(toolsBody)))
	if err != nil {
		ts.addResult("MCP Server Tools", "FAIL", fmt.Sprintf("Tools list request failed: %v", err), "", duration)
		return
	}
	defer toolsResp.Body.Close()

	if toolsResp.StatusCode != http.StatusOK {
		ts.addResult("MCP Server Tools", "FAIL", fmt.Sprintf("Tools list HTTP %d", toolsResp.StatusCode), "", duration)
		return
	}

	var toolsResponse map[string]interface{}
	if err := json.NewDecoder(toolsResp.Body).Decode(&toolsResponse); err != nil {
		ts.addResult("MCP Server Tools", "FAIL", fmt.Sprintf("Tools list response decode failed: %v", err), "", duration)
		return
	}

	if result, ok := toolsResponse["result"].(map[string]interface{}); ok {
		if tools, ok := result["tools"].([]interface{}); ok {
			ts.addResult("MCP Server Tools", "PASS", fmt.Sprintf("MCP server initialized and %d tools available", len(tools)), "", duration)
		} else {
			ts.addResult("MCP Server Tools", "FAIL", "Tools list format invalid", "", duration)
		}
	} else {
		ts.addResult("MCP Server Tools", "FAIL", "Initialize response format invalid", "", duration)
	}
}

// RunAllTests runs all tests
func (ts *TestSuite) RunAllTests() {
	fmt.Println("🧪 COMPREHENSIVE TEST SUITE")
	fmt.Println("============================")
	fmt.Printf("🔗 Testing Obsidian API: %s\n", ts.baseURL)
	fmt.Printf("🔑 Using token: %s...\n", ts.token[:8])
	fmt.Println()

	// Run all tests
	ts.TestObsidianAPIConnection()
	ts.TestFileListing()
	ts.TestFileReading()
	ts.TestSearchFunctionality()
	ts.TestMCPServerConnection()
	ts.TestMCPServerTools()

	// Print results
	fmt.Println("📊 TEST RESULTS")
	fmt.Println("===============")

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

	if failed == 0 {
		fmt.Println("🎉 ALL TESTS PASSED! System is fully functional.")
	} else {
		fmt.Printf("⚠️ %d tests failed. Please review the issues above.\n", failed)
	}
}

func main() {
	// Configuration
	obsidianBaseURL := "https://127.0.0.1:27124"
	obsidianToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	// Create and run test suite
	testSuite := NewTestSuite(obsidianBaseURL, obsidianToken)
	testSuite.RunAllTests()
}
