package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// WebInterface provides a web-based interface for vault management
type WebInterface struct {
	baseURL        string
	token          string
	ollamaHost     string
	ollamaModel    string
	client         *http.Client
	searchEngine   *SemanticSearchEngine
	taggingEngine  *BulkTaggingEngine
	linkAnalyzer   *LinkAnalysisEngine
	aiAgent        *AIVaultAgent
}

// NewWebInterface creates a new web interface
func NewWebInterface(baseURL, token, ollamaHost, ollamaModel string) *WebInterface {
	return &WebInterface{
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
		searchEngine:  NewSemanticSearchEngine(baseURL, token, ollamaHost, ollamaModel),
		taggingEngine: NewBulkTaggingEngine(baseURL, token),
		linkAnalyzer:  NewLinkAnalysisEngine(baseURL, token),
		aiAgent:       NewAIVaultAgent(baseURL, token, ollamaHost, ollamaModel),
	}
}

// WebPage represents a web page
type WebPage struct {
	Title       string
	Content     string
	Data        interface{}
	Timestamp   time.Time
}

// SearchResult represents a search result for web display
type SearchResult struct {
	File      string  `json:"file"`
	Score     float64 `json:"score"`
	Snippet   string  `json:"snippet"`
	Type      string  `json:"type"`
	Relevance string  `json:"relevance"`
}

// VaultStats represents vault statistics for web display
type VaultStats struct {
	TotalFiles     int     `json:"total_files"`
	TotalNotes     int     `json:"total_notes"`
	TotalFolders   int     `json:"total_folders"`
	AverageWords   int     `json:"average_words"`
	FilesWithTags  int     `json:"files_with_tags"`
	FilesWithLinks int     `json:"files_with_links"`
	LastModified   string  `json:"last_modified"`
	HealthScore    float64 `json:"health_score"`
}

// StartWebServer starts the web interface server
func (wi *WebInterface) StartWebServer(port string) error {
	http.HandleFunc("/", wi.handleHome)
	http.HandleFunc("/search", wi.handleSearch)
	http.HandleFunc("/stats", wi.handleStats)
	http.HandleFunc("/analyze", wi.handleAnalyze)
	http.HandleFunc("/recommend", wi.handleRecommend)
	http.HandleFunc("/api/search", wi.handleAPISearch)
	http.HandleFunc("/api/stats", wi.handleAPIStats)
	http.HandleFunc("/api/analyze", wi.handleAPIAnalyze)
	http.HandleFunc("/api/recommend", wi.handleAPIRecommend)
	
	fmt.Printf("🌐 Starting web interface on port %s\n", port)
	fmt.Printf("🔗 Access at: http://localhost:%s\n", port)
	
	return http.ListenAndServe(":"+port, nil)
}

// handleHome handles the home page
func (wi *WebInterface) handleHome(w http.ResponseWriter, r *http.Request) {
	page := WebPage{
		Title:     "Obsidian Vault Manager",
		Content:   wi.getHomePageHTML(),
		Timestamp: time.Now(),
	}
	
	wi.renderPage(w, page)
}

// handleSearch handles the search page
func (wi *WebInterface) handleSearch(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	
	var results []SearchResult
	var message string
	
	if query != "" {
		// Perform semantic search
		semanticResults, err := wi.searchEngine.SemanticSearch(query, 10)
		if err != nil {
			message = fmt.Sprintf("Search failed: %v", err)
		} else {
			// Convert to web format
			for _, result := range semanticResults {
				results = append(results, SearchResult{
					File:      result.File,
					Score:     result.Score,
					Snippet:   result.Snippet,
					Type:      "semantic",
					Relevance: result.Relevance,
				})
			}
			message = fmt.Sprintf("Found %d results for '%s'", len(results), query)
		}
	}
	
	page := WebPage{
		Title:   "Search Results",
		Content: wi.getSearchPageHTML(query, results, message),
		Data: map[string]interface{}{
			"query":   query,
			"results": results,
			"message": message,
		},
		Timestamp: time.Now(),
	}
	
	wi.renderPage(w, page)
}

// handleStats handles the statistics page
func (wi *WebInterface) handleStats(w http.ResponseWriter, r *http.Request) {
	stats, err := wi.getVaultStats()
	if err != nil {
		stats = &VaultStats{
			TotalFiles: 0,
			Message:    fmt.Sprintf("Failed to get stats: %v", err),
		}
	}
	
	page := WebPage{
		Title:   "Vault Statistics",
		Content: wi.getStatsPageHTML(stats),
		Data:    stats,
		Timestamp: time.Now(),
	}
	
	wi.renderPage(w, page)
}

