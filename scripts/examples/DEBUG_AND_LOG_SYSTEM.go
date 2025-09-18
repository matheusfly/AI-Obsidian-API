package main

import (
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

// DebugAndLogSystem provides comprehensive debugging and logging
type DebugAndLogSystem struct {
	logFile    *os.File
	apiBaseURL string
	apiToken   string
}

// NewDebugAndLogSystem creates a new debug and log system
func NewDebugAndLogSystem(apiBaseURL, apiToken string) (*DebugAndLogSystem, error) {
	logFile, err := os.OpenFile("debug.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		return nil, err
	}

	log.SetOutput(logFile)
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	return &DebugAndLogSystem{
		logFile:    logFile,
		apiBaseURL: apiBaseURL,
		apiToken:   apiToken,
	}, nil
}

// createHTTPClient creates an HTTP client with SSL certificate skipping
func (d *DebugAndLogSystem) createHTTPClient() *http.Client {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	return &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
	}
}

// LogInfo logs an info message
func (d *DebugAndLogSystem) LogInfo(message string) {
	log.Printf("[INFO] %s", message)
	fmt.Printf("ℹ️ %s\n", message)
}

// LogError logs an error message
func (d *DebugAndLogSystem) LogError(message string, err error) {
	if err != nil {
		log.Printf("[ERROR] %s: %v", message, err)
		fmt.Printf("❌ %s: %v\n", message, err)
	} else {
		log.Printf("[ERROR] %s", message)
		fmt.Printf("❌ %s\n", message)
	}
}

// LogSuccess logs a success message
func (d *DebugAndLogSystem) LogSuccess(message string) {
	log.Printf("[SUCCESS] %s", message)
	fmt.Printf("✅ %s\n", message)
}

// LogWarning logs a warning message
func (d *DebugAndLogSystem) LogWarning(message string) {
	log.Printf("[WARNING] %s", message)
	fmt.Printf("⚠️ %s\n", message)
}

// TestAPIConnection tests the API connection
func (d *DebugAndLogSystem) TestAPIConnection() error {
	d.LogInfo("Testing API connection...")

	client := d.createHTTPClient()
	req, err := http.NewRequest("GET", d.apiBaseURL+"/vault/", nil)
	if err != nil {
		d.LogError("Failed to create request", err)
		return err
	}
	req.Header.Set("Authorization", "Bearer "+d.apiToken)

	start := time.Now()
	resp, err := client.Do(req)
	duration := time.Since(start)

	if err != nil {
		d.LogError("API connection failed", err)
		return err
	}
	defer resp.Body.Close()

	d.LogSuccess(fmt.Sprintf("API connection successful (Status: %d, Duration: %v)", resp.StatusCode, duration))
	return nil
}

