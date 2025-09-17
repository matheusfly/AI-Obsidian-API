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

type MCPTool struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
}

type MCPResponse struct {
	Tools []MCPTool `json:"tools"`
	Count int       `json:"count"`
}

type ToolExecutionRequest struct {
	ToolName   string                 `json:"tool_name"`
	Parameters map[string]interface{} `json:"parameters"`
}

type ToolExecutionResponse struct {
	Success bool        `json:"success"`
	Data    interface{} `json:"data"`
	Error   string      `json:"error"`
	Message string      `json:"message"`
}

type InteractiveCLI struct {
	serverURL string
	client    *http.Client
	tools     []MCPTool
}

func NewInteractiveCLI(serverURL string) *InteractiveCLI {
	return &InteractiveCLI{
		serverURL: serverURL,
		client:    &http.Client{Timeout: 30 * time.Second},
		tools:     []MCPTool{},
	}
}

func (cli *InteractiveCLI) loadTools() error {
	resp, err := cli.client.Get(cli.serverURL + "/tools/list")
	if err != nil {
		return fmt.Errorf("failed to load tools: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response: %v", err)
	}

	// The tools endpoint returns an array directly, not wrapped in an object
	var tools []MCPTool
	if err := json.Unmarshal(body, &tools); err != nil {
		return fmt.Errorf("failed to parse tools: %v", err)
	}

	cli.tools = tools
	return nil
}

func (cli *InteractiveCLI) executeTool(toolName string, params map[string]interface{}) (*ToolExecutionResponse, error) {
	request := ToolExecutionRequest{
		ToolName:   toolName,
		Parameters: params,
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}

	resp, err := cli.client.Post(cli.serverURL+"/tools/execute", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to execute tool: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	var result ToolExecutionResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %v", err)
	}

	return &result, nil
}

func (cli *InteractiveCLI) showWelcome() {
	fmt.Println("🤖 MCP Server Interactive CLI Chat")
	fmt.Println("==================================")
	fmt.Println("Welcome! I'm your AI assistant connected to the MCP server.")
	fmt.Println("I can help you interact with your Obsidian vault using various tools.")
	fmt.Println()
	fmt.Println("Available commands:")
	fmt.Println("  /help     - Show this help message")
	fmt.Println("  /tools    - List available MCP tools")
	fmt.Println("  /status   - Check server status")
	fmt.Println("  /quit     - Exit the chat")
	fmt.Println()
	fmt.Println("You can also ask me to:")
	fmt.Println("  - List files in your vault")
	fmt.Println("  - Search for specific content")
	fmt.Println("  - Read notes")
	fmt.Println("  - Create new notes")
	fmt.Println("  - Analyze links between notes")
	fmt.Println("  - And much more!")
	fmt.Println()
	fmt.Println("Type your message and press Enter to start chatting...")
	fmt.Println()
}

func (cli *InteractiveCLI) showTools() {
	fmt.Println("🔧 Available MCP Tools:")
	fmt.Println("========================")
	for i, tool := range cli.tools {
		fmt.Printf("%d. %s\n", i+1, tool.Name)
		fmt.Printf("   Description: %s\n", tool.Description)
		if params, ok := tool.Parameters["properties"].(map[string]interface{}); ok {
			fmt.Printf("   Parameters: ")
			var paramNames []string
			for paramName := range params {
				paramNames = append(paramNames, paramName)
			}
			fmt.Printf("%s\n", strings.Join(paramNames, ", "))
		}
		fmt.Println()
	}
}

func (cli *InteractiveCLI) checkStatus() {
	resp, err := cli.client.Get(cli.serverURL + "/health")
	if err != nil {
		fmt.Printf("❌ Server status check failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read status: %v\n", err)
		return
	}

	var status map[string]interface{}
	if err := json.Unmarshal(body, &status); err != nil {
		fmt.Printf("❌ Failed to parse status: %v\n", err)
		return
	}

	fmt.Println("🟢 Server Status:")
	fmt.Printf("   Status: %v\n", status["status"])
	fmt.Printf("   Mode: %v\n", status["mode"])
	fmt.Printf("   Timestamp: %v\n", status["timestamp"])
}

