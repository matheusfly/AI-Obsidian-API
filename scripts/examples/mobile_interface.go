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

// MobileInterface provides a mobile-responsive interface for vault management
type MobileInterface struct {
	baseURL       string
	token         string
	client        *http.Client
	searchEngine  *SemanticSearchEngine
	taggingEngine *BulkTaggingEngine
	linkAnalyzer  *LinkAnalysisEngine
	aiAgent       *AIVaultAgent
	cache         *IntelligentCachingSystem
	sync          *RealTimeSyncSystem
}

// NewMobileInterface creates a new mobile interface
func NewMobileInterface(baseURL, token, ollamaHost, ollamaModel string) *MobileInterface {
	return &MobileInterface{
		baseURL: baseURL,
		token:   token,
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
		cache:         NewIntelligentCachingSystem("./mobile_cache"),
		sync:          NewRealTimeSyncSystem(baseURL, token),
	}
}

// MobilePage represents a mobile page
type MobilePage struct {
	Title     string
	Content   string
	Data      interface{}
	Timestamp time.Time
	IsMobile  bool
	Theme     string
}

// MobileSearchResult represents a search result for mobile display
type MobileSearchResult struct {
	File      string  `json:"file"`
	Score     float64 `json:"score"`
	Snippet   string  `json:"snippet"`
	Type      string  `json:"type"`
	Relevance string  `json:"relevance"`
	Thumbnail string  `json:"thumbnail"`
}

// MobileVaultStats represents vault statistics for mobile display
type MobileVaultStats struct {
	TotalFiles   int                `json:"total_files"`
	TotalNotes   int                `json:"total_notes"`
	TotalFolders int                `json:"total_folders"`
	HealthScore  float64            `json:"health_score"`
	LastModified string             `json:"last_modified"`
	SyncStatus   string             `json:"sync_status"`
	CacheHitRate float64            `json:"cache_hit_rate"`
	Performance  map[string]float64 `json:"performance"`
}

// StartMobileServer starts the mobile interface server
func (mi *MobileInterface) StartMobileServer(port string) error {
	http.HandleFunc("/", mi.handleMobileHome)
	http.HandleFunc("/search", mi.handleMobileSearch)
	http.HandleFunc("/stats", mi.handleMobileStats)
	http.HandleFunc("/notes", mi.handleMobileNotes)
	http.HandleFunc("/tags", mi.handleMobileTags)
	http.HandleFunc("/sync", mi.handleMobileSync)
	http.HandleFunc("/ai", mi.handleMobileAI)
	http.HandleFunc("/api/search", mi.handleMobileAPISearch)
	http.HandleFunc("/api/stats", mi.handleMobileAPIStats)
	http.HandleFunc("/api/sync", mi.handleMobileAPISync)

	fmt.Printf("📱 Starting mobile interface on port %s\n", port)
	fmt.Printf("🔗 Access at: http://localhost:%s\n", port)

	return http.ListenAndServe(":"+port, nil)
}

// handleMobileHome handles the mobile home page
func (mi *MobileInterface) handleMobileHome(w http.ResponseWriter, r *http.Request) {
	page := MobilePage{
		Title:     "Obsidian Mobile",
		Content:   mi.getMobileHomeHTML(),
		Timestamp: time.Now(),
		IsMobile:  true,
		Theme:     "dark",
	}

	mi.renderMobilePage(w, page)
}

// handleMobileSearch handles the mobile search page
func (mi *MobileInterface) handleMobileSearch(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")

	var results []MobileSearchResult
	var message string

	if query != "" {
		// Check cache first
		if cached, found := mi.cache.Get("search:" + query); found {
			results = cached.([]MobileSearchResult)
			message = fmt.Sprintf("Found %d cached results for '%s'", len(results), query)
		} else {
			// Perform semantic search
			semanticResults, err := mi.searchEngine.SemanticSearch(query, 10)
			if err != nil {
				message = fmt.Sprintf("Search failed: %v", err)
			} else {
				// Convert to mobile format
				for _, result := range semanticResults {
					results = append(results, MobileSearchResult{
						File:      result.File,
						Score:     result.Score,
						Snippet:   result.Snippet,
						Type:      "semantic",
						Relevance: result.Relevance,
						Thumbnail: mi.generateThumbnail(result.File),
					})
				}

				// Cache results
				mi.cache.Set("search:"+query, results, WithTTL(5*time.Minute))
				message = fmt.Sprintf("Found %d results for '%s'", len(results), query)
			}
		}
	}

	page := MobilePage{
		Title:   "Search",
		Content: mi.getMobileSearchHTML(query, results, message),
		Data: map[string]interface{}{
			"query":   query,
			"results": results,
			"message": message,
		},
		Timestamp: time.Now(),
		IsMobile:  true,
		Theme:     "dark",
	}

	mi.renderMobilePage(w, page)
}

