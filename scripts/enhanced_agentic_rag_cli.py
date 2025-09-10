#!/usr/bin/env python3
"""
Enhanced Agentic RAG CLI with Phase 2 Improvements
Integrates advanced chunking, topic detection, smart filtering, and re-ranking
"""

import asyncio
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from topic_detector import TopicDetector
from smart_document_filter import SmartDocumentFilter
from reranker import ReRanker
from advanced_content_processor import AdvancedContentProcessor
from rag_quality_validator import RAGQualityValidator

class EnhancedAgenticRAGCLI:
    def __init__(self, vault_path: str = "D:\\Nomade Milionario"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize all Phase 2 services
        self.topic_detector = TopicDetector()
        self.smart_filter = SmartDocumentFilter(self.topic_detector)
        self.reranker = ReRanker()
        self.content_processor = AdvancedContentProcessor()
        self.quality_validator = RAGQualityValidator()
        
        # Load and process documents with advanced chunking
        self.documents = self._load_and_process_documents()
        
        self.logger.info(f"Enhanced RAG CLI initialized with {len(self.documents)} document chunks")
    
    def _load_and_process_documents(self) -> List[Dict]:
        """Load and process all documents with advanced chunking"""
        documents = []
        
        for file_path in self.vault_path.rglob("*.md"):
            try:
                # Process file with advanced content processor
                chunks = self.content_processor.process_file(str(file_path))
                
                # Add chunks to documents
                for chunk in chunks:
                    documents.append({
                        'id': f"{Path(file_path).stem}_chunk_{chunk['chunk_index']}",
                        'file_path': str(file_path),
                        'content': chunk['content'],
                        'heading': chunk['heading'],
                        'chunk_index': chunk['chunk_index'],
                        'word_count': chunk['word_count'],
                        'token_count': chunk['token_count'],
                        'metadata': chunk['metadata']
                    })
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
        
        self.logger.info(f"Loaded {len(documents)} document chunks with advanced processing")
        return documents
    
    async def search(self, query: str, top_k: int = 5, 
                    filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Enhanced search with intelligent filtering and re-ranking"""
        try:
            start_time = time.time()
            
            # Step 1: Apply smart filtering
            filtered_docs = self.smart_filter.smart_filter(
                self.documents, query, filters or {}
            )
            
            if not filtered_docs:
                self.logger.warning(f"No documents found after filtering for query: {query}")
                return []
            
            # Step 2: Perform basic similarity search (placeholder for now)
            # In a real implementation, this would use vector embeddings
            results = self._basic_similarity_search(query, filtered_docs, top_k * 2)
            
            # Step 3: Apply topic filtering
            topic = self.topic_detector.detect_topic(query)
            if topic != "general":
                results = self.smart_filter.filter_by_topic(results, topic)
            
            # Step 4: Re-rank results for better precision
            results = self.reranker.rerank(query, results, top_k)
            
            # Add search metadata
            search_time = time.time() - start_time
            for result in results:
                result['search_time'] = search_time
                result['search_metadata'] = {
                    'query': query,
                    'topic': topic,
                    'filtered_docs_count': len(filtered_docs),
                    'total_docs_count': len(self.documents)
                }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Enhanced search error: {e}")
            return []
    
    def _basic_similarity_search(self, query: str, documents: List[Dict], top_k: int) -> List[Dict]:
        """Basic similarity search (placeholder for vector search)"""
        query_words = set(query.lower().split())
        
        results = []
        for doc in documents:
            content_words = set(doc['content'].lower().split())
            
            # Calculate basic similarity
            intersection = len(query_words.intersection(content_words))
            union = len(query_words.union(content_words))
            similarity = intersection / union if union > 0 else 0
            
            # Boost for exact phrase matches
            phrase_boost = 0.3 if query.lower() in doc['content'].lower() else 0
            
            # Boost for heading matches
            heading_boost = 0.2 if any(word in doc.get('heading', '').lower() for word in query_words) else 0
            
            total_similarity = similarity + phrase_boost + heading_boost
            
            results.append({
                **doc,
                'similarity': min(total_similarity, 1.0)
            })
        
        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    async def search_with_analysis(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search with detailed analysis and metrics"""
        start_time = time.time()
        
        # Detect topics
        primary_topic = self.topic_detector.detect_topic(query)
        all_topics = self.topic_detector.detect_multiple_topics(query)
        
        # Perform search
        results = await self.search(query, top_k)
        
        # Calculate metrics
        search_time = time.time() - start_time
        
        # Analyze result quality
        if results:
            avg_similarity = sum(r.get('final_score', r.get('similarity', 0)) for r in results) / len(results)
            topic_coverage = len(set(r.get('metadata', {}).get('topic', '') for r in results))
        else:
            avg_similarity = 0
            topic_coverage = 0
        
        # Validate quality
        quality_validation = self.quality_validator.validate_search_quality(query, results)
        
        return {
            'query': query,
            'results': results,
            'analysis': {
                'primary_topic': primary_topic,
                'detected_topics': all_topics,
                'search_time': search_time,
                'result_count': len(results),
                'avg_similarity': avg_similarity,
                'topic_coverage': topic_coverage,
                'quality_score': self._calculate_quality_score(results),
                'quality_validation': quality_validation
            }
        }
    
    def _calculate_quality_score(self, results: List[Dict]) -> float:
        """Calculate overall quality score for results"""
        if not results:
            return 0.0
        
        # Factors: similarity distribution, topic diversity, content length
        similarities = [r.get('final_score', r.get('similarity', 0)) for r in results]
        
        # Similarity quality (prefer 0.3-0.8 range)
        sim_quality = 1.0 - abs(0.55 - (sum(similarities) / len(similarities)))
        
        # Topic diversity
        topics = set(r.get('metadata', {}).get('topic', '') for r in results)
        topic_diversity = min(len(topics) / len(results), 1.0)
        
        # Content quality (prefer medium-length chunks)
        content_lengths = [r.get('word_count', 0) for r in results]
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        length_quality = 1.0 - abs(200 - avg_length) / 200  # Optimal around 200 words
        
        # Overall quality score
        quality_score = (sim_quality * 0.4 + topic_diversity * 0.3 + length_quality * 0.3)
        return min(max(quality_score, 0.0), 1.0)
    
    async def chat(self, query: str) -> str:
        """Enhanced chat interface with improved context"""
        # Search for relevant content
        search_result = await self.search_with_analysis(query, top_k=3)
        results = search_result['results']
        analysis = search_result['analysis']
        
        if not results:
            return "I couldn't find relevant information for your query."
        
        # Build enhanced context
        context = self._build_enhanced_context(query, results, analysis)
        
        # Generate response (placeholder for LLM integration)
        response = self._generate_enhanced_response(query, context, analysis)
        
        return response
    
    def _build_enhanced_context(self, query: str, results: List[Dict], analysis: Dict) -> str:
        """Build enhanced context from search results and analysis"""
        context_parts = []
        
        context_parts.append(f"Query Analysis:")
        context_parts.append(f"  Primary Topic: {analysis['primary_topic']}")
        context_parts.append(f"  Detected Topics: {', '.join(analysis['detected_topics'])}")
        context_parts.append(f"  Quality Score: {analysis['quality_score']:.3f}")
        context_parts.append("")
        
        context_parts.append(f"Search Results ({len(results)} found):")
        for i, result in enumerate(results, 1):
            final_score = result.get('final_score', result.get('similarity', 0))
            rerank_score = result.get('rerank_score', 0)
            
            context_parts.append(f"\nDocument {i} (Final: {final_score:.3f}, Rerank: {rerank_score:.3f}):")
            context_parts.append(f"  File: {result.get('file_path', 'Unknown')}")
            context_parts.append(f"  Heading: {result.get('heading', 'No heading')}")
            context_parts.append(f"  Content: {result['content'][:500]}...")
        
        return "\n".join(context_parts)
    
    def _generate_enhanced_response(self, query: str, context: str, analysis: Dict) -> str:
        """Generate enhanced response based on context and analysis"""
        return f"""
🤖 Enhanced RAG Response

Query: {query}

📊 Analysis:
- Primary Topic: {analysis['primary_topic']}
- Quality Score: {analysis['quality_score']:.3f}
- Search Time: {analysis['search_time']:.3f}s
- Results Found: {analysis['result_count']}

📝 Context:
{context}

[This is where you would integrate with Gemini or another LLM to generate a proper response based on the enhanced context]
"""
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics and health metrics"""
        return {
            "total_documents": len(self.documents),
            "vault_path": str(self.vault_path),
            "services_loaded": {
                "topic_detector": True,
                "smart_filter": True,
                "reranker": True,
                "content_processor": True,
                "quality_validator": True
            },
            "document_stats": {
                "avg_word_count": sum(d.get('word_count', 0) for d in self.documents) / len(self.documents) if self.documents else 0,
                "avg_token_count": sum(d.get('token_count', 0) for d in self.documents) / len(self.documents) if self.documents else 0,
                "unique_headings": len(set(d.get('heading', '') for d in self.documents)),
                "unique_files": len(set(d.get('file_path', '') for d in self.documents))
            }
        }

# Test the enhanced RAG CLI
async def test_enhanced_rag():
    """Test the enhanced RAG system"""
    print("🚀 Testing Enhanced Agentic RAG CLI")
    print("=" * 60)
    
    cli = EnhancedAgenticRAGCLI()
    
    # Test queries
    test_queries = [
        "philosophical currents of logic and mathematics",
        "machine learning algorithms and neural networks",
        "performance optimization techniques",
        "business strategy and management"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 40)
        
        # Search with analysis
        result = await cli.search_with_analysis(query, top_k=3)
        
        print(f"Results: {result['analysis']['result_count']}")
        print(f"Primary Topic: {result['analysis']['primary_topic']}")
        print(f"Quality Score: {result['analysis']['quality_score']:.3f}")
        print(f"Search Time: {result['analysis']['search_time']:.3f}s")
        
        # Show top results
        for i, doc in enumerate(result['results'][:2], 1):
            print(f"  {i}. {doc.get('final_score', 0):.3f} - {doc['content'][:80]}...")
    
    # Show system stats
    stats = cli.get_system_stats()
    print(f"\n📊 System Stats:")
    print(f"  Total Documents: {stats['total_documents']}")
    print(f"  Avg Word Count: {stats['document_stats']['avg_word_count']:.1f}")
    print(f"  Unique Headings: {stats['document_stats']['unique_headings']}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_rag())
