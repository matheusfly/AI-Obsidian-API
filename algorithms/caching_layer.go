package algorithms

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// CachingLayer provides intelligent caching for vault operations
// to optimize repeated calls and reduce API load
type CachingLayer struct {
	cacheDir   string
	cacheFiles map[string]string
	ttl        time.Duration
	mutex      sync.RWMutex
	stats      CacheStats
}

// CacheStats tracks caching performance metrics
type CacheStats struct {
	Hits        int       `json:"hits"`
	Misses      int       `json:"misses"`
	Evictions   int       `json:"evictions"`
	TotalSize   int64     `json:"total_size"`
	LastCleanup time.Time `json:"last_cleanup"`
	HitRate     float64   `json:"hit_rate"`
}

// CacheEntry represents a cached item with metadata
type CacheEntry struct {
	Data      interface{}   `json:"data"`
	Timestamp time.Time     `json:"timestamp"`
	TTL       time.Duration `json:"ttl"`
	Key       string        `json:"key"`
	Size      int64         `json:"size"`
}

// NewCachingLayer creates a new CachingLayer instance
func NewCachingLayer(cacheDir string) *CachingLayer {
	if cacheDir == "" {
		cacheDir = "./cache"
	}

	// Ensure cache directory exists
	os.MkdirAll(cacheDir, 0755)

	return &CachingLayer{
		cacheDir:   cacheDir,
		cacheFiles: make(map[string]string),
		ttl:        5 * time.Minute,
		stats:      CacheStats{},
	}
}

// Get retrieves data from cache if valid, otherwise calls fetchFunc
func (cl *CachingLayer) Get(key string, fetchFunc func() (interface{}, error)) (interface{}, error) {
	cl.mutex.Lock()
	defer cl.mutex.Unlock()

	// Check if we have a cached entry
	if entry, exists := cl.getCachedEntry(key); exists && cl.isValid(entry) {
		cl.stats.Hits++
		cl.updateHitRate()
		return entry.Data, nil
	}

	// Cache miss - fetch fresh data
	cl.stats.Misses++
	cl.updateHitRate()

	data, err := fetchFunc()
	if err != nil {
		return nil, fmt.Errorf("fetch function failed: %w", err)
	}

	// Cache the new data
	entry := CacheEntry{
		Data:      data,
		Timestamp: time.Now(),
		TTL:       cl.ttl,
		Key:       key,
		Size:      cl.calculateSize(data),
	}

	if err := cl.saveCachedEntry(key, entry); err != nil {
		// Log error but don't fail the operation
		fmt.Printf("Warning: failed to cache data for key %s: %v\n", key, err)
	}

	return data, nil
}

// GetWithTTL retrieves data with custom TTL
func (cl *CachingLayer) GetWithTTL(key string, ttl time.Duration, fetchFunc func() (interface{}, error)) (interface{}, error) {
	originalTTL := cl.ttl
	cl.SetTTL(ttl)
	defer cl.SetTTL(originalTTL)

	return cl.Get(key, fetchFunc)
}

// Set manually stores data in cache
func (cl *CachingLayer) Set(key string, data interface{}) error {
	cl.mutex.Lock()
	defer cl.mutex.Unlock()

	entry := CacheEntry{
		Data:      data,
		Timestamp: time.Now(),
		TTL:       cl.ttl,
		Key:       key,
		Size:      cl.calculateSize(data),
	}

	return cl.saveCachedEntry(key, entry)
}

// SetWithTTL stores data with custom TTL
func (cl *CachingLayer) SetWithTTL(key string, data interface{}, ttl time.Duration) error {
	cl.mutex.Lock()
	defer cl.mutex.Unlock()

	entry := CacheEntry{
		Data:      data,
		Timestamp: time.Now(),
		TTL:       ttl,
		Key:       key,
		Size:      cl.calculateSize(data),
	}

	return cl.saveCachedEntry(key, entry)
}

// Delete removes data from cache
func (cl *CachingLayer) Delete(key string) error {
	cl.mutex.Lock()
	defer cl.mutex.Unlock()

	cacheFile := cl.getCacheFilePath(key)
	if err := os.Remove(cacheFile); err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("failed to delete cache file: %w", err)
	}

	delete(cl.cacheFiles, key)
	return nil
}

// Clear removes all cached data
func (cl *CachingLayer) Clear() error {
	cl.mutex.Lock()
	defer cl.mutex.Unlock()

	// Remove all cache files
	files, err := filepath.Glob(filepath.Join(cl.cacheDir, "*.cache"))
	if err != nil {
		return fmt.Errorf("failed to list cache files: %w", err)
	}

	for _, file := range files {
		if err := os.Remove(file); err != nil {
			fmt.Printf("Warning: failed to remove cache file %s: %v\n", file, err)
		}
	}

	cl.cacheFiles = make(map[string]string)
	cl.stats = CacheStats{}
	return nil
}

// Cleanup removes expired cache entries
func (cl *CachingLayer) Cleanup() error {
	cl.mutex.Lock()
	defer cl.mutex.Unlock()

	now := time.Now()
	evicted := 0

	files, err := filepath.Glob(filepath.Join(cl.cacheDir, "*.cache"))
	if err != nil {
		return fmt.Errorf("failed to list cache files: %w", err)
	}

	for _, file := range files {
		entry, err := cl.loadCachedEntry(file)
		if err != nil {
			// Remove corrupted cache files
			os.Remove(file)
			evicted++
			continue
		}

		if !cl.isValid(entry) {
			os.Remove(file)
			evicted++
		}
	}

	cl.stats.Evictions += evicted
	cl.stats.LastCleanup = now

	return nil
}

