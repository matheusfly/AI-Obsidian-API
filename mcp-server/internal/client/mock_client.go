package client

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"go.uber.org/zap"
)

// MockClient provides mock responses for testing without external services
type MockClient struct {
	logger *zap.Logger
}

// NewMockClient creates a new mock client
func NewMockClient(logger *zap.Logger) *MockClient {
	return &MockClient{
		logger: logger,
	}
}

// Get simulates a GET request with mock data
func (m *MockClient) Get(ctx context.Context, path string, result interface{}) error {
	m.logger.Info("Mock GET request", zap.String("path", path))

	// Simulate network delay
	time.Sleep(100 * time.Millisecond)

	switch path {
	case "/":
		// Root endpoint response
		response := map[string]interface{}{
			"status": "OK",
			"manifest": map[string]interface{}{
				"id":      "obsidian-local-rest-api",
				"name":    "Obsidian Local REST API",
				"version": "3.2.0",
			},
		}
		return m.setResult(result, response)

	case "/vault/":
		// Vault listing response
		files := []map[string]interface{}{
			{
				"path":     "test-note.md",
				"name":     "test-note.md",
				"type":     "file",
				"modified": "2025-09-16T19:30:00Z",
			},
			{
				"path":     "another-note.md",
				"name":     "another-note.md",
				"type":     "file",
				"modified": "2025-09-16T19:25:00Z",
			},
			{
				"path":     "folder/",
				"name":     "folder",
				"type":     "folder",
				"modified": "2025-09-16T19:20:00Z",
			},
		}
		return m.setResult(result, files)

	case "/vault/test-note.md":
		// Note content response
		content := `# Test Note

This is a test note created by the MCP server mock mode.

## Features
- Mock data for testing
- No external dependencies
- Simulates real API responses

## Tags
#test #mock #mcp

## Links
- [[another-note]]
- [[folder/sub-note]]
`
		return m.setResult(result, content)

	case "/vault/another-note.md":
		// Another note content
		content := `# Another Note

This is another test note with different content.

## Content
- Some interesting information
- More test data
- Different structure

## Related
- [[test-note]]
`
		return m.setResult(result, content)

	default:
		// Default response for unknown paths
		response := map[string]interface{}{
			"error":   "Not found",
			"message": fmt.Sprintf("Mock endpoint %s not implemented", path),
		}
		return m.setResult(result, response)
	}
}

// Post simulates a POST request
func (m *MockClient) Post(ctx context.Context, path string, body interface{}, result interface{}) error {
	m.logger.Info("Mock POST request", zap.String("path", path), zap.Any("body", body))

	// Simulate network delay
	time.Sleep(100 * time.Millisecond)

	// Simulate successful creation
	response := map[string]interface{}{
		"success": true,
		"message": fmt.Sprintf("Mock created resource at %s", path),
		"data":    body,
	}

	return m.setResult(result, response)
}

// Put simulates a PUT request
func (m *MockClient) Put(ctx context.Context, path string, body interface{}, result interface{}) error {
	m.logger.Info("Mock PUT request", zap.String("path", path), zap.Any("body", body))

	// Simulate network delay
	time.Sleep(100 * time.Millisecond)

	// Simulate successful update
	response := map[string]interface{}{
		"success": true,
		"message": fmt.Sprintf("Mock updated resource at %s", path),
		"data":    body,
	}

	return m.setResult(result, response)
}

// Delete simulates a DELETE request
func (m *MockClient) Delete(ctx context.Context, path string) error {
	m.logger.Info("Mock DELETE request", zap.String("path", path))

	// Simulate network delay
	time.Sleep(100 * time.Millisecond)

	// Simulate successful deletion
	return nil
}

// Search simulates a search request
func (m *MockClient) Search(ctx context.Context, query string, limit int) ([]map[string]interface{}, error) {
	m.logger.Info("Mock search request", zap.String("query", query), zap.Int("limit", limit))

	// Simulate network delay
	time.Sleep(200 * time.Millisecond)

	// Return mock search results
	results := []map[string]interface{}{
		{
			"path":    "test-note.md",
			"matches": []map[string]interface{}{
				{
					"line": 1,
					"text": fmt.Sprintf("Found query '%s' in test-note.md", query),
				},
			},
			"score": 0.95,
		},
		{
			"path":    "another-note.md",
			"matches": []map[string]interface{}{
				{
					"line": 3,
					"text": fmt.Sprintf("Another match for '%s' in another-note.md", query),
				},
			},
			"score": 0.87,
		},
	}

	// Limit results
	if len(results) > limit {
		results = results[:limit]
	}

	return results, nil
}

// ClearCache is a no-op for mock client
func (m *MockClient) ClearCache() {
	m.logger.Info("Mock cache cleared")
}

// GetCacheStats returns mock cache statistics
func (m *MockClient) GetCacheStats() map[string]interface{} {
	return map[string]interface{}{
		"enabled": false,
		"items":   0,
		"ttl":     "0s",
		"mode":    "mock",
	}
}

// setResult sets the result using JSON marshaling/unmarshaling
func (m *MockClient) setResult(result interface{}, data interface{}) error {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("failed to marshal mock data: %w", err)
	}

	if err := json.Unmarshal(jsonData, result); err != nil {
		return fmt.Errorf("failed to unmarshal mock data: %w", err)
	}

	return nil
}
