package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"sort"
	"strings"
	"time"
)

// LinkAnalysisEngine provides advanced link analysis using graph algorithms
type LinkAnalysisEngine struct {
	baseURL string
	token   string
	client  *http.Client
}

// NewLinkAnalysisEngine creates a new link analysis engine
func NewLinkAnalysisEngine(baseURL, token string) *LinkAnalysisEngine {
	return &LinkAnalysisEngine{
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

// Link represents a link between notes
type Link struct {
	Source      string `json:"source"`
	Target      string `json:"target"`
	Type        string `json:"type"`        // "internal", "external", "attachment"
	Context     string `json:"context"`     // Text around the link
	Position    int    `json:"position"`    // Position in the file
	Anchor      string `json:"anchor"`      // Anchor text
	IsBidirectional bool `json:"is_bidirectional"`
}

// Node represents a note in the graph
type Node struct {
	File        string   `json:"file"`
	Title       string   `json:"title"`
	InLinks     []string `json:"in_links"`
	OutLinks    []string `json:"out_links"`
	InDegree    int      `json:"in_degree"`
	OutDegree   int      `json:"out_degree"`
	Centrality  float64  `json:"centrality"`
	PageRank    float64  `json:"page_rank"`
	Tags        []string `json:"tags"`
	Content     string   `json:"content"`
	WordCount   int      `json:"word_count"`
	LastModified string  `json:"last_modified"`
}

// Graph represents the complete link graph
type Graph struct {
	Nodes      map[string]*Node `json:"nodes"`
	Links      []Link            `json:"links"`
	Statistics GraphStatistics   `json:"statistics"`
}

// GraphStatistics provides graph analysis statistics
type GraphStatistics struct {
	TotalNodes     int     `json:"total_nodes"`
	TotalLinks     int     `json:"total_links"`
	AverageDegree  float64 `json:"average_degree"`
	MaxInDegree    int     `json:"max_in_degree"`
	MaxOutDegree   int     `json:"max_out_degree"`
	IsolatedNodes  int     `json:"isolated_nodes"`
	ConnectedComponents int `json:"connected_components"`
	Density        float64 `json:"density"`
	ClusteringCoefficient float64 `json:"clustering_coefficient"`
}

// LinkAnalysisResult represents the result of link analysis
type LinkAnalysisResult struct {
	Graph           Graph                    `json:"graph"`
	HubNodes        []Node                   `json:"hub_nodes"`
	AuthorityNodes  []Node                   `json:"authority_nodes"`
	IsolatedNodes   []Node                   `json:"isolated_nodes"`
	StronglyConnected []string               `json:"strongly_connected"`
	Recommendations []LinkRecommendation     `json:"recommendations"`
	AnalysisTime    int64                    `json:"analysis_time_ms"`
}

// LinkRecommendation represents a link recommendation
type LinkRecommendation struct {
	Source      string  `json:"source"`
	Target      string  `json:"target"`
	Reason      string  `json:"reason"`
	Confidence  float64 `json:"confidence"`
	Type        string  `json:"type"` // "missing", "suggested", "broken"
}

// AnalyzeLinks performs comprehensive link analysis
func (lae *LinkAnalysisEngine) AnalyzeLinks() (*LinkAnalysisResult, error) {
	start := time.Now()
	
	fmt.Println("🔗 Starting comprehensive link analysis...")
	
	// Step 1: Build the graph
	graph, err := lae.buildGraph()
	if err != nil {
		return nil, fmt.Errorf("failed to build graph: %v", err)
	}
	
	// Step 2: Calculate graph statistics
	lae.calculateGraphStatistics(&graph)
	
	// Step 3: Identify hub and authority nodes
	hubNodes := lae.identifyHubNodes(graph)
	authorityNodes := lae.identifyAuthorityNodes(graph)
	
	// Step 4: Find isolated nodes
	isolatedNodes := lae.findIsolatedNodes(graph)
	
	// Step 5: Find strongly connected components
	stronglyConnected := lae.findStronglyConnectedComponents(graph)
	
	// Step 6: Generate link recommendations
	recommendations := lae.generateLinkRecommendations(graph)
	
	duration := time.Since(start).Milliseconds()
	
	fmt.Printf("✅ Link analysis completed in %dms\n", duration)
	fmt.Printf("📊 Analyzed %d nodes and %d links\n", graph.Statistics.TotalNodes, graph.Statistics.TotalLinks)
	
	return &LinkAnalysisResult{
		Graph:           graph,
		HubNodes:        hubNodes,
		AuthorityNodes:  authorityNodes,
		IsolatedNodes:   isolatedNodes,
		StronglyConnected: stronglyConnected,
		Recommendations: recommendations,
		AnalysisTime:    duration,
	}, nil
}

// buildGraph builds the complete link graph
func (lae *LinkAnalysisEngine) buildGraph() (Graph, error) {
	fmt.Println("🏗️ Building link graph...")
	
	graph := Graph{
		Nodes: make(map[string]*Node),
		Links: []Link{},
	}
	
	// Get all files
	files, err := lae.getAllFiles()
	if err != nil {
		return graph, err
	}
	
	// Process each file
	for _, file := range files {
		if strings.HasSuffix(strings.ToLower(file), ".md") {
			node, links, err := lae.processFile(file)
			if err != nil {
				fmt.Printf("⚠️ Failed to process %s: %v\n", file, err)
				continue
			}
			
			graph.Nodes[file] = node
			graph.Links = append(graph.Links, links...)
		}
	}
	
	// Calculate degrees
	lae.calculateDegrees(&graph)
	
	return graph, nil
}

// processFile processes a single file and extracts links
func (lae *LinkAnalysisEngine) processFile(filename string) (*Node, []Link, error) {
	content, err := lae.readFileContent(filename)
	if err != nil {
		return nil, nil, err
	}
	
	// Extract title from filename or content
	title := lae.extractTitle(filename, content)
	
	// Extract tags
	tags := lae.extractTags(content)
	
	// Extract links
	links := lae.extractLinks(filename, content)
	
	// Create node
	node := &Node{
		File:      filename,
		Title:     title,
		Tags:      tags,
		Content:   content,
		WordCount: len(strings.Fields(content)),
		InLinks:   []string{},
		OutLinks:  []string{},
	}
	
	// Extract outbound links
	for _, link := range links {
		node.OutLinks = append(node.OutLinks, link.Target)
	}
	
	return node, links, nil
}

// extractLinks extracts all links from content
func (lae *LinkAnalysisEngine) extractLinks(filename, content string) []Link {
	var links []Link
	
	// Extract internal links [[note]] or [[note|display]]
	internalRegex := regexp.MustCompile(`\[\[([^|\]]+)(?:\|([^\]]+))?\]\]`)
	matches := internalRegex.FindAllStringSubmatch(content, -1)
	
	for i, match := range matches {
		if len(match) >= 2 {
			target := strings.TrimSpace(match[1])
			anchor := target
			if len(match) > 2 && match[2] != "" {
				anchor = match[2]
			}
			
			links = append(links, Link{
				Source:   filename,
				Target:   target,
				Type:     "internal",
				Anchor:   anchor,
				Position: i,
				Context:  lae.extractContext(content, match[0]),
			})
		}
	}
	
	// Extract external links [text](url)
	externalRegex := regexp.MustCompile(`\[([^\]]+)\]\(([^)]+)\)`)
	externalMatches := externalRegex.FindAllStringSubmatch(content, -1)
	
	for i, match := range externalMatches {
		if len(match) >= 3 {
			links = append(links, Link{
				Source:   filename,
				Target:   match[2],
				Type:     "external",
				Anchor:   match[1],
				Position: i,
				Context:  lae.extractContext(content, match[0]),
			})
		}
	}
	
	return links
}

// extractTitle extracts title from filename or content
func (lae *LinkAnalysisEngine) extractTitle(filename, content string) string {
	// Try to extract title from frontmatter
	titleRegex := regexp.MustCompile(`(?i)^title:\s*(.+)$`)
	matches := titleRegex.FindStringSubmatch(content)
	if len(matches) > 1 {
		return strings.TrimSpace(matches[1])
	}
	
	// Try to extract first heading
	headingRegex := regexp.MustCompile(`^#\s+(.+)$`)
	headingMatches := headingRegex.FindStringSubmatch(content)
	if len(headingMatches) > 1 {
		return strings.TrimSpace(headingMatches[1])
	}
	
	// Use filename as title
	name := strings.TrimSuffix(filename, ".md")
	return strings.ReplaceAll(name, "_", " ")
}

// extractTags extracts tags from content
func (lae *LinkAnalysisEngine) extractTags(content string) []string {
	var tags []string
	
	// Extract frontmatter tags
	frontmatterRegex := regexp.MustCompile(`(?s)^---\n(.*?)\n---`)
	matches := frontmatterRegex.FindStringSubmatch(content)
	
	if len(matches) > 1 {
		frontmatter := matches[1]
		tagsRegex := regexp.MustCompile(`(?i)tags?:\s*(.*)`)
		tagMatches := tagsRegex.FindStringSubmatch(frontmatter)
		
		if len(tagMatches) > 1 {
			tagString := tagMatches[1]
			if strings.Contains(tagString, "[") {
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
			}
		}
	}
	
	// Extract inline tags
	inlineRegex := regexp.MustCompile(`#([a-zA-Z0-9_-]+)`)
	inlineMatches := inlineRegex.FindAllStringSubmatch(content, -1)
	
	for _, match := range inlineMatches {
		if len(match) > 1 {
			tag := strings.TrimSpace(match[1])
			if tag != "" {
				tags = append(tags, tag)
			}
		}
	}
	
	return tags
}

// extractContext extracts context around a link
func (lae *LinkAnalysisEngine) extractContext(content, linkText string) string {
	index := strings.Index(content, linkText)
	if index == -1 {
		return ""
	}
	
	start := max(0, index-50)
	end := min(len(content), index+len(linkText)+50)
	
	context := content[start:end]
	if start > 0 {
		context = "..." + context
	}
	if end < len(content) {
		context = context + "..."
	}
	
	return context
}

// calculateDegrees calculates in-degree and out-degree for each node
func (lae *LinkAnalysisEngine) calculateDegrees(graph *Graph) {
	for _, link := range graph.Links {
		if link.Type == "internal" {
			// Add to source node's out-degree
			if sourceNode, exists := graph.Nodes[link.Source]; exists {
				sourceNode.OutDegree++
			}
			
			// Add to target node's in-degree
			if targetNode, exists := graph.Nodes[link.Target]; exists {
				targetNode.InDegree++
				targetNode.InLinks = append(targetNode.InLinks, link.Source)
			}
		}
	}
}

// calculateGraphStatistics calculates various graph statistics
func (lae *LinkAnalysisEngine) calculateGraphStatistics(graph *Graph) {
	stats := GraphStatistics{}
	
	stats.TotalNodes = len(graph.Nodes)
	stats.TotalLinks = len(graph.Links)
	
	if stats.TotalNodes == 0 {
		return
	}
	
	// Calculate average degree
	totalDegree := 0
	maxInDegree := 0
	maxOutDegree := 0
	isolatedCount := 0
	
	for _, node := range graph.Nodes {
		totalDegree += node.InDegree + node.OutDegree
		if node.InDegree > maxInDegree {
			maxInDegree = node.InDegree
		}
		if node.OutDegree > maxOutDegree {
			maxOutDegree = node.OutDegree
		}
		if node.InDegree == 0 && node.OutDegree == 0 {
			isolatedCount++
		}
	}
	
	stats.AverageDegree = float64(totalDegree) / float64(stats.TotalNodes)
	stats.MaxInDegree = maxInDegree
	stats.MaxOutDegree = maxOutDegree
	stats.IsolatedNodes = isolatedCount
	
	// Calculate density
	maxPossibleLinks := stats.TotalNodes * (stats.TotalNodes - 1)
	if maxPossibleLinks > 0 {
		stats.Density = float64(stats.TotalLinks) / float64(maxPossibleLinks)
	}
	
	graph.Statistics = stats
}

// identifyHubNodes identifies nodes with high out-degree
func (lae *LinkAnalysisEngine) identifyHubNodes(graph Graph) []Node {
	var hubNodes []Node
	
	for _, node := range graph.Nodes {
		if node.OutDegree > 5 { // Threshold for hub nodes
			hubNodes = append(hubNodes, *node)
		}
	}
	
	// Sort by out-degree
	sort.Slice(hubNodes, func(i, j int) bool {
		return hubNodes[i].OutDegree > hubNodes[j].OutDegree
	})
	
	return hubNodes
}

// identifyAuthorityNodes identifies nodes with high in-degree
func (lae *LinkAnalysisEngine) identifyAuthorityNodes(graph Graph) []Node {
	var authorityNodes []Node
	
	for _, node := range graph.Nodes {
		if node.InDegree > 3 { // Threshold for authority nodes
			authorityNodes = append(authorityNodes, *node)
		}
	}
	
	// Sort by in-degree
	sort.Slice(authorityNodes, func(i, j int) bool {
		return authorityNodes[i].InDegree > authorityNodes[j].InDegree
	})
	
	return authorityNodes
}

// findIsolatedNodes finds nodes with no connections
func (lae *LinkAnalysisEngine) findIsolatedNodes(graph Graph) []Node {
	var isolatedNodes []Node
	
	for _, node := range graph.Nodes {
		if node.InDegree == 0 && node.OutDegree == 0 {
			isolatedNodes = append(isolatedNodes, *node)
		}
	}
	
	return isolatedNodes
}

// findStronglyConnectedComponents finds strongly connected components
func (lae *LinkAnalysisEngine) findStronglyConnectedComponents(graph Graph) []string {
	// Simplified implementation - in practice, you'd use Tarjan's algorithm
	var components []string
	
	visited := make(map[string]bool)
	
	for filename := range graph.Nodes {
		if !visited[filename] {
			component := lae.dfsComponent(filename, graph, visited)
			if len(component) > 1 {
				components = append(components, strings.Join(component, ", "))
			}
		}
	}
	
	return components
}

// dfsComponent performs DFS to find connected components
func (lae *LinkAnalysisEngine) dfsComponent(start string, graph Graph, visited map[string]bool) []string {
	var component []string
	var stack []string
	
	stack = append(stack, start)
	
	for len(stack) > 0 {
		current := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		
		if visited[current] {
			continue
		}
		
		visited[current] = true
		component = append(component, current)
		
		// Add neighbors to stack
		if node, exists := graph.Nodes[current]; exists {
			for _, neighbor := range node.OutLinks {
				if !visited[neighbor] {
					stack = append(stack, neighbor)
				}
			}
			for _, neighbor := range node.InLinks {
				if !visited[neighbor] {
					stack = append(stack, neighbor)
				}
			}
		}
	}
	
	return component
}

// generateLinkRecommendations generates link recommendations
func (lae *LinkAnalysisEngine) generateLinkRecommendations(graph Graph) []LinkRecommendation {
	var recommendations []LinkRecommendation
	
	// Find nodes with similar tags that aren't linked
	for filename, node := range graph.Nodes {
		for otherFilename, otherNode := range graph.Nodes {
			if filename == otherFilename {
				continue
			}
			
			// Check if they share tags
			sharedTags := lae.findSharedTags(node.Tags, otherNode.Tags)
			if len(sharedTags) > 0 {
				// Check if they're already linked
				if !lae.areLinked(node, otherNode) {
					recommendations = append(recommendations, LinkRecommendation{
						Source:     filename,
						Target:     otherFilename,
						Reason:     fmt.Sprintf("Share tags: %s", strings.Join(sharedTags, ", ")),
						Confidence: float64(len(sharedTags)) / float64(len(node.Tags)+len(otherNode.Tags)),
						Type:       "suggested",
					})
				}
			}
		}
	}
	
	// Sort by confidence
	sort.Slice(recommendations, func(i, j int) bool {
		return recommendations[i].Confidence > recommendations[j].Confidence
	})
	
	return recommendations
}

// Helper functions
func (lae *LinkAnalysisEngine) findSharedTags(tags1, tags2 []string) []string {
	var shared []string
	
	for _, tag1 := range tags1 {
		for _, tag2 := range tags2 {
			if strings.EqualFold(tag1, tag2) {
				shared = append(shared, tag1)
			}
		}
	}
	
	return shared
}

func (lae *LinkAnalysisEngine) areLinked(node1, node2 *Node) bool {
	for _, link := range node1.OutLinks {
		if link == node2.File {
			return true
		}
	}
	for _, link := range node1.InLinks {
		if link == node2.File {
			return true
		}
	}
	return false
}

func (lae *LinkAnalysisEngine) getAllFiles() ([]string, error) {
	var allFiles []string
	
	resp, err := lae.makeRequest("GET", "/vault/", nil)
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
			subFiles, err := lae.getDirectoryFiles(file)
			if err == nil {
				allFiles = append(allFiles, subFiles...)
			}
		} else {
			allFiles = append(allFiles, file)
		}
	}
	
	return allFiles, nil
}