func (cli *InteractiveCLI) processNaturalLanguage(input string) {
	input = strings.ToLower(strings.TrimSpace(input))

	// Natural language processing for common requests
	if strings.Contains(input, "list") && strings.Contains(input, "file") {
		fmt.Println("📁 Listing files in your vault...")
		result, err := cli.executeTool("list_files_in_vault", map[string]interface{}{})
		cli.handleToolResult(result, err)
		return
	}

	if strings.Contains(input, "search") || strings.Contains(input, "find") {
		// Extract search query
		query := input
		if strings.Contains(input, "for") {
			parts := strings.Split(input, "for")
			if len(parts) > 1 {
				query = strings.TrimSpace(parts[1])
			}
		}

		fmt.Printf("🔍 Searching for: %s\n", query)
		result, err := cli.executeTool("search_vault", map[string]interface{}{
			"query": query,
			"limit": 10,
		})
		cli.handleToolResult(result, err)
		return
	}

	if strings.Contains(input, "read") && strings.Contains(input, "note") {
		// Extract filename
		filename := "test.md" // Default
		if strings.Contains(input, "note") {
			parts := strings.Split(input, "note")
			if len(parts) > 1 {
				filename = strings.TrimSpace(parts[1])
				if !strings.HasSuffix(filename, ".md") {
					filename += ".md"
				}
			}
		}

		fmt.Printf("📖 Reading note: %s\n", filename)
		result, err := cli.executeTool("read_note", map[string]interface{}{
			"filename": filename,
		})
		cli.handleToolResult(result, err)
		return
	}

	if strings.Contains(input, "create") && strings.Contains(input, "note") {
		fmt.Println("📝 Creating a new note...")
		result, err := cli.executeTool("create_note", map[string]interface{}{
			"path":    "interactive-note.md",
			"content": "# Interactive Note\n\nCreated via MCP CLI chat\n\n" + input,
		})
		cli.handleToolResult(result, err)
		return
	}

	if strings.Contains(input, "analyze") && strings.Contains(input, "link") {
		fmt.Println("🔗 Analyzing links in your vault...")
		result, err := cli.executeTool("analyze_links", map[string]interface{}{})
		cli.handleToolResult(result, err)
		return
	}

	if strings.Contains(input, "semantic") && strings.Contains(input, "search") {
		query := input
		if strings.Contains(input, "for") {
			parts := strings.Split(input, "for")
			if len(parts) > 1 {
				query = strings.TrimSpace(parts[1])
			}
		}

		fmt.Printf("🧠 Semantic search for: %s\n", query)
		result, err := cli.executeTool("semantic_search", map[string]interface{}{
			"query": query,
			"top_k": 5,
		})
		cli.handleToolResult(result, err)
		return
	}

	// Default response for unrecognized input
	fmt.Println("🤔 I'm not sure what you'd like me to do. Try one of these:")
	fmt.Println("  - 'list files' - List all files in your vault")
	fmt.Println("  - 'search for [query]' - Search your vault")
	fmt.Println("  - 'read note [filename]' - Read a specific note")
	fmt.Println("  - 'create note' - Create a new note")
	fmt.Println("  - 'analyze links' - Analyze note connections")
	fmt.Println("  - 'semantic search for [query]' - AI-powered search")
	fmt.Println("  - '/help' - Show help")
}

func (cli *InteractiveCLI) handleToolResult(result *ToolExecutionResponse, err error) {
	if err != nil {
		fmt.Printf("❌ Error: %v\n", err)
		return
	}

	if !result.Success {
		fmt.Printf("❌ Tool execution failed: %s\n", result.Error)
		return
	}

	fmt.Println("✅ Success!")
	if result.Data != nil {
		// Pretty print the result
		jsonData, err := json.MarshalIndent(result.Data, "", "  ")
		if err != nil {
			fmt.Printf("📊 Result: %v\n", result.Data)
		} else {
			fmt.Printf("📊 Result:\n%s\n", string(jsonData))
		}
	}
	if result.Message != "" {
		fmt.Printf("💬 Message: %s\n", result.Message)
	}
}

func (cli *InteractiveCLI) run() {
	// Load tools
	if err := cli.loadTools(); err != nil {
		fmt.Printf("❌ Failed to load tools: %v\n", err)
		return
	}

	cli.showWelcome()

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("🤖 You: ")
		if !scanner.Scan() {
			break
		}

		input := strings.TrimSpace(scanner.Text())
		if input == "" {
			continue
		}

		// Handle commands
		switch input {
		case "/help":
			cli.showWelcome()
		case "/tools":
			cli.showTools()
		case "/status":
			cli.checkStatus()
		case "/quit", "/exit":
			fmt.Println("👋 Goodbye! Thanks for using the MCP Interactive CLI!")
			return
		default:
			cli.processNaturalLanguage(input)
		}

		fmt.Println()
	}
}

func main() {
	serverURL := "http://localhost:3010" // Fixed port to match server config
	if len(os.Args) > 1 {
		serverURL = os.Args[1]
	}

	cli := NewInteractiveCLI(serverURL)
	cli.run()
}
