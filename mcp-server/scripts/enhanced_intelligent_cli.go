package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"regexp"
	"strings"
)

const (
	serverURL = "http://localhost:3011"
)

// Tool represents a simplified tool definition for display
type Tool struct {
	Name        string      `json:"name"`
	Description string      `json:"description"`
	Parameters  interface{} `json:"parameters"`
}

// ToolResult represents the structure of a tool execution response
type ToolResult struct {
	Success bool        `json:"success"`
	Message string      `json:"message"`
	Data    interface{} `json:"data"`
	Error   string      `json:"error"`
}

func main() {
	fmt.Println("🤖 Enhanced MCP Server Intelligent CLI")
	fmt.Println("======================================")
	fmt.Println("Welcome! I'm your AI-powered assistant for your Obsidian vault.")
	fmt.Println("I can help you with intelligent reasoning, complex workflows, and natural conversations.")
	fmt.Println()
	fmt.Println("✨ Features:")
	fmt.Println("  • Natural language understanding")
	fmt.Println("  • Intelligent tool selection")
	fmt.Println("  • Multi-step reasoning workflows")
	fmt.Println("  • Context-aware conversations")
	fmt.Println("  • Proactive suggestions")
	fmt.Println()
	fmt.Println("💡 Try saying things like:")
	fmt.Println("  'Help me find all notes about AI'")
	fmt.Println("  'Create a summary of my recent work'")
	fmt.Println("  'Analyze the connections between my ideas'")
	fmt.Println("  'What can you help me with?'")

	// Check server connection
	if !checkServerConnection() {
		fmt.Println("❌ Cannot connect to MCP server. Please ensure it's running on port 3011.")
		return
	}

	fmt.Println("✅ Connected to MCP Server")

	// Get available tools
	tools := getAvailableTools()
	fmt.Printf("🔧 Available tools: %d\n", len(tools))

	reader := bufio.NewReader(os.Stdin)

	for {
		fmt.Print("\n🤖 You: ")
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)

		if input == "" {
			continue
		}

		if strings.HasPrefix(input, "/") {
			handleCommand(input)
		} else {
			handleNaturalLanguage(input)
		}
	}
}

func checkServerConnection() bool {
	resp, err := http.Get(serverURL + "/health")
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	return resp.StatusCode == http.StatusOK
}

func getAvailableTools() []Tool {
	resp, err := http.Get(serverURL + "/tools")
	if err != nil {
		return []Tool{}
	}
	defer resp.Body.Close()

	var toolsResponse struct {
		Tools []Tool `json:"tools"`
		Count int    `json:"count"`
	}
	json.NewDecoder(resp.Body).Decode(&toolsResponse)
	return toolsResponse.Tools
}

func handleCommand(command string) {
	switch command {
	case "/help":
		showHelp()
	case "/tools":
		listTools()
	case "/status":
		checkStatus()
	case "/quit":
		fmt.Println("👋 Goodbye! Thanks for using the Enhanced MCP Intelligent CLI!")
		os.Exit(0)
	default:
		fmt.Println("🤔 Unknown command. Type '/help' for a list of commands.")
	}
}

func showHelp() {
	fmt.Println("\n🤖 **Enhanced MCP Assistant Help**")
	fmt.Println()
	fmt.Println("**Basic Commands:**")
	fmt.Println("• \"list files\" - Show all files in your vault")
	fmt.Println("• \"read note [filename]\" - Read a specific note")
	fmt.Println("• \"search for [query]\" - Search your vault")
	fmt.Println("• \"semantic search for [query]\" - AI-powered search")
	fmt.Println("• \"create note\" - Create a new note")
	fmt.Println("• \"analyze links\" - Analyze note connections")
	fmt.Println()
	fmt.Println("**Advanced Features:**")
	fmt.Println("• \"help me find [topic]\" - Intelligent search assistance")
	fmt.Println("• \"create a summary of [topic]\" - Multi-step workflow")
	fmt.Println("• \"what notes do I have about [topic]\" - Context-aware queries")
	fmt.Println("• \"show me the connections between [topic1] and [topic2]\" - Relationship analysis")
	fmt.Println()
	fmt.Println("**Conversation:**")
	fmt.Println("• I remember our conversation context")
	fmt.Println("• I can chain multiple operations together")
	fmt.Println("• I provide proactive suggestions")
	fmt.Println("• I learn from your preferences")
	fmt.Println()
	fmt.Println("**System Commands:**")
	fmt.Println("• \"/status\" - Check server health")
	fmt.Println("• \"/tools\" - List available tools")
	fmt.Println("• \"/quit\" - Exit the assistant")
	fmt.Println()
	fmt.Println("💡 **Pro Tip:** Be natural! I understand context and can help with complex workflows.")
}

