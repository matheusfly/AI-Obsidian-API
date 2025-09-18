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
	"time"
)

// SemanticSearchEngine provides AI-powered semantic search using DeepSeek-R1:8B
type SemanticSearchEngine struct {
	baseURL      string
	token        string
	ollamaHost   string
	ollamaModel  string
	client       *http.Client
	ollamaClient *http.Client
}

// NewSemanticSearchEngine creates a new semantic search engine
func NewSemanticSearchEngine(baseURL, token, ollamaHost, ollamaModel string) *SemanticSearchEngine {
	return &SemanticSearchEngine{
		baseURL:     baseURL,
		token:       token,
		ollamaHost:  ollamaHost,
		ollamaModel: ollamaModel,
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
		ollamaClient: &http.Client{
			Timeout: 60 * time.Second,
		},
	}
}

// SemanticSearchResult represents a semantic search result
type SemanticSearchResult struct {
	File      string    `json:"file"`
	Score     float64   `json:"score"`
	Snippet   string    `json:"snippet"`
	Relevance string    `json:"relevance"`
	Embedding []float64 `json:"embedding,omitempty"`
	Context   string    `json:"context"`
}

// SemanticSearch performs AI-powered semantic search
func (sse *SemanticSearchEngine) SemanticSearch(query string, maxResults int) ([]SemanticSearchResult, error) {
	fmt.Printf("🧠 Performing semantic search for: '%s'\n", query)

	// Step 1: Generate query embedding using DeepSeek-R1:8B
	queryEmbedding, err := sse.generateEmbedding(query)
	if err != nil {
		fmt.Printf("⚠️ Failed to generate query embedding: %v\n", err)
		// Fallback to traditional search
		return sse.fallbackSearch(query, maxResults)
	}

	// Step 2: Get all files from vault
	files, err := sse.getAllFiles()
	if err != nil {
		return nil, fmt.Errorf("failed to get files: %v", err)
	}

	// Step 3: Process files and calculate semantic similarity
	var results []SemanticSearchResult
	processedCount := 0

	for _, file := range files {
		if processedCount >= maxResults*3 { // Process more files than needed for better results
			break
		}

		if strings.HasSuffix(strings.ToLower(file), ".md") {
			content, err := sse.readFileContent(file)
			if err != nil {
				continue
			}

			// Generate content embedding
			contentEmbedding, err := sse.generateEmbedding(content[:min(len(content), 1000)]) // Limit content for embedding
			if err != nil {
				continue
			}

			// Calculate semantic similarity
			similarity := sse.calculateSimilarity(queryEmbedding, contentEmbedding)

			if similarity > 0.3 { // Threshold for relevance
				snippet := sse.extractRelevantSnippet(content, query)
				relevance := sse.determineRelevance(similarity)

				results = append(results, SemanticSearchResult{
					File:      file,
					Score:     similarity,
					Snippet:   snippet,
					Relevance: relevance,
					Embedding: contentEmbedding,
					Context:   sse.extractContext(content, query),
				})
				processedCount++
			}
		}
	}

	// Step 4: Sort by similarity score and return top results
	sse.sortResultsByScore(results)
	if len(results) > maxResults {
		results = results[:maxResults]
	}

	fmt.Printf("✅ Semantic search completed: %d results found\n", len(results))
	return results, nil
}

// generateEmbedding generates embedding using DeepSeek-R1:8B via Ollama
func (sse *SemanticSearchEngine) generateEmbedding(text string) ([]float64, error) {
	// Use Ollama's embedding endpoint
	requestBody := map[string]interface{}{
		"model":  sse.ollamaModel,
		"prompt": text,
	}

	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		return nil, err
	}

	resp, err := sse.ollamaClient.Post(
		fmt.Sprintf("%s/api/embeddings", sse.ollamaHost),
		"application/json",
		strings.NewReader(string(jsonBody)),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ollama embedding request failed with status %d", resp.StatusCode)
	}

	var response struct {
		Embedding []float64 `json:"embedding"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	return response.Embedding, nil
}

// calculateSimilarity calculates cosine similarity between two embeddings
func (sse *SemanticSearchEngine) calculateSimilarity(embedding1, embedding2 []float64) float64 {
	if len(embedding1) != len(embedding2) {
		return 0.0
	}

	var dotProduct, norm1, norm2 float64

	for i := 0; i < len(embedding1); i++ {
		dotProduct += embedding1[i] * embedding2[i]
		norm1 += embedding1[i] * embedding1[i]
		norm2 += embedding2[i] * embedding2[i]
	}

	if norm1 == 0 || norm2 == 0 {
		return 0.0
	}

	return dotProduct / (math.Sqrt(norm1) * math.Sqrt(norm2))
}

// extractRelevantSnippet extracts the most relevant snippet from content
func (sse *SemanticSearchEngine) extractRelevantSnippet(content, query string) string {
	// Find the best sentence containing query terms
	sentences := strings.Split(content, ".")
	queryLower := strings.ToLower(query)
	queryWords := strings.Fields(queryLower)

	bestSentence := ""
	bestScore := 0

	for _, sentence := range sentences {
		sentenceLower := strings.ToLower(sentence)
		score := 0

		for _, word := range queryWords {
			if strings.Contains(sentenceLower, word) {
				score++
			}
		}

		if score > bestScore {
			bestScore = score
			bestSentence = sentence
		}
	}

	if bestSentence == "" {
		// Fallback to first 200 characters
		if len(content) > 200 {
			return content[:200] + "..."
		}
		return content
	}

	return strings.TrimSpace(bestSentence)
}

// extractContext extracts broader context around the query
func (sse *SemanticSearchEngine) extractContext(content, query string) string {
	queryLower := strings.ToLower(query)
	contentLower := strings.ToLower(content)

	index := strings.Index(contentLower, queryLower)
	if index == -1 {
		return "Context not found"
	}

	start := max(0, index-100)
	end := min(len(content), index+len(query)+100)

	context := content[start:end]
	if start > 0 {
		context = "..." + context
	}
	if end < len(content) {
		context = context + "..."
	}

	return context
}

// determineRelevance determines relevance level based on similarity score
func (sse *SemanticSearchEngine) determineRelevance(score float64) string {
	switch {
	case score >= 0.8:
		return "Very High"
	case score >= 0.6:
		return "High"
	case score >= 0.4:
		return "Medium"
	case score >= 0.2:
		return "Low"
	default:
		return "Very Low"
	}
}

// sortResultsByScore sorts results by similarity score (descending)
func (sse *SemanticSearchEngine) sortResultsByScore(results []SemanticSearchResult) {
	for i := 0; i < len(results)-1; i++ {
		for j := i + 1; j < len(results); j++ {
			if results[i].Score < results[j].Score {
				results[i], results[j] = results[j], results[i]
			}
		}
	}
}

// getAllFiles gets all files from the vault recursively
func (sse *SemanticSearchEngine) getAllFiles() ([]string, error) {
	var allFiles []string

	// Get root files
	resp, err := sse.makeRequest("GET", "/vault/", nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var response struct {
		Files []string `json:"files"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	// Process files recursively
	for _, file := range response.Files {
		if strings.HasSuffix(file, "/") {
			// Directory - get subfiles
			subFiles, err := sse.getDirectoryFiles(file)
			if err == nil {
				allFiles = append(allFiles, subFiles...)
			}
		} else {
			allFiles = append(allFiles, file)
		}
	}

	return allFiles, nil
}

