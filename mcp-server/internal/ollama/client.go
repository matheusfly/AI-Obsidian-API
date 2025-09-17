package ollama

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

// Client represents an Ollama API client
type Client struct {
	host       string
	model      string
	httpClient *http.Client
}

// Ensure Client implements OllamaClient interface
var _ OllamaClient = (*Client)(nil)

// NewClient creates a new Ollama API client
func NewClient(host, model string) *Client {
	return &Client{
		host:       host,
		model:      model,
		httpClient: &http.Client{Timeout: 300 * time.Second}, // Longer timeout for LLM calls
	}
}

// GenerateCompletion sends a completion request to Ollama
func (c *Client) GenerateCompletion(ctx context.Context, prompt string) (string, error) {
	requestBody := map[string]interface{}{
		"model":  c.model,
		"prompt": prompt,
		"stream": false,
	}
	jsonBody, _ := json.Marshal(requestBody)

	resp, err := c.httpClient.Post(c.host+"/api/generate", "application/json", bytes.NewReader(jsonBody))
	if err != nil {
		return "", fmt.Errorf("failed to send generate request to Ollama: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		return "", fmt.Errorf("ollama generate API returned status %d: %s", resp.StatusCode, string(bodyBytes))
	}

	var response struct {
		Response string `json:"response"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return "", fmt.Errorf("failed to decode Ollama generate response: %w", err)
	}

	return response.Response, nil
}

// ChatCompletion sends a chat completion request to Ollama (for tool calling)
func (c *Client) ChatCompletion(ctx context.Context, messages []map[string]interface{}) (map[string]interface{}, error) {
	requestBody := map[string]interface{}{
		"model":    c.model,
		"messages": messages,
		"stream":   false,
	}
	jsonBody, _ := json.Marshal(requestBody)

	resp, err := c.httpClient.Post(c.host+"/api/chat", "application/json", bytes.NewReader(jsonBody))
	if err != nil {
		return nil, fmt.Errorf("failed to send chat request to Ollama: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		return nil, fmt.Errorf("ollama chat API returned status %d: %s", resp.StatusCode, string(bodyBytes))
	}

	var response map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode Ollama chat response: %w", err)
	}

	return response, nil
}

// GenerateEmbedding generates embeddings for the given text
func (c *Client) GenerateEmbedding(ctx context.Context, text string) ([]float64, error) {
	requestBody := map[string]interface{}{
		"model":  c.model,
		"prompt": text,
	}
	jsonBody, _ := json.Marshal(requestBody)

	resp, err := c.httpClient.Post(c.host+"/api/embeddings", "application/json", bytes.NewReader(jsonBody))
	if err != nil {
		return nil, fmt.Errorf("failed to send embedding request to Ollama: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		return nil, fmt.Errorf("ollama embedding API returned status %d: %s", resp.StatusCode, string(bodyBytes))
	}

	var response struct {
		Embedding []float64 `json:"embedding"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("failed to decode Ollama embedding response: %w", err)
	}

	return response.Embedding, nil
}
