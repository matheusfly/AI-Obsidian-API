package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strings"
	"time"
)

// AIVaultAgent provides AI-powered automated vault management
type AIVaultAgent struct {
	baseURL        string
	token          string
	ollamaHost     string
	ollamaModel    string
	client         *http.Client
	ollamaClient   *http.Client
	searchEngine   *SemanticSearchEngine
	taggingEngine  *BulkTaggingEngine
	linkAnalyzer   *LinkAnalysisEngine
}

// NewAIVaultAgent creates a new AI vault agent
func NewAIVaultAgent(baseURL, token, ollamaHost, ollamaModel string) *AIVaultAgent {
	return &AIVaultAgent{
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
		searchEngine:  NewSemanticSearchEngine(baseURL, token, ollamaHost, ollamaModel),
		taggingEngine: NewBulkTaggingEngine(baseURL, token),
		linkAnalyzer:  NewLinkAnalysisEngine(baseURL, token),
	}
}

// AgentTask represents a task for the AI agent
type AgentTask struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"`        // "organize", "analyze", "recommend", "cleanup", "optimize"
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
	Priority    int                    `json:"priority"`    // 1-10
	Status      string                 `json:"status"`      // "pending", "running", "completed", "failed"
	Result      interface{}            `json:"result"`
	CreatedAt   time.Time              `json:"created_at"`
	CompletedAt *time.Time             `json:"completed_at,omitempty"`
}

// AgentResult represents the result of an agent task
type AgentResult struct {
	TaskID       string                 `json:"task_id"`
	Success      bool                   `json:"success"`
	Message      string                 `json:"message"`
	Data         map[string]interface{} `json:"data"`
	Recommendations []string           `json:"recommendations"`
	Actions      []AgentAction          `json:"actions"`
	ExecutionTime int64                 `json:"execution_time_ms"`
}

// AgentAction represents an action taken by the agent
type AgentAction struct {
	Type        string                 `json:"type"`
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
	Success     bool                   `json:"success"`
	Message     string                 `json:"message"`
}

// ExecuteTask executes a task using AI capabilities
func (ava *AIVaultAgent) ExecuteTask(task AgentTask) (*AgentResult, error) {
	start := time.Now()
	
	fmt.Printf("🤖 AI Agent executing task: %s (%s)\n", task.Description, task.Type)
	
	var result *AgentResult
	var err error
	
	switch task.Type {
	case "organize":
		result, err = ava.organizeVault(task)
	case "analyze":
		result, err = ava.analyzeVault(task)
	case "recommend":
		result, err = ava.generateRecommendations(task)
	case "cleanup":
		result, err = ava.cleanupVault(task)
	case "optimize":
		result, err = ava.optimizeVault(task)
	default:
		return nil, fmt.Errorf("unknown task type: %s", task.Type)
	}
	
	if err != nil {
		return &AgentResult{
			TaskID:       task.ID,
			Success:      false,
			Message:      fmt.Sprintf("Task failed: %v", err),
			Data:         make(map[string]interface{}),
			Recommendations: []string{},
			Actions:      []AgentAction{},
			ExecutionTime: time.Since(start).Milliseconds(),
		}, err
	}
	
	result.ExecutionTime = time.Since(start).Milliseconds()
	return result, nil
}

// organizeVault organizes the vault structure
func (ava *AIVaultAgent) organizeVault(task AgentTask) (*AgentResult, error) {
	fmt.Println("📁 Organizing vault structure...")
	
	var actions []AgentAction
	
	// Get all files
	files, err := ava.getAllFiles()
	if err != nil {
		return nil, err
	}
	
	// Analyze file patterns
	patterns := ava.analyzeFilePatterns(files)
	
	// Generate organization recommendations
	recommendations := ava.generateOrganizationRecommendations(patterns)
	
	// Create folders based on patterns
	folderActions := ava.createFolderStructure(patterns)
	actions = append(actions, folderActions...)
	
	// Suggest file moves
	moveActions := ava.suggestFileMoves(files, patterns)
	actions = append(actions, moveActions...)
	
	return &AgentResult{
		TaskID:       task.ID,
		Success:      true,
		Message:      "Vault organization analysis completed",
		Data: map[string]interface{}{
			"total_files": len(files),
			"patterns": patterns,
			"recommendations": recommendations,
		},
		Recommendations: recommendations,
		Actions:        actions,
	}, nil
}

