package client

import (
	"context"
	"crypto/tls"
	"fmt"
	"net/http"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/sony/gobreaker"
)

// HTTPClient represents a robust HTTP client with retry, backoff, and circuit breaker
type HTTPClient struct {
	client         *resty.Client
	circuitBreaker *gobreaker.CircuitBreaker
	apiKey         string
	baseURL        string
	timeouts       map[string]time.Duration
	retryConfig    RetryConfig
}

// RetryConfig represents retry configuration
type RetryConfig struct {
	MaxRetries       int
	RetryWaitTime    time.Duration
	MaxRetryWaitTime time.Duration
	RetryConditions  []func(*resty.Response, error) bool
}

// CircuitBreakerConfig represents circuit breaker configuration
type CircuitBreakerConfig struct {
	MaxRequests   uint32
	Interval      time.Duration
	Timeout       time.Duration
	ReadyToTrip   func(counts gobreaker.Counts) bool
	OnStateChange func(name string, from gobreaker.State, to gobreaker.State)
}

// NewHTTPClient creates a new HTTP client with robust error handling
func NewHTTPClient(apiKey, baseURL string) *HTTPClient {
	// Create RESTy client with TLS skip verification
	client := resty.New()
	client.SetTLSClientConfig(&tls.Config{InsecureSkipVerify: true})

	// Set default headers
	client.SetHeaders(map[string]string{
		"Authorization": "Bearer " + apiKey,
		"Content-Type":  "application/json",
		"Accept":        "application/json",
		"User-Agent":    "API-MCP-Simbiosis/1.0",
	})

	// Configure timeouts
	timeouts := map[string]time.Duration{
		"short":  1 * time.Second,  // GET /, health checks
		"medium": 5 * time.Second,  // GET /vault/, file operations
		"long":   30 * time.Second, // Large file operations, commands
	}

	// Configure retry
	retryConfig := RetryConfig{
		MaxRetries:       3,
		RetryWaitTime:    1 * time.Second,
		MaxRetryWaitTime: 10 * time.Second,
		RetryConditions: []func(*resty.Response, error) bool{
			func(resp *resty.Response, err error) bool {
				// Retry on 5xx errors and timeouts
				return err != nil || (resp != nil && resp.StatusCode() >= 500)
			},
		},
	}

	// Configure circuit breaker
	cbConfig := CircuitBreakerConfig{
		MaxRequests: 5,
		Interval:    10 * time.Second,
		Timeout:     30 * time.Second,
		ReadyToTrip: func(counts gobreaker.Counts) bool {
			return counts.ConsecutiveFailures >= 5
		},
		OnStateChange: func(name string, from gobreaker.State, to gobreaker.State) {
			fmt.Printf("Circuit breaker %s changed from %s to %s\n", name, from, to)
		},
	}

	circuitBreaker := gobreaker.NewCircuitBreaker(gobreaker.Settings{
		Name:          "obsidian-api",
		MaxRequests:   cbConfig.MaxRequests,
		Interval:      cbConfig.Interval,
		Timeout:       cbConfig.Timeout,
		ReadyToTrip:   cbConfig.ReadyToTrip,
		OnStateChange: cbConfig.OnStateChange,
	})

	return &HTTPClient{
		client:         client,
		circuitBreaker: circuitBreaker,
		apiKey:         apiKey,
		baseURL:        baseURL,
		timeouts:       timeouts,
		retryConfig:    retryConfig,
	}
}

// Get performs a GET request with circuit breaker protection
func (hc *HTTPClient) Get(endpoint string, timeoutType string) (*resty.Response, error) {
	timeout := hc.timeouts[timeoutType]
	if timeout == 0 {
		timeout = hc.timeouts["medium"]
	}

	// Execute with circuit breaker
	result, err := hc.circuitBreaker.Execute(func() (interface{}, error) {
		resp, err := hc.client.R().
			Get(hc.baseURL + endpoint)
		return resp, err
	})

	if err != nil {
		return nil, err
	}

	return result.(*resty.Response), nil
}

// Post performs a POST request with circuit breaker protection
func (hc *HTTPClient) Post(endpoint string, body interface{}, timeoutType string) (*resty.Response, error) {
	timeout := hc.timeouts[timeoutType]
	if timeout == 0 {
		timeout = hc.timeouts["medium"]
	}

	// Execute with circuit breaker
	result, err := hc.circuitBreaker.Execute(func() (interface{}, error) {
		resp, err := hc.client.R().
			SetBody(body).
			Post(hc.baseURL + endpoint)
		return resp, err
	})

	if err != nil {
		return nil, err
	}

	return result.(*resty.Response), nil
}

// Put performs a PUT request with circuit breaker protection
func (hc *HTTPClient) Put(endpoint string, body interface{}, timeoutType string) (*resty.Response, error) {
	timeout := hc.timeouts[timeoutType]
	if timeout == 0 {
		timeout = hc.timeouts["medium"]
	}

	// Execute with circuit breaker
	result, err := hc.circuitBreaker.Execute(func() (interface{}, error) {
		resp, err := hc.client.R().
			SetBody(body).
			Put(hc.baseURL + endpoint)
		return resp, err
	})

	if err != nil {
		return nil, err
	}

	return result.(*resty.Response), nil
}

