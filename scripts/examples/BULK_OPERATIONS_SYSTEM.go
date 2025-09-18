package main

import (
	"fmt"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"
)

// BulkOperationsSystem provides comprehensive bulk operations for vault management
type BulkOperationsSystem struct {
	apiPipeline     *APIPipeline
	tagManager      *BulkTagManager
	linkManager     *BulkLinkManager
	organizer       *BulkOrganizer
	analyzer        *BulkAnalyzer
	processor       *BulkProcessor
	validator       *BulkValidator
	progressTracker *ProgressTracker
	mutex           sync.RWMutex
}

// BulkTagManager handles bulk tagging operations
type BulkTagManager struct {
	apiPipeline *APIPipeline
	tagIndex    map[string][]string // tag -> files
	fileTags    map[string][]string // file -> tags
	mutex       sync.RWMutex
}

// BulkLinkManager handles bulk linking operations
type BulkLinkManager struct {
	apiPipeline *APIPipeline
	linkGraph   map[string][]string // file -> linked files
	backlinks   map[string][]string // file -> backlinks
	mutex       sync.RWMutex
}

// BulkOrganizer handles bulk organization operations
type BulkOrganizer struct {
	apiPipeline *APIPipeline
	categories  map[string][]string // category -> files
	rules       []OrganizationRule
	mutex       sync.RWMutex
}

// OrganizationRule represents an organization rule
type OrganizationRule struct {
	Name        string
	Pattern     string
	Action      string
	Destination string
	Priority    int
	Enabled     bool
}

// BulkAnalyzer analyzes vault content for bulk operations
type BulkAnalyzer struct {
	apiPipeline *APIPipeline
	metrics     map[string]interface{}
	mutex       sync.RWMutex
}

// BulkProcessor processes bulk operations
type BulkProcessor struct {
	apiPipeline *APIPipeline
	workers     int
	queue       chan BulkOperation
	results     chan BulkOperationResult
	mutex       sync.RWMutex
}

// BulkValidator validates bulk operations
type BulkValidator struct {
	rules map[string]ValidationRule
	mutex sync.RWMutex
}

// ProgressTracker tracks progress of bulk operations
type ProgressTracker struct {
	operations map[string]*OperationProgress
	mutex      sync.RWMutex
}

// OperationProgress represents progress of an operation
type OperationProgress struct {
	OperationID string
	Total       int
	Completed   int
	Failed      int
	StartTime   time.Time
	EndTime     time.Time
	Status      string // "running", "completed", "failed", "cancelled"
	Errors      []string
}

// BulkOperation represents a bulk operation
type BulkOperation struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"` // "tag", "link", "organize", "analyze", "process"
	Files       []string               `json:"files"`
	Parameters  map[string]interface{} `json:"parameters"`
	Options     map[string]interface{} `json:"options"`
	Priority    int                    `json:"priority"`
	CreatedAt   time.Time              `json:"created_at"`
	StartedAt   time.Time              `json:"started_at,omitempty"`
	CompletedAt time.Time              `json:"completed_at,omitempty"`
}

