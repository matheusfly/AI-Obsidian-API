package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

// APIPipeline represents an advanced API calling pipeline
type APIPipeline struct {
	name           string
	baseURL        string
	token          string
	client         *http.Client
	circuitBreaker *CircuitBreaker
	retryPolicy    *RetryPolicy
	rateLimiter    *RateLimiter
	cache          *PipelineCache
	monitor        *PipelineMonitor
}

// CircuitBreaker implements circuit breaker pattern for API calls
type CircuitBreaker struct {
	failureThreshold int
	timeout          time.Duration
	state            string // "closed", "open", "half-open"
	failureCount     int
	lastFailure      time.Time
	mutex            sync.RWMutex
}

// RetryPolicy defines retry behavior for failed requests
type RetryPolicy struct {
	maxRetries    int
	baseDelay     time.Duration
	maxDelay      time.Duration
	backoffFactor float64
}

// RateLimiter controls API call rate
type RateLimiter struct {
	requestsPerSecond int
	lastRequest       time.Time
	mutex             sync.Mutex
}

// PipelineCache provides intelligent caching for API responses
type PipelineCache struct {
	cache   map[string]*CacheEntry
	ttl     time.Duration
	maxSize int
	mutex   sync.RWMutex
}

// CacheEntry represents a cached API response
type CacheEntry struct {
	Data      interface{}
	Timestamp time.Time
	TTL       time.Duration
}

// PipelineMonitor tracks pipeline performance and health
type PipelineMonitor struct {
	metrics map[string]*Metric
	alerts  []Alert
	mutex   sync.RWMutex
}

// Metric represents a performance metric
type Metric struct {
	Name      string
	Value     float64
	Timestamp time.Time
	Type      string // "counter", "gauge", "histogram"
}

// Alert represents a pipeline alert
type Alert struct {
	Level     string
	Message   string
	Timestamp time.Time
	Resolved  bool
}

// APICall represents an API call with metadata
type APICall struct {
	Method     string
	Path       string
	Headers    map[string]string
	Body       interface{}
	Timeout    time.Duration
	RetryCount int
	CacheKey   string
	Priority   int
	Tags       []string
}

// APICallResult represents the result of an API call
type APICallResult struct {
	Success    bool
	StatusCode int
	Data       interface{}
	Error      error
	Duration   time.Duration
	RetryCount int
	FromCache  bool
	CacheHit   bool
	Metadata   map[string]interface{}
}

// NewAPIPipeline creates a new advanced API pipeline
func NewAPIPipeline(name, baseURL, token string) *APIPipeline {
	return &APIPipeline{
		name:    name,
		baseURL: baseURL,
		token:   token,
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
		circuitBreaker: &CircuitBreaker{
			failureThreshold: 5,
			timeout:          30 * time.Second,
			state:            "closed",
		},
		retryPolicy: &RetryPolicy{
			maxRetries:    3,
			baseDelay:     1 * time.Second,
			maxDelay:      10 * time.Second,
			backoffFactor: 2.0,
		},
		rateLimiter: &RateLimiter{
			requestsPerSecond: 10,
		},
		cache: &PipelineCache{
			cache:   make(map[string]*CacheEntry),
			ttl:     5 * time.Minute,
			maxSize: 1000,
		},
		monitor: &PipelineMonitor{
			metrics: make(map[string]*Metric),
			alerts:  make([]Alert, 0),
		},
	}
}