// getDirectoryFiles gets files from a specific directory
func (sse *SemanticSearchEngine) getDirectoryFiles(dirPath string) ([]string, error) {
	resp, err := sse.makeRequest("GET", "/vault/"+url.PathEscape(dirPath), nil)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var response struct {
		Files []string `json:"files"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}

	var files []string
	for _, file := range response.Files {
		if strings.HasSuffix(file, "/") {
			// Subdirectory - recursively get files
			subFiles, err := sse.getDirectoryFiles(dirPath + file)
			if err == nil {
				files = append(files, subFiles...)
			}
		} else {
			files = append(files, dirPath+file)
		}
	}

	return files, nil
}

// readFileContent reads content of a specific file
func (sse *SemanticSearchEngine) readFileContent(filename string) (string, error) {
	resp, err := sse.makeRequest("GET", "/vault/"+url.PathEscape(filename), nil)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("failed to read file '%s': HTTP %d", filename, resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	return string(body), nil
}

// makeRequest makes an authenticated request to Obsidian API
func (sse *SemanticSearchEngine) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, sse.baseURL+path, body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+sse.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	return sse.client.Do(req)
}

// fallbackSearch provides fallback to traditional search when AI fails
func (sse *SemanticSearchEngine) fallbackSearch(query string, maxResults int) ([]SemanticSearchResult, error) {
	fmt.Printf("🔄 Falling back to traditional search for: '%s'\n", query)

	files, err := sse.getAllFiles()
	if err != nil {
		return nil, err
	}

	var results []SemanticSearchResult
	queryLower := strings.ToLower(query)

	for _, file := range files {
		if len(results) >= maxResults {
			break
		}

		if strings.HasSuffix(strings.ToLower(file), ".md") {
			content, err := sse.readFileContent(file)
			if err != nil {
				continue
			}

			contentLower := strings.ToLower(content)
			if strings.Contains(contentLower, queryLower) {
				snippet := sse.extractRelevantSnippet(content, query)

				results = append(results, SemanticSearchResult{
					File:      file,
					Score:     0.7, // Default score for traditional search
					Snippet:   snippet,
					Relevance: "Medium",
					Context:   sse.extractContext(content, query),
				})
			}
		}
	}

	return results, nil
}

// Helper functions
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// Demo function to test semantic search
func main() {
	fmt.Println("🧠 ADVANCED SEMANTIC SEARCH ENGINE")
	fmt.Println("==================================")

	// Configuration
	baseURL := "https://127.0.0.1:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	ollamaHost := "http://localhost:11434"
	ollamaModel := "deepseek-r1:8b"

	// Create semantic search engine
	sse := NewSemanticSearchEngine(baseURL, token, ollamaHost, ollamaModel)

	// Test semantic search
	query := "artificial intelligence and machine learning"
	fmt.Printf("🔍 Testing semantic search for: '%s'\n", query)

	results, err := sse.SemanticSearch(query, 5)
	if err != nil {
		fmt.Printf("❌ Semantic search failed: %v\n", err)
		return
	}

	fmt.Printf("✅ Found %d semantic results:\n\n", len(results))

	for i, result := range results {
		fmt.Printf("%d. 📄 %s (Score: %.3f, Relevance: %s)\n", i+1, result.File, result.Score, result.Relevance)
		fmt.Printf("   💬 %s\n", result.Snippet)
		fmt.Printf("   🔗 Context: %s\n\n", result.Context)
	}

	fmt.Println("🎉 Semantic search engine is ready!")
}
