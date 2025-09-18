package main

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"
)

// AIPoweredFeatures provides AI-powered features using DeepSeek-R1:8B
type AIPoweredFeatures struct {
	ollamaHost           string
	ollamaModel          string
	client               *http.Client
	apiPipeline          *APIPipeline
	contentAnalyzer      *AIContentAnalyzer
	textGenerator        *AITextGenerator
	contentProcessor     *AIContentProcessor
	insightEngine        *AIInsightEngine
	recommendationEngine *AIRecommendationEngine
	mutex                sync.RWMutex
}

// AIContentAnalyzer analyzes content using AI
type AIContentAnalyzer struct {
	ollamaHost  string
	ollamaModel string
	client      *http.Client
}

// AITextGenerator generates text using AI
type AITextGenerator struct {
	ollamaHost  string
	ollamaModel string
	client      *http.Client
}

// AIContentProcessor processes content using AI
type AIContentProcessor struct {
	ollamaHost  string
	ollamaModel string
	client      *http.Client
}

// AIInsightEngine generates insights using AI
type AIInsightEngine struct {
	ollamaHost  string
	ollamaModel string
	client      *http.Client
}

// AIRecommendationEngine provides recommendations using AI
type AIRecommendationEngine struct {
	ollamaHost  string
	ollamaModel string
	client      *http.Client
}

// AIAnalysisResult represents the result of AI analysis
type AIAnalysisResult struct {
	Success    bool                   `json:"success"`
	Analysis   map[string]interface{} `json:"analysis"`
	Confidence float64                `json:"confidence"`
	Message    string                 `json:"message"`
	Timestamp  time.Time              `json:"timestamp"`
	Duration   time.Duration          `json:"duration"`
}

// AIGenerationResult represents the result of AI text generation
type AIGenerationResult struct {
	Success    bool          `json:"success"`
	Generated  string        `json:"generated"`
	Confidence float64       `json:"confidence"`
	Message    string        `json:"message"`
	Timestamp  time.Time     `json:"timestamp"`
	Duration   time.Duration `json:"duration"`
}

// AIProcessingResult represents the result of AI content processing
type AIProcessingResult struct {
	Success    bool          `json:"success"`
	Processed  string        `json:"processed"`
	Changes    []string      `json:"changes"`
	Confidence float64       `json:"confidence"`
	Message    string        `json:"message"`
	Timestamp  time.Time     `json:"timestamp"`
	Duration   time.Duration `json:"duration"`
}

// AIInsightResult represents the result of AI insight generation
type AIInsightResult struct {
	Success         bool          `json:"success"`
	Insights        []string      `json:"insights"`
	Recommendations []string      `json:"recommendations"`
	Confidence      float64       `json:"confidence"`
	Message         string        `json:"message"`
	Timestamp       time.Time     `json:"timestamp"`
	Duration        time.Duration `json:"duration"`
}

// NewAIPoweredFeatures creates a new AI-powered features system
func NewAIPoweredFeatures(ollamaHost, ollamaModel string, apiPipeline *APIPipeline) *AIPoweredFeatures {
	client := &http.Client{
		Timeout: 60 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}

	return &AIPoweredFeatures{
		ollamaHost:  ollamaHost,
		ollamaModel: ollamaModel,
		client:      client,
		apiPipeline: apiPipeline,
		contentAnalyzer: &AIContentAnalyzer{
			ollamaHost:  ollamaHost,
			ollamaModel: ollamaModel,
			client:      client,
		},
		textGenerator: &AITextGenerator{
			ollamaHost:  ollamaHost,
			ollamaModel: ollamaModel,
			client:      client,
		},
		contentProcessor: &AIContentProcessor{
			ollamaHost:  ollamaHost,
			ollamaModel: ollamaModel,
			client:      client,
		},
		insightEngine: &AIInsightEngine{
			ollamaHost:  ollamaHost,
			ollamaModel: ollamaModel,
			client:      client,
		},
		recommendationEngine: &AIRecommendationEngine{
			ollamaHost:  ollamaHost,
			ollamaModel: ollamaModel,
			client:      client,
		},
	}
}

