package tests

import (
	"context"
	"fmt"
	"testing"

	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/internal/tools"
	"go.uber.org/zap"
)

// MockHTTPClient for testing
type MockHTTPClient struct {
	GetFunc    func(ctx context.Context, path string, result interface{}) error
	PostFunc   func(ctx context.Context, path string, body interface{}, result interface{}) error
	SearchFunc func(ctx context.Context, query string, limit int) ([]map[string]interface{}, error)
}

func (m *MockHTTPClient) Get(ctx context.Context, path string, result interface{}) error {
	if m.GetFunc != nil {
		return m.GetFunc(ctx, path, result)
	}
	return nil
}

func (m *MockHTTPClient) Post(ctx context.Context, path string, body interface{}, result interface{}) error {
	if m.PostFunc != nil {
		return m.PostFunc(ctx, path, body, result)
	}
	return nil
}

func (m *MockHTTPClient) Search(ctx context.Context, query string, limit int) ([]map[string]interface{}, error) {
	if m.SearchFunc != nil {
		return m.SearchFunc(ctx, query, limit)
	}
	return []map[string]interface{}{}, nil
}

func (m *MockHTTPClient) Put(ctx context.Context, path string, body interface{}, result interface{}) error {
	return nil
}

func (m *MockHTTPClient) Delete(ctx context.Context, path string) error {
	return nil
}

func (m *MockHTTPClient) ClearCache() {}
func (m *MockHTTPClient) GetCacheStats() map[string]interface{} {
	return map[string]interface{}{"enabled": false}
}

// MockOllamaClient for testing - implements the same interface as ollama.Client
type MockOllamaClient struct {
	GenerateCompletionFunc func(ctx context.Context, prompt string) (string, error)
	ChatCompletionFunc     func(ctx context.Context, messages []map[string]interface{}) (map[string]interface{}, error)
	GenerateEmbeddingFunc  func(ctx context.Context, text string) ([]float64, error)
}

// Ensure MockOllamaClient implements OllamaClient interface
var _ ollama.OllamaClient = (*MockOllamaClient)(nil)

func (m *MockOllamaClient) GenerateCompletion(ctx context.Context, prompt string) (string, error) {
	if m.GenerateCompletionFunc != nil {
		return m.GenerateCompletionFunc(ctx, prompt)
	}
	return "mock response", nil
}

func (m *MockOllamaClient) ChatCompletion(ctx context.Context, messages []map[string]interface{}) (map[string]interface{}, error) {
	if m.ChatCompletionFunc != nil {
		return m.ChatCompletionFunc(ctx, messages)
	}
	return map[string]interface{}{"response": "mock chat response"}, nil
}

func (m *MockOllamaClient) GenerateEmbedding(ctx context.Context, text string) ([]float64, error) {
	if m.GenerateEmbeddingFunc != nil {
		return m.GenerateEmbeddingFunc(ctx, text)
	}
	// Return a mock embedding vector
	return []float64{0.1, 0.2, 0.3, 0.4, 0.5}, nil
}

func TestListFilesInVault(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockHTTP := &MockHTTPClient{
		GetFunc: func(ctx context.Context, path string, result interface{}) error {
			// Mock response
			files := []map[string]interface{}{
				{"name": "test1.md", "path": "test1.md", "type": "file"},
				{"name": "test2.md", "path": "test2.md", "type": "file"},
			}
			*result.(*[]map[string]interface{}) = files
			return nil
		},
	}

	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	// Test with empty path
	result := advancedTools.ListFilesInVault(context.Background(), map[string]interface{}{})

	if !result.Success {
		t.Errorf("Expected success, got error: %s", result.Error)
	}

	files, ok := result.Data.([]map[string]interface{})
	if !ok {
		t.Errorf("Expected []map[string]interface{}, got %T", result.Data)
	}

	if len(files) != 2 {
		t.Errorf("Expected 2 files, got %d", len(files))
	}
}

