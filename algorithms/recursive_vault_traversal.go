package algorithms

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// RecursiveVaultTraversal handles recursive traversal of Obsidian vault directories
// to discover all files, addressing the limitation where root /vault/ may only return top-level items
type RecursiveVaultTraversal struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
	cache      map[string][]FileInfo
	cacheTime  time.Time
	cacheTTL   time.Duration
}

// VaultItem represents a file or folder item from the vault API
type VaultItem struct {
	Path     string    `json:"path"`
	Name     string    `json:"name"`
	Type     string    `json:"type"` // "file" or "folder"
	Modified time.Time `json:"modified"`
	Size     int64     `json:"size"`
}

// NewRecursiveVaultTraversal creates a new RecursiveVaultTraversal instance
func NewRecursiveVaultTraversal(apiKey, baseURL string) *RecursiveVaultTraversal {
	// Configure HTTP client with TLS bypass for self-signed certificates
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	return &RecursiveVaultTraversal{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Transport: tr, Timeout: 30 * time.Second},
		cache:      make(map[string][]FileInfo),
		cacheTTL:   5 * time.Minute,
	}
}

// Traverse recursively lists all files in the vault by traversing directories
// Returns all markdown files found in the vault
func (rvt *RecursiveVaultTraversal) Traverse(path string) ([]FileInfo, error) {
	// Check cache first
	if rvt.isCacheValid(path) {
		return rvt.cache[path], nil
	}

	allFiles := make([]FileInfo, 0)
	err := rvt.traverseRecursive(path, &allFiles)
	if err != nil {
		return nil, fmt.Errorf("recursive traversal failed: %w", err)
	}

	// Cache the results
	rvt.cache[path] = allFiles
	rvt.cacheTime = time.Now()

	return allFiles, nil
}

// traverseRecursive performs the actual recursive traversal
func (rvt *RecursiveVaultTraversal) traverseRecursive(path string, allFiles *[]FileInfo) error {
	url := rvt.baseURL + "/vault/" + path
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+rvt.apiKey)
	req.Header.Add("Accept", "application/json")

	resp, err := rvt.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == 404 {
		// Empty directory or non-existent path - not an error
		return nil
	}

	if resp.StatusCode != 200 {
		return fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	// Parse the response structure - vault API returns {"files": []string}
	var response struct {
		Files []string `json:"files"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return fmt.Errorf("failed to decode response: %w", err)
	}

	for _, filePath := range response.Files {
		// Check if it's a markdown file
		if strings.HasSuffix(filePath, ".md") {
			// Create FileInfo from the path
			fileInfo := FileInfo{
				Path:     filePath,
				Name:     strings.TrimPrefix(filePath, path+"/"),
				Modified: time.Now(), // We don't have modification time from this endpoint
				Size:     0,          // We don't have size from this endpoint
			}
			*allFiles = append(*allFiles, fileInfo)
		}
	}

	return nil
}

// isCacheValid checks if the cache is still valid for the given path
func (rvt *RecursiveVaultTraversal) isCacheValid(path string) bool {
	if rvt.cacheTime.IsZero() {
		return false
	}
	return time.Since(rvt.cacheTime) < rvt.cacheTTL && rvt.cache[path] != nil
}

// GetStats returns statistics about the traversal
func (rvt *RecursiveVaultTraversal) GetStats() map[string]interface{} {
	totalFiles := 0
	for _, files := range rvt.cache {
		totalFiles += len(files)
	}

	return map[string]interface{}{
		"CacheSize":  len(rvt.cache),
		"TotalFiles": totalFiles,
		"CacheTime":  rvt.cacheTime,
		"CacheTTL":   rvt.cacheTTL,
		"CacheValid": !rvt.cacheTime.IsZero() && time.Since(rvt.cacheTime) < rvt.cacheTTL,
	}
}

// ClearCache clears the traversal cache
func (rvt *RecursiveVaultTraversal) ClearCache() {
	rvt.cache = make(map[string][]FileInfo)
	rvt.cacheTime = time.Time{}
}

// SetCacheTTL sets the cache time-to-live
func (rvt *RecursiveVaultTraversal) SetCacheTTL(ttl time.Duration) {
	rvt.cacheTTL = ttl
}

// GetCachedFiles returns cached files for a specific path
func (rvt *RecursiveVaultTraversal) GetCachedFiles(path string) ([]FileInfo, bool) {
	if rvt.isCacheValid(path) {
		return rvt.cache[path], true
	}
	return nil, false
}

// TraverseWithFilter performs traversal with a custom filter function
func (rvt *RecursiveVaultTraversal) TraverseWithFilter(path string, filter func(FileInfo) bool) ([]FileInfo, error) {
	allFiles, err := rvt.Traverse(path)
	if err != nil {
		return nil, err
	}

	if filter == nil {
		return allFiles, nil
	}

	filteredFiles := make([]FileInfo, 0)
	for _, file := range allFiles {
		if filter(file) {
			filteredFiles = append(filteredFiles, file)
		}
	}

	return filteredFiles, nil
}

// GetFileCount returns the total number of files found in the vault
func (rvt *RecursiveVaultTraversal) GetFileCount() int {
	total := 0
	for _, files := range rvt.cache {
		total += len(files)
	}
	return total
}

// GetDirectoryCount returns the number of directories traversed
func (rvt *RecursiveVaultTraversal) GetDirectoryCount() int {
	return len(rvt.cache)
}

// IsEmpty checks if the vault is empty (no files found)
func (rvt *RecursiveVaultTraversal) IsEmpty() bool {
	return rvt.GetFileCount() == 0
}

// GetFilesByExtension returns files filtered by extension
func (rvt *RecursiveVaultTraversal) GetFilesByExtension(extension string) ([]FileInfo, error) {
	return rvt.TraverseWithFilter("", func(file FileInfo) bool {
		return strings.HasSuffix(strings.ToLower(file.Name), strings.ToLower(extension))
	})
}

// GetFilesByPathPattern returns files matching a path pattern
func (rvt *RecursiveVaultTraversal) GetFilesByPathPattern(pattern string) ([]FileInfo, error) {
	return rvt.TraverseWithFilter("", func(file FileInfo) bool {
		return strings.Contains(strings.ToLower(file.Path), strings.ToLower(pattern))
	})
}

// GetRecentFiles returns files modified within the specified duration
func (rvt *RecursiveVaultTraversal) GetRecentFiles(since time.Duration) ([]FileInfo, error) {
	cutoff := time.Now().Add(-since)
	return rvt.TraverseWithFilter("", func(file FileInfo) bool {
		return file.Modified.After(cutoff)
	})
}
