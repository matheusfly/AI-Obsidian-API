package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
	"time"
)

func main() {
	// Create debug file
	file, err := os.Create("debug_output.txt")
	if err != nil {
		fmt.Printf("Error creating file: %v\n", err)
		return
	}
	defer file.Close()
	
	fmt.Fprintln(file, "🔍 DEBUGGING SEARCH PROBLEM")
	fmt.Fprintln(file, "===========================")
	
	apiBaseURL := "https://127.0.0.1:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
	}
	
	fmt.Fprintf(file, "🌐 Testing API: %s\n", apiBaseURL)
	
	// Test API connection
	req, err := http.NewRequest("GET", apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Fprintf(file, "❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+apiToken)
	
	resp, err := client.Do(req)
	if err != nil {
		fmt.Fprintf(file, "❌ Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		fmt.Fprintf(file, "❌ API returned status: %d\n", resp.StatusCode)
		return
	}
	
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Fprintf(file, "❌ Failed to read response: %v\n", err)
		return
	}
	
	fmt.Fprintf(file, "✅ API Connection: SUCCESS\n")
	fmt.Fprintf(file, "📥 Response length: %d bytes\n", len(body))
	
	// Show raw response (first 1000 chars)
	fmt.Fprintf(file, "📥 Raw response (first 1000 chars):\n%s\n", string(body)[:1000])
	
	// Try parsing with the new structure
	var result struct {
		Files []string `json:"files"`
	}
	
	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Fprintf(file, "❌ JSON parsing failed: %v\n", err)
		return
	}
	
	fmt.Fprintf(file, "✅ JSON parsing: SUCCESS\n")
	fmt.Fprintf(file, "📄 Files found: %d\n", len(result.Files))
	
	if len(result.Files) > 0 {
		fmt.Fprintln(file, "📄 First 20 files:")
		for i, file := range result.Files {
			if i < 20 {
				fmt.Fprintf(file, "   %d. %s\n", i+1, file)
			}
		}
		
		// Test searches with detailed output
		queries := []string{"logica", "matematica", "performance", "test", "md", "API", "AGENTS"}
		for _, query := range queries {
			fmt.Fprintf(file, "\n🔍 Testing search for: '%s'\n", query)
			var matches []string
			for _, file := range result.Files {
				if strings.Contains(strings.ToLower(file), strings.ToLower(query)) {
					matches = append(matches, file)
					fmt.Fprintf(file, "   ✅ MATCH: %s\n", file)
				}
			}
			fmt.Fprintf(file, "📊 Total matches for '%s': %d\n", query, len(matches))
		}
		
	} else {
		fmt.Fprintln(file, "❌ No files found in response!")
		fmt.Fprintf(file, "Raw response: %s\n", string(body))
	}
	
	fmt.Fprintln(file, "\n🎉 Debug completed!")
	fmt.Println("Debug output written to debug_output.txt")
}