// AnalyzeContent analyzes content using AI
func (aif *AIPoweredFeatures) AnalyzeContent(content string, analysisType string) *AIAnalysisResult {
	start := time.Now()
	result := &AIAnalysisResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Create analysis prompt based on type
	prompt := aif.createAnalysisPrompt(content, analysisType)

	// Call AI model
	aiResponse, err := aif.callAIModel(prompt)
	if err != nil {
		result.Message = fmt.Sprintf("AI analysis failed: %v", err)
		return result
	}

	// Parse AI response
	analysis, confidence, err := aif.parseAnalysisResponse(aiResponse, analysisType)
	if err != nil {
		result.Message = fmt.Sprintf("Failed to parse AI response: %v", err)
		return result
	}

	result.Success = true
	result.Analysis = analysis
	result.Confidence = confidence
	result.Message = "Content analysis completed successfully"
	result.Duration = time.Since(start)

	return result
}

// GenerateText generates text using AI
func (aif *AIPoweredFeatures) GenerateText(prompt string, options map[string]interface{}) *AIGenerationResult {
	start := time.Now()
	result := &AIGenerationResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Enhance prompt with options
	enhancedPrompt := aif.enhancePrompt(prompt, options)

	// Call AI model
	aiResponse, err := aif.callAIModel(enhancedPrompt)
	if err != nil {
		result.Message = fmt.Sprintf("AI text generation failed: %v", err)
		return result
	}

	// Parse AI response
	generated, confidence, err := aif.parseGenerationResponse(aiResponse)
	if err != nil {
		result.Message = fmt.Sprintf("Failed to parse AI response: %v", err)
		return result
	}

	result.Success = true
	result.Generated = generated
	result.Confidence = confidence
	result.Message = "Text generation completed successfully"
	result.Duration = time.Since(start)

	return result
}

// ProcessContent processes content using AI
func (aif *AIPoweredFeatures) ProcessContent(content string, processingType string, options map[string]interface{}) *AIProcessingResult {
	start := time.Now()
	result := &AIProcessingResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Create processing prompt
	prompt := aif.createProcessingPrompt(content, processingType, options)

	// Call AI model
	aiResponse, err := aif.callAIModel(prompt)
	if err != nil {
		result.Message = fmt.Sprintf("AI content processing failed: %v", err)
		return result
	}

	// Parse AI response
	processed, changes, confidence, err := aif.parseProcessingResponse(aiResponse)
	if err != nil {
		result.Message = fmt.Sprintf("Failed to parse AI response: %v", err)
		return result
	}

	result.Success = true
	result.Processed = processed
	result.Changes = changes
	result.Confidence = confidence
	result.Message = "Content processing completed successfully"
	result.Duration = time.Since(start)

	return result
}

// GenerateInsights generates insights using AI
func (aif *AIPoweredFeatures) GenerateInsights(content string, context map[string]interface{}) *AIInsightResult {
	start := time.Now()
	result := &AIInsightResult{
		Success:   false,
		Timestamp: time.Now(),
	}

	// Create insight prompt
	prompt := aif.createInsightPrompt(content, context)

	// Call AI model
	aiResponse, err := aif.callAIModel(prompt)
	if err != nil {
		result.Message = fmt.Sprintf("AI insight generation failed: %v", err)
		return result
	}

	// Parse AI response
	insights, recommendations, confidence, err := aif.parseInsightResponse(aiResponse)
	if err != nil {
		result.Message = fmt.Sprintf("Failed to parse AI response: %v", err)
		return result
	}

	result.Success = true
	result.Insights = insights
	result.Recommendations = recommendations
	result.Confidence = confidence
	result.Message = "Insight generation completed successfully"
	result.Duration = time.Since(start)

	return result
}

// SummarizeContent summarizes content using AI
func (aif *AIPoweredFeatures) SummarizeContent(content string, maxLength int) *AIGenerationResult {
	options := map[string]interface{}{
		"max_length": maxLength,
		"type":       "summary",
	}
	return aif.GenerateText(fmt.Sprintf("Summarize the following content in %d words or less:\n\n%s", maxLength, content), options)
}

