package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

func main() {
	fmt.Println("🔍 COMPREHENSIVE DEBUG TEST")
	fmt.Println("============================")
	
	// Configuration
	apiBaseURL := "https://127.0.0.1:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	
	// Create HTTP client with SSL skipping
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{
		Transport: tr,
		Timeout:   30 * time.Second,
	}
	
	fmt.Printf("🌐 Testing API: %s\n", apiBaseURL)
	fmt.Printf("🔑 Using token: %s...\n", apiToken[:20])
	fmt.Println()
	
	// Test 1: Basic API connectivity
	fmt.Println("Test 1: Basic API Connectivity")
	fmt.Println("-------------------------------")
	
	req, err := http.NewRequest("GET", apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+apiToken)
	
	fmt.Printf("📤 Sending request to: %s\n", req.URL.String())
	fmt.Printf("📤 Headers: %+v\n", req.Header)
	
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("❌ Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()
	
	fmt.Printf("📥 Response Status: %d\n", resp.StatusCode)
	fmt.Printf("📥 Response Headers: %+v\n", resp.Header)
	
	// Read response body
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read response: %v\n", err)
		return
	}
	
	fmt.Printf("📥 Response Body Length: %d bytes\n", len(body))
	fmt.Printf("📥 Response Body: %s\n", string(body))
	
	// Test 2: Parse JSON response
	fmt.Println("\nTest 2: JSON Parsing")
	fmt.Println("--------------------")
	
	var result struct {
		Data []struct {
			Name string `json:"name"`
			Path string `json:"path"`
		} `json:"data"`
		Success bool   `json:"success"`
		Message string `json:"message"`
		Error   string `json:"error"`
	}
	
	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("❌ JSON parsing failed: %v\n", err)
		fmt.Printf("Raw response: %s\n", string(body))
		return
	}
	
	fmt.Printf("✅ JSON parsing successful\n")
	fmt.Printf("📊 Success: %t\n", result.Success)
	fmt.Printf("📊 Message: %s\n", result.Message)
	fmt.Printf("📊 Error: %s\n", result.Error)
	fmt.Printf("📊 Files found: %d\n", len(result.Data))
	
	if len(result.Data) > 0 {
		fmt.Println("📄 First few files:")
		for i, file := range result.Data {
			if i < 5 {
				fmt.Printf("   %d. %s (%s)\n", i+1, file.Name, file.Path)
			}
		}
	}
	
	// Test 3: Try different endpoints
	fmt.Println("\nTest 3: Different Endpoints")
	fmt.Println("---------------------------")
	
	endpoints := []string{
		"/",
		"/vault/",
		"/files/",
		"/notes/",
		"/search/",
	}
	
	for _, endpoint := range endpoints {
		fmt.Printf("\n🔍 Testing endpoint: %s\n", endpoint)
		
		req2, err := http.NewRequest("GET", apiBaseURL+endpoint, nil)
		if err != nil {
			fmt.Printf("❌ Failed to create request: %v\n", err)
			continue
		}
		req2.Header.Set("Authorization", "Bearer "+apiToken)
		
		resp2, err := client.Do(req2)
		if err != nil {
			fmt.Printf("❌ Request failed: %v\n", err)
			continue
		}
		defer resp2.Body.Close()
		
		body2, err := ioutil.ReadAll(resp2.Body)
		if err != nil {
			fmt.Printf("❌ Failed to read response: %v\n", err)
			continue
		}
		
		fmt.Printf("📥 Status: %d, Length: %d bytes\n", resp2.StatusCode, len(body2))
		if len(body2) < 500 {
			fmt.Printf("📥 Content: %s\n", string(body2))
		} else {
			fmt.Printf("📥 Content (first 500 chars): %s...\n", string(body2)[:500])
		}
	}
	
	// Test 4: Try without authentication
	fmt.Println("\nTest 4: Without Authentication")
	fmt.Println("------------------------------")
	
	req3, err := http.NewRequest("GET", apiBaseURL+"/vault/", nil)
	if err != nil {
		fmt.Printf("❌ Failed to create request: %v\n", err)
		return
	}
	
	resp3, err := client.Do(req3)
	if err != nil {
		fmt.Printf("❌ Request failed: %v\n", err)
		return
	}
	defer resp3.Body.Close()
	
	body3, err := ioutil.ReadAll(resp3.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read response: %v\n", err)
		return
	}
	
	fmt.Printf("📥 Status: %d, Length: %d bytes\n", resp3.StatusCode, len(body3))
	fmt.Printf("📥 Content: %s\n", string(body3))
	
	fmt.Println("\n🎉 Debug test completed!")
}
