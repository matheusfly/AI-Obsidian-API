package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"time"
)

func main() {
	fmt.Println("🔍 DEBUGGING SEARCH PROBLEM")
	fmt.Println("===========================")
	
	apiBaseURL := "https://127.0.0.1:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
	}
	
	fmt.Printf("🌐 Testing API: %s\n", apiBaseURL)
	
	// Test API connection
	req, err := http.NewRequest("GET", apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+apiToken)
	
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		fmt.Printf("❌ API returned status: %d\n", resp.StatusCode)
		return
	}
	
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read response: %v\n", err)
		return
	}
	
	fmt.Printf("✅ API Connection: SUCCESS\n")
	fmt.Printf("📥 Response length: %d bytes\n", len(body))
	
	// Show raw response (first 500 chars)
	fmt.Printf("📥 Raw response (first 500 chars):\n%s\n", string(body)[:500])
	
	// Try parsing with the new structure
	var result struct {
		Files []string `json:"files"`
	}
	
	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("❌ JSON parsing failed: %v\n", err)
		return
	}
	
	fmt.Printf("✅ JSON parsing: SUCCESS\n")
	fmt.Printf("📄 Files found: %d\n", len(result.Files))
	
	if len(result.Files) > 0 {
		fmt.Println("📄 First 20 files:")
		for i, file := range result.Files {
			if i < 20 {
				fmt.Printf("   %d. %s\n", i+1, file)
			}
		}
		
		// Test searches with detailed output
		queries := []string{"logica", "matematica", "performance", "test", "md", "API", "AGENTS"}
		for _, query := range queries {
			fmt.Printf("\n🔍 Testing search for: '%s'\n", query)
			var matches []string
			for _, file := range result.Files {
				if strings.Contains(strings.ToLower(file), strings.ToLower(query)) {
					matches = append(matches, file)
					fmt.Printf("   ✅ MATCH: %s\n", file)
				}
			}
			fmt.Printf("📊 Total matches for '%s': %d\n", query, len(matches))
		}
		
		// Test case sensitivity
		fmt.Printf("\n🔍 Testing case sensitivity:\n")
		testFile := result.Files[0]
		fmt.Printf("   Original file: %s\n", testFile)
		fmt.Printf("   Lowercase: %s\n", strings.ToLower(testFile))
		fmt.Printf("   Contains 'md': %t\n", strings.Contains(strings.ToLower(testFile), "md"))
		fmt.Printf("   Contains 'MD': %t\n", strings.Contains(strings.ToLower(testFile), "MD"))
		
	} else {
		fmt.Println("❌ No files found in response!")
		fmt.Printf("Raw response: %s\n", string(body))
	}
	
	fmt.Println("\n🎉 Debug completed!")
}