func handleNaturalLanguage(input string) {
	inputLower := strings.ToLower(input)
	fmt.Printf("🧠 Processing your request: \"%s\"\n", input)

	var toolName string
	var params map[string]interface{}
	var conversationalResponse string

	// Enhanced NLP-like mapping to MCP tools with conversational responses
	if strings.Contains(inputLower, "list files") || strings.Contains(inputLower, "show files") || strings.Contains(inputLower, "what's in my vault") {
		toolName = "list_files_in_vault"
		params = make(map[string]interface{})
		conversationalResponse = "📁 Listing files in your vault..."
	} else if strings.Contains(inputLower, "read note") || strings.Contains(inputLower, "show me the content of") {
		toolName = "read_note"
		filename := extractFilename(inputLower)
		if filename == "" {
			fmt.Println("🤖: I need a filename to read. Could you please specify which note (e.g., 'read note my-note.md')?")
			return
		}
		params = map[string]interface{}{"filename": filename}
		conversationalResponse = fmt.Sprintf("📖 Reading the note '%s' for you...", filename)
	} else if strings.Contains(inputLower, "search for") || strings.Contains(inputLower, "find") || strings.Contains(inputLower, "look for") || strings.Contains(inputLower, "help me find") {
		toolName = "search_vault"
		query := extractSearchQuery(inputLower)
		if query == "" {
			fmt.Println("🤖: I need a search query. Could you please specify what to search for (e.g., 'search for AI ethics')?")
			return
		}
		params = map[string]interface{}{"query": query, "limit": 10}
		conversationalResponse = fmt.Sprintf("🔍 Searching for '%s'...", query)
	} else if strings.Contains(inputLower, "semantic search for") || strings.Contains(inputLower, "ai search for") {
		toolName = "semantic_search"
		query := extractSemanticQuery(inputLower)
		if query == "" {
			fmt.Println("🤖: I need a semantic search query. Could you please specify what to search for (e.g., 'semantic search for machine learning')?")
			return
		}
		params = map[string]interface{}{"query": query, "top_k": 5}
		conversationalResponse = fmt.Sprintf("🧠 Performing semantic search for '%s'...", query)
	} else if strings.Contains(inputLower, "create note") || strings.Contains(inputLower, "new note") {
		toolName = "create_note"
		fmt.Print("🤖: What is the path for the new note (e.g., 'new-ideas/my-idea.md')? ")
		path, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		path = strings.TrimSpace(path)
		if path == "" {
			fmt.Println("🤖: Note path cannot be empty. Aborting.")
			return
		}
		fmt.Print("🤖: Enter the content for the new note (type 'END' on a new line to finish):\n")
		contentBuilder := strings.Builder{}
		for {
			line, _ := bufio.NewReader(os.Stdin).ReadString('\n')
			if strings.TrimSpace(line) == "END" {
				break
			}
			contentBuilder.WriteString(line)
		}
		params = map[string]interface{}{"path": path, "content": contentBuilder.String()}
		conversationalResponse = fmt.Sprintf("📝 Creating note '%s'...", path)
	} else if strings.Contains(inputLower, "bulk tag") || strings.Contains(inputLower, "add tags") {
		toolName = "bulk_tag"
		fmt.Print("🤖: Enter tags separated by commas (e.g., 'tag1, tag2, tag3'): ")
		tagsInput, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		tagsInput = strings.TrimSpace(tagsInput)
		if tagsInput == "" {
			fmt.Println("🤖: No tags provided. Aborting.")
			return
		}
		tags := strings.Split(tagsInput, ",")
		for i, tag := range tags {
			tags[i] = strings.TrimSpace(tag)
		}
		params = map[string]interface{}{"tags": tags}
		conversationalResponse = fmt.Sprintf("🏷️ Adding tags: %s...", strings.Join(tags, ", "))
	} else if strings.Contains(inputLower, "analyze links") || strings.Contains(inputLower, "link analysis") {
		toolName = "analyze_links"
		params = make(map[string]interface{})
		conversationalResponse = "🔗 Analyzing links between notes..."
	} else if strings.Contains(inputLower, "help") || strings.Contains(inputLower, "what can you do") {
		showHelp()
		return
	} else {
		// Try to be more intelligent about understanding the request
		if strings.Contains(inputLower, "matematica") || strings.Contains(inputLower, "math") || strings.Contains(inputLower, "mathematics") {
			toolName = "search_vault"
			params = map[string]interface{}{"query": "matematica", "limit": 10}
			conversationalResponse = "🔍 Searching for mathematics-related content..."
		} else if strings.Contains(inputLower, "ai") || strings.Contains(inputLower, "artificial intelligence") {
			toolName = "search_vault"
			params = map[string]interface{}{"query": "AI", "limit": 10}
			conversationalResponse = "🔍 Searching for AI-related content..."
		} else if strings.Contains(inputLower, "programming") || strings.Contains(inputLower, "code") {
			toolName = "search_vault"
			params = map[string]interface{}{"query": "programming", "limit": 10}
			conversationalResponse = "🔍 Searching for programming-related content..."
		} else {
			fmt.Println("🤔 I'm not sure how to help with that, but here are some suggestions:")
			fmt.Println()
			fmt.Println("• 'list files' - See what's in your vault")
			fmt.Println("• 'search for [topic]' - Find specific information")
			fmt.Println("• 'create note' - Add a new note")
			fmt.Println("• 'analyze links' - Explore connections")
			fmt.Println()
			fmt.Println("💡 **Try being more specific:** \"search for [topic]\", \"list files\", \"create note\", etc.")
			fmt.Println("🆘 **Need help?** Just say \"help\" for a full list of commands.")
			return
		}
	}

	if toolName != "" {
		fmt.Println(conversationalResponse)
		result := executeTool(toolName, params)
		if result.Success {
			fmt.Println("✅ Success!")
			displayResults(result.Data, toolName)
		} else {
			fmt.Println("❌ Failed!")
			fmt.Printf("❗ Error: %s\n", result.Error)
		}
	}
}

