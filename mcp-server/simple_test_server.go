package main

import (
	"fmt"
	"log"
	"net/http"
	"time"
)

func main() {
	fmt.Println("🚀 Starting Simple Test Server")
	fmt.Println("==============================")

	// Simple health endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"status": "healthy", "message": "Simple test server running", "timestamp": "%s"}`, time.Now().Format(time.RFC3339))
	})

	// Simple tools endpoint
	http.HandleFunc("/tools/list", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `[
			{
				"name": "list_files_in_vault",
				"description": "List all files in the Obsidian vault",
				"parameters": {"type": "object", "properties": {}}
			},
			{
				"name": "read_note", 
				"description": "Read contents of a specific note",
				"parameters": {"type": "object", "properties": {"filename": {"type": "string"}}}
			},
			{
				"name": "search_vault",
				"description": "Search the Obsidian vault for notes matching a query", 
				"parameters": {"type": "object", "properties": {"query": {"type": "string"}}}
			}
		]`)
	})

	// Simple tool execution endpoint
	http.HandleFunc("/tools/execute", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")

		// Mock response for testing
		fmt.Fprintf(w, `{
			"success": true,
			"data": [
				{
					"name": "Real-Vault-File.md",
					"path": "Real-Vault-File.md", 
					"type": "file"
				},
				{
					"name": "Another-Real-File.md",
					"path": "Another-Real-File.md",
					"type": "file"
				}
			],
			"message": "Found 2 files in real vault"
		}`)
	})

	fmt.Println("✅ Server starting on port 3010")
	fmt.Println("📡 Endpoints available:")
	fmt.Println("   GET  /health")
	fmt.Println("   GET  /tools/list")
	fmt.Println("   POST /tools/execute")
	fmt.Println("")
	fmt.Println("🧪 Test with: curl http://localhost:3010/health")
	fmt.Println("")

	log.Fatal(http.ListenAndServe(":3010", nil))
}

