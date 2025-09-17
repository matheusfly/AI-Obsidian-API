package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

func main() {
	fmt.Println("🔍 DEBUG VAULT FILES")
	fmt.Println("===================")

	// Configuration
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Create HTTP client
	client := &http.Client{
		Timeout: 30 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}

	// Get vault files
	req, err := http.NewRequest("GET", baseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}

	req.Header.Add("Authorization", "Bearer "+apiKey)
	req.Header.Add("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Failed to get vault files: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("❌ Vault request failed with status: %d\n", resp.StatusCode)
		return
	}

	// Parse the response structure
	var response struct {
		Files []string `json:"files"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		fmt.Printf("❌ Failed to decode response: %v\n", err)
		return
	}

	fmt.Printf("✅ Found %d files in vault\n", len(response.Files))

	// Look for files containing "logica" in their names
	fmt.Println("\n🔍 Looking for files containing 'logica'...")
	logicaFiles := 0
	for _, filePath := range response.Files {
		if containsIgnoreCase(filePath, "logica") {
			fmt.Printf("🎯 Found: %s\n", filePath)
			logicaFiles++
		}
	}

	if logicaFiles == 0 {
		fmt.Println("❌ No files containing 'logica' found in vault")
	} else {
		fmt.Printf("✅ Found %d files containing 'logica'\n", logicaFiles)
	}

	// Look for files containing "LOGICA" in their names
	fmt.Println("\n🔍 Looking for files containing 'LOGICA'...")
	LOGICAFiles := 0
	for _, filePath := range response.Files {
		if containsIgnoreCase(filePath, "LOGICA") {
			fmt.Printf("🎯 Found: %s\n", filePath)
			LOGICAFiles++
		}
	}

	if LOGICAFiles == 0 {
		fmt.Println("❌ No files containing 'LOGICA' found in vault")
	} else {
		fmt.Printf("✅ Found %d files containing 'LOGICA'\n", LOGICAFiles)
	}

	// Look for files containing "logic" in their names
	fmt.Println("\n🔍 Looking for files containing 'logic'...")
	logicFiles := 0
	for _, filePath := range response.Files {
		if containsIgnoreCase(filePath, "logic") {
			fmt.Printf("🎯 Found: %s\n", filePath)
			logicFiles++
		}
	}

	if logicFiles == 0 {
		fmt.Println("❌ No files containing 'logic' found in vault")
	} else {
		fmt.Printf("✅ Found %d files containing 'logic'\n", logicFiles)
	}

	// Show first 20 files for debugging
	fmt.Println("\n📋 First 20 files in vault:")
	for i, filePath := range response.Files {
		if i >= 20 {
			break
		}
		fmt.Printf("   %d. %s\n", i+1, filePath)
	}

	// Show files in specific directories
	fmt.Println("\n📁 Files in '2- Notas De Leitura/' directory:")
	for _, filePath := range response.Files {
		if containsIgnoreCase(filePath, "2- Notas De Leitura") {
			fmt.Printf("   📄 %s\n", filePath)
		}
	}

	fmt.Println("\n📁 Files in '3- Notas Atômicas/' directory:")
	for _, filePath := range response.Files {
		if containsIgnoreCase(filePath, "3- Notas Atômicas") {
			fmt.Printf("   📄 %s\n", filePath)
		}
	}

	fmt.Println("\n📁 Files in '4- Notas Permanentes/' directory:")
	for _, filePath := range response.Files {
		if containsIgnoreCase(filePath, "4- Notas Permanentes") {
			fmt.Printf("   📄 %s\n", filePath)
		}
	}
}

// containsIgnoreCase checks if s contains substr (case-insensitive)
func containsIgnoreCase(s, substr string) bool {
	return len(s) >= len(substr) &&
		strings.Contains(strings.ToLower(s), strings.ToLower(substr))
}