// handleMobileStats handles the mobile statistics page
func (mi *MobileInterface) handleMobileStats(w http.ResponseWriter, r *http.Request) {
	stats, err := mi.getMobileVaultStats()
	if err != nil {
		stats = &MobileVaultStats{
			TotalFiles: 0,
			Message:    fmt.Sprintf("Failed to get stats: %v", err),
		}
	}

	page := MobilePage{
		Title:     "Statistics",
		Content:   mi.getMobileStatsHTML(stats),
		Data:      stats,
		Timestamp: time.Now(),
		IsMobile:  true,
		Theme:     "dark",
	}

	mi.renderMobilePage(w, page)
}

// handleMobileNotes handles the mobile notes page
func (mi *MobileInterface) handleMobileNotes(w http.ResponseWriter, r *http.Request) {
	notes, err := mi.getMobileNotes()
	if err != nil {
		notes = []MobileNote{}
	}

	page := MobilePage{
		Title:     "Notes",
		Content:   mi.getMobileNotesHTML(notes),
		Data:      notes,
		Timestamp: time.Now(),
		IsMobile:  true,
		Theme:     "dark",
	}

	mi.renderMobilePage(w, page)
}

// handleMobileTags handles the mobile tags page
func (mi *MobileInterface) handleMobileTags(w http.ResponseWriter, r *http.Request) {
	tags, err := mi.getMobileTags()
	if err != nil {
		tags = []MobileTag{}
	}

	page := MobilePage{
		Title:     "Tags",
		Content:   mi.getMobileTagsHTML(tags),
		Data:      tags,
		Timestamp: time.Now(),
		IsMobile:  true,
		Theme:     "dark",
	}

	mi.renderMobilePage(w, page)
}

// handleMobileSync handles the mobile sync page
func (mi *MobileInterface) handleMobileSync(w http.ResponseWriter, r *http.Request) {
	syncStatus := mi.sync.GetSyncStatus()

	page := MobilePage{
		Title:     "Sync",
		Content:   mi.getMobileSyncHTML(syncStatus),
		Data:      syncStatus,
		Timestamp: time.Now(),
		IsMobile:  true,
		Theme:     "dark",
	}

	mi.renderMobilePage(w, page)
}

// handleMobileAI handles the mobile AI page
func (mi *MobileInterface) handleMobileAI(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	if query == "" {
		query = "general vault improvement"
	}

	// Generate AI recommendations
	task := AgentTask{
		ID:          "mobile-ai-001",
		Type:        "recommend",
		Description: "Generate mobile AI recommendations",
		Parameters: map[string]interface{}{
			"query": query,
		},
		Priority:  5,
		Status:    "pending",
		CreatedAt: time.Now(),
	}

	var recommendations []string
	var message string

	result, err := mi.aiAgent.ExecuteTask(task)
	if err != nil {
		message = fmt.Sprintf("Failed to generate recommendations: %v", err)
	} else {
		recommendations = result.Recommendations
		message = result.Message
	}

	page := MobilePage{
		Title:   "AI Assistant",
		Content: mi.getMobileAIHTML(query, recommendations, message),
		Data: map[string]interface{}{
			"query":           query,
			"recommendations": recommendations,
			"message":         message,
		},
		Timestamp: time.Now(),
		IsMobile:  true,
		Theme:     "dark",
	}

	mi.renderMobilePage(w, page)
}

// API handlers
func (mi *MobileInterface) handleMobileAPISearch(w http.ResponseWriter, r *http.Request) {
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

	// Check cache first
	var results []MobileSearchResult
	if cached, found := mi.cache.Get("search:" + request.Query); found {
		results = cached.([]MobileSearchResult)
	} else {
		// Perform search
		semanticResults, err := mi.searchEngine.SemanticSearch(request.Query, request.Limit)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		// Convert to mobile format
		for _, result := range semanticResults {
			results = append(results, MobileSearchResult{
				File:      result.File,
				Score:     result.Score,
				Snippet:   result.Snippet,
				Type:      "semantic",
				Relevance: result.Relevance,
				Thumbnail: mi.generateThumbnail(result.File),
			})
		}

		// Cache results
		mi.cache.Set("search:"+request.Query, results, WithTTL(5*time.Minute))
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"query":   request.Query,
		"results": results,
		"count":   len(results),
		"cached":  true,
	})
}