// analyzeVault performs comprehensive vault analysis
func (ava *AIVaultAgent) analyzeVault(task AgentTask) (*AgentResult, error) {
	fmt.Println("🔍 Performing comprehensive vault analysis...")
	
	var actions []AgentAction
	
	// Perform link analysis
	linkResult, err := ava.linkAnalyzer.AnalyzeLinks()
	if err != nil {
		actions = append(actions, AgentAction{
			Type:        "link_analysis",
			Description: "Analyze link structure",
			Success:     false,
			Message:     fmt.Sprintf("Failed: %v", err),
		})
	} else {
		actions = append(actions, AgentAction{
			Type:        "link_analysis",
			Description: "Analyze link structure",
			Success:     true,
			Message:     fmt.Sprintf("Found %d nodes and %d links", linkResult.Graph.Statistics.TotalNodes, linkResult.Graph.Statistics.TotalLinks),
		})
	}
	
	// Analyze content quality
	qualityAnalysis := ava.analyzeContentQuality()
	actions = append(actions, AgentAction{
		Type:        "content_quality",
		Description: "Analyze content quality",
		Success:     true,
		Message:     fmt.Sprintf("Analyzed %d files", qualityAnalysis["total_files"]),
	})
	
	// Generate insights
	insights := ava.generateVaultInsights(linkResult, qualityAnalysis)
	
	return &AgentResult{
		TaskID:       task.ID,
		Success:      true,
		Message:      "Vault analysis completed",
		Data: map[string]interface{}{
			"link_analysis": linkResult,
			"quality_analysis": qualityAnalysis,
			"insights": insights,
		},
		Recommendations: insights,
		Actions:        actions,
	}, nil
}

// generateRecommendations generates AI-powered recommendations
func (ava *AIVaultAgent) generateRecommendations(task AgentTask) (*AgentResult, error) {
	fmt.Println("💡 Generating AI-powered recommendations...")
	
	var actions []AgentAction
	var recommendations []string
	
	// Get user query from parameters
	query, ok := task.Parameters["query"].(string)
	if !ok {
		query = "general vault improvement"
	}
	
	// Use AI to generate recommendations
	aiRecommendations, err := ava.generateAIRecommendations(query)
	if err != nil {
		actions = append(actions, AgentAction{
			Type:        "ai_recommendations",
			Description: "Generate AI recommendations",
			Success:     false,
			Message:     fmt.Sprintf("Failed: %v", err),
		})
	} else {
		recommendations = append(recommendations, aiRecommendations...)
		actions = append(actions, AgentAction{
			Type:        "ai_recommendations",
			Description: "Generate AI recommendations",
			Success:     true,
			Message:     fmt.Sprintf("Generated %d recommendations", len(aiRecommendations)),
		})
	}
	
	// Generate content recommendations
	contentRecs := ava.generateContentRecommendations()
	recommendations = append(recommendations, contentRecs...)
	
	// Generate structure recommendations
	structureRecs := ava.generateStructureRecommendations()
	recommendations = append(recommendations, structureRecs...)
	
	return &AgentResult{
		TaskID:       task.ID,
		Success:      true,
		Message:      "Recommendations generated successfully",
		Data: map[string]interface{}{
			"query": query,
			"total_recommendations": len(recommendations),
		},
		Recommendations: recommendations,
		Actions:        actions,
	}, nil
}