func (lae *LinkAnalysisEngine) getDirectoryFiles(dirPath string) ([]string, error) {
	resp, err := lae.makeRequest("GET", "/vault/"+url.PathEscape(dirPath), nil)
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
			subFiles, err := lae.getDirectoryFiles(dirPath + file)
			if err == nil {
				files = append(files, subFiles...)
			}
		} else {
			files = append(files, dirPath+file)
		}
	}
	
	return files, nil
}

func (lae *LinkAnalysisEngine) readFileContent(filename string) (string, error) {
	resp, err := lae.makeRequest("GET", "/vault/"+url.PathEscape(filename), nil)
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

func (lae *LinkAnalysisEngine) makeRequest(method, path string, body io.Reader) (*http.Response, error) {
	req, err := http.NewRequest(method, lae.baseURL+path, body)
	if err != nil {
		return nil, err
	}
	
	req.Header.Set("Authorization", "Bearer "+lae.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	
	return lae.client.Do(req)
}

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

// Demo function to test link analysis
func main() {
	fmt.Println("🔗 ADVANCED LINK ANALYSIS ENGINE")
	fmt.Println("================================")
	
	// Configuration
	baseURL := "https://127.0.0.1:27124"
	token := "b26efa44ceb0bd4e1fae338cede5384237bbab8624c61927986aa3f06c2f5a70"
	
	// Create link analysis engine
	lae := NewLinkAnalysisEngine(baseURL, token)
	
	// Perform link analysis
	result, err := lae.AnalyzeLinks()
	if err != nil {
		fmt.Printf("❌ Link analysis failed: %v\n", err)
		return
	}
	
	// Display results
	fmt.Printf("📊 Graph Statistics:\n")
	fmt.Printf("   • Total nodes: %d\n", result.Graph.Statistics.TotalNodes)
	fmt.Printf("   • Total links: %d\n", result.Graph.Statistics.TotalLinks)
	fmt.Printf("   • Average degree: %.2f\n", result.Graph.Statistics.AverageDegree)
	fmt.Printf("   • Density: %.4f\n", result.Graph.Statistics.Density)
	fmt.Printf("   • Isolated nodes: %d\n", result.Graph.Statistics.IsolatedNodes)
	
	fmt.Printf("\n🏆 Hub Nodes (high out-degree):\n")
	for i, node := range result.HubNodes {
		if i >= 5 { // Show top 5
			break
		}
		fmt.Printf("   %d. %s (%d out-links)\n", i+1, node.Title, node.OutDegree)
	}
	
	fmt.Printf("\n🎯 Authority Nodes (high in-degree):\n")
	for i, node := range result.AuthorityNodes {
		if i >= 5 { // Show top 5
			break
		}
		fmt.Printf("   %d. %s (%d in-links)\n", i+1, node.Title, node.InDegree)
	}
	
	fmt.Printf("\n🔗 Link Recommendations:\n")
	for i, rec := range result.Recommendations {
		if i >= 5 { // Show top 5
			break
		}
		fmt.Printf("   %d. %s → %s (%.2f confidence)\n", i+1, rec.Source, rec.Target, rec.Confidence)
		fmt.Printf("      Reason: %s\n", rec.Reason)
	}
	
	fmt.Printf("\n⏱️ Analysis completed in %dms\n", result.AnalysisTime)
	fmt.Println("\n🎉 Link analysis engine is ready!")
}
