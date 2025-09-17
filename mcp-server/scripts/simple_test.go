package main

import (
	"fmt"
	"io"
	"net/http"
	"time"
)

func main() {
	fmt.Println("🧪 Simple MCP Server Test")
	fmt.Println("========================")

	client := &http.Client{Timeout: 10 * time.Second}

	// Test health endpoint
	fmt.Println("Testing health endpoint...")
	resp, err := client.Get("http://localhost:3010/health")
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read response: %v\n", err)
		return
	}

	fmt.Printf("✅ Health response: %s\n", string(body))

	// Test tools list
	fmt.Println("\nTesting tools list...")
	resp, err = client.Get("http://localhost:3010/tools/list")
	if err != nil {
		fmt.Printf("❌ Tools list failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, err = io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Failed to read tools response: %v\n", err)
		return
	}

	fmt.Printf("✅ Tools response: %s\n", string(body))

	fmt.Println("\n🎉 Simple test completed!")
}
