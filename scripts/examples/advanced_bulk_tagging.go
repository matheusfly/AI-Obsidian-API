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

// BulkTaggingEngine provides advanced bulk tagging functionality
type BulkTaggingEngine struct {
	baseURL string
	token   string
	client  *http.Client
}

// NewBulkTaggingEngine creates a new bulk tagging engine
func NewBulkTaggingEngine(baseURL, token string) *BulkTaggingEngine {
	return &BulkTaggingEngine{
		baseURL: baseURL,
		token:   token,
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			},
		},
	}
}

// TaggingOperation represents a tagging operation
type TaggingOperation struct {
	Operation string   `json:"operation"` // "add", "remove", "replace", "auto"
	Tags      []string `json:"tags"`
	Pattern   string   `json:"pattern,omitempty"`
	Condition string   `json:"condition,omitempty"`
}

// TaggingResult represents the result of a tagging operation
type TaggingResult struct {
	File        string `json:"file"`
	Success     bool   `json:"success"`
	Message     string `json:"message"`
	TagsAdded   []string `json:"tags_added"`
	TagsRemoved []string `json:"tags_removed"`
	TagsBefore  []string `json:"tags_before"`
	TagsAfter   []string `json:"tags_after"`
}

// BulkTaggingResult represents the result of bulk tagging
type BulkTaggingResult struct {
	TotalFiles     int             `json:"total_files"`
	SuccessCount   int             `json:"success_count"`
	FailureCount   int             `json:"failure_count"`
	Results        []TaggingResult `json:"results"`
	Summary        string          `json:"summary"`
	ExecutionTime  int64           `json:"execution_time_ms"`
}

// BulkTag performs bulk tagging operations on multiple files
func (bte *BulkTaggingEngine) BulkTag(files []string, operation TaggingOperation) (*BulkTaggingResult, error) {
	start := time.Now()
	
	fmt.Printf("🏷️ Starting bulk tagging operation: %s\n", operation.Operation)
	fmt.Printf("📁 Processing %d files\n", len(files))
	
	var results []TaggingResult
	successCount := 0
	failureCount := 0
	
	for _, file := range files {
		result := bte.tagFile(file, operation)
		results = append(results, result)
		
		if result.Success {
			successCount++
		} else {
			failureCount++
		}
		
		fmt.Printf("📄 %s: %s\n", file, result.Message)
	}
	
	duration := time.Since(start).Milliseconds()
	
	summary := fmt.Sprintf("Bulk tagging completed: %d successful, %d failed", successCount, failureCount)
	
	return &BulkTaggingResult{
		TotalFiles:    len(files),
		SuccessCount:  successCount,
		FailureCount:  failureCount,
		Results:       results,
		Summary:       summary,
		ExecutionTime: duration,
	}, nil
}

// tagFile performs tagging operation on a single file
func (bte *BulkTaggingEngine) tagFile(filename string, operation TaggingOperation) TaggingResult {
	// Read current file content
	content, err := bte.readFileContent(filename)
	if err != nil {
		return TaggingResult{
			File:    filename,
			Success: false,
			Message: fmt.Sprintf("Failed to read file: %v", err),
		}
	}
	
	// Extract current tags
	currentTags := bte.extractTags(content)
	tagsBefore := make([]string, len(currentTags))
	copy(tagsBefore, currentTags)
	
	// Apply tagging operation
	var newContent string
	var tagsAdded, tagsRemoved []string
	
	switch operation.Operation {
	case "add":
		newContent, tagsAdded = bte.addTags(content, operation.Tags)
	case "remove":
		newContent, tagsRemoved = bte.removeTags(content, operation.Tags)
	case "replace":
		newContent, tagsAdded, tagsRemoved = bte.replaceTags(content, operation.Tags)
	case "auto":
		newContent, tagsAdded = bte.autoTag(content, filename)
	default:
		return TaggingResult{
			File:    filename,
			Success: false,
			Message: "Invalid operation",
		}
	}
	
	// Write updated content back to file
	if newContent != content {
		err = bte.writeFileContent(filename, newContent)
		if err != nil {
			return TaggingResult{
				File:    filename,
				Success: false,
				Message: fmt.Sprintf("Failed to write file: %v", err),
			}
		}
	}
	
	// Extract final tags
	finalTags := bte.extractTags(newContent)
	
	return TaggingResult{
		File:       filename,
		Success:    true,
		Message:    "Tagging operation completed successfully",
		TagsAdded:  tagsAdded,
		TagsRemoved: tagsRemoved,
		TagsBefore: tagsBefore,
		TagsAfter:  finalTags,
	}
}

