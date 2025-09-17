# 📚 API-MCP-Simbiosis API Reference

## 🔧 **Core Algorithms API**

### **QueryComposer**

```go
// Initialize
qc := algorithms.NewQueryComposer()

// Compose query with expansion and boosting
result := qc.ComposeQuery("monge alta performance")
// Returns: map[string]interface{}{
//   "tokens": []string{"monge", "alta", "performance", "desempenho", "rendimento"},
//   "fieldBoosts": map[string]float64{"filename": 2.0, "content": 1.0},
//   "filters": map[string]string{"file_pattern": "*.md"}
// }

// Add custom synonyms
qc.AddSynonym("performance", []string{"desempenho", "rendimento", "eficiencia"})

// Get statistics
stats := qc.GetStats()
```

### **CandidateAggregator**

```go
// Initialize with API credentials
ca := algorithms.NewCandidateAggregator(apiKey, baseURL)

// Set limit for performance
ca.SetLimit(100)

// Aggregate candidates from vault
candidates, err := ca.AggregateCandidates(query, limit)
// Returns: []algorithms.Candidate

// Get aggregation statistics
stats := ca.GetStats()
```

### **BM25-lite/TF-IDF**

```go
// Initialize
bt := algorithms.NewBM25TFIDF()

// Configure parameters
bt.SetK1(1.2)
bt.SetB(0.75)
bt.SetEpsilon(0.25)

// Rank candidates by relevance
rankedCandidates := bt.RankCandidates(candidates, query)
// Returns: []algorithms.Candidate (sorted by relevance score)

// Get algorithm statistics
stats := bt.GetStats()
```

### **MetadataBoost**

```go
// Initialize
mb := algorithms.NewMetadataBoost()

// Configure boost settings
config := algorithms.BoostConfig{
    PathPatterns:    map[string]float64{"docs/": 1.5, "notes/": 1.2},
    TagBoosts:       map[string]float64{"important": 2.0, "urgent": 1.8},
    FreshnessWeight: 0.3,
    PathWeight:      0.4,
    TagWeight:       0.3,
    MaxAge:          365 * 24 * time.Hour,
}
mb.SetBoostConfig(config)

// Apply metadata boosting
boostedCandidates := mb.BoostCandidates(candidates, query)

// Add custom path patterns
mb.AddPathPattern("docs/", 1.5)

// Add custom tag boosts
mb.AddTagBoost("important", 2.0)

// Get boost statistics
stats := mb.GetBoostStats(candidates)
```

### **Deduplicator**

```go
// Initialize
d := algorithms.NewDeduplicator()

// Configure similarity threshold
d.SetSimilarityThreshold(0.9)

// Set canonical strategy
d.SetCanonicalStrategy("freshest") // or "shortest", "longest"

// Remove duplicates
deduplicatedCandidates := d.DeduplicateCandidates(candidates)

// Analyze duplicates
duplicateInfo := d.AnalyzeDuplicates(candidates)

// Get deduplication statistics
stats := d.GetDeduplicationStats(originalCandidates, deduplicatedCandidates)
```

### **ContextAssembler**

```go
// Initialize
ctx := algorithms.NewContextAssembler()

// Configure token budget
ctx.SetMaxTokens(4000)
ctx.SetChunkSize(500)

// Assemble context within token budget
context := ctx.AssembleContext(candidates, query)
// Returns: algorithms.Context{
//   Content: string,
//   TokenCount: int,
//   BudgetUsed: float64,
//   Sources: []algorithms.Source
// }

// Get context statistics
stats := ctx.GetStats()
```

### **StreamingMerger**

```go
// Initialize
sm := algorithms.NewStreamingMerger()

// Configure streaming
sm.SetBufferSize(8192)
sm.SetDelimiter("\n")
sm.SetTimeout(30 * time.Second)

// Optimize for content type
sm.OptimizeStreaming("markdown")

// Merge streaming chunks
mergedContent := sm.MergeChunks(chunks)

// Get streaming statistics
stats := sm.GetStats()
```