// BulkOperationResult represents the result of a bulk operation
type BulkOperationResult struct {
	OperationID string                 `json:"operation_id"`
	Success     bool                   `json:"success"`
	Message     string                 `json:"message"`
	Data        interface{}            `json:"data,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
	Duration    time.Duration          `json:"duration"`
	Timestamp   time.Time              `json:"timestamp"`
}

// NewBulkOperationsSystem creates a new bulk operations system
func NewBulkOperationsSystem(apiPipeline *APIPipeline) *BulkOperationsSystem {
	return &BulkOperationsSystem{
		apiPipeline: apiPipeline,
		tagManager: &BulkTagManager{
			apiPipeline: apiPipeline,
			tagIndex:    make(map[string][]string),
			fileTags:    make(map[string][]string),
		},
		linkManager: &BulkLinkManager{
			apiPipeline: apiPipeline,
			linkGraph:   make(map[string][]string),
			backlinks:   make(map[string][]string),
		},
		organizer: &BulkOrganizer{
			apiPipeline: apiPipeline,
			categories:  make(map[string][]string),
			rules:       make([]OrganizationRule, 0),
		},
		analyzer: &BulkAnalyzer{
			apiPipeline: apiPipeline,
			metrics:     make(map[string]interface{}),
		},
		processor: &BulkProcessor{
			apiPipeline: apiPipeline,
			workers:     5,
			queue:       make(chan BulkOperation, 100),
			results:     make(chan BulkOperationResult, 100),
		},
		validator: &BulkValidator{
			rules: make(map[string]ValidationRule),
		},
		progressTracker: &ProgressTracker{
			operations: make(map[string]*OperationProgress),
		},
	}
}

// BulkTagOperations performs bulk tagging operations
func (bos *BulkOperationsSystem) BulkTagOperations(operation *BulkOperation) *BulkOperationResult {
	start := time.Now()
	result := &BulkOperationResult{
		OperationID: operation.ID,
		Success:     false,
		Timestamp:   time.Now(),
	}

	// Validate operation
	if err := bos.validator.ValidateBulkOperation(operation); err != nil {
		result.Message = fmt.Sprintf("Validation failed: %v", err)
		return result
	}

	// Get operation parameters
	action, ok := operation.Parameters["action"].(string)
	if !ok {
		result.Message = "Action parameter is required"
		return result
	}

	tag, ok := operation.Parameters["tag"].(string)
	if !ok {
		result.Message = "Tag parameter is required"
		return result
	}

	// Execute bulk tagging
	var successCount, failCount int
	var errors []string

	for _, file := range operation.Files {
		fileResult := bos.tagManager.TagFile(file, tag, action)
		if fileResult.Success {
			successCount++
		} else {
			failCount++
			errors = append(errors, fmt.Sprintf("%s: %s", file, fileResult.Message))
		}
	}

	// Update progress
	bos.progressTracker.UpdateProgress(operation.ID, len(operation.Files), successCount, failCount, errors)

	result.Success = successCount > 0
	result.Message = fmt.Sprintf("Tagged %d files successfully, %d failed", successCount, failCount)
	result.Data = map[string]interface{}{
		"success_count": successCount,
		"fail_count":    failCount,
		"errors":        errors,
		"action":        action,
		"tag":           tag,
	}
	result.Duration = time.Since(start)

	return result
}

// BulkLinkOperations performs bulk linking operations
func (bos *BulkOperationsSystem) BulkLinkOperations(operation *BulkOperation) *BulkOperationResult {
	start := time.Now()
	result := &BulkOperationResult{
		OperationID: operation.ID,
		Success:     false,
		Timestamp:   time.Now(),
	}

	// Validate operation
	if err := bos.validator.ValidateBulkOperation(operation); err != nil {
		result.Message = fmt.Sprintf("Validation failed: %v", err)
		return result
	}

	// Get operation parameters
	action, ok := operation.Parameters["action"].(string)
	if !ok {
		result.Message = "Action parameter is required"
		return result
	}

	linkPattern, ok := operation.Parameters["link_pattern"].(string)
	if !ok {
		result.Message = "Link pattern parameter is required"
		return result
	}

	// Execute bulk linking
	var successCount, failCount int
	var errors []string

	for _, file := range operation.Files {
		fileResult := bos.linkManager.LinkFile(file, linkPattern, action)
		if fileResult.Success {
			successCount++
		} else {
			failCount++
			errors = append(errors, fmt.Sprintf("%s: %s", file, fileResult.Message))
		}
	}

	// Update progress
	bos.progressTracker.UpdateProgress(operation.ID, len(operation.Files), successCount, failCount, errors)

	result.Success = successCount > 0
	result.Message = fmt.Sprintf("Linked %d files successfully, %d failed", successCount, failCount)
	result.Data = map[string]interface{}{
		"success_count": successCount,
		"fail_count":    failCount,
		"errors":        errors,
		"action":        action,
		"link_pattern":  linkPattern,
	}
	result.Duration = time.Since(start)

	return result
}

// BulkOrganizeOperations performs bulk organization operations
func (bos *BulkOperationsSystem) BulkOrganizeOperations(operation *BulkOperation) *BulkOperationResult {
	start := time.Now()
	result := &BulkOperationResult{
		OperationID: operation.ID,
		Success:     false,
		Timestamp:   time.Now(),
	}

	// Validate operation
	if err := bos.validator.ValidateBulkOperation(operation); err != nil {
		result.Message = fmt.Sprintf("Validation failed: %v", err)
		return result
	}

	// Get operation parameters
	action, ok := operation.Parameters["action"].(string)
	if !ok {
		result.Message = "Action parameter is required"
		return result
	}

	// Execute bulk organization
	var successCount, failCount int
	var errors []string

	for _, file := range operation.Files {
		fileResult := bos.organizer.OrganizeFile(file, action, operation.Parameters)
		if fileResult.Success {
			successCount++
		} else {
			failCount++
			errors = append(errors, fmt.Sprintf("%s: %s", file, fileResult.Message))
		}
	}

	// Update progress
	bos.progressTracker.UpdateProgress(operation.ID, len(operation.Files), successCount, failCount, errors)

	result.Success = successCount > 0
	result.Message = fmt.Sprintf("Organized %d files successfully, %d failed", successCount, failCount)
	result.Data = map[string]interface{}{
		"success_count": successCount,
		"fail_count":    failCount,
		"errors":        errors,
		"action":        action,
	}
	result.Duration = time.Since(start)

	return result
}

// BulkAnalyzeOperations performs bulk analysis operations
func (bos *BulkOperationsSystem) BulkAnalyzeOperations(operation *BulkOperation) *BulkOperationResult {
	start := time.Now()
	result := &BulkOperationResult{
		OperationID: operation.ID,
		Success:     false,
		Timestamp:   time.Now(),
	}

	// Execute bulk analysis
	analysisResult := bos.analyzer.AnalyzeFiles(operation.Files, operation.Parameters)
	if !analysisResult.Success {
		result.Message = analysisResult.Message
		return result
	}

	result.Success = true
	result.Message = "Analysis completed successfully"
	result.Data = analysisResult.Data
	result.Duration = time.Since(start)

	return result
}

// ProcessBulkOperation processes a bulk operation
func (bos *BulkOperationsSystem) ProcessBulkOperation(operation *BulkOperation) *BulkOperationResult {
	// Add to queue
	bos.processor.queue <- *operation

	// Wait for result
	select {
	case result := <-bos.processor.results:
		return &result
	case <-time.After(30 * time.Second):
		return &BulkOperationResult{
			OperationID: operation.ID,
			Success:     false,
			Message:     "Operation timeout",
			Timestamp:   time.Now(),
		}
	}
}

// GetOperationProgress gets the progress of an operation
func (bos *BulkOperationsSystem) GetOperationProgress(operationID string) *OperationProgress {
	return bos.progressTracker.GetProgress(operationID)
}

// CancelOperation cancels a running operation
func (bos *BulkOperationsSystem) CancelOperation(operationID string) bool {
	return bos.progressTracker.CancelOperation(operationID)
}

// Tag Manager methods
func (btm *BulkTagManager) TagFile(filename, tag, action string) *BulkOperationResult {
	result := &BulkOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Read file content
	apiResult := btm.apiPipeline.ReadVaultFile(filename)
	if !apiResult.Success {
		result.Message = fmt.Sprintf("Failed to read file: %v", apiResult.Error)
		return result
	}

	content := btm.getContentString(apiResult.Data)

	// Apply tagging action
	var newContent string
	var err error

	switch action {
	case "add":
		newContent, err = btm.addTag(content, tag)
	case "remove":
		newContent, err = btm.removeTag(content, tag)
	case "replace":
		oldTag, ok := btm.getParameter("old_tag")
		if !ok {
			result.Message = "Old tag parameter required for replace action"
			return result
		}
		newContent, err = btm.replaceTag(content, oldTag, tag)
	default:
		result.Message = "Invalid action: " + action
		return result
	}

	if err != nil {
		result.Message = fmt.Sprintf("Failed to apply tag: %v", err)
		return result
	}

	// Update file if content changed
	if newContent != content {
		updateResult := btm.apiPipeline.UpdateVaultFile(filename, newContent)
		if !updateResult.Success {
			result.Message = fmt.Sprintf("Failed to update file: %v", updateResult.Error)
			return result
		}
	}

	// Update tag index
	btm.updateTagIndex(filename, tag, action)

	result.Success = true
	result.Message = fmt.Sprintf("Successfully %sed tag '%s' in file '%s'", action, tag, filename)
	return result
}

func (btm *BulkTagManager) addTag(content, tag string) (string, error) {
	// Check if tag already exists
	if strings.Contains(content, "#"+tag) {
		return content, nil
	}

	// Add tag at the end of the file
	return content + "\n\n#" + tag, nil
}

func (btm *BulkTagManager) removeTag(content, tag string) (string, error) {
	// Remove tag from content
	tagRegex := regexp.MustCompile(`#` + regexp.QuoteMeta(tag) + `\b`)
	return tagRegex.ReplaceAllString(content, ""), nil
}

