#!/usr/bin/env python3
"""
Optimized Gemini Client for LLM Integration
Handles token counting, context assembly, and structured prompt engineering
"""
import logging
import asyncio
import os
import re
import time
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
import tiktoken

logger = logging.getLogger(__name__)

class PromptStyle(Enum):
    """Different prompt styles for different use cases"""
    RESEARCH_ASSISTANT = "research_assistant"
    TECHNICAL_EXPERT = "technical_expert"
    SUMMARIZER = "summarizer"
    ANALYST = "analyst"

@dataclass
class ContextChunk:
    """Structured context chunk with metadata"""
    content: str
    metadata: Dict[str, Any]
    relevance_score: float
    token_count: int
    source_file: str
    chunk_index: int

@dataclass
class LLMResponse:
    """Structured LLM response with metadata"""
    answer: str
    sources_used: List[str]
    confidence_score: float
    token_usage: Dict[str, int]
    processing_time: float
    context_chunks_used: int
    total_context_tokens: int

class GeminiClient:
    """Optimized Gemini client with token counting and context assembly"""
    
    def __init__(self, api_key: Optional[str] = None, max_context_tokens: int = 3072, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        self.max_context_tokens = max_context_tokens
        
        # Initialize tokenizer for token counting
        try:
            # Use tiktoken for token counting (approximation for Gemini)
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            logger.info("✅ Tokenizer initialized for token counting")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize tokenizer: {e}")
            self.tokenizer = None
        
        # Prompt templates for different styles
        self.prompt_templates = self._initialize_prompt_templates()
        
        logger.info(f"✅ GeminiClient initialized with model: {model_name}, max_tokens: {max_context_tokens}")
    
    def _initialize_prompt_templates(self) -> Dict[PromptStyle, str]:
        """Initialize structured prompt templates"""
        return {
            PromptStyle.RESEARCH_ASSISTANT: """
## Role
You are an expert research assistant with access to a personal knowledge base (Obsidian Vault).

## Task
Answer the user's question based *strictly* on the provided context. Do not use prior knowledge.

## Context
The following are the most relevant excerpts from the knowledge base, ranked by relevance:
{context_text}

## User Question
{query}

## Instructions
1. Provide a clear, concise, and comprehensive answer.
2. If the context is insufficient, state "I could not find sufficient information in the provided context to answer your question."
3. Cite the source file(s) you used for your answer.
4. If multiple sources are relevant, synthesize information from all applicable sources.
5. Maintain accuracy and avoid speculation beyond the provided context.

## Response Format
- Start with a direct answer to the question
- Provide supporting details from the context
- End with source citations in the format: "Sources: [filename1], [filename2]"
""",
            
            PromptStyle.TECHNICAL_EXPERT: """
## Role
You are a technical expert analyzing code and technical documentation from a knowledge base.

## Task
Provide technical analysis and guidance based on the provided context.

## Context
Technical excerpts from the knowledge base:
{context_text}

## Technical Question
{query}

## Instructions
1. Analyze the technical content thoroughly
2. Provide specific, actionable technical guidance
3. Include code examples or technical details when relevant
4. Identify potential issues or improvements
5. Reference specific technical concepts from the context

## Response Format
- Technical analysis and recommendations
- Code examples or technical details (if applicable)
- Potential issues or improvements
- Source citations for technical references
""",
            
            PromptStyle.SUMMARIZER: """
## Role
You are an expert summarizer specializing in knowledge base content.

## Task
Create comprehensive summaries based on the provided context.

## Context
Content excerpts from the knowledge base:
{context_text}

## Summarization Request
{query}

## Instructions
1. Create a comprehensive summary of the relevant content
2. Organize information logically and coherently
3. Highlight key points and important details
4. Maintain accuracy and completeness
5. Use clear, professional language

## Response Format
- Executive summary
- Detailed breakdown of key points
- Important details and context
- Source references
""",
            
            PromptStyle.ANALYST: """
## Role
You are a data analyst and insights expert working with knowledge base content.

## Task
Analyze patterns, trends, and insights from the provided context.

## Context
Data and content from the knowledge base:
{context_text}

## Analysis Request
{query}

## Instructions
1. Analyze patterns and trends in the content
2. Provide data-driven insights and observations
3. Identify relationships between different pieces of information
4. Draw meaningful conclusions from the data
5. Suggest actionable recommendations based on analysis

## Response Format
- Key findings and insights
- Pattern analysis and trends
- Data-driven conclusions
- Actionable recommendations
- Supporting evidence from sources
"""
        }
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tokenizer"""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception as e:
                logger.warning(f"Token counting failed: {e}")
        
        # Fallback: rough estimation (words * 1.3)
        return int(len(text.split()) * 1.3)
    
    def format_context_chunk(self, chunk: ContextChunk) -> str:
        """Format a context chunk for inclusion in prompt"""
        metadata = chunk.metadata
        source_info = f"Source: {chunk.source_file}"
        
        # Add additional metadata if available
        if 'heading' in metadata and metadata['heading']:
            source_info += f" | Section: {metadata['heading']}"
        if 'path_category' in metadata and metadata['path_category']:
            source_info += f" | Category: {metadata['path_category']}"
        
        formatted_chunk = f"""
--- {source_info} (Relevance: {chunk.relevance_score:.3f}) ---
{chunk.content}

"""
        return formatted_chunk
    
    def assemble_context(self, context_chunks: List[Dict[str, Any]], max_tokens: Optional[int] = None) -> Tuple[str, List[ContextChunk], int]:
        """
        Assemble context with token counting and relevance-based prioritization
        Args:
            context_chunks: List of search results with metadata
            max_tokens: Maximum tokens for context (defaults to self.max_context_tokens)
        Returns:
            Tuple of (context_text, used_chunks, total_tokens)
        """
        if not context_chunks:
            return "", [], 0
        
        max_tokens = max_tokens or self.max_context_tokens
        
        # Convert to ContextChunk objects and sort by relevance
        chunks = []
        for chunk_data in context_chunks:
            relevance_score = chunk_data.get('final_score', chunk_data.get('similarity', 0))
            content = chunk_data.get('content', '')
            metadata = chunk_data.get('metadata', {})
            source_file = metadata.get('path', 'unknown')
            chunk_index = metadata.get('chunk_index', 0)
            
            token_count = self.count_tokens(content)
            
            context_chunk = ContextChunk(
                content=content,
                metadata=metadata,
                relevance_score=relevance_score,
                token_count=token_count,
                source_file=source_file,
                chunk_index=chunk_index
            )
            chunks.append(context_chunk)
        
        # Sort by relevance score (highest first)
        chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Assemble context with token counting
        context_parts = []
        used_chunks = []
        total_tokens = 0
        
        for chunk in chunks:
            formatted_chunk = self.format_context_chunk(chunk)
            chunk_tokens = self.count_tokens(formatted_chunk)
            
            # Check if adding this chunk would exceed token limit
            if total_tokens + chunk_tokens > max_tokens:
                logger.info(f"Token limit reached ({max_tokens}). Stopping context assembly.")
                break
            
            context_parts.append(formatted_chunk)
            used_chunks.append(chunk)
            total_tokens += chunk_tokens
            
            logger.debug(f"Added chunk from {chunk.source_file} ({chunk_tokens} tokens, relevance: {chunk.relevance_score:.3f})")
        
        context_text = "".join(context_parts)
        
        logger.info(f"Context assembled: {len(used_chunks)} chunks, {total_tokens} tokens")
        return context_text, used_chunks, total_tokens
    
    def create_structured_prompt(self, query: str, context_text: str, style: PromptStyle = PromptStyle.RESEARCH_ASSISTANT) -> str:
        """Create a structured prompt using the specified style"""
        template = self.prompt_templates[style]
        
        # Clean and format the query
        cleaned_query = query.strip()
        
        # Format the prompt
        prompt = template.format(
            context_text=context_text,
            query=cleaned_query
        )
        
        # Add token count information for debugging
        prompt_tokens = self.count_tokens(prompt)
        logger.debug(f"Generated prompt: {prompt_tokens} tokens")
        
        return prompt
    
    async def process_content(self, query: str, context_chunks: List[Dict[str, Any]], 
                            style: PromptStyle = PromptStyle.RESEARCH_ASSISTANT,
                            max_context_tokens: Optional[int] = None) -> LLMResponse:
        """
        Process content with optimized context assembly and structured prompting
        Args:
            query: User's question
            context_chunks: Search results from vector search
            style: Prompt style to use
            max_context_tokens: Override default token limit
        Returns:
            LLMResponse with structured answer and metadata
        """
        start_time = asyncio.get_event_loop().time()
        status = "success"
        
        try:
            logger.info(f"Processing query: '{query[:50]}...' with {len(context_chunks)} context chunks")
            
            # Assemble context with token counting
            context_text, used_chunks, context_tokens = self.assemble_context(
                context_chunks, max_context_tokens
            )
            
            if not context_text.strip():
                logger.warning("No context available for query")
                return LLMResponse(
                    answer="I could not find sufficient information in the provided context to answer your question.",
                    sources_used=[],
                    confidence_score=0.0,
                    token_usage={"context_tokens": 0, "prompt_tokens": 0, "response_tokens": 0},
                    processing_time=asyncio.get_event_loop().time() - start_time,
                    context_chunks_used=0,
                    total_context_tokens=0
                )
            
            # Create structured prompt
            prompt = self.create_structured_prompt(query, context_text, style)
            prompt_tokens = self.count_tokens(prompt)
            
            # Generate response
            logger.info(f"Sending prompt to Gemini ({prompt_tokens} tokens)...")
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            response_tokens = self.count_tokens(response.text)
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Extract sources used
            sources_used = list(set(chunk.source_file for chunk in used_chunks))
            
            # Calculate confidence score based on relevance scores
            avg_relevance = sum(chunk.relevance_score for chunk in used_chunks) / len(used_chunks) if used_chunks else 0
            
            # Create structured response
            llm_response = LLMResponse(
                answer=response.text.strip(),
                sources_used=sources_used,
                confidence_score=avg_relevance,
                token_usage={
                    "context_tokens": context_tokens,
                    "prompt_tokens": prompt_tokens,
                    "response_tokens": response_tokens
                },
                processing_time=processing_time,
                context_chunks_used=len(used_chunks),
                total_context_tokens=context_tokens
            )
            
            logger.info(f"✅ LLM processing complete: {processing_time:.2f}s, {response_tokens} response tokens")
            logger.info(f"Sources used: {sources_used}")
            
            return llm_response
            
        except Exception as e:
            status = "error"
            logger.error(f"❌ Error processing content: {e}")
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return LLMResponse(
                answer=f"I encountered an error while processing your request: {str(e)}",
                sources_used=[],
                confidence_score=0.0,
                token_usage={"context_tokens": 0, "prompt_tokens": 0, "response_tokens": 0},
                processing_time=processing_time,
                context_chunks_used=0,
                total_context_tokens=0
            )
        finally:
            # Record metrics
            processing_time = asyncio.get_event_loop().time() - start_time
            try:
                from ..monitoring.metrics import get_metrics
                metrics = get_metrics()
                metrics.record_llm_request(self.model_name, "process_content", processing_time, status)
                
                # Record token usage if available
                if 'llm_response' in locals() and hasattr(llm_response, 'token_usage'):
                    metrics.record_llm_tokens(self.model_name, "context_tokens", llm_response.token_usage.get("context_tokens", 0))
                    metrics.record_llm_tokens(self.model_name, "prompt_tokens", llm_response.token_usage.get("prompt_tokens", 0))
                    metrics.record_llm_tokens(self.model_name, "response_tokens", llm_response.token_usage.get("response_tokens", 0))
            except Exception as e:
                logger.warning(f"Failed to record LLM metrics: {e}")
    
    async def stream_content(self, query: str, context_chunks: List[Dict[str, Any]], 
                           prompt_style: PromptStyle = PromptStyle.RESEARCH_ASSISTANT) -> AsyncGenerator[str, None]:
        """
        Stream content generation with real-time token delivery
        
        Args:
            query: User query
            context_chunks: List of context chunks with metadata
            prompt_style: Style of prompt to use
            
        Yields:
            str: Text chunks as they are generated
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Sort chunks by relevance score if available (from re-ranking)
            context_chunks.sort(key=lambda x: x.get('final_score', x.get('similarity', 0)), reverse=True)
            
            # Assemble context with token counting
            context_parts = []
            total_tokens = 0
            
            for chunk in context_chunks:
                part = f"--- Source: {chunk['metadata']['path']} (Relevance: {chunk.get('final_score', chunk.get('similarity', 0)):.3f}) ---\n{chunk['content']}\n\n"
                # Rough token estimation (1.3x word count)
                token_count = len(part.split()) * 1.3
                if total_tokens + token_count > self.max_context_tokens:
                    break
                context_parts.append(part)
                total_tokens += token_count
            
            context_text = "".join(context_parts)
            
            # Create structured prompt based on style
            prompt = self.create_structured_prompt(query, context_text, prompt_style)
            
            logger.info(f"Starting streaming generation for query: {query[:50]}...")
            logger.info(f"Context: {len(context_chunks)} chunks, ~{total_tokens:.0f} tokens")
            
            # Generate streaming response
            response = self.model.generate_content(prompt, stream=True)
            
            tokens_generated = 0
            first_token_time = None
            
            for chunk in response:
                if chunk.text:
                    if first_token_time is None:
                        first_token_time = asyncio.get_event_loop().time()
                        time_to_first_token = first_token_time - start_time
                        logger.info(f"Time to first token: {time_to_first_token:.3f}s")
                    
                    tokens_generated += len(chunk.text.split())
                    yield chunk.text
            
            total_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"Streaming completed: {tokens_generated} tokens in {total_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Error in streaming content: {e}")
            yield f"Error: {str(e)}"
    
    async def analyze_content(self, query: str, context_chunks: List[Dict[str, Any]]) -> LLMResponse:
        """Analyze content using analyst prompt style"""
        return await self.process_content(query, context_chunks, PromptStyle.ANALYST)
    
    async def summarize_content(self, query: str, context_chunks: List[Dict[str, Any]]) -> LLMResponse:
        """Summarize content using summarizer prompt style"""
        return await self.process_content(query, context_chunks, PromptStyle.SUMMARIZER)
    
    async def get_technical_guidance(self, query: str, context_chunks: List[Dict[str, Any]]) -> LLMResponse:
        """Get technical guidance using technical expert prompt style"""
        return await self.process_content(query, context_chunks, PromptStyle.TECHNICAL_EXPERT)
    
    def get_token_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics"""
        return {
            "max_context_tokens": self.max_context_tokens,
            "model_name": self.model_name,
            "tokenizer_available": self.tokenizer is not None
        }

# Example usage and testing
async def test_gemini_client():
    """Test the Gemini client functionality"""
    try:
        client = GeminiClient(max_context_tokens=2048)
        
        # Mock context chunks
        mock_chunks = [
            {
                "content": "Python is a high-level programming language known for its simplicity and readability.",
                "metadata": {"path": "python_basics.md", "heading": "Introduction", "chunk_index": 0},
                "similarity": 0.85
            },
            {
                "content": "Machine learning with Python involves libraries like scikit-learn, pandas, and numpy.",
                "metadata": {"path": "ml_python.md", "heading": "Libraries", "chunk_index": 1},
                "similarity": 0.72
            }
        ]
        
        # Test different prompt styles
        query = "What is Python and how is it used in machine learning?"
        
        print("Testing Research Assistant style...")
        response = await client.process_content(query, mock_chunks, PromptStyle.RESEARCH_ASSISTANT)
        print(f"Answer: {response.answer[:200]}...")
        print(f"Sources: {response.sources_used}")
        print(f"Confidence: {response.confidence_score:.3f}")
        print(f"Processing time: {response.processing_time:.2f}s")
        print(f"Token usage: {response.token_usage}")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini_client())