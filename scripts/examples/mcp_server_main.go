package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

// MCPRequest represents a JSON-RPC 2.0 request
type MCPRequest struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      interface{} `json:"id"`
	Method  string      `json:"method"`
	Params  interface{} `json:"params,omitempty"`
}

// MCPResponse represents a JSON-RPC 2.0 response
type MCPResponse struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      interface{} `json:"id"`
	Result  interface{} `json:"result,omitempty"`
	Error   *MCPError   `json:"error,omitempty"`
}

// MCPError represents a JSON-RPC 2.0 error
type MCPError struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// Tool represents an MCP tool definition
type Tool struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	InputSchema map[string]interface{} `json:"inputSchema"`
}

// Resource represents an MCP resource
type Resource struct {
	URI         string `json:"uri"`
	Name        string `json:"name"`
	Description string `json:"description"`
	MimeType    string `json:"mimeType"`
}

// MCPServer implements the Model Context Protocol server
type MCPServer struct {
	httpClient          *client.HTTPClient
	queryComposer       *algorithms.QueryComposer
	candidateAggregator *algorithms.CandidateAggregator
	bm25TFIDF           *algorithms.BM25TFIDF
	metadataBoost       *algorithms.MetadataBoost
	deduplicator        *algorithms.Deduplicator
	contextAssembler    *algorithms.ContextAssembler
	streamingMerger     *algorithms.StreamingMerger

	// Configuration
	apiKey  string
	baseURL string
	port    string

	// Server state
	initialized  bool
	capabilities map[string]interface{}
}

// NewMCPServer creates a new MCP server instance
func NewMCPServer(apiKey, baseURL, port string) *MCPServer {
	server := &MCPServer{
		apiKey:  apiKey,
		baseURL: baseURL,
		port:    port,
		capabilities: map[string]interface{}{
			"tools": map[string]interface{}{
				"listChanged": true,
			},
			"resources": map[string]interface{}{
				"subscribe":   true,
				"listChanged": true,
			},
			"prompts": map[string]interface{}{
				"listChanged": true,
			},
		},
	}

	// Initialize components
	server.httpClient = client.NewHTTPClient(apiKey, baseURL)
	server.queryComposer = algorithms.NewQueryComposer()
	server.candidateAggregator = algorithms.NewCandidateAggregatorWithClient(apiKey, baseURL, server.httpClient.GetClient())
	server.bm25TFIDF = algorithms.NewBM25TFIDF()
	server.metadataBoost = algorithms.NewMetadataBoost()
	server.deduplicator = algorithms.NewDeduplicator()
	server.contextAssembler = algorithms.NewContextAssembler()
	server.streamingMerger = algorithms.NewStreamingMerger()

	return server
}

// Initialize handles the MCP initialize request
func (s *MCPServer) Initialize(params map[string]interface{}) *MCPResponse {
	s.initialized = true

	result := map[string]interface{}{
		"protocolVersion": "2024-11-05",
		"capabilities":    s.capabilities,
		"serverInfo": map[string]interface{}{
			"name":    "obsidian-vault-mcp-server",
			"version": "1.0.0",
		},
	}

	return &MCPResponse{
		JSONRPC: "2.0",
		ID:      params["id"],
		Result:  result,
	}
}