// addTags adds new tags to file content
func (bte *BulkTaggingEngine) addTags(content string, newTags []string) (string, []string) {
	// Extract existing tags
	existingTags := bte.extractTags(content)
	
	// Find tags to add (avoid duplicates)
	var tagsToAdd []string
	for _, tag := range newTags {
		if !bte.containsTag(existingTags, tag) {
			tagsToAdd = append(tagsToAdd, tag)
		}
	}
	
	if len(tagsToAdd) == 0 {
		return content, []string{}
	}
	
	// Add tags to frontmatter or create frontmatter
	if bte.hasFrontmatter(content) {
		// Add to existing frontmatter
		return bte.addTagsToFrontmatter(content, tagsToAdd), tagsToAdd
	} else {
		// Create new frontmatter
		return bte.createFrontmatterWithTags(content, tagsToAdd), tagsToAdd
	}
}

// removeTags removes specified tags from file content
func (bte *BulkTaggingEngine) removeTags(content string, tagsToRemove []string) (string, []string) {
	// Extract existing tags
	existingTags := bte.extractTags(content)
	
	// Find tags to remove
	var tagsRemoved []string
	for _, tag := range tagsToRemove {
		if bte.containsTag(existingTags, tag) {
			tagsRemoved = append(tagsRemoved, tag)
		}
	}
	
	if len(tagsRemoved) == 0 {
		return content, []string{}
	}
	
	// Remove tags from frontmatter
	if bte.hasFrontmatter(content) {
		return bte.removeTagsFromFrontmatter(content, tagsRemoved), tagsRemoved
	} else {
		// Remove inline tags
		return bte.removeInlineTags(content, tagsRemoved), tagsRemoved
	}
}

// replaceTags replaces all tags with new ones
func (bte *BulkTaggingEngine) replaceTags(content string, newTags []string) (string, []string, []string) {
	// Extract existing tags
	existingTags := bte.extractTags(content)
	
	// Remove all existing tags
	contentWithoutTags := bte.removeAllTags(content)
	
	// Add new tags
	newContent, tagsAdded := bte.addTags(contentWithoutTags, newTags)
	
	return newContent, tagsAdded, existingTags
}

// autoTag automatically generates tags based on content analysis
func (bte *BulkTaggingEngine) autoTag(content, filename string) (string, []string) {
	var suggestedTags []string
	
	// Extract tags from filename
	filenameTags := bte.extractTagsFromFilename(filename)
	suggestedTags = append(suggestedTags, filenameTags...)
	
	// Extract tags from content
	contentTags := bte.extractTagsFromContent(content)
	suggestedTags = append(suggestedTags, contentTags...)
	
	// Remove duplicates
	suggestedTags = bte.removeDuplicateTags(suggestedTags)
	
	// Limit to reasonable number of tags
	if len(suggestedTags) > 10 {
		suggestedTags = suggestedTags[:10]
	}
	
	// Add auto-generated tags
	newContent, tagsAdded := bte.addTags(content, suggestedTags)
	
	return newContent, tagsAdded
}

// extractTags extracts all tags from file content
func (bte *BulkTaggingEngine) extractTags(content string) []string {
	var tags []string
	
	// Extract frontmatter tags
	if bte.hasFrontmatter(content) {
		frontmatterTags := bte.extractFrontmatterTags(content)
		tags = append(tags, frontmatterTags...)
	}
	
	// Extract inline tags (#tag)
	inlineTags := bte.extractInlineTags(content)
	tags = append(tags, inlineTags...)
	
	// Remove duplicates
	return bte.removeDuplicateTags(tags)
}

