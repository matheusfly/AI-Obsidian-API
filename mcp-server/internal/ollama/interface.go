package ollama

import "context"

// OllamaClient defines the interface for Ollama operations
type OllamaClient interface {
	GenerateCompletion(ctx context.Context, prompt string) (string, error)
	ChatCompletion(ctx context.Context, messages []map[string]interface{}) (map[string]interface{}, error)
	GenerateEmbedding(ctx context.Context, text string) ([]float64, error)
}