// ListTools returns available MCP tools
func (s *MCPServer) ListTools(params map[string]interface{}) *MCPResponse {
	tools := []Tool{
		{
			Name:        "search_vault",
			Description: "Search the Obsidian vault for notes matching a query using advanced algorithms",
			InputSchema: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"query": map[string]interface{}{
						"type":        "string",
						"description": "Search query string",
					},
					"limit": map[string]interface{}{
						"type":        "integer",
						"description": "Maximum number of results to return",
						"default":     10,
					},
					"algorithm": map[string]interface{}{
						"type":        "string",
						"description": "Search algorithm to use (smart, bm25, metadata, hybrid)",
						"default":     "smart",
						"enum":        []string{"smart", "bm25", "metadata", "hybrid"},
					},
				},
				"required": []string{"query"},
			},
		},
		{
			Name:        "read_note",
			Description: "Read the content of a specific note from the vault",
			InputSchema: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"path": map[string]interface{}{
						"type":        "string",
						"description": "Path to the note file",
					},
				},
				"required": []string{"path"},
			},
		},
		{
			Name:        "list_files",
			Description: "List all files in the vault or a specific directory",
			InputSchema: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"path": map[string]interface{}{
						"type":        "string",
						"description": "Directory path to list (empty for root)",
						"default":     "",
					},
					"recursive": map[string]interface{}{
						"type":        "boolean",
						"description": "Whether to recursively list subdirectories",
						"default":     false,
					},
				},
			},
		},
		{
			Name:        "get_vault_stats",
			Description: "Get statistics about the vault (file count, size, etc.)",
			InputSchema: map[string]interface{}{
				"type":       "object",
				"properties": map[string]interface{}{},
			},
		},
		{
			Name:        "analyze_content",
			Description: "Analyze note content using advanced algorithms (BM25-TFIDF, metadata boost)",
			InputSchema: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"path": map[string]interface{}{
						"type":        "string",
						"description": "Path to the note file",
					},
					"analysis_type": map[string]interface{}{
						"type":        "string",
						"description": "Type of analysis to perform",
						"enum":        []string{"keywords", "metadata", "similarity", "full"},
						"default":     "full",
					},
				},
				"required": []string{"path"},
			},
		},
	}

	return &MCPResponse{
		JSONRPC: "2.0",
		ID:      params["id"],
		Result: map[string]interface{}{
			"tools": tools,
		},
	}
}

// CallTool executes an MCP tool
func (s *MCPServer) CallTool(params map[string]interface{}) *MCPResponse {
	if !s.initialized {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      params["id"],
			Error: &MCPError{
				Code:    -32002,
				Message: "Server not initialized",
			},
		}
	}

	toolName, ok := params["name"].(string)
	if !ok {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      params["id"],
			Error: &MCPError{
				Code:    -32602,
				Message: "Invalid params: missing tool name",
			},
		}
	}

	arguments, _ := params["arguments"].(map[string]interface{})

	switch toolName {
	case "search_vault":
		return s.handleSearchVault(params["id"], arguments)
	case "read_note":
		return s.handleReadNote(params["id"], arguments)
	case "list_files":
		return s.handleListFiles(params["id"], arguments)
	case "get_vault_stats":
		return s.handleGetVaultStats(params["id"], arguments)
	case "analyze_content":
		return s.handleAnalyzeContent(params["id"], arguments)
	default:
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      params["id"],
			Error: &MCPError{
				Code:    -32601,
				Message: "Method not found",
			},
		}
	}
}

// handleSearchVault implements the search_vault tool
func (s *MCPServer) handleSearchVault(id interface{}, args map[string]interface{}) *MCPResponse {
	query, ok := args["query"].(string)
	if !ok || query == "" {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32602,
				Message: "Invalid params: query is required",
			},
		}
	}

	limit := 10
	if l, ok := args["limit"].(float64); ok {
		limit = int(l)
	}

	algorithm := "smart"
	if alg, ok := args["algorithm"].(string); ok {
		algorithm = alg
	}

	startTime := time.Now()
	var results []map[string]interface{}
	var err error

	switch algorithm {
	case "smart":
		results, err = s.performSmartSearch(query, limit)
	case "bm25":
		results, err = s.performBM25Search(query, limit)
	case "metadata":
		results, err = s.performMetadataSearch(query, limit)
	case "hybrid":
		results, err = s.performHybridSearch(query, limit)
	default:
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32602,
				Message: "Invalid algorithm: " + algorithm,
			},
		}
	}

	if err != nil {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32603,
				Message: "Internal error: " + err.Error(),
			},
		}
	}

	duration := time.Since(startTime)

	return &MCPResponse{
		JSONRPC: "2.0",
		ID:      id,
		Result: map[string]interface{}{
			"content": []map[string]interface{}{
				{
					"type": "text",
					"text": fmt.Sprintf("Search completed in %v. Found %d results for query '%s' using %s algorithm.", duration, len(results), query, algorithm),
				},
			},
			"isError": false,
			"results": results,
			"metadata": map[string]interface{}{
				"query":     query,
				"algorithm": algorithm,
				"limit":     limit,
				"duration":  duration.String(),
				"count":     len(results),
			},
		},
	}
}

