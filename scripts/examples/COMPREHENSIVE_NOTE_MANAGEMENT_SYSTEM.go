package main

import (
	"fmt"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"
)

// ComprehensiveNoteManagementSystem provides complete note management capabilities
type ComprehensiveNoteManagementSystem struct {
	apiPipeline   *APIPipeline
	noteTemplates *NoteTemplateManager
	noteValidator *NoteValidator
	noteIndexer   *NoteIndexer
	noteBackup    *NoteBackupManager
	noteAnalytics *NoteAnalytics
	noteWorkflows *NoteWorkflowManager
	mutex         sync.RWMutex
}

// NoteTemplateManager manages note templates
type NoteTemplateManager struct {
	templates map[string]*NoteTemplate
	mutex     sync.RWMutex
}

// NoteTemplate represents a note template
type NoteTemplate struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Content     string                 `json:"content"`
	Variables   []string               `json:"variables"`
	Metadata    map[string]interface{} `json:"metadata"`
	CreatedAt   time.Time              `json:"created_at"`
	UpdatedAt   time.Time              `json:"updated_at"`
}

// NoteValidator validates note content and structure
type NoteValidator struct {
	rules map[string]ValidationRule
}

// ValidationRule represents a validation rule
type ValidationRule struct {
	Name        string
	Description string
	Function    func(string) (bool, string)
	Severity    string // "error", "warning", "info"
}

// NoteIndexer indexes notes for fast searching
type NoteIndexer struct {
	index    map[string]*IndexedNote
	metadata map[string]*NoteMetadata
	mutex    sync.RWMutex
}

// IndexedNote represents an indexed note
type IndexedNote struct {
	File      string
	Title     string
	Content   string
	Tags      []string
	Links     []string
	Headers   []string
	Metadata  map[string]interface{}
	IndexedAt time.Time
}

// NoteMetadata represents note metadata
type NoteMetadata struct {
	File       string                 `json:"file"`
	Title      string                 `json:"title"`
	Tags       []string               `json:"tags"`
	Links      []string               `json:"links"`
	Headers    []string               `json:"headers"`
	WordCount  int                    `json:"word_count"`
	LineCount  int                    `json:"line_count"`
	CharCount  int                    `json:"char_count"`
	CreatedAt  time.Time              `json:"created_at"`
	UpdatedAt  time.Time              `json:"updated_at"`
	LastRead   time.Time              `json:"last_read"`
	ReadCount  int                    `json:"read_count"`
	CustomData map[string]interface{} `json:"custom_data"`
}

// NoteBackupManager manages note backups
type NoteBackupManager struct {
	backupDir string
	versions  map[string][]BackupVersion
	mutex     sync.RWMutex
}

// BackupVersion represents a backup version
type BackupVersion struct {
	File      string
	Content   string
	Timestamp time.Time
	Size      int64
	Checksum  string
}

// NoteAnalytics provides analytics for notes
type NoteAnalytics struct {
	metrics map[string]interface{}
	mutex   sync.RWMutex
}

// NoteWorkflowManager manages note workflows
type NoteWorkflowManager struct {
	workflows map[string]*NoteWorkflow
	mutex     sync.RWMutex
}

// NoteWorkflow represents a note workflow
type NoteWorkflow struct {
	Name        string
	Description string
	Steps       []WorkflowStep
	Triggers    []WorkflowTrigger
	Enabled     bool
}

// WorkflowStep represents a workflow step
type WorkflowStep struct {
	Type       string
	Action     string
	Parameters map[string]interface{}
	Condition  string
}

// WorkflowTrigger represents a workflow trigger
type WorkflowTrigger struct {
	Type      string
	Condition string
	Action    string
}

// NoteOperation represents a note operation
type NoteOperation struct {
	Type      string                 `json:"type"` // "create", "read", "update", "delete", "copy", "move", "rename"
	File      string                 `json:"file"`
	Content   string                 `json:"content,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Options   map[string]interface{} `json:"options,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
}

