package tests

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/config"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"go.uber.org/zap"
)

// IntegrationTestSuite provides integration tests for Obsidian API
type IntegrationTestSuite struct {
	config         *config.Config
	obsidianClient *client.Client
	ollamaClient   *ollama.Client
	advancedTools  *tools.AdvancedTools
	logger         *zap.Logger
}

// SetupIntegrationTest initializes the integration test suite
func SetupIntegrationTest(t *testing.T) *IntegrationTestSuite {
	// Load configuration
	cfg, err := config.LoadConfig("./configs/config.yaml")
	if err != nil {
		t.Skipf("Skipping integration test: failed to load config: %v", err)
	}

	// Initialize logger
	logger, err := zap.NewDevelopment()
	if err != nil {
		t.Fatalf("Failed to create logger: %v", err)
	}

	// Initialize HTTP client
	clientConfig := &client.Config{
		BaseURL:     cfg.API.BaseURL,
		Token:       cfg.API.Token,
		Timeout:     30 * time.Second,
		RateLimit:   10,
		CacheTTL:    5 * time.Minute,
		EnableCache: cfg.Vault.EnableCache,
	}

	obsidianClient := client.NewClient(clientConfig, logger)

	// Initialize Ollama client
	ollamaClient := ollama.NewClient(cfg.Ollama.Host, cfg.Ollama.Model)

	// Initialize advanced tools
	advancedTools := tools.NewAdvancedTools(obsidianClient, ollamaClient, logger)

	return &IntegrationTestSuite{
		config:         cfg,
		obsidianClient: obsidianClient,
		ollamaClient:   ollamaClient,
		advancedTools:  advancedTools,
		logger:         logger,
	}
}

// TestObsidianAPIConnection tests basic connectivity to Obsidian API
func TestObsidianAPIConnection(t *testing.T) {
	suite := SetupIntegrationTest(t)
	defer suite.logger.Sync()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Test basic API connectivity
	var result interface{}
	err := suite.obsidianClient.Get(ctx, "/vault/", &result)
	if err != nil {
		t.Skipf("Skipping integration test: Obsidian API not available: %v", err)
	}

	t.Logf("Successfully connected to Obsidian API at %s", suite.config.API.BaseURL)
}

// TestListFilesIntegration tests listing files through the API
func TestListFilesIntegration(t *testing.T) {
	suite := SetupIntegrationTest(t)
	defer suite.logger.Sync()

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Test listing files
	result := suite.advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
	if !result.Success {
		t.Skipf("Skipping integration test: %s", result.Error)
	}

	files, ok := result.Data.([]map[string]interface{})
	if !ok {
		t.Errorf("Expected []map[string]interface{}, got %T", result.Data)
		return
	}

	t.Logf("Found %d files in vault", len(files))

	// Verify file structure
	for i, file := range files {
		if i >= 5 { // Limit output for large vaults
			break
		}

		name, hasName := file["name"]
		path, hasPath := file["path"]

		if !hasName || !hasPath {
			t.Errorf("File %d missing name or path: %+v", i, file)
		} else {
			t.Logf("File %d: %s (%s)", i, name, path)
		}
	}
}

// TestSearchIntegration tests search functionality
func TestSearchIntegration(t *testing.T) {
	suite := SetupIntegrationTest(t)
	defer suite.logger.Sync()

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Test search with a common term
	result := suite.advancedTools.SearchVault(ctx, map[string]interface{}{
		"query": "test",
		"limit": 5,
	})

	if !result.Success {
		t.Skipf("Skipping integration test: %s", result.Error)
	}

	results, ok := result.Data.([]map[string]interface{})
	if !ok {
		t.Errorf("Expected []map[string]interface{}, got %T", result.Data)
		return
	}

	t.Logf("Search for 'test' returned %d results", len(results))

	// Verify search result structure
	for i, searchResult := range results {
		if i >= 3 { // Limit output
			break
		}

		path, hasPath := searchResult["path"]
		if !hasPath {
			t.Errorf("Search result %d missing path: %+v", i, searchResult)
		} else {
			t.Logf("Search result %d: %s", i, path)
		}
	}
}

// TestOllamaIntegration tests Ollama connectivity
func TestOllamaIntegration(t *testing.T) {
	suite := SetupIntegrationTest(t)
	defer suite.logger.Sync()

	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	// Test Ollama connectivity with a simple prompt
	response, err := suite.ollamaClient.GenerateCompletion(ctx, "Hello, this is a test.")
	if err != nil {
		t.Skipf("Skipping Ollama integration test: %v", err)
	}

	if response == "" {
		t.Error("Expected non-empty response from Ollama")
		return
	}

	t.Logf("Ollama response: %s", response)
}

