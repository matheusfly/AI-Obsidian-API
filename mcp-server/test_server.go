package main

import (
	"fmt"
	"net/http"
	"time"
)

func main() {
	fmt.Println("🚀 Starting MCP Test Server...")

	// Health endpoint
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"status":"healthy","timestamp":"%s","version":"1.0.0"}`, time.Now().Format(time.RFC3339))
		fmt.Println("✅ Health check requested")
	})

	// Tools list endpoint
	http.HandleFunc("/tools/list", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `[{"name":"search_notes","description":"Search notes in vault"},{"name":"get_note","description":"Get a specific note"},{"name":"list_files","description":"List files in vault"}]`)
		fmt.Println("✅ Tools list requested")
	})

	// MCP tools endpoint
	http.HandleFunc("/mcp/tools", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `[{"name":"search_notes","description":"Search notes in vault"},{"name":"get_note","description":"Get a specific note"},{"name":"list_files","description":"List files in vault"}]`)
		fmt.Println("✅ MCP tools requested")
	})

	// Tool execution endpoint
	http.HandleFunc("/tools/execute", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.Method == "POST" {
			fmt.Fprintf(w, `{"success":true,"message":"Tool executed successfully","data":{"result":"Test execution completed"}}`)
			fmt.Println("✅ Tool execution requested")
		} else {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		}
	})

	fmt.Println("🌐 Server starting on :3010")
	fmt.Println("📋 Available endpoints:")
	fmt.Println("  - GET  /health")
	fmt.Println("  - GET  /tools/list")
	fmt.Println("  - GET  /mcp/tools")
	fmt.Println("  - POST /tools/execute")
	fmt.Println("")
	fmt.Println("🚀 Server is running! Press Ctrl+C to stop")

	if err := http.ListenAndServe(":3010", nil); err != nil {
		fmt.Printf("❌ Server failed: %v\n", err)
	}
}