// NoteOperationResult represents the result of a note operation
type NoteOperationResult struct {
	Success   bool                   `json:"success"`
	Message   string                 `json:"message"`
	Data      interface{}            `json:"data,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
	Timestamp time.Time              `json:"timestamp"`
	Duration  time.Duration          `json:"duration"`
}

// NewComprehensiveNoteManagementSystem creates a new note management system
func NewComprehensiveNoteManagementSystem(apiPipeline *APIPipeline) *ComprehensiveNoteManagementSystem {
	return &ComprehensiveNoteManagementSystem{
		apiPipeline: apiPipeline,
		noteTemplates: &NoteTemplateManager{
			templates: make(map[string]*NoteTemplate),
		},
		noteValidator: &NoteValidator{
			rules: make(map[string]ValidationRule),
		},
		noteIndexer: &NoteIndexer{
			index:    make(map[string]*IndexedNote),
			metadata: make(map[string]*NoteMetadata),
		},
		noteBackup: &NoteBackupManager{
			backupDir: "./backups",
			versions:  make(map[string][]BackupVersion),
		},
		noteAnalytics: &NoteAnalytics{
			metrics: make(map[string]interface{}),
		},
		noteWorkflows: &NoteWorkflowManager{
			workflows: make(map[string]*NoteWorkflow),
		},
	}
}

// CreateNote creates a new note
func (nms *ComprehensiveNoteManagementSystem) CreateNote(operation *NoteOperation) *NoteOperationResult {
	start := time.Now()
	result := &NoteOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Validate operation
	if operation.File == "" {
		result.Message = "Filename is required"
		return result
	}

	// Check if note already exists
	existingResult := nms.apiPipeline.ReadVaultFile(operation.File)
	if existingResult.Success {
		result.Message = "Note already exists"
		return result
	}

	// Prepare content
	content := operation.Content
	if content == "" {
		content = nms.generateDefaultContent(operation.File)
	}

	// Apply template if specified
	if templateName, ok := operation.Options["template"].(string); ok {
		templateContent, err := nms.noteTemplates.GetTemplate(templateName)
		if err == nil {
			content = nms.applyTemplate(templateContent, operation.Metadata)
		}
	}

	// Validate content
	if validationResult := nms.noteValidator.ValidateContent(content); !validationResult.Valid {
		result.Message = fmt.Sprintf("Content validation failed: %s", validationResult.Message)
		return result
	}

	// Create the note
	apiResult := nms.apiPipeline.CreateVaultFile(operation.File, content)
	if !apiResult.Success {
		result.Message = fmt.Sprintf("Failed to create note: %v", apiResult.Error)
		return result
	}

	// Index the note
	nms.noteIndexer.IndexNote(operation.File, content)

	// Create backup
	nms.noteBackup.CreateBackup(operation.File, content)

	// Record analytics
	nms.noteAnalytics.RecordOperation("create", operation.File)

	// Execute workflows
	nms.noteWorkflows.ExecuteWorkflows("create", operation.File, content)

	result.Success = true
	result.Message = fmt.Sprintf("Successfully created note: %s", operation.File)
	result.Data = map[string]interface{}{
		"file":    operation.File,
		"content": content,
		"size":    len(content),
	}
	result.Duration = time.Since(start)

	return result
}

// ReadNote reads a note
func (nms *ComprehensiveNoteManagementSystem) ReadNote(operation *NoteOperation) *NoteOperationResult {
	start := time.Now()
	result := &NoteOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	if operation.File == "" {
		result.Message = "Filename is required"
		return result
	}

	// Read from API
	apiResult := nms.apiPipeline.ReadVaultFile(operation.File)
	if !apiResult.Success {
		result.Message = fmt.Sprintf("Failed to read note: %v", apiResult.Error)
		return result
	}

	content := nms.getContentString(apiResult.Data)

	// Update metadata
	nms.noteIndexer.UpdateReadMetadata(operation.File)

	// Record analytics
	nms.noteAnalytics.RecordOperation("read", operation.File)

	result.Success = true
	result.Message = fmt.Sprintf("Successfully read note: %s", operation.File)
	result.Data = map[string]interface{}{
		"file":    operation.File,
		"content": content,
		"size":    len(content),
	}
	result.Duration = time.Since(start)

	return result
}

// UpdateNote updates a note
func (nms *ComprehensiveNoteManagementSystem) UpdateNote(operation *NoteOperation) *NoteOperationResult {
	start := time.Now()
	result := &NoteOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	if operation.File == "" {
		result.Message = "Filename is required"
		return result
	}

	if operation.Content == "" {
		result.Message = "Content is required for update"
		return result
	}

	// Create backup before update
	existingResult := nms.apiPipeline.ReadVaultFile(operation.File)
	if existingResult.Success {
		existingContent := nms.getContentString(existingResult.Data)
		nms.noteBackup.CreateBackup(operation.File, existingContent)
	}

	// Validate content
	if validationResult := nms.noteValidator.ValidateContent(operation.Content); !validationResult.Valid {
		result.Message = fmt.Sprintf("Content validation failed: %s", validationResult.Message)
		return result
	}

	// Update the note
	apiResult := nms.apiPipeline.UpdateVaultFile(operation.File, operation.Content)
	if !apiResult.Success {
		result.Message = fmt.Sprintf("Failed to update note: %v", apiResult.Error)
		return result
	}

	// Update index
	nms.noteIndexer.IndexNote(operation.File, operation.Content)

	// Record analytics
	nms.noteAnalytics.RecordOperation("update", operation.File)

	// Execute workflows
	nms.noteWorkflows.ExecuteWorkflows("update", operation.File, operation.Content)

	result.Success = true
	result.Message = fmt.Sprintf("Successfully updated note: %s", operation.File)
	result.Data = map[string]interface{}{
		"file":    operation.File,
		"content": operation.Content,
		"size":    len(operation.Content),
	}
	result.Duration = time.Since(start)

	return result
}

// DeleteNote deletes a note
func (nms *ComprehensiveNoteManagementSystem) DeleteNote(operation *NoteOperation) *NoteOperationResult {
	start := time.Now()
	result := &NoteOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	if operation.File == "" {
		result.Message = "Filename is required"
		return result
	}

	// Create backup before deletion
	existingResult := nms.apiPipeline.ReadVaultFile(operation.File)
	if existingResult.Success {
		existingContent := nms.getContentString(existingResult.Data)
		nms.noteBackup.CreateBackup(operation.File, existingContent)
	}

	// Delete the note
	apiResult := nms.apiPipeline.DeleteVaultFile(operation.File)
	if !apiResult.Success {
		result.Message = fmt.Sprintf("Failed to delete note: %v", apiResult.Error)
		return result
	}

	// Remove from index
	nms.noteIndexer.RemoveFromIndex(operation.File)

	// Record analytics
	nms.noteAnalytics.RecordOperation("delete", operation.File)

	// Execute workflows
	nms.noteWorkflows.ExecuteWorkflows("delete", operation.File, "")

	result.Success = true
	result.Message = fmt.Sprintf("Successfully deleted note: %s", operation.File)
	result.Duration = time.Since(start)

	return result
}

// CopyNote copies a note
func (nms *ComprehensiveNoteManagementSystem) CopyNote(operation *NoteOperation) *NoteOperationResult {
	start := time.Now()
	result := &NoteOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	if operation.File == "" {
		result.Message = "Source filename is required"
		return result
	}

	destFile, ok := operation.Options["destination"].(string)
	if !ok || destFile == "" {
		result.Message = "Destination filename is required"
		return result
	}

	// Read source note
	readResult := nms.ReadNote(&NoteOperation{
		Type: "read",
		File: operation.File,
	})
	if !readResult.Success {
		result.Message = fmt.Sprintf("Failed to read source note: %s", readResult.Message)
		return result
	}

	// Create copy
	copyOperation := &NoteOperation{
		Type:    "create",
		File:    destFile,
		Content: readResult.Data.(map[string]interface{})["content"].(string),
	}

	copyResult := nms.CreateNote(copyOperation)
	if !copyResult.Success {
		result.Message = fmt.Sprintf("Failed to create copy: %s", copyResult.Message)
		return result
	}

	result.Success = true
	result.Message = fmt.Sprintf("Successfully copied note from %s to %s", operation.File, destFile)
	result.Data = map[string]interface{}{
		"source":      operation.File,
		"destination": destFile,
	}
	result.Duration = time.Since(start)

	return result
}

// MoveNote moves a note
func (nms *ComprehensiveNoteManagementSystem) MoveNote(operation *NoteOperation) *NoteOperationResult {
	start := time.Now()
	result := &NoteOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	if operation.File == "" {
		result.Message = "Source filename is required"
		return result
	}

	destFile, ok := operation.Options["destination"].(string)
	if !ok || destFile == "" {
		result.Message = "Destination filename is required"
		return result
	}

	// Copy the note
	copyResult := nms.CopyNote(operation)
	if !copyResult.Success {
		result.Message = fmt.Sprintf("Failed to copy note: %s", copyResult.Message)
		return result
	}

	// Delete the original
	deleteResult := nms.DeleteNote(&NoteOperation{
		Type: "delete",
		File: operation.File,
	})
	if !deleteResult.Success {
		// If deletion fails, try to clean up the copy
		nms.DeleteNote(&NoteOperation{
			Type: "delete",
			File: destFile,
		})
		result.Message = fmt.Sprintf("Failed to delete original note: %s", deleteResult.Message)
		return result
	}

	result.Success = true
	result.Message = fmt.Sprintf("Successfully moved note from %s to %s", operation.File, destFile)
	result.Data = map[string]interface{}{
		"source":      operation.File,
		"destination": destFile,
	}
	result.Duration = time.Since(start)

	return result
}

// RenameNote renames a note
func (nms *ComprehensiveNoteManagementSystem) RenameNote(operation *NoteOperation) *NoteOperationResult {
	start := time.Now()
	result := &NoteOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	if operation.File == "" {
		result.Message = "Current filename is required"
		return result
	}

	newName, ok := operation.Options["new_name"].(string)
	if !ok || newName == "" {
		result.Message = "New filename is required"
		return result
	}

	// Move the note
	moveOperation := &NoteOperation{
		Type: "move",
		File: operation.File,
		Options: map[string]interface{}{
			"destination": newName,
		},
	}

	moveResult := nms.MoveNote(moveOperation)
	if !moveResult.Success {
		result.Message = fmt.Sprintf("Failed to rename note: %s", moveResult.Message)
		return result
	}

	result.Success = true
	result.Message = fmt.Sprintf("Successfully renamed note from %s to %s", operation.File, newName)
	result.Data = map[string]interface{}{
		"old_name": operation.File,
		"new_name": newName,
	}
	result.Duration = time.Since(start)

	return result
}

// ListNotes lists all notes with metadata
func (nms *ComprehensiveNoteManagementSystem) ListNotes(filters map[string]interface{}) *NoteOperationResult {
	start := time.Now()
	result := &NoteOperationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Get all files
	apiResult := nms.apiPipeline.ListVaultFiles("")
	if !apiResult.Success {
		result.Message = fmt.Sprintf("Failed to list files: %v", apiResult.Error)
		return result
	}

	files := nms.getFileList(apiResult.Data)
	var notes []map[string]interface{}

	for _, file := range files {
		if strings.HasSuffix(strings.ToLower(file), ".md") {
			metadata := nms.noteIndexer.GetMetadata(file)
			if metadata != nil {
				notes = append(notes, map[string]interface{}{
					"file":       metadata.File,
					"title":      metadata.Title,
					"tags":       metadata.Tags,
					"links":      metadata.Links,
					"headers":    metadata.Headers,
					"word_count": metadata.WordCount,
					"line_count": metadata.LineCount,
					"char_count": metadata.CharCount,
					"created_at": metadata.CreatedAt,
					"updated_at": metadata.UpdatedAt,
					"last_read":  metadata.LastRead,
					"read_count": metadata.ReadCount,
				})
			}
		}
	}

	// Apply filters
	if len(filters) > 0 {
		notes = nms.applyNoteFilters(notes, filters)
	}

	result.Success = true
	result.Message = fmt.Sprintf("Found %d notes", len(notes))
	result.Data = notes
	result.Duration = time.Since(start)

	return result
}

// Helper methods
func (nms *ComprehensiveNoteManagementSystem) generateDefaultContent(filename string) string {
	title := strings.TrimSuffix(filepath.Base(filename), ".md")
	return fmt.Sprintf("# %s\n\nCreated on %s\n\n## Content\n\n", title, time.Now().Format("2006-01-02 15:04:05"))
}

func (nms *ComprehensiveNoteManagementSystem) applyTemplate(template *NoteTemplate, metadata map[string]interface{}) string {
	content := template.Content

	// Replace variables
	for _, variable := range template.Variables {
		if value, ok := metadata[variable]; ok {
			content = strings.ReplaceAll(content, "{{"+variable+"}}", fmt.Sprintf("%v", value))
		}
	}

	return content
}

func (nms *ComprehensiveNoteManagementSystem) getContentString(data interface{}) string {
	if content, ok := data.(string); ok {
		return content
	}
	return ""
}

func (nms *ComprehensiveNoteManagementSystem) getFileList(data interface{}) []string {
	if files, ok := data.([]string); ok {
		return files
	}
	if result, ok := data.(map[string]interface{}); ok {
		if files, ok := result["files"].([]interface{}); ok {
			var fileList []string
			for _, file := range files {
				if fileStr, ok := file.(string); ok {
					fileList = append(fileList, fileStr)
				}
			}
			return fileList
		}
	}
	return []string{}
}

func (nms *ComprehensiveNoteManagementSystem) applyNoteFilters(notes []map[string]interface{}, filters map[string]interface{}) []map[string]interface{} {
	var filtered []map[string]interface{}

	for _, note := range notes {
		include := true

		for key, value := range filters {
			switch key {
			case "tag":
				if tag, ok := value.(string); ok {
					noteTags, _ := note["tags"].([]string)
					found := false
					for _, noteTag := range noteTags {
						if strings.Contains(strings.ToLower(noteTag), strings.ToLower(tag)) {
							found = true
							break
						}
					}
					if !found {
						include = false
					}
				}
			case "min_word_count":
				if minCount, ok := value.(int); ok {
					if wordCount, ok := note["word_count"].(int); ok {
						if wordCount < minCount {
							include = false
						}
					}
				}
			case "created_after":
				if after, ok := value.(time.Time); ok {
					if created, ok := note["created_at"].(time.Time); ok {
						if created.Before(after) {
							include = false
						}
					}
				}
			}

			if !include {
				break
			}
		}

		if include {
			filtered = append(filtered, note)
		}
	}

	return filtered
}

// Template Manager methods
func (ntm *NoteTemplateManager) GetTemplate(name string) (*NoteTemplate, error) {
	ntm.mutex.RLock()
	defer ntm.mutex.RUnlock()

	template, exists := ntm.templates[name]
	if !exists {
		return nil, fmt.Errorf("template not found: %s", name)
	}

	return template, nil
}

func (ntm *NoteTemplateManager) AddTemplate(template *NoteTemplate) {
	ntm.mutex.Lock()
	defer ntm.mutex.Unlock()

	ntm.templates[template.Name] = template
}

// Validator methods
func (nv *NoteValidator) ValidateContent(content string) ValidationResult {
	// Basic validation rules
	if len(content) == 0 {
		return ValidationResult{Valid: false, Message: "Content cannot be empty"}
	}

	if len(content) > 1000000 { // 1MB limit
		return ValidationResult{Valid: false, Message: "Content too large (max 1MB)"}
	}

	// Check for valid markdown structure
	if !strings.Contains(content, "#") {
		return ValidationResult{Valid: false, Message: "Content should have at least one header"}
	}

	return ValidationResult{Valid: true, Message: "Content is valid"}
}

type ValidationResult struct {
	Valid   bool
	Message string
}

// Indexer methods
func (ni *NoteIndexer) IndexNote(filename, content string) {
	ni.mutex.Lock()
	defer ni.mutex.Unlock()

	// Extract metadata
	title := ni.extractTitle(content)
	tags := ni.extractTags(content)
	links := ni.extractLinks(content)
	headers := ni.extractHeaders(content)

	// Create indexed note
	indexedNote := &IndexedNote{
		File:      filename,
		Title:     title,
		Content:   content,
		Tags:      tags,
		Links:     links,
		Headers:   headers,
		Metadata:  make(map[string]interface{}),
		IndexedAt: time.Now(),
	}

	ni.index[filename] = indexedNote

	// Create metadata
	metadata := &NoteMetadata{
		File:       filename,
		Title:      title,
		Tags:       tags,
		Links:      links,
		Headers:    headers,
		WordCount:  len(strings.Fields(content)),
		LineCount:  len(strings.Split(content, "\n")),
		CharCount:  len(content),
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
		LastRead:   time.Now(),
		ReadCount:  0,
		CustomData: make(map[string]interface{}),
	}

	ni.metadata[filename] = metadata
}

func (ni *NoteIndexer) GetMetadata(filename string) *NoteMetadata {
	ni.mutex.RLock()
	defer ni.mutex.RUnlock()

	return ni.metadata[filename]
}

func (ni *NoteIndexer) UpdateReadMetadata(filename string) {
	ni.mutex.Lock()
	defer ni.mutex.Unlock()

	if metadata, exists := ni.metadata[filename]; exists {
		metadata.LastRead = time.Now()
		metadata.ReadCount++
	}
}

func (ni *NoteIndexer) RemoveFromIndex(filename string) {
	ni.mutex.Lock()
	defer ni.mutex.Unlock()

	delete(ni.index, filename)
	delete(ni.metadata, filename)
}

func (ni *NoteIndexer) extractTitle(content string) string {
	lines := strings.Split(content, "\n")
	for _, line := range lines {
		if strings.HasPrefix(line, "# ") {
			return strings.TrimSpace(line[2:])
		}
	}
	return ""
}

func (ni *NoteIndexer) extractTags(content string) []string {
	var tags []string
	tagRegex := regexp.MustCompile(`#(\w+)`)
	matches := tagRegex.FindAllStringSubmatch(content, -1)
	for _, match := range matches {
		tags = append(tags, match[1])
	}
	return tags
}

