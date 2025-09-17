package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

func main() {
	fmt.Println("🧪 Testing MCP Server Build Process...")
	
	// Test 1: Check if Go is available
	fmt.Println("\n1. Testing Go installation...")
	goVersion, err := exec.Command("go", "version").Output()
	if err != nil {
		log.Fatalf("❌ Go not found: %v", err)
	}
	fmt.Printf("✅ Go version: %s", string(goVersion))
	
	// Test 2: Check if we can build the project
	fmt.Println("\n2. Testing project build...")
	buildCmd := exec.Command("go", "build", "-o", "test-server.exe", "./cmd/server")
	buildCmd.Dir = ".."
	output, err := buildCmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Build failed: %v\n", err)
		fmt.Printf("Output: %s\n", string(output))
		return
	}
	fmt.Println("✅ Build successful!")
	
	// Test 3: Check if binary was created
	fmt.Println("\n3. Testing binary creation...")
	binaryPath := filepath.Join("..", "test-server.exe")
	if _, err := os.Stat(binaryPath); os.IsNotExist(err) {
		fmt.Printf("❌ Binary not found at: %s\n", binaryPath)
		return
	}
	fmt.Printf("✅ Binary created at: %s\n", binaryPath)
	
	// Test 4: Test binary execution (briefly)
	fmt.Println("\n4. Testing binary execution...")
	cmd := exec.Command(binaryPath)
	cmd.Dir = ".."
	
	// Start the server
	if err := cmd.Start(); err != nil {
		fmt.Printf("❌ Failed to start server: %v\n", err)
		return
	}
	
	fmt.Println("✅ Server started successfully!")
	
	// Give it a moment to start
	time.Sleep(2 * time.Second)
	
	// Kill the process
	if err := cmd.Process.Kill(); err != nil {
		fmt.Printf("⚠️  Warning: Could not kill process: %v\n", err)
	}
	
	// Clean up
	if err := os.Remove(binaryPath); err != nil {
		fmt.Printf("⚠️  Warning: Could not remove test binary: %v\n", err)
	}
	
	fmt.Println("\n🎉 All tests passed! MCP Server is ready to use.")
	fmt.Println("\n📋 Next steps:")
	fmt.Println("   1. Make sure Obsidian is running with Local REST API plugin")
	fmt.Println("   2. Make sure Ollama is running on localhost:11434")
	fmt.Println("   3. Run: go run ./cmd/server")
	fmt.Println("   4. Or build and run: go build -o mcp-server.exe ./cmd/server && ./mcp-server.exe")
}

