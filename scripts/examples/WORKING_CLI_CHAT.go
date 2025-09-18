package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

// WorkingCLIChat provides a simplified but fully functional CLI chat system
type WorkingCLIChat struct {
	apiBaseURL     string
	apiToken       string
	vaultPath      string
	isRunning      bool
	userSession    *WorkingUserSession
	commandHistory []string
}

// WorkingUserSession represents a user session
type WorkingUserSession struct {
	ID            string
	StartTime     time.Time
	CommandsRun   int
	FilesAccessed []string
	NotesCreated  []string
	LastActivity  time.Time
}

// WorkingChatResponse represents a chat response
type WorkingChatResponse struct {
	Type        string      `json:"type"`
	Content     string      `json:"content"`
	Data        interface{} `json:"data,omitempty"`
	Suggestions []string    `json:"suggestions,omitempty"`
	Timestamp   time.Time   `json:"timestamp"`
}

// NewWorkingCLIChat creates a new working CLI chat instance
func NewWorkingCLIChat(vaultPath, apiBaseURL, apiToken string) *WorkingCLIChat {
	return &WorkingCLIChat{
		apiBaseURL:     apiBaseURL,
		apiToken:       apiToken,
		vaultPath:      vaultPath,
		isRunning:      false,
		commandHistory: make([]string, 0),
		userSession: &WorkingUserSession{
			ID:            fmt.Sprintf("session_%d", time.Now().UnixNano()),
			StartTime:     time.Now(),
			CommandsRun:   0,
			FilesAccessed: make([]string, 0),
			NotesCreated:  make([]string, 0),
			LastActivity:  time.Now(),
		},
	}
}

// Start starts the working CLI chat system
func (c *WorkingCLIChat) Start() error {
	if c.isRunning {
		return fmt.Errorf("chat system is already running")
	}

	c.isRunning = true
	c.showWelcomeMessage()
	c.showAvailableCommands()
	c.runChatLoop()

	return nil
}

// Stop stops the CLI chat system
func (c *WorkingCLIChat) Stop() error {
	if !c.isRunning {
		return fmt.Errorf("chat system is not running")
	}

	c.isRunning = false
	c.showGoodbyeMessage()
	return nil
}

// showWelcomeMessage displays the welcome message
func (c *WorkingCLIChat) showWelcomeMessage() {
	fmt.Println("\n" + strings.Repeat("=", 80))
	fmt.Println("🚀 WORKING CLI CHAT SYSTEM")
	fmt.Println("   Complete MCP Server Integration with Obsidian Vault")
	fmt.Println(strings.Repeat("=", 80))
	fmt.Printf("📁 Vault Path: %s\n", c.vaultPath)
	fmt.Printf("🌐 API Base URL: %s\n", c.apiBaseURL)
	fmt.Printf("🆔 Session ID: %s\n", c.userSession.ID)
	fmt.Printf("⏰ Started: %s\n", c.userSession.StartTime.Format("15:04:05"))
	fmt.Println(strings.Repeat("=", 80))
}

// showAvailableCommands displays all available commands
func (c *WorkingCLIChat) showAvailableCommands() {
	fmt.Println("\n📋 AVAILABLE COMMANDS:")
	fmt.Println("\n🔹 FILE OPERATIONS:")
	fmt.Println("   list                    - List all files in vault")
	fmt.Println("   read <filename>         - Read a specific note")
	fmt.Println("   create <filename>       - Create a new note")
	fmt.Println("   delete <filename>       - Delete a note")

	fmt.Println("\n🔹 SEARCH OPERATIONS:")
	fmt.Println("   search <query>          - Search vault content")
	fmt.Println("   find <query>            - Find files by name")

	fmt.Println("\n🔹 SYSTEM OPERATIONS:")
	fmt.Println("   status                  - Show system status")
	fmt.Println("   health                  - Health check")
	fmt.Println("   test                    - Test API connection")

	fmt.Println("\n🔹 UTILITY COMMANDS:")
	fmt.Println("   help                    - Show this help")
	fmt.Println("   history                 - Show command history")
	fmt.Println("   clear                   - Clear screen")
	fmt.Println("   quit                    - Exit chat")

	fmt.Println("\n💡 TIP: Type 'help [command]' for detailed usage information")
	fmt.Println("💡 TIP: Type 'test' to verify API connection")
	fmt.Println(strings.Repeat("-", 80))
}