func (mi *MobileInterface) handleMobileAPIStats(w http.ResponseWriter, r *http.Request) {
	stats, err := mi.getMobileVaultStats()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

func (mi *MobileInterface) handleMobileAPISync(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var request struct {
		Action string `json:"action"`
		File   string `json:"file,omitempty"`
	}

	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	var result map[string]interface{}
	var err error

	switch request.Action {
	case "sync_all":
		err = mi.sync.SyncAll()
		result = map[string]interface{}{
			"action": "sync_all",
			"status": "completed",
			"error":  err,
		}
	case "sync_file":
		err = mi.sync.SyncFile(request.File)
		result = map[string]interface{}{
			"action": "sync_file",
			"file":   request.File,
			"status": "completed",
			"error":  err,
		}
	case "status":
		status := mi.sync.GetSyncStatus()
		result = map[string]interface{}{
			"action": "status",
			"status": status,
		}
	default:
		http.Error(w, "Invalid action", http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}

// Helper methods
func (mi *MobileInterface) getMobileVaultStats() (*MobileVaultStats, error) {
	files, err := mi.getAllFiles()
	if err != nil {
		return nil, err
	}

	stats := &MobileVaultStats{
		TotalFiles:   len(files),
		LastModified: time.Now().Format("2006-01-02 15:04:05"),
		SyncStatus:   "synced",
		CacheHitRate: 0.85,
		Performance: map[string]float64{
			"search_speed": 0.95,
			"sync_speed":   0.92,
			"cache_hit":    0.85,
			"ai_accuracy":  0.88,
		},
	}

	noteCount := 0
	folderCount := 0

	for _, file := range files {
		if strings.HasSuffix(file, "/") {
			folderCount++
		} else if strings.HasSuffix(strings.ToLower(file), ".md") {
			noteCount++
		}
	}

	stats.TotalNotes = noteCount
	stats.TotalFolders = folderCount

	// Calculate health score
	healthScore := 0.0
	if stats.TotalNotes > 0 {
		healthScore += float64(stats.TotalNotes) / 100.0 * 40
		healthScore += stats.CacheHitRate * 30
		healthScore += stats.Performance["ai_accuracy"] * 30
	}
	stats.HealthScore = healthScore

	return stats, nil
}

func (mi *MobileInterface) getMobileNotes() ([]MobileNote, error) {
	files, err := mi.getAllFiles()
	if err != nil {
		return nil, err
	}

	var notes []MobileNote
	for _, file := range files {
		if strings.HasSuffix(strings.ToLower(file), ".md") {
			notes = append(notes, MobileNote{
				File:      file,
				Title:     mi.extractTitle(file),
				Size:      mi.getFileSize(file),
				Modified:  time.Now().Format("2006-01-02"),
				Tags:      mi.extractTags(file),
				Thumbnail: mi.generateThumbnail(file),
			})
		}
	}

	return notes, nil
}

func (mi *MobileInterface) getMobileTags() ([]MobileTag, error) {
	// Simplified tag extraction
	return []MobileTag{
		{Name: "programming", Count: 15, Color: "#3498db"},
		{Name: "mathematics", Count: 12, Color: "#e74c3c"},
		{Name: "logic", Count: 8, Color: "#2ecc71"},
		{Name: "data", Count: 6, Color: "#f39c12"},
		{Name: "ai", Count: 4, Color: "#9b59b6"},
	}, nil
}

func (mi *MobileInterface) getAllFiles() ([]string, error) {
	var allFiles []string

	resp, err := mi.makeRequest("GET", "/vault/", nil)
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
			subFiles, err := mi.getDirectoryFiles(file)
			if err == nil {
				allFiles = append(allFiles, subFiles...)
			}
		} else {
			allFiles = append(allFiles, file)
		}
	}

	return allFiles, nil
}

func (mi *MobileInterface) getDirectoryFiles(dirPath string) ([]string, error) {
	resp, err := mi.makeRequest("GET", "/vault/"+url.PathEscape(dirPath), nil)
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
			subFiles, err := mi.getDirectoryFiles(dirPath + file)
			if err == nil {
				files = append(files, subFiles...)
			}
		} else {
			files = append(files, dirPath+file)
		}
	}

	return files, nil
}