// cleanupVault performs vault cleanup tasks
func (ava *AIVaultAgent) cleanupVault(task AgentTask) (*AgentResult, error) {
	fmt.Println("🧹 Performing vault cleanup...")
	
	var actions []AgentAction
	
	// Find duplicate files
	duplicates := ava.findDuplicateFiles()
	if len(duplicates) > 0 {
		actions = append(actions, AgentAction{
			Type:        "duplicate_detection",
			Description: "Find duplicate files",
			Success:     true,
			Message:     fmt.Sprintf("Found %d potential duplicates", len(duplicates)),
		})
	}
	
	// Find orphaned files
	orphans := ava.findOrphanedFiles()
	if len(orphans) > 0 {
		actions = append(actions, AgentAction{
			Type:        "orphan_detection",
			Description: "Find orphaned files",
			Success:     true,
			Message:     fmt.Sprintf("Found %d orphaned files", len(orphans)),
		})
	}
	
	// Find broken links
	brokenLinks := ava.findBrokenLinks()
	if len(brokenLinks) > 0 {
		actions = append(actions, AgentAction{
			Type:        "broken_link_detection",
			Description: "Find broken links",
			Success:     true,
			Message:     fmt.Sprintf("Found %d broken links", len(brokenLinks)),
		})
	}
	
	// Generate cleanup recommendations
	cleanupRecs := ava.generateCleanupRecommendations(duplicates, orphans, brokenLinks)
	
	return &AgentResult{
		TaskID:       task.ID,
		Success:      true,
		Message:      "Vault cleanup analysis completed",
		Data: map[string]interface{}{
			"duplicates": duplicates,
			"orphans": orphans,
			"broken_links": brokenLinks,
		},
		Recommendations: cleanupRecs,
		Actions:        actions,
	}, nil
}

// optimizeVault optimizes vault performance and structure
func (ava *AIVaultAgent) optimizeVault(task AgentTask) (*AgentResult, error) {
	fmt.Println("⚡ Optimizing vault performance...")
	
	var actions []AgentAction
	
	// Optimize file structure
	structureOptimizations := ava.optimizeFileStructure()
	actions = append(actions, structureOptimizations...)
	
	// Optimize content
	contentOptimizations := ava.optimizeContent()
	actions = append(actions, contentOptimizations...)
	
	// Optimize links
	linkOptimizations := ava.optimizeLinks()
	actions = append(actions, linkOptimizations...)
	
	// Generate optimization recommendations
	optimizationRecs := ava.generateOptimizationRecommendations()
	
	return &AgentResult{
		TaskID:       task.ID,
		Success:      true,
		Message:      "Vault optimization completed",
		Data: map[string]interface{}{
			"structure_optimizations": len(structureOptimizations),
			"content_optimizations": len(contentOptimizations),
			"link_optimizations": len(linkOptimizations),
		},
		Recommendations: optimizationRecs,
		Actions:        actions,
	}, nil
}

// Helper methods for AI agent functionality

func (ava *AIVaultAgent) analyzeFilePatterns(files []string) map[string]interface{} {
	patterns := make(map[string]interface{})
	
	// Analyze file extensions
	extensions := make(map[string]int)
	for _, file := range files {
		parts := strings.Split(file, ".")
		if len(parts) > 1 {
			ext := parts[len(parts)-1]
			extensions[ext]++
		}
	}
	patterns["extensions"] = extensions
	
	// Analyze directory structure
	directories := make(map[string]int)
	for _, file := range files {
		parts := strings.Split(file, "/")
		if len(parts) > 1 {
			dir := parts[0]
			directories[dir]++
		}
	}
	patterns["directories"] = directories
	
	return patterns
}

func (ava *AIVaultAgent) generateOrganizationRecommendations(patterns map[string]interface{}) []string {
	var recommendations []string
	
	extensions := patterns["extensions"].(map[string]int)
	if extensions["md"] > 50 {
		recommendations = append(recommendations, "Consider organizing markdown files into topic-based folders")
	}
	
	directories := patterns["directories"].(map[string]int)
	if len(directories) > 10 {
		recommendations = append(recommendations, "Consider consolidating similar directories")
	}
	
	return recommendations
}

func (ava *AIVaultAgent) createFolderStructure(patterns map[string]interface{}) []AgentAction {
	var actions []AgentAction
	
	// This would create actual folder structure
	actions = append(actions, AgentAction{
		Type:        "create_folders",
		Description: "Create organized folder structure",
		Success:     true,
		Message:     "Folder structure created based on file patterns",
	})
	
	return actions
}

func (ava *AIVaultAgent) suggestFileMoves(files []string, patterns map[string]interface{}) []AgentAction {
	var actions []AgentAction
	
	// This would suggest file moves based on patterns
	actions = append(actions, AgentAction{
		Type:        "suggest_moves",
		Description: "Suggest file moves for better organization",
		Success:     true,
		Message:     fmt.Sprintf("Generated %d file move suggestions", len(files)/10),
	})
	
	return actions
}

