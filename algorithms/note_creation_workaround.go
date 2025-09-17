package algorithms

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"path/filepath"
	"strings"
	"time"
)

// NoteCreationWorkaround bypasses POST /vault/{path} failures by using PUT for creation/update
type NoteCreationWorkaround struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
	stats      CreationStats
}

// CreationStats tracks note creation/update statistics
type CreationStats struct {
	Created     int           `json:"created"`
	Updated     int           `json:"updated"`
	Failed      int           `json:"failed"`
	TotalTime   time.Duration `json:"total_time"`
	LastCreated time.Time     `json:"last_created"`
	LastUpdated time.Time     `json:"last_updated"`
}

// NoteContent represents the content structure for note operations
type NoteContent struct {
	Content string `json:"content"`
}

// CreationResult represents the result of a note creation/update operation
type CreationResult struct {
	Success   bool          `json:"success"`
	Action    string        `json:"action"` // "created" or "updated"
	Path      string        `json:"path"`
	Size      int64         `json:"size"`
	Duration  time.Duration `json:"duration"`
	Error     string        `json:"error,omitempty"`
	Timestamp time.Time     `json:"timestamp"`
}

// NewNoteCreationWorkaround creates a new NoteCreationWorkaround instance
func NewNoteCreationWorkaround(apiKey, baseURL string) *NoteCreationWorkaround {
	// Configure HTTP client with TLS bypass for self-signed certificates
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	return &NoteCreationWorkaround{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Transport: tr, Timeout: 30 * time.Second},
		stats:      CreationStats{},
	}
}

// CreateOrUpdate creates a new note or updates an existing one using PUT
func (ncw *NoteCreationWorkaround) CreateOrUpdate(path, content string) (*CreationResult, error) {
	startTime := time.Now()
	result := &CreationResult{
		Path:      path,
		Timestamp: time.Now(),
	}

	// Normalize path
	path = ncw.normalizePath(path)

	// Check if file exists
	exists, err := ncw.fileExists(path)
	if err != nil {
		result.Error = fmt.Sprintf("failed to check file existence: %v", err)
		ncw.stats.Failed++
		return result, err
	}

	// Prepare content
	noteContent := NoteContent{Content: content}
	jsonData, err := json.Marshal(noteContent)
	if err != nil {
		result.Error = fmt.Sprintf("failed to marshal content: %v", err)
		ncw.stats.Failed++
		return result, err
	}

	// Create or update using PUT
	url := ncw.baseURL + "/vault/" + path
	req, err := http.NewRequest("PUT", url, bytes.NewBuffer(jsonData))
	if err != nil {
		result.Error = fmt.Sprintf("failed to create request: %v", err)
		ncw.stats.Failed++
		return result, err
	}

	req.Header.Add("Authorization", "Bearer "+ncw.apiKey)
	req.Header.Add("Content-Type", "application/json")

	resp, err := ncw.httpClient.Do(req)
	if err != nil {
		result.Error = fmt.Sprintf("failed to execute request: %v", err)
		ncw.stats.Failed++
		return result, err
	}
	defer resp.Body.Close()

	result.Duration = time.Since(startTime)

	if resp.StatusCode == 204 {
		result.Success = true
		result.Size = int64(len(content))

		if exists {
			result.Action = "updated"
			ncw.stats.Updated++
			ncw.stats.LastUpdated = time.Now()
		} else {
			result.Action = "created"
			ncw.stats.Created++
			ncw.stats.LastCreated = time.Now()
		}

		ncw.stats.TotalTime += result.Duration
	} else {
		result.Error = fmt.Sprintf("API request failed with status %d", resp.StatusCode)
		ncw.stats.Failed++
	}

	return result, nil
}

// Create creates a new note (fails if already exists)
func (ncw *NoteCreationWorkaround) Create(path, content string) (*CreationResult, error) {
	// Check if file already exists
	exists, err := ncw.fileExists(path)
	if err != nil {
		return nil, fmt.Errorf("failed to check file existence: %w", err)
	}

	if exists {
		return &CreationResult{
			Success: false,
			Path:    path,
			Error:   "file already exists",
		}, fmt.Errorf("file %s already exists", path)
	}

	return ncw.CreateOrUpdate(path, content)
}

// Update updates an existing note (fails if doesn't exist)
func (ncw *NoteCreationWorkaround) Update(path, content string) (*CreationResult, error) {
	// Check if file exists
	exists, err := ncw.fileExists(path)
	if err != nil {
		return nil, fmt.Errorf("failed to check file existence: %w", err)
	}

	if !exists {
		return &CreationResult{
			Success: false,
			Path:    path,
			Error:   "file does not exist",
		}, fmt.Errorf("file %s does not exist", path)
	}

	return ncw.CreateOrUpdate(path, content)
}