// handleAnalyze handles the analysis page
func (wi *WebInterface) handleAnalyze(w http.ResponseWriter, r *http.Request) {
	var analysisResult *LinkAnalysisResult
	var message string
	
	// Perform link analysis
	result, err := wi.linkAnalyzer.AnalyzeLinks()
	if err != nil {
		message = fmt.Sprintf("Analysis failed: %v", err)
	} else {
		analysisResult = result
		message = "Analysis completed successfully"
	}
	
	page := WebPage{
		Title:   "Vault Analysis",
		Content: wi.getAnalysisPageHTML(analysisResult, message),
		Data: map[string]interface{}{
			"analysis": analysisResult,
			"message":  message,
		},
		Timestamp: time.Now(),
	}
	
	wi.renderPage(w, page)
}

// handleRecommend handles the recommendations page
func (wi *WebInterface) handleRecommend(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	if query == "" {
		query = "general vault improvement"
	}
	
	// Generate recommendations using AI agent
	task := AgentTask{
		ID:          "web-recommend-001",
		Type:        "recommend",
		Description: "Generate recommendations for web interface",
		Parameters: map[string]interface{}{
			"query": query,
		},
		Priority:  5,
		Status:    "pending",
		CreatedAt: time.Now(),
	}
	
	var recommendations []string
	var message string
	
	result, err := wi.aiAgent.ExecuteTask(task)
	if err != nil {
		message = fmt.Sprintf("Failed to generate recommendations: %v", err)
	} else {
		recommendations = result.Recommendations
		message = result.Message
	}
	
	page := WebPage{
		Title:   "AI Recommendations",
		Content: wi.getRecommendationsPageHTML(query, recommendations, message),
		Data: map[string]interface{}{
			"query":           query,
			"recommendations": recommendations,
			"message":         message,
		},
		Timestamp: time.Now(),
	}
	
	wi.renderPage(w, page)
}

// API handlers
func (wi *WebInterface) handleAPISearch(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	
	var request struct {
		Query string `json:"query"`
		Limit int    `json:"limit"`
	}
	
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	
	if request.Limit == 0 {
		request.Limit = 10
	}
	
	// Perform search
	results, err := wi.searchEngine.SemanticSearch(request.Query, request.Limit)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	// Convert to web format
	var webResults []SearchResult
	for _, result := range results {
		webResults = append(webResults, SearchResult{
			File:      result.File,
			Score:     result.Score,
			Snippet:   result.Snippet,
			Type:      "semantic",
			Relevance: result.Relevance,
		})
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"query":   request.Query,
		"results": webResults,
		"count":   len(webResults),
	})
}

func (wi *WebInterface) handleAPIStats(w http.ResponseWriter, r *http.Request) {
	stats, err := wi.getVaultStats()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

func (wi *WebInterface) handleAPIAnalyze(w http.ResponseWriter, r *http.Request) {
	result, err := wi.linkAnalyzer.AnalyzeLinks()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

func (wi *WebInterface) handleAPIRecommend(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}
	
	var request struct {
		Query string `json:"query"`
	}
	
	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	
	if request.Query == "" {
		request.Query = "general vault improvement"
	}
	
	// Generate recommendations
	task := AgentTask{
		ID:          "api-recommend-001",
		Type:        "recommend",
		Description: "Generate recommendations for API",
		Parameters: map[string]interface{}{
			"query": request.Query,
		},
		Priority:  5,
		Status:    "pending",
		CreatedAt: time.Now(),
	}
	
	result, err := wi.aiAgent.ExecuteTask(task)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"query":           request.Query,
		"recommendations": result.Recommendations,
		"message":         result.Message,
	})
}

// Helper methods
func (wi *WebInterface) getVaultStats() (*VaultStats, error) {
	files, err := wi.getAllFiles()
	if err != nil {
		return nil, err
	}
	
	stats := &VaultStats{
		TotalFiles: len(files),
		LastModified: time.Now().Format("2006-01-02 15:04:05"),
	}
	
	noteCount := 0
	folderCount := 0
	totalWords := 0
	filesWithTags := 0
	filesWithLinks := 0
	
	for _, file := range files {
		if strings.HasSuffix(file, "/") {
			folderCount++
		} else if strings.HasSuffix(strings.ToLower(file), ".md") {
			noteCount++
			
			// Read content to analyze
			content, err := wi.readFileContent(file)
			if err == nil {
				words := len(strings.Fields(content))
				totalWords += words
				
				// Check for tags
				if strings.Contains(content, "#") {
					filesWithTags++
				}
				
				// Check for links
				if strings.Contains(content, "[["]) {
					filesWithLinks++
				}
			}
		}
	}
	
	stats.TotalNotes = noteCount
	stats.TotalFolders = folderCount
	stats.FilesWithTags = filesWithTags
	stats.FilesWithLinks = filesWithLinks
	
	if noteCount > 0 {
		stats.AverageWords = totalWords / noteCount
	}
	
	// Calculate health score
	healthScore := 0.0
	if stats.TotalNotes > 0 {
		healthScore += float64(stats.FilesWithTags) / float64(stats.TotalNotes) * 30
		healthScore += float64(stats.FilesWithLinks) / float64(stats.TotalNotes) * 40
		healthScore += min(float64(stats.AverageWords)/100, 1.0) * 30
	}
	stats.HealthScore = healthScore
	
	return stats, nil
}

