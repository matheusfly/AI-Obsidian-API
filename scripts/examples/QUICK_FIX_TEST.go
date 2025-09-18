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
	fmt.Println("🔍 QUICK FIX TEST")
	fmt.Println("=================")
	
	apiBaseURL := "https://127.0.0.1:27124"
	apiToken := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
	}
	
	// Test list files
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
	
	var result struct {
		Files []string `json:"files"`
	}
	
	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("❌ JSON Error: %v\n", err)
		return
	}
	
	fmt.Printf("✅ Found %d files\n", len(result.Files))
	
	// Test search
	query := "logica"
	var matches []string
	for _, file := range result.Files {
		if strings.Contains(strings.ToLower(file), strings.ToLower(query)) {
			matches = append(matches, file)
		}
	}
	
	fmt.Printf("🔍 Search for '%s': %d matches\n", query, len(matches))
	for i, match := range matches {
		if i < 5 {
			fmt.Printf("   %d. %s\n", i+1, match)
		}
	}
	
	fmt.Println("🎉 Fix test completed!")
}