---

## 🌐 **HTTP Client API**

### **HTTPClient**

```go
// Initialize with API credentials
client := client.NewHTTPClient(apiKey, baseURL)

// Configure timeouts
client.SetTimeout("short", 1*time.Second)
client.SetTimeout("medium", 5*time.Second)
client.SetTimeout("long", 30*time.Second)

// Configure retry settings
retryConfig := client.RetryConfig{
    MaxRetries:      3,
    RetryWaitTime:   1 * time.Second,
    MaxRetryWaitTime: 10 * time.Second,
    RetryConditions: []func(*resty.Response, error) bool{
        func(resp *resty.Response, err error) bool {
            return resp.StatusCode() >= 500 || err != nil
        },
    },
}
client.SetRetryConfig(retryConfig)

// Make HTTP requests
resp, err := client.Get("/vault/", "medium")
resp, err := client.Post("/vault/file.md", body, "long")
resp, err := client.Put("/vault/file.md", body, "long")
resp, err := client.Delete("/vault/file.md", "short")

// Get with retry
resp, err := client.GetWithRetry("/vault/", "medium")

// Stream large responses
streamResp, err := client.StreamGet("/vault/large-file.md", "long")

// Health check
health, err := client.HealthCheck()

// Get client statistics
stats := client.GetStats()

// Get circuit breaker state
state := client.GetCircuitBreakerState()
counts := client.GetCircuitBreakerCounts()
```

---

## 🔍 **Search Pipeline API**

### **Complete Search Pipeline**

```go
// Initialize all components
qc := algorithms.NewQueryComposer()
ca := algorithms.NewCandidateAggregator(apiKey, baseURL)
bt := algorithms.NewBM25TFIDF()
mb := algorithms.NewMetadataBoost()
d := algorithms.NewDeduplicator()
ctx := algorithms.NewContextAssembler()

// Configure algorithms
ca.SetLimit(100)
ctx.SetMaxTokens(4000)
ctx.SetChunkSize(500)

// Execute search pipeline
query := "monge alta performance"

// Step 1: Query composition
composedQuery := qc.ComposeQuery(query)

// Step 2: Candidate aggregation
candidates, err := ca.AggregateCandidates(query, 100)

// Step 3: BM25-TFIDF ranking
rankedCandidates := bt.RankCandidates(candidates, query)

// Step 4: Metadata boost
boostedCandidates := mb.BoostCandidates(rankedCandidates, query)

// Step 5: Deduplication
deduplicatedCandidates := d.DeduplicateCandidates(boostedCandidates)

// Step 6: Context assembly
context := ctx.AssembleContext(deduplicatedCandidates, query)

// Result contains:
// - context.Content: Final assembled context
// - context.TokenCount: Number of tokens used
// - context.BudgetUsed: Percentage of token budget used
// - context.Sources: List of sources used
```

---

## 📊 **Data Structures**

### **Candidate**

```go
type Candidate struct {
    FileInfo
    MatchType      string  `json:"match_type"`
    MatchScore     float64 `json:"match_score"`
    RelevanceScore float64 `json:"relevance_score"`
}
```

### **FileInfo**

```go
type FileInfo struct {
    Path     string                 `json:"path"`
    Name     string                 `json:"name"`
    Metadata map[string]interface{} `json:"metadata"`
    Content  string                 `json:"content,omitempty"`
    Size     int64                  `json:"size,omitempty"`
    Modified time.Time              `json:"modified,omitempty"`
}
```

### **Context**

```go
type Context struct {
    Content    string    `json:"content"`
    TokenCount int       `json:"token_count"`
    BudgetUsed float64   `json:"budget_used"`
    Sources    []Source  `json:"sources"`
}
```

### **Source**