func (ni *NoteIndexer) extractLinks(content string) []string {
	var links []string
	linkRegex := regexp.MustCompile(`\[\[([^\]]+)\]\]`)
	matches := linkRegex.FindAllStringSubmatch(content, -1)
	for _, match := range matches {
		links = append(links, match[1])
	}
	return links
}

func (ni *NoteIndexer) extractHeaders(content string) []string {
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

// Backup Manager methods
func (nbm *NoteBackupManager) CreateBackup(filename, content string) {
	nbm.mutex.Lock()
	defer nbm.mutex.Unlock()

	backup := BackupVersion{
		File:      filename,
		Content:   content,
		Timestamp: time.Now(),
		Size:      int64(len(content)),
		Checksum:  fmt.Sprintf("%x", content), // Simple checksum
	}

	nbm.versions[filename] = append(nbm.versions[filename], backup)

	// Keep only last 10 versions
	if len(nbm.versions[filename]) > 10 {
		nbm.versions[filename] = nbm.versions[filename][len(nbm.versions[filename])-10:]
	}
}

// Analytics methods
func (na *NoteAnalytics) RecordOperation(operation, filename string) {
	na.mutex.Lock()
	defer na.mutex.Unlock()

	key := fmt.Sprintf("%s_%s", operation, filename)
	na.metrics[key] = time.Now()
}

// Workflow Manager methods
func (nwm *NoteWorkflowManager) ExecuteWorkflows(trigger, filename, content string) {
	nwm.mutex.RLock()
	defer nwm.mutex.RUnlock()

	for _, workflow := range nwm.workflows {
		if !workflow.Enabled {
			continue
		}

		for _, workflowTrigger := range workflow.Triggers {
			if workflowTrigger.Type == trigger {
				// Execute workflow steps
				for _, step := range workflow.Steps {
					nwm.executeStep(step, filename, content)
				}
			}
		}
	}
}

func (nwm *NoteWorkflowManager) executeStep(step WorkflowStep, filename, content string) {
	// Execute workflow step
	// This would implement the actual workflow execution logic
	fmt.Printf("Executing workflow step: %s for file: %s\n", step.Action, filename)
}

// Demo function
func demoComprehensiveNoteManagementSystem() {
	fmt.Println("📝 COMPREHENSIVE NOTE MANAGEMENT SYSTEM DEMO")
	fmt.Println("=============================================")

	// Create API pipeline
	apiPipeline := NewAPIPipeline("obsidian-vault", "https://127.0.0.1:27124",
		"b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")

	// Create note management system
	nms := NewComprehensiveNoteManagementSystem(apiPipeline)

	// Test note operations
	operations := []*NoteOperation{
		{
			Type:    "create",
			File:    "test-note.md",
			Content: "# Test Note\n\nThis is a test note created by the comprehensive note management system.",
		},
		{
			Type: "read",
			File: "test-note.md",
		},
		{
			Type:    "update",
			File:    "test-note.md",
			Content: "# Test Note\n\nThis is an updated test note with more content.\n\n## Additional Section\n\nMore content here.",
		},
		{
			Type: "list",
		},
		{
			Type: "delete",
			File: "test-note.md",
		},
	}

	for i, operation := range operations {
		fmt.Printf("\n🔧 Test %d: %s operation\n", i+1, operation.Type)

		var result *NoteOperationResult
		switch operation.Type {
		case "create":
			result = nms.CreateNote(operation)
		case "read":
			result = nms.ReadNote(operation)
		case "update":
			result = nms.UpdateNote(operation)
		case "list":
			result = nms.ListNotes(map[string]interface{}{})
		case "delete":
			result = nms.DeleteNote(operation)
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

	fmt.Println("\n🎉 Comprehensive Note Management System demo completed!")
}

func main() {
	demoComprehensiveNoteManagementSystem()
}
