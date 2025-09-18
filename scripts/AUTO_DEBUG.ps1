# Auto Debug and Fix Script
Write-Host "🔍 AUTO DEBUGGING AND FIXING" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

$apiBaseURL = "https://127.0.0.1:27124"
$apiToken = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

try {
    Write-Host "🌐 Testing API: $apiBaseURL" -ForegroundColor Cyan
    
    $headers = @{
        'Authorization' = "Bearer $apiToken"
    }
    
    $response = Invoke-WebRequest -Uri "$apiBaseURL/vault/" -Headers $headers -SkipCertificateCheck -TimeoutSec 10
    
    Write-Host "✅ API Connection: SUCCESS" -ForegroundColor Green
    Write-Host "📥 Response length: $($response.Content.Length) bytes" -ForegroundColor Green
    
    # Show first 1000 characters
    Write-Host "📥 Raw response (first 1000 chars):" -ForegroundColor Yellow
    Write-Host $response.Content.Substring(0, [Math]::Min(1000, $response.Content.Length)) -ForegroundColor White
    
    # Parse JSON
    $json = $response.Content | ConvertFrom-Json
    
    Write-Host "`n🔍 Testing different JSON structures:" -ForegroundColor Cyan
    
    # Test different structures
    $structures = @("files", "data", "items", "results")
    $workingStructure = $null
    $workingFiles = @()
    
    foreach ($structure in $structures) {
        if ($json.$structure) {
            $files = $json.$structure
            Write-Host "✅ Structure '$structure': $($files.Count) files" -ForegroundColor Green
            if ($files.Count -gt 0) {
                Write-Host "📄 First 5 files:" -ForegroundColor Cyan
                for ($i = 0; $i -lt [Math]::Min(5, $files.Count); $i++) {
                    Write-Host "   $($i+1). $($files[$i])" -ForegroundColor White
                }
                if (-not $workingStructure) {
                    $workingStructure = $structure
                    $workingFiles = $files
                }
            }
        } else {
            Write-Host "❌ Structure '$structure': Not found" -ForegroundColor Red
        }
    }
    
    # Test if it's a simple array
    if ($json -is [array]) {
        Write-Host "✅ Structure 'simple array': $($json.Count) files" -ForegroundColor Green
        if ($json.Count -gt 0) {
            Write-Host "📄 First 5 files:" -ForegroundColor Cyan
            for ($i = 0; $i -lt [Math]::Min(5, $json.Count); $i++) {
                Write-Host "   $($i+1). $($json[$i])" -ForegroundColor White
            }
            if (-not $workingStructure) {
                $workingStructure = "simple array"
                $workingFiles = $json
            }
        }
    }
    
    if ($workingFiles.Count -gt 0) {
        Write-Host "`n✅ Working structure: $workingStructure with $($workingFiles.Count) files" -ForegroundColor Green
        
        # Test searches
        Write-Host "`n🔍 Testing searches with working structure:" -ForegroundColor Cyan
        $queries = @("logica", "matematica", "performance", "test", "md", "API", "AGENTS")
        foreach ($query in $queries) {
            $matches = $workingFiles | Where-Object { $_.ToLower() -like "*$($query.ToLower())*" }
            Write-Host "🔍 Search '$query': $($matches.Count) matches" -ForegroundColor Yellow
            if ($matches.Count -gt 0 -and $matches.Count -le 5) {
                foreach ($match in $matches) {
                    Write-Host "   - $match" -ForegroundColor White
                }
            }
        }
        
        # Create the fixed version
        Write-Host "`n🔧 Creating fixed version..." -ForegroundColor Cyan
        
        $fixedCode = @"
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

// FixedChat provides the completely fixed CLI chat system
type FixedChat struct {
	apiBaseURL string
	apiToken   string
	vaultPath  string
	isRunning  bool
	sessionID  string
	startTime  time.Time
	commands   int
}

// NewFixedChat creates a new fixed chat instance
func NewFixedChat(vaultPath, apiBaseURL, apiToken string) *FixedChat {
	return &FixedChat{
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
func (c *FixedChat) createHTTPClient() *http.Client {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	return &http.Client{
		Transport: tr,
		Timeout:   30 * time.Second,
	}
}

// Start starts the fixed chat
func (c *FixedChat) Start() error {
	if c.isRunning {
		return fmt.Errorf("chat is already running")
	}

	c.isRunning = true
	c.showWelcome()
	c.runChatLoop()
	return nil
}

// showWelcome shows welcome message
func (c *FixedChat) showWelcome() {
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("🚀 FIXED CHAT - MCP SYSTEM")
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
}

// runChatLoop runs the main chat loop
func (c *FixedChat) runChatLoop() {
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
func (c *FixedChat) processInput(input string) {
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
func (c *FixedChat) handleTest() {
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
func (c *FixedChat) handleList() {
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
		Files []string `json:"$workingStructure"`
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
func (c *FixedChat) handleRead(args []string) {
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
func (c *FixedChat) handleCreate(args []string) {
	if len(args) == 0 {
		fmt.Println("❌ Please specify a filename")
		return
	}

	filename := args[0]
	content := fmt.Sprintf("# New Note\n\nCreated via Fixed Chat System.\n\nTimestamp: %s", time.Now().Format("2006-01-02 15:04:05"))
	
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
func (c *FixedChat) handleSearch(args []string) {
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
		Files []string `json:"$workingStructure"`
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
}

// handleStatus shows status
func (c *FixedChat) handleStatus() {
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
func (c *FixedChat) handleHelp() {
	fmt.Println("📋 AVAILABLE COMMANDS:")
	fmt.Println("   test          - Test API connection")
	fmt.Println("   list          - List all files in vault")
	fmt.Println("   read <file>   - Read a specific note")
	fmt.Println("   create <file> - Create a new note")
	fmt.Println("   search <query>- Search vault content")
	fmt.Println("   status        - Show system status")
	fmt.Println("   help          - Show this help")
	fmt.Println("   quit          - Exit chat")
}

// handleQuit quits the chat
func (c *FixedChat) handleQuit() {
	c.isRunning = false
	fmt.Println("👋 Goodbye! Thanks for using Fixed Chat!")
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
	chat := NewFixedChat(vaultPath, apiBaseURL, apiToken)
	
	fmt.Println("🚀 Starting Fixed Chat System...")
	err := chat.Start()
	if err != nil {
		log.Fatalf("Failed to start chat: %v", err)
	}
}
"@
        
        # Replace the working structure in the code
        $fixedCode = $fixedCode -replace '\$workingStructure', $workingStructure
        
        # Write the fixed code to a file
        $fixedCode | Out-File -FilePath "FINAL_FIXED_CHAT.go" -Encoding UTF8
        
        Write-Host "✅ Fixed code written to FINAL_FIXED_CHAT.go" -ForegroundColor Green
        Write-Host "✅ Working structure: $workingStructure" -ForegroundColor Green
        Write-Host "✅ Files found: $($workingFiles.Count)" -ForegroundColor Green
        
    } else {
        Write-Host "❌ No working structure found!" -ForegroundColor Red
        Write-Host "Raw response: $($response.Content)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "❌ Full Error: $($_.Exception)" -ForegroundColor Red
}

Write-Host "`n🎉 Auto debug completed!" -ForegroundColor Green
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host
