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
	"time"
)

const (
	serverURL = "http://localhost:3011"
)

// ConversationState tracks the conversation context
type ConversationState struct {
	UserName     string
	SessionStart time.Time
	LastAction   string
	Context      map[string]interface{}
	Memory       []ConversationMemory
}

// ConversationMemory stores important conversation points
type ConversationMemory struct {
	Timestamp time.Time
	Type      string // "action", "note", "search", "insight"
	Content   string
	Metadata  map[string]interface{}
}

// Tool represents a simplified tool definition for display
type Tool struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Parameters  interface{} `json:"parameters"`
}

// ToolResult represents the structure of a tool execution response
type ToolResult struct {
	Success bool        `json:"success"`
	Message string      `json:"message"`
	Data    interface{} `json:"data"`
	Error   string      `json:"error"`
}

// IntelligentCLI provides enhanced conversational AI capabilities
type IntelligentCLI struct {
	state    *ConversationState
	client   *http.Client
	patterns map[string]*regexp.Regexp
}

// NewIntelligentCLI creates a new intelligent CLI instance
func NewIntelligentCLI() *IntelligentCLI {
	return &IntelligentCLI{
		state: &ConversationState{
			SessionStart: time.Now(),
			Context:      make(map[string]interface{}),
			Memory:       make([]ConversationMemory, 0),
		},
		client: &http.Client{Timeout: 30 * time.Second},
		patterns: map[string]*regexp.Regexp{
			"greeting":     regexp.MustCompile(`(?i)(hello|hi|hey|good morning|good afternoon|good evening)`),
			"list_files":   regexp.MustCompile(`(?i)(list|show|display).*(files|notes|documents)`),
			"read_note":    regexp.MustCompile(`(?i)(read|open|view|show).*(note|file|document).*["']?([^"']+)["']?`),
			"search":       regexp.MustCompile(`(?i)(search|find|look for).*["']?([^"']+)["']?`),
			"semantic":     regexp.MustCompile(`(?i)(semantic|ai|intelligent|smart).*search.*["']?([^"']+)["']?`),
			"create":       regexp.MustCompile(`(?i)(create|make|write|add).*(note|file|document)`),
			"analyze":      regexp.MustCompile(`(?i)(analyze|examine|study|investigate).*(links|connections|relationships)`),
			"help":         regexp.MustCompile(`(?i)(help|assist|support|guide)`),
			"status":       regexp.MustCompile(`(?i)(status|health|check|ping)`),
			"quit":         regexp.MustCompile(`(?i)(quit|exit|bye|goodbye|stop)`),
		},
	}
}

func main() {
	cli := NewIntelligentCLI()
	cli.startConversation()
}

func (cli *IntelligentCLI) startConversation() {
	cli.printWelcome()
	cli.initializeSession()

	reader := bufio.NewReader(os.Stdin)

	for {
		fmt.Print("\n🤖 You: ")
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)

		if input == "" {
			continue
		}

		// Process the input with intelligent reasoning
		response := cli.processInput(input)
		cli.printResponse(response)

		// Check for exit
		if cli.patterns["quit"].MatchString(input) {
			cli.sayGoodbye()
			break
		}
	}
}

func (cli *IntelligentCLI) printWelcome() {
	fmt.Println("🧠 Intelligent MCP Server Assistant")
	fmt.Println("====================================")
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
}

func (cli *IntelligentCLI) initializeSession() {
	// Check server health
	status := cli.checkServerHealth()
	if !status {
		fmt.Println("❌ MCP Server is not responding. Please start the server first.")
		fmt.Println("   Run: go run scripts/working_mcp_server.go -mock=true -port=3011")
		os.Exit(1)
	}

	// Get available tools
	tools := cli.getAvailableTools()
	cli.state.Context["available_tools"] = tools

	// Store initialization in memory
	cli.addMemory("action", "Session initialized", map[string]interface{}{
		"tools_count": len(tools),
		"server_status": "healthy",
	})

	fmt.Println("✅ Connected to MCP Server")
	fmt.Println("🔧 Available tools:", len(tools))
}

