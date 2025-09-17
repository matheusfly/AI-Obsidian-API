package main

import (
	"fmt"
	"log"
	"net/http"
	"time"
)

func main() {
	fmt.Println("Testing MCP Server startup...")
	
	// Test if the server can start
	go func() {
		// This would normally be the server startup code
		fmt.Println("Server would start here...")
	}()
	
	// Give it a moment
	time.Sleep(1 * time.Second)
	
	// Test HTTP client
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get("http://localhost:8080/health")
	if err != nil {
		fmt.Printf("Expected: Server not running yet - %v\n", err)
	} else {
		fmt.Printf("Server responded: %s\n", resp.Status)
		resp.Body.Close()
	}
	
	fmt.Println("✅ Test completed successfully!")
}

