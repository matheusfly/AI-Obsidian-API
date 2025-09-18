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
	fmt.Println("🔍 AUTO DEBUGGING AND FIXING")
	fmt.Println("============================")

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

	// Show raw response (first 1000 chars)
	fmt.Printf("📥 Raw response (first 1000 chars):\n%s\n", string(body)[:1000])

	// Try multiple JSON structures
	fmt.Println("\n🔍 Testing different JSON structures:")

	// Structure 1: {"files": [...]}
	var result1 struct {
		Files []string `json:"files"`
	}
	if err := json.Unmarshal(body, &result1); err == nil {
		fmt.Printf("✅ Structure 1 (files): %d files\n", len(result1.Files))
		if len(result1.Files) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range result1.Files {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 1 failed: %v\n", err)
	}

	// Structure 2: {"data": [...]}
	var result2 struct {
		Data []string `json:"data"`
	}
	if err := json.Unmarshal(body, &result2); err == nil {
		fmt.Printf("✅ Structure 2 (data): %d files\n", len(result2.Data))
		if len(result2.Data) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range result2.Data {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 2 failed: %v\n", err)
	}

	// Structure 3: {"items": [...]}
	var result3 struct {
		Items []string `json:"items"`
	}
	if err := json.Unmarshal(body, &result3); err == nil {
		fmt.Printf("✅ Structure 3 (items): %d files\n", len(result3.Items))
		if len(result3.Items) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range result3.Items {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 3 failed: %v\n", err)
	}

	// Structure 4: {"results": [...]}
	var result4 struct {
		Results []string `json:"results"`
	}
	if err := json.Unmarshal(body, &result4); err == nil {
		fmt.Printf("✅ Structure 4 (results): %d files\n", len(result4.Results))
		if len(result4.Results) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range result4.Results {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 4 failed: %v\n", err)
	}

	// Try to parse as a simple array
	var simpleArray []string
	if err := json.Unmarshal(body, &simpleArray); err == nil {
		fmt.Printf("✅ Structure 5 (simple array): %d files\n", len(simpleArray))
		if len(simpleArray) > 0 {
			fmt.Println("📄 First 5 files:")
			for i, file := range simpleArray {
				if i < 5 {
					fmt.Printf("   %d. %s\n", i+1, file)
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 5 failed: %v\n", err)
	}

	// Try to parse as a map
	var mapResult map[string]interface{}
	if err := json.Unmarshal(body, &mapResult); err == nil {
		fmt.Printf("✅ Structure 6 (map): %d keys\n", len(mapResult))
		fmt.Println("📄 Map keys:")
		for key, value := range mapResult {
			fmt.Printf("   %s: %T\n", key, value)
			if arr, ok := value.([]interface{}); ok {
				fmt.Printf("     -> Array with %d items\n", len(arr))
				if len(arr) > 0 {
					fmt.Printf("     -> First item: %v\n", arr[0])
				}
			}
		}
	} else {
		fmt.Printf("❌ Structure 6 failed: %v\n", err)
	}

	// Test searches with the working structure
	fmt.Println("\n🔍 Testing searches with working structure:")

	// Find which structure has files
	var workingFiles []string
	var workingStructure string

	if len(result1.Files) > 0 {
		workingFiles = result1.Files
		workingStructure = "files"
	} else if len(result2.Data) > 0 {
		workingFiles = result2.Data
		workingStructure = "data"
	} else if len(result3.Items) > 0 {
		workingFiles = result3.Items
		workingStructure = "items"
	} else if len(result4.Results) > 0 {
		workingFiles = result4.Results
		workingStructure = "results"
	} else if len(simpleArray) > 0 {
		workingFiles = simpleArray
		workingStructure = "simple array"
	}

	if len(workingFiles) > 0 {
		fmt.Printf("✅ Working structure: %s with %d files\n", workingStructure, len(workingFiles))

		// Test searches
		queries := []string{"logica", "matematica", "performance", "test", "md", "API", "AGENTS"}
		for _, query := range queries {
			var matches []string
			for _, file := range workingFiles {
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
	} else {
		fmt.Println("❌ No working structure found!")
		fmt.Printf("Raw response: %s\n", string(body))
	}

	fmt.Println("\n🎉 Auto debug completed!")
}
