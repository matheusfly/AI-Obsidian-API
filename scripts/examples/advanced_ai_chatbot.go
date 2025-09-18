package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"regexp"
	"strings"
	"sync"
	"time"
)

// AdvancedAIChatbot provides natural language interaction with the vault
type AdvancedAIChatbot struct {
	baseURL       string
	token         string
	ollamaHost    string
	ollamaModel   string
	client        *http.Client
	ollamaClient  *http.Client
	searchEngine  *SemanticSearchEngine
	taggingEngine *BulkTaggingEngine
	linkAnalyzer  *LinkAnalysisEngine
	aiAgent       *AIVaultAgent
	cache         *IntelligentCachingSystem
	sync          *RealTimeSyncSystem
	conversation  *ConversationManager
	context       *ContextManager
	personality   *PersonalityEngine
}

// ConversationManager manages conversation state and history
type ConversationManager struct {
	sessions       map[string]*ConversationSession
	currentSession *ConversationSession
	mutex          sync.RWMutex
}

// ConversationSession represents a conversation session
type ConversationSession struct {
	ID           string                 `json:"id"`
	UserID       string                 `json:"user_id"`
	StartTime    time.Time              `json:"start_time"`
	LastActivity time.Time              `json:"last_activity"`
	Messages     []*ChatMessage         `json:"messages"`
	Context      map[string]interface{} `json:"context"`
	Preferences  *UserPreferences       `json:"preferences"`
	State        string                 `json:"state"` // "active", "paused", "ended"
}

// ChatMessage represents a chat message
type ChatMessage struct {
	ID         string                 `json:"id"`
	SessionID  string                 `json:"session_id"`
	Type       string                 `json:"type"` // "user", "assistant", "system"
	Content    string                 `json:"content"`
	Timestamp  time.Time              `json:"timestamp"`
	Metadata   map[string]interface{} `json:"metadata"`
	Intent     string                 `json:"intent"`
	Entities   []Entity               `json:"entities"`
	Confidence float64                `json:"confidence"`
}

// Entity represents an extracted entity
type Entity struct {
	Type       string  `json:"type"`
	Value      string  `json:"value"`
	Start      int     `json:"start"`
	End        int     `json:"end"`
	Confidence float64 `json:"confidence"`
}

// ContextManager manages conversation context
type ContextManager struct {
	currentTopic     string
	relevantFiles    []string
	userIntent       string
	conversationFlow string
	contextHistory   []*ContextEntry
}

// ContextEntry represents a context entry
type ContextEntry struct {
	Type      string    `json:"type"`
	Content   string    `json:"content"`
	Timestamp time.Time `json:"timestamp"`
	Relevance float64   `json:"relevance"`
}

// PersonalityEngine provides personality and tone management
type PersonalityEngine struct {
	personality string
	tone        string
	style       string
	knowledge   map[string]interface{}
}

// UserPreferences represents user preferences
type UserPreferences struct {
	Language      string   `json:"language"`
	Topics        []string `json:"topics"`
	Verbosity     string   `json:"verbosity"` // "concise", "detailed", "verbose"
	Formality     string   `json:"formality"` // "casual", "professional", "formal"
	AILevel       string   `json:"ai_level"`  // "beginner", "intermediate", "advanced"
	Notifications bool     `json:"notifications"`
}

// NewAdvancedAIChatbot creates a new advanced AI chatbot
func NewAdvancedAIChatbot(baseURL, token, ollamaHost, ollamaModel string) *AdvancedAIChatbot {
	return &AdvancedAIChatbot{
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
		aiAgent:       NewAIVaultAgent(baseURL, token, ollamaHost, ollamaModel),
		cache:         NewIntelligentCachingSystem("./chatbot_cache"),
		sync:          NewRealTimeSyncSystem(baseURL, token),
		conversation: &ConversationManager{
			sessions: make(map[string]*ConversationSession),
		},
		context: &ContextManager{
			contextHistory: make([]*ContextEntry, 0),
		},
		personality: &PersonalityEngine{
			personality: "helpful",
			tone:        "friendly",
			style:       "conversational",
			knowledge:   make(map[string]interface{}),
		},
	}
}