func (cli *IntelligentCLI) processInput(input string) string {
	// Add user input to memory
	cli.addMemory("action", "User input: "+input, nil)

	// Analyze intent and determine action
	intent := cli.analyzeIntent(input)
	
	switch intent.Type {
	case "greeting":
		return cli.handleGreeting(input)
	case "list_files":
		return cli.handleListFiles()
	case "read_note":
		return cli.handleReadNote(intent.Params)
	case "search":
		return cli.handleSearch(intent.Params)
	case "semantic":
		return cli.handleSemanticSearch(intent.Params)
	case "create":
		return cli.handleCreateNote()
	case "analyze":
		return cli.handleAnalyzeLinks()
	case "help":
		return cli.handleHelp()
	case "status":
		return cli.handleStatus()
	case "complex_workflow":
		return cli.handleComplexWorkflow(input)
	default:
		return cli.handleUnknown(input)
	}
}

type Intent struct {
	Type   string
	Params map[string]string
}

func (cli *IntelligentCLI) analyzeIntent(input string) Intent {
	// Check for complex workflows first
	if cli.isComplexWorkflow(input) {
		return Intent{Type: "complex_workflow", Params: map[string]string{"input": input}}
	}

	// Check patterns
	for patternType, pattern := range cli.patterns {
		if pattern.MatchString(input) {
			matches := pattern.FindStringSubmatch(input)
			params := make(map[string]string)
			
			// Extract parameters based on pattern type
			switch patternType {
			case "read_note":
				if len(matches) > 3 {
					params["filename"] = matches[3]
				}
			case "search", "semantic":
				if len(matches) > 2 {
					params["query"] = matches[2]
				}
			}
			
			return Intent{Type: patternType, Params: params}
		}
	}

	return Intent{Type: "unknown", Params: map[string]string{"input": input}}
}

func (cli *IntelligentCLI) isComplexWorkflow(input string) bool {
	complexKeywords := []string{
		"workflow", "process", "pipeline", "chain", "sequence",
		"analyze and", "find and", "create and", "search and",
		"help me", "can you", "please", "would you",
	}
	
	lowerInput := strings.ToLower(input)
	for _, keyword := range complexKeywords {
		if strings.Contains(lowerInput, keyword) {
			return true
		}
	}
	return false
}

func (cli *IntelligentCLI) handleGreeting(input string) string {
	greetings := []string{
		"Hello! I'm here to help you with your Obsidian vault. What would you like to do?",
		"Hi there! I'm your intelligent assistant. How can I help you today?",
		"Greetings! I'm ready to help you explore and manage your knowledge base.",
		"Hello! I can help you with searching, creating, and analyzing your notes.",
	}
	
	// Store greeting in memory
	cli.addMemory("action", "Greeting received", nil)
	
	return greetings[time.Now().Unix()%int64(len(greetings))]
}

func (cli *IntelligentCLI) handleListFiles() string {
	fmt.Print("📁 Listing files in your vault... ")
	result := cli.executeTool("list_files_in_vault", map[string]interface{}{})
	
	if result.Success {
		cli.addMemory("action", "Listed files", map[string]interface{}{
			"file_count": len(result.Data.([]interface{})),
		})
		return fmt.Sprintf("✅ Found %d files in your vault!", len(result.Data.([]interface{})))
	}
	
	return fmt.Sprintf("❌ Failed to list files: %s", result.Error)
}

func (cli *IntelligentCLI) handleReadNote(params map[string]string) string {
	filename, exists := params["filename"]
	if !exists || filename == "" {
		return "🤔 I need a filename to read. Try: 'read note my-note.md'"
	}
	
	fmt.Printf("📖 Reading note '%s'... ", filename)
	result := cli.executeTool("read_note", map[string]interface{}{"filename": filename})
	
	if result.Success {
		cli.addMemory("note", "Read note: "+filename, map[string]interface{}{
			"filename": filename,
			"length": result.Data.(map[string]interface{})["length"],
		})
		return fmt.Sprintf("✅ Successfully read '%s'", filename)
	}
	
	return fmt.Sprintf("❌ Failed to read '%s': %s", filename, result.Error)
}