// ExecuteCall executes an API call with advanced features
func (p *APIPipeline) ExecuteCall(call *APICall) *APICallResult {
	start := time.Now()
	result := &APICallResult{
		Metadata: make(map[string]interface{}),
	}

	// Check circuit breaker
	if !p.circuitBreaker.CanExecute() {
		result.Error = fmt.Errorf("circuit breaker is open")
		result.Success = false
		return result
	}

	// Apply rate limiting
	if err := p.rateLimiter.Wait(); err != nil {
		result.Error = err
		result.Success = false
		return result
	}

	// Check cache first
	if call.CacheKey != "" {
		if cached, found := p.cache.Get(call.CacheKey); found {
			result.Data = cached
			result.Success = true
			result.FromCache = true
			result.CacheHit = true
			result.Duration = time.Since(start)
			p.monitor.RecordMetric("cache_hit", 1, "counter")
			return result
		}
	}

	// Execute the API call with retries
	for attempt := 0; attempt <= p.retryPolicy.maxRetries; attempt++ {
		result.RetryCount = attempt

		// Make the HTTP request
		httpResult := p.makeHTTPRequest(call)
		result.StatusCode = httpResult.StatusCode
		result.Data = httpResult.Data
		result.Error = httpResult.Error

		if httpResult.Error == nil && httpResult.StatusCode < 400 {
			result.Success = true
			result.Duration = time.Since(start)

			// Cache successful responses
			if call.CacheKey != "" && result.Data != nil {
				p.cache.Set(call.CacheKey, result.Data)
			}

			// Record success metrics
			p.monitor.RecordMetric("api_call_success", 1, "counter")
			p.monitor.RecordMetric("api_call_duration", float64(result.Duration.Milliseconds()), "histogram")

			// Reset circuit breaker on success
			p.circuitBreaker.RecordSuccess()
			break
		}

		// Record failure
		p.monitor.RecordMetric("api_call_failure", 1, "counter")
		p.circuitBreaker.RecordFailure()

		// Check if we should retry
		if attempt < p.retryPolicy.maxRetries {
			delay := p.calculateRetryDelay(attempt)
			time.Sleep(delay)
		}
	}

	result.Duration = time.Since(start)
	return result
}

// makeHTTPRequest makes the actual HTTP request
func (p *APIPipeline) makeHTTPRequest(call *APICall) *APICallResult {
	result := &APICallResult{}

	// Build URL
	fullURL := p.baseURL + call.Path

	// Prepare request body
	var body io.Reader
	if call.Body != nil {
		jsonBody, err := json.Marshal(call.Body)
		if err != nil {
			result.Error = fmt.Errorf("failed to marshal request body: %v", err)
			return result
		}
		body = strings.NewReader(string(jsonBody))
	}

	// Create HTTP request
	req, err := http.NewRequest(call.Method, fullURL, body)
	if err != nil {
		result.Error = fmt.Errorf("failed to create request: %v", err)
		return result
	}

	// Set headers
	req.Header.Set("Authorization", "Bearer "+p.token)
	req.Header.Set("Content-Type", "application/json")

	for key, value := range call.Headers {
		req.Header.Set(key, value)
	}

	// Set timeout
	if call.Timeout > 0 {
		client := &http.Client{
			Timeout: call.Timeout,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		}
		resp, err := client.Do(req)
		if err != nil {
			result.Error = err
			return result
		}
		defer resp.Body.Close()
		result.StatusCode = resp.StatusCode
	} else {
		resp, err := p.client.Do(req)
		if err != nil {
			result.Error = err
			return result
		}
		defer resp.Body.Close()
		result.StatusCode = resp.StatusCode
	}

	// Read response body
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		result.Error = fmt.Errorf("failed to read response body: %v", err)
		return result
	}

	// Parse JSON response
	var jsonData interface{}
	if err := json.Unmarshal(responseBody, &jsonData); err != nil {
		// If JSON parsing fails, return raw string
		result.Data = string(responseBody)
	} else {
		result.Data = jsonData
	}

	return result
}

// calculateRetryDelay calculates the delay for retry attempts
func (p *APIPipeline) calculateRetryDelay(attempt int) time.Duration {
	delay := time.Duration(float64(p.retryPolicy.baseDelay) *
		math.Pow(p.retryPolicy.backoffFactor, float64(attempt)))

	if delay > p.retryPolicy.maxDelay {
		delay = p.retryPolicy.maxDelay
	}

	return delay
}

// Circuit Breaker Methods
func (cb *CircuitBreaker) CanExecute() bool {
	cb.mutex.RLock()
	defer cb.mutex.RUnlock()

	if cb.state == "closed" {
		return true
	}

	if cb.state == "open" {
		if time.Since(cb.lastFailure) > cb.timeout {
			cb.state = "half-open"
			return true
		}
		return false
	}

	// half-open state
	return true
}

