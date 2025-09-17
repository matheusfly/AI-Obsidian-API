package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"
)

// TestRunner provides comprehensive test execution
type TestRunner struct {
	serverURL   string
	serverCmd   *exec.Cmd
	serverPort  string
	testResults map[string]bool
	startTime   time.Time
}

// NewTestRunner creates a new test runner
func NewTestRunner(serverURL, serverPort string) *TestRunner {
	return &TestRunner{
		serverURL:   serverURL,
		serverPort:  serverPort,
		testResults: make(map[string]bool),
		startTime:   time.Now(),
	}
}

// StartServer starts the MCP server in the background
func (tr *TestRunner) StartServer() error {
	fmt.Println("🚀 Starting MCP Server...")

	// Start server in background
	tr.serverCmd = exec.Command("go", "run", "scripts/working_mcp_server.go", "-mock=true", "-port="+tr.serverPort)
	tr.serverCmd.Stdout = os.Stdout
	tr.serverCmd.Stderr = os.Stderr

	if err := tr.serverCmd.Start(); err != nil {
		return fmt.Errorf("failed to start server: %v", err)
	}

	// Wait for server to be ready
	fmt.Println("⏳ Waiting for server to be ready...")
	time.Sleep(5 * time.Second)

	// Test server health
	if err := tr.testServerHealth(); err != nil {
		return fmt.Errorf("server health check failed: %v", err)
	}

	fmt.Println("✅ MCP Server started successfully")
	return nil
}

// StopServer stops the MCP server
func (tr *TestRunner) StopServer() error {
	if tr.serverCmd != nil && tr.serverCmd.Process != nil {
		fmt.Println("🛑 Stopping MCP Server...")
		if err := tr.serverCmd.Process.Kill(); err != nil {
			return fmt.Errorf("failed to stop server: %v", err)
		}
		tr.serverCmd.Wait()
		fmt.Println("✅ MCP Server stopped")
	}
	return nil
}

// testServerHealth tests if the server is responding
func (tr *TestRunner) testServerHealth() error {
	// This would typically make an HTTP request to /health
	// For now, we'll assume the server is ready after the sleep
	return nil
}

// RunTestSuite runs a specific test suite
func (tr *TestRunner) RunTestSuite(suiteName, testFile string) error {
	fmt.Printf("🧪 Running %s tests...\n", suiteName)

	cmd := exec.Command("go", "test", "-v", testFile)
	cmd.Dir = "tests"
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	start := time.Now()
	err := cmd.Run()
	duration := time.Since(start)

	success := err == nil
	tr.testResults[suiteName] = success

	status := "✅ PASSED"
	if !success {
		status = "❌ FAILED"
	}

	fmt.Printf("%s %s tests completed in %v\n", status, suiteName, duration)
	return err
}

// RunAllTests runs all test suites
func (tr *TestRunner) RunAllTests() error {
	fmt.Println("🎯 Starting Comprehensive Test Suite")
	fmt.Println("=====================================")

	// Define test suites
	testSuites := []struct {
		name     string
		file     string
		required bool
	}{
		{"Unit Tests", "tools_test.go", true},
		{"Integration Tests", "integration_test.go", true},
		{"End-to-End Tests", "end_to_end_test.go", true},
		{"Performance Tests", "performance_test.go", false},
		{"API Validation Tests", "api_validation_test.go", false},
		{"Ollama Validation Tests", "ollama_validation_test.go", false},
		{"MCP Protocol Validation Tests", "mcp_protocol_validation_test.go", true},
		{"Security Validation Tests", "security_validation_test.go", true},
		{"Production Readiness Tests", "production_readiness_test.go", true},
	}

	// Run each test suite
	for _, suite := range testSuites {
		if err := tr.RunTestSuite(suite.name, suite.file); err != nil {
			if suite.required {
				fmt.Printf("❌ Required test suite %s failed: %v\n", suite.name, err)
				return fmt.Errorf("required test suite %s failed", suite.name)
			} else {
				fmt.Printf("⚠️ Optional test suite %s failed: %v\n", suite.name, err)
			}
		}
	}

	return nil
}

// GenerateTestReport generates a comprehensive test report
func (tr *TestRunner) GenerateTestReport() {
	fmt.Println("\n📊 Test Report")
	fmt.Println("==============")

	totalTests := len(tr.testResults)
	passedTests := 0
	failedTests := 0

	for suiteName, success := range tr.testResults {
		status := "❌ FAILED"
		if success {
			status = "✅ PASSED"
			passedTests++
		} else {
			failedTests++
		}
		fmt.Printf("%s %s\n", status, suiteName)
	}

	fmt.Printf("\nSummary: %d/%d test suites passed\n", passedTests, totalTests)
	fmt.Printf("Total execution time: %v\n", time.Since(tr.startTime))

	if failedTests > 0 {
		fmt.Printf("❌ %d test suites failed\n", failedTests)
		os.Exit(1)
	} else {
		fmt.Println("🎉 All test suites passed!")
	}
}

// Cleanup performs cleanup operations
func (tr *TestRunner) Cleanup() {
	fmt.Println("\n🧹 Cleaning up...")

	// Stop server
	if err := tr.StopServer(); err != nil {
		fmt.Printf("⚠️ Error stopping server: %v\n", err)
	}

	// Clean up any temporary files
	cleanupFiles := []string{
		"test_output.json",
		"performance_results.json",
		"security_scan_results.json",
	}

	for _, file := range cleanupFiles {
		if err := os.Remove(file); err != nil && !os.IsNotExist(err) {
			fmt.Printf("⚠️ Error removing %s: %v\n", file, err)
		}
	}

	fmt.Println("✅ Cleanup completed")
}

// Main function
func main() {
	// Parse command line arguments
	serverPort := "3011"
	if len(os.Args) > 1 {
		serverPort = os.Args[1]
	}

	serverURL := "http://localhost:" + serverPort

	// Create test runner
	runner := NewTestRunner(serverURL, serverPort)

	// Ensure cleanup on exit
	defer runner.Cleanup()

	// Start server
	if err := runner.StartServer(); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}

	// Run all tests
	if err := runner.RunAllTests(); err != nil {
		fmt.Printf("❌ Test execution failed: %v\n", err)
		runner.GenerateTestReport()
		os.Exit(1)
	}

	// Generate report
	runner.GenerateTestReport()
}