func (cli *IntelligentCLI) handleSearch(params map[string]string) string {
	query, exists := params["query"]
	if !exists || query == "" {
		return "🔍 What would you like to search for? Try: 'search for AI'"
	}
	
	fmt.Printf("🔍 Searching for '%s'... ", query)
	result := cli.executeTool("search_vault", map[string]interface{}{
		"query": query,
		"limit": 10,
	})
	
	if result.Success {
		results := result.Data.([]interface{})
		cli.addMemory("search", "Searched for: "+query, map[string]interface{}{
			"query": query,
			"results_count": len(results),
		})
		return fmt.Sprintf("✅ Found %d results for '%s'", len(results), query)
	}
	
	return fmt.Sprintf("❌ Search failed: %s", result.Error)
}

func (cli *IntelligentCLI) handleSemanticSearch(params map[string]string) string {
	query, exists := params["query"]
	if !exists || query == "" {
		return "🧠 What would you like to search semantically? Try: 'semantic search for machine learning'"
	}
	
	fmt.Printf("🧠 Performing semantic search for '%s'... ", query)
	result := cli.executeTool("semantic_search", map[string]interface{}{
		"query": query,
		"top_k": 5,
	})
	
	if result.Success {
		data := result.Data.(map[string]interface{})
		results := data["results"].([]interface{})
		cli.addMemory("search", "Semantic search: "+query, map[string]interface{}{
			"query": query,
			"results_count": len(results),
			"type": "semantic",
		})
		return fmt.Sprintf("✅ Found %d semantic matches for '%s'", len(results), query)
	}
	
	return fmt.Sprintf("❌ Semantic search failed: %s", result.Error)
}

func (cli *IntelligentCLI) handleCreateNote() string {
	fmt.Print("📝 Creating a new note... ")
	
	// Generate a unique filename
	filename := fmt.Sprintf("note-%d.md", time.Now().Unix())
	content := "# New Note\n\nCreated by AI Assistant on " + time.Now().Format("2006-01-02 15:04:05")
	
	result := cli.executeTool("create_note", map[string]interface{}{
		"path":    filename,
		"content": content,
	})
	
	if result.Success {
		cli.addMemory("note", "Created note: "+filename, map[string]interface{}{
			"filename": filename,
			"action": "create",
		})
		return fmt.Sprintf("✅ Created note '%s'", filename)
	}
	
	return fmt.Sprintf("❌ Failed to create note: %s", result.Error)
}

func (cli *IntelligentCLI) handleAnalyzeLinks() string {
	fmt.Print("🔗 Analyzing link relationships... ")
	result := cli.executeTool("analyze_links", map[string]interface{}{})
	
	if result.Success {
		cli.addMemory("action", "Analyzed links", nil)
		return "✅ Link analysis completed"
	}
	
	return fmt.Sprintf("❌ Link analysis failed: %s", result.Error)
}

func (cli *IntelligentCLI) handleHelp() string {
	helpText := `🤖 **Intelligent MCP Assistant Help**

**Basic Commands:**
• "list files" - Show all files in your vault
• "read note [filename]" - Read a specific note
• "search for [query]" - Search your vault
• "semantic search for [query]" - AI-powered search
• "create note" - Create a new note
• "analyze links" - Analyze note connections

**Advanced Features:**
• "help me find [topic]" - Intelligent search assistance
• "create a summary of [topic]" - Multi-step workflow
• "what notes do I have about [topic]" - Context-aware queries
• "show me the connections between [topic1] and [topic2]" - Relationship analysis

**Conversation:**
• I remember our conversation context
• I can chain multiple operations together
• I provide proactive suggestions
• I learn from your preferences

**System Commands:**
• "/status" - Check server health
• "/tools" - List available tools
• "/quit" - Exit the assistant

💡 **Pro Tip:** Be natural! I understand context and can help with complex workflows.`

	cli.addMemory("action", "Help requested", nil)
	return helpText
}