// ExtractKeyPoints extracts key points from content using AI
func (aif *AIPoweredFeatures) ExtractKeyPoints(content string) *AIAnalysisResult {
	return aif.AnalyzeContent(content, "key_points")
}

// ImproveWriting improves writing using AI
func (aif *AIPoweredFeatures) ImproveWriting(content string, style string) *AIProcessingResult {
	options := map[string]interface{}{
		"style": style,
	}
	return aif.ProcessContent(content, "improve_writing", options)
}

// TranslateContent translates content using AI
func (aif *AIPoweredFeatures) TranslateContent(content string, targetLanguage string) *AIProcessingResult {
	options := map[string]interface{}{
		"target_language": targetLanguage,
	}
	return aif.ProcessContent(content, "translate", options)
}

// GenerateTags generates tags using AI
func (aif *AIPoweredFeatures) GenerateTags(content string) *AIAnalysisResult {
	return aif.AnalyzeContent(content, "tags")
}

// GenerateOutline generates outline using AI
func (aif *AIPoweredFeatures) GenerateOutline(content string) *AIGenerationResult {
	options := map[string]interface{}{
		"type": "outline",
	}
	return aif.GenerateText(fmt.Sprintf("Create a detailed outline for the following content:\n\n%s", content), options)
}

// GenerateQuestions generates questions using AI
func (aif *AIPoweredFeatures) GenerateQuestions(content string) *AIGenerationResult {
	options := map[string]interface{}{
		"type": "questions",
	}
	return aif.GenerateText(fmt.Sprintf("Generate thoughtful questions about the following content:\n\n%s", content), options)
}

// Helper methods
func (aif *AIPoweredFeatures) callAIModel(prompt string) (string, error) {
	requestBody := map[string]interface{}{
		"model":  aif.ollamaModel,
		"prompt": prompt,
		"stream": false,
		"options": map[string]interface{}{
			"temperature": 0.7,
			"top_p":       0.9,
			"max_tokens":  2000,
		},
	}

	jsonBody, err := json.Marshal(requestBody)
	if err != nil {
		return "", err
	}

	resp, err := aif.client.Post(
		fmt.Sprintf("%s/api/generate", aif.ollamaHost),
		"application/json",
		bytes.NewBuffer(jsonBody),
	)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("AI model request failed with status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	var response struct {
		Response string `json:"response"`
	}

	if err := json.Unmarshal(body, &response); err != nil {
		return "", err
	}

	return response.Response, nil
}

func (aif *AIPoweredFeatures) createAnalysisPrompt(content, analysisType string) string {
	switch analysisType {
	case "key_points":
		return fmt.Sprintf(`Analyze the following content and extract the key points. Return them as a numbered list:

%s

Key Points:`, content)
	case "tags":
		return fmt.Sprintf(`Analyze the following content and suggest relevant tags. Return them as a comma-separated list:

%s

Tags:`, content)
	case "sentiment":
		return fmt.Sprintf(`Analyze the sentiment of the following content. Return a JSON object with sentiment (positive/negative/neutral) and confidence score:

%s

Analysis:`, content)
	case "readability":
		return fmt.Sprintf(`Analyze the readability of the following content. Return a JSON object with readability score and suggestions for improvement:

%s

Analysis:`, content)
	case "topics":
		return fmt.Sprintf(`Analyze the following content and identify the main topics. Return them as a list:

%s

Topics:`, content)
	default:
		return fmt.Sprintf(`Analyze the following content and provide insights:

%s

Analysis:`, content)
	}
}