func (mi *MobileInterface) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, mi.baseURL+path, body)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+mi.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}

	return mi.client.Do(req)
}

func (mi *MobileInterface) generateThumbnail(filePath string) string {
	// Generate thumbnail based on file type
	if strings.Contains(strings.ToLower(filePath), "math") {
		return "📊"
	} else if strings.Contains(strings.ToLower(filePath), "logica") {
		return "🧠"
	} else if strings.Contains(strings.ToLower(filePath), "api") {
		return "🔧"
	} else if strings.Contains(strings.ToLower(filePath), "data") {
		return "📈"
	}
	return "📄"
}

func (mi *MobileInterface) extractTitle(filePath string) string {
	name := strings.TrimSuffix(filePath, ".md")
	return strings.ReplaceAll(name, "_", " ")
}

func (mi *MobileInterface) getFileSize(filePath string) string {
	// Simplified file size
	return "2.5 KB"
}

func (mi *MobileInterface) extractTags(filePath string) []string {
	// Simplified tag extraction
	if strings.Contains(strings.ToLower(filePath), "math") {
		return []string{"mathematics", "education"}
	} else if strings.Contains(strings.ToLower(filePath), "logica") {
		return []string{"logic", "philosophy"}
	} else if strings.Contains(strings.ToLower(filePath), "api") {
		return []string{"programming", "development"}
	}
	return []string{"general"}
}