// Delete deletes a note
func (ncw *NoteCreationWorkaround) Delete(path string) error {
	path = ncw.normalizePath(path)
	url := ncw.baseURL + "/vault/" + path

	req, err := http.NewRequest("DELETE", url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+ncw.apiKey)

	resp, err := ncw.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 204 {
		return fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	return nil
}

// fileExists checks if a file exists in the vault
func (ncw *NoteCreationWorkaround) fileExists(path string) (bool, error) {
	path = ncw.normalizePath(path)
	url := ncw.baseURL + "/vault/" + path

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return false, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+ncw.apiKey)

	resp, err := ncw.httpClient.Do(req)
	if err != nil {
		return false, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	return resp.StatusCode == 200, nil
}

// normalizePath normalizes the file path for API calls
func (ncw *NoteCreationWorkaround) normalizePath(path string) string {
	// Remove leading slash if present
	path = strings.TrimPrefix(path, "/")

	// Ensure .md extension
	if !strings.HasSuffix(strings.ToLower(path), ".md") {
		path += ".md"
	}

	// Clean path
	path = filepath.Clean(path)

	return path
}

// GetStats returns creation/update statistics
func (ncw *NoteCreationWorkaround) GetStats() CreationStats {
	return ncw.stats
}

// ResetStats resets the statistics
func (ncw *NoteCreationWorkaround) ResetStats() {
	ncw.stats = CreationStats{}
}

// GetSuccessRate returns the success rate as a percentage
func (ncw *NoteCreationWorkaround) GetSuccessRate() float64 {
	total := ncw.stats.Created + ncw.stats.Updated + ncw.stats.Failed
	if total == 0 {
		return 0.0
	}
	successful := ncw.stats.Created + ncw.stats.Updated
	return float64(successful) / float64(total) * 100.0
}

// GetAverageTime returns the average operation time
func (ncw *NoteCreationWorkaround) GetAverageTime() time.Duration {
	total := ncw.stats.Created + ncw.stats.Updated + ncw.stats.Failed
	if total == 0 {
		return 0
	}
	return ncw.stats.TotalTime / time.Duration(total)
}

// BatchCreate creates multiple notes in batch
func (ncw *NoteCreationWorkaround) BatchCreate(notes map[string]string) ([]CreationResult, error) {
	results := make([]CreationResult, 0, len(notes))

	for path, content := range notes {
		result, err := ncw.CreateOrUpdate(path, content)
		if err != nil {
			result = &CreationResult{
				Success: false,
				Path:    path,
				Error:   err.Error(),
			}
		}
		results = append(results, *result)
	}

	return results, nil
}

// CreateWithTemplate creates a note using a template
func (ncw *NoteCreationWorkaround) CreateWithTemplate(path, template string, variables map[string]string) (*CreationResult, error) {
	// Replace template variables
	content := template
	for key, value := range variables {
		placeholder := "{{" + key + "}}"
		content = strings.ReplaceAll(content, placeholder, value)
	}

	return ncw.CreateOrUpdate(path, content)
}

// CreateFromFile creates a note from a local file
func (ncw *NoteCreationWorkaround) CreateFromFile(vaultPath, localFilePath string) (*CreationResult, error) {
	// Read local file content
	content, err := ncw.readFileContent(localFilePath)
	if err != nil {
		return &CreationResult{
			Success: false,
			Path:    vaultPath,
			Error:   fmt.Sprintf("failed to read local file: %v", err),
		}, err
	}

	return ncw.CreateOrUpdate(vaultPath, content)
}

// readFileContent reads content from a local file
func (ncw *NoteCreationWorkaround) readFileContent(filePath string) (string, error) {
	// This is a simplified implementation
	// In a real implementation, you would read the file here
	return "", fmt.Errorf("file reading not implemented")
}

// ValidatePath validates if a path is suitable for note creation
func (ncw *NoteCreationWorkaround) ValidatePath(path string) error {
	if path == "" {
		return fmt.Errorf("path cannot be empty")
	}

	// Check for invalid characters
	invalidChars := []string{"<", ">", ":", "\"", "|", "?", "*"}
	for _, char := range invalidChars {
		if strings.Contains(path, char) {
			return fmt.Errorf("path contains invalid character: %s", char)
		}
	}

	// Check path length
	if len(path) > 255 {
		return fmt.Errorf("path too long (max 255 characters)")
	}

	return nil
}

// GetFileInfo retrieves information about a file
func (ncw *NoteCreationWorkaround) GetFileInfo(path string) (*FileInfo, error) {
	path = ncw.normalizePath(path)
	url := ncw.baseURL + "/vault/" + path

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+ncw.apiKey)

	resp, err := ncw.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("file not found or access denied")
	}

	// Parse response to get file info
	// This is a simplified implementation
	fileInfo := &FileInfo{
		Path:     path,
		Name:     filepath.Base(path),
		Modified: time.Now(), // Would parse from response headers
		Size:     resp.ContentLength,
	}

	return fileInfo, nil
}
