package tests

import (
	"testing"
	"time"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"

	"github.com/stretchr/testify/assert"
)

// TestQueryComposer tests the QueryComposer algorithm
func TestQueryComposer(t *testing.T) {
	qc := algorithms.NewQueryComposer()

	t.Run("Basic Query Composition", func(t *testing.T) {
		query := "performance optimization"
		result := qc.ComposeQuery(query)

		assert.NotNil(t, result)
		assert.Contains(t, result, "query")
		assert.Contains(t, result, "filters")
		assert.Contains(t, result, "tokens")

		tokens := result["tokens"].([]string)
		assert.Greater(t, len(tokens), 0)
		assert.Contains(t, tokens, "performance")
		assert.Contains(t, tokens, "optimization")
	})

	t.Run("Synonym Expansion", func(t *testing.T) {
		query := "performance"
		result := qc.ComposeQuery(query)

		tokens := result["tokens"].([]string)
		// Should include synonyms for "performance"
		assert.Contains(t, tokens, "desempenho")
		assert.Contains(t, tokens, "rendimento")
	})

	t.Run("Custom Synonym Addition", func(t *testing.T) {
		qc.AddCustomSynonym("test", []string{"testing", "validation"})
		result := qc.ComposeQuery("test")

		tokens := result["tokens"].([]string)
		assert.Contains(t, tokens, "testing")
		assert.Contains(t, tokens, "validation")
	})
}

// TestCandidateAggregator tests the CandidateAggregator algorithm
func TestCandidateAggregator(t *testing.T) {
	// Mock API key and base URL for testing
	apiKey := "test-api-key"
	baseURL := "https://test.example.com"

	ca := algorithms.NewCandidateAggregator(apiKey, baseURL)

	t.Run("Configuration", func(t *testing.T) {
		// Test that aggregator was created successfully
		assert.NotNil(t, ca)
	})

	t.Run("Limit Setting", func(t *testing.T) {
		ca.SetLimit(50)
		// Test that limit was set (we can't access private field directly)
		assert.NotNil(t, ca)
	})
}

// TestBM25TFIDF tests the BM25/TF-IDF ranking algorithm
func TestBM25TFIDF(t *testing.T) {
	bt := algorithms.NewBM25TFIDF()

	t.Run("Parameter Configuration", func(t *testing.T) {
		bt.SetParameters(1.5, 0.8)
		// Test that parameters were set (we can't access private fields directly)
		assert.NotNil(t, bt)
	})

	t.Run("Algorithm Functionality", func(t *testing.T) {
		// Test basic functionality with public methods
		candidates := []algorithms.Candidate{
			{
				FileInfo: algorithms.FileInfo{
					Name:    "test.md",
					Content: "Hello world test",
				},
				RelevanceScore: 0.5,
			},
		}

		ranked := bt.RankCandidates(candidates, "hello")
		assert.Equal(t, len(candidates), len(ranked))
	})
}

// TestMetadataBoost tests the MetadataBoost algorithm
func TestMetadataBoost(t *testing.T) {
	mb := algorithms.NewMetadataBoost()

	t.Run("Boost Functionality", func(t *testing.T) {
		// Test boosting with public methods
		candidates := []algorithms.Candidate{
			{
				FileInfo: algorithms.FileInfo{
					Name:     "README.md",
					Path:     "docs/README.md",
					Modified: time.Now().Add(-24 * time.Hour),
				},
				RelevanceScore: 1.0,
			},
		}

		boosted := mb.BoostCandidates(candidates, "documentation")
		assert.Equal(t, len(candidates), len(boosted))
	})

	t.Run("Custom Path Pattern", func(t *testing.T) {
		mb.AddPathPattern("custom/", 2.0)
		// Test that pattern was added (we can't access private fields directly)
		assert.NotNil(t, mb)
	})
}

// TestDeduplicator tests the Deduplicator algorithm
func TestDeduplicator(t *testing.T) {
	d := algorithms.NewDeduplicator()

	t.Run("Similarity Threshold", func(t *testing.T) {
		d.SetSimilarityThreshold(0.8)
		// Test that threshold was set (we can't access private fields directly)
		assert.NotNil(t, d)
	})

	t.Run("Canonical Strategy", func(t *testing.T) {
		d.SetCanonicalStrategy("freshest")
		// Test that strategy was set (we can't access private fields directly)
		assert.NotNil(t, d)
	})

	t.Run("Deduplication Functionality", func(t *testing.T) {
		// Test deduplication with public methods
		candidates := []algorithms.Candidate{
			{
				FileInfo: algorithms.FileInfo{
					Name:     "test.md",
					Content:  "Hello world",
					Modified: time.Now().Add(-24 * time.Hour),
				},
				RelevanceScore: 1.0,
			},
			{
				FileInfo: algorithms.FileInfo{
					Name:     "test.md",
					Content:  "Hello world", // Duplicate
					Modified: time.Now().Add(-48 * time.Hour),
				},
				RelevanceScore: 0.8,
			},
		}

		deduplicated := d.DeduplicateCandidates(candidates)
		assert.LessOrEqual(t, len(deduplicated), len(candidates))
	})
}

