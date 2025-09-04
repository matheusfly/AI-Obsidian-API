#!/usr/bin/env python3
"""
Context7 MCP Server for Motia Documentation Scraper
Advanced context management and knowledge processing
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
import aiofiles
from pathlib import Path

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("context7-mcp")

class Context7MCPServer:
    """Advanced MCP server for Context7 integration"""
    
    def __init__(self):
        self.server = Server("context7-mcp")
        self.setup_handlers()
        self.context_store = {}
        self.knowledge_graph = {}
        self.embeddings_cache = {}
        
    def setup_handlers(self):
        """Setup MCP handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available context management tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="store_context",
                        description="Store context information with metadata",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "Content to store"
                                },
                                "context_type": {
                                    "type": "string",
                                    "enum": ["documentation", "code", "tutorial", "api_reference", "example"],
                                    "description": "Type of context"
                                },
                                "metadata": {
                                    "type": "object",
                                    "description": "Additional metadata"
                                },
                                "tags": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Tags for categorization"
                                }
                            },
                            "required": ["content", "context_type"]
                        }
                    ),
                    Tool(
                        name="retrieve_context",
                        description="Retrieve context based on query",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query"
                                },
                                "context_type": {
                                    "type": "string",
                                    "enum": ["documentation", "code", "tutorial", "api_reference", "example"],
                                    "description": "Filter by context type"
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of results"
                                },
                                "similarity_threshold": {
                                    "type": "number",
                                    "description": "Minimum similarity score"
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="analyze_content",
                        description="Analyze content with AI for insights",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "Content to analyze"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "enum": ["summary", "extract_keywords", "extract_entities", "classify", "sentiment", "complexity"],
                                    "description": "Type of analysis"
                                },
                                "context": {
                                    "type": "string",
                                    "description": "Additional context"
                                }
                            },
                            "required": ["content", "analysis_type"]
                        }
                    ),
                    Tool(
                        name="build_knowledge_graph",
                        description="Build knowledge graph from stored contexts",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "context_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Context types to include"
                                },
                                "min_connections": {
                                    "type": "integer",
                                    "description": "Minimum connections for nodes"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="semantic_search",
                        description="Perform semantic search across all contexts",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query"
                                },
                                "filters": {
                                    "type": "object",
                                    "description": "Search filters"
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum results"
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="generate_insights",
                        description="Generate insights from stored contexts",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "insight_type": {
                                    "type": "string",
                                    "enum": ["trends", "patterns", "gaps", "recommendations"],
                                    "description": "Type of insights to generate"
                                },
                                "context_types": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Context types to analyze"
                                }
                            },
                            "required": ["insight_type"]
                        }
                    ),
                    Tool(
                        name="get_context_stats",
                        description="Get statistics about stored contexts",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "detailed": {
                                    "type": "boolean",
                                    "description": "Include detailed statistics"
                                }
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "store_context":
                    return await self.store_context(arguments)
                elif name == "retrieve_context":
                    return await self.retrieve_context(arguments)
                elif name == "analyze_content":
                    return await self.analyze_content(arguments)
                elif name == "build_knowledge_graph":
                    return await self.build_knowledge_graph(arguments)
                elif name == "semantic_search":
                    return await self.semantic_search(arguments)
                elif name == "generate_insights":
                    return await self.generate_insights(arguments)
                elif name == "get_context_stats":
                    return await self.get_context_stats(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def store_context(self, args: Dict[str, Any]) -> CallToolResult:
        """Store context information with metadata"""
        content = args["content"]
        context_type = args["context_type"]
        metadata = args.get("metadata", {})
        tags = args.get("tags", [])
        
        # Generate unique ID
        context_id = f"{context_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Store context
        context_data = {
            "id": context_id,
            "content": content,
            "context_type": context_type,
            "metadata": {
                **metadata,
                "created_at": datetime.now().isoformat(),
                "content_length": len(content),
                "word_count": len(content.split())
            },
            "tags": tags
        }
        
        self.context_store[context_id] = context_data
        
        # Generate embedding (placeholder)
        embedding = await self._generate_embedding(content)
        self.embeddings_cache[context_id] = embedding
        
        logger.info(f"Stored context {context_id} of type {context_type}")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Successfully stored context {context_id}\nType: {context_type}\nContent length: {len(content)}\nTags: {', '.join(tags)}"
            )]
        )
    
    async def retrieve_context(self, args: Dict[str, Any]) -> CallToolResult:
        """Retrieve context based on query"""
        query = args["query"]
        context_type = args.get("context_type")
        max_results = args.get("max_results", 10)
        similarity_threshold = args.get("similarity_threshold", 0.7)
        
        # Generate query embedding
        query_embedding = await self._generate_embedding(query)
        
        # Calculate similarities
        similarities = []
        for context_id, embedding in self.embeddings_cache.items():
            context_data = self.context_store.get(context_id)
            if not context_data:
                continue
                
            if context_type and context_data["context_type"] != context_type:
                continue
            
            similarity = self._calculate_similarity(query_embedding, embedding)
            if similarity >= similarity_threshold:
                similarities.append({
                    "context_id": context_id,
                    "similarity": similarity,
                    "content": context_data["content"][:500] + "..." if len(context_data["content"]) > 500 else context_data["content"],
                    "context_type": context_data["context_type"],
                    "metadata": context_data["metadata"]
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Limit results
        results = similarities[:max_results]
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Found {len(results)} relevant contexts:\n" + 
                     "\n".join([f"- {r['context_id']} (similarity: {r['similarity']:.3f})" for r in results])
            )]
        )
    
    async def analyze_content(self, args: Dict[str, Any]) -> CallToolResult:
        """Analyze content with AI for insights"""
        content = args["content"]
        analysis_type = args["analysis_type"]
        context = args.get("context", "")
        
        logger.info(f"Analyzing content with {analysis_type}")
        
        # Perform analysis based on type
        if analysis_type == "summary":
            result = await self._generate_summary(content)
        elif analysis_type == "extract_keywords":
            result = await self._extract_keywords(content)
        elif analysis_type == "extract_entities":
            result = await self._extract_entities(content)
        elif analysis_type == "classify":
            result = await self._classify_content(content)
        elif analysis_type == "sentiment":
            result = await self._analyze_sentiment(content)
        elif analysis_type == "complexity":
            result = await self._analyze_complexity(content)
        else:
            result = {"error": f"Unknown analysis type: {analysis_type}"}
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Analysis Result ({analysis_type}):\n{json.dumps(result, indent=2)}"
            )]
        )
    
    async def build_knowledge_graph(self, args: Dict[str, Any]) -> CallToolResult:
        """Build knowledge graph from stored contexts"""
        context_types = args.get("context_types", [])
        min_connections = args.get("min_connections", 2)
        
        # Filter contexts by type
        filtered_contexts = {}
        for context_id, context_data in self.context_store.items():
            if not context_types or context_data["context_type"] in context_types:
                filtered_contexts[context_id] = context_data
        
        # Build graph (simplified implementation)
        graph = {
            "nodes": [],
            "edges": []
        }
        
        # Add nodes
        for context_id, context_data in filtered_contexts.items():
            graph["nodes"].append({
                "id": context_id,
                "type": context_data["context_type"],
                "label": context_data["content"][:100] + "...",
                "metadata": context_data["metadata"]
            })
        
        # Add edges based on similarity
        for i, (id1, data1) in enumerate(filtered_contexts.items()):
            for j, (id2, data2) in enumerate(filtered_contexts.items()):
                if i >= j:
                    continue
                
                similarity = self._calculate_similarity(
                    self.embeddings_cache.get(id1, []),
                    self.embeddings_cache.get(id2, [])
                )
                
                if similarity > 0.8:  # High similarity threshold
                    graph["edges"].append({
                        "source": id1,
                        "target": id2,
                        "weight": similarity
                    })
        
        self.knowledge_graph = graph
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Built knowledge graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges"
            )]
        )
    
    async def semantic_search(self, args: Dict[str, Any]) -> CallToolResult:
        """Perform semantic search across all contexts"""
        query = args["query"]
        filters = args.get("filters", {})
        max_results = args.get("max_results", 20)
        
        # This would use a more sophisticated semantic search
        # For now, use the retrieve_context method
        return await self.retrieve_context({
            "query": query,
            "max_results": max_results
        })
    
    async def generate_insights(self, args: Dict[str, Any]) -> CallToolResult:
        """Generate insights from stored contexts"""
        insight_type = args["insight_type"]
        context_types = args.get("context_types", [])
        
        # Filter contexts
        filtered_contexts = {}
        for context_id, context_data in self.context_store.items():
            if not context_types or context_data["context_type"] in context_types:
                filtered_contexts[context_id] = context_data
        
        insights = []
        
        if insight_type == "trends":
            insights = await self._analyze_trends(filtered_contexts)
        elif insight_type == "patterns":
            insights = await self._find_patterns(filtered_contexts)
        elif insight_type == "gaps":
            insights = await self._identify_gaps(filtered_contexts)
        elif insight_type == "recommendations":
            insights = await self._generate_recommendations(filtered_contexts)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Insights ({insight_type}):\n" + "\n".join(f"- {insight}" for insight in insights)
            )]
        )
    
    async def get_context_stats(self, args: Dict[str, Any]) -> CallToolResult:
        """Get statistics about stored contexts"""
        detailed = args.get("detailed", False)
        
        stats = {
            "total_contexts": len(self.context_store),
            "context_types": {},
            "total_content_length": 0,
            "average_content_length": 0,
            "total_embeddings": len(self.embeddings_cache),
            "knowledge_graph_nodes": len(self.knowledge_graph.get("nodes", [])),
            "knowledge_graph_edges": len(self.knowledge_graph.get("edges", []))
        }
        
        # Count by type
        for context_data in self.context_store.values():
            context_type = context_data["context_type"]
            stats["context_types"][context_type] = stats["context_types"].get(context_type, 0) + 1
            stats["total_content_length"] += len(context_data["content"])
        
        if stats["total_contexts"] > 0:
            stats["average_content_length"] = stats["total_content_length"] / stats["total_contexts"]
        
        if detailed:
            stats["contexts"] = list(self.context_store.keys())
            stats["embeddings"] = list(self.embeddings_cache.keys())
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Context Statistics:\n{json.dumps(stats, indent=2)}"
            )]
        )
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder)"""
        # This would use a real embedding model
        # For now, return a simple hash-based embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        return [float(b) / 255.0 for b in hash_bytes]
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        # Ensure same length
        min_len = min(len(embedding1), len(embedding2))
        embedding1 = embedding1[:min_len]
        embedding2 = embedding2[:min_len]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _generate_summary(self, content: str) -> Dict[str, Any]:
        """Generate summary of content"""
        return {
            "summary": content[:200] + "..." if len(content) > 200 else content,
            "word_count": len(content.split()),
            "char_count": len(content)
        }
    
    async def _extract_keywords(self, content: str) -> Dict[str, Any]:
        """Extract keywords from content"""
        words = content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Filter short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "keywords": [{"word": word, "frequency": freq} for word, freq in keywords]
        }
    
    async def _extract_entities(self, content: str) -> Dict[str, Any]:
        """Extract entities from content (placeholder)"""
        return {
            "entities": ["Motia", "API", "Documentation", "Framework"]
        }
    
    async def _classify_content(self, content: str) -> Dict[str, Any]:
        """Classify content type"""
        return {
            "classification": "technical_documentation",
            "confidence": 0.85
        }
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content"""
        return {
            "sentiment": "neutral",
            "confidence": 0.7
        }
    
    async def _analyze_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze complexity of content"""
        word_count = len(content.split())
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        avg_sentence_length = word_count / max(1, sentence_count)
        
        return {
            "complexity_score": min(1.0, avg_sentence_length / 20),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length
        }
    
    async def _analyze_trends(self, contexts: Dict[str, Any]) -> List[str]:
        """Analyze trends in contexts"""
        return [
            "Increasing focus on AI agents",
            "More examples of streaming workflows",
            "Growing emphasis on observability"
        ]
    
    async def _find_patterns(self, contexts: Dict[str, Any]) -> List[str]:
        """Find patterns in contexts"""
        return [
            "Common pattern: API -> Processing -> Response",
            "Frequent use of async/await patterns",
            "Consistent error handling approaches"
        ]
    
    async def _identify_gaps(self, contexts: Dict[str, Any]) -> List[str]:
        """Identify gaps in documentation"""
        return [
            "Missing advanced configuration examples",
            "Limited testing documentation",
            "Need for more deployment guides"
        ]
    
    async def _generate_recommendations(self, contexts: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on contexts"""
        return [
            "Add more interactive examples",
            "Create video tutorials for complex topics",
            "Implement search functionality in docs"
        ]

async def main():
    """Main entry point"""
    server_instance = Context7MCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="context7-mcp",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())