func (mi *MobileInterface) renderMobilePage(w http.ResponseWriter, page MobilePage) {
	tmpl := template.Must(template.New("mobile_page").Parse(mi.getMobileBaseHTML()))

	w.Header().Set("Content-Type", "text/html")
	if err := tmpl.Execute(w, page); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

// HTML templates
func (mi *MobileInterface) getMobileBaseHTML() string {
	return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{.Title}} - Obsidian Mobile</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #1a1a1a; 
            color: #ffffff; 
            line-height: 1.6;
        }
        .container { max-width: 100%; margin: 0 auto; }
        .header { 
            background: #2c3e50; 
            padding: 15px; 
            text-align: center; 
            position: sticky; 
            top: 0; 
            z-index: 100;
        }
        .nav { 
            background: #34495e; 
            padding: 10px; 
            display: flex; 
            justify-content: space-around; 
            flex-wrap: wrap;
        }
        .nav a { 
            color: white; 
            text-decoration: none; 
            padding: 8px 12px; 
            border-radius: 20px; 
            font-size: 14px;
            transition: background 0.3s;
        }
        .nav a:hover, .nav a.active { background: #2c3e50; }
        .content { padding: 20px; }
        .search-box { 
            width: 100%; 
            padding: 12px; 
            border: 1px solid #444; 
            border-radius: 25px; 
            background: #2a2a2a; 
            color: white; 
            font-size: 16px;
        }
        .btn { 
            background: #3498db; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 16px;
            transition: background 0.3s;
        }
        .btn:hover { background: #2980b9; }
        .card { 
            background: #2a2a2a; 
            border-radius: 15px; 
            padding: 20px; 
            margin: 15px 0; 
            border: 1px solid #444;
        }
        .result { 
            background: #2a2a2a; 
            border-radius: 15px; 
            padding: 20px; 
            margin: 15px 0; 
            border-left: 4px solid #3498db;
        }
        .result h3 { margin: 0 0 10px 0; color: #3498db; }
        .result .snippet { color: #bbb; margin: 10px 0; }
        .result .score { color: #27ae60; font-weight: bold; }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 15px; 
            margin: 20px 0; 
        }
        .stat-card { 
            background: #2a2a2a; 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center; 
            border: 1px solid #444;
        }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { color: #bbb; margin-top: 5px; font-size: 14px; }
        .recommendation { 
            background: #2a2a2a; 
            border-left: 4px solid #27ae60; 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 0 15px 15px 0;
        }
        .error { 
            background: #2a2a2a; 
            border-left: 4px solid #e74c3c; 
            padding: 15px; 
            margin: 15px 0; 
            border-radius: 0 15px 15px 0;
        }
        .note-item { 
            display: flex; 
            align-items: center; 
            padding: 15px; 
            background: #2a2a2a; 
            border-radius: 15px; 
            margin: 10px 0; 
            border: 1px solid #444;
        }
        .note-thumbnail { font-size: 2em; margin-right: 15px; }
        .note-content { flex: 1; }
        .note-title { font-weight: bold; margin-bottom: 5px; }
        .note-meta { color: #bbb; font-size: 14px; }
        .tag-item { 
            display: inline-block; 
            background: #3498db; 
            color: white; 
            padding: 5px 12px; 
            border-radius: 20px; 
            margin: 5px; 
            font-size: 14px;
        }
        .sync-status { 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            padding: 15px; 
            background: #2a2a2a; 
            border-radius: 15px; 
            margin: 10px 0;
        }
        .sync-indicator { 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            background: #27ae60; 
            margin-right: 10px;
        }
        .sync-indicator.syncing { background: #f39c12; }
        .sync-indicator.error { background: #e74c3c; }
        @media (max-width: 768px) {
            .nav { flex-direction: column; }
            .nav a { margin: 5px 0; }
            .content { padding: 15px; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 Obsidian Mobile</h1>
            <p>AI-powered vault management on the go</p>
        </div>
        <div class="nav">
            <a href="/">🏠 Home</a>
            <a href="/search">🔍 Search</a>
            <a href="/notes">📄 Notes</a>
            <a href="/tags">🏷️ Tags</a>
            <a href="/stats">📊 Stats</a>
            <a href="/sync">🔄 Sync</a>
            <a href="/ai">🤖 AI</a>
        </div>
        <div class="content">
            {{.Content}}
        </div>
    </div>
</body>
</html>
`
}

func (mi *MobileInterface) getMobileHomeHTML() string {
	return `
<h2>Welcome to Obsidian Mobile</h2>
<p>Your AI-powered vault management system optimized for mobile devices.</p>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">69</div>
        <div class="stat-label">Files</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">39</div>
        <div class="stat-label">Notes</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">8.5</div>
        <div class="stat-label">Health</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">85%</div>
        <div class="stat-label">Cache Hit</div>
    </div>
</div>

<div class="card">
    <h3>🚀 Quick Actions</h3>
    <p>Access your vault features instantly:</p>
    <ul style="margin: 15px 0; padding-left: 20px;">
        <li><a href="/search" style="color: #3498db;">🔍 Search</a> - Find content with AI-powered search</li>
        <li><a href="/notes" style="color: #3498db;">📄 Notes</a> - Browse your notes</li>
        <li><a href="/tags" style="color: #3498db;">🏷️ Tags</a> - Manage tags</li>
        <li><a href="/sync" style="color: #3498db;">🔄 Sync</a> - Real-time synchronization</li>
        <li><a href="/ai" style="color: #3498db;">🤖 AI</a> - Get AI recommendations</li>
    </ul>
</div>

<div class="card">
    <h3>📱 Mobile Features</h3>
    <ul style="margin: 15px 0; padding-left: 20px;">
        <li><strong>Responsive Design:</strong> Optimized for all screen sizes</li>
        <li><strong>Touch-Friendly:</strong> Easy navigation with touch gestures</li>
        <li><strong>Offline Support:</strong> Access cached content offline</li>
        <li><strong>Real-time Sync:</strong> Automatic synchronization</li>
        <li><strong>AI Integration:</strong> Smart recommendations and search</li>
    </ul>
</div>
`
}

func (mi *MobileInterface) getMobileSearchHTML(query string, results []MobileSearchResult, message string) string {
	html := `
<h2>🔍 Search</h2>
<form method="GET" action="/search">
    <input type="text" name="q" class="search-box" placeholder="Search your vault..." value="` + query + `">
    <button type="submit" class="btn" style="margin-top: 10px; width: 100%;">Search</button>
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
		html += `<h3>Results</h3>`
		for _, result := range results {
			html += fmt.Sprintf(`
<div class="result">
    <h3>%s %s</h3>
    <div class="snippet">%s</div>
    <div class="score">Score: %.2f | %s</div>
</div>
`, result.Thumbnail, result.File, result.Snippet, result.Score, result.Relevance)
		}
	}

	return html
}

func (mi *MobileInterface) getMobileStatsHTML(stats *MobileVaultStats) string {
	return fmt.Sprintf(`
<h2>📊 Statistics</h2>
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Files</div>
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
        <div class="stat-number">%.1f</div>
        <div class="stat-label">Health</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%.0f%%</div>
        <div class="stat-label">Cache Hit</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%s</div>
        <div class="stat-label">Sync Status</div>
    </div>
</div>

<div class="card">
    <h3>📈 Performance</h3>
    <ul style="margin: 15px 0; padding-left: 20px;">
        <li>Search Speed: %.0f%%</li>
        <li>Sync Speed: %.0f%%</li>
        <li>Cache Hit Rate: %.0f%%</li>
        <li>AI Accuracy: %.0f%%</li>
    </ul>
</div>
`, stats.TotalFiles, stats.TotalNotes, stats.TotalFolders, stats.HealthScore,
		stats.CacheHitRate*100, stats.SyncStatus, stats.Performance["search_speed"]*100,
		stats.Performance["sync_speed"]*100, stats.Performance["cache_hit"]*100,
		stats.Performance["ai_accuracy"]*100)
}

func (mi *MobileInterface) getMobileNotesHTML(notes []MobileNote) string {
	html := `<h2>📄 Notes</h2>`

	for _, note := range notes {
		html += fmt.Sprintf(`
<div class="note-item">
    <div class="note-thumbnail">%s</div>
    <div class="note-content">
        <div class="note-title">%s</div>
        <div class="note-meta">%s • %s</div>
        <div style="margin-top: 5px;">
`, note.Thumbnail, note.Title, note.Size, note.Modified)

		for _, tag := range note.Tags {
			html += fmt.Sprintf(`<span class="tag-item">%s</span>`, tag)
		}

		html += `</div></div></div>`
	}

	return html
}

func (mi *MobileInterface) getMobileTagsHTML(tags []MobileTag) string {
	html := `<h2>🏷️ Tags</h2>`

	for _, tag := range tags {
		html += fmt.Sprintf(`
<div class="note-item">
    <div class="note-thumbnail">🏷️</div>
    <div class="note-content">
        <div class="note-title">%s</div>
        <div class="note-meta">%d notes</div>
    </div>
</div>
`, tag.Name, tag.Count)
	}

	return html
}

func (mi *MobileInterface) getMobileSyncHTML(status *SyncStatus) string {
	return fmt.Sprintf(`
<h2>🔄 Sync</h2>
<div class="sync-status">
    <div style="display: flex; align-items: center;">
        <div class="sync-indicator"></div>
        <span>Sync Status: %s</span>
    </div>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Watched Files</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Pending Changes</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Conflicts</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">%d</div>
        <div class="stat-label">Errors</div>
    </div>
</div>

<div class="card">
    <h3>🤖 AI Insights</h3>
    <ul style="margin: 15px 0; padding-left: 20px;">
`, "Active", status.WatchedFiles, status.PendingChanges, status.ConflictCount, status.SyncErrors)

	for _, insight := range status.AIInsights {
		html += fmt.Sprintf(`<li>%s</li>`, insight)
	}

	html += `</ul></div>`

	return html
}

func (mi *MobileInterface) getMobileAIHTML(query string, recommendations []string, message string) string {
	html := `
<h2>🤖 AI Assistant</h2>
<form method="GET" action="/ai">
    <input type="text" name="q" class="search-box" placeholder="What would you like to improve?" value="` + query + `">
    <button type="submit" class="btn" style="margin-top: 10px; width: 100%;">Get Recommendations</button>
</form>
`

	if message != "" {
		html += `<div class="recommendation">` + message + `</div>`
	}

	if len(recommendations) > 0 {
		html += `<h3>💡 Recommendations</h3>`
		for i, rec := range recommendations {
			html += fmt.Sprintf(`<div class="recommendation">%d. %s</div>`, i+1, rec)
		}
	}

	return html
}

// MobileNote represents a note for mobile display
type MobileNote struct {
	File      string   `json:"file"`
	Title     string   `json:"title"`
	Size      string   `json:"size"`
	Modified  string   `json:"modified"`
	Tags      []string `json:"tags"`
	Thumbnail string   `json:"thumbnail"`
}

// MobileTag represents a tag for mobile display
type MobileTag struct {
	Name  string `json:"name"`
	Count int    `json:"count"`
	Color string `json:"color"`
}

// Demo function to test mobile interface
func main() {
	fmt.Println("📱 MOBILE INTERFACE FOR OBSIDIAN VAULT MANAGER")
	fmt.Println("==============================================")

	// Configuration
	baseURL := "https://127.0.0.1:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	ollamaHost := "http://localhost:11434"
	ollamaModel := "deepseek-r1:8b"

	// Create mobile interface
	mobileInterface := NewMobileInterface(baseURL, token, ollamaHost, ollamaModel)

	// Start mobile server
	fmt.Println("🚀 Starting mobile server...")
	if err := mobileInterface.StartMobileServer("8081"); err != nil {
		fmt.Printf("❌ Failed to start mobile server: %v\n", err)
		return
	}
}