// StartConversation starts a new conversation session
func (chatbot *AdvancedAIChatbot) StartConversation(userID string) (*ConversationSession, error) {
	sessionID := fmt.Sprintf("session_%d", time.Now().Unix())

	session := &ConversationSession{
		ID:           sessionID,
		UserID:       userID,
		StartTime:    time.Now(),
		LastActivity: time.Now(),
		Messages:     make([]*ChatMessage, 0),
		Context:      make(map[string]interface{}),
		Preferences: &UserPreferences{
			Language:      "en",
			Topics:        []string{},
			Verbosity:     "detailed",
			Formality:     "casual",
			AILevel:       "intermediate",
			Notifications: true,
		},
		State: "active",
	}

	chatbot.conversation.mutex.Lock()
	chatbot.conversation.sessions[sessionID] = session
	chatbot.conversation.currentSession = session
	chatbot.conversation.mutex.Unlock()

	// Add welcome message
	welcomeMsg := &ChatMessage{
		ID:         fmt.Sprintf("msg_%d", time.Now().Unix()),
		SessionID:  sessionID,
		Type:       "assistant",
		Content:    chatbot.generateWelcomeMessage(),
		Timestamp:  time.Now(),
		Metadata:   make(map[string]interface{}),
		Intent:     "greeting",
		Entities:   []Entity{},
		Confidence: 1.0,
	}

	session.Messages = append(session.Messages, welcomeMsg)

	return session, nil
}

// ProcessMessage processes a user message and generates a response
func (chatbot *AdvancedAIChatbot) ProcessMessage(sessionID, userMessage string) (*ChatMessage, error) {
	// Get session
	chatbot.conversation.mutex.RLock()
	session, exists := chatbot.conversation.sessions[sessionID]
	chatbot.conversation.mutex.RUnlock()

	if !exists {
		return nil, fmt.Errorf("session not found: %s", sessionID)
	}

	// Create user message
	userMsg := &ChatMessage{
		ID:         fmt.Sprintf("msg_%d", time.Now().Unix()),
		SessionID:  sessionID,
		Type:       "user",
		Content:    userMessage,
		Timestamp:  time.Now(),
		Metadata:   make(map[string]interface{}),
		Intent:     "",
		Entities:   []Entity{},
		Confidence: 0.0,
	}

	// Analyze user message
	analysis, err := chatbot.analyzeMessage(userMessage)
	if err != nil {
		return nil, fmt.Errorf("failed to analyze message: %v", err)
	}

	userMsg.Intent = analysis.Intent
	userMsg.Entities = analysis.Entities
	userMsg.Confidence = analysis.Confidence

	// Add to session
	session.Messages = append(session.Messages, userMsg)
	session.LastActivity = time.Now()

	// Update context
	chatbot.updateContext(userMessage, analysis)

	// Generate response
	response, err := chatbot.generateResponse(session, userMessage, analysis)
	if err != nil {
		return nil, fmt.Errorf("failed to generate response: %v", err)
	}

	// Add response to session
	session.Messages = append(session.Messages, response)

	return response, nil
}

// analyzeMessage analyzes a user message using AI
func (chatbot *AdvancedAIChatbot) analyzeMessage(message string) (*MessageAnalysis, error) {
	// Use Ollama for message analysis
	prompt := fmt.Sprintf(`
Analyze the following user message and extract:
1. Intent (what the user wants to do)
2. Entities (specific items mentioned)
3. Confidence level (0.0 to 1.0)

Message: "%s"

Respond in JSON format:
{
  "intent": "search|create|organize|analyze|recommend|help|other",
  "entities": [
    {"type": "file|tag|topic|action", "value": "extracted_value", "confidence": 0.9}
  ],
  "confidence": 0.8
}
`, message)

	requestBody := map[string]interface{}{
		"model":  chatbot.ollamaModel,
		"prompt": prompt,
		"stream": false,
	}

	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		return nil, err
	}

	resp, err := chatbot.ollamaClient.Post(
		fmt.Sprintf("%s/api/generate", chatbot.ollamaHost),
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

	// Parse response
	var analysis MessageAnalysis
	if err := json.Unmarshal([]byte(response.Response), &analysis); err != nil {
		// Fallback to simple analysis
		analysis = chatbot.simpleMessageAnalysis(message)
	}

	return &analysis, nil
}

