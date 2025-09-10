#!/usr/bin/env python3
"""
Advanced Performance & Quality Improvements
Based on initial planning documents from agentic_RAG_cli.md and 02_agentic_RAG_cli.md
"""

import sys
import os
import json
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from datetime import datetime
import logging

# Add data-pipeline services to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

print("🚀 Advanced Performance & Quality Improvements")
print("=" * 60)

try:
    from embeddings.embedding_service import EmbeddingService
    from vector.chroma_service import ChromaService
    from search.semantic_search_service import SemanticSearchService
    from processing.content_processor import ContentProcessor
    from search.reranker import ReRanker
    from search.topic_detector import TopicDetector
    from search.smart_document_filter import SmartDocumentFilter
    from processing.advanced_content_processor import AdvancedContentProcessor
    print("✅ All services imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Advanced Performance Improvements Implementation
class AdvancedPerformanceImprovements:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService()
        self.search_service = SemanticSearchService(self.chroma_service, self.embedding_service)
        self.content_processor = ContentProcessor()
        self.reranker = ReRanker()
        self.topic_detector = TopicDetector()
        self.smart_filter = SmartDocumentFilter()
        self.advanced_processor = AdvancedContentProcessor()
        
        # Performance metrics
        self.performance_metrics = {
            "query_count": 0,
            "total_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "embedding_generation_time": 0.0,
            "search_time": 0.0,
            "reranking_time": 0.0
        }
        
        # Quality metrics
        self.quality_metrics = {
            "precision_scores": [],
            "mrr_scores": [],
            "ndcg_scores": [],
            "user_satisfaction": [],
            "response_relevance": []
        }
        
        # Query expansion cache
        self.query_expansion_cache = {}
        
        # Response quality cache
        self.response_quality_cache = {}
        
        print("✅ Advanced Performance Improvements initialized")

    # 1. Query Expansion Implementation
    def expand_query(self, query: str) -> List[str]:
        """Implement query expansion based on initial planning"""
        if query in self.query_expansion_cache:
            return self.query_expansion_cache[query]
        
        # Basic query expansion techniques
        expanded_queries = [query]
        
        # Add synonyms for key terms
        synonyms = {
            "philosophy": ["philosophical", "philosophical currents", "philosophical schools"],
            "mathematics": ["mathematical", "math", "mathematical concepts"],
            "logic": ["logical", "logical reasoning", "logical systems"],
            "programming": ["coding", "software development", "programming languages"],
            "scraping": ["web scraping", "data extraction", "web crawling"],
            "reading": ["reading techniques", "reading methods", "comprehension"]
        }
        
        query_lower = query.lower()
        for term, syns in synonyms.items():
            if term in query_lower:
                for syn in syns:
                    expanded_query = query_lower.replace(term, syn)
                    if expanded_query not in expanded_queries:
                        expanded_queries.append(expanded_query)
        
        # Add question variations
        if query.endswith('?'):
            base_query = query[:-1]
            variations = [
                f"What is {base_query.lower()}?",
                f"How does {base_query.lower()} work?",
                f"Explain {base_query.lower()}",
                f"Tell me about {base_query.lower()}"
            ]
            expanded_queries.extend(variations)
        
        self.query_expansion_cache[query] = expanded_queries
        return expanded_queries

    # 2. Query Classification Implementation
    def classify_query(self, query: str) -> Dict[str, Any]:
        """Classify query type and intent based on initial planning"""
        query_lower = query.lower()
        
        # Query type classification
        query_types = {
            "philosophy": ["philosophy", "philosophical", "logic", "mathematics", "mathematical"],
            "technology": ["programming", "code", "software", "python", "scrapy", "web"],
            "reading": ["reading", "comprehension", "techniques", "methods", "pqlp"],
            "general": ["what", "how", "explain", "tell me", "describe"]
        }
        
        detected_type = "general"
        confidence = 0.0
        
        for qtype, keywords in query_types.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            if matches > 0:
                type_confidence = matches / len(keywords)
                if type_confidence > confidence:
                    confidence = type_confidence
                    detected_type = qtype
        
        # Intent classification
        intents = {
            "definition": ["what is", "define", "definition"],
            "explanation": ["how", "explain", "tell me about"],
            "comparison": ["compare", "difference", "versus", "vs"],
            "procedure": ["how to", "steps", "process", "method"]
        }
        
        detected_intent = "explanation"
        intent_confidence = 0.0
        
        for intent, keywords in intents.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            if matches > 0:
                intent_confidence = matches / len(keywords)
                if intent_confidence > intent_confidence:
                    intent_confidence = intent_confidence
                    detected_intent = intent
        
        return {
            "type": detected_type,
            "intent": detected_intent,
            "confidence": confidence,
            "intent_confidence": intent_confidence
        }

    # 3. Intent Recognition Implementation
    def recognize_intent(self, query: str) -> Dict[str, Any]:
        """Recognize user intent for more targeted retrieval"""
        classification = self.classify_query(query)
        
        # Intent-based query modification
        intent_modifications = {
            "definition": {
                "boost_terms": ["definition", "meaning", "concept"],
                "filter_topics": ["concepts", "definitions", "basics"]
            },
            "explanation": {
                "boost_terms": ["explanation", "how", "why", "process"],
                "filter_topics": ["explanations", "tutorials", "guides"]
            },
            "comparison": {
                "boost_terms": ["compare", "difference", "versus", "vs"],
                "filter_topics": ["comparisons", "analysis", "evaluation"]
            },
            "procedure": {
                "boost_terms": ["steps", "process", "method", "procedure"],
                "filter_topics": ["tutorials", "guides", "procedures"]
            }
        }
        
        intent = classification["intent"]
        modifications = intent_modifications.get(intent, intent_modifications["explanation"])
        
        return {
            "intent": intent,
            "boost_terms": modifications["boost_terms"],
            "filter_topics": modifications["filter_topics"],
            "confidence": classification["intent_confidence"]
        }

    # 4. Query-focused Summarization Implementation
    def generate_query_focused_summary(self, query: str, documents: List[Dict]) -> str:
        """Generate query-focused summary based on initial planning"""
        # Extract key terms from query
        query_terms = set(query.lower().split())
        
        # Score documents by query term relevance
        scored_docs = []
        for doc in documents:
            content = doc.get('content', '').lower()
            term_matches = sum(1 for term in query_terms if term in content)
            relevance_score = term_matches / len(query_terms) if query_terms else 0
            
            scored_docs.append({
                **doc,
                'relevance_score': relevance_score
            })
        
        # Sort by relevance
        scored_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Generate focused summary
        summary_parts = []
        for doc in scored_docs[:3]:  # Top 3 most relevant
            content = doc.get('content', '')
            # Extract sentences containing query terms
            sentences = content.split('.')
            relevant_sentences = [
                sent.strip() for sent in sentences 
                if any(term in sent.lower() for term in query_terms)
            ]
            
            if relevant_sentences:
                summary_parts.append(f"**{doc.get('filename', 'Unknown')}**: {' '.join(relevant_sentences[:2])}")
        
        return '\n\n'.join(summary_parts)

    # 5. Multi-hop Retrieval Implementation
    def multi_hop_retrieval(self, query: str, initial_results: List[Dict]) -> List[Dict]:
        """Implement multi-hop retrieval for complex questions"""
        # Extract entities and concepts from initial results
        entities = set()
        concepts = set()
        
        for result in initial_results:
            content = result.get('content', '')
            # Simple entity extraction (in practice, use NER)
            words = content.split()
            for word in words:
                if word.isupper() and len(word) > 2:
                    entities.add(word)
                if word.endswith('ism') or word.endswith('ology'):
                    concepts.add(word)
        
        # Generate follow-up queries
        follow_up_queries = []
        for entity in list(entities)[:3]:
            follow_up_queries.append(f"What is {entity}?")
        for concept in list(concepts)[:3]:
            follow_up_queries.append(f"Explain {concept}")
        
        # Search for additional relevant documents
        additional_results = []
        for follow_up_query in follow_up_queries:
            results = self.search_service.search(follow_up_query, [], top_k=3)
            additional_results.extend(results)
        
        # Combine and deduplicate results
        all_results = initial_results + additional_results
        seen_ids = set()
        unique_results = []
        
        for result in all_results:
            result_id = result.get('id', result.get('filename', ''))
            if result_id not in seen_ids:
                seen_ids.add(result_id)
                unique_results.append(result)
        
        return unique_results

    # 6. User Feedback Loop Implementation
    def process_user_feedback(self, query: str, response: str, feedback: str, retrieved_docs: List[Dict]):
        """Process user feedback for continuous improvement"""
        feedback_data = {
            "query": query,
            "response": response,
            "feedback": feedback,
            "retrieved_docs": [doc.get('filename', '') for doc in retrieved_docs],
            "timestamp": datetime.now().isoformat()
        }
        
        # Store feedback for analysis
        feedback_file = "user_feedback_log.json"
        try:
            if os.path.exists(feedback_file):
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedback_log = json.load(f)
            else:
                feedback_log = []
            
            feedback_log.append(feedback_data)
            
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_log, f, indent=2, ensure_ascii=False)
            
            print(f"✅ User feedback logged: {feedback}")
            
        except Exception as e:
            print(f"⚠️ Error logging feedback: {e}")

    # 7. Advanced Quality Metrics Implementation
    def calculate_advanced_quality_metrics(self, query: str, results: List[Dict], response: str) -> Dict[str, float]:
        """Calculate advanced quality metrics based on initial planning"""
        # Basic quality metrics
        precision_at_5 = self.calculate_precision_at_k(results, query, 5)
        mrr = self.calculate_mrr(results, query)
        ndcg_at_5 = self.calculate_ndcg_at_k(results, query, 5)
        
        # Response quality metrics
        response_relevance = self.calculate_response_relevance(query, response)
        response_completeness = self.calculate_response_completeness(query, response, results)
        response_coherence = self.calculate_response_coherence(response)
        
        # Citation quality
        citation_quality = self.calculate_citation_quality(response, results)
        
        # Overall quality score
        overall_quality = (
            0.2 * precision_at_5 +
            0.2 * mrr +
            0.2 * ndcg_at_5 +
            0.2 * response_relevance +
            0.1 * response_completeness +
            0.05 * response_coherence +
            0.05 * citation_quality
        )
        
        return {
            "precision_at_5": precision_at_5,
            "mrr": mrr,
            "ndcg_at_5": ndcg_at_5,
            "response_relevance": response_relevance,
            "response_completeness": response_completeness,
            "response_coherence": response_coherence,
            "citation_quality": citation_quality,
            "overall_quality": overall_quality
        }

    def calculate_precision_at_k(self, results: List[Dict], query: str, k: int) -> float:
        """Calculate Precision@K"""
        if not results:
            return 0.0
        
        top_k_results = results[:k]
        query_terms = set(query.lower().split())
        
        relevant_count = 0
        for result in top_k_results:
            content = result.get('content', '').lower()
            if any(term in content for term in query_terms):
                relevant_count += 1
        
        return relevant_count / len(top_k_results)

    def calculate_mrr(self, results: List[Dict], query: str) -> float:
        """Calculate Mean Reciprocal Rank"""
        query_terms = set(query.lower().split())
        
        for i, result in enumerate(results, 1):
            content = result.get('content', '').lower()
            if any(term in content for term in query_terms):
                return 1.0 / i
        
        return 0.0

    def calculate_ndcg_at_k(self, results: List[Dict], query: str, k: int) -> float:
        """Calculate NDCG@K"""
        query_terms = set(query.lower().split())
        
        # Calculate DCG
        dcg = 0.0
        for i, result in enumerate(results[:k], 1):
            content = result.get('content', '').lower()
            relevance = 1 if any(term in content for term in query_terms) else 0
            dcg += relevance / np.log2(i + 1)
        
        # Calculate IDCG (ideal DCG)
        idcg = sum(1 / np.log2(i + 1) for i in range(1, min(len(query_terms), k) + 1))
        
        return dcg / idcg if idcg > 0 else 0.0

    def calculate_response_relevance(self, query: str, response: str) -> float:
        """Calculate response relevance to query"""
        query_terms = set(query.lower().split())
        response_terms = set(response.lower().split())
        
        overlap = len(query_terms.intersection(response_terms))
        return overlap / len(query_terms) if query_terms else 0.0

    def calculate_response_completeness(self, query: str, response: str, results: List[Dict]) -> float:
        """Calculate response completeness based on retrieved documents"""
        if not results:
            return 0.0
        
        # Extract key concepts from retrieved documents
        all_content = ' '.join([doc.get('content', '') for doc in results])
        content_terms = set(all_content.lower().split())
        
        # Check how many key concepts are covered in response
        response_terms = set(response.lower().split())
        covered_concepts = len(content_terms.intersection(response_terms))
        
        return min(1.0, covered_concepts / len(content_terms)) if content_terms else 0.0

    def calculate_response_coherence(self, response: str) -> float:
        """Calculate response coherence"""
        # Simple coherence metric based on sentence structure
        sentences = response.split('.')
        if len(sentences) < 2:
            return 0.5
        
        # Check for transition words and logical flow
        transition_words = ['however', 'therefore', 'furthermore', 'additionally', 'moreover', 'consequently']
        transition_count = sum(1 for word in transition_words if word in response.lower())
        
        # Check for proper sentence structure
        proper_sentences = sum(1 for sent in sentences if len(sent.split()) > 3)
        
        coherence_score = (transition_count * 0.3 + proper_sentences / len(sentences) * 0.7)
        return min(1.0, coherence_score)

    def calculate_citation_quality(self, response: str, results: List[Dict]) -> float:
        """Calculate citation quality in response"""
        if not results:
            return 0.0
        
        # Check if response mentions source documents
        source_mentions = 0
        for result in results:
            filename = result.get('filename', '')
            if filename and filename.lower() in response.lower():
                source_mentions += 1
        
        return source_mentions / len(results) if results else 0.0

    # 8. Performance Monitoring Implementation
    def monitor_performance(self, operation: str, duration: float, success: bool = True):
        """Monitor system performance"""
        self.performance_metrics["query_count"] += 1
        self.performance_metrics["total_response_time"] += duration
        
        if operation == "embedding":
            self.performance_metrics["embedding_generation_time"] += duration
        elif operation == "search":
            self.performance_metrics["search_time"] += duration
        elif operation == "reranking":
            self.performance_metrics["reranking_time"] += duration
        
        if success:
            self.performance_metrics["cache_hits"] += 1
        else:
            self.performance_metrics["cache_misses"] += 1

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        total_queries = self.performance_metrics["query_count"]
        if total_queries == 0:
            return {"status": "No queries processed"}
        
        avg_response_time = self.performance_metrics["total_response_time"] / total_queries
        cache_hit_rate = self.performance_metrics["cache_hits"] / total_queries
        
        return {
            "total_queries": total_queries,
            "avg_response_time": avg_response_time,
            "cache_hit_rate": cache_hit_rate,
            "embedding_time": self.performance_metrics["embedding_generation_time"],
            "search_time": self.performance_metrics["search_time"],
            "reranking_time": self.performance_metrics["reranking_time"]
        }

    # 9. Advanced Search with All Improvements
    def advanced_search(self, query: str, vault_content: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced search with all improvements"""
        start_time = time.time()
        
        # 1. Query expansion
        expanded_queries = self.expand_query(query)
        
        # 2. Query classification
        classification = self.classify_query(query)
        
        # 3. Intent recognition
        intent = self.recognize_intent(query)
        
        # 4. Topic detection and filtering
        topic = self.topic_detector.detect_topic(query)
        filtered_docs = [
            doc for doc in vault_content.values()
            if topic in doc.get('topics', [])
        ]
        
        # 5. Semantic search
        search_start = time.time()
        results = self.search_service.search(query, filtered_docs, top_k=10)
        search_time = time.time() - search_start
        self.monitor_performance("search", search_time)
        
        # 6. Re-ranking
        if results:
            rerank_start = time.time()
            results = self.reranker.rerank(query, results)
            rerank_time = time.time() - rerank_start
            self.monitor_performance("reranking", rerank_time)
        
        # 7. Multi-hop retrieval for complex queries
        if classification["intent"] in ["comparison", "procedure"]:
            results = self.multi_hop_retrieval(query, results)
        
        # 8. Query-focused summarization
        summary = self.generate_query_focused_summary(query, results[:5])
        
        total_time = time.time() - start_time
        
        return {
            "query": query,
            "expanded_queries": expanded_queries,
            "classification": classification,
            "intent": intent,
            "topic": topic,
            "results": results[:5],
            "summary": summary,
            "search_time": search_time,
            "total_time": total_time,
            "results_count": len(results)
        }

# Test the advanced improvements
def test_advanced_improvements():
    """Test all advanced performance improvements"""
    print("\n🧪 Testing Advanced Performance Improvements")
    print("-" * 50)
    
    improvements = AdvancedPerformanceImprovements()
    
    # Test query expansion
    print("\n1. Testing Query Expansion:")
    test_query = "What are the main philosophical currents of logic and mathematics?"
    expanded = improvements.expand_query(test_query)
    print(f"Original: {test_query}")
    print(f"Expanded: {expanded[:3]}...")  # Show first 3 expansions
    
    # Test query classification
    print("\n2. Testing Query Classification:")
    classification = improvements.classify_query(test_query)
    print(f"Type: {classification['type']}")
    print(f"Intent: {classification['intent']}")
    print(f"Confidence: {classification['confidence']:.3f}")
    
    # Test intent recognition
    print("\n3. Testing Intent Recognition:")
    intent = improvements.recognize_intent(test_query)
    print(f"Intent: {intent['intent']}")
    print(f"Boost Terms: {intent['boost_terms']}")
    print(f"Filter Topics: {intent['filter_topics']}")
    
    # Test quality metrics calculation
    print("\n4. Testing Quality Metrics:")
    mock_results = [
        {"content": "Philosophy of mathematics examines the nature of mathematical objects", "filename": "philosophy.md"},
        {"content": "Logic is the study of reasoning and argumentation", "filename": "logic.md"}
    ]
    mock_response = "The main philosophical currents include Platonism, Formalism, and Intuitionism in mathematics and logic."
    
    quality_metrics = improvements.calculate_advanced_quality_metrics(test_query, mock_results, mock_response)
    print(f"Precision@5: {quality_metrics['precision_at_5']:.3f}")
    print(f"MRR: {quality_metrics['mrr']:.3f}")
    print(f"NDCG@5: {quality_metrics['ndcg_at_5']:.3f}")
    print(f"Response Relevance: {quality_metrics['response_relevance']:.3f}")
    print(f"Overall Quality: {quality_metrics['overall_quality']:.3f}")
    
    # Test performance monitoring
    print("\n5. Testing Performance Monitoring:")
    improvements.monitor_performance("search", 0.065, True)
    improvements.monitor_performance("reranking", 0.020, True)
    improvements.monitor_performance("embedding", 0.045, True)
    
    performance_summary = improvements.get_performance_summary()
    print(f"Total Queries: {performance_summary['total_queries']}")
    print(f"Avg Response Time: {performance_summary['avg_response_time']:.3f}s")
    print(f"Cache Hit Rate: {performance_summary['cache_hit_rate']:.3f}")
    
    print("\n✅ Advanced Performance Improvements Test Complete!")
    
    return improvements

if __name__ == "__main__":
    test_advanced_improvements()
