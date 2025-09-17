package algorithms

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"
)

// BatchParallelFetcher fetches multiple file contents in parallel using concurrent API calls
type BatchParallelFetcher struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
	batchSize  int
	maxRetries int
	retryDelay time.Duration
	timeout    time.Duration
	stats      FetchStats
}

// FetchStats tracks fetching statistics
type FetchStats struct {
	TotalRequests      int           `json:"total_requests"`
	SuccessfulRequests int           `json:"successful_requests"`
	FailedRequests     int           `json:"failed_requests"`
	TotalTime          time.Duration `json:"total_time"`
	AverageTime        time.Duration `json:"average_time"`
	ConcurrencyLevel   int           `json:"concurrency_level"`
}

// FetchResult represents the result of fetching a file
type FetchResult struct {
	Path      string        `json:"path"`
	Content   string        `json:"content"`
	Success   bool          `json:"success"`
	Error     string        `json:"error,omitempty"`
	FetchTime time.Duration `json:"fetch_time"`
	Retries   int           `json:"retries"`
}

// NewBatchParallelFetcher creates a new BatchParallelFetcher instance
func NewBatchParallelFetcher(apiKey, baseURL string, batchSize, maxRetries int) *BatchParallelFetcher {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}

	return &BatchParallelFetcher{
		apiKey:     apiKey,
		baseURL:    baseURL,
		httpClient: &http.Client{Transport: tr, Timeout: 30 * time.Second},
		batchSize:  batchSize,
		maxRetries: maxRetries,
		retryDelay: 1 * time.Second,
		timeout:    30 * time.Second,
		stats:      FetchStats{},
	}
}

// FetchFiles fetches multiple files in parallel batches
func (bpf *BatchParallelFetcher) FetchFiles(paths []string) (map[string]*FetchResult, error) {
	startTime := time.Now()

	if len(paths) == 0 {
		return make(map[string]*FetchResult), nil
	}

	// Initialize results map
	results := make(map[string]*FetchResult)
	var mu sync.Mutex
	var wg sync.WaitGroup

	// Process files in batches
	for i := 0; i < len(paths); i += bpf.batchSize {
		end := i + bpf.batchSize
		if end > len(paths) {
			end = len(paths)
		}

		batch := paths[i:end]
		wg.Add(1)

		go func(batch []string) {
			defer wg.Done()
			bpf.processBatch(batch, results, &mu)
		}(batch)
	}

	// Wait for all batches to complete
	wg.Wait()

	// Update statistics
	bpf.updateStats(len(paths), results, time.Since(startTime))

	return results, nil
}

// processBatch processes a batch of files
func (bpf *BatchParallelFetcher) processBatch(batch []string, results map[string]*FetchResult, mu *sync.Mutex) {
	for _, path := range batch {
		result := bpf.fetchFile(path)

		mu.Lock()
		results[path] = result
		mu.Unlock()
	}
}

// fetchFile fetches a single file with retry logic
func (bpf *BatchParallelFetcher) fetchFile(path string) *FetchResult {
	startTime := time.Now()

	for attempt := 0; attempt <= bpf.maxRetries; attempt++ {
		content, err := bpf.makeRequest(path)
		fetchTime := time.Since(startTime)

		if err == nil {
			return &FetchResult{
				Path:      path,
				Content:   content,
				Success:   true,
				FetchTime: fetchTime,
				Retries:   attempt,
			}
		}

		// If this is not the last attempt, wait before retrying
		if attempt < bpf.maxRetries {
			time.Sleep(bpf.retryDelay * time.Duration(attempt+1)) // Exponential backoff
		}
	}

	// All retries failed
	return &FetchResult{
		Path:      path,
		Content:   "",
		Success:   false,
		Error:     fmt.Sprintf("failed after %d retries", bpf.maxRetries),
		FetchTime: time.Since(startTime),
		Retries:   bpf.maxRetries,
	}
}

