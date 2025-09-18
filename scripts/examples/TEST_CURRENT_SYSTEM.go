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
	fmt.Println("🔍 TESTING CURRENT SYSTEM")
	fmt.Println("=========================")

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

	// Parse JSON
	var result struct {
		Files []string `json:"files"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("❌ JSON parsing failed: %v\n", err)
		fmt.Printf("Raw response: %s\n", string(body)[:200])
		return
	}

	fmt.Printf("✅ JSON parsing: SUCCESS\n")
	fmt.Printf("📄 Files found: %d\n", len(result.Files))

	if len(result.Files) > 0 {
		fmt.Println("📄 First 10 files:")
		for i, file := range result.Files {
			if i < 10 {
				fmt.Printf("   %d. %s\n", i+1, file)
			}
		}

		// Test searches
		queries := []string{"logica", "matematica", "test", "md", "API"}
		for _, query := range queries {
			var matches []string
			for _, file := range result.Files {
				if strings.Contains(strings.ToLower(file), strings.ToLower(query)) {
					matches = append(matches, file)
				}
			}
			fmt.Printf("🔍 Search '%s': %d matches\n", query, len(matches))
			if len(matches) > 0 && len(matches) <= 5 {
				for _, match := range matches {
					fmt.Printf("   - %s\n", match)
				}
			}
		}
	}

	fmt.Println("\n🎉 System test completed!")
	fmt.Println("✅ API Connection: Working")
	fmt.Println("✅ File Listing: Working")
	fmt.Println("✅ Search: Working")
	fmt.Println("✅ JSON Parsing: Working")
}