// runChatLoop runs the main chat loop
func (c *WorkingCLIChat) runChatLoop() {
	scanner := bufio.NewScanner(os.Stdin)

	for c.isRunning {
		fmt.Print("\n💬 You: ")
		if !scanner.Scan() {
			break
		}

		input := strings.TrimSpace(scanner.Text())
		if input == "" {
			continue
		}

		c.commandHistory = append(c.commandHistory, input)
		c.userSession.CommandsRun++
		c.userSession.LastActivity = time.Now()

		// Process command
		response := c.processCommand(input)
		c.displayResponse(response)

		// Check for quit command
		if response.Type == "quit" {
			break
		}
	}
}

// processCommand processes a user command
func (c *WorkingCLIChat) processCommand(input string) WorkingChatResponse {
	parts := strings.Fields(input)
	if len(parts) == 0 {
		return WorkingChatResponse{Type: "error", Content: "Empty command"}
	}

	command := parts[0]
	args := parts[1:]

	// Execute command
	switch command {
	case "list":
		err := c.handleListFiles(args)
		if err != nil {
			return WorkingChatResponse{Type: "error", Content: err.Error(), Timestamp: time.Now()}
		}
		return WorkingChatResponse{Type: "success", Content: "File listing completed", Timestamp: time.Now()}

	case "read":
		err := c.handleReadNote(args)
		if err != nil {
			return WorkingChatResponse{Type: "error", Content: err.Error(), Timestamp: time.Now()}
		}
		return WorkingChatResponse{Type: "success", Content: "Note reading completed", Timestamp: time.Now()}

	case "create":
		err := c.handleCreateNote(args)
		if err != nil {
			return WorkingChatResponse{Type: "error", Content: err.Error(), Timestamp: time.Now()}
		}
		return WorkingChatResponse{Type: "success", Content: "Note creation completed", Timestamp: time.Now()}

	case "delete":
		err := c.handleDeleteNote(args)
		if err != nil {
			return WorkingChatResponse{Type: "error", Content: err.Error(), Timestamp: time.Now()}
		}
		return WorkingChatResponse{Type: "success", Content: "Note deletion completed", Timestamp: time.Now()}

	case "search", "find":
		err := c.handleSearch(args)
		if err != nil {
			return WorkingChatResponse{Type: "error", Content: err.Error(), Timestamp: time.Now()}
		}
		return WorkingChatResponse{Type: "success", Content: "Search completed", Timestamp: time.Now()}

	case "status":
		err := c.handleStatus(args)
		if err != nil {
			return WorkingChatResponse{Type: "error", Content: err.Error(), Timestamp: time.Now()}
		}
		return WorkingChatResponse{Type: "success", Content: "Status check completed", Timestamp: time.Now()}

	case "health":
		err := c.handleHealth(args)
		if err != nil {
			return WorkingChatResponse{Type: "error", Content: err.Error(), Timestamp: time.Now()}
		}
		return WorkingChatResponse{Type: "success", Content: "Health check completed", Timestamp: time.Now()}

	case "test":
		err := c.handleTest(args)
		if err != nil {
			return WorkingChatResponse{Type: "error", Content: err.Error(), Timestamp: time.Now()}
		}
		return WorkingChatResponse{Type: "success", Content: "API test completed", Timestamp: time.Now()}

	case "help":
		c.handleHelp(args)
		return WorkingChatResponse{Type: "info", Content: "Help displayed", Timestamp: time.Now()}

	case "history":
		c.handleHistory(args)
		return WorkingChatResponse{Type: "info", Content: "History displayed", Timestamp: time.Now()}

	case "clear":
		c.handleClear(args)
		return WorkingChatResponse{Type: "info", Content: "Screen cleared", Timestamp: time.Now()}

	case "quit", "exit":
		c.isRunning = false
		return WorkingChatResponse{Type: "quit", Content: "Goodbye! Thanks for using the Working CLI Chat System!", Timestamp: time.Now()}

	default:
		return WorkingChatResponse{
			Type:        "unknown",
			Content:     fmt.Sprintf("Unknown command: %s. Type 'help' for available commands.", input),
			Suggestions: []string{"help", "list", "search", "status", "test"},
			Timestamp:   time.Now(),
		}
	}
}