// generateResponse generates a response using AI
func (chatbot *AdvancedAIChatbot) generateResponse(session *ConversationSession, userMessage string, analysis *MessageAnalysis) (*ChatMessage, error) {
	// Build context for AI
	context := chatbot.buildContext(session, analysis)

	// Generate response based on intent
	var responseContent string
	var err error

	switch analysis.Intent {
	case "search":
		responseContent, err = chatbot.handleSearchIntent(userMessage, analysis)
	case "create":
		responseContent, err = chatbot.handleCreateIntent(userMessage, analysis)
	case "organize":
		responseContent, err = chatbot.handleOrganizeIntent(userMessage, analysis)
	case "analyze":
		responseContent, err = chatbot.handleAnalyzeIntent(userMessage, analysis)
	case "recommend":
		responseContent, err = chatbot.handleRecommendIntent(userMessage, analysis)
	case "help":
		responseContent, err = chatbot.handleHelpIntent(userMessage, analysis)
	default:
		responseContent, err = chatbot.handleGeneralIntent(userMessage, analysis, context)
	}

	if err != nil {
		responseContent = fmt.Sprintf("I apologize, but I encountered an error: %v", err)
	}

	// Create response message
	response := &ChatMessage{
		ID:        fmt.Sprintf("msg_%d", time.Now().Unix()),
		SessionID: session.ID,
		Type:      "assistant",
		Content:   responseContent,
		Timestamp: time.Now(),
		Metadata: map[string]interface{}{
			"intent":   analysis.Intent,
			"entities": analysis.Entities,
			"context":  context,
		},
		Intent:     analysis.Intent,
		Entities:   analysis.Entities,
		Confidence: analysis.Confidence,
	}

	return response, nil
}

// Intent handlers
func (chatbot *AdvancedAIChatbot) handleSearchIntent(message string, analysis *MessageAnalysis) (string, error) {
	// Extract search query
	query := chatbot.extractSearchQuery(message, analysis)

	// Perform semantic search
	results, err := chatbot.searchEngine.SemanticSearch(query, 5)
	if err != nil {
		return fmt.Sprintf("I couldn't search your vault right now: %v", err), nil
	}

	if len(results) == 0 {
		return fmt.Sprintf("I couldn't find anything related to '%s' in your vault. Would you like me to help you create a note about this topic?", query), nil
	}

	response := fmt.Sprintf("I found %d results for '%s':\n\n", len(results), query)
	for i, result := range results {
		response += fmt.Sprintf("%d. **%s** (%.2f relevance)\n   %s\n\n", i+1, result.File, result.Score, result.Snippet)
	}

	return response, nil
}

func (chatbot *AdvancedAIChatbot) handleCreateIntent(message string, analysis *MessageAnalysis) (string, error) {
	// Extract creation details
	title := chatbot.extractTitle(message, analysis)
	content := chatbot.extractContent(message, analysis)

	if title == "" {
		return "I'd be happy to help you create a note! What would you like to call it?", nil
	}

	// Use AI agent to create note
	task := AgentTask{
		ID:          "create-note-001",
		Type:        "create",
		Description: "Create a new note",
		Parameters: map[string]interface{}{
			"title":   title,
			"content": content,
		},
		Priority:  7,
		Status:    "pending",
		CreatedAt: time.Now(),
	}

	result, err := chatbot.aiAgent.ExecuteTask(task)
	if err != nil {
		return fmt.Sprintf("I couldn't create the note '%s' right now: %v", title, err), nil
	}

	return fmt.Sprintf("I've created the note '%s' for you! %s", title, result.Message), nil
}

