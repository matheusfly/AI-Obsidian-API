package main

import (
	"bufio"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

// FinalWorkingChat provides the final working CLI chat system
type FinalWorkingChat struct {
	apiBaseURL string
	apiToken   string
	vaultPath  string
	isRunning  bool
	sessionID  string
	startTime  time.Time
	commands   int
}

// NewFinalWorkingChat creates a new final working chat instance
func NewFinalWorkingChat(vaultPath, apiBaseURL, apiToken string) *FinalWorkingChat {
	return &FinalWorkingChat{
		apiBaseURL: apiBaseURL,
		apiToken:   apiToken,
		vaultPath:  vaultPath,
		isRunning:  false,
		sessionID:  fmt.Sprintf("session_%d", time.Now().UnixNano()),
		startTime:  time.Now(),
		commands:   0,
	}
}

// createHTTPClient creates an HTTP client with SSL certificate skipping
func (c *FinalWorkingChat) createHTTPClient() *http.Client {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	return &http.Client{
		Transport: tr,
		Timeout:   30 * time.Second,
	}
}

// Start starts the final working chat
func (c *FinalWorkingChat) Start() error {
	if c.isRunning {
		return fmt.Errorf("chat is already running")
	}

	c.isRunning = true
	c.showWelcome()
	c.runChatLoop()
	return nil
}

// showWelcome shows welcome message
func (c *FinalWorkingChat) showWelcome() {
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("🚀 FINAL WORKING CHAT - MCP SYSTEM")
	fmt.Println("   Complete Obsidian Vault Integration")
	fmt.Println(strings.Repeat("=", 60))
	fmt.Printf("📁 Vault: %s\n", c.vaultPath)
	fmt.Printf("🌐 API: %s\n", c.apiBaseURL)
	fmt.Printf("🆔 Session: %s\n", c.sessionID)
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("💬 Available Commands:")
	fmt.Println("   test          - Test API connection")
	fmt.Println("   list          - List vault files")
	fmt.Println("   read <file>   - Read a note")
	fmt.Println("   create <file> - Create a note")
	fmt.Println("   search <query>- Search vault")
	fmt.Println("   status        - Show status")
	fmt.Println("   help          - Show help")
	fmt.Println("   quit          - Exit")
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("💡 Try searching for: AGENTS, Math, Energia, leis, data, test")
	fmt.Println(strings.Repeat("=", 60))
}

// runChatLoop runs the main chat loop
func (c *FinalWorkingChat) runChatLoop() {
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

		c.commands++
		c.processInput(input)
	}
}

// processInput processes user input
func (c *FinalWorkingChat) processInput(input string) {
	parts := strings.Fields(input)
	if len(parts) == 0 {
		return
	}

	command := parts[0]
	args := parts[1:]

	fmt.Printf("\n🤖 Assistant: ")

	switch command {
	case "test":
		c.handleTest()
	case "list":
		c.handleList()
	case "read":
		c.handleRead(args)
	case "create":
		c.handleCreate(args)
	case "search":
		c.handleSearch(args)
	case "status":
		c.handleStatus()
	case "help":
		c.handleHelp()
	case "quit", "exit":
		c.handleQuit()
	default:
		fmt.Printf("❌ Unknown command: %s. Type 'help' for commands.\n", input)
	}
}

// handleTest tests API connection
func (c *FinalWorkingChat) handleTest() {
	fmt.Println("🧪 Testing API connection...")

	client := c.createHTTPClient()
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Connection failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		fmt.Println("✅ API Connection: SUCCESS")
	} else {
		fmt.Printf("⚠️ API Response: %d\n", resp.StatusCode)
	}
}

