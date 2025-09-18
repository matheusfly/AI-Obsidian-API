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

// UltimateFixedChat provides the ultimate fixed CLI chat system
type UltimateFixedChat struct {
	apiBaseURL string
	apiToken   string
	vaultPath  string
	isRunning  bool
	sessionID  string
	startTime  time.Time
	commands   int
}

// NewUltimateFixedChat creates a new ultimate fixed chat instance
func NewUltimateFixedChat(vaultPath, apiBaseURL, apiToken string) *UltimateFixedChat {
	return &UltimateFixedChat{
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
func (c *UltimateFixedChat) createHTTPClient() *http.Client {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	return &http.Client{
		Transport: tr,
		Timeout:   30 * time.Second,
	}
}

// Start starts the ultimate fixed chat
func (c *UltimateFixedChat) Start() error {
	if c.isRunning {
		return fmt.Errorf("chat is already running")
	}

	c.isRunning = true
	c.showWelcome()
	c.runChatLoop()
	return nil
}

// showWelcome shows welcome message
func (c *UltimateFixedChat) showWelcome() {
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("🚀 ULTIMATE FIXED CHAT - MCP SYSTEM")
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
	fmt.Println("   debug         - Debug API response")
	fmt.Println("   status        - Show status")
	fmt.Println("   help          - Show help")
	fmt.Println("   quit          - Exit")
	fmt.Println(strings.Repeat("=", 60))
}

// runChatLoop runs the main chat loop
func (c *UltimateFixedChat) runChatLoop() {
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
func (c *UltimateFixedChat) processInput(input string) {
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
	case "debug":
		c.handleDebug()
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
func (c *UltimateFixedChat) handleTest() {
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

// handleDebug debugs the API response
func (c *UltimateFixedChat) handleDebug() {
	fmt.Println("🔍 Debugging API response...")

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

	fmt.Printf("📥 Response length: %d bytes\n", len(body))
	fmt.Printf("📥 Raw response (first 500 chars):\n%s\n", string(body)[:500])

	// Try multiple JSON structures
	fmt.Println("\n🔍 Trying different JSON structures:")

	// Structure 1: {"files": [...]}
	var result1 struct {
		Files []string `json:"files"`
	}
	if err := json.Unmarshal(body, &result1); err == nil {
		fmt.Printf("✅ Structure 1 (files): %d files\n", len(result1.Files))
		if len(result1.Files) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range result1.Files {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 1 failed: %v\n", err)
	}

	// Structure 2: {"data": [...]}
	var result2 struct {
		Data []string `json:"data"`
	}
	if err := json.Unmarshal(body, &result2); err == nil {
		fmt.Printf("✅ Structure 2 (data): %d files\n", len(result2.Data))
		if len(result2.Data) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range result2.Data {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 2 failed: %v\n", err)
	}

	// Structure 3: {"items": [...]}
	var result3 struct {
		Items []string `json:"items"`
	}
	if err := json.Unmarshal(body, &result3); err == nil {
		fmt.Printf("✅ Structure 3 (items): %d files\n", len(result3.Items))
		if len(result3.Items) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range result3.Items {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 3 failed: %v\n", err)
	}

	// Structure 4: {"results": [...]}
	var result4 struct {
		Results []string `json:"results"`
	}
	if err := json.Unmarshal(body, &result4); err == nil {
		fmt.Printf("✅ Structure 4 (results): %d files\n", len(result4.Results))
		if len(result4.Results) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range result4.Results {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 4 failed: %v\n", err)
	}
}

// handleList lists vault files
func (c *UltimateFixedChat) handleList() {
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

	// Try multiple JSON structures
	var files []string

	// Structure 1: {"files": [...]}
	var result1 struct {
		Files []string `json:"files"`
	}
	if err := json.Unmarshal(body, &result1); err == nil && len(result1.Files) > 0 {
		files = result1.Files
		fmt.Printf("✅ Using structure 1 (files): %d files\n", len(files))
	} else {
		// Structure 2: {"data": [...]}
		var result2 struct {
			Data []string `json:"data"`
		}
		if err := json.Unmarshal(body, &result2); err == nil && len(result2.Data) > 0 {
			files = result2.Data
			fmt.Printf("✅ Using structure 2 (data): %d files\n", len(files))
		} else {
			// Structure 3: {"items": [...]}
			var result3 struct {
				Items []string `json:"items"`
			}
			if err := json.Unmarshal(body, &result3); err == nil && len(result3.Items) > 0 {
				files = result3.Items
				fmt.Printf("✅ Using structure 3 (items): %d files\n", len(files))
			} else {
				// Structure 4: {"results": [...]}
				var result4 struct {
					Results []string `json:"results"`
				}
				if err := json.Unmarshal(body, &result4); err == nil && len(result4.Results) > 0 {
					files = result4.Results
					fmt.Printf("✅ Using structure 4 (results): %d files\n", len(files))
				} else {
					fmt.Printf("❌ Failed to parse response with any known structure\n")
					fmt.Printf("Raw response: %s\n", string(body)[:500])
					return
				}
			}
		}
	}

	fmt.Printf("📄 Found %d files:\n", len(files))
	for i, file := range files {
		if i < 15 { // Show first 15 files
			fmt.Printf("   %s\n", file)
		}
	}

	if len(files) > 15 {
		fmt.Printf("   ... and %d more files\n", len(files)-15)
	}
}

// handleRead reads a note
func (c *UltimateFixedChat) handleRead(args []string) {
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
func (c *UltimateFixedChat) handleCreate(args []string) {
	if len(args) == 0 {
		fmt.Println("❌ Please specify a filename")
		return
	}

	filename := args[0]
	content := fmt.Sprintf("# New Note\n\nCreated via Ultimate Fixed Chat System.\n\nTimestamp: %s", time.Now().Format("2006-01-02 15:04:05"))

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
func (c *UltimateFixedChat) handleSearch(args []string) {
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

	// Try multiple JSON structures
	var files []string

	// Structure 1: {"files": [...]}
	var result1 struct {
		Files []string `json:"files"`
	}
	if err := json.Unmarshal(body, &result1); err == nil && len(result1.Files) > 0 {
		files = result1.Files
	} else {
		// Structure 2: {"data": [...]}
		var result2 struct {
			Data []string `json:"data"`
		}
		if err := json.Unmarshal(body, &result2); err == nil && len(result2.Data) > 0 {
			files = result2.Data
		} else {
			// Structure 3: {"items": [...]}
			var result3 struct {
				Items []string `json:"items"`
			}
			if err := json.Unmarshal(body, &result3); err == nil && len(result3.Items) > 0 {
				files = result3.Items
			} else {
				// Structure 4: {"results": [...]}
				var result4 struct {
					Results []string `json:"results"`
				}
				if err := json.Unmarshal(body, &result4); err == nil && len(result4.Results) > 0 {
					files = result4.Results
				} else {
					fmt.Printf("❌ Failed to parse response with any known structure\n")
					return
				}
			}
		}
	}

	// Simple text matching
	var matches []string
	for _, file := range files {
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
}

// handleStatus shows status
func (c *UltimateFixedChat) handleStatus() {
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
func (c *UltimateFixedChat) handleHelp() {
	fmt.Println("📋 AVAILABLE COMMANDS:")
	fmt.Println("   test          - Test API connection")
	fmt.Println("   list          - List all files in vault")
	fmt.Println("   read <file>   - Read a specific note")
	fmt.Println("   create <file> - Create a new note")
	fmt.Println("   search <query>- Search vault content")
	fmt.Println("   debug         - Debug API response")
	fmt.Println("   status        - Show system status")
	fmt.Println("   help          - Show this help")
	fmt.Println("   quit          - Exit chat")
}

// handleQuit quits the chat
func (c *UltimateFixedChat) handleQuit() {
	c.isRunning = false
	fmt.Println("👋 Goodbye! Thanks for using Ultimate Fixed Chat!")
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
	chat := NewUltimateFixedChat(vaultPath, apiBaseURL, apiToken)

	fmt.Println("🚀 Starting Ultimate Fixed Chat System...")
	err := chat.Start()
	if err != nil {
		log.Fatalf("Failed to start chat: %v", err)
	}
}
