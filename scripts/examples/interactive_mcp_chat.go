package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

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

// ToolCall represents a tool call request
type ToolCall struct {
	Name      string                 `json:"name"`
	Arguments map[string]interface{} `json:"arguments"`
}

// SearchResult represents a search result
type SearchResult struct {
	File    string  `json:"file"`
	Score   float64 `json:"score"`
	Snippet string  `json:"snippet"`
	Type    string  `json:"type"`
}

// InteractiveMCPChat represents the interactive chat client
type InteractiveMCPChat struct {
	serverURL string
	client    *http.Client
	requestID int
}

// NewInteractiveMCPChat creates a new interactive chat client
func NewInteractiveMCPChat(serverURL string) *InteractiveMCPChat {
	return &InteractiveMCPChat{
		serverURL: serverURL,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
		requestID: 1,
	}
}

// sendRequest sends a request to the MCP server
func (chat *InteractiveMCPChat) sendRequest(method string, params interface{}) (*MCPResponse, error) {
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

	resp, err := chat.client.Post(chat.serverURL+"/mcp", "application/json", bytes.NewBuffer(jsonData))
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

// callTool calls a specific MCP tool
func (chat *InteractiveMCPChat) callTool(toolName string, arguments map[string]interface{}) (*MCPResponse, error) {
	return chat.sendRequest("tools/call", map[string]interface{}{
		"name":      toolName,
		"arguments": arguments,
	})
}

// listTools lists all available MCP tools
func (chat *InteractiveMCPChat) listTools() (*MCPResponse, error) {
	return chat.sendRequest("tools/list", map[string]interface{}{})
}

// searchVault searches the vault using MCP tools
func (chat *InteractiveMCPChat) searchVault(query string, maxResults int) (*MCPResponse, error) {
	return chat.callTool("search_vault", map[string]interface{}{
		"query":       query,
		"max_results": maxResults,
	})
}

// readNote reads a specific note using MCP tools
func (chat *InteractiveMCPChat) readNote(filePath string) (*MCPResponse, error) {
	return chat.callTool("read_note", map[string]interface{}{
		"file_path": filePath,
	})
}

// listFiles lists files in the vault using MCP tools
func (chat *InteractiveMCPChat) listFiles(path string, recursive bool) (*MCPResponse, error) {
	return chat.callTool("list_files", map[string]interface{}{
		"path":      path,
		"recursive": recursive,
	})
}

// getVaultStats gets vault statistics using MCP tools
func (chat *InteractiveMCPChat) getVaultStats() (*MCPResponse, error) {
	return chat.callTool("get_vault_stats", map[string]interface{}{})
}

// analyzeContent analyzes content using MCP tools
func (chat *InteractiveMCPChat) analyzeContent(content string, analysisType string) (*MCPResponse, error) {
	return chat.callTool("analyze_content", map[string]interface{}{
		"content":        content,
		"analysis_type":  analysisType,
	})
}

// checkServerHealth checks if the MCP server is healthy
func (chat *InteractiveMCPChat) checkServerHealth() error {
	resp, err := chat.client.Get(chat.serverURL + "/health")
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("server health check failed with status: %d", resp.StatusCode)
	}

	return nil
}

// processUserInput processes user input and determines the appropriate action
func (chat *InteractiveMCPChat) processUserInput(input string) {
	input = strings.TrimSpace(input)
	if input == "" {
		return
	}

	// Convert to lowercase for command detection
	lowerInput := strings.ToLower(input)

	// Handle special commands
	if strings.HasPrefix(lowerInput, "/help") {
		chat.showHelp()
		return
	}

	if strings.HasPrefix(lowerInput, "/stats") {
		chat.showVaultStats()
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

	if strings.HasPrefix(lowerInput, "/analyze ") {
		parts := strings.SplitN(input[9:], " ", 2)
		if len(parts) == 2 {
			chat.analyzeSpecificContent(parts[0], parts[1])
		} else {
			fmt.Println("❌ Usage: /analyze <type> <content>")
		}
		return
	}

	// Default: treat as search query
	chat.performSearch(input)
}

// performSearch performs a search using MCP tools
func (chat *InteractiveMCPChat) performSearch(query string) {
	fmt.Printf("🔍 Searching for: '%s'\n", query)
	fmt.Println("⏳ Processing...")

	resp, err := chat.searchVault(query, 10)
	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ Search error: %s\n", resp.Error.Message)
		return
	}

	// Parse search results
	if result, ok := resp.Result.(map[string]interface{}); ok {
		if results, ok := result["results"].([]interface{}); ok {
			fmt.Printf("✅ Found %d results:\n\n", len(results))
			
			for i, item := range results {
				if resultMap, ok := item.(map[string]interface{}); ok {
					file := resultMap["file"].(string)
					score := resultMap["score"].(float64)
					snippet := resultMap["snippet"].(string)
					
					fmt.Printf("%d. 📄 %s (Score: %.2f)\n", i+1, file, score)
					if snippet != "" {
						fmt.Printf("   💬 %s\n", snippet)
					}
					fmt.Println()
				}
			}
		} else {
			fmt.Println("📝 No results found")
		}
	}
}

