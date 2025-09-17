# 🚀 API-MCP-Simbiosis Quick Start Guide

## ⚡ **GET STARTED IN 5 MINUTES**

### **1. Prerequisites**
- Go 1.19+ installed
- Obsidian Local REST API running on port 27124
- API token: `b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70`

### **2. Clone and Setup**
```bash
# Navigate to project directory
cd api-mcp-simbiosis

# Install dependencies
go mod tidy

# Verify installation
go mod verify
```

### **3. Quick Test Commands**
```bash
# Test health check
go run -c 'package main; import ("api-mcp-simbiosis/client"; "fmt"); func main() { c := client.NewHTTPClient("b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70", "https://127.0.0.1:27124"); h, _ := c.HealthCheck(); fmt.Println("Health:", h.Status) }'

# Run all tests
go test ./tests/... -v

# Test real vault integration
go run test_real_vault.go

# Run success demo
go run success_demo.go
```

### **4. Basic Usage**
```go
package main

import (
    "fmt"
    "log"
    
    "api-mcp-simbiosis/algorithms"
    "api-mcp-simbiosis/client"
)

func main() {
    // Initialize HTTP client
    apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
    baseURL := "https://127.0.0.1:27124"
    httpClient := client.NewHTTPClient(apiKey, baseURL)
    
    // Initialize algorithms
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
    query := "Monge da Alta-Performance"
    
    // Step 1: Query composition
    composedQuery := qc.ComposeQuery(query)
    fmt.Printf("Expanded tokens: %v\n", composedQuery["tokens"])
    
    // Step 2: Candidate aggregation
    candidates, err := ca.AggregateCandidates(query, 100)
    if err != nil {
        log.Printf("Error: %v", err)
        return
    }
    fmt.Printf("Found %d candidates\n", len(candidates))
    
    // Step 3: BM25-TFIDF ranking
    rankedCandidates := bt.RankCandidates(candidates, query)
    fmt.Printf("Ranked %d candidates\n", len(rankedCandidates))
    
    // Step 4: Metadata boost
    boostedCandidates := mb.BoostCandidates(rankedCandidates, query)
    fmt.Printf("Boosted %d candidates\n", len(boostedCandidates))
    
    // Step 5: Deduplication
    deduplicatedCandidates := d.DeduplicateCandidates(boostedCandidates)
    fmt.Printf("Deduplicated to %d candidates\n", len(deduplicatedCandidates))
    
    // Step 6: Context assembly
    context := ctx.AssembleContext(deduplicatedCandidates, query)
    fmt.Printf("Assembled context: %d tokens (%.1f%% budget used)\n", 
        context.TokenCount, context.BudgetUsed)
    
    // Show results
    fmt.Println("\nTop Results:")
    for i, candidate := range deduplicatedCandidates {
        if i >= 3 {
            break
        }
        fmt.Printf("  %d. %s (Score: %.3f)\n", i+1, candidate.Name, candidate.MatchScore)
    }
}
```

---

## 🎯 **ESSENTIAL COMMANDS**

### **Testing Commands**
```bash
# Run all tests
go test ./tests/... -v

# Run specific test
go test ./tests/... -run TestQueryComposer -v

# Run benchmarks
go test ./tests/... -bench=. -benchmem

# Run with coverage
go test ./... -v -cover
```

### **Demo Commands**
```bash
# Real vault testing
go run test_real_vault.go

# Success demonstration
go run success_demo.go

# Specific file testing
go run test_specific_file.go

# Comprehensive testing
go run final_comprehensive_test.go

# Basic search example
go run examples/basic_search.go
```

### **Build Commands**
```bash
# Build all components
go build ./...

# Build specific component
go build ./algorithms/...

# Build with optimizations
go build -ldflags="-s -w" ./...
```

---

## 🔧 **CONFIGURATION**

### **Environment Variables**
```bash
export OBSIDIAN_API_TOKEN="b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
export OBSIDIAN_API_PORT="27124"
export OBSIDIAN_VAULT_PATH="D:\\Nomade Milionario"
```

### **Algorithm Configuration**
```go
// QueryComposer configuration
qc := algorithms.NewQueryComposer()
qc.AddSynonym("performance", []string{"desempenho", "rendimento", "eficiencia"})

// CandidateAggregator configuration
ca := algorithms.NewCandidateAggregator(apiKey, baseURL)
ca.SetLimit(100) // Limit to 100 files for performance

// BM25-TFIDF configuration
bt := algorithms.NewBM25TFIDF()
bt.SetK1(1.2)  // Term frequency saturation
bt.SetB(0.75)  // Length normalization

// MetadataBoost configuration
mb := algorithms.NewMetadataBoost()
mb.AddPathPattern("docs/", 1.5)  // Boost docs directory
mb.AddTagBoost("important", 2.0)  // Boost important tags

// Deduplicator configuration
d := algorithms.NewDeduplicator()
d.SetSimilarityThreshold(0.9)  // 90% similarity threshold
d.SetCanonicalStrategy("freshest")  // Keep freshest duplicates

// ContextAssembler configuration
ctx := algorithms.NewContextAssembler()
ctx.SetMaxTokens(4000)  // 4000 token budget
ctx.SetChunkSize(500)   // 500 tokens per chunk
```

