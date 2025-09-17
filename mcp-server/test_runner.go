package main

import (
	"fmt"
	"os"
	"os/exec"
	"time"
)

func main() {
	fmt.Println("🧪 Running MCP Server Tests")
	fmt.Println("==========================")

	// Test 1: Build the server
	fmt.Println("\n1. Building MCP Server...")
	buildCmd := exec.Command("go", "build", "scripts/working_mcp_server.go")
	buildCmd.Dir = "."
	buildOutput, err := buildCmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Build failed: %v\n", err)
		fmt.Printf("Output: %s\n", buildOutput)
		os.Exit(1)
	}
	fmt.Println("✅ Server built successfully")

	// Test 2: Run unit tests
	fmt.Println("\n2. Running Unit Tests...")
	testCmd := exec.Command("go", "test", "-v", "tests/tools_test.go")
	testCmd.Dir = "."
	testOutput, err := testCmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Unit tests failed: %v\n", err)
		fmt.Printf("Output: %s\n", testOutput)
	} else {
		fmt.Println("✅ Unit tests passed")
	}

	// Test 3: Start server in background
	fmt.Println("\n3. Starting MCP Server...")
	serverCmd := exec.Command("go", "run", "scripts/working_mcp_server.go", "-mock=true", "-port=3011")
	serverCmd.Dir = "."

	// Start server in background
	if err := serverCmd.Start(); err != nil {
		fmt.Printf("❌ Failed to start server: %v\n", err)
		os.Exit(1)
	}

	// Wait for server to start
	time.Sleep(3 * time.Second)
	fmt.Println("✅ Server started")

	// Test 4: Test health endpoint
	fmt.Println("\n4. Testing Health Endpoint...")
	curlCmd := exec.Command("curl", "http://localhost:3011/health")
	curlOutput, err := curlCmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		fmt.Printf("Output: %s\n", curlOutput)
	} else {
		fmt.Println("✅ Health check passed")
		fmt.Printf("Response: %s\n", curlOutput)
	}

	// Test 5: Test tools endpoint
	fmt.Println("\n5. Testing Tools Endpoint...")
	toolsCmd := exec.Command("curl", "http://localhost:3011/tools")
	toolsOutput, err := toolsCmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Tools endpoint failed: %v\n", err)
		fmt.Printf("Output: %s\n", toolsOutput)
	} else {
		fmt.Println("✅ Tools endpoint passed")
	}

	// Test 6: Test tool execution
	fmt.Println("\n6. Testing Tool Execution...")
	execCmd := exec.Command("curl", "-X", "POST", "-H", "Content-Type: application/json",
		"-d", `{"tool": "list_files_in_vault", "params": {}}`,
		"http://localhost:3011/tools/execute")
	execOutput, err := execCmd.CombinedOutput()
	if err != nil {
		fmt.Printf("❌ Tool execution failed: %v\n", err)
		fmt.Printf("Output: %s\n", execOutput)
	} else {
		fmt.Println("✅ Tool execution passed")
		fmt.Printf("Response: %s\n", execOutput)
	}

	fmt.Println("\n🎉 All tests completed!")
}