```go
type Source struct {
    Path     string    `json:"path"`
    Modified time.Time `json:"modified"`
    Score    float64   `json:"score"`
}
```

---

## 🚨 **Error Handling**

### **Common Error Types**

```go
// HTTP Client Errors
type HTTPError struct {
    StatusCode int
    Message    string
    URL        string
}

// Algorithm Errors
type AlgorithmError struct {
    Algorithm string
    Operation string
    Message   string
}

// Configuration Errors
type ConfigError struct {
    Parameter string
    Value     interface{}
    Message   string
}
```

### **Error Handling Examples**

```go
// Handle HTTP errors
resp, err := client.Get("/vault/", "medium")
if err != nil {
    if httpErr, ok := err.(*client.HTTPError); ok {
        log.Printf("HTTP Error %d: %s", httpErr.StatusCode, httpErr.Message)
    } else {
        log.Printf("Network Error: %v", err)
    }
    return
}

// Handle algorithm errors
candidates, err := ca.AggregateCandidates(query, limit)
if err != nil {
    if algoErr, ok := err.(*algorithms.AlgorithmError); ok {
        log.Printf("Algorithm Error in %s: %s", algoErr.Algorithm, algoErr.Message)
    } else {
        log.Printf("Aggregation Error: %v", err)
    }
    return
}
```

---

## 📈 **Performance Optimization**

### **Benchmarking**

```go
// Run benchmarks
go test ./tests/... -bench=. -benchmem

// Benchmark specific algorithm
go test ./tests/... -bench=BenchmarkQueryComposer -benchmem

// Profile performance
go test ./tests/... -bench=. -cpuprofile=cpu.prof -memprofile=mem.prof
```

### **Performance Tuning**

```go
// Optimize QueryComposer
qc := algorithms.NewQueryComposer()
// Use cached synonyms for better performance

// Optimize CandidateAggregator
ca := algorithms.NewCandidateAggregator(apiKey, baseURL)
ca.SetLimit(50) // Reduce limit for faster processing

// Optimize BM25-TFIDF
bt := algorithms.NewBM25TFIDF()
bt.SetK1(1.2)  // Tune k1 parameter
bt.SetB(0.75)  // Tune b parameter

// Optimize ContextAssembler
ctx := algorithms.NewContextAssembler()
ctx.SetMaxTokens(2000) // Reduce token budget for faster processing
ctx.SetChunkSize(250)  // Smaller chunks for better performance
```

---

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Obsidian API Configuration
export OBSIDIAN_API_TOKEN="your-api-token"
export OBSIDIAN_API_PORT="27124"
export OBSIDIAN_VAULT_PATH="/path/to/vault"

# Performance Configuration
export MAX_CONCURRENT_REQUESTS="10"
export REQUEST_TIMEOUT="30s"
export CIRCUIT_BREAKER_THRESHOLD="5"
```

### **Configuration Files**

```yaml
# config.yaml
api:
  token: "your-api-token"
  port: 27124
  base_url: "https://127.0.0.1:27124"
  timeout:
    short: 1s
    medium: 5s
    long: 30s

algorithms:
  query_composer:
    synonyms:
      performance: ["desempenho", "rendimento", "eficiencia"]
  
  candidate_aggregator:
    limit: 100
    
  bm25_tfidf:
    k1: 1.2
    b: 0.75
    epsilon: 0.25
    
  metadata_boost:
    freshness_weight: 0.3
    path_weight: 0.4
    tag_weight: 0.3
    
  deduplicator:
    similarity_threshold: 0.9
    canonical_strategy: "freshest"
    
  context_assembler:
    max_tokens: 4000
    chunk_size: 500
    
  streaming_merger:
    buffer_size: 8192
    delimiter: "\n"
    timeout: 30s
```

---

**CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!**

---

*Generated by AI Assistant - API-MCP-Simbiosis Project*  
*API Reference v1.0.0 - Production Ready*
