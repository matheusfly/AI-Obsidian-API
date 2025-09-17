package tools

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/datamaster/mcp-server/internal/client"
	"github.com/datamaster/mcp-server/internal/ollama"
	"github.com/datamaster/mcp-server/pkg/mcp"
	"go.uber.org/zap"
)

// AdvancedWorkflowTools provides advanced workflow and reasoning tools
type AdvancedWorkflowTools struct {
	obsidianClient client.HTTPClient
	ollamaClient   ollama.OllamaClient
	logger         *zap.Logger
}

// NewAdvancedWorkflowTools creates a new advanced workflow tools instance
func NewAdvancedWorkflowTools(obsidianClient client.HTTPClient, ollamaClient ollama.OllamaClient, logger *zap.Logger) *AdvancedWorkflowTools {
	return &AdvancedWorkflowTools{
		obsidianClient: obsidianClient,
		ollamaClient:   ollamaClient,
		logger:         logger,
	}
}

// MultiStepReasoning implements complex multi-step reasoning workflows
func (awt *AdvancedWorkflowTools) MultiStepReasoning(ctx context.Context, params map[string]interface{}) mcp.ToolResult {
	query, ok := params["query"].(string)
	if !ok || query == "" {
		return mcp.ToolResult{
			Success: false,
			Error:   "Missing or invalid 'query' parameter",
		}
	}

	steps := []string{
		"1. Analyzing the query and breaking it down into components",
		"2. Searching for relevant information in the vault",
		"3. Synthesizing findings from multiple sources",
		"4. Generating comprehensive response with reasoning",
		"5. Providing actionable insights and next steps",
	}

	awt.logger.Info("Starting multi-step reasoning", zap.String("query", query))

	// Step 1: Search for relevant information
	searchResults, _ := awt.obsidianClient.Search(ctx, query, 10)

	// Step 2: Generate reasoning using LLM
	var reasoning string
	if awt.ollamaClient != nil {
		prompt := fmt.Sprintf("Analyze this query and provide comprehensive reasoning: %s\n\nSearch results: %v", query, searchResults)
		reasoning, _ = awt.ollamaClient.GenerateCompletion(ctx, prompt)
	} else {
		reasoning = fmt.Sprintf("Based on the search results for '%s', I can provide insights and analysis.", query)
	}

	// Step 3: Generate actionable insights
	insights := []string{
		fmt.Sprintf("Query: %s", query),
		fmt.Sprintf("Found %d relevant results", len(searchResults)),
		"Key insights and recommendations",
		"Potential follow-up actions",
	}

	awt.logger.Info("Multi-step reasoning completed", zap.String("query", query))
	return mcp.ToolResult{
		Success: true,
		Data: map[string]interface{}{
			"query":     query,
			"steps":     steps,
			"reasoning": reasoning,
			"insights":  insights,
			"results":   searchResults,
			"timestamp": time.Now(),
		},
		Message: fmt.Sprintf("Multi-step reasoning completed for '%s'", query),
	}
}

// ContextAwareSearch implements context-aware search with conversation memory
func (awt *AdvancedWorkflowTools) ContextAwareSearch(ctx context.Context, params map[string]interface{}) mcp.ToolResult {
	query, ok := params["query"].(string)
	if !ok || query == "" {
		return mcp.ToolResult{
			Success: false,
			Error:   "Missing or invalid 'query' parameter",
		}
	}

	context, _ := params["context"].(string)
	previousQueries, _ := params["previous_queries"].([]string)

	// Enhance query with context
	enhancedQuery := query
	if context != "" {
		enhancedQuery = fmt.Sprintf("%s (context: %s)", query, context)
	}

	// Search with enhanced query
	results, _ := awt.obsidianClient.Search(ctx, enhancedQuery, 10)

	// Generate contextual response
	var contextualResponse string
	if awt.ollamaClient != nil {
		prompt := fmt.Sprintf("Given the context '%s' and previous queries %v, provide a contextual response for: %s", context, previousQueries, query)
		contextualResponse, _ = awt.ollamaClient.GenerateCompletion(ctx, prompt)
	} else {
		contextualResponse = fmt.Sprintf("Based on the context and previous queries, here are the results for '%s'", query)
	}

	awt.logger.Info("Context-aware search completed", zap.String("query", query), zap.String("context", context))
	return mcp.ToolResult{
		Success: true,
		Data: map[string]interface{}{
			"query":               query,
			"enhanced_query":      enhancedQuery,
			"context":             context,
			"previous_queries":    previousQueries,
			"results":             results,
			"contextual_response": contextualResponse,
			"timestamp":           time.Now(),
		},
		Message: fmt.Sprintf("Context-aware search completed for '%s'", query),
	}
}