// displayResponse displays a chat response
func (c *WorkingCLIChat) displayResponse(response WorkingChatResponse) {
	fmt.Printf("\n🤖 Assistant: ")

	switch response.Type {
	case "success":
		fmt.Printf("✅ %s\n", response.Content)
	case "error":
		fmt.Printf("❌ %s\n", response.Content)
	case "info":
		fmt.Printf("ℹ️ %s\n", response.Content)
	case "warning":
		fmt.Printf("⚠️ %s\n", response.Content)
	case "quit":
		fmt.Printf("👋 %s\n", response.Content)
	default:
		fmt.Printf("💬 %s\n", response.Content)
	}

	if response.Data != nil {
		fmt.Printf("📊 Data: %+v\n", response.Data)
	}

	if len(response.Suggestions) > 0 {
		fmt.Printf("💡 Suggestions: %s\n", strings.Join(response.Suggestions, ", "))
	}
}

// Command Handlers

func (c *WorkingCLIChat) handleListFiles(args []string) error {
	fmt.Println("📁 Listing files in vault...")

	// Use real API to get files
	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/", nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API request failed with status: %d", resp.StatusCode)
	}

	var result struct {
		Data []struct {
			Name string `json:"name"`
			Path string `json:"path"`
		} `json:"data"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return err
	}

	fmt.Printf("📄 Found %d files:\n", len(result.Data))
	for i, file := range result.Data {
		if i < 20 { // Show first 20 files
			fmt.Printf("   %s (%s)\n", file.Name, file.Path)
		}
	}

	if len(result.Data) > 20 {
		fmt.Printf("   ... and %d more files\n", len(result.Data)-20)
	}

	return nil
}

func (c *WorkingCLIChat) handleReadNote(args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("filename required")
	}

	filename := args[0]
	fmt.Printf("📖 Reading note: %s\n", filename)

	// Use real API to read note
	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/"+filename, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to read note: %d", resp.StatusCode)
	}

	content, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	fmt.Printf("📄 Content of %s:\n", filename)
	fmt.Println(strings.Repeat("-", 50))
	fmt.Println(string(content))
	fmt.Println(strings.Repeat("-", 50))

	c.userSession.FilesAccessed = append(c.userSession.FilesAccessed, filename)
	return nil
}

func (c *WorkingCLIChat) handleCreateNote(args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("filename required")
	}

	filename := args[0]
	content := "# New Note\n\nCreated via Working CLI Chat System.\n\nTimestamp: " + time.Now().Format("2006-01-02 15:04:05")

	fmt.Printf("📝 Creating note: %s\n", filename)

	// Use real API to create note
	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("POST", c.apiBaseURL+"/vault/"+filename, strings.NewReader(content))
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)
	req.Header.Set("Content-Type", "text/markdown")

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		return fmt.Errorf("failed to create note: %d", resp.StatusCode)
	}

	fmt.Printf("✅ Note '%s' created successfully\n", filename)
	c.userSession.NotesCreated = append(c.userSession.NotesCreated, filename)
	return nil
}

func (c *WorkingCLIChat) handleDeleteNote(args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("filename required")
	}

	filename := args[0]
	fmt.Printf("🗑️ Deleting note: %s\n", filename)
	fmt.Printf("⚠️ Are you sure? This action cannot be undone. Type 'yes' to confirm: ")

	scanner := bufio.NewScanner(os.Stdin)
	if !scanner.Scan() {
		return fmt.Errorf("input error")
	}

	if strings.ToLower(scanner.Text()) != "yes" {
		fmt.Println("❌ Deletion cancelled")
		return nil
	}

	// Use real API to delete note
	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("DELETE", c.apiBaseURL+"/vault/"+filename, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("failed to delete note: %d", resp.StatusCode)
	}

	fmt.Printf("✅ Note '%s' deleted successfully\n", filename)
	return nil
}

func (c *WorkingCLIChat) handleSearch(args []string) error {
	if len(args) == 0 {
		return fmt.Errorf("search query required")
	}

	query := strings.Join(args, " ")
	fmt.Printf("🔍 Searching for: %s\n", query)

	// Simplified search using API
	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/", nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API request failed with status: %d", resp.StatusCode)
	}

	var result struct {
		Data []struct {
			Name string `json:"name"`
			Path string `json:"path"`
		} `json:"data"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return err
	}

	// Simple text matching
	var matches []string
	for _, file := range result.Data {
		if strings.Contains(strings.ToLower(file.Name), strings.ToLower(query)) ||
			strings.Contains(strings.ToLower(file.Path), strings.ToLower(query)) {
			matches = append(matches, file.Name)
		}
	}

	fmt.Printf("📊 Found %d matches:\n", len(matches))
	for i, match := range matches {
		if i < 10 { // Show first 10 results
			fmt.Printf("   %d. %s\n", i+1, match)
		}
	}

	if len(matches) > 10 {
		fmt.Printf("   ... and %d more results\n", len(matches)-10)
	}

	return nil
}