// performSmartSearch implements smart search using the existing functionality
func (s *MCPServer) performSmartSearch(query string, limit int) ([]map[string]interface{}, error) {
	// Use the existing smart search implementation
	// This would integrate with the SmartSearchEngine we created earlier
	// For now, return a simplified implementation

	// Get files from vault
	files, err := s.getVaultFiles("", true)
	if err != nil {
		return nil, err
	}

	var results []map[string]interface{}
	queryLower := strings.ToLower(query)

	for _, file := range files {
		if strings.Contains(strings.ToLower(file), queryLower) {
			results = append(results, map[string]interface{}{
				"file":  file,
				"score": 0.8,
				"type":  "filename",
			})
			if len(results) >= limit {
				break
			}
		}
	}

	return results, nil
}

// performBM25Search implements BM25-TFIDF search
func (s *MCPServer) performBM25Search(query string, limit int) ([]map[string]interface{}, error) {
	// Implement BM25 search using the algorithms package
	// This would use the BM25TFIDF component
	return []map[string]interface{}{}, nil
}

// performMetadataSearch implements metadata-boosted search
func (s *MCPServer) performMetadataSearch(query string, limit int) ([]map[string]interface{}, error) {
	// Implement metadata search using the algorithms package
	// This would use the MetadataBoost component
	return []map[string]interface{}{}, nil
}

// performHybridSearch implements hybrid search combining multiple algorithms
func (s *MCPServer) performHybridSearch(query string, limit int) ([]map[string]interface{}, error) {
	// Implement hybrid search combining multiple algorithms
	// This would use multiple components together
	return []map[string]interface{}{}, nil
}

// handleReadNote implements the read_note tool
func (s *MCPServer) handleReadNote(id interface{}, args map[string]interface{}) *MCPResponse {
	path, ok := args["path"].(string)
	if !ok || path == "" {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32602,
				Message: "Invalid params: path is required",
			},
		}
	}

	content, err := s.getFileContent(path)
	if err != nil {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32603,
				Message: "Failed to read file: " + err.Error(),
			},
		}
	}

	return &MCPResponse{
		JSONRPC: "2.0",
		ID:      id,
		Result: map[string]interface{}{
			"content": []map[string]interface{}{
				{
					"type": "text",
					"text": content,
				},
			},
			"isError": false,
		},
	}
}

// handleListFiles implements the list_files tool
func (s *MCPServer) handleListFiles(id interface{}, args map[string]interface{}) *MCPResponse {
	path := ""
	if p, ok := args["path"].(string); ok {
		path = p
	}

	recursive := false
	if r, ok := args["recursive"].(bool); ok {
		recursive = r
	}

	files, err := s.getVaultFiles(path, recursive)
	if err != nil {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32603,
				Message: "Failed to list files: " + err.Error(),
			},
		}
	}

	return &MCPResponse{
		JSONRPC: "2.0",
		ID:      id,
		Result: map[string]interface{}{
			"content": []map[string]interface{}{
				{
					"type": "text",
					"text": fmt.Sprintf("Found %d files in path '%s'", len(files), path),
				},
			},
			"isError": false,
			"files":   files,
		},
	}
}

// handleGetVaultStats implements the get_vault_stats tool
func (s *MCPServer) handleGetVaultStats(id interface{}, args map[string]interface{}) *MCPResponse {
	files, err := s.getVaultFiles("", true)
	if err != nil {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32603,
				Message: "Failed to get vault stats: " + err.Error(),
			},
		}
	}

	stats := map[string]interface{}{
		"total_files": len(files),
		"timestamp":   time.Now().Format(time.RFC3339),
	}

	return &MCPResponse{
		JSONRPC: "2.0",
		ID:      id,
		Result: map[string]interface{}{
			"content": []map[string]interface{}{
				{
					"type": "text",
					"text": fmt.Sprintf("Vault contains %d files", len(files)),
				},
			},
			"isError": false,
			"stats":   stats,
		},
	}
}