func (aif *AIPoweredFeatures) createProcessingPrompt(content, processingType string, options map[string]interface{}) string {
	switch processingType {
	case "improve_writing":
		style := "professional"
		if s, ok := options["style"].(string); ok {
			style = s
		}
		return fmt.Sprintf(`Improve the following content to make it more %s. Return the improved version:

%s

Improved Version:`, style, content)
	case "translate":
		targetLang := "Spanish"
		if lang, ok := options["target_language"].(string); ok {
			targetLang = lang
		}
		return fmt.Sprintf(`Translate the following content to %s:

%s

Translation:`, targetLang, content)
	case "simplify":
		return fmt.Sprintf(`Simplify the following content to make it easier to understand:

%s

Simplified Version:`, content)
	case "expand":
		return fmt.Sprintf(`Expand the following content with more details and examples:

%s

Expanded Version:`, content)
	default:
		return fmt.Sprintf(`Process the following content:

%s

Processed Version:`, content)
	}
}

func (aif *AIPoweredFeatures) createInsightPrompt(content string, context map[string]interface{}) string {
	return fmt.Sprintf(`Analyze the following content and provide insights and recommendations:

%s

Context: %+v

Insights and Recommendations:`, content, context)
}

func (aif *AIPoweredFeatures) enhancePrompt(prompt string, options map[string]interface{}) string {
	enhanced := prompt

	if maxLength, ok := options["max_length"].(int); ok {
		enhanced += fmt.Sprintf("\n\nPlease limit your response to %d words or less.", maxLength)
	}

	if style, ok := options["style"].(string); ok {
		enhanced += fmt.Sprintf("\n\nPlease write in a %s style.", style)
	}

	if tone, ok := options["tone"].(string); ok {
		enhanced += fmt.Sprintf("\n\nPlease use a %s tone.", tone)
	}

	return enhanced
}

func (aif *AIPoweredFeatures) parseAnalysisResponse(response, analysisType string) (map[string]interface{}, float64, error) {
	analysis := make(map[string]interface{})
	confidence := 0.8 // Default confidence

	switch analysisType {
	case "key_points":
		// Extract numbered list
		lines := strings.Split(response, "\n")
		var keyPoints []string
		for _, line := range lines {
			line = strings.TrimSpace(line)
			if line != "" && (strings.HasPrefix(line, "1.") || strings.HasPrefix(line, "2.") || strings.HasPrefix(line, "3.") || strings.HasPrefix(line, "4.") || strings.HasPrefix(line, "5.")) {
				keyPoints = append(keyPoints, line)
			}
		}
		analysis["key_points"] = keyPoints
	case "tags":
		// Extract comma-separated tags
		tags := strings.Split(response, ",")
		var cleanTags []string
		for _, tag := range tags {
			tag = strings.TrimSpace(tag)
			if tag != "" {
				cleanTags = append(cleanTags, tag)
			}
		}
		analysis["tags"] = cleanTags
	case "sentiment":
		// Try to parse JSON
		var sentimentData map[string]interface{}
		if err := json.Unmarshal([]byte(response), &sentimentData); err == nil {
			analysis = sentimentData
		} else {
			// Fallback to simple parsing
			analysis["sentiment"] = "neutral"
			analysis["confidence"] = 0.5
		}
	default:
		analysis["analysis"] = response
	}

	return analysis, confidence, nil
}

func (aif *AIPoweredFeatures) parseGenerationResponse(response string) (string, float64, error) {
	// Clean up response
	generated := strings.TrimSpace(response)
	confidence := 0.8 // Default confidence

	return generated, confidence, nil
}

func (aif *AIPoweredFeatures) parseProcessingResponse(response string) (string, []string, float64, error) {
	// Clean up response
	processed := strings.TrimSpace(response)
	changes := []string{"Content processed by AI"}
	confidence := 0.8 // Default confidence

	return processed, changes, confidence, nil
}

func (aif *AIPoweredFeatures) parseInsightResponse(response string) ([]string, []string, float64, error) {
	// Parse insights and recommendations
	lines := strings.Split(response, "\n")
	var insights []string
	var recommendations []string
	confidence := 0.8 // Default confidence

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line != "" {
			if strings.Contains(strings.ToLower(line), "insight") || strings.Contains(strings.ToLower(line), "observation") {
				insights = append(insights, line)
			} else if strings.Contains(strings.ToLower(line), "recommend") || strings.Contains(strings.ToLower(line), "suggest") {
				recommendations = append(recommendations, line)
			} else {
				insights = append(insights, line)
			}
		}
	}

	return insights, recommendations, confidence, nil
}

