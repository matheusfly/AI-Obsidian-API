package client

import (
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/url"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/patrickmn/go-cache"
	"go.uber.org/zap"
)

// Client represents an HTTP client with caching and retry logic
type Client struct {
	restyClient *resty.Client
	cache       *cache.Cache
	logger      *zap.Logger
	cfg         *Config
}

// Config holds client configuration
type Config struct {
	BaseURL     string
	Token       string
	Timeout     time.Duration
	RateLimit   int
	CacheTTL    time.Duration
	EnableCache bool
}

// NewClient creates a new HTTP client with caching
func NewClient(cfg *Config, logger *zap.Logger) *Client {
	restyClient := resty.New()
	restyClient.SetTimeout(cfg.Timeout)
	restyClient.SetHeader("Authorization", "Bearer "+cfg.Token)
	restyClient.SetBaseURL(cfg.BaseURL)

	// Configure TLS for self-signed certificates
	restyClient.SetTLSClientConfig(&tls.Config{
		InsecureSkipVerify: true, // Skip certificate verification for self-signed certs
	})

	// Add retry logic
	restyClient.SetRetryCount(3)
	restyClient.SetRetryWaitTime(1 * time.Second)
	restyClient.SetRetryMaxWaitTime(5 * time.Second)

	var cacheClient *cache.Cache
	if cfg.EnableCache {
		cacheClient = cache.New(cfg.CacheTTL, cfg.CacheTTL*2)
	}

	return &Client{
		restyClient: restyClient,
		cache:       cacheClient,
		logger:      logger,
		cfg:         cfg,
	}
}

// Get performs a GET request with caching
func (c *Client) Get(ctx context.Context, path string, result interface{}) error {
	// Check cache first
	if c.cache != nil {
		if cached, found := c.cache.Get(path); found {
			if c.logger != nil {
				c.logger.Debug("Cache hit", zap.String("path", path))
			}
			return json.Unmarshal(cached.([]byte), result)
		}
	}

	// Make request
	resp, err := c.restyClient.R().SetContext(ctx).SetResult(result).Get(path)
	if err != nil {
		if c.logger != nil {
			c.logger.Error("HTTP GET failed", zap.String("path", path), zap.Error(err))
		}
		return fmt.Errorf("HTTP GET failed: %w", err)
	}

	if resp.StatusCode() >= 400 {
		if c.logger != nil {
			c.logger.Error("HTTP error", zap.String("path", path), zap.Int("status", resp.StatusCode()))
		}
		return fmt.Errorf("HTTP error %d: %s", resp.StatusCode(), resp.String())
	}

	// Cache successful response
	if c.cache != nil && resp.StatusCode() == 200 {
		if body, err := json.Marshal(result); err == nil {
			c.cache.Set(path, body, cache.DefaultExpiration)
			if c.logger != nil {
				c.logger.Debug("Cached response", zap.String("path", path))
			}
		}
	}

	return nil
}

// Post performs a POST request
func (c *Client) Post(ctx context.Context, path string, body interface{}, result interface{}) error {
	resp, err := c.restyClient.R().
		SetContext(ctx).
		SetBody(body).
		SetResult(result).
		Post(path)

	if err != nil {
		if c.logger != nil {
			c.logger.Error("HTTP POST failed", zap.String("path", path), zap.Error(err))
		}
		return fmt.Errorf("HTTP POST failed: %w", err)
	}

	if resp.StatusCode() >= 400 {
		if c.logger != nil {
			c.logger.Error("HTTP error", zap.String("path", path), zap.Int("status", resp.StatusCode()))
		}
		return fmt.Errorf("HTTP error %d: %s", resp.StatusCode(), resp.String())
	}

	// Invalidate cache for write operations
	if c.cache != nil {
		c.cache.Delete(path)
		if c.logger != nil {
			c.logger.Debug("Invalidated cache", zap.String("path", path))
		}
	}

	return nil
}

// Put performs a PUT request
func (c *Client) Put(ctx context.Context, path string, body interface{}, result interface{}) error {
	resp, err := c.restyClient.R().
		SetContext(ctx).
		SetBody(body).
		SetResult(result).
		Put(path)

	if err != nil {
		if c.logger != nil {
			c.logger.Error("HTTP PUT failed", zap.String("path", path), zap.Error(err))
		}
		return fmt.Errorf("HTTP PUT failed: %w", err)
	}

	if resp.StatusCode() >= 400 {
		if c.logger != nil {
			c.logger.Error("HTTP error", zap.String("path", path), zap.Int("status", resp.StatusCode()))
		}
		return fmt.Errorf("HTTP error %d: %s", resp.StatusCode(), resp.String())
	}

	// Invalidate cache for write operations
	if c.cache != nil {
		c.cache.Delete(path)
		if c.logger != nil {
			c.logger.Debug("Invalidated cache", zap.String("path", path))
		}
	}

	return nil
}

// Delete performs a DELETE request
func (c *Client) Delete(ctx context.Context, path string) error {
	resp, err := c.restyClient.R().SetContext(ctx).Delete(path)

	if err != nil {
		if c.logger != nil {
			c.logger.Error("HTTP DELETE failed", zap.String("path", path), zap.Error(err))
		}
		return fmt.Errorf("HTTP DELETE failed: %w", err)
	}

	if resp.StatusCode() >= 400 {
		if c.logger != nil {
			c.logger.Error("HTTP error", zap.String("path", path), zap.Int("status", resp.StatusCode()))
		}
		return fmt.Errorf("HTTP error %d: %s", resp.StatusCode(), resp.String())
	}

	// Invalidate cache for write operations
	if c.cache != nil {
		c.cache.Delete(path)
		if c.logger != nil {
			c.logger.Debug("Invalidated cache", zap.String("path", path))
		}
	}

	return nil
}

// Search performs a search request with query parameters
func (c *Client) Search(ctx context.Context, query string, limit int) ([]map[string]interface{}, error) {
	path := fmt.Sprintf("/search/?query=%s&limit=%d", url.QueryEscape(query), limit)

	var results struct {
		Results []map[string]interface{} `json:"results"`
		Total   int                      `json:"total"`
	}

	if err := c.Get(ctx, path, &results); err != nil {
		return nil, err
	}

	return results.Results, nil
}

// ClearCache clears the client cache
func (c *Client) ClearCache() {
	if c.cache != nil {
		c.cache.Flush()
		if c.logger != nil {
			c.logger.Info("Cache cleared")
		}
	}
}

// GetCacheStats returns cache statistics
func (c *Client) GetCacheStats() map[string]interface{} {
	if c.cache == nil {
		return map[string]interface{}{
			"enabled": false,
		}
	}

	stats := c.cache.ItemCount()
	return map[string]interface{}{
		"enabled": true,
		"items":   stats,
		"ttl":     c.cfg.CacheTTL.String(),
	}
}