// makeRequest makes a single HTTP request to fetch file content
func (bpf *BatchParallelFetcher) makeRequest(path string) (string, error) {
	url := bpf.baseURL + "/vault/" + path
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Add("Authorization", "Bearer "+bpf.apiKey)
	req.Header.Add("Accept", "application/json")

	resp, err := bpf.httpClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == 404 {
		return "", fmt.Errorf("file not found: %s", path)
	}

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("API request failed with status %d", resp.StatusCode)
	}

	var fileResponse struct {
		Content string `json:"content"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&fileResponse); err != nil {
		return "", fmt.Errorf("failed to decode response: %w", err)
	}

	return fileResponse.Content, nil
}

// updateStats updates the fetching statistics
func (bpf *BatchParallelFetcher) updateStats(totalRequests int, results map[string]*FetchResult, totalTime time.Duration) {
	successful := 0
	failed := 0
	var totalFetchTime time.Duration

	for _, result := range results {
		if result.Success {
			successful++
		} else {
			failed++
		}
		totalFetchTime += result.FetchTime
	}

	bpf.stats = FetchStats{
		TotalRequests:      totalRequests,
		SuccessfulRequests: successful,
		FailedRequests:     failed,
		TotalTime:          totalTime,
		AverageTime:        totalTime / time.Duration(totalRequests),
		ConcurrencyLevel:   bpf.batchSize,
	}
}

// GetStats returns the current fetching statistics
func (bpf *BatchParallelFetcher) GetStats() FetchStats {
	return bpf.stats
}

// SetBatchSize sets the batch size for parallel fetching
func (bpf *BatchParallelFetcher) SetBatchSize(size int) {
	bpf.batchSize = size
}

// SetMaxRetries sets the maximum number of retries
func (bpf *BatchParallelFetcher) SetMaxRetries(retries int) {
	bpf.maxRetries = retries
}

// SetRetryDelay sets the delay between retries
func (bpf *BatchParallelFetcher) SetRetryDelay(delay time.Duration) {
	bpf.retryDelay = delay
}

// SetTimeout sets the timeout for individual requests
func (bpf *BatchParallelFetcher) SetTimeout(timeout time.Duration) {
	bpf.timeout = timeout
	bpf.httpClient.Timeout = timeout
}

// FetchFilesWithProgress fetches files with progress reporting
func (bpf *BatchParallelFetcher) FetchFilesWithProgress(paths []string, progressCallback func(int, int)) (map[string]*FetchResult, error) {
	startTime := time.Now()

	if len(paths) == 0 {
		return make(map[string]*FetchResult), nil
	}

	results := make(map[string]*FetchResult)
	var mu sync.Mutex
	var wg sync.WaitGroup
	completed := 0

	// Process files in batches
	for i := 0; i < len(paths); i += bpf.batchSize {
		end := i + bpf.batchSize
		if end > len(paths) {
			end = len(paths)
		}

		batch := paths[i:end]
		wg.Add(1)

		go func(batch []string) {
			defer wg.Done()
			for _, path := range batch {
				result := bpf.fetchFile(path)

				mu.Lock()
				results[path] = result
				completed++
				mu.Unlock()

				// Report progress
				if progressCallback != nil {
					progressCallback(completed, len(paths))
				}
			}
		}(batch)
	}

	wg.Wait()

	// Update statistics
	bpf.updateStats(len(paths), results, time.Since(startTime))

	return results, nil
}

// GetSuccessfulResults returns only the successful fetch results
func (bpf *BatchParallelFetcher) GetSuccessfulResults(results map[string]*FetchResult) map[string]string {
	successful := make(map[string]string)

	for path, result := range results {
		if result.Success {
			successful[path] = result.Content
		}
	}

	return successful
}

// GetFailedResults returns only the failed fetch results
func (bpf *BatchParallelFetcher) GetFailedResults(results map[string]*FetchResult) map[string]string {
	failed := make(map[string]string)

	for path, result := range results {
		if !result.Success {
			failed[path] = result.Error
		}
	}

	return failed
}

// ResetStats resets the fetching statistics
func (bpf *BatchParallelFetcher) ResetStats() {
	bpf.stats = FetchStats{}
}