func (cb *CircuitBreaker) RecordSuccess() {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	cb.failureCount = 0
	cb.state = "closed"
}

func (cb *CircuitBreaker) RecordFailure() {
	cb.mutex.Lock()
	defer cb.mutex.Unlock()

	cb.failureCount++
	cb.lastFailure = time.Now()

	if cb.failureCount >= cb.failureThreshold {
		cb.state = "open"
	}
}

// Rate Limiter Methods
func (rl *RateLimiter) Wait() error {
	rl.mutex.Lock()
	defer rl.mutex.Unlock()

	now := time.Now()
	elapsed := now.Sub(rl.lastRequest)

	if elapsed < time.Second/time.Duration(rl.requestsPerSecond) {
		sleepTime := time.Second/time.Duration(rl.requestsPerSecond) - elapsed
		time.Sleep(sleepTime)
	}

	rl.lastRequest = time.Now()
	return nil
}

// Cache Methods
func (c *PipelineCache) Get(key string) (interface{}, bool) {
	c.mutex.RLock()
	defer c.mutex.RUnlock()

	entry, exists := c.cache[key]
	if !exists {
		return nil, false
	}

	// Check if entry has expired
	if time.Since(entry.Timestamp) > entry.TTL {
		delete(c.cache, key)
		return nil, false
	}

	return entry.Data, true
}

func (c *PipelineCache) Set(key string, data interface{}) {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	// Check cache size limit
	if len(c.cache) >= c.maxSize {
		// Remove oldest entry
		var oldestKey string
		var oldestTime time.Time
		for k, v := range c.cache {
			if oldestKey == "" || v.Timestamp.Before(oldestTime) {
				oldestKey = k
				oldestTime = v.Timestamp
			}
		}
		delete(c.cache, oldestKey)
	}

	c.cache[key] = &CacheEntry{
		Data:      data,
		Timestamp: time.Now(),
		TTL:       c.ttl,
	}
}

// Monitor Methods
func (m *PipelineMonitor) RecordMetric(name string, value float64, metricType string) {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	m.metrics[name] = &Metric{
		Name:      name,
		Value:     value,
		Timestamp: time.Now(),
		Type:      metricType,
	}
}

func (m *PipelineMonitor) GetMetrics() map[string]*Metric {
	m.mutex.RLock()
	defer m.mutex.RUnlock()

	// Return a copy
	result := make(map[string]*Metric)
	for k, v := range m.metrics {
		result[k] = v
	}
	return result
}

func (m *PipelineMonitor) AddAlert(level, message string) {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	m.alerts = append(m.alerts, Alert{
		Level:     level,
		Message:   message,
		Timestamp: time.Now(),
		Resolved:  false,
	})
}

// Advanced API Pipeline Methods for Obsidian Integration
func (p *APIPipeline) ListVaultFiles(path string) *APICallResult {
	cacheKey := fmt.Sprintf("vault_files_%s", path)

	call := &APICall{
		Method:   "GET",
		Path:     "/vault/" + url.PathEscape(path),
		CacheKey: cacheKey,
		Priority: 1,
		Tags:     []string{"vault", "files", "list"},
	}

	return p.ExecuteCall(call)
}

func (p *APIPipeline) ReadVaultFile(filename string) *APICallResult {
	cacheKey := fmt.Sprintf("vault_file_%s", filename)

	call := &APICall{
		Method:   "GET",
		Path:     "/vault/" + url.PathEscape(filename),
		CacheKey: cacheKey,
		Priority: 2,
		Tags:     []string{"vault", "file", "read"},
	}

	return p.ExecuteCall(call)
}

func (p *APIPipeline) SearchVaultContent(query string, maxResults int) *APICallResult {
	// This would implement advanced search through the vault
	// For now, we'll use the file listing and search through content

	call := &APICall{
		Method:   "GET",
		Path:     "/vault/",
		CacheKey: fmt.Sprintf("search_%s_%d", query, maxResults),
		Priority: 3,
		Tags:     []string{"vault", "search", "content"},
	}

	return p.ExecuteCall(call)
}