func (btm *BulkTagManager) replaceTag(content, oldTag, newTag string) (string, error) {
	// Replace old tag with new tag
	tagRegex := regexp.MustCompile(`#` + regexp.QuoteMeta(oldTag) + `\b`)
	return tagRegex.ReplaceAllString(content, "#"+newTag), nil
}

func (btm *BulkTagManager) getParameter(key string) (string, bool) {
	// This would get parameters from the operation context
	// For now, return empty
	return "", false
}

func (btm *BulkTagManager) updateTagIndex(filename, tag, action string) {
	btm.mutex.Lock()
	defer btm.mutex.Unlock()

	switch action {
	case "add":
		// Add to tag index
		btm.tagIndex[tag] = append(btm.tagIndex[tag], filename)
		// Add to file tags
		btm.fileTags[filename] = append(btm.fileTags[filename], tag)
	case "remove":
		// Remove from tag index
		if files, exists := btm.tagIndex[tag]; exists {
			for i, file := range files {
				if file == filename {
					btm.tagIndex[tag] = append(files[:i], files[i+1:]...)
					break
				}
			}
		}
		// Remove from file tags
		if tags, exists := btm.fileTags[filename]; exists {
			for i, t := range tags {
				if t == tag {
					btm.fileTags[filename] = append(tags[:i], tags[i+1:]...)
					break
				}
			}
		}
	}
}