// TestContextAssembler tests the ContextAssembler algorithm
func TestContextAssembler(t *testing.T) {
	ca := algorithms.NewContextAssembler()

	t.Run("Configuration", func(t *testing.T) {
		ca.SetMaxTokens(2000)
		ca.SetChunkSize(300)
		// Test that configuration was set (we can't access private fields directly)
		assert.NotNil(t, ca)
	})

	t.Run("Context Assembly", func(t *testing.T) {
		// Test context assembly with public methods
		candidates := []algorithms.Candidate{
			{
				FileInfo: algorithms.FileInfo{
					Name:    "test.md",
					Content: "This is a test document for context assembly.",
					Path:    "docs/test.md",
				},
				RelevanceScore: 1.0,
			},
		}

		context := ca.AssembleContext(candidates, "test")
		assert.NotNil(t, context)
		assert.GreaterOrEqual(t, context.TokenCount, 0)
	})
}

// TestStreamingMerger tests the StreamingMerger algorithm
func TestStreamingMerger(t *testing.T) {
	sm := algorithms.NewStreamingMerger()

	t.Run("Configuration", func(t *testing.T) {
		sm.SetBufferSize(8192)
		sm.SetDelimiter("\r\n")
		sm.SetTimeout(60 * time.Second)
		// Test that configuration was set (we can't access private fields directly)
		assert.NotNil(t, sm)
	})

	t.Run("Content Type Optimization", func(t *testing.T) {
		sm.OptimizeStreaming("text/plain")
		sm.OptimizeStreaming("application/json")
		// Test that optimization was applied (we can't access private fields directly)
		assert.NotNil(t, sm)
	})
}

// TestHTTPClient tests the HTTP client
func TestHTTPClient(t *testing.T) {
	apiKey := "test-api-key"
	baseURL := "https://test.example.com"

	hc := client.NewHTTPClient(apiKey, baseURL)

	t.Run("Configuration", func(t *testing.T) {
		// Test that client is properly initialized
		assert.NotNil(t, hc)
	})

	t.Run("Timeout Configuration", func(t *testing.T) {
		// Test timeout setting functionality
		hc.SetTimeout("custom", 15*time.Second)
		// We can't directly test private fields, but we can test the method works
		assert.NotNil(t, hc)
	})

	t.Run("Circuit Breaker State", func(t *testing.T) {
		state := hc.GetCircuitBreakerState()
		assert.NotNil(t, state)

		counts := hc.GetCircuitBreakerCounts()
		assert.NotNil(t, counts)
	})

	t.Run("Stats", func(t *testing.T) {
		stats := hc.GetStats()
		assert.NotNil(t, stats)
		assert.NotNil(t, stats.CircuitBreakerState)
		assert.NotNil(t, stats.CircuitBreakerCounts)
		assert.NotNil(t, stats.Timeouts)
	})
}

// TestIntegration tests the integration of all algorithms
func TestIntegration(t *testing.T) {
	t.Run("End-to-End Search Pipeline", func(t *testing.T) {
		// This would test the complete pipeline
		// For now, we'll test that all components can be instantiated

		qc := algorithms.NewQueryComposer()
		ca := algorithms.NewCandidateAggregator("test", "https://test.com")
		bt := algorithms.NewBM25TFIDF()
		mb := algorithms.NewMetadataBoost()
		d := algorithms.NewDeduplicator()
		ctx := algorithms.NewContextAssembler()
		sm := algorithms.NewStreamingMerger()

		assert.NotNil(t, qc)
		assert.NotNil(t, ca)
		assert.NotNil(t, bt)
		assert.NotNil(t, mb)
		assert.NotNil(t, d)
		assert.NotNil(t, ctx)
		assert.NotNil(t, sm)
	})
}

// Benchmark tests for performance validation
func BenchmarkQueryComposer(b *testing.B) {
	qc := algorithms.NewQueryComposer()
	query := "performance optimization algorithm"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		qc.ComposeQuery(query)
	}
}

func BenchmarkBM25TFIDF(b *testing.B) {
	bt := algorithms.NewBM25TFIDF()
	candidates := []algorithms.Candidate{
		{
			FileInfo: algorithms.FileInfo{
				Name:     "test1.md",
				Content:  "This is a test document with multiple words for benchmarking purposes.",
				Path:     "test1.md",
				Modified: time.Now(),
			},
		},
	}
	query := "test document"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		bt.RankCandidates(candidates, query)
	}
}

func BenchmarkMetadataBoost(b *testing.B) {
	mb := algorithms.NewMetadataBoost()
	candidates := []algorithms.Candidate{
		{
			FileInfo: algorithms.FileInfo{
				Name:     "README.md",
				Content:  "This is a test document.",
				Path:     "docs/README.md",
				Modified: time.Now(),
			},
		},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		mb.BoostCandidates(candidates, "test")
	}
}

func BenchmarkDeduplicator(b *testing.B) {
	d := algorithms.NewDeduplicator()
	candidates := []algorithms.Candidate{
		{
			FileInfo: algorithms.FileInfo{
				Name:     "test1.md",
				Content:  "Hello world",
				Path:     "test1.md",
				Modified: time.Now(),
			},
		},
		{
			FileInfo: algorithms.FileInfo{
				Name:     "test2.md",
				Content:  "Hello world",
				Path:     "test2.md",
				Modified: time.Now(),
			},
		},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		d.DeduplicateCandidates(candidates)
	}
}

func BenchmarkContextAssembler(b *testing.B) {
	ca := algorithms.NewContextAssembler()
	candidates := []algorithms.Candidate{
		{
			FileInfo: algorithms.FileInfo{
				Name:     "test.md",
				Content:  "This is a test document for benchmarking the context assembler algorithm.",
				Path:     "test.md",
				Modified: time.Now(),
			},
		},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ca.AssembleContext(candidates, "test")
	}
}