func (chatbot *AdvancedAIChatbot) handleOrganizeIntent(message string, analysis *MessageAnalysis) (string, error) {
	// Use AI agent for organization
	task := AgentTask{
		ID:          "organize-vault-001",
		Type:        "organize",
		Description: "Organize vault based on user request",
		Parameters: map[string]interface{}{
			"request": message,
		},
		Priority:  6,
		Status:    "pending",
		CreatedAt: time.Now(),
	}

	result, err := chatbot.aiAgent.ExecuteTask(task)
	if err != nil {
		return fmt.Sprintf("I couldn't organize your vault right now: %v", err), nil
	}

	response := fmt.Sprintf("I've analyzed your vault and here are my organization recommendations:\n\n")
	for i, rec := range result.Recommendations {
		response += fmt.Sprintf("%d. %s\n", i+1, rec)
	}

	return response, nil
}

func (chatbot *AdvancedAIChatbot) handleAnalyzeIntent(message string, analysis *MessageAnalysis) (string, error) {
	// Use link analyzer for analysis
	result, err := chatbot.linkAnalyzer.AnalyzeLinks()
	if err != nil {
		return fmt.Sprintf("I couldn't analyze your vault right now: %v", err), nil
	}

	response := fmt.Sprintf("Here's my analysis of your vault:\n\n")
	response += fmt.Sprintf("📊 **Graph Statistics:**\n")
	response += fmt.Sprintf("• Total nodes: %d\n", result.Graph.Statistics.TotalNodes)
	response += fmt.Sprintf("• Total links: %d\n", result.Graph.Statistics.TotalLinks)
	response += fmt.Sprintf("• Average degree: %.2f\n", result.Graph.Statistics.AverageDegree)
	response += fmt.Sprintf("• Density: %.4f\n\n", result.Graph.Statistics.Density)

	if len(result.HubNodes) > 0 {
		response += fmt.Sprintf("🏆 **Hub Nodes (High Out-Degree):**\n")
		for i, node := range result.HubNodes {
			if i < 3 {
				response += fmt.Sprintf("• %s (%d out-links)\n", node.Title, node.OutDegree)
			}
		}
		response += "\n"
	}

	if len(result.AuthorityNodes) > 0 {
		response += fmt.Sprintf("🎯 **Authority Nodes (High In-Degree):**\n")
		for i, node := range result.AuthorityNodes {
			if i < 3 {
				response += fmt.Sprintf("• %s (%d in-links)\n", node.Title, node.InDegree)
			}
		}
	}

	return response, nil
}

func (chatbot *AdvancedAIChatbot) handleRecommendIntent(message string, analysis *MessageAnalysis) (string, error) {
	// Use AI agent for recommendations
	task := AgentTask{
		ID:          "recommend-001",
		Type:        "recommend",
		Description: "Generate recommendations based on user request",
		Parameters: map[string]interface{}{
			"query": message,
		},
		Priority:  5,
		Status:    "pending",
		CreatedAt: time.Now(),
	}

	result, err := chatbot.aiAgent.ExecuteTask(task)
	if err != nil {
		return fmt.Sprintf("I couldn't generate recommendations right now: %v", err), nil
	}

	response := fmt.Sprintf("Here are my recommendations for you:\n\n")
	for i, rec := range result.Recommendations {
		response += fmt.Sprintf("%d. %s\n", i+1, rec)
	}

	return response, nil
}