func (btm *BulkTagManager) getContentString(data interface{}) string {
	if content, ok := data.(string); ok {
		return content
	}
	return ""
}

// Link Manager methods
func (blm *BulkLinkManager) LinkFile(filename, linkPattern, action string) *BulkOperationResult {
	result := &BulkOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Read file content
	apiResult := blm.apiPipeline.ReadVaultFile(filename)
	if !apiResult.Success {
		result.Message = fmt.Sprintf("Failed to read file: %v", apiResult.Error)
		return result
	}

	content := blm.getContentString(apiResult.Data)

	// Apply linking action
	var newContent string
	var err error

	switch action {
	case "add":
		newContent, err = blm.addLink(content, linkPattern)
	case "remove":
		newContent, err = blm.removeLink(content, linkPattern)
	case "update":
		oldPattern, ok := blm.getParameter("old_pattern")
		if !ok {
			result.Message = "Old pattern parameter required for update action"
			return result
		}
		newContent, err = blm.updateLink(content, oldPattern, linkPattern)
	default:
		result.Message = "Invalid action: " + action
		return result
	}

	if err != nil {
		result.Message = fmt.Sprintf("Failed to apply link: %v", err)
		return result
	}

	// Update file if content changed
	if newContent != content {
		updateResult := blm.apiPipeline.UpdateVaultFile(filename, newContent)
		if !updateResult.Success {
			result.Message = fmt.Sprintf("Failed to update file: %v", updateResult.Error)
			return result
		}
	}

	// Update link index
	blm.updateLinkIndex(filename, linkPattern, action)

	result.Success = true
	result.Message = fmt.Sprintf("Successfully %sed link pattern '%s' in file '%s'", action, linkPattern, filename)
	return result
}