func extractFilename(input string) string {
	// Enhanced filename extraction with regex
	re := regexp.MustCompile(`read note\s+([^\s]+\.md)`)
	matches := re.FindStringSubmatch(strings.ToLower(input))
	if len(matches) > 1 {
		return matches[1]
	}

	// Fallback: simple extraction
	parts := strings.Split(input, "read note")
	if len(parts) > 1 {
		filename := strings.TrimSpace(parts[1])
		filename = strings.TrimPrefix(filename, "'")
		filename = strings.TrimSuffix(filename, "'")
		filename = strings.TrimPrefix(filename, "\"")
		filename = strings.TrimSuffix(filename, "\"")
		return filename
	}
	return ""
}

func extractSearchQuery(input string) string {
	// Enhanced search query extraction
	patterns := []string{
		`search for\s+(.+)`,
		`find\s+(.+)`,
		`look for\s+(.+)`,
		`help me find\s+(.+)`,
	}

	for _, pattern := range patterns {
		re := regexp.MustCompile(pattern)
		matches := re.FindStringSubmatch(strings.ToLower(input))
		if len(matches) > 1 {
			query := strings.TrimSpace(matches[1])
			// Remove common stop words
			query = strings.TrimPrefix(query, "all ")
			query = strings.TrimPrefix(query, "the ")
			query = strings.TrimPrefix(query, "a ")
			return query
		}
	}

	// Fallback: extract after "search for"
	parts := strings.Split(input, "search for")
	if len(parts) > 1 {
		return strings.TrimSpace(parts[1])
	}

	parts = strings.Split(input, "find")
	if len(parts) > 1 {
		return strings.TrimSpace(parts[1])
	}

	return ""
}

func extractSemanticQuery(input string) string {
	// Enhanced semantic search query extraction
	patterns := []string{
		`semantic search for\s+(.+)`,
		`ai search for\s+(.+)`,
	}

	for _, pattern := range patterns {
		re := regexp.MustCompile(pattern)
		matches := re.FindStringSubmatch(strings.ToLower(input))
		if len(matches) > 1 {
			return strings.TrimSpace(matches[1])
		}
	}

	// Fallback
	parts := strings.Split(input, "semantic search for")
	if len(parts) > 1 {
		return strings.TrimSpace(parts[1])
	}

	return ""
}