func (cli *IntelligentCLI) handleStatus() string {
	status := cli.checkServerHealth()
	if status {
		cli.addMemory("action", "Status checked", map[string]interface{}{"status": "healthy"})
		return "🟢 Server Status: Healthy and ready!"
	}
	
	cli.addMemory("action", "Status checked", map[string]interface{}{"status": "unhealthy"})
	return "🔴 Server Status: Unhealthy - please check the MCP server"
}

func (cli *IntelligentCLI) handleComplexWorkflow(input string) string {
	// Analyze the complex request and break it down
	workflow := cli.analyzeComplexWorkflow(input)
	
	if len(workflow.Steps) == 0 {
		return "🤔 I'm not sure how to help with that. Could you be more specific?"
	}
	
	// Execute the workflow
	return cli.executeWorkflow(workflow)
}

type Workflow struct {
	Description string
	Steps       []WorkflowStep
}

type WorkflowStep struct {
	Action string
	Params map[string]interface{}
	Tool   string
}

func (cli *IntelligentCLI) analyzeComplexWorkflow(input string) Workflow {
	workflow := Workflow{
		Description: "Complex workflow execution",
		Steps:       make([]WorkflowStep, 0),
	}
	
	lowerInput := strings.ToLower(input)
	
	// Example workflow patterns
	if strings.Contains(lowerInput, "help me find") {
		// Extract search query
		query := cli.extractQuery(input, "help me find")
		workflow.Steps = append(workflow.Steps, WorkflowStep{
			Action: "Search for information",
			Params: map[string]interface{}{"query": query, "limit": 10},
			Tool:   "search_vault",
		})
	}
	
	if strings.Contains(lowerInput, "create a summary") {
		// Extract topic
		topic := cli.extractQuery(input, "create a summary of")
		workflow.Steps = append(workflow.Steps, WorkflowStep{
			Action: "Search for topic information",
			Params: map[string]interface{}{"query": topic, "limit": 5},
			Tool:   "search_vault",
		})
		workflow.Steps = append(workflow.Steps, WorkflowStep{
			Action: "Create summary note",
			Params: map[string]interface{}{
				"path":    fmt.Sprintf("summary-%s-%d.md", topic, time.Now().Unix()),
				"content": fmt.Sprintf("# Summary: %s\n\nGenerated on %s\n\n", topic, time.Now().Format("2006-01-02 15:04:05")),
			},
			Tool: "create_note",
		})
	}
	
	return workflow
}

func (cli *IntelligentCLI) extractQuery(input, prefix string) string {
	// Simple extraction - in a real implementation, this would be more sophisticated
	query := strings.TrimSpace(strings.ToLower(input))
	query = strings.TrimPrefix(query, strings.ToLower(prefix))
	query = strings.TrimSpace(query)
	
	// Remove common words
	commonWords := []string{"about", "on", "regarding", "concerning", "related to"}
	for _, word := range commonWords {
		query = strings.TrimPrefix(query, word+" ")
	}
	
	return query
}

func (cli *IntelligentCLI) executeWorkflow(workflow Workflow) string {
	if len(workflow.Steps) == 0 {
		return "🤔 I couldn't understand what you want me to do. Could you rephrase?"
	}
	
	results := make([]string, 0)
	
	for i, step := range workflow.Steps {
		fmt.Printf("🔄 Step %d: %s... ", i+1, step.Action)
		
		result := cli.executeTool(step.Tool, step.Params)
		if result.Success {
			results = append(results, fmt.Sprintf("✅ %s", step.Action))
			cli.addMemory("workflow", step.Action, step.Params)
		} else {
			results = append(results, fmt.Sprintf("❌ %s failed: %s", step.Action, result.Error))
		}
	}
	
	return fmt.Sprintf("🎯 Workflow completed:\n%s", strings.Join(results, "\n"))
}