func (blm *BulkLinkManager) addLink(content, linkPattern string) (string, error) {
	// Add link at the end of the file
	return content + "\n\n[[" + linkPattern + "]]", nil
}

func (blm *BulkLinkManager) removeLink(content, linkPattern string) (string, error) {
	// Remove link from content
	linkRegex := regexp.MustCompile(`\[\[` + regexp.QuoteMeta(linkPattern) + `\]\]`)
	return linkRegex.ReplaceAllString(content, ""), nil
}

func (blm *BulkLinkManager) updateLink(content, oldPattern, newPattern string) (string, error) {
	// Replace old link with new link
	linkRegex := regexp.MustCompile(`\[\[` + regexp.QuoteMeta(oldPattern) + `\]\]`)
	return linkRegex.ReplaceAllString(content, "[["+newPattern+"]]"), nil
}

func (blm *BulkLinkManager) getParameter(key string) (string, bool) {
	// This would get parameters from the operation context
	// For now, return empty
	return "", false
}

func (blm *BulkLinkManager) updateLinkIndex(filename, linkPattern, action string) {
	blm.mutex.Lock()
	defer blm.mutex.Unlock()

	switch action {
	case "add":
		// Add to link graph
		blm.linkGraph[filename] = append(blm.linkGraph[filename], linkPattern)
		// Add to backlinks
		blm.backlinks[linkPattern] = append(blm.backlinks[linkPattern], filename)
	case "remove":
		// Remove from link graph
		if links, exists := blm.linkGraph[filename]; exists {
			for i, link := range links {
				if link == linkPattern {
					blm.linkGraph[filename] = append(links[:i], links[i+1:]...)
					break
				}
			}
		}
		// Remove from backlinks
		if backlinks, exists := blm.backlinks[linkPattern]; exists {
			for i, backlink := range backlinks {
				if backlink == filename {
					blm.backlinks[linkPattern] = append(backlinks[:i], backlinks[i+1:]...)
					break
				}
			}
		}
	}
}

func (blm *BulkLinkManager) getContentString(data interface{}) string {
	if content, ok := data.(string); ok {
		return content
	}
	return ""
}

// Organizer methods
func (bo *BulkOrganizer) OrganizeFile(filename, action string, parameters map[string]interface{}) *BulkOperationResult {
	result := &BulkOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Read file content
	apiResult := bo.apiPipeline.ReadVaultFile(filename)
	if !apiResult.Success {
		result.Message = fmt.Sprintf("Failed to read file: %v", apiResult.Error)
		return result
	}

	content := bo.getContentString(apiResult.Data)

	// Apply organization action
	var newContent string
	var err error

	switch action {
	case "categorize":
		category, ok := parameters["category"].(string)
		if !ok {
			result.Message = "Category parameter required for categorize action"
			return result
		}
		newContent, err = bo.categorizeFile(content, category)
	case "structure":
		template, ok := parameters["template"].(string)
		if !ok {
			result.Message = "Template parameter required for structure action"
			return result
		}
		newContent, err = bo.structureFile(content, template)
	case "cleanup":
		newContent, err = bo.cleanupFile(content)
	default:
		result.Message = "Invalid action: " + action
		return result
	}

	if err != nil {
		result.Message = fmt.Sprintf("Failed to organize file: %v", err)
		return result
	}

	// Update file if content changed
	if newContent != content {
		updateResult := bo.apiPipeline.UpdateVaultFile(filename, newContent)
		if !updateResult.Success {
			result.Message = fmt.Sprintf("Failed to update file: %v", updateResult.Error)
			return result
		}
	}

	// Update category index
	bo.updateCategoryIndex(filename, action, parameters)

	result.Success = true
	result.Message = fmt.Sprintf("Successfully %sed file '%s'", action, filename)
	return result
}