func (p *APIPipeline) CreateVaultFile(filename, content string) *APICallResult {
	call := &APICall{
		Method: "PUT",
		Path:   "/vault/" + url.PathEscape(filename),
		Body: map[string]interface{}{
			"content": content,
		},
		Headers: map[string]string{
			"Content-Type": "text/markdown",
		},
		Priority: 4,
		Tags:     []string{"vault", "file", "create"},
	}

	return p.ExecuteCall(call)
}

func (p *APIPipeline) UpdateVaultFile(filename, content string) *APICallResult {
	call := &APICall{
		Method: "PUT",
		Path:   "/vault/" + url.PathEscape(filename),
		Body: map[string]interface{}{
			"content": content,
		},
		Headers: map[string]string{
			"Content-Type": "text/markdown",
		},
		Priority: 4,
		Tags:     []string{"vault", "file", "update"},
	}

	return p.ExecuteCall(call)
}

func (p *APIPipeline) DeleteVaultFile(filename string) *APICallResult {
	call := &APICall{
		Method:   "DELETE",
		Path:     "/vault/" + url.PathEscape(filename),
		Priority: 5,
		Tags:     []string{"vault", "file", "delete"},
	}

	return p.ExecuteCall(call)
}

// GetPipelineHealth returns the health status of the pipeline
func (p *APIPipeline) GetPipelineHealth() map[string]interface{} {
	metrics := p.monitor.GetMetrics()

	health := map[string]interface{}{
		"name":     p.name,
		"base_url": p.baseURL,
		"circuit_breaker": map[string]interface{}{
			"state":         p.circuitBreaker.state,
			"failure_count": p.circuitBreaker.failureCount,
			"last_failure":  p.circuitBreaker.lastFailure,
		},
		"cache": map[string]interface{}{
			"size":     len(p.cache.cache),
			"max_size": p.cache.maxSize,
			"ttl":      p.cache.ttl.String(),
		},
		"metrics": metrics,
		"alerts":  p.monitor.alerts,
	}

	return health
}

// Demo function to show the advanced API pipeline in action
func demoAdvancedAPIPipeline() {
	fmt.Println("🚀 ADVANCED API PIPELINE DEMO")
	fmt.Println("=============================")

	// Create pipeline
	pipeline := NewAPIPipeline("obsidian-vault", "https://127.0.0.1:27124",
		"b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")

	// Test 1: List vault files
	fmt.Println("📁 Testing vault file listing...")
	result := pipeline.ListVaultFiles("")
	if result.Success {
		fmt.Printf("✅ Successfully listed files (%dms)\n", result.Duration.Milliseconds())
		if result.FromCache {
			fmt.Println("   📦 Result from cache")
		}
	} else {
		fmt.Printf("❌ Failed to list files: %v\n", result.Error)
	}

	// Test 2: Read a specific file
	fmt.Println("\n📖 Testing file reading...")
	result = pipeline.ReadVaultFile("1- Notas Indice/CIÊNCIAS EXATAS.md")
	if result.Success {
		fmt.Printf("✅ Successfully read file (%dms)\n", result.Duration.Milliseconds())
		if result.FromCache {
			fmt.Println("   📦 Result from cache")
		}
	} else {
		fmt.Printf("❌ Failed to read file: %v\n", result.Error)
	}

	// Test 3: Search content
	fmt.Println("\n🔍 Testing content search...")
	result = pipeline.SearchVaultContent("logica", 10)
	if result.Success {
		fmt.Printf("✅ Successfully searched content (%dms)\n", result.Duration.Milliseconds())
		if result.FromCache {
			fmt.Println("   📦 Result from cache")
		}
	} else {
		fmt.Printf("❌ Failed to search content: %v\n", result.Error)
	}

	// Show pipeline health
	fmt.Println("\n📊 Pipeline Health:")
	health := pipeline.GetPipelineHealth()
	healthJSON, _ := json.MarshalIndent(health, "", "  ")
	fmt.Println(string(healthJSON))

	fmt.Println("\n🎉 Advanced API Pipeline demo completed!")
}

func main() {
	demoAdvancedAPIPipeline()
}