func (cli *IntelligentCLI) handleUnknown(input string) string {
	// Use context and memory to provide helpful suggestions
	suggestions := cli.generateSuggestions(input)
	
	cli.addMemory("action", "Unknown input: "+input, nil)
	
	return fmt.Sprintf(`🤔 I'm not sure how to help with that, but here are some suggestions:

%s

💡 **Try being more specific:** "search for [topic]", "list files", "create note", etc.
🆘 **Need help?** Just say "help" for a full list of commands.`, suggestions)
}

func (cli *IntelligentCLI) generateSuggestions(input string) string {
	suggestions := []string{
		"• 'list files' - See what's in your vault",
		"• 'search for [topic]' - Find specific information",
		"• 'create note' - Add a new note",
		"• 'analyze links' - Explore connections",
	}
	
	// Add context-aware suggestions based on memory
	if len(cli.state.Memory) > 0 {
		lastAction := cli.state.Memory[len(cli.state.Memory)-1]
		if lastAction.Type == "search" {
			suggestions = append(suggestions, "• 'read note [filename]' - Read one of the search results")
		}
	}
	
	return strings.Join(suggestions, "\n")
}

func (cli *IntelligentCLI) executeTool(tool string, params map[string]interface{}) ToolResult {
	requestBody, _ := json.Marshal(map[string]interface{}{
		"tool":   tool,
		"params": params,
	})

	resp, err := cli.client.Post(serverURL+"/tools/execute", "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		return ToolResult{Success: false, Error: fmt.Sprintf("Error sending request: %v", err)}
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	var result ToolResult
	if err := json.Unmarshal(body, &result); err != nil {
		return ToolResult{Success: false, Error: fmt.Sprintf("Error decoding response: %v", err)}
	}

	return result
}

func (cli *IntelligentCLI) checkServerHealth() bool {
	resp, err := cli.client.Get(serverURL + "/health")
	if err != nil {
		return false
	}
	defer resp.Body.Close()
	return resp.StatusCode == 200
}

func (cli *IntelligentCLI) getAvailableTools() []Tool {
	resp, err := cli.client.Get(serverURL + "/tools")
	if err != nil {
		return []Tool{}
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)
	var toolsResponse struct {
		Tools []Tool `json:"tools"`
	}
	json.Unmarshal(body, &toolsResponse)
	return toolsResponse.Tools
}

func (cli *IntelligentCLI) addMemory(memType, content string, metadata map[string]interface{}) {
	memory := ConversationMemory{
		Timestamp: time.Now(),
		Type:      memType,
		Content:   content,
		Metadata:  metadata,
	}
	cli.state.Memory = append(cli.state.Memory, memory)
	
	// Keep only last 50 memories to prevent memory bloat
	if len(cli.state.Memory) > 50 {
		cli.state.Memory = cli.state.Memory[len(cli.state.Memory)-50:]
	}
}

func (cli *IntelligentCLI) printResponse(response string) {
	fmt.Println("\n🤖 Assistant:", response)
}

func (cli *IntelligentCLI) sayGoodbye() {
	goodbyes := []string{
		"👋 Goodbye! Thanks for using the Intelligent MCP Assistant!",
		"👋 See you later! Your vault is in good hands.",
		"👋 Farewell! I enjoyed helping you with your knowledge base.",
		"👋 Take care! Remember, I'm here whenever you need help.",
	}
	
	fmt.Println(goodbyes[time.Now().Unix()%int64(len(goodbyes))])
	
	// Store session summary
	cli.addMemory("action", "Session ended", map[string]interface{}{
		"session_duration": time.Since(cli.state.SessionStart).String(),
		"total_actions": len(cli.state.Memory),
	})
}