func (bo *BulkOrganizer) categorizeFile(content, category string) (string, error) {
	// Add category tag to content
	if !strings.Contains(content, "#"+category) {
		content += "\n\n#" + category
	}
	return content, nil
}

func (bo *BulkOrganizer) structureFile(content, template string) (string, error) {
	// Apply template structure to content
	// This would implement template-based structuring
	return content, nil
}

func (bo *BulkOrganizer) cleanupFile(content string) (string, error) {
	// Clean up content (remove extra spaces, fix formatting, etc.)
	// Remove multiple consecutive newlines
	content = regexp.MustCompile(`\n{3,}`).ReplaceAllString(content, "\n\n")
	// Remove trailing spaces
	content = regexp.MustCompile(`[ \t]+$`).ReplaceAllString(content, "")
	return content, nil
}

func (bo *BulkOrganizer) updateCategoryIndex(filename, action string, parameters map[string]interface{}) {
	bo.mutex.Lock()
	defer bo.mutex.Unlock()

	if action == "categorize" {
		if category, ok := parameters["category"].(string); ok {
			bo.categories[category] = append(bo.categories[category], filename)
		}
	}
}

func (bo *BulkOrganizer) getContentString(data interface{}) string {
	if content, ok := data.(string); ok {
		return content
	}
	return ""
}

// Analyzer methods
func (ba *BulkAnalyzer) AnalyzeFiles(files []string, parameters map[string]interface{}) *BulkOperationResult {
	result := &BulkOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Analyze files
	analysis := make(map[string]interface{})

	for _, file := range files {
		fileAnalysis := ba.analyzeFile(file)
		analysis[file] = fileAnalysis
	}

	// Generate summary
	summary := ba.generateSummary(analysis)

	result.Success = true
	result.Message = "Analysis completed successfully"
	result.Data = map[string]interface{}{
		"files":   analysis,
		"summary": summary,
	}

	return result
}

func (ba *BulkAnalyzer) analyzeFile(filename string) map[string]interface{} {
	// Read file content
	apiResult := ba.apiPipeline.ReadVaultFile(filename)
	if !apiResult.Success {
		return map[string]interface{}{
			"error": apiResult.Error.Error(),
		}
	}

	content := ba.getContentString(apiResult.Data)

	// Analyze content
	analysis := map[string]interface{}{
		"filename":    filename,
		"word_count":  len(strings.Fields(content)),
		"line_count":  len(strings.Split(content, "\n")),
		"char_count":  len(content),
		"tags":        ba.extractTags(content),
		"links":       ba.extractLinks(content),
		"headers":     ba.extractHeaders(content),
		"readability": ba.calculateReadability(content),
	}

	return analysis
}

func (ba *BulkAnalyzer) extractTags(content string) []string {
	var tags []string
	tagRegex := regexp.MustCompile(`#(\w+)`)
	matches := tagRegex.FindAllStringSubmatch(content, -1)
	for _, match := range matches {
		tags = append(tags, match[1])
	}
	return tags
}

func (ba *BulkAnalyzer) extractLinks(content string) []string {
	var links []string
	linkRegex := regexp.MustCompile(`\[\[([^\]]+)\]\]`)
	matches := linkRegex.FindAllStringSubmatch(content, -1)
	for _, match := range matches {
		links = append(links, match[1])
	}
	return links
}