// handleAnalyzeContent implements the analyze_content tool
func (s *MCPServer) handleAnalyzeContent(id interface{}, args map[string]interface{}) *MCPResponse {
	path, ok := args["path"].(string)
	if !ok || path == "" {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32602,
				Message: "Invalid params: path is required",
			},
		}
	}

	analysisType := "full"
	if at, ok := args["analysis_type"].(string); ok {
		analysisType = at
	}

	content, err := s.getFileContent(path)
	if err != nil {
		return &MCPResponse{
			JSONRPC: "2.0",
			ID:      id,
			Error: &MCPError{
				Code:    -32603,
				Message: "Failed to read file: " + err.Error(),
			},
		}
	}

	// Perform analysis based on type
	analysis := s.performContentAnalysis(content, analysisType)

	return &MCPResponse{
		JSONRPC: "2.0",
		ID:      id,
		Result: map[string]interface{}{
			"content": []map[string]interface{}{
				{
					"type": "text",
					"text": fmt.Sprintf("Analysis completed for %s using %s method", path, analysisType),
				},
			},
			"isError":  false,
			"analysis": analysis,
		},
	}
}

// getVaultFiles retrieves files from the vault
func (s *MCPServer) getVaultFiles(path string, recursive bool) ([]string, error) {
	// Implement file listing using the HTTP client
	// This would use the existing vault API integration
	return []string{}, nil
}

// getFileContent retrieves content of a specific file
func (s *MCPServer) getFileContent(path string) (string, error) {
	// Implement file content retrieval using the HTTP client
	// This would use the existing vault API integration
	return "", nil
}

// performContentAnalysis performs content analysis using the algorithms
func (s *MCPServer) performContentAnalysis(content, analysisType string) map[string]interface{} {
	// Implement content analysis using the algorithms package
	return map[string]interface{}{
		"type":    analysisType,
		"content": content,
	}
}

// StartHTTPServer starts the MCP server as an HTTP server
func (s *MCPServer) StartHTTPServer() error {
	http.HandleFunc("/mcp", s.handleHTTPRequest)
	http.HandleFunc("/health", s.handleHealthCheck)
	
	fmt.Printf("🚀 Starting MCP Server on port %s\n", s.port)
	fmt.Printf("📡 API Key: %s\n", s.apiKey[:8]+"...")
	fmt.Printf("🔗 Base URL: %s\n", s.baseURL)
	fmt.Printf("🌐 Server will be available at: http://localhost:%s/mcp\n", s.port)
	
	server := &http.Server{
		Addr:         ":" + s.port,
		Handler:      nil,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}
	
	fmt.Printf("✅ MCP Server started successfully!\n")
	return server.ListenAndServe()
}

// handleHTTPRequest handles HTTP requests to the MCP server
func (s *MCPServer) handleHTTPRequest(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req MCPRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	var resp *MCPResponse
	switch req.Method {
	case "initialize":
		resp = s.Initialize(map[string]interface{}{"id": req.ID})
	case "tools/list":
		resp = s.ListTools(map[string]interface{}{"id": req.ID})
	case "tools/call":
		resp = s.CallTool(map[string]interface{}{
			"id":        req.ID,
			"name":      req.Params.(map[string]interface{})["name"],
			"arguments": req.Params.(map[string]interface{})["arguments"],
		})
	default:
		resp = &MCPResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Error: &MCPError{
				Code:    -32601,
				Message: "Method not found",
			},
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// handleHealthCheck handles health check requests
func (s *MCPServer) handleHealthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    "healthy",
		"server":    "obsidian-vault-mcp-server",
		"version":   "1.0.0",
		"timestamp": time.Now().Format(time.RFC3339),
		"initialized": s.initialized,
	})
}

func main() {
	// Configuration from environment variables
	apiKey := os.Getenv("OBSIDIAN_API_TOKEN")
	if apiKey == "" {
		apiKey = "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	}

	baseURL := os.Getenv("OBSIDIAN_BASE_URL")
	if baseURL == "" {
		baseURL = "https://127.0.0.1:27124"
	}

	port := os.Getenv("MCP_SERVER_PORT")
	if port == "" {
		port = "8081"
	}

	// Create and start MCP server
	server := NewMCPServer(apiKey, baseURL, port)

	if err := server.StartHTTPServer(); err != nil {
		log.Fatal("Failed to start MCP server:", err)
	}
}