func TestReadNote(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockHTTP := &MockHTTPClient{
		GetFunc: func(ctx context.Context, path string, result interface{}) error {
			*result.(*string) = "# Test Note\nThis is test content."
			return nil
		},
	}

	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	// Test valid filename
	result := advancedTools.ReadNote(context.Background(), map[string]interface{}{
		"filename": "test.md",
	})

	if !result.Success {
		t.Errorf("Expected success, got error: %s", result.Error)
	}

	data, ok := result.Data.(map[string]interface{})
	if !ok {
		t.Errorf("Expected map[string]interface{}, got %T", result.Data)
	}

	if data["filename"] != "test.md" {
		t.Errorf("Expected filename 'test.md', got '%s'", data["filename"])
	}

	// Test missing filename
	result = advancedTools.ReadNote(context.Background(), map[string]interface{}{})
	if result.Success {
		t.Error("Expected failure for missing filename")
	}
}

func TestSearchVault(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockHTTP := &MockHTTPClient{
		SearchFunc: func(ctx context.Context, query string, limit int) ([]map[string]interface{}, error) {
			return []map[string]interface{}{
				{"path": "test1.md", "matches": []string{"test query"}},
				{"path": "test2.md", "matches": []string{"test query"}},
			}, nil
		},
	}

	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	// Test valid search
	result := advancedTools.SearchVault(context.Background(), map[string]interface{}{
		"query": "test query",
		"limit": 5,
	})

	if !result.Success {
		t.Errorf("Expected success, got error: %s", result.Error)
	}

	results, ok := result.Data.([]map[string]interface{})
	if !ok {
		t.Errorf("Expected []map[string]interface{}, got %T", result.Data)
	}

	if len(results) != 2 {
		t.Errorf("Expected 2 results, got %d", len(results))
	}

	// Test missing query
	result = advancedTools.SearchVault(context.Background(), map[string]interface{}{})
	if result.Success {
		t.Error("Expected failure for missing query")
	}
}

func TestSemanticSearch(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockHTTP := &MockHTTPClient{
		SearchFunc: func(ctx context.Context, query string, limit int) ([]map[string]interface{}, error) {
			return []map[string]interface{}{
				{"path": "semantic1.md", "score": 0.95},
				{"path": "semantic2.md", "score": 0.87},
			}, nil
		},
	}

	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	// Test semantic search
	result := advancedTools.SemanticSearch(context.Background(), map[string]interface{}{
		"query": "semantic test",
		"top_k": 5,
	})

	if !result.Success {
		t.Errorf("Expected success, got error: %s", result.Error)
	}

	data, ok := result.Data.(map[string]interface{})
	if !ok {
		t.Errorf("Expected map[string]interface{}, got %T", result.Data)
	}

	if data["query"] != "semantic test" {
		t.Errorf("Expected query 'semantic test', got '%s'", data["query"])
	}

	if data["top_k"] != 5 {
		t.Errorf("Expected top_k 5, got %v", data["top_k"])
	}
}

func TestCreateNote(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockHTTP := &MockHTTPClient{
		PostFunc: func(ctx context.Context, path string, body interface{}, result interface{}) error {
			*result.(*interface{}) = map[string]string{"status": "created"}
			return nil
		},
	}

	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	// Test valid note creation
	result := advancedTools.CreateNote(context.Background(), map[string]interface{}{
		"path":    "new-note.md",
		"content": "# New Note\nThis is new content.",
	})

	if !result.Success {
		t.Errorf("Expected success, got error: %s", result.Error)
	}

	data, ok := result.Data.(map[string]interface{})
	if !ok {
		t.Errorf("Expected map[string]interface{}, got %T", result.Data)
	}

	if data["path"] != "new-note.md" {
		t.Errorf("Expected path 'new-note.md', got '%s'", data["path"])
	}

	// Test missing path
	result = advancedTools.CreateNote(context.Background(), map[string]interface{}{
		"content": "content without path",
	})
	if result.Success {
		t.Error("Expected failure for missing path")
	}
}