func (ba *BulkAnalyzer) extractHeaders(content string) []string {
	var headers []string
	headerRegex := regexp.MustCompile(`^#+\s+(.+)$`)
	lines := strings.Split(content, "\n")
	for _, line := range lines {
		if matches := headerRegex.FindStringSubmatch(line); len(matches) > 1 {
			headers = append(headers, strings.TrimSpace(matches[1]))
		}
	}
	return headers
}

func (ba *BulkAnalyzer) calculateReadability(content string) float64 {
	// Simple readability score based on average word length and sentence length
	words := strings.Fields(content)
	if len(words) == 0 {
		return 0.0
	}

	// Calculate average word length
	totalChars := 0
	for _, word := range words {
		totalChars += len(word)
	}
	avgWordLength := float64(totalChars) / float64(len(words))

	// Calculate average sentence length
	sentences := strings.Split(content, ".")
	avgSentenceLength := float64(len(words)) / float64(len(sentences))

	// Simple readability formula (higher is more readable)
	readability := 100.0 - (avgWordLength * 1.5) - (avgSentenceLength * 0.5)
	if readability < 0 {
		readability = 0
	}
	if readability > 100 {
		readability = 100
	}

	return readability
}

func (ba *BulkAnalyzer) generateSummary(analysis map[string]interface{}) map[string]interface{} {
	totalFiles := len(analysis)
	totalWords := 0
	totalLines := 0
	totalChars := 0
	allTags := make(map[string]int)
	allLinks := make(map[string]int)

	for _, fileAnalysis := range analysis {
		if fa, ok := fileAnalysis.(map[string]interface{}); ok {
			if wordCount, ok := fa["word_count"].(int); ok {
				totalWords += wordCount
			}
			if lineCount, ok := fa["line_count"].(int); ok {
				totalLines += lineCount
			}
			if charCount, ok := fa["char_count"].(int); ok {
				totalChars += charCount
			}
			if tags, ok := fa["tags"].([]string); ok {
				for _, tag := range tags {
					allTags[tag]++
				}
			}
			if links, ok := fa["links"].([]string); ok {
				for _, link := range links {
					allLinks[link]++
				}
			}
		}
	}

	// Find most common tags and links
	commonTags := ba.findMostCommon(allTags, 5)
	commonLinks := ba.findMostCommon(allLinks, 5)

	return map[string]interface{}{
		"total_files":        totalFiles,
		"total_words":        totalWords,
		"total_lines":        totalLines,
		"total_chars":        totalChars,
		"avg_words_per_file": float64(totalWords) / float64(totalFiles),
		"avg_lines_per_file": float64(totalLines) / float64(totalFiles),
		"common_tags":        commonTags,
		"common_links":       commonLinks,
	}
}

func (ba *BulkAnalyzer) findMostCommon(items map[string]int, limit int) []map[string]interface{} {
	var pairs []struct {
		Key   string
		Value int
	}
	for k, v := range items {
		pairs = append(pairs, struct {
			Key   string
			Value int
		}{k, v})
	}

	// Sort by value (descending)
	sort.Slice(pairs, func(i, j int) bool {
		return pairs[i].Value > pairs[j].Value
	})

	// Take top N
	var result []map[string]interface{}
	for i, pair := range pairs {
		if i >= limit {
			break
		}
		result = append(result, map[string]interface{}{
			"item":  pair.Key,
			"count": pair.Value,
		})
	}

	return result
}

func (ba *BulkAnalyzer) getContentString(data interface{}) string {
	if content, ok := data.(string); ok {
		return content
	}
	return ""
}

// Validator methods
func (bv *BulkValidator) ValidateBulkOperation(operation *BulkOperation) error {
	// Basic validation
	if operation.ID == "" {
		return fmt.Errorf("operation ID is required")
	}
	if operation.Type == "" {
		return fmt.Errorf("operation type is required")
	}
	if len(operation.Files) == 0 {
		return fmt.Errorf("at least one file is required")
	}

	// Type-specific validation
	switch operation.Type {
	case "tag":
		if _, ok := operation.Parameters["tag"]; !ok {
			return fmt.Errorf("tag parameter is required for tag operations")
		}
	case "link":
		if _, ok := operation.Parameters["link_pattern"]; !ok {
			return fmt.Errorf("link_pattern parameter is required for link operations")
		}
	case "organize":
		if _, ok := operation.Parameters["action"]; !ok {
			return fmt.Errorf("action parameter is required for organize operations")
		}
	}

	return nil
}

