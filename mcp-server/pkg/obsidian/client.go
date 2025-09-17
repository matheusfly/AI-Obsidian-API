package obsidian

import (
	"bytes"
	"context"
	"crypto/tls"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

// Client represents an Obsidian Local REST API client
type Client struct {
	baseURL    string
	token      string
	httpClient *http.Client
}

// FileInfo represents a file or folder in the vault
type FileInfo struct {
	Path    string `json:"path"`
	Name    string `json:"name"`
	Type    string `json:"type"` // "file" or "folder"
	Modified time.Time `json:"modified"`
}

// SearchResult represents a single search match
type SearchResult struct {
	Path    string `json:"path"`
	Matches []struct {
		Line int    `json:"line"`
		Text string `json:"text"`
	} `json:"matches"`
}

// Command represents an Obsidian command
type Command struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

// NewClient creates a new Obsidian API client
func NewClient(baseURL, token string, httpClient *http.Client) *Client {
	if httpClient == nil {
		httpClient = &http.Client{
			Timeout: 10 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true}, // Bypass SSL for local Obsidian API
			},
		}
	}
	return &Client{
		baseURL:    baseURL,
		token:      token,
		httpClient: httpClient,
	}
}

// request performs an HTTP request to the Obsidian API with retries
func (c *Client) request(ctx context.Context, method, path string, body []byte) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")

	for i := 0; i < 3; i++ { // Retries
		resp, err := c.httpClient.Do(req)
		if err != nil {
			// Log and retry on network errors
			fmt.Printf("Request failed (attempt %d/%d): %v\n", i+1, 3, err)
			time.Sleep(time.Second * time.Duration(i+1))
			continue
		}
		defer resp.Body.Close()

		if resp.StatusCode >= 200 && resp.StatusCode < 300 {
			return ioutil.ReadAll(resp.Body)
		}

		// Handle specific API errors
		respBody, _ := ioutil.ReadAll(resp.Body)
		fmt.Printf("API error (status %d, attempt %d/%d): %s\n", resp.StatusCode, i+1, 3, string(respBody))

		if resp.StatusCode == http.StatusUnauthorized {
			return nil, errors.New("unauthorized: invalid or missing API token")
		}
		if resp.StatusCode == http.StatusNotFound {
			return nil, errors.New("not found: check path or endpoint")
		}

		time.Sleep(time.Second * time.Duration(i+1))
	}
	return nil, fmt.Errorf("request to %s %s failed after multiple retries", method, path)
}

// ListVault lists all files and folders in the vault
func (c *Client) ListVault(ctx context.Context) ([]FileInfo, error) {
	data, err := c.request(ctx, "GET", "/vault/", nil)
	if err != nil {
		return nil, err
	}
	var files []FileInfo
	// The API returns {"files": []string} for top-level, but FileInfo for sub-folders.
	// We need to handle both. For now, assume it returns FileInfo directly or adapt.
	// Based on the audit, /vault/ returns an array of objects.
	if err := json.Unmarshal(data, &files); err != nil {
		// Attempt to unmarshal as {"files": []string} if direct unmarshal fails
		var raw struct {
			Files []string `json:"files"`
		}
		if err := json.Unmarshal(data, &raw); err == nil {
			// Convert raw strings to FileInfo
			convertedFiles := make([]FileInfo, len(raw.Files))
			for i, f := range raw.Files {
				convertedFiles[i] = FileInfo{Path: f, Name: f, Type: "file"} // Type might need more logic
			}
			return convertedFiles, nil
		}
		return nil, fmt.Errorf("failed to unmarshal vault list: %w", err)
	}
	return files, nil
}

// GetFileContent retrieves the content of a specific file
func (c *Client) GetFileContent(ctx context.Context, path string) (string, error) {
	data, err := c.request(ctx, "GET", "/vault/"+path, nil)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// CreateFile creates a new file with content
func (c *Client) CreateFile(ctx context.Context, path, content string) error {
	body, _ := json.Marshal(map[string]string{"content": content})
	_, err := c.request(ctx, "POST", "/vault/"+path, body)
	return err
}

// UpdateFile updates an existing file with new content
func (c *Client) UpdateFile(ctx context.Context, path, content string) error {
	body, _ := json.Marshal(map[string]string{"content": content})
	_, err := c.request(ctx, "PUT", "/vault/"+path, body)
	return err
}

// DeleteFile deletes a file or folder
func (c *Client) DeleteFile(ctx context.Context, path string) error {
	_, err := c.request(ctx, "DELETE", "/vault/"+path, nil)
	return err
}

// SearchVault performs a search query on the vault
func (c *Client) SearchVault(ctx context.Context, query string, limit int) ([]SearchResult, error) {
	// The API audit mentions GET /search/?query=string&limit=int
	// and POST /search/ with a body. Let's use GET for simplicity first.
	path := fmt.Sprintf("/search/?query=%s&limit=%d", query, limit)
	data, err := c.request(ctx, "GET", path, nil)
	if err != nil {
		return nil, err
	}
	var results struct {
		Results []SearchResult `json:"results"`
		Total   int            `json:"total"`
	}
	if err := json.Unmarshal(data, &results); err != nil {
		return nil, fmt.Errorf("failed to unmarshal search results: %w", err)
	}
	return results.Results, nil
}

// ListCommands lists available Obsidian commands
func (c *Client) ListCommands(ctx context.Context) ([]Command, error) {
	data, err := c.request(ctx, "GET", "/commands/", nil)
	if err != nil {
		return nil, err
	}
	var commands []Command
	if err := json.Unmarshal(data, &commands); err != nil {
		return nil, fmt.Errorf("failed to unmarshal commands: %w", err)
	}
	return commands, nil
}

// ExecuteCommand executes an Obsidian command by ID
func (c *Client) ExecuteCommand(ctx context.Context, commandID string, params map[string]interface{}) (interface{}, error) {
	body, _ := json.Marshal(params)
	data, err := c.request(ctx, "POST", "/commands/"+commandID, body)
	if err != nil {
		return nil, err
	}
	var result interface{}
	if len(data) > 0 {
		if err := json.Unmarshal(data, &result); err != nil {
			return nil, fmt.Errorf("failed to unmarshal command execution result: %w", err)
		}
	}
	return result, nil
}