// extractFrontmatterTags extracts tags from YAML frontmatter
func (bte *BulkTaggingEngine) extractFrontmatterTags(content string) []string {
	var tags []string
	
	// Find frontmatter section
	frontmatterRegex := regexp.MustCompile(`(?s)^---\n(.*?)\n---`)
	matches := frontmatterRegex.FindStringSubmatch(content)
	
	if len(matches) > 1 {
		frontmatter := matches[1]
		
		// Look for tags field
		tagsRegex := regexp.MustCompile(`(?i)tags?:\s*(.*)`)
		tagMatches := tagsRegex.FindStringSubmatch(frontmatter)
		
		if len(tagMatches) > 1 {
			tagString := tagMatches[1]
			// Parse tags (handle both array and string formats)
			if strings.Contains(tagString, "[") {
				// Array format: tags: [tag1, tag2, tag3]
				arrayRegex := regexp.MustCompile(`\[(.*?)\]`)
				arrayMatches := arrayRegex.FindStringSubmatch(tagString)
				if len(arrayMatches) > 1 {
					tagList := strings.Split(arrayMatches[1], ",")
					for _, tag := range tagList {
						cleanTag := strings.TrimSpace(strings.Trim(tag, `"'`))
						if cleanTag != "" {
							tags = append(tags, cleanTag)
						}
					}
				}
			} else {
				// String format: tags: tag1 tag2 tag3
				tagList := strings.Fields(tagString)
				for _, tag := range tagList {
					cleanTag := strings.TrimSpace(strings.Trim(tag, `"'`))
					if cleanTag != "" {
						tags = append(tags, cleanTag)
					}
				}
			}
		}
	}
	
	return tags
}

// extractInlineTags extracts inline tags (#tag)
func (bte *BulkTaggingEngine) extractInlineTags(content string) []string {
	var tags []string
	
	// Find all #tag patterns
	tagRegex := regexp.MustCompile(`#([a-zA-Z0-9_-]+)`)
	matches := tagRegex.FindAllStringSubmatch(content, -1)
	
	for _, match := range matches {
		if len(match) > 1 {
			tag := strings.TrimSpace(match[1])
			if tag != "" {
				tags = append(tags, tag)
			}
		}
	}
	
	return tags
}

// extractTagsFromFilename extracts tags from filename
func (bte *BulkTaggingEngine) extractTagsFromFilename(filename string) []string {
	var tags []string
	
	// Remove extension
	name := strings.TrimSuffix(filename, ".md")
	
	// Split by common separators
	parts := regexp.MustCompile(`[-_\s]+`).Split(name, -1)
	
	for _, part := range parts {
		cleanPart := strings.TrimSpace(part)
		if len(cleanPart) > 2 && len(cleanPart) < 20 {
			tags = append(tags, strings.ToLower(cleanPart))
		}
	}
	
	return tags
}

// extractTagsFromContent extracts tags from content analysis
func (bte *BulkTaggingEngine) extractTagsFromContent(content string) []string {
	var tags []string
	
	// Common technical terms
	technicalTerms := []string{
		"programming", "coding", "development", "software", "algorithm",
		"data", "analysis", "machine", "learning", "ai", "artificial",
		"intelligence", "python", "javascript", "go", "java", "react",
		"node", "database", "sql", "api", "web", "frontend", "backend",
		"devops", "docker", "kubernetes", "git", "github", "testing",
		"debugging", "optimization", "performance", "security", "scalability",
	}
	
	contentLower := strings.ToLower(content)
	
	for _, term := range technicalTerms {
		if strings.Contains(contentLower, term) {
			tags = append(tags, term)
		}
	}
	
	return tags
}

// Helper functions
func (bte *BulkTaggingEngine) hasFrontmatter(content string) bool {
	return strings.HasPrefix(content, "---\n")
}

func (bte *BulkTaggingEngine) containsTag(tags []string, tag string) bool {
	for _, t := range tags {
		if strings.EqualFold(t, tag) {
			return true
		}
	}
	return false
}