// TestFileAccess tests file access
func (d *DebugAndLogSystem) TestFileAccess() error {
	d.LogInfo("Testing file access...")

	// First get list of files
	client := d.createHTTPClient()
	req, err := http.NewRequest("GET", d.apiBaseURL+"/vault/", nil)
	if err != nil {
		d.LogError("Failed to create request", err)
		return err
	}
	req.Header.Set("Authorization", "Bearer "+d.apiToken)

	resp, err := client.Do(req)
	if err != nil {
		d.LogError("Failed to get file list", err)
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		d.LogError(fmt.Sprintf("Failed to get file list (Status: %d)", resp.StatusCode), nil)
		return fmt.Errorf("status code: %d", resp.StatusCode)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		d.LogError("Failed to read response", err)
		return err
	}

	d.LogSuccess(fmt.Sprintf("File list retrieved (%d bytes)", len(body)))

	// Try to parse JSON
	var result struct {
		Files []string `json:"files"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		d.LogError("Failed to parse JSON response", err)
		d.LogInfo(fmt.Sprintf("Raw response: %s", string(body)[:minInt(200, len(body))]))
		return err
	}

	d.LogSuccess(fmt.Sprintf("JSON parsing successful (%d files found)", len(result.Files)))
	
	// Test accessing first file
	if len(result.Files) > 0 {
		testFile := result.Files[0]
		d.LogInfo(fmt.Sprintf("Testing access to file: %s", testFile))

		req2, err := http.NewRequest("GET", d.apiBaseURL+"/vault/"+testFile, nil)
		if err != nil {
			d.LogError("Failed to create file request", err)
			return err
		}
		req2.Header.Set("Authorization", "Bearer "+d.apiToken)

		resp2, err := client.Do(req2)
		if err != nil {
			d.LogError("Failed to access file", err)
			return err
		}
		defer resp2.Body.Close()

		if resp2.StatusCode == http.StatusOK {
			d.LogSuccess(fmt.Sprintf("File access successful: %s", testFile))
		} else {
			d.LogWarning(fmt.Sprintf("File access returned status %d: %s", resp2.StatusCode, testFile))
		}
	}

	return nil
}

// TestCreateFile tests file creation
func (d *DebugAndLogSystem) TestCreateFile() error {
	d.LogInfo("Testing file creation...")

	testFilename := fmt.Sprintf("debug-test-%d.md", time.Now().Unix())
	testContent := fmt.Sprintf("# Debug Test File\n\nCreated at: %s\n\nThis is a test file created by the debug system.", time.Now().Format("2006-01-02 15:04:05"))

	client := d.createHTTPClient()
	req, err := http.NewRequest("POST", d.apiBaseURL+"/vault/"+testFilename, strings.NewReader(testContent))
	if err != nil {
		d.LogError("Failed to create file request", err)
		return err
	}
	req.Header.Set("Authorization", "Bearer "+d.apiToken)
	req.Header.Set("Content-Type", "text/markdown")

	resp, err := client.Do(req)
	if err != nil {
		d.LogError("Failed to create file", err)
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusCreated {
		d.LogSuccess(fmt.Sprintf("File creation successful: %s", testFilename))

		// Clean up - delete the test file
		d.LogInfo("Cleaning up test file...")
		req2, err := http.NewRequest("DELETE", d.apiBaseURL+"/vault/"+testFilename, nil)
		if err != nil {
			d.LogWarning("Failed to create delete request", err)
			return nil
		}
		req2.Header.Set("Authorization", "Bearer "+d.apiToken)

		resp2, err := client.Do(req2)
		if err != nil {
			d.LogWarning("Failed to delete test file", err)
			return nil
		}
		defer resp2.Body.Close()

		if resp2.StatusCode == http.StatusOK {
			d.LogSuccess("Test file cleaned up successfully")
		} else {
			d.LogWarning(fmt.Sprintf("Test file cleanup returned status %d", resp2.StatusCode))
		}
	} else {
		d.LogError(fmt.Sprintf("File creation failed (Status: %d)", resp.StatusCode), nil)
		return fmt.Errorf("status code: %d", resp.StatusCode)
	}

	return nil
}

// RunComprehensiveTest runs all tests
func (d *DebugAndLogSystem) RunComprehensiveTest() error {
	d.LogInfo("Starting comprehensive debug test...")
	fmt.Println(strings.Repeat("=", 60))

	tests := []struct {
		name string
		test func() error
	}{
		{"API Connection", d.TestAPIConnection},
		{"File Access", d.TestFileAccess},
		{"File Creation", d.TestCreateFile},
	}

	passed := 0
	total := len(tests)

	for i, test := range tests {
		fmt.Printf("\nTest %d/%d: %s\n", i+1, total, test.name)
		fmt.Println(strings.Repeat("-", 40))

		if err := test.test(); err != nil {
			d.LogError(fmt.Sprintf("Test '%s' failed", test.name), err)
		} else {
			d.LogSuccess(fmt.Sprintf("Test '%s' passed", test.name))
			passed++
		}
	}

	fmt.Println(strings.Repeat("=", 60))
	fmt.Printf("\n📊 TEST RESULTS:\n")
	fmt.Printf("   Total Tests: %d\n", total)
	fmt.Printf("   Passed: %d\n", passed)
	fmt.Printf("   Failed: %d\n", total-passed)
	fmt.Printf("   Success Rate: %.1f%%\n", float64(passed)/float64(total)*100)

	if passed == total {
		d.LogSuccess("All tests passed! System is fully functional.")
		return nil
	} else {
		d.LogError(fmt.Sprintf("%d tests failed", total-passed), nil)
		return fmt.Errorf("%d tests failed", total-passed)
	}
}

// Close closes the debug system
func (d *DebugAndLogSystem) Close() error {
	if d.logFile != nil {
		return d.logFile.Close()
	}
	return nil
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Example usage
func main() {
	// Configuration
	apiBaseURL := "https://127.0.0.1:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	// Create debug system
	debug, err := NewDebugAndLogSystem(apiBaseURL, apiToken)
	if err != nil {
		log.Fatalf("Failed to create debug system: %v", err)
	}
	defer debug.Close()

	// Run comprehensive test
	err = debug.RunComprehensiveTest()
	if err != nil {
		log.Fatalf("Debug test failed: %v", err)
	}

	fmt.Println("\n🎉 Debug test completed successfully!")
	fmt.Println("📄 Check debug.log for detailed logs")
}