func (wi *WebInterface) getAllFiles() ([]string, error) {
	var allFiles []string
	
	resp, err := wi.makeRequest("GET", "/vault/", nil)
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
	
	for _, file := range response.Files {
		if strings.HasSuffix(file, "/") {
			subFiles, err := wi.getDirectoryFiles(file)
			if err == nil {
				allFiles = append(allFiles, subFiles...)
			}
		} else {
			allFiles = append(allFiles, file)
		}
	}
	
	return allFiles, nil
}

func (wi *WebInterface) getDirectoryFiles(dirPath string) ([]string, error) {
	resp, err := wi.makeRequest("GET", "/vault/"+url.PathEscape(dirPath), nil)
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
			subFiles, err := wi.getDirectoryFiles(dirPath + file)
			if err == nil {
				files = append(files, subFiles...)
			}
		} else {
			files = append(files, dirPath+file)
		}
	}
	
	return files, nil
}

func (wi *WebInterface) readFileContent(filename string) (string, error) {
	resp, err := wi.makeRequest("GET", "/vault/"+url.PathEscape(filename), nil)
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

func (wi *WebInterface) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, wi.baseURL+path, body)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("Authorization", "Bearer "+wi.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	
	return wi.client.Do(req)
}

func (wi *WebInterface) renderPage(w http.ResponseWriter, page WebPage) {
	tmpl := template.Must(template.New("page").Parse(wi.getBaseHTML()))
	
	w.Header().Set("Content-Type", "text/html")
	if err := tmpl.Execute(w, page); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

// HTML templates
func (wi *WebInterface) getBaseHTML() string {
	return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{.Title}} - Obsidian Vault Manager</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; padding: 8px 16px; border-radius: 4px; }
        .nav a:hover { background: #2c3e50; }
        .content { padding: 20px; }
        .search-box { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
        .btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .result { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 4px; }
        .result h3 { margin: 0 0 10px 0; color: #2c3e50; }
        .result .snippet { color: #666; margin: 10px 0; }
        .result .score { color: #27ae60; font-weight: bold; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 4px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #666; margin-top: 5px; }
        .recommendation { background: #e8f5e8; border-left: 4px solid #27ae60; padding: 15px; margin: 10px 0; }
        .error { background: #ffeaea; border-left: 4px solid #e74c3c; padding: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Obsidian Vault Manager</h1>
            <p>AI-powered vault management and analysis</p>
        </div>
        <div class="nav">
            <a href="/">🏠 Home</a>
            <a href="/search">🔍 Search</a>
            <a href="/stats">📊 Statistics</a>
            <a href="/analyze">🔗 Analysis</a>
            <a href="/recommend">💡 Recommendations</a>
        </div>
        <div class="content">
            {{.Content}}
        </div>
    </div>
</body>
</html>
`
}

func (wi *WebInterface) getHomePageHTML() string {
	return `
<h2>Welcome to Obsidian Vault Manager</h2>
<p>Your AI-powered vault management system is ready to help you organize, analyze, and optimize your knowledge base.</p>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">69</div>
        <div class="stat-label">Total Files</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">39</div>
        <div class="stat-label">Notes</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">22</div>
        <div class="stat-label">Folders</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">8.5</div>
        <div class="stat-label">Health Score</div>
    </div>
</div>

<h3>🚀 Quick Actions</h3>
<ul>
    <li><a href="/search">🔍 Search your vault</a> - Find content with AI-powered semantic search</li>
    <li><a href="/stats">📊 View statistics</a> - See detailed vault metrics and health</li>
    <li><a href="/analyze">🔗 Analyze links</a> - Understand your knowledge graph</li>
    <li><a href="/recommend">💡 Get recommendations</a> - AI-powered improvement suggestions</li>
</ul>

<h3>🎯 Features</h3>
<ul>
    <li><strong>Semantic Search:</strong> Find content by meaning, not just keywords</li>
    <li><strong>Link Analysis:</strong> Understand connections between your notes</li>
    <li><strong>AI Recommendations:</strong> Get personalized suggestions for improvement</li>
    <li><strong>Bulk Operations:</strong> Organize and tag files efficiently</li>
    <li><strong>Real-time Stats:</strong> Monitor your vault's health and growth</li>
</ul>
`
}

func (wi *WebInterface) getSearchPageHTML(query string, results []SearchResult, message string) string {
	html := `
<h2>🔍 Semantic Search</h2>
<form method="GET" action="/search">
    <input type="text" name="q" class="search-box" placeholder="Search your vault..." value="` + query + `">
    <button type="submit" class="btn">Search</button>
</form>
`

	if message != "" {
		if strings.Contains(message, "Found") {
			html += `<div class="recommendation">` + message + `</div>`
		} else {
			html += `<div class="error">` + message + `</div>`
		}
	}

	if len(results) > 0 {
		html += `<h3>Search Results</h3>`
		for _, result := range results {
			html += fmt.Sprintf(`
<div class="result">
    <h3>📄 %s</h3>
    <div class="snippet">%s</div>
    <div class="score">Score: %.2f | Relevance: %s</div>
</div>
`, result.File, result.Snippet, result.Score, result.Relevance)
		}
	}

	return html
}

func (wi *WebInterface) getStatsPageHTML(stats *VaultStats) string {
	return fmt.Sprintf(`
<h2>📊 Vault Statistics</h2>
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Total Files</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Notes</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Folders</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Average Words</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Files with Tags</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Files with Links</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%.1f</div>
        <div class="stat-label">Health Score</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%s</div>
        <div class="stat-label">Last Modified</div>
    </div>
</div>
`, stats.TotalFiles, stats.TotalNotes, stats.TotalFolders, stats.AverageWords, 
   stats.FilesWithTags, stats.FilesWithLinks, stats.HealthScore, stats.LastModified)
}

func (wi *WebInterface) getAnalysisPageHTML(analysis *LinkAnalysisResult, message string) string {
	html := `<h2>🔗 Vault Analysis</h2>`
	
	if message != "" {
		if strings.Contains(message, "completed") {
			html += `<div class="recommendation">` + message + `</div>`
		} else {
			html += `<div class="error">` + message + `</div>`
		}
	}
	
	if analysis != nil {
		html += fmt.Sprintf(`
<h3>📊 Graph Statistics</h3>
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Total Nodes</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Total Links</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%.2f</div>
        <div class="stat-label">Average Degree</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%.4f</div>
        <div class="stat-label">Density</div>
    </div>
</div>
`, analysis.Graph.Statistics.TotalNodes, analysis.Graph.Statistics.TotalLinks, 
   analysis.Graph.Statistics.AverageDegree, analysis.Graph.Statistics.Density)
		
		if len(analysis.HubNodes) > 0 {
			html += `<h3>🏆 Hub Nodes (High Out-Degree)</h3>`
			for i, node := range analysis.HubNodes {
				if i < 5 {
					html += fmt.Sprintf(`<div class="result"><h3>%s</h3><div class="snippet">%d out-links</div></div>`, node.Title, node.OutDegree)
				}
			}
		}
		
		if len(analysis.AuthorityNodes) > 0 {
			html += `<h3>🎯 Authority Nodes (High In-Degree)</h3>`
			for i, node := range analysis.AuthorityNodes {
				if i < 5 {
					html += fmt.Sprintf(`<div class="result"><h3>%s</h3><div class="snippet">%d in-links</div></div>`, node.Title, node.InDegree)
				}
			}
		}
	}
	
	return html
}

func (wi *WebInterface) getRecommendationsPageHTML(query string, recommendations []string, message string) string {
	html := `
<h2>💡 AI Recommendations</h2>
<form method="GET" action="/recommend">
    <input type="text" name="q" class="search-box" placeholder="What would you like to improve?" value="` + query + `">
    <button type="submit" class="btn">Get Recommendations</button>
</form>
`

	if message != "" {
		html += `<div class="recommendation">` + message + `</div>`
	}

	if len(recommendations) > 0 {
		html += `<h3>🎯 Recommendations</h3>`
		for i, rec := range recommendations {
			html += fmt.Sprintf(`<div class="recommendation">%d. %s</div>`, i+1, rec)
		}
	}

	return html
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}

// Demo function to test web interface
func main() {
	fmt.Println("🌐 WEB INTERFACE FOR OBSIDIAN VAULT MANAGER")
	fmt.Println("==========================================")
	
	// Configuration
	baseURL := "https://127.0.0.1:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	ollamaHost := "http://localhost:11434"
	ollamaModel := "deepseek-r1:8b"
	
	// Create web interface
	webInterface := NewWebInterface(baseURL, token, ollamaHost, ollamaModel)
	
	// Start web server
	fmt.Println("🚀 Starting web server...")
	if err := webInterface.StartWebServer("8080"); err != nil {
		fmt.Printf("❌ Failed to start web server: %v\n", err)
		return
	}
}