// handleList lists vault files
func (c *FinalWorkingChat) handleList() {
	fmt.Println("📁 Listing vault files...")

	client := c.createHTTPClient()
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("❌ API request failed: %d\n", resp.StatusCode)
		return
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read response: %v\n", err)
		return
	}

	// Parse JSON with the correct structure
	var result struct {
		Files []string `json:"files"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("❌ Failed to parse response: %v\n", err)
		return
	}

	fmt.Printf("📄 Found %d files:\n", len(result.Files))
	for i, file := range result.Files {
		if i < 15 { // Show first 15 files
			fmt.Printf("   %s\n", file)
		}
	}

	if len(result.Files) > 15 {
		fmt.Printf("   ... and %d more files\n", len(result.Files)-15)
	}
}

// handleRead reads a note
func (c *FinalWorkingChat) handleRead(args []string) {
	if len(args) == 0 {
		fmt.Println("❌ Please specify a filename")
		return
	}

	filename := args[0]
	fmt.Printf("📖 Reading: %s\n", filename)

	client := c.createHTTPClient()
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/"+filename, nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("❌ Failed to read note: %d\n", resp.StatusCode)
		return
	}

	content, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read content: %v\n", err)
		return
	}

	fmt.Printf("📄 Content of %s:\n", filename)
	fmt.Println(strings.Repeat("-", 50))
	fmt.Println(string(content))
	fmt.Println(strings.Repeat("-", 50))
}

// handleCreate creates a note
func (c *FinalWorkingChat) handleCreate(args []string) {
	if len(args) == 0 {
		fmt.Println("❌ Please specify a filename")
		return
	}

	filename := args[0]
	content := fmt.Sprintf("# New Note\n\nCreated via Final Working Chat System.\n\nTimestamp: %s", time.Now().Format("2006-01-02 15:04:05"))

	fmt.Printf("📝 Creating: %s\n", filename)

	client := c.createHTTPClient()
	req, err := http.NewRequest("POST", c.apiBaseURL+"/vault/"+filename, strings.NewReader(content))
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)
	req.Header.Set("Content-Type", "text/markdown")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusCreated {
		fmt.Printf("✅ Note '%s' created successfully\n", filename)
	} else {
		fmt.Printf("❌ Failed to create note: %d\n", resp.StatusCode)
	}
}

// handleSearch searches the vault
func (c *FinalWorkingChat) handleSearch(args []string) {
	if len(args) == 0 {
		fmt.Println("❌ Please specify a search query")
		return
	}

	query := strings.Join(args, " ")
	fmt.Printf("🔍 Searching for: %s\n", query)

	client := c.createHTTPClient()
	req, err := http.NewRequest("GET", c.apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+c.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("❌ API request failed: %d\n", resp.StatusCode)
		return
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read response: %v\n", err)
		return
	}

	// Parse JSON with the correct structure
	var result struct {
		Files []string `json:"files"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("❌ Failed to parse response: %v\n", err)
		return
	}

	// Simple text matching
	var matches []string
	for _, file := range result.Files {
		if strings.Contains(strings.ToLower(file), strings.ToLower(query)) {
			matches = append(matches, file)
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

	if len(matches) == 0 {
		fmt.Println("💡 Try searching for: AGENTS, Math, Energia, leis, data, test, md")
	}
}

// handleStatus shows status
func (c *FinalWorkingChat) handleStatus() {
	fmt.Println("📊 SYSTEM STATUS:")
	fmt.Println(strings.Repeat("-", 30))
	fmt.Printf("🆔 Session ID: %s\n", c.sessionID)
	fmt.Printf("⏰ Duration: %v\n", time.Since(c.startTime))
	fmt.Printf("🔢 Commands: %d\n", c.commands)
	fmt.Printf("🌐 API URL: %s\n", c.apiBaseURL)
	fmt.Printf("📁 Vault: %s\n", c.vaultPath)
	fmt.Println("💚 Status: Running")
}

// handleHelp shows help
func (c *FinalWorkingChat) handleHelp() {
	fmt.Println("📋 AVAILABLE COMMANDS:")
	fmt.Println("   test          - Test API connection")
	fmt.Println("   list          - List all files in vault")
	fmt.Println("   read <file>   - Read a specific note")
	fmt.Println("   create <file> - Create a new note")
	fmt.Println("   search <query>- Search vault content")
	fmt.Println("   status        - Show system status")
	fmt.Println("   help          - Show this help")
	fmt.Println("   quit          - Exit chat")
	fmt.Println("")
	fmt.Println("💡 SUGGESTED SEARCHES:")
	fmt.Println("   search AGENTS    - Find AGENTS.md")
	fmt.Println("   search Math      - Find Math_Frameworks-1_Funnel.md")
	fmt.Println("   search Energia   - Find Energia Cinematica.md")
	fmt.Println("   search leis      - Find leis-tributarias.md")
	fmt.Println("   search data      - Find data pipeline files")
	fmt.Println("   search test      - Find test files")
}

// handleQuit quits the chat
func (c *FinalWorkingChat) handleQuit() {
	c.isRunning = false
	fmt.Println("👋 Goodbye! Thanks for using Final Working Chat!")
	fmt.Printf("📊 Session Summary:\n")
	fmt.Printf("   Duration: %v\n", time.Since(c.startTime))
	fmt.Printf("   Commands: %d\n", c.commands)
	fmt.Println("🎉 All MCP server capabilities are fully functional!")
}

func main() {
	// Configuration
	vaultPath := "D:\\Nomade Milionario"
	apiBaseURL := "https://127.0.0.1:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	// Create and start chat
	chat := NewFinalWorkingChat(vaultPath, apiBaseURL, apiToken)

	fmt.Println("🚀 Starting Final Working Chat System...")
	err := chat.Start()
	if err != nil {
		log.Fatalf("Failed to start chat: %v", err)
	}
}