// Progress Tracker methods
func (pt *ProgressTracker) UpdateProgress(operationID string, total, completed, failed int, errors []string) {
	pt.mutex.Lock()
	defer pt.mutex.Unlock()

	if progress, exists := pt.operations[operationID]; exists {
		progress.Total = total
		progress.Completed = completed
		progress.Failed = failed
		progress.Errors = errors

		if completed+failed >= total {
			progress.Status = "completed"
			progress.EndTime = time.Now()
		}
	} else {
		pt.operations[operationID] = &OperationProgress{
			OperationID: operationID,
			Total:       total,
			Completed:   completed,
			Failed:      failed,
			StartTime:   time.Now(),
			Status:      "running",
			Errors:      errors,
		}
	}
}

func (pt *ProgressTracker) GetProgress(operationID string) *OperationProgress {
	pt.mutex.RLock()
	defer pt.mutex.RUnlock()

	return pt.operations[operationID]
}

func (pt *ProgressTracker) CancelOperation(operationID string) bool {
	pt.mutex.Lock()
	defer pt.mutex.Unlock()

	if progress, exists := pt.operations[operationID]; exists {
		progress.Status = "cancelled"
		progress.EndTime = time.Now()
		return true
	}
	return false
}

// Demo function
func demoBulkOperationsSystem() {
	fmt.Println("⚡ BULK OPERATIONS SYSTEM DEMO")
	fmt.Println("=============================")

	// Create API pipeline
	apiPipeline := NewAPIPipeline("obsidian-vault", "https://127.0.0.1:27124",
		"b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")

	// Create bulk operations system
	bos := NewBulkOperationsSystem(apiPipeline)

	// Test bulk operations
	operations := []*BulkOperation{
		{
			ID:    "tag-op-1",
			Type:  "tag",
			Files: []string{"test-note-1.md", "test-note-2.md"},
			Parameters: map[string]interface{}{
				"action": "add",
				"tag":    "test",
			},
		},
		{
			ID:    "link-op-1",
			Type:  "link",
			Files: []string{"test-note-1.md"},
			Parameters: map[string]interface{}{
				"action":       "add",
				"link_pattern": "test-note-2",
			},
		},
		{
			ID:    "organize-op-1",
			Type:  "organize",
			Files: []string{"test-note-1.md", "test-note-2.md"},
			Parameters: map[string]interface{}{
				"action":   "categorize",
				"category": "demo",
			},
		},
		{
			ID:         "analyze-op-1",
			Type:       "analyze",
			Files:      []string{"test-note-1.md", "test-note-2.md"},
			Parameters: map[string]interface{}{},
		},
	}

	for i, operation := range operations {
		fmt.Printf("\n🔧 Test %d: %s operation\n", i+1, operation.Type)

		var result *BulkOperationResult
		switch operation.Type {
		case "tag":
			result = bos.BulkTagOperations(operation)
		case "link":
			result = bos.BulkLinkOperations(operation)
		case "organize":
			result = bos.BulkOrganizeOperations(operation)
		case "analyze":
			result = bos.BulkAnalyzeOperations(operation)
		}

		if result.Success {
			fmt.Printf("✅ %s\n", result.Message)
			if result.Data != nil {
				fmt.Printf("   Data: %+v\n", result.Data)
			}
		} else {
			fmt.Printf("❌ %s\n", result.Message)
		}

		fmt.Printf("   Duration: %dms\n", result.Duration.Milliseconds())
	}

	fmt.Println("\n🎉 Bulk Operations System demo completed!")
}

func main() {
	demoBulkOperationsSystem()
}