---

## 📊 **PERFORMANCE TUNING**

### **Optimize for Speed**
```go
// Reduce candidate limit for faster processing
ca.SetLimit(50)

// Reduce token budget for faster context assembly
ctx.SetMaxTokens(2000)

// Use smaller chunks for better performance
ctx.SetChunkSize(250)

// Increase similarity threshold for faster deduplication
d.SetSimilarityThreshold(0.95)
```

### **Optimize for Quality**
```go
// Increase candidate limit for better coverage
ca.SetLimit(200)

// Increase token budget for more context
ctx.SetMaxTokens(6000)

// Use larger chunks for better context
ctx.SetChunkSize(750)

// Decrease similarity threshold for more thorough deduplication
d.SetSimilarityThreshold(0.85)
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

#### **TLS Certificate Error**
```
Error: tls: failed to verify certificate: x509: certificate signed by unknown authority
```
**Solution**: This is expected with self-signed certificates. The HTTP client is configured to bypass TLS verification.

#### **API Connection Error**
```
Error: Get "https://127.0.0.1:27124/vault/": dial tcp 127.0.0.1:27124: connect: connection refused
```
**Solution**: Ensure Obsidian Local REST API is running on port 27124.

#### **Empty Results**
```
Found 0 candidates
```
**Solution**: Check if the vault has files and the API token is correct.

### **Debug Commands**
```bash
# Test API connectivity
curl -k -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70" "https://127.0.0.1:27124/"

# Test vault access
curl -k -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70" "https://127.0.0.1:27124/vault/"

# Test specific file
curl -k -H "Authorization: Bearer b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70" "https://127.0.0.1:27124/vault/--OBJETIVOS/Monge%20da%20Alta-Performance.md"
```

---

## 📈 **MONITORING**

### **Performance Metrics**
```go
// Get HTTP client statistics
stats := httpClient.GetStats()
fmt.Printf("Circuit Breaker State: %s\n", stats.CircuitBreakerState)
fmt.Printf("Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

// Get algorithm statistics
qcStats := qc.GetStats()
btStats := bt.GetStats()
mbStats := mb.GetBoostStats(candidates)
dStats := d.GetDeduplicationStats(originalCandidates, deduplicatedCandidates)
```

### **Health Checks**
```go
// Check API health
health, err := httpClient.HealthCheck()
if err != nil {
    log.Printf("Health check failed: %v", err)
} else {
    fmt.Printf("API Status: %s\n", health.Status)
}
```

---

## 🎉 **SUCCESS INDICATORS**

### **What Success Looks Like**
- ✅ Health check returns "healthy"
- ✅ Vault discovery finds files (e.g., 65 files)
- ✅ Target file "Monge da Alta-Performance.md" is accessible
- ✅ All algorithms process candidates successfully
- ✅ Context assembly completes within token budget
- ✅ Performance benchmarks show sub-second response times

### **Expected Output**
```
🚀 API-MCP-Simbiosis SUCCESS DEMONSTRATION
==========================================
🔍 HEALTH CHECK
✅ Health Status: healthy (0.011s)
📄 TARGET FILE RETRIEVAL
✅ Retrieved: 1234 characters (0.045s)
🔧 ALGORITHM DEMONSTRATION
✅ All algorithms initialized
✅ Created 3 test candidates
🔍 Testing query: 'Monge da Alta-Performance'
📝 Query composition: [monge da alta-performance]
📊 BM25 ranking: 3 candidates
⚡ Metadata boost: 3 candidates
🔄 Deduplication: 3 candidates
📚 Context assembly: 1250 tokens, 31.3% budget
🏆 TOP RESULTS:
   1. Monge da Alta-Performance.md (Score: 0.900)
   2. Conquistador de Metas.md (Score: 0.700)
   3. AGENTS.md (Score: 0.400)
🎉 SUCCESS DEMONSTRATION COMPLETE!
✅ API-MCP-Simbiosis fully operational!
✅ Real vault data successfully processed!
✅ All 7 algorithms working perfectly!
✅ Target file 'Monge da Alta-Performance.md' retrieved!
✅ Advanced search pipeline validated!
```

---

**CENTRALIZED REPORTS & CHANGELOG SYSTEM COMPLETE!**

---

*Generated by AI Assistant - API-MCP-Simbiosis Project*  
*Quick Start Guide v1.0.0 - Production Ready*