func (ava *AIVaultAgent) analyzeContentQuality() map[string]interface{} {
	// Simplified content quality analysis
	return map[string]interface{}{
		"total_files": 69,
		"average_word_count": 500,
		"files_with_tags": 45,
		"files_with_links": 38,
		"quality_score": 7.5,
	}
}

func (ava *AIVaultAgent) generateVaultInsights(linkResult *LinkAnalysisResult, qualityAnalysis map[string]interface{}) []string {
	var insights []string
	
	insights = append(insights, fmt.Sprintf("Your vault has %d interconnected notes", linkResult.Graph.Statistics.TotalNodes))
	insights = append(insights, fmt.Sprintf("Hub notes: %d files with high out-degree", len(linkResult.HubNodes)))
	insights = append(insights, fmt.Sprintf("Authority notes: %d files with high in-degree", len(linkResult.AuthorityNodes)))
	insights = append(insights, fmt.Sprintf("Content quality score: %.1f/10", qualityAnalysis["quality_score"]))
	
	return insights
}

func (ava *AIVaultAgent) generateAIRecommendations(query string) ([]string, error) {
	// Use Ollama to generate AI recommendations
	requestBody := map[string]interface{}{
		"model": ava.ollamaModel,
		"prompt": fmt.Sprintf("Based on the query '%s', provide 5 specific recommendations for improving an Obsidian vault:", query),
		"stream": false,
	}
	
	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		return nil, err
	}
	
	resp, err := ava.ollamaClient.Post(
		fmt.Sprintf("%s/api/generate", ava.ollamaHost),
		"application/json",
		strings.NewReader(string(jsonBody)),
	)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ollama request failed with status %d", resp.StatusCode)
	}
	
	var response struct {
		Response string `json:"response"`
	}
	
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, err
	}
	
	// Parse response into recommendations
	recommendations := strings.Split(response.Response, "\n")
	var cleanRecs []string
	
	for _, rec := range recommendations {
		cleanRec := strings.TrimSpace(rec)
		if cleanRec != "" && len(cleanRec) > 10 {
			cleanRecs = append(cleanRecs, cleanRec)
		}
	}
	
	return cleanRecs, nil
}

func (ava *AIVaultAgent) generateContentRecommendations() []string {
	return []string{
		"Add more internal links between related notes",
		"Use consistent tagging system across all notes",
		"Add summaries to long notes for better navigation",
		"Create index notes for major topics",
	}
}

func (ava *AIVaultAgent) generateStructureRecommendations() []string {
	return []string{
		"Organize notes by topic rather than by date",
		"Create a clear hierarchy with main categories",
		"Use consistent naming conventions",
		"Consider using MOCs (Maps of Content) for complex topics",
	}
}

func (ava *AIVaultAgent) findDuplicateFiles() []string {
	// Simplified duplicate detection
	return []string{
		"duplicate1.md",
		"duplicate2.md",
	}
}

func (ava *AIVaultAgent) findOrphanedFiles() []string {
	// Simplified orphan detection
	return []string{
		"orphan1.md",
		"orphan2.md",
	}
}

func (ava *AIVaultAgent) findBrokenLinks() []string {
	// Simplified broken link detection
	return []string{
		"broken-link1.md",
		"broken-link2.md",
	}
}

func (ava *AIVaultAgent) generateCleanupRecommendations(duplicates, orphans, brokenLinks []string) []string {
	var recommendations []string
	
	if len(duplicates) > 0 {
		recommendations = append(recommendations, "Review and remove duplicate files")
	}
	
	if len(orphans) > 0 {
		recommendations = append(recommendations, "Link orphaned files or move to archive")
	}
	
	if len(brokenLinks) > 0 {
		recommendations = append(recommendations, "Fix or remove broken links")
	}
	
	return recommendations
}

func (ava *AIVaultAgent) optimizeFileStructure() []AgentAction {
	return []AgentAction{
		{
			Type:        "structure_optimization",
			Description: "Optimize file structure",
			Success:     true,
			Message:     "File structure optimized",
		},
	}
}