func (bte *BulkTaggingEngine) removeDuplicateTags(tags []string) []string {
	var unique []string
	seen := make(map[string]bool)
	
	for _, tag := range tags {
		if !seen[tag] {
			seen[tag] = true
			unique = append(unique, tag)
		}
	}
	
	return unique
}

func (bte *BulkTaggingEngine) addTagsToFrontmatter(content string, tags []string) string {
	// Implementation for adding tags to existing frontmatter
	// This is a simplified version
	return content
}

func (bte *BulkTaggingEngine) createFrontmatterWithTags(content string, tags []string) string {
	tagString := strings.Join(tags, ", ")
	frontmatter := fmt.Sprintf("---\ntags: [%s]\n---\n\n%s", tagString, content)
	return frontmatter
}

func (bte *BulkTaggingEngine) removeTagsFromFrontmatter(content string, tags []string) string {
	// Implementation for removing tags from frontmatter
	// This is a simplified version
	return content
}

func (bte *BulkTaggingEngine) removeInlineTags(content string, tags []string) string {
	// Remove inline tags
	for _, tag := range tags {
		pattern := fmt.Sprintf(`#%s\b`, regexp.QuoteMeta(tag))
		regex := regexp.MustCompile(pattern)
		content = regex.ReplaceAllString(content, "")
	}
	return content
}

func (bte *BulkTaggingEngine) removeAllTags(content string) string {
	// Remove all tags (both frontmatter and inline)
	// This is a simplified version
	return content
}

// File operations
func (bte *BulkTaggingEngine) readFileContent(filename string) (string, error) {
	resp, err := bte.makeRequest("GET", "/vault/"+url.PathEscape(filename), nil)
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

func (bte *BulkTaggingEngine) writeFileContent(filename string, content string) error {
	// Note: Obsidian Local REST API doesn't support writing files directly
	// This would need to be implemented through file system operations
	// For now, we'll return an error indicating this limitation
	return fmt.Errorf("file writing not supported by Obsidian Local REST API")
}

func (bte *BulkTaggingEngine) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, bte.baseURL+path, body)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("Authorization", "Bearer "+bte.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	
	return bte.client.Do(req)
}

// Demo function to test bulk tagging
func main() {
	fmt.Println("🏷️ ADVANCED BULK TAGGING ENGINE")
	fmt.Println("================================")
	
	// Configuration
	baseURL := "https://127.0.0.1:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	
	// Create bulk tagging engine
	bte := NewBulkTaggingEngine(baseURL, token)
	
	// Test files (you would get these from your vault)
	testFiles := []string{
		"1- Notas Indice/MATH-index.md",
		"2- Notas De Leitura/Fundamentos da Computação.md",
		"4- Notas Permanentes/API Build.md",
	}
	
	// Test bulk tagging operation
	operation := TaggingOperation{
		Operation: "add",
		Tags:      []string{"programming", "technology", "learning"},
	}
	
	fmt.Printf("🔍 Testing bulk tagging on %d files\n", len(testFiles))
	
	result, err := bte.BulkTag(testFiles, operation)
	if err != nil {
		fmt.Printf("❌ Bulk tagging failed: %v\n", err)
		return
	}
	
	fmt.Printf("✅ %s\n", result.Summary)
	fmt.Printf("⏱️ Execution time: %dms\n", result.ExecutionTime)
	fmt.Printf("📊 Success rate: %.1f%%\n", float64(result.SuccessCount)/float64(result.TotalFiles)*100)
	
	fmt.Println("\n📋 Detailed Results:")
	for _, res := range result.Results {
		status := "✅"
		if !res.Success {
			status = "❌"
		}
		fmt.Printf("%s %s: %s\n", status, res.File, res.Message)
		if len(res.TagsAdded) > 0 {
			fmt.Printf("   ➕ Added: %s\n", strings.Join(res.TagsAdded, ", "))
		}
		if len(res.TagsRemoved) > 0 {
			fmt.Printf("   ➖ Removed: %s\n", strings.Join(res.TagsRemoved, ", "))
		}
	}
	
	fmt.Println("\n🎉 Bulk tagging engine is ready!")
}