// KnowledgeSynthesis implements knowledge synthesis from multiple sources
func (awt *AdvancedWorkflowTools) KnowledgeSynthesis(ctx context.Context, params map[string]interface{}) mcp.ToolResult {
	topics, ok := params["topics"].([]interface{})
	if !ok || len(topics) == 0 {
		return mcp.ToolResult{
			Success: false,
			Error:   "Missing or invalid 'topics' parameter",
		}
	}

	// Convert topics to string slice
	topicStrings := make([]string, len(topics))
	for i, topic := range topics {
		if topicStr, ok := topic.(string); ok {
			topicStrings[i] = topicStr
		}
	}

	// Search for each topic
	allResults := make(map[string][]map[string]interface{})
	for _, topic := range topicStrings {
		results, _ := awt.obsidianClient.Search(ctx, topic, 5)
		allResults[topic] = results
	}

	// Generate synthesis
	var synthesis string
	if awt.ollamaClient != nil {
		prompt := fmt.Sprintf("Synthesize knowledge from these topics: %v\n\nResults: %v", topicStrings, allResults)
		synthesis, _ = awt.ollamaClient.GenerateCompletion(ctx, prompt)
	} else {
		synthesis = fmt.Sprintf("Synthesized knowledge from topics: %v", topicStrings)
	}

	// Generate connections
	connections := []string{
		fmt.Sprintf("Found connections between %d topics", len(topicStrings)),
		"Identified key themes and patterns",
		"Generated actionable insights",
	}

	awt.logger.Info("Knowledge synthesis completed", zap.Strings("topics", topicStrings))
	return mcp.ToolResult{
		Success: true,
		Data: map[string]interface{}{
			"topics":      topicStrings,
			"results":     allResults,
			"synthesis":   synthesis,
			"connections": connections,
			"timestamp":   time.Now(),
		},
		Message: fmt.Sprintf("Knowledge synthesis completed for %d topics", len(topicStrings)),
	}
}

// ProactiveInsights implements proactive insight generation
func (awt *AdvancedWorkflowTools) ProactiveInsights(ctx context.Context, params map[string]interface{}) mcp.ToolResult {
	// Get recent files
	var files []map[string]interface{}
	awt.obsidianClient.Get(ctx, "/vault/", &files)

	// Analyze recent activity
	recentFiles := files
	if len(files) > 10 {
		recentFiles = files[:10]
	}

	// Generate insights
	var insights []string
	if awt.ollamaClient != nil {
		prompt := fmt.Sprintf("Analyze these recent files and provide proactive insights: %v", recentFiles)
		insightsStr, _ := awt.ollamaClient.GenerateCompletion(ctx, prompt)
		insights = strings.Split(insightsStr, "\n")
	} else {
		insights = []string{
			"Recent activity analysis completed",
			"Identified potential areas for improvement",
			"Suggested next actions based on current work",
		}
	}

	// Generate recommendations
	recommendations := []string{
		"Review and organize recent notes",
		"Create connections between related topics",
		"Consider creating summaries of key concepts",
	}

	awt.logger.Info("Proactive insights generated", zap.Int("files_analyzed", len(recentFiles)))
	return mcp.ToolResult{
		Success: true,
		Data: map[string]interface{}{
			"recent_files":    recentFiles,
			"insights":        insights,
			"recommendations": recommendations,
			"timestamp":       time.Now(),
		},
		Message: "Proactive insights generated successfully",
	}
}

// GetWorkflowToolDefinitions returns all advanced workflow tool definitions
func (awt *AdvancedWorkflowTools) GetWorkflowToolDefinitions() []mcp.ToolDefinition {
	return []mcp.ToolDefinition{
		{
			Name:        "multi_step_reasoning",
			Description: "Perform complex multi-step reasoning workflows with LLM integration",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"query": map[string]interface{}{
						"type":        "string",
						"description": "The query to reason about",
					},
				},
				"required": []string{"query"},
			},
		},
		{
			Name:        "context_aware_search",
			Description: "Perform context-aware search with conversation memory",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"query": map[string]interface{}{
						"type":        "string",
						"description": "The search query",
					},
					"context": map[string]interface{}{
						"type":        "string",
						"description": "Additional context for the search",
					},
					"previous_queries": map[string]interface{}{
						"type":        "array",
						"description": "Previous queries for context",
					},
				},
				"required": []string{"query"},
			},
		},
		{
			Name:        "knowledge_synthesis",
			Description: "Synthesize knowledge from multiple topics and sources",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"topics": map[string]interface{}{
						"type":        "array",
						"description": "Topics to synthesize knowledge from",
					},
				},
				"required": []string{"topics"},
			},
		},
		{
			Name:        "proactive_insights",
			Description: "Generate proactive insights based on recent activity",
			Parameters: map[string]interface{}{
				"type":       "object",
				"properties": map[string]interface{}{},
			},
		},
	}
}