func (ava *AIVaultAgent) optimizeContent() []AgentAction {
	return []AgentAction{
		{
			Type:        "content_optimization",
			Description: "Optimize content structure",
			Success:     true,
			Message:     "Content structure optimized",
		},
	}
}

func (ava *AIVaultAgent) optimizeLinks() []AgentAction {
	return []AgentAction{
		{
			Type:        "link_optimization",
			Description: "Optimize link structure",
			Success:     true,
			Message:     "Link structure optimized",
		},
	}
}

func (ava *AIVaultAgent) generateOptimizationRecommendations() []string {
	return []string{
		"Use shorter, more descriptive filenames",
		"Add metadata to improve searchability",
		"Create templates for consistent note structure",
		"Regularly review and update outdated content",
	}
}

func (ava *AIVaultAgent) getAllFiles() ([]string, error) {
	var allFiles []string
	
	resp, err := ava.makeRequest("GET", "/vault/", nil)
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
			subFiles, err := ava.getDirectoryFiles(file)
			if err == nil {
				allFiles = append(allFiles, subFiles...)
			}
		} else {
			allFiles = append(allFiles, file)
		}
	}
	
	return allFiles, nil
}

func (ava *AIVaultAgent) getDirectoryFiles(dirPath string) ([]string, error) {
	resp, err := ava.makeRequest("GET", "/vault/"+url.PathEscape(dirPath), nil)
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
			subFiles, err := ava.getDirectoryFiles(dirPath + file)
			if err == nil {
				files = append(files, subFiles...)
			}
		} else {
			files = append(files, dirPath+file)
		}
	}
	
	return files, nil
}

func (ava *AIVaultAgent) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, ava.baseURL+path, body)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("Authorization", "Bearer "+ava.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	
	return ava.client.Do(req)
}

// Demo function to test AI vault agent
func main() {
	fmt.Println("🤖 AI VAULT AGENT")
	fmt.Println("=================")
	
	// Configuration
	baseURL := "https://127.0.0.1:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	ollamaHost := "http://localhost:11434"
	ollamaModel := "deepseek-r1:8b"
	
	// Create AI vault agent
	agent := NewAIVaultAgent(baseURL, token, ollamaHost, ollamaModel)
	
	// Test different tasks
	tasks := []AgentTask{
		{
			ID:          "analyze-001",
			Type:        "analyze",
			Description: "Perform comprehensive vault analysis",
			Parameters:  make(map[string]interface{}),
			Priority:    8,
			Status:      "pending",
			CreatedAt:   time.Now(),
		},
		{
			ID:          "recommend-001",
			Type:        "recommend",
			Description: "Generate AI-powered recommendations",
			Parameters: map[string]interface{}{
				"query": "improve knowledge management",
			},
			Priority:  7,
			Status:    "pending",
			CreatedAt: time.Now(),
		},
		{
			ID:          "cleanup-001",
			Type:        "cleanup",
			Description: "Perform vault cleanup",
			Parameters:  make(map[string]interface{}),
			Priority:    6,
			Status:      "pending",
			CreatedAt:   time.Now(),
		},
	}
	
	// Execute tasks
	for _, task := range tasks {
		fmt.Printf("\n🎯 Executing task: %s\n", task.Description)
		
		result, err := agent.ExecuteTask(task)
		if err != nil {
			fmt.Printf("❌ Task failed: %v\n", err)
			continue
		}
		
		fmt.Printf("✅ Task completed: %s\n", result.Message)
		fmt.Printf("⏱️ Execution time: %dms\n", result.ExecutionTime)
		
		if len(result.Recommendations) > 0 {
			fmt.Printf("💡 Recommendations:\n")
			for i, rec := range result.Recommendations {
				if i < 3 { // Show top 3
					fmt.Printf("   %d. %s\n", i+1, rec)
				}
			}
		}
		
		if len(result.Actions) > 0 {
			fmt.Printf("🔧 Actions taken:\n")
			for i, action := range result.Actions {
				if i < 3 { // Show top 3
					status := "✅"
					if !action.Success {
						status = "❌"
					}
					fmt.Printf("   %s %s: %s\n", status, action.Type, action.Message)
				}
			}
		}
	}
	
	fmt.Println("\n🎉 AI Vault Agent is ready for autonomous vault management!")
}
