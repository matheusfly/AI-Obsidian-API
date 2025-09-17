package main

import (
	"bufio"
	"bytes"
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
		requestPath += url.QueryEscape(path)
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
	requestPath := fmt.Sprintf("/vault/%s", url.QueryEscape(filename))
	
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

// SearchFiles performs content search across files
func (c *RealObsidianClient) SearchFiles(query string, maxResults int) ([]SearchResult, error) {
	// Get all files first
	files, err := c.ListFiles("")
	if err != nil {
		return nil, err
	}
	
	var results []SearchResult
	queryLower := strings.ToLower(query)
	
	// Search through files recursively
	for _, file := range files {
		if strings.HasSuffix(file, "/") {
			// This is a directory, search recursively
			subFiles, err := c.ListFiles(file)
			if err == nil {
				for _, subFile := range subFiles {
					if strings.HasSuffix(subFile, "/") {
						continue // Skip subdirectories for now
					}
					
					// Check filename match
					fileName := strings.ToLower(subFile)
					if strings.Contains(fileName, queryLower) {
						results = append(results, SearchResult{
							File:    file + subFile,
							Score:   0.9,
							Snippet: fmt.Sprintf("📁 Filename match: %s", file + subFile),
							Type:    "filename",
						})
					}
					
					// Check content match for markdown files
					if len(results) < maxResults && strings.HasSuffix(strings.ToLower(subFile), ".md") {
						content, err := c.ReadFile(file + subFile)
						if err == nil {
							contentLower := strings.ToLower(content)
							if strings.Contains(contentLower, queryLower) {
								snippet := extractSnippet(content, queryLower)
								score := calculateContentScore(contentLower, queryLower)
								results = append(results, SearchResult{
									File:    file + subFile,
									Score:   score,
									Snippet: snippet,
									Type:    "content",
								})
							}
						}
					}
					
					if len(results) >= maxResults {
						break
					}
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
			}
			
			// Check content match for markdown files
			if len(results) < maxResults && strings.HasSuffix(strings.ToLower(file), ".md") {
				content, err := c.ReadFile(file)
				if err == nil {
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
					}
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

// MCPRequest represents a JSON-RPC request
type MCPRequest struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      int         `json:"id"`
	Method  string      `json:"method"`
	Params  interface{} `json:"params"`
}

// MCPResponse represents a JSON-RPC response
type MCPResponse struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      int         `json:"id"`
	Result  interface{} `json:"result"`
	Error   *MCPError   `json:"error,omitempty"`
}

// MCPError represents an MCP error
type MCPError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

// sendMCPRequest sends a request to the MCP server
func (chat *ComprehensiveRealCLIChat) sendMCPRequest(method string, params interface{}) (*MCPResponse, error) {
	request := MCPRequest{
		JSONRPC: "2.0",
		ID:      chat.requestID,
		Method:  method,
		Params:  params,
	}
	chat.requestID++

	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, err
	}

	resp, err := chat.mcpClient.Post(chat.mcpServerURL+"/mcp", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var mcpResp MCPResponse
	err = json.Unmarshal(body, &mcpResp)
	if err != nil {
		return nil, err
	}

	return &mcpResp, nil
}

// callMCPTool calls a specific MCP tool
func (chat *ComprehensiveRealCLIChat) callMCPTool(toolName string, arguments map[string]interface{}) (*MCPResponse, error) {
	return chat.sendMCPRequest("tools/call", map[string]interface{}{
		"name":      toolName,
		"arguments": arguments,
	})
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

	if strings.HasPrefix(lowerInput, "/create ") {
		parts := strings.SplitN(input[8:], " ", 2)
		if len(parts) == 2 {
			chat.createNote(parts[0], parts[1])
		} else {
			fmt.Println("❌ Usage: /create <filename> <content>")
		}
		return
	}

	if strings.HasPrefix(lowerInput, "/search ") {
		query := strings.TrimSpace(input[8:])
		chat.performAdvancedSearch(query)
		return
	}

	if strings.HasPrefix(lowerInput, "/semantic ") {
		query := strings.TrimSpace(input[10:])
		chat.performSemanticSearch(query)
		return
	}

	if strings.HasPrefix(lowerInput, "/stats") {
		chat.showVaultStats()
		return
	}

	if strings.HasPrefix(lowerInput, "/analyze") {
		chat.analyzeVaultLinks()
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

// performAdvancedSearch performs search using MCP tools
func (chat *ComprehensiveRealCLIChat) performAdvancedSearch(query string) {
	fmt.Printf("🔍 Advanced search for: '%s'\n", query)
	fmt.Println("⏳ Processing with MCP tools...")

	resp, err := chat.callMCPTool("search_vault", map[string]interface{}{
		"query": query,
		"limit": 10,
	})
	if err != nil {
		fmt.Printf("❌ Advanced search failed: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ Advanced search error: %s\n", resp.Error.Message)
		return
	}

	if result, ok := resp.Result.(map[string]interface{}); ok {
		if results, ok := result["results"].([]interface{}); ok {
			fmt.Printf("✅ Found %d results:\n\n", len(results))
			
			for i, item := range results {
				if resultMap, ok := item.(map[string]interface{}); ok {
					file := resultMap["path"].(string)
					score := resultMap["score"].(float64)
					fmt.Printf("%d. 📄 %s (Score: %.2f)\n", i+1, file, score)
				}
			}
		} else {
			fmt.Println("📝 No results found")
		}
	}
}

// performSemanticSearch performs semantic search using MCP tools
func (chat *ComprehensiveRealCLIChat) performSemanticSearch(query string) {
	fmt.Printf("🧠 Semantic search for: '%s'\n", query)
	fmt.Println("⏳ Processing with DeepSeek-R1:8B...")

	resp, err := chat.callMCPTool("semantic_search", map[string]interface{}{
		"query": query,
		"top_k": 5,
	})
	if err != nil {
		fmt.Printf("❌ Semantic search failed: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ Semantic search error: %s\n", resp.Error.Message)
		return
	}

	if result, ok := resp.Result.(map[string]interface{}); ok {
		if results, ok := result["results"].([]interface{}); ok {
			fmt.Printf("✅ Found %d semantic results:\n\n", len(results))
			
			for i, item := range results {
				if resultMap, ok := item.(map[string]interface{}); ok {
					file := resultMap["path"].(string)
					score := resultMap["score"].(float64)
					title := resultMap["title"].(string)
					fmt.Printf("%d. 📄 %s - %s (Score: %.2f)\n", i+1, file, title, score)
				}
			}
		} else {
			fmt.Println("📝 No semantic results found")
		}
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

// createNote creates a new note using MCP tools
func (chat *ComprehensiveRealCLIChat) createNote(filename, content string) {
	fmt.Printf("📝 Creating note: %s\n", filename)
	
	resp, err := chat.callMCPTool("create_note", map[string]interface{}{
		"path":    filename,
		"content": content,
	})
	if err != nil {
		fmt.Printf("❌ Failed to create note: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ Create note error: %s\n", resp.Error.Message)
		return
	}

	fmt.Printf("✅ Note '%s' created successfully!\n", filename)
}

// showVaultStats shows vault statistics using MCP tools
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

// analyzeVaultLinks analyzes vault links using MCP tools
func (chat *ComprehensiveRealCLIChat) analyzeVaultLinks() {
	fmt.Println("🔗 Analyzing vault links...")
	
	resp, err := chat.callMCPTool("analyze_links", map[string]interface{}{})
	if err != nil {
		fmt.Printf("❌ Failed to analyze links: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ Analyze links error: %s\n", resp.Error.Message)
		return
	}

	if result, ok := resp.Result.(map[string]interface{}); ok {
		fmt.Println("🔗 LINK ANALYSIS:")
		fmt.Println("==================")
		for key, value := range result {
			fmt.Printf("• %s: %v\n", key, value)
		}
	}
}

// showHelp shows help information
func (chat *ComprehensiveRealCLIChat) showHelp() {
	fmt.Println(`
🤖 COMPREHENSIVE REAL CLI CHAT HELP
===================================

🔍 SEARCH COMMANDS:
• Type any text to search the vault (direct API)
• /search <query> - Advanced search using MCP tools
• /semantic <query> - Semantic search using DeepSeek-R1:8B

📋 FILE COMMANDS:
• /list - List all vault files
• /read <filename> - Read specific note
• /create <filename> <content> - Create new note

📊 ANALYSIS COMMANDS:
• /stats - Show vault statistics
• /analyze - Analyze note links

🎯 EXAMPLES:
• Search: "matematica" or "performance"
• Advanced: /search "algorithms"
• Semantic: /semantic "machine learning concepts"
• Read: /read "Matematica_Home.md"
• Create: /create "test.md" "# Test Note\nThis is a test."

💡 TIP: All commands use REAL data from your Obsidian vault!
`)
}

// Run starts the comprehensive CLI chat session
func (chat *ComprehensiveRealCLIChat) Run() {
	fmt.Println(`
🚀 COMPREHENSIVE REAL CLI CHAT
==============================
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
• Create new notes
• Show vault statistics
• Analyze note connections

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
