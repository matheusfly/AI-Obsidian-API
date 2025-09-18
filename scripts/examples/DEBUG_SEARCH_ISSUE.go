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
	fmt.Println("🔍 DEBUGGING SEARCH ISSUE")
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

	// Get files
	req, err := http.NewRequest("GET", apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Error: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+apiToken)

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Error: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Error: %v\n", err)
		return
	}

	fmt.Printf("📥 Raw response length: %d bytes\n", len(body))
	fmt.Printf("📥 Raw response: %s\n", string(body)[:500])

	// Try parsing with the new structure
	var result struct {
		Files []string `json:"files"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("❌ JSON parsing failed: %v\n", err)
		return
	}

	fmt.Printf("✅ Parsed successfully: %d files\n", len(result.Files))

	if len(result.Files) > 0 {
		fmt.Println("📄 First 10 files:")
		for i, file := range result.Files {
			if i < 10 {
				fmt.Printf("   %d. %s\n", i+1, file)
			}
		}

		// Test search
		query := "logica"
		fmt.Printf("\n🔍 Searching for: %s\n", query)

		var matches []string
		for _, file := range result.Files {
			if strings.Contains(strings.ToLower(file), strings.ToLower(query)) {
				matches = append(matches, file)
			}
		}

		fmt.Printf("📊 Found %d matches:\n", len(matches))
		for i, match := range matches {
			fmt.Printf("   %d. %s\n", i+1, match)
		}

		// Test other searches
		queries := []string{"matematica", "test", "md", "API"}
		for _, q := range queries {
			var m []string
			for _, file := range result.Files {
				if strings.Contains(strings.ToLower(file), strings.ToLower(q)) {
					m = append(m, file)
				}
			}
			fmt.Printf("🔍 '%s': %d matches\n", q, len(m))
		}
	}

	fmt.Println("\n🎉 Debug completed!")
}