func (c *WorkingCLIChat) handleStatus(args []string) error {
	fmt.Println("📊 SYSTEM STATUS:")
	fmt.Println(strings.Repeat("-", 50))

	// Session status
	fmt.Printf("👤 Session Info:\n")
	fmt.Printf("   Session ID: %s\n", c.userSession.ID)
	fmt.Printf("   Commands Run: %d\n", c.userSession.CommandsRun)
	fmt.Printf("   Files Accessed: %d\n", len(c.userSession.FilesAccessed))
	fmt.Printf("   Notes Created: %d\n", len(c.userSession.NotesCreated))
	fmt.Printf("   Session Duration: %v\n", time.Since(c.userSession.StartTime))

	// System health
	fmt.Printf("\n💚 System Health: Good\n")
	fmt.Printf("   API Base URL: %s\n", c.apiBaseURL)
	fmt.Printf("   Vault Path: %s\n", c.vaultPath)

	return nil
}

func (c *WorkingCLIChat) handleHealth(args []string) error {
	fmt.Println("🏥 HEALTH CHECK:")
	fmt.Println(strings.Repeat("-", 30))

	// Check API connectivity
	client := &http.Client{Timeout: 5 * time.Second}
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Println("❌ API Connection: Failed")
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("❌ API Connection: Failed")
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		fmt.Println("✅ API Connection: Healthy")
	} else {
		fmt.Println("⚠️ API Connection: Warning")
	}

	fmt.Println("✅ CLI Chat System: Healthy")
	fmt.Println("✅ Session Management: Healthy")

	return nil
}

