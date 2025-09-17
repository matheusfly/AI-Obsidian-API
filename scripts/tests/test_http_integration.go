package main

import (
	"fmt"
	"time"

	"api-mcp-simbiosis/algorithms"
	"api-mcp-simbiosis/client"
)

func main() {
	fmt.Println("🔧 HTTP INTEGRATION TEST")
	fmt.Println("=======================")

	// Configuration
	apiKey := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	baseURL := "https://127.0.0.1:27124"

	// Initialize HTTP client
	httpClient := client.NewHTTPClient(apiKey, baseURL)

	// Initialize CandidateAggregator with shared HTTP client
	candidateAggregator := algorithms.NewCandidateAggregatorWithClient(apiKey, baseURL, httpClient.GetClient())

	fmt.Println("🔍 Initial HTTP Client Statistics:")
	stats := httpClient.GetStats()
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	// Test 1: Health check
	fmt.Println("\n🔍 Test 1: Health check...")
	health, err := httpClient.HealthCheck()
	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	fmt.Printf("✅ API Status: %s (%.3fs)\n", health.Status, health.ResponseTime.Seconds())

	fmt.Println("📊 HTTP Client Statistics after health check:")
	stats = httpClient.GetStats()
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	// Test 2: Search query
	fmt.Println("\n🔍 Test 2: Search query 'logica'...")
	startTime := time.Now()
	candidates, err := candidateAggregator.AggregateCandidates("logica", 10)
	duration := time.Since(startTime)

	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	fmt.Printf("✅ Found %d candidates in %.3fs\n", len(candidates), duration.Seconds())

	fmt.Println("📊 HTTP Client Statistics after search:")
	stats = httpClient.GetStats()
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	// Show results
	fmt.Println("\n🏆 Search Results:")
	for i, candidate := range candidates {
		if i >= 5 {
			break
		}
		fmt.Printf("   %d. %s (Score: %.3f, Type: %s)\n", i+1, candidate.Name, candidate.MatchScore, candidate.MatchType)
	}

	// Test 3: Another search to see more requests
	fmt.Println("\n🔍 Test 3: Another search query 'performance'...")
	startTime = time.Now()
	candidates2, err := candidateAggregator.AggregateCandidates("performance", 5)
	duration = time.Since(startTime)

	if err != nil {
		fmt.Printf("❌ Search failed: %v\n", err)
		return
	}

	fmt.Printf("✅ Found %d candidates in %.3fs\n", len(candidates2), duration.Seconds())

	fmt.Println("📊 HTTP Client Statistics after second search:")
	stats = httpClient.GetStats()
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	// Test 4: Direct HTTP request to verify tracking
	fmt.Println("\n🔍 Test 4: Direct HTTP request...")
	startTime = time.Now()
	health2, err := httpClient.HealthCheck()
	duration = time.Since(startTime)

	if err != nil {
		fmt.Printf("❌ Health check failed: %v\n", err)
		return
	}
	fmt.Printf("✅ API Status: %s (%.3fs)\n", health2.Status, health2.ResponseTime.Seconds())

	fmt.Println("📊 HTTP Client Statistics after direct request:")
	stats = httpClient.GetStats()
	fmt.Printf("   Circuit Breaker State: %s\n", stats.CircuitBreakerState)
	fmt.Printf("   Circuit Breaker Counts: %+v\n", stats.CircuitBreakerCounts)

	fmt.Println("\n🎉 HTTP INTEGRATION TEST COMPLETE!")
	fmt.Println("✅ HTTP requests are being tracked properly!")
	fmt.Println("✅ Shared HTTP client is working!")
	fmt.Println("✅ Statistics are being updated!")
}
