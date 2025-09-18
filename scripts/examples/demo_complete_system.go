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

// DemoSystem represents the complete MCP system demo
type DemoSystem struct {
	serverURL string
	client    *http.Client
}

// NewDemoSystem creates a new demo system
func NewDemoSystem() *DemoSystem {
	return &DemoSystem{
		serverURL: "http://localhost:8081",
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// checkServerHealth checks if the MCP server is running
func (demo *DemoSystem) checkServerHealth() bool {
	resp, err := demo.client.Get(demo.serverURL + "/health")
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	return resp.StatusCode == http.StatusOK
}

// sendMCPRequest sends a request to the MCP server
func (demo *DemoSystem) sendMCPRequest(method string, params interface{}) (map[string]interface{}, error) {
	request := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      1,
		"method":  method,
		"params":  params,
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, err
	}

	resp, err := demo.client.Post(demo.serverURL+"/mcp", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result map[string]interface{}
	err = json.Unmarshal(body, &result)
	if err != nil {
		return nil, err
	}

	return result, nil
}

// callMCPTool calls a specific MCP tool
func (demo *DemoSystem) callMCPTool(toolName string, arguments map[string]interface{}) (map[string]interface{}, error) {
	return demo.sendMCPRequest("tools/call", map[string]interface{}{
		"name":      toolName,
		"arguments": arguments,
	})
}

// listMCPTools lists all available MCP tools
func (demo *DemoSystem) listMCPTools() (map[string]interface{}, error) {
	return demo.sendMCPRequest("tools/list", map[string]interface{}{})
}

// demonstrateSearchVault demonstrates the search_vault tool
func (demo *DemoSystem) demonstrateSearchVault() {
	fmt.Println("🔍 DEMONSTRATING SEARCH_VAULT TOOL")
	fmt.Println("==================================")

	// Test search
	result, err := demo.callMCPTool("search_vault", map[string]interface{}{
		"query":       "matematica",
		"max_results": 5,
	})

	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	if error, ok := result["error"]; ok {
		fmt.Printf("❌ Search error: %v\n", error)
		return
	}

	if resultData, ok := result["result"].(map[string]interface{}); ok {
		if results, ok := resultData["results"].([]interface{}); ok {
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
		}
	}
}

// demonstrateReadNote demonstrates the read_note tool
func (demo *DemoSystem) demonstrateReadNote() {
	fmt.Println("📖 DEMONSTRATING READ_NOTE TOOL")
	fmt.Println("================================")

	// Test reading a note
	result, err := demo.callMCPTool("read_note", map[string]interface{}{
		"file_path": "Matematica_Home.md",
	})

	if err != nil {
		fmt.Printf("❌ Read note failed: %v\n", err)
		return
	}

	if error, ok := result["error"]; ok {
		fmt.Printf("❌ Read note error: %v\n", error)
		return
	}

	if resultData, ok := result["result"].(map[string]interface{}); ok {
		if content, ok := resultData["content"].(string); ok {
			fmt.Printf("✅ Successfully read note:\n")
			fmt.Printf("📄 Content preview: %s\n", content[:min(200, len(content))])
		}
	}
}

// demonstrateListFiles demonstrates the list_files tool
func (demo *DemoSystem) demonstrateListFiles() {
	fmt.Println("📁 DEMONSTRATING LIST_FILES TOOL")
	fmt.Println("=================================")

	// Test listing files
	result, err := demo.callMCPTool("list_files", map[string]interface{}{
		"path":      "",
		"recursive": false,
	})

	if err != nil {
		fmt.Printf("❌ List files failed: %v\n", err)
		return
	}

	if error, ok := result["error"]; ok {
		fmt.Printf("❌ List files error: %v\n", error)
		return
	}

	if resultData, ok := result["result"].(map[string]interface{}); ok {
		if files, ok := resultData["files"].([]interface{}); ok {
			fmt.Printf("✅ Found %d files:\n\n", len(files))

			for i, file := range files {
				if i < 10 { // Show first 10 files
					fmt.Printf("%d. %v\n", i+1, file)
				}
			}

			if len(files) > 10 {
				fmt.Printf("... and %d more files\n", len(files)-10)
			}
		}
	}
}

// demonstrateGetVaultStats demonstrates the get_vault_stats tool
func (demo *DemoSystem) demonstrateGetVaultStats() {
	fmt.Println("📊 DEMONSTRATING GET_VAULT_STATS TOOL")
	fmt.Println("=====================================")

	// Test getting vault stats
	result, err := demo.callMCPTool("get_vault_stats", map[string]interface{}{})

	if err != nil {
		fmt.Printf("❌ Get vault stats failed: %v\n", err)
		return
	}

	if error, ok := result["error"]; ok {
		fmt.Printf("❌ Get vault stats error: %v\n", error)
		return
	}

	if resultData, ok := result["result"].(map[string]interface{}); ok {
		fmt.Printf("✅ Vault Statistics:\n")
		for key, value := range resultData {
			fmt.Printf("• %s: %v\n", key, value)
		}
	}
}

// demonstrateAnalyzeContent demonstrates the analyze_content tool
func (demo *DemoSystem) demonstrateAnalyzeContent() {
	fmt.Println("🧠 DEMONSTRATING ANALYZE_CONTENT TOOL")
	fmt.Println("=====================================")

	// Test content analysis
	result, err := demo.callMCPTool("analyze_content", map[string]interface{}{
		"content":       "This is a test document about mathematics and algorithms.",
		"analysis_type": "summary",
	})

	if err != nil {
		fmt.Printf("❌ Analyze content failed: %v\n", err)
		return
	}

	if error, ok := result["error"]; ok {
		fmt.Printf("❌ Analyze content error: %v\n", error)
		return
	}

	if resultData, ok := result["result"].(map[string]interface{}); ok {
		fmt.Printf("✅ Content Analysis Result:\n")
		for key, value := range resultData {
			fmt.Printf("• %s: %v\n", key, value)
		}
	}
}

// demonstrateInteractiveChat demonstrates the interactive chat functionality
func (demo *DemoSystem) demonstrateInteractiveChat() {
	fmt.Println("💬 DEMONSTRATING INTERACTIVE CHAT")
	fmt.Println("==================================")
	fmt.Println("This would be the interactive chat interface...")
	fmt.Println("Type 'exit' to return to demo menu")

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("💬 You: ")
		if !scanner.Scan() {
			break
		}

		input := scanner.Text()
		if strings.ToLower(input) == "exit" {
			break
		}

		// Simulate chat response
		fmt.Printf("🤖 MCP Assistant: I understand you want to search for '%s'. Let me help you with that!\n", input)

		// Perform search
		result, err := demo.callMCPTool("search_vault", map[string]interface{}{
			"query":       input,
			"max_results": 3,
		})

		if err == nil && result["error"] == nil {
			if resultData, ok := result["result"].(map[string]interface{}); ok {
				if results, ok := resultData["results"].([]interface{}); ok {
					fmt.Printf("🔍 Found %d results for '%s':\n", len(results), input)
					for i, item := range results {
						if resultMap, ok := item.(map[string]interface{}); ok {
							file := resultMap["file"].(string)
							fmt.Printf("  %d. %s\n", i+1, file)
						}
					}
				}
			}
		}
		fmt.Println()
	}
}

// showMenu shows the demo menu
func (demo *DemoSystem) showMenu() {
	fmt.Println(`
🎯 COMPLETE MCP SYSTEM DEMO
==========================
Choose a demonstration:

1. 🔍 Search Vault Tool
2. 📖 Read Note Tool  
3. 📁 List Files Tool
4. 📊 Vault Statistics Tool
5. 🧠 Analyze Content Tool
6. 💬 Interactive Chat Demo
7. 🛠️ List All MCP Tools
8. ❓ Help
9. 🚪 Exit

Enter your choice (1-9): `)
}

// showHelp shows help information
func (demo *DemoSystem) showHelp() {
	fmt.Println(`
🤖 COMPLETE MCP SYSTEM HELP
===========================

This demo showcases all MCP server capabilities:

🔍 SEARCH_VAULT: Advanced search with 7 algorithms
📖 READ_NOTE: Read individual notes from vault
📁 LIST_FILES: Browse vault directory structure
📊 GET_VAULT_STATS: Get comprehensive vault statistics
🧠 ANALYZE_CONTENT: Analyze content using AI algorithms
💬 INTERACTIVE_CHAT: Natural language interface

🎯 FEATURES:
• Real-time vault integration
• Advanced search algorithms (BM25-TFIDF, MetadataBoost, etc.)
• Case-insensitive search
• Content analysis and summarization
• Natural language processing
• JSON-RPC 2.0 protocol compliance

💡 TIP: Each tool demonstrates real functionality with your Obsidian vault!
`)
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Run starts the demo system
func (demo *DemoSystem) Run() {
	fmt.Println(`
🚀 COMPLETE MCP SYSTEM DEMONSTRATION
====================================
Advanced AI-powered MCP server with full Obsidian vault integration
Powered by 5 sophisticated tools and 7 search algorithms

🔍 Checking MCP server connection...
`)

	// Check server health
	if !demo.checkServerHealth() {
		fmt.Println("❌ MCP Server not available!")
		fmt.Println("💡 Please start the MCP server first:")
		fmt.Println("   go run mcp_server_main.go")
		return
	}

	fmt.Println("✅ MCP Server connected successfully!")
	fmt.Println("🎯 Ready to demonstrate all features!")
	fmt.Println()

	// Main demo loop
	scanner := bufio.NewScanner(os.Stdin)
	for {
		demo.showMenu()

		if !scanner.Scan() {
			break
		}

		choice := strings.TrimSpace(scanner.Text())

		switch choice {
		case "1":
			demo.demonstrateSearchVault()
		case "2":
			demo.demonstrateReadNote()
		case "3":
			demo.demonstrateListFiles()
		case "4":
			demo.demonstrateGetVaultStats()
		case "5":
			demo.demonstrateAnalyzeContent()
		case "6":
			demo.demonstrateInteractiveChat()
		case "7":
			fmt.Println("🛠️ AVAILABLE MCP TOOLS:")
			fmt.Println("========================")
			if tools, err := demo.listMCPTools(); err == nil {
				if resultData, ok := tools["result"].(map[string]interface{}); ok {
					if toolList, ok := resultData["tools"].([]interface{}); ok {
						for i, tool := range toolList {
							if toolMap, ok := tool.(map[string]interface{}); ok {
								name := toolMap["name"].(string)
								description := toolMap["description"].(string)
								fmt.Printf("%d. %s: %s\n", i+1, name, description)
							}
						}
					}
				}
			}
		case "8":
			demo.showHelp()
		case "9":
			fmt.Println("👋 Thank you for using the Complete MCP System Demo!")
			return
		default:
			fmt.Println("❌ Invalid choice. Please enter 1-9.")
		}

		fmt.Println("\nPress Enter to continue...")
		scanner.Scan()
		fmt.Println()
	}
}

func main() {
	demo := NewDemoSystem()
	demo.Run()
}