// GetStats returns cache statistics
func (cl *CachingLayer) GetStats() CacheStats {
	cl.mutex.RLock()
	defer cl.mutex.RUnlock()

	// Calculate total cache size
	totalSize := int64(0)
	files, _ := filepath.Glob(filepath.Join(cl.cacheDir, "*.cache"))
	for _, file := range files {
		if info, err := os.Stat(file); err == nil {
			totalSize += info.Size()
		}
	}

	cl.stats.TotalSize = totalSize
	return cl.stats
}

// SetTTL sets the default cache TTL
func (cl *CachingLayer) SetTTL(ttl time.Duration) {
	cl.mutex.Lock()
	defer cl.mutex.Unlock()
	cl.ttl = ttl
}

// GetTTL returns the current TTL
func (cl *CachingLayer) GetTTL() time.Duration {
	cl.mutex.RLock()
	defer cl.mutex.RUnlock()
	return cl.ttl
}

// IsValid checks if a cache entry is still valid
func (cl *CachingLayer) IsValid(key string) bool {
	cl.mutex.RLock()
	defer cl.mutex.RUnlock()

	entry, exists := cl.getCachedEntry(key)
	return exists && cl.isValid(entry)
}

// GetSize returns the size of cached data for a key
func (cl *CachingLayer) GetSize(key string) int64 {
	cl.mutex.RLock()
	defer cl.mutex.RUnlock()

	entry, exists := cl.getCachedEntry(key)
	if !exists {
		return 0
	}
	return entry.Size
}

// ListKeys returns all cached keys
func (cl *CachingLayer) ListKeys() []string {
	cl.mutex.RLock()
	defer cl.mutex.RUnlock()

	keys := make([]string, 0, len(cl.cacheFiles))
	for key := range cl.cacheFiles {
		keys = append(keys, key)
	}
	return keys
}

// getCachedEntry loads a cached entry from disk
func (cl *CachingLayer) getCachedEntry(key string) (CacheEntry, bool) {
	cacheFile := cl.getCacheFilePath(key)

	// Check if file exists
	if _, err := os.Stat(cacheFile); os.IsNotExist(err) {
		return CacheEntry{}, false
	}

	entry, err := cl.loadCachedEntry(cacheFile)
	if err != nil {
		return CacheEntry{}, false
	}

	return entry, true
}

// loadCachedEntry loads a cache entry from file
func (cl *CachingLayer) loadCachedEntry(filePath string) (CacheEntry, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return CacheEntry{}, err
	}

	var entry CacheEntry
	if err := json.Unmarshal(data, &entry); err != nil {
		return CacheEntry{}, err
	}

	return entry, nil
}

// saveCachedEntry saves a cache entry to disk
func (cl *CachingLayer) saveCachedEntry(key string, entry CacheEntry) error {
	cacheFile := cl.getCacheFilePath(key)

	data, err := json.Marshal(entry)
	if err != nil {
		return fmt.Errorf("failed to marshal cache entry: %w", err)
	}

	if err := os.WriteFile(cacheFile, data, 0644); err != nil {
		return fmt.Errorf("failed to write cache file: %w", err)
	}

	cl.cacheFiles[key] = cacheFile
	return nil
}

// getCacheFilePath returns the file path for a cache key
func (cl *CachingLayer) getCacheFilePath(key string) string {
	// Sanitize key for filename
	safeKey := filepath.Base(key)
	if safeKey == "." || safeKey == "" {
		safeKey = "default"
	}
	return filepath.Join(cl.cacheDir, safeKey+".cache")
}

// isValid checks if a cache entry is still valid
func (cl *CachingLayer) isValid(entry CacheEntry) bool {
	return time.Since(entry.Timestamp) < entry.TTL
}

// calculateSize estimates the size of data in bytes
func (cl *CachingLayer) calculateSize(data interface{}) int64 {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return 0
	}
	return int64(len(jsonData))
}

// updateHitRate updates the hit rate statistic
func (cl *CachingLayer) updateHitRate() {
	total := cl.stats.Hits + cl.stats.Misses
	if total > 0 {
		cl.stats.HitRate = float64(cl.stats.Hits) / float64(total)
	}
}

// GetCacheDir returns the cache directory path
func (cl *CachingLayer) GetCacheDir() string {
	return cl.cacheDir
}

// SetCacheDir sets a new cache directory
func (cl *CachingLayer) SetCacheDir(dir string) error {
	cl.mutex.Lock()
	defer cl.mutex.Unlock()

	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create cache directory: %w", err)
	}

	cl.cacheDir = dir
	return nil
}

// AutoCleanup starts automatic cleanup in a goroutine
func (cl *CachingLayer) AutoCleanup(interval time.Duration) {
	go func() {
		ticker := time.NewTicker(interval)
		defer ticker.Stop()

		for range ticker.C {
			if err := cl.Cleanup(); err != nil {
				fmt.Printf("Warning: cache cleanup failed: %v\n", err)
			}
		}
	}()
}
