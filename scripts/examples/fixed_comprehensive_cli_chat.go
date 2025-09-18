package main

import (
	"bufio"
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

// RealObsidianClient handles direct communication with Obsidian API
type RealObsidianClient struct {
	baseURL string
	token   string
	client  *http.Client
}

// NewRealObsidianClient creates a new Obsidian client
func NewRealObsidianClient(baseURL, token string) *RealObsidianClient {
	return &RealObsidianClient{
		baseURL: baseURL,
		token:   token,
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
	}
}

// makeRequest makes an authenticated request to Obsidian API
func (c *RealObsidianClient) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, c.baseURL+path, body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	return c.client.Do(req)
}

// ListFiles lists files in the vault
func (c *RealObsidianClient) ListFiles(path string) ([]string, error) {
	requestPath := "/vault/"
	if path != "" {
		cleanPath := strings.TrimPrefix(path, "/")
		requestPath += url.PathEscape(cleanPath)
	}

	resp, err := c.makeRequest("GET", requestPath, nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	var response struct {
		Files []string `json:"files"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	return response.Files, nil
}

// ReadFile reads content of a specific file
func (c *RealObsidianClient) ReadFile(filename string) (string, error) {
	// Clean filename and encode properly
	cleanFilename := strings.TrimPrefix(filename, "/")
	requestPath := fmt.Sprintf("/vault/%s", url.PathEscape(cleanFilename))

	resp, err := c.makeRequest("GET", requestPath, nil)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("failed to read file '%s': HTTP %d", filename, resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

// SearchFiles performs content search across files - FIXED VERSION
func (c *RealObsidianClient) SearchFiles(query string, maxResults int) ([]SearchResult, error) {
	// Get all files first
	files, err := c.ListFiles("")
	if err != nil {
		return nil, err
	}

	var results []SearchResult
	queryLower := strings.ToLower(query)

	fmt.Printf("🔍 Searching through %d files for '%s'...\n", len(files), query)

	// Search through files recursively
	for _, file := range files {
		if strings.HasSuffix(file, "/") {
			// This is a directory, search recursively
			subFiles, err := c.ListFiles(file)
			if err != nil {
				fmt.Printf("⚠️ Failed to list directory %s: %v\n", file, err)
				continue
			}

			for _, subFile := range subFiles {
				if strings.HasSuffix(subFile, "/") {
					continue // Skip subdirectories for now
				}

				fullPath := file + subFile

				// Check filename match
				fileName := strings.ToLower(subFile)
				if strings.Contains(fileName, queryLower) {
					results = append(results, SearchResult{
						File:    fullPath,
						Score:   0.9,
						Snippet: fmt.Sprintf("📁 Filename match: %s", subFile),
						Type:    "filename",
					})
					fmt.Printf("✅ Filename match: %s\n", fullPath)
				}

				// Check content match for markdown files
				if len(results) < maxResults && strings.HasSuffix(strings.ToLower(subFile), ".md") {
					content, err := c.ReadFile(fullPath)
					if err != nil {
						fmt.Printf("⚠️ Failed to read %s: %v\n", fullPath, err)
						continue
					}

					contentLower := strings.ToLower(content)
					if strings.Contains(contentLower, queryLower) {
						snippet := extractSnippet(content, queryLower)
						score := calculateContentScore(contentLower, queryLower)
						results = append(results, SearchResult{
							File:    fullPath,
							Score:   score,
							Snippet: snippet,
							Type:    "content",
						})
						fmt.Printf("✅ Content match: %s (score: %.2f)\n", fullPath, score)
					}
				}

				if len(results) >= maxResults {
					break
				}
			}
		} else {
			// This is a file in root directory
			// Check filename match
			fileName := strings.ToLower(file)
			if strings.Contains(fileName, queryLower) {
				results = append(results, SearchResult{
					File:    file,
					Score:   0.9,
					Snippet: fmt.Sprintf("📁 Filename match: %s", file),
					Type:    "filename",
				})
				fmt.Printf("✅ Filename match: %s\n", file)
			}

			// Check content match for markdown files
			if len(results) < maxResults && strings.HasSuffix(strings.ToLower(file), ".md") {
				content, err := c.ReadFile(file)
				if err != nil {
					fmt.Printf("⚠️ Failed to read %s: %v\n", file, err)
					continue
				}

				contentLower := strings.ToLower(content)
				if strings.Contains(contentLower, queryLower) {
					snippet := extractSnippet(content, queryLower)
					score := calculateContentScore(contentLower, queryLower)
					results = append(results, SearchResult{
						File:    file,
						Score:   score,
						Snippet: snippet,
						Type:    "content",
					})
					fmt.Printf("✅ Content match: %s (score: %.2f)\n", file, score)
				}
			}
		}

		if len(results) >= maxResults {
			break
		}
	}

	return results, nil
}

// SearchResult represents a search result
type SearchResult struct {
	File    string  `json:"file"`
	Score   float64 `json:"score"`
	Snippet string  `json:"snippet"`
	Type    string  `json:"type"`
}

// extractSnippet extracts a snippet around the search term
func extractSnippet(content, query string) string {
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
func calculateContentScore(content, query string) float64 {
	count := strings.Count(content, query)
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

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// max returns the maximum of two integers
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// ComprehensiveRealCLIChat represents the complete CLI chat system
type ComprehensiveRealCLIChat struct {
	obsidianClient *RealObsidianClient
	mcpServerURL   string
	mcpClient      *http.Client
	requestID      int
}

// NewComprehensiveRealCLIChat creates a new comprehensive CLI chat
func NewComprehensiveRealCLIChat(obsidianBaseURL, obsidianToken, mcpServerURL string) *ComprehensiveRealCLIChat {
	return &ComprehensiveRealCLIChat{
		obsidianClient: NewRealObsidianClient(obsidianBaseURL, obsidianToken),
		mcpServerURL:   mcpServerURL,
		mcpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		requestID: 1,
	}
}

// checkMCPServerHealth checks if MCP server is running
func (chat *ComprehensiveRealCLIChat) checkMCPServerHealth() error {
	resp, err := chat.mcpClient.Get(chat.mcpServerURL + "/health")
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("MCP server health check failed with status: %d", resp.StatusCode)
	}

	return nil
}

// processUserInput processes user input and determines the appropriate action
func (chat *ComprehensiveRealCLIChat) processUserInput(input string) {
	input = strings.TrimSpace(input)
	if input == "" {
		return
	}

	lowerInput := strings.ToLower(input)

	// Handle special commands
	if strings.HasPrefix(lowerInput, "/help") {
		chat.showHelp()
		return
	}

	if strings.HasPrefix(lowerInput, "/list") {
		chat.listVaultFiles()
		return
	}

	if strings.HasPrefix(lowerInput, "/read ") {
		filePath := strings.TrimSpace(input[6:])
		chat.readSpecificNote(filePath)
		return
	}

	if strings.HasPrefix(lowerInput, "/stats") {
		chat.showVaultStats()
		return
	}

	// Default: treat as search query using direct Obsidian API
	chat.performDirectSearch(input)
}

// performDirectSearch performs search using direct Obsidian API
func (chat *ComprehensiveRealCLIChat) performDirectSearch(query string) {
	fmt.Printf("🔍 Searching vault for: '%s'\n", query)
	fmt.Println("⏳ Processing with real Obsidian API...")

	results, err := chat.obsidianClient.SearchFiles(query, 10)
	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	if len(results) == 0 {
		fmt.Println("📝 No results found")
		return
	}

	fmt.Printf("✅ Found %d results:\n\n", len(results))

	for i, result := range results {
		fmt.Printf("%d. 📄 %s (Score: %.2f, Type: %s)\n", i+1, result.File, result.Score, result.Type)
		if result.Snippet != "" {
			fmt.Printf("   💬 %s\n", result.Snippet)
		}
		fmt.Println()
	}
}

// listVaultFiles lists vault files using direct API
func (chat *ComprehensiveRealCLIChat) listVaultFiles() {
	fmt.Println("📁 Listing vault files...")

	files, err := chat.obsidianClient.ListFiles("")
	if err != nil {
		fmt.Printf("❌ Failed to list files: %v\n", err)
		return
	}

	fmt.Printf("📁 Found %d files:\n\n", len(files))

	for i, file := range files {
		if i < 20 { // Show first 20 files
			fileType := "📄"
			if strings.HasSuffix(file, "/") {
				fileType = "📁"
			}
			fmt.Printf("%d. %s %s\n", i+1, fileType, file)
		}
	}

	if len(files) > 20 {
		fmt.Printf("... and %d more files\n", len(files)-20)
	}
}

// readSpecificNote reads a specific note using direct API
func (chat *ComprehensiveRealCLIChat) readSpecificNote(filePath string) {
	fmt.Printf("📖 Reading note: %s\n", filePath)

	content, err := chat.obsidianClient.ReadFile(filePath)
	if err != nil {
		fmt.Printf("❌ Failed to read note: %v\n", err)
		return
	}

	fmt.Printf("📄 CONTENT (%d characters):\n", len(content))
	fmt.Println("=" + strings.Repeat("=", 50))
	fmt.Println(content)
	fmt.Println("=" + strings.Repeat("=", 50))
}

// showVaultStats shows vault statistics using direct API
func (chat *ComprehensiveRealCLIChat) showVaultStats() {
	fmt.Println("📊 Getting vault statistics...")

	// Get file count using direct API
	files, err := chat.obsidianClient.ListFiles("")
	if err != nil {
		fmt.Printf("❌ Failed to get file count: %v\n", err)
		return
	}

	fileCount := len(files)
	folderCount := 0
	noteCount := 0

	for _, file := range files {
		if strings.HasSuffix(file, "/") {
			folderCount++
		} else if strings.HasSuffix(strings.ToLower(file), ".md") {
			noteCount++
		}
	}

	fmt.Println("📊 VAULT STATISTICS:")
	fmt.Println("===================")
	fmt.Printf("• Total files: %d\n", fileCount)
	fmt.Printf("• Folders: %d\n", folderCount)
	fmt.Printf("• Notes (.md): %d\n", noteCount)
	fmt.Printf("• Other files: %d\n", fileCount-folderCount-noteCount)
}

// showHelp shows help information
func (chat *ComprehensiveRealCLIChat) showHelp() {
	fmt.Println(`
🤖 COMPREHENSIVE REAL CLI CHAT HELP
===================================

🔍 SEARCH COMMANDS:
• Type any text to search the vault (direct API)
• /list - List all vault files
• /read <filename> - Read specific note
• /stats - Show vault statistics

🎯 EXAMPLES:
• Search: "logica", "programação", "computação"
• Read: /read "1- Notas Indice/CIÊNCIAS EXATAS.md"
• List: /list
• Stats: /stats

💡 TIP: All commands use REAL data from your Obsidian vault!
`)
}

// Run starts the comprehensive CLI chat session
func (chat *ComprehensiveRealCLIChat) Run() {
	fmt.Println(`
🚀 COMPREHENSIVE REAL CLI CHAT - FIXED VERSION
==============================================
Advanced AI-powered chat interface for your Obsidian vault
Using REAL data from Obsidian Local REST API endpoints

🔍 Checking connections...
`)

	// Check MCP server health
	if err := chat.checkMCPServerHealth(); err != nil {
		fmt.Printf("⚠️ MCP Server not available: %v\n", err)
		fmt.Println("💡 Continuing with direct Obsidian API access...")
	} else {
		fmt.Println("✅ MCP Server connected successfully!")
	}

	// Test direct Obsidian API
	fmt.Println("🔍 Testing direct Obsidian API...")
	files, err := chat.obsidianClient.ListFiles("")
	if err != nil {
		fmt.Printf("❌ Obsidian API not accessible: %v\n", err)
		fmt.Println("💡 Please ensure Obsidian is running with Local REST API plugin")
		return
	}

	fmt.Printf("✅ Obsidian API connected! Found %d files in vault\n", len(files))

	fmt.Println(`
🎯 READY TO CHAT WITH REAL VAULT DATA!
=====================================
Type your questions or commands. I can:
• Search your vault with real content
• Read and analyze notes
• Show vault statistics

Type /help for command reference or just start chatting!
`)

	// Start interactive loop
	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("💬 You: ")
		if !scanner.Scan() {
			break
		}

		input := scanner.Text()
		if strings.ToLower(input) == "exit" || strings.ToLower(input) == "quit" {
			fmt.Println("👋 Goodbye! Thanks for using Comprehensive Real CLI Chat!")
			break
		}

		chat.processUserInput(input)
		fmt.Println()
	}
}

func main() {
	// Configuration from environment variables or defaults
	obsidianBaseURL := os.Getenv("OBSIDIAN_BASE_URL")
	if obsidianBaseURL == "" {
		obsidianBaseURL = "https://127.0.0.1:27124"
	}

	obsidianToken := os.Getenv("OBSIDIAN_API_TOKEN")
	if obsidianToken == "" {
		obsidianToken = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	}

	mcpServerURL := os.Getenv("MCP_SERVER_URL")
	if mcpServerURL == "" {
		mcpServerURL = "http://localhost:3010"
	}

	// Create and run comprehensive chat
	chat := NewComprehensiveRealCLIChat(obsidianBaseURL, obsidianToken, mcpServerURL)
	chat.Run()
}