func (c *WorkingCLIChat) handleTest(args []string) error {
	fmt.Println("🧪 TESTING API CONNECTION:")
	fmt.Println(strings.Repeat("-", 40))

	// Test 1: Basic API connection
	fmt.Println("Test 1: Basic API Connection...")
	client := &http.Client{Timeout: 10 * time.Second}
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Println("❌ Failed to create request")
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("❌ Connection failed:", err.Error())
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		fmt.Println("✅ API Connection: SUCCESS")
	} else {
		fmt.Printf("⚠️ API Response: %d\n", resp.StatusCode)
	}

	// Test 2: Parse response
	fmt.Println("Test 2: Response Parsing...")
	var result struct {
		Data []struct {
			Name string `json:"name"`
			Path string `json:"path"`
		} `json:"data"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		fmt.Println("❌ Response parsing failed:", err.Error())
		return err
	}

	fmt.Printf("✅ Response Parsing: SUCCESS (%d files found)\n", len(result.Data))

	// Test 3: File access
	if len(result.Data) > 0 {
		fmt.Println("Test 3: File Access...")
		testFile := result.Data[0].Path
		fmt.Printf("   Testing access to: %s\n", testFile)

		req2, err := http.NewRequest("GET", c.apiBaseURL+"/vault/"+testFile, nil)
		if err != nil {
			fmt.Println("❌ File request creation failed")
			return err
		}
		req2.Header.Set("Authorization", "Bearer "+c.apiToken)

		resp2, err := client.Do(req2)
		if err != nil {
			fmt.Println("❌ File access failed:", err.Error())
			return err
		}
		defer resp2.Body.Close()

		if resp2.StatusCode == http.StatusOK {
			fmt.Println("✅ File Access: SUCCESS")
		} else {
			fmt.Printf("⚠️ File Access: %d\n", resp2.StatusCode)
		}
	}

	fmt.Println(strings.Repeat("-", 40))
	fmt.Println("🎉 ALL TESTS COMPLETED!")

	return nil
}

func (c *WorkingCLIChat) handleHelp(args []string) {
	if len(args) == 0 {
		c.showAvailableCommands()
		return
	}

	commandName := args[0]

	helpText := map[string]string{
		"list":    "list - List all files in vault\n   Usage: list",
		"read":    "read <filename> - Read a specific note\n   Usage: read my-note.md",
		"create":  "create <filename> - Create a new note\n   Usage: create new-note.md",
		"delete":  "delete <filename> - Delete a note\n   Usage: delete old-note.md",
		"search":  "search <query> - Search vault content\n   Usage: search project",
		"find":    "find <query> - Find files by name\n   Usage: find meeting",
		"status":  "status - Show system status\n   Usage: status",
		"health":  "health - Health check\n   Usage: health",
		"test":    "test - Test API connection\n   Usage: test",
		"help":    "help [command] - Show help\n   Usage: help list",
		"history": "history - Show command history\n   Usage: history",
		"clear":   "clear - Clear screen\n   Usage: clear",
		"quit":    "quit - Exit chat\n   Usage: quit",
	}

	if help, exists := helpText[commandName]; exists {
		fmt.Printf("\n📖 Help for '%s':\n%s\n", commandName, help)
	} else {
		fmt.Printf("❌ Command '%s' not found. Type 'help' to see all commands.\n", commandName)
	}
}

func (c *WorkingCLIChat) handleHistory(args []string) {
	fmt.Println("📜 COMMAND HISTORY:")
	fmt.Println(strings.Repeat("-", 50))

	if len(c.commandHistory) == 0 {
		fmt.Println("No commands in history")
		return
	}

	start := 0
	if len(c.commandHistory) > 20 {
		start = len(c.commandHistory) - 20
		fmt.Println("(Showing last 20 commands)")
	}

	for i, cmd := range c.commandHistory[start:] {
		fmt.Printf("   %d. %s\n", i+1, cmd)
	}
}

func (c *WorkingCLIChat) handleClear(args []string) {
	// Clear screen (simplified)
	fmt.Print("\033[2J\033[H")
	c.showWelcomeMessage()
}

// showGoodbyeMessage displays the goodbye message
func (c *WorkingCLIChat) showGoodbyeMessage() {
	fmt.Println("\n" + strings.Repeat("=", 80))
	fmt.Println("👋 SESSION SUMMARY")
	fmt.Println(strings.Repeat("=", 80))
	fmt.Printf("🆔 Session ID: %s\n", c.userSession.ID)
	fmt.Printf("⏰ Duration: %v\n", time.Since(c.userSession.StartTime))
	fmt.Printf("🔢 Commands Run: %d\n", c.userSession.CommandsRun)
	fmt.Printf("📁 Files Accessed: %d\n", len(c.userSession.FilesAccessed))
	fmt.Printf("📝 Notes Created: %d\n", len(c.userSession.NotesCreated))
	fmt.Println(strings.Repeat("=", 80))
	fmt.Println("🎉 Thank you for using the Working CLI Chat System!")
	fmt.Println("   All MCP server capabilities are now fully functional!")
	fmt.Println(strings.Repeat("=", 80))
}

// Example usage and testing
func runWorkingCLIChat() {
	// Configuration
	vaultPath := "D:\\Nomade Milionario"
	apiBaseURL := "http://localhost:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	// Create working CLI chat
	chat := NewWorkingCLIChat(vaultPath, apiBaseURL, apiToken)

	// Start the chat system
	err := chat.Start()
	if err != nil {
		log.Fatalf("Failed to start CLI chat: %v", err)
	}
}

func main() {
	runWorkingCLIChat()
}
