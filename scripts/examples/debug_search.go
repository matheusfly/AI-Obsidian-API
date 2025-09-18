package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// DebugSearch tests the search functionality step by step
func main() {
	fmt.Println("🔍 DEBUGGING SEARCH FUNCTIONALITY")
	fmt.Println("==================================")
	
	// Test Obsidian API connection
	baseURL := "https://127.0.0.1:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	
	client := &http.Client{
		Timeout: 30 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}
	
	// Step 1: Test root directory listing
	fmt.Println("📁 Step 1: Testing root directory listing...")
	req, err := http.NewRequest("GET", baseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+token)
	
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Failed to connect: %v\n", err)
		return
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		fmt.Printf("❌ API request failed with status: %d\n", resp.StatusCode)
		return
	}
	
	var response struct {
		Files []string `json:"files"`
	}
	
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		fmt.Printf("❌ Failed to decode response: %v\n", err)
		return
	}
	
	fmt.Printf("✅ Found %d files in root directory\n", len(response.Files))
	for i, file := range response.Files {
		if i < 10 { // Show first 10 files
			fmt.Printf("  %d. %s\n", i+1, file)
		}
	}
	
	// Step 2: Test subdirectory listing
	fmt.Println("\n📁 Step 2: Testing subdirectory listing...")
	for _, file := range response.Files {
		if strings.HasSuffix(file, "/") {
			fmt.Printf("🔍 Testing directory: %s\n", file)
			
			req, err := http.NewRequest("GET", baseURL+"/vault/"+url.QueryEscape(file), nil)
			if err != nil {
				fmt.Printf("❌ Failed to create request: %v\n", err)
				continue
			}
			req.Header.Set("Authorization", "Bearer "+token)
			
			resp, err := client.Do(req)
			if err != nil {
				fmt.Printf("❌ Failed to list directory: %v\n", err)
				continue
			}
			defer resp.Body.Close()
			
			if resp.StatusCode != http.StatusOK {
				fmt.Printf("❌ Directory listing failed with status: %d\n", resp.StatusCode)
				continue
			}
			
			var dirResponse struct {
				Files []string `json:"files"`
			}
			
			if err := json.NewDecoder(resp.Body).Decode(&dirResponse); err != nil {
				fmt.Printf("❌ Failed to decode directory response: %v\n", err)
				continue
			}
			
			fmt.Printf("✅ Found %d files in %s\n", len(dirResponse.Files), file)
			for i, subFile := range dirResponse.Files {
				if i < 5 { // Show first 5 files
					fmt.Printf("    %d. %s\n", i+1, subFile)
				}
			}
			
			// Step 3: Test content reading
			fmt.Println("\n📖 Step 3: Testing content reading...")
			for _, subFile := range dirResponse.Files {
				if strings.HasSuffix(strings.ToLower(subFile), ".md") {
					fmt.Printf("🔍 Reading file: %s%s\n", file, subFile)
					
					fileReq, err := http.NewRequest("GET", baseURL+"/vault/"+url.QueryEscape(file+subFile), nil)
					if err != nil {
						fmt.Printf("❌ Failed to create file request: %v\n", err)
						continue
					}
					fileReq.Header.Set("Authorization", "Bearer "+token)
					
					fileResp, err := client.Do(fileReq)
					if err != nil {
						fmt.Printf("❌ Failed to read file: %v\n", err)
						continue
					}
					defer fileResp.Body.Close()
					
					if fileResp.StatusCode != http.StatusOK {
						fmt.Printf("❌ File read failed with status: %d\n", fileResp.StatusCode)
						continue
					}
					
					body, err := io.ReadAll(fileResp.Body)
					if err != nil {
						fmt.Printf("❌ Failed to read file body: %v\n", err)
						continue
					}
					
					content := string(body)
					fmt.Printf("✅ Read file %s (%d characters)\n", subFile, len(content))
					
					// Step 4: Test search in content
					fmt.Println("\n🔍 Step 4: Testing search in content...")
					searchTerms := []string{"logica", "computação", "programação", "matemática"}
					
					for _, term := range searchTerms {
						contentLower := strings.ToLower(content)
						if strings.Contains(contentLower, term) {
							fmt.Printf("✅ Found '%s' in %s%s\n", term, file, subFile)
							
							// Extract snippet
							index := strings.Index(contentLower, term)
							start := max(0, index-50)
							end := min(len(content), index+len(term)+50)
							snippet := content[start:end]
							if start > 0 {
								snippet = "..." + snippet
							}
							if end < len(content) {
								snippet = snippet + "..."
							}
							fmt.Printf("   Snippet: %s\n", snippet)
						} else {
							fmt.Printf("❌ '%s' not found in %s%s\n", term, file, subFile)
						}
					}
					
					break // Test only first file for now
				}
			}
			break // Test only first directory for now
		}
	}
	
	fmt.Println("\n🎯 DEBUG COMPLETE!")
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// max returns the maximum of two integers
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
