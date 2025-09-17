package tools

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"github.com/datamaster/mcp-server/pkg/obsidian"
)

// ToolHandler defines the interface for a tool's execution logic
type ToolHandler func(ctx context.Context, params map[string]interface{}) mcp.ToolResult

// Registry manages the available MCP tools
type Registry struct {
	obsidianClient *obsidian.Client
	httpClient     client.HTTPClient
	ollamaClient   *ollama.Client
	tools          map[string]mcp.ToolDefinition
	handlers       map[string]ToolHandler
	baseURL        string
	token          string
}

// NewRegistry creates a new tool registry
func NewRegistry(oc *obsidian.Client, olc *ollama.Client) *Registry {
	baseURL := "https://localhost:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"

	// Create HTTP client for advanced tools
	httpClientCfg := &client.Config{
		BaseURL:     baseURL,
		Token:       token,
		Timeout:     10 * time.Second,
		EnableCache: true,
		CacheTTL:    5 * time.Minute,
	}
	httpClient := client.NewClient(httpClientCfg, nil)

	return &Registry{
		obsidianClient: oc,
		httpClient:     httpClient,
		ollamaClient:   olc,
		tools:          make(map[string]mcp.ToolDefinition),
		handlers:       make(map[string]ToolHandler),
		baseURL:        baseURL,
		token:          token,
	}
}

// NewRegistryWithConfig creates a new tool registry with configuration
func NewRegistryWithConfig(oc *obsidian.Client, olc *ollama.Client, baseURL, token string) *Registry {
	// Create HTTP client for advanced tools
	httpClientCfg := &client.Config{
		BaseURL:     baseURL,
		Token:       token,
		Timeout:     10 * time.Second,
		EnableCache: true,
		CacheTTL:    5 * time.Minute,
	}
	httpClient := client.NewClient(httpClientCfg, nil)

	return &Registry{
		obsidianClient: oc,
		httpClient:     httpClient,
		ollamaClient:   olc,
		tools:          make(map[string]mcp.ToolDefinition),
		handlers:       make(map[string]ToolHandler),
		baseURL:        baseURL,
		token:          token,
	}
}

// RegisterTool adds a new tool to the registry
func (r *Registry) RegisterTool(def mcp.ToolDefinition, handler ToolHandler) {
	r.tools[def.Name] = def
	r.handlers[def.Name] = handler
	log.Printf("Registered tool: %s", def.Name)
}

// RegisterDefaultTools registers a set of predefined tools
func (r *Registry) RegisterDefaultTools() {
	// Register advanced tools that use real Obsidian API
	advancedTools := NewAdvancedToolsWithConfig(r.httpClient, r.ollamaClient, nil, r.baseURL, r.token)

	// Register all advanced tool definitions
	for _, toolDef := range advancedTools.GetToolDefinitions() {
		var handler ToolHandler
		switch toolDef.Name {
		case "list_files_in_vault":
			handler = advancedTools.ListFilesInVault
		case "read_note":
			handler = advancedTools.ReadNote
		case "search_vault":
			handler = advancedTools.SearchVault
		case "semantic_search":
			handler = advancedTools.SemanticSearch
		case "create_note":
			handler = advancedTools.CreateNote
		case "bulk_tag":
			handler = advancedTools.BulkTag
		case "analyze_links":
			handler = advancedTools.AnalyzeLinks
		default:
			continue
		}
		r.RegisterTool(toolDef, handler)
	}
}

// ListTools returns all registered tool definitions
func (r *Registry) ListTools() []mcp.ToolDefinition {
	defs := make([]mcp.ToolDefinition, 0, len(r.tools))
	for _, def := range r.tools {
		defs = append(defs, def)
	}
	return defs
}

// ExecuteTool executes a registered tool
func (r *Registry) ExecuteTool(ctx context.Context, call mcp.ToolCall) mcp.ToolResult {
	handler, ok := r.handlers[call.ToolName]
	if !ok {
		return mcp.ToolResult{Success: false, Error: fmt.Sprintf("tool '%s' not found", call.ToolName)}
	}
	return handler(ctx, call.Parameters)
}

// handleSearchNotes implements the logic for the "search_notes" tool
func (r *Registry) handleSearchNotes(ctx context.Context, params map[string]interface{}) mcp.ToolResult {
	query, ok := params["query"].(string)
	if !ok || query == "" {
		return mcp.ToolResult{Success: false, Error: "missing or invalid 'query' parameter"}
	}
	limit := 10
	if l, ok := params["limit"].(float64); ok { // JSON numbers are float64
		limit = int(l)
	}

	results, err := r.obsidianClient.SearchVault(ctx, query, limit)
	if err != nil {
		return mcp.ToolResult{Success: false, Error: fmt.Sprintf("Obsidian search failed: %v", err)}
	}

	return mcp.ToolResult{Success: true, Data: results}
}

// handleGetNoteContent implements the logic for the "get_note_content" tool
func (r *Registry) handleGetNoteContent(ctx context.Context, params map[string]interface{}) mcp.ToolResult {
	path, ok := params["path"].(string)
	if !ok || path == "" {
		return mcp.ToolResult{Success: false, Error: "missing or invalid 'path' parameter"}
	}

	content, err := r.obsidianClient.GetFileContent(ctx, path)
	if err != nil {
		return mcp.ToolResult{Success: false, Error: fmt.Sprintf("failed to get note content: %v", err)}
	}

	return mcp.ToolResult{Success: true, Data: map[string]string{"path": path, "content": content}}
}