// showVaultStats shows vault statistics
func (chat *InteractiveMCPChat) showVaultStats() {
	fmt.Println("📊 Getting vault statistics...")
	
	resp, err := chat.getVaultStats()
	if err != nil {
		fmt.Printf("❌ Failed to get stats: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ Stats error: %s\n", resp.Error.Message)
		return
	}

	if stats, ok := resp.Result.(map[string]interface{}); ok {
		fmt.Println("📊 VAULT STATISTICS:")
		fmt.Println("===================")
		for key, value := range stats {
			fmt.Printf("• %s: %v\n", key, value)
		}
	}
}

// listVaultFiles lists vault files
func (chat *InteractiveMCPChat) listVaultFiles() {
	fmt.Println("📁 Listing vault files...")
	
	resp, err := chat.listFiles("", true)
	if err != nil {
		fmt.Printf("❌ Failed to list files: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ List error: %s\n", resp.Error.Message)
		return
	}

	if result, ok := resp.Result.(map[string]interface{}); ok {
		if files, ok := result["files"].([]interface{}); ok {
			fmt.Printf("📁 Found %d files:\n\n", len(files))
			
			for i, file := range files {
				if i < 20 { // Show first 20 files
					fmt.Printf("%d. %v\n", i+1, file)
				}
			}
			
			if len(files) > 20 {
				fmt.Printf("... and %d more files\n", len(files)-20)
			}
		}
	}
}

// readSpecificNote reads a specific note
func (chat *InteractiveMCPChat) readSpecificNote(filePath string) {
	fmt.Printf("📖 Reading note: %s\n", filePath)
	
	resp, err := chat.readNote(filePath)
	if err != nil {
		fmt.Printf("❌ Failed to read note: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ Read error: %s\n", resp.Error.Message)
		return
	}

	if result, ok := resp.Result.(map[string]interface{}); ok {
		if content, ok := result["content"].(string); ok {
			fmt.Printf("📄 CONTENT:\n%s\n", content)
		}
	}
}

// analyzeSpecificContent analyzes specific content
func (chat *InteractiveMCPChat) analyzeSpecificContent(analysisType, content string) {
	fmt.Printf("🧠 Analyzing content (%s): %s\n", analysisType, content[:min(50, len(content))])
	
	resp, err := chat.analyzeContent(content, analysisType)
	if err != nil {
		fmt.Printf("❌ Failed to analyze content: %v\n", err)
		return
	}

	if resp.Error != nil {
		fmt.Printf("❌ Analysis error: %s\n", resp.Error.Message)
		return
	}

	if result, ok := resp.Result.(map[string]interface{}); ok {
		fmt.Printf("📊 ANALYSIS RESULT:\n%v\n", result)
	}
}

// showHelp shows help information
func (chat *InteractiveMCPChat) showHelp() {
	fmt.Println(`
🤖 INTERACTIVE MCP CHAT HELP
============================

🔍 SEARCH COMMANDS:
• Type any text to search the vault
• Example: "matematica", "performance", "algorithms"

📋 SPECIAL COMMANDS:
• /help          - Show this help
• /stats         - Show vault statistics  
• /list          - List all vault files
• /read <file>   - Read specific note
• /analyze <type> <content> - Analyze content

🎯 EXAMPLES:
• Search: "monge da alta performance"
• Read: /read "Matematica_Home.md"
• Analyze: /analyze summary "This is a test content"
• Stats: /stats

💡 TIP: Just type naturally - I'll understand what you want!
`)
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Run starts the interactive chat session
func (chat *InteractiveMCPChat) Run() {
	fmt.Println(`
🚀 INTERACTIVE MCP CHAT
========================
Advanced AI-powered chat interface for your Obsidian vault
Powered by MCP Server with 5 sophisticated tools

🔍 Checking MCP server connection...
`)

	// Check server health
	if err := chat.checkServerHealth(); err != nil {
		fmt.Printf("❌ MCP Server not available: %v\n", err)
		fmt.Println("💡 Make sure the MCP server is running on port 8081")
		return
	}

	fmt.Println("✅ MCP Server connected successfully!")
	
	// List available tools
	resp, err := chat.listTools()
	if err != nil {
		fmt.Printf("⚠️ Could not list tools: %v\n", err)
	} else {
		if result, ok := resp.Result.(map[string]interface{}); ok {
			if tools, ok := result["tools"].([]interface{}); ok {
				fmt.Printf("🛠️ Available tools: %d\n", len(tools))
			}
		}
	}

	fmt.Println(`
🎯 READY TO CHAT!
=================
Type your questions or commands. I can:
• Search your vault intelligently
• Read and analyze notes
• Show vault statistics
• Help you navigate your knowledge

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
			fmt.Println("👋 Goodbye! Thanks for using Interactive MCP Chat!")
			break
		}

		chat.processUserInput(input)
		fmt.Println()
	}
}

func main() {
	// Configuration
	serverURL := "http://localhost:8081"
	if envURL := os.Getenv("MCP_SERVER_URL"); envURL != "" {
		serverURL = envURL
	}

	// Create and run interactive chat
	chat := NewInteractiveMCPChat(serverURL)
	chat.Run()
}