func (chatbot *AdvancedAIChatbot) handleHelpIntent(message string, analysis *MessageAnalysis) (string, error) {
	helpText := `
I'm your AI assistant for managing your Obsidian vault! Here's what I can help you with:

🔍 **Search & Find:**
• "Search for logic notes"
• "Find files about mathematics"
• "Look for API documentation"

📝 **Create & Manage:**
• "Create a note about machine learning"
• "Organize my vault"
• "Add tags to my files"

📊 **Analyze & Insights:**
• "Analyze my vault structure"
• "Show me link statistics"
• "What are my most connected notes?"

💡 **Recommendations:**
• "Give me improvement suggestions"
• "How can I better organize my notes?"
• "What should I focus on next?"

🔄 **Sync & Updates:**
• "Sync my vault"
• "Check for conflicts"
• "Show sync status"

Just ask me anything about your vault in natural language, and I'll help you out!
`
	return helpText, nil
}

func (chatbot *AdvancedAIChatbot) handleGeneralIntent(message string, analysis *MessageAnalysis, context map[string]interface{}) (string, error) {
	// Use AI for general conversation
	prompt := fmt.Sprintf(`
You are a helpful AI assistant for managing an Obsidian vault. The user said: "%s"

Context: %v

Respond in a helpful, friendly way. If you're not sure what they want, ask for clarification.
Keep responses concise but informative.
`, message, context)

	requestBody := map[string]interface{}{
		"model":  chatbot.ollamaModel,
		"prompt": prompt,
		"stream": false,
	}

	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		return "I'm not sure how to help with that. Could you be more specific?", nil
	}

	resp, err := chatbot.ollamaClient.Post(
		fmt.Sprintf("%s/api/generate", chatbot.ollamaHost),
		"application/json",
		strings.NewReader(string(jsonBody)),
	)
	if err != nil {
		return "I'm having trouble processing your request right now. Please try again.", nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "I'm not sure how to help with that. Could you be more specific?", nil
	}

	var response struct {
		Response string `json:"response"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return "I'm not sure how to help with that. Could you be more specific?", nil
	}

	return response.Response, nil
}

// Helper methods
func (chatbot *AdvancedAIChatbot) generateWelcomeMessage() string {
	return `👋 Hello! I'm your AI assistant for managing your Obsidian vault. 

I can help you:
• 🔍 Search and find content
• 📝 Create and organize notes  
• 📊 Analyze your vault structure
• 💡 Provide recommendations
• 🔄 Sync and manage files

Just tell me what you'd like to do in natural language, and I'll help you out!`
}

func (chatbot *AdvancedAIChatbot) updateContext(message string, analysis *MessageAnalysis) {
	// Update conversation context
	entry := &ContextEntry{
		Type:      "message",
		Content:   message,
		Timestamp: time.Now(),
		Relevance: analysis.Confidence,
	}

	chatbot.context.contextHistory = append(chatbot.context.contextHistory, entry)

	// Keep only recent context (last 10 entries)
	if len(chatbot.context.contextHistory) > 10 {
		chatbot.context.contextHistory = chatbot.context.contextHistory[len(chatbot.context.contextHistory)-10:]
	}
}

func (chatbot *AdvancedAIChatbot) buildContext(session *ConversationSession, analysis *MessageAnalysis) map[string]interface{} {
	context := make(map[string]interface{})

	context["intent"] = analysis.Intent
	context["entities"] = analysis.Entities
	context["confidence"] = analysis.Confidence
	context["session_id"] = session.ID
	context["message_count"] = len(session.Messages)
	context["user_preferences"] = session.Preferences

	return context
}

func (chatbot *AdvancedAIChatbot) extractSearchQuery(message string, analysis *MessageAnalysis) string {
	// Look for search-related entities
	for _, entity := range analysis.Entities {
		if entity.Type == "topic" || entity.Type == "file" {
			return entity.Value
		}
	}

	// Fallback: remove common words and use the rest
	words := strings.Fields(message)
	var queryWords []string

	for _, word := range words {
		word = strings.ToLower(word)
		if word != "search" && word != "find" && word != "look" && word != "for" && word != "about" {
			queryWords = append(queryWords, word)
		}
	}

	return strings.Join(queryWords, " ")
}

func (chatbot *AdvancedAIChatbot) extractTitle(message string, analysis *MessageAnalysis) string {
	// Look for title-related entities
	for _, entity := range analysis.Entities {
		if entity.Type == "file" {
			return entity.Value
		}
	}

	// Fallback: extract from message
	titleRegex := regexp.MustCompile(`(?i)(?:create|make|new)\s+(?:note|file)\s+(?:called|named|about)\s+"?([^"]+)"?`)
	matches := titleRegex.FindStringSubmatch(message)
	if len(matches) > 1 {
		return matches[1]
	}

	return ""
}

