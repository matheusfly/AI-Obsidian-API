package client

import (
	"context"
)

// HTTPClient defines the interface for HTTP operations
type HTTPClient interface {
	Get(ctx context.Context, path string, result interface{}) error
	Post(ctx context.Context, path string, body interface{}, result interface{}) error
	Put(ctx context.Context, path string, body interface{}, result interface{}) error
	Delete(ctx context.Context, path string) error
	Search(ctx context.Context, query string, limit int) ([]map[string]interface{}, error)
	ClearCache()
	GetCacheStats() map[string]interface{}
}