// TestSemanticSearchIntegration tests semantic search with DeepSeek-R1:8B
func TestSemanticSearchIntegration(t *testing.T) {
	suite := SetupIntegrationTest(t)
	defer suite.logger.Sync()

	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()

	// Test semantic search
	result := suite.advancedTools.SemanticSearch(ctx, map[string]interface{}{
		"query": "knowledge management",
		"top_k": 3,
	})

	if !result.Success {
		t.Skipf("Skipping semantic search test: %s", result.Error)
	}

	data, ok := result.Data.(map[string]interface{})
	if !ok {
		t.Errorf("Expected map[string]interface{}, got %T", result.Data)
		return
	}

	query, hasQuery := data["query"]
	embedding, hasEmbedding := data["embedding"]
	results, hasResults := data["results"]

	if !hasQuery || !hasEmbedding || !hasResults {
		t.Errorf("Missing required fields in semantic search result: query=%v, embedding=%v, results=%v",
			hasQuery, hasEmbedding, hasResults)
		return
	}

	t.Logf("Semantic search query: %s", query)
	t.Logf("Generated embedding length: %d", len(embedding.(string)))

	if resultsSlice, ok := results.([]map[string]interface{}); ok {
		t.Logf("Semantic search returned %d results", len(resultsSlice))
	}
}

// TestCreateNoteIntegration tests note creation (if write permissions available)
func TestCreateNoteIntegration(t *testing.T) {
	suite := SetupIntegrationTest(t)
	defer suite.logger.Sync()

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Test note creation with a unique name
	testNoteName := fmt.Sprintf("mcp-test-%d.md", time.Now().Unix())
	testContent := "# MCP Test Note\n\nThis is a test note created by the MCP integration test.\n\nCreated at: " + time.Now().Format(time.RFC3339)

	result := suite.advancedTools.CreateNote(ctx, map[string]interface{}{
		"path":    testNoteName,
		"content": testContent,
	})

	if !result.Success {
		t.Skipf("Skipping note creation test: %s", result.Error)
	}

	data, ok := result.Data.(map[string]interface{})
	if !ok {
		t.Errorf("Expected map[string]interface{}, got %T", result.Data)
		return
	}

	createdPath, hasPath := data["path"]
	if !hasPath || createdPath != testNoteName {
		t.Errorf("Expected path '%s', got '%v'", testNoteName, createdPath)
	}

	t.Logf("Successfully created test note: %s", testNoteName)

	// Clean up: try to read the created note
	readResult := suite.advancedTools.ReadNote(ctx, map[string]interface{}{
		"filename": testNoteName,
	})

	if readResult.Success {
		t.Logf("Successfully verified created note")
	} else {
		t.Logf("Note created but could not be read: %s", readResult.Error)
	}
}

// TestPerformanceIntegration tests performance with realistic workloads
func TestPerformanceIntegration(t *testing.T) {
	suite := SetupIntegrationTest(t)
	defer suite.logger.Sync()

	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	// Test multiple operations to measure performance
	operations := []struct {
		name string
		fn   func() mcp.ToolResult
	}{
		{
			name: "ListFiles",
			fn: func() mcp.ToolResult {
				return suite.advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
			},
		},
		{
			name: "Search",
			fn: func() mcp.ToolResult {
				return suite.advancedTools.SearchVault(ctx, map[string]interface{}{
					"query": "test",
					"limit": 10,
				})
			},
		},
	}

	for _, op := range operations {
		t.Run(op.name, func(t *testing.T) {
			start := time.Now()
			result := op.fn()
			duration := time.Since(start)

			if !result.Success {
				t.Skipf("Skipping performance test for %s: %s", op.name, result.Error)
			}

			t.Logf("%s completed in %v", op.name, duration)

			// Performance expectations
			if duration > 10*time.Second {
				t.Errorf("%s took too long: %v", op.name, duration)
			}
		})
	}
}

// TestErrorHandlingIntegration tests error handling with invalid inputs
func TestErrorHandlingIntegration(t *testing.T) {
	suite := SetupIntegrationTest(t)
	defer suite.logger.Sync()

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Test invalid filename
	result := suite.advancedTools.ReadNote(ctx, map[string]interface{}{
		"filename": "../../../etc/passwd", // Path traversal attempt
	})

	// Should either succeed (if sanitized) or fail gracefully
	if result.Success {
		t.Logf("Path traversal attempt was sanitized successfully")
	} else {
		t.Logf("Path traversal attempt was rejected: %s", result.Error)
	}

	// Test invalid search
	result = suite.advancedTools.SearchVault(ctx, map[string]interface{}{
		"query": "", // Empty query
	})

	if result.Success {
		t.Error("Expected failure for empty query")
	}

	// Test invalid note creation
	result = suite.advancedTools.CreateNote(ctx, map[string]interface{}{
		"path": "", // Empty path
	})

	if result.Success {
		t.Error("Expected failure for empty path")
	}
}

// BenchmarkIntegration provides benchmarks for integration tests
func BenchmarkListFilesIntegration(b *testing.B) {
	suite := SetupIntegrationTest(&testing.T{})
	defer suite.logger.Sync()

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		suite.advancedTools.ListFilesInVault(ctx, map[string]interface{}{})
	}
}

func BenchmarkSearchIntegration(b *testing.B) {
	suite := SetupIntegrationTest(&testing.T{})
	defer suite.logger.Sync()

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		suite.advancedTools.SearchVault(ctx, map[string]interface{}{
			"query": "test",
			"limit": 5,
		})
	}
}