// Delete performs a DELETE request with circuit breaker protection
func (hc *HTTPClient) Delete(endpoint string, timeoutType string) (*resty.Response, error) {
	timeout := hc.timeouts[timeoutType]
	if timeout == 0 {
		timeout = hc.timeouts["medium"]
	}

	// Execute with circuit breaker
	result, err := hc.circuitBreaker.Execute(func() (interface{}, error) {
		resp, err := hc.client.R().
			Delete(hc.baseURL + endpoint)
		return resp, err
	})

	if err != nil {
		return nil, err
	}

	return result.(*resty.Response), nil
}

// GetWithRetry performs a GET request with retry logic
func (hc *HTTPClient) GetWithRetry(endpoint string, timeoutType string) (*resty.Response, error) {
	timeout := hc.timeouts[timeoutType]
	if timeout == 0 {
		timeout = hc.timeouts["medium"]
	}

	// Configure retry on the client
	hc.client.SetRetryCount(hc.retryConfig.MaxRetries)
	hc.client.SetRetryWaitTime(hc.retryConfig.RetryWaitTime)
	hc.client.SetRetryMaxWaitTime(hc.retryConfig.MaxRetryWaitTime)

	// Add retry conditions
	for _, condition := range hc.retryConfig.RetryConditions {
		hc.client.AddRetryCondition(condition)
	}

	// Execute with circuit breaker
	result, err := hc.circuitBreaker.Execute(func() (interface{}, error) {
		resp, err := hc.client.R().Get(hc.baseURL + endpoint)
		return resp, err
	})

	if err != nil {
		return nil, err
	}

	return result.(*resty.Response), nil
}

// StreamGet performs a streaming GET request
func (hc *HTTPClient) StreamGet(endpoint string, timeoutType string) (*http.Response, error) {
	timeout := hc.timeouts[timeoutType]
	if timeout == 0 {
		timeout = hc.timeouts["long"]
	}

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	// Create request
	req, err := http.NewRequestWithContext(ctx, "GET", hc.baseURL+endpoint, nil)
	if err != nil {
		return nil, err
	}

	// Set headers
	req.Header.Set("Authorization", "Bearer "+hc.apiKey)
	req.Header.Set("Accept", "application/json")
	req.Header.Set("User-Agent", "API-MCP-Simbiosis/1.0")

	// Create HTTP client with TLS skip verification
	httpClient := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
		Timeout: timeout,
	}

	// Execute with circuit breaker
	result, err := hc.circuitBreaker.Execute(func() (interface{}, error) {
		resp, err := httpClient.Do(req)
		return resp, err
	})

	if err != nil {
		return nil, err
	}

	return result.(*http.Response), nil
}

// HealthCheck performs a health check on the API
func (hc *HTTPClient) HealthCheck() (*HealthStatus, error) {
	startTime := time.Now()

	// Try to get vault list as health check
	resp, err := hc.Get("/vault/", "short")
	if err != nil {
		return &HealthStatus{
			Status:       "unhealthy",
			Error:        err.Error(),
			ResponseTime: time.Since(startTime),
			Timestamp:    time.Now(),
		}, nil
	}

	responseTime := time.Since(startTime)

	if resp.StatusCode() == 200 {
		return &HealthStatus{
			Status:       "healthy",
			ResponseTime: responseTime,
			StatusCode:   resp.StatusCode(),
			Timestamp:    time.Now(),
		}, nil
	}

	return &HealthStatus{
		Status:       "unhealthy",
		StatusCode:   resp.StatusCode(),
		ResponseTime: responseTime,
		Timestamp:    time.Now(),
	}, nil
}

// SetTimeout sets a custom timeout for a specific operation type
func (hc *HTTPClient) SetTimeout(operationType string, timeout time.Duration) {
	hc.timeouts[operationType] = timeout
}

// SetRetryConfig updates the retry configuration
func (hc *HTTPClient) SetRetryConfig(config RetryConfig) {
	hc.retryConfig = config
}

// GetCircuitBreakerState returns the current circuit breaker state
func (hc *HTTPClient) GetCircuitBreakerState() gobreaker.State {
	return hc.circuitBreaker.State()
}

// GetCircuitBreakerCounts returns the current circuit breaker counts
func (hc *HTTPClient) GetCircuitBreakerCounts() gobreaker.Counts {
	return hc.circuitBreaker.Counts()
}

// HealthStatus represents the health status of the API
type HealthStatus struct {
	Status       string        `json:"status"`
	ResponseTime time.Duration `json:"response_time"`
	StatusCode   int           `json:"status_code,omitempty"`
	Error        string        `json:"error,omitempty"`
	Timestamp    time.Time     `json:"timestamp"`
}

// ClientStats represents statistics about the HTTP client
type ClientStats struct {
	CircuitBreakerState  gobreaker.State          `json:"circuit_breaker_state"`
	CircuitBreakerCounts gobreaker.Counts         `json:"circuit_breaker_counts"`
	Timeouts             map[string]time.Duration `json:"timeouts"`
	RetryConfig          RetryConfig              `json:"retry_config"`
}

// GetStats returns statistics about the HTTP client
func (hc *HTTPClient) GetStats() ClientStats {
	return ClientStats{
		CircuitBreakerState:  hc.circuitBreaker.State(),
		CircuitBreakerCounts: hc.circuitBreaker.Counts(),
		Timeouts:             hc.timeouts,
		RetryConfig:          hc.retryConfig,
	}
}

// GetClient returns the underlying HTTP client for sharing
func (hc *HTTPClient) GetClient() *http.Client {
	return hc.client.GetClient()
}