// Demo function
func demoAIPoweredFeatures() {
	fmt.Println("🤖 AI-POWERED FEATURES DEMO")
	fmt.Println("===========================")

	// Create API pipeline
	apiPipeline := NewAPIPipeline("obsidian-vault", "https://127.0.0.1:27124",
		"b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70")

	// Create AI-powered features
	aiFeatures := NewAIPoweredFeatures("http://localhost:11434", "deepseek-r1:8b", apiPipeline)

	// Test content
	content := `# Machine Learning in Healthcare

Machine learning is revolutionizing healthcare by enabling predictive analytics, personalized treatment, and automated diagnosis. 

## Key Applications

1. **Predictive Analytics**: ML models can predict patient outcomes and disease progression.
2. **Medical Imaging**: AI can analyze X-rays, MRIs, and CT scans with high accuracy.
3. **Drug Discovery**: ML accelerates the discovery of new medications.
4. **Personalized Medicine**: AI helps tailor treatments to individual patients.

## Challenges

- Data privacy and security concerns
- Need for large, high-quality datasets
- Regulatory compliance requirements
- Integration with existing healthcare systems

## Future Outlook

The future of ML in healthcare looks promising, with continued advances in AI technology and increasing adoption by healthcare providers.`

	// Test different AI features
	fmt.Println("\n🔍 Testing AI Content Analysis...")
	analysisResult := aiFeatures.AnalyzeContent(content, "key_points")
	if analysisResult.Success {
		fmt.Printf("✅ Analysis completed (%.2f confidence)\n", analysisResult.Confidence)
		fmt.Printf("   Key Points: %+v\n", analysisResult.Analysis["key_points"])
	} else {
		fmt.Printf("❌ Analysis failed: %s\n", analysisResult.Message)
	}

	fmt.Println("\n🏷️ Testing AI Tag Generation...")
	tagResult := aiFeatures.GenerateTags(content)
	if tagResult.Success {
		fmt.Printf("✅ Tags generated (%.2f confidence)\n", tagResult.Confidence)
		fmt.Printf("   Tags: %+v\n", tagResult.Analysis["tags"])
	} else {
		fmt.Printf("❌ Tag generation failed: %s\n", tagResult.Message)
	}

	fmt.Println("\n📝 Testing AI Text Generation...")
	generationResult := aiFeatures.SummarizeContent(content, 100)
	if generationResult.Success {
		fmt.Printf("✅ Summary generated (%.2f confidence)\n", generationResult.Confidence)
		fmt.Printf("   Summary: %s\n", generationResult.Generated)
	} else {
		fmt.Printf("❌ Text generation failed: %s\n", generationResult.Message)
	}

	fmt.Println("\n🔧 Testing AI Content Processing...")
	processingResult := aiFeatures.ImproveWriting(content, "academic")
	if processingResult.Success {
		fmt.Printf("✅ Content processed (%.2f confidence)\n", processingResult.Confidence)
		fmt.Printf("   Changes: %+v\n", processingResult.Changes)
	} else {
		fmt.Printf("❌ Content processing failed: %s\n", processingResult.Message)
	}

	fmt.Println("\n💡 Testing AI Insight Generation...")
	insightResult := aiFeatures.GenerateInsights(content, map[string]interface{}{
		"context":  "healthcare technology",
		"audience": "medical professionals",
	})
	if insightResult.Success {
		fmt.Printf("✅ Insights generated (%.2f confidence)\n", insightResult.Confidence)
		fmt.Printf("   Insights: %+v\n", insightResult.Insights)
		fmt.Printf("   Recommendations: %+v\n", insightResult.Recommendations)
	} else {
		fmt.Printf("❌ Insight generation failed: %s\n", insightResult.Message)
	}

	fmt.Println("\n🎉 AI-Powered Features demo completed!")
}

func main() {
	demoAIPoweredFeatures()
}