func TestBulkTag(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockHTTP := &MockHTTPClient{}
	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	// Test valid bulk tagging
	result := advancedTools.BulkTag(context.Background(), map[string]interface{}{
		"tags": []interface{}{"tag1", "tag2", "tag3"},
	})

	if !result.Success {
		t.Errorf("Expected success, got error: %s", result.Error)
	}

	data, ok := result.Data.(map[string]interface{})
	if !ok {
		t.Errorf("Expected map[string]interface{}, got %T", result.Data)
	}

	tags, ok := data["tags"].([]string)
	if !ok {
		t.Errorf("Expected []string, got %T", data["tags"])
	}

	if len(tags) != 3 {
		t.Errorf("Expected 3 tags, got %d", len(tags))
	}

	// Test missing tags
	result = advancedTools.BulkTag(context.Background(), map[string]interface{}{})
	if result.Success {
		t.Error("Expected failure for missing tags")
	}
}

func TestAnalyzeLinks(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	mockHTTP := &MockHTTPClient{}
	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	// Test link analysis
	result := advancedTools.AnalyzeLinks(context.Background(), map[string]interface{}{})

	if !result.Success {
		t.Errorf("Expected success, got error: %s", result.Error)
	}

	data, ok := result.Data.(map[string]interface{})
	if !ok {
		t.Errorf("Expected map[string]interface{}, got %T", result.Data)
	}

	// Check that required fields are present
	requiredFields := []string{"nodes", "edges", "clusters"}
	for _, field := range requiredFields {
		if _, exists := data[field]; !exists {
			t.Errorf("Missing required field: %s", field)
		}
	}
}

func TestGetToolDefinitions(t *testing.T) {
	logger, _ := zap.NewDevelopment()
	mockHTTP := &MockHTTPClient{}
	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	definitions := advancedTools.GetToolDefinitions()

	if len(definitions) == 0 {
		t.Error("Expected tool definitions, got empty slice")
	}

	// Check that all expected tools are present
	expectedTools := []string{
		"list_files_in_vault",
		"read_note",
		"search_vault",
		"semantic_search",
		"create_note",
		"bulk_tag",
		"analyze_links",
	}

	foundTools := make(map[string]bool)
	for _, def := range definitions {
		foundTools[def.Name] = true
	}

	for _, expected := range expectedTools {
		if !foundTools[expected] {
			t.Errorf("Missing expected tool: %s", expected)
		}
	}
}

// Benchmark tests for performance validation
func BenchmarkListFilesInVault(b *testing.B) {
	logger, _ := zap.NewDevelopment()
	mockHTTP := &MockHTTPClient{
		GetFunc: func(ctx context.Context, path string, result interface{}) error {
			files := make([]map[string]interface{}, 1000)
			for i := 0; i < 1000; i++ {
				files[i] = map[string]interface{}{
					"name": fmt.Sprintf("file%d.md", i),
					"path": fmt.Sprintf("file%d.md", i),
					"type": "file",
				}
			}
			*result.(*[]map[string]interface{}) = files
			return nil
		},
	}
	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		advancedTools.ListFilesInVault(context.Background(), map[string]interface{}{})
	}
}

func BenchmarkSearchVault(b *testing.B) {
	logger, _ := zap.NewDevelopment()
	mockHTTP := &MockHTTPClient{
		SearchFunc: func(ctx context.Context, query string, limit int) ([]map[string]interface{}, error) {
			results := make([]map[string]interface{}, limit)
			for i := 0; i < limit; i++ {
				results[i] = map[string]interface{}{
					"path":    fmt.Sprintf("result%d.md", i),
					"matches": []string{query},
				}
			}
			return results, nil
		},
	}
	mockOllama := &MockOllamaClient{}

	advancedTools := tools.NewAdvancedTools(mockHTTP, mockOllama, logger)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		advancedTools.SearchVault(context.Background(), map[string]interface{}{
			"query": "benchmark test",
			"limit": 10,
		})
	}
}