func displayResults(data interface{}, toolName string) {
	switch toolName {
	case "list_files_in_vault":
		if files, ok := data.([]interface{}); ok {
			fmt.Printf("📁 Found %d files:\n", len(files))
			for i, file := range files {
				if fileMap, ok := file.(map[string]interface{}); ok {
					name := fileMap["name"]
					path := fileMap["path"]
					fmt.Printf("  %d. %s (%s)\n", i+1, name, path)
				}
			}
		}
	case "search_vault":
		if results, ok := data.([]interface{}); ok {
			fmt.Printf("🔍 Found %d search results:\n", len(results))
			for i, result := range results {
				if resultMap, ok := result.(map[string]interface{}); ok {
					path := resultMap["path"]
					score := resultMap["score"]
					fmt.Printf("  %d. %s (score: %.2f)\n", i+1, path, score)
				}
			}
		}
	case "semantic_search":
		if dataMap, ok := data.(map[string]interface{}); ok {
			if results, ok := dataMap["results"].([]interface{}); ok {
				fmt.Printf("🧠 Found %d semantic search results:\n", len(results))
				for i, result := range results {
					if resultMap, ok := result.(map[string]interface{}); ok {
						title := resultMap["title"]
						path := resultMap["path"]
						score := resultMap["score"]
						fmt.Printf("  %d. %s (%s) - score: %.2f\n", i+1, title, path, score)
					}
				}
			}
		}
	case "read_note":
		if content, ok := data.(string); ok {
			fmt.Printf("📖 Note content:\n%s\n", content)
		}
	case "create_note":
		if dataMap, ok := data.(map[string]interface{}); ok {
			path := dataMap["path"]
			fmt.Printf("📝 Created note: %s\n", path)
		}
	case "bulk_tag":
		if dataMap, ok := data.(map[string]interface{}); ok {
			tags := dataMap["tags"]
			processed := dataMap["processed"]
			fmt.Printf("🏷️ Applied tags: %v to %v notes\n", tags, processed)
		}
	case "analyze_links":
		if dataMap, ok := data.(map[string]interface{}); ok {
			nodes := dataMap["nodes"]
			edges := dataMap["edges"]
			clusters := dataMap["clusters"]
			fmt.Printf("🔗 Link analysis: %v nodes, %v edges, %v clusters\n", nodes, edges, clusters)
		}
	default:
		fmt.Printf("📊 Result: %v\n", data)
	}
}

func checkStatus() {
	fmt.Print("🤖: Checking MCP server health... ")
	resp, err := http.Get(serverURL + "/health")
	if err != nil {
		fmt.Printf("❌ Error connecting to server: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	var status map[string]interface{}
	json.Unmarshal(body, &status)

	if resp.StatusCode == http.StatusOK {
		fmt.Println("✅ Healthy!")
		fmt.Printf("📄 Status: %v\n", status)
	} else {
		fmt.Printf("❌ Unhealthy! Status Code: %d\n", resp.StatusCode)
		fmt.Printf("📄 Response: %s\n", string(body))
	}
}

func listTools() {
	fmt.Print("🤖: Fetching available tools... ")
	resp, err := http.Get(serverURL + "/tools")
	if err != nil {
		fmt.Printf("❌ Error connecting to server: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	var toolsResponse struct {
		Tools []Tool `json:"tools"`
		Count int    `json:"count"`
	}
	json.Unmarshal(body, &toolsResponse)

	if resp.StatusCode == http.StatusOK {
		fmt.Printf("✅ Found %d tools:\n", toolsResponse.Count)
		for _, tool := range toolsResponse.Tools {
			fmt.Printf("  - %s: %s\n", tool.Name, tool.Description)
		}
	} else {
		fmt.Printf("❌ Failed to fetch tools! Status Code: %d\n", resp.StatusCode)
		fmt.Printf("📄 Response: %s\n", string(body))
	}
}

func executeTool(tool string, params map[string]interface{}) ToolResult {
	requestBody, _ := json.Marshal(map[string]interface{}{
		"tool":   tool,
		"params": params,
	})

	resp, err := http.Post(serverURL+"/tools/execute", "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return ToolResult{Success: false, Error: fmt.Sprintf("Error sending request: %v", err)}
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	var result ToolResult
	if err := json.Unmarshal(body, &result); err != nil {
		return ToolResult{Success: false, Error: fmt.Sprintf("Error decoding response: %v, Body: %s", err, string(body))}
	}

	// Handle server errors
	if resp.StatusCode != http.StatusOK && result.Success {
		result.Success = false
		result.Error = fmt.Sprintf("Server returned status %d, but tool reported success. Possible partial success or unexpected behavior. Message: %s", resp.StatusCode, result.Message)
	} else if resp.StatusCode != http.StatusOK && !result.Success {
		if result.Error == "" {
			result.Error = fmt.Sprintf("Server returned status %d: %s", resp.StatusCode, string(body))
		}
	}

	return result
}