func (chatbot *AdvancedAIChatbot) extractContent(message string, analysis *MessageAnalysis) string {
	// Simple content extraction
	return "Created by AI assistant"
}

func (chatbot *AdvancedAIChatbot) simpleMessageAnalysis(message string) MessageAnalysis {
	// Simple fallback analysis
	messageLower := strings.ToLower(message)

	var intent string
	if strings.Contains(messageLower, "search") || strings.Contains(messageLower, "find") {
		intent = "search"
	} else if strings.Contains(messageLower, "create") || strings.Contains(messageLower, "make") {
		intent = "create"
	} else if strings.Contains(messageLower, "organize") || strings.Contains(messageLower, "organize") {
		intent = "organize"
	} else if strings.Contains(messageLower, "analyze") || strings.Contains(messageLower, "analysis") {
		intent = "analyze"
	} else if strings.Contains(messageLower, "recommend") || strings.Contains(messageLower, "suggest") {
		intent = "recommend"
	} else if strings.Contains(messageLower, "help") {
		intent = "help"
	} else {
		intent = "general"
	}

	return MessageAnalysis{
		Intent:     intent,
		Entities:   []Entity{},
		Confidence: 0.7,
	}
}

// MessageAnalysis represents the analysis of a user message
type MessageAnalysis struct {
	Intent     string   `json:"intent"`
	Entities   []Entity `json:"entities"`
	Confidence float64  `json:"confidence"`
}

// Demo function to test advanced AI chatbot
func main() {
	fmt.Println("🤖 ADVANCED AI CHATBOT FOR OBSIDIAN VAULT")
	fmt.Println("==========================================")

	// Configuration
	baseURL := "https://127.0.0.1:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	ollamaHost := "http://localhost:11434"
	ollamaModel := "deepseek-r1:8b"

	// Create advanced AI chatbot
	chatbot := NewAdvancedAIChatbot(baseURL, token, ollamaHost, ollamaModel)

	// Start conversation
	session, err := chatbot.StartConversation("user_001")
	if err != nil {
		fmt.Printf("❌ Failed to start conversation: %v\n", err)
		return
	}

	fmt.Printf("✅ Conversation started: %s\n", session.ID)
	fmt.Printf("👋 Welcome message: %s\n", session.Messages[0].Content)

	// Test conversation
	testMessages := []string{
		"Hello! Can you help me search for logic notes?",
		"Create a new note about machine learning",
		"Analyze my vault structure",
		"Give me some recommendations for improving my vault",
		"What can you help me with?",
	}

	for i, message := range testMessages {
		fmt.Printf("\n👤 User: %s\n", message)

		response, err := chatbot.ProcessMessage(session.ID, message)
		if err != nil {
			fmt.Printf("❌ Error processing message: %v\n", err)
			continue
		}

		fmt.Printf("🤖 Assistant: %s\n", response.Content)
		fmt.Printf("   Intent: %s (%.2f confidence)\n", response.Intent, response.Confidence)

		if len(response.Entities) > 0 {
			fmt.Printf("   Entities: ")
			for _, entity := range response.Entities {
				fmt.Printf("%s:%s ", entity.Type, entity.Value)
			}
			fmt.Println()
		}
	}

	fmt.Println("\n🎉 Advanced AI chatbot is ready for natural language interaction!")
}
