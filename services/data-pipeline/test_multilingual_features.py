#!/usr/bin/env python3
"""
Comprehensive Multilingual Testing Suite
Tests English and Portuguese semantic features with performance validation
"""

import asyncio
import time
import logging
from typing import List, Dict, Any
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from embeddings.embedding_service import EmbeddingService
from search.query_expansion_service import QueryExpansionService, ExpansionStrategy
from vector.chroma_service import ChromaService
from search.search_service import SemanticSearchService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultilingualTester:
    """Comprehensive tester for multilingual semantic features"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.query_expansion_service = QueryExpansionService()
        self.chroma_service = ChromaService()
        self.search_service = SemanticSearchService(
            chroma_service=self.chroma_service,
            embedding_service=self.embedding_service,
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        
        # Test data
        self.english_content = [
            "Python is a powerful programming language for data science and machine learning.",
            "Machine learning algorithms can predict outcomes based on historical data patterns.",
            "Docker containers provide isolated environments for application deployment.",
            "REST APIs enable communication between different software systems.",
            "Database optimization improves query performance and reduces response times.",
            "Version control with Git helps track changes and collaborate on projects.",
            "Cloud computing offers scalable infrastructure for modern applications.",
            "Security best practices protect applications from vulnerabilities and attacks.",
            "Testing frameworks ensure code quality and prevent bugs in production.",
            "Microservices architecture enables scalable and maintainable software systems."
        ]
        
        self.portuguese_content = [
            "Python é uma linguagem de programação poderosa para ciência de dados e machine learning.",
            "Algoritmos de machine learning podem prever resultados baseados em padrões de dados históricos.",
            "Containers Docker fornecem ambientes isolados para deploy de aplicações.",
            "APIs REST permitem comunicação entre diferentes sistemas de software.",
            "Otimização de banco de dados melhora performance de consultas e reduz tempos de resposta.",
            "Controle de versão com Git ajuda a rastrear mudanças e colaborar em projetos.",
            "Computação em nuvem oferece infraestrutura escalável para aplicações modernas.",
            "Melhores práticas de segurança protegem aplicações de vulnerabilidades e ataques.",
            "Frameworks de teste garantem qualidade de código e previnem bugs em produção.",
            "Arquitetura de microserviços permite sistemas de software escaláveis e manuteníveis."
        ]
        
        self.test_queries = {
            'english': [
                "Python programming tips",
                "How to optimize database performance",
                "Machine learning examples",
                "Docker container setup",
                "REST API security best practices"
            ],
            'portuguese': [
                "Dicas de programação Python",
                "Como otimizar performance do banco de dados",
                "Exemplos de machine learning",
                "Configuração de container Docker",
                "Melhores práticas de segurança para API REST"
            ],
            'cross_lingual': [
                "Python dicas",  # Mixed EN/PT
                "machine learning exemplos",  # Mixed EN/PT
                "Docker setup",  # Mixed EN/PT
                "API segurança",  # Mixed EN/PT
                "database otimização"  # Mixed EN/PT
            ]
        }

    async def test_language_detection(self) -> Dict[str, Any]:
        """Test language detection accuracy"""
        logger.info("🔍 Testing Language Detection...")
        
        results = {
            'english_detection': [],
            'portuguese_detection': [],
            'mixed_detection': [],
            'accuracy': {}
        }
        
        # Test English detection
        for text in self.english_content:
            detected = self.embedding_service.detect_language(text)
            results['english_detection'].append({
                'text': text[:50] + "...",
                'detected': detected,
                'correct': detected == 'en'
            })
        
        # Test Portuguese detection
        for text in self.portuguese_content:
            detected = self.embedding_service.detect_language(text)
            results['portuguese_detection'].append({
                'text': text[:50] + "...",
                'detected': detected,
                'correct': detected == 'pt'
            })
        
        # Test mixed queries
        for query in self.test_queries['cross_lingual']:
            detected = self.query_expansion_service.detect_language(query)
            results['mixed_detection'].append({
                'query': query,
                'detected': detected
            })
        
        # Calculate accuracy
        en_correct = sum(1 for r in results['english_detection'] if r['correct'])
        pt_correct = sum(1 for r in results['portuguese_detection'] if r['correct'])
        
        results['accuracy'] = {
            'english': en_correct / len(results['english_detection']),
            'portuguese': pt_correct / len(results['portuguese_detection']),
            'overall': (en_correct + pt_correct) / (len(results['english_detection']) + len(results['portuguese_detection']))
        }
        
        logger.info(f"✅ Language Detection Results:")
        logger.info(f"   English Accuracy: {results['accuracy']['english']:.2%}")
        logger.info(f"   Portuguese Accuracy: {results['accuracy']['portuguese']:.2%}")
        logger.info(f"   Overall Accuracy: {results['accuracy']['overall']:.2%}")
        
        return results

    async def test_multilingual_embeddings(self) -> Dict[str, Any]:
        """Test multilingual embedding quality and cross-lingual similarity"""
        logger.info("🧠 Testing Multilingual Embeddings...")
        
        results = {
            'embedding_info': self.embedding_service.get_multilingual_info(),
            'similarity_tests': [],
            'cross_lingual_similarity': []
        }
        
        # Generate embeddings for all content
        all_texts = self.english_content + self.portuguese_content
        embeddings = self.embedding_service.batch_generate_embeddings(all_texts)
        
        # Test within-language similarity
        en_embeddings = embeddings[:len(self.english_content)]
        pt_embeddings = embeddings[len(self.english_content):]
        
        # Calculate average similarity within English
        en_similarities = []
        for i in range(len(en_embeddings)):
            for j in range(i + 1, len(en_embeddings)):
                similarity = self._cosine_similarity(en_embeddings[i], en_embeddings[j])
                en_similarities.append(similarity)
        
        # Calculate average similarity within Portuguese
        pt_similarities = []
        for i in range(len(pt_embeddings)):
            for j in range(i + 1, len(pt_embeddings)):
                similarity = self._cosine_similarity(pt_embeddings[i], pt_embeddings[j])
                pt_similarities.append(similarity)
        
        # Test cross-lingual similarity (same concepts, different languages)
        cross_lingual_similarities = []
        for i in range(len(self.english_content)):
            similarity = self._cosine_similarity(en_embeddings[i], pt_embeddings[i])
            cross_lingual_similarities.append({
                'english': self.english_content[i][:50] + "...",
                'portuguese': self.portuguese_content[i][:50] + "...",
                'similarity': similarity
            })
        
        results['similarity_tests'] = {
            'english_avg_similarity': sum(en_similarities) / len(en_similarities) if en_similarities else 0,
            'portuguese_avg_similarity': sum(pt_similarities) / len(pt_similarities) if pt_similarities else 0,
            'cross_lingual_avg_similarity': sum(s['similarity'] for s in cross_lingual_similarities) / len(cross_lingual_similarities)
        }
        
        results['cross_lingual_similarity'] = cross_lingual_similarities
        
        logger.info(f"✅ Multilingual Embedding Results:")
        logger.info(f"   Model: {results['embedding_info']['model_name']}")
        logger.info(f"   Multilingual: {results['embedding_info']['is_multilingual']}")
        logger.info(f"   English Avg Similarity: {results['similarity_tests']['english_avg_similarity']:.3f}")
        logger.info(f"   Portuguese Avg Similarity: {results['similarity_tests']['portuguese_avg_similarity']:.3f}")
        logger.info(f"   Cross-lingual Avg Similarity: {results['similarity_tests']['cross_lingual_avg_similarity']:.3f}")
        
        return results

    async def test_query_expansion_multilingual(self) -> Dict[str, Any]:
        """Test query expansion for both languages"""
        logger.info("🔍 Testing Multilingual Query Expansion...")
        
        results = {
            'english_expansions': [],
            'portuguese_expansions': [],
            'mixed_expansions': [],
            'performance_metrics': {}
        }
        
        start_time = time.time()
        
        # Test English query expansion
        for query in self.test_queries['english']:
            analysis = await self.query_expansion_service.expand_query(query, ExpansionStrategy.RULE_BASED)
            results['english_expansions'].append({
                'original': query,
                'expanded': analysis.expanded_query,
                'intent': analysis.intent,
                'entities': analysis.entities,
                'confidence': analysis.expansion_confidence,
                'language': self.query_expansion_service.detect_language(query)
            })
        
        # Test Portuguese query expansion
        for query in self.test_queries['portuguese']:
            analysis = await self.query_expansion_service.expand_query(query, ExpansionStrategy.RULE_BASED)
            results['portuguese_expansions'].append({
                'original': query,
                'expanded': analysis.expanded_query,
                'intent': analysis.intent,
                'entities': analysis.entities,
                'confidence': analysis.expansion_confidence,
                'language': self.query_expansion_service.detect_language(query)
            })
        
        # Test mixed language queries
        for query in self.test_queries['cross_lingual']:
            analysis = await self.query_expansion_service.expand_query(query, ExpansionStrategy.RULE_BASED)
            results['mixed_expansions'].append({
                'original': query,
                'expanded': analysis.expanded_query,
                'intent': analysis.intent,
                'entities': analysis.entities,
                'confidence': analysis.expansion_confidence,
                'language': self.query_expansion_service.detect_language(query)
            })
        
        end_time = time.time()
        
        results['performance_metrics'] = {
            'total_queries': len(self.test_queries['english']) + len(self.test_queries['portuguese']) + len(self.test_queries['cross_lingual']),
            'total_time': end_time - start_time,
            'avg_time_per_query': (end_time - start_time) / (len(self.test_queries['english']) + len(self.test_queries['portuguese']) + len(self.test_queries['cross_lingual'])),
            'avg_confidence': {
                'english': sum(r['confidence'] for r in results['english_expansions']) / len(results['english_expansions']),
                'portuguese': sum(r['confidence'] for r in results['portuguese_expansions']) / len(results['portuguese_expansions']),
                'mixed': sum(r['confidence'] for r in results['mixed_expansions']) / len(results['mixed_expansions'])
            }
        }
        
        logger.info(f"✅ Query Expansion Results:")
        logger.info(f"   Total Queries: {results['performance_metrics']['total_queries']}")
        logger.info(f"   Total Time: {results['performance_metrics']['total_time']:.3f}s")
        logger.info(f"   Avg Time per Query: {results['performance_metrics']['avg_time_per_query']:.3f}s")
        logger.info(f"   Avg Confidence - English: {results['performance_metrics']['avg_confidence']['english']:.3f}")
        logger.info(f"   Avg Confidence - Portuguese: {results['performance_metrics']['avg_confidence']['portuguese']:.3f}")
        logger.info(f"   Avg Confidence - Mixed: {results['performance_metrics']['avg_confidence']['mixed']:.3f}")
        
        return results

    async def test_cross_lingual_search(self) -> Dict[str, Any]:
        """Test cross-lingual search capabilities"""
        logger.info("🔍 Testing Cross-lingual Search...")
        
        # First, ingest some test data
        await self._ingest_test_data()
        
        results = {
            'english_search_results': [],
            'portuguese_search_results': [],
            'cross_lingual_results': [],
            'search_performance': {}
        }
        
        start_time = time.time()
        
        # Test English queries finding Portuguese content
        for query in self.test_queries['english']:
            search_results = await self.search_service.search_similar(query, n_results=3, expand_query=True)
            results['english_search_results'].append({
                'query': query,
                'results_count': len(search_results),
                'top_result': search_results[0] if search_results else None,
                'avg_similarity': sum(r.get('similarity', 0) for r in search_results) / len(search_results) if search_results else 0
            })
        
        # Test Portuguese queries finding English content
        for query in self.test_queries['portuguese']:
            search_results = await self.search_service.search_similar(query, n_results=3, expand_query=True)
            results['portuguese_search_results'].append({
                'query': query,
                'results_count': len(search_results),
                'top_result': search_results[0] if search_results else None,
                'avg_similarity': sum(r.get('similarity', 0) for r in search_results) / len(search_results) if search_results else 0
            })
        
        # Test mixed language queries
        for query in self.test_queries['cross_lingual']:
            search_results = await self.search_service.search_similar(query, n_results=3, expand_query=True)
            results['cross_lingual_results'].append({
                'query': query,
                'results_count': len(search_results),
                'top_result': search_results[0] if search_results else None,
                'avg_similarity': sum(r.get('similarity', 0) for r in search_results) / len(search_results) if search_results else 0
            })
        
        end_time = time.time()
        
        results['search_performance'] = {
            'total_searches': len(self.test_queries['english']) + len(self.test_queries['portuguese']) + len(self.test_queries['cross_lingual']),
            'total_time': end_time - start_time,
            'avg_time_per_search': (end_time - start_time) / (len(self.test_queries['english']) + len(self.test_queries['portuguese']) + len(self.test_queries['cross_lingual'])),
            'avg_results_per_query': {
                'english': sum(r['results_count'] for r in results['english_search_results']) / len(results['english_search_results']),
                'portuguese': sum(r['results_count'] for r in results['portuguese_search_results']) / len(results['portuguese_search_results']),
                'mixed': sum(r['results_count'] for r in results['cross_lingual_results']) / len(results['cross_lingual_results'])
            },
            'avg_similarity': {
                'english': sum(r['avg_similarity'] for r in results['english_search_results']) / len(results['english_search_results']),
                'portuguese': sum(r['avg_similarity'] for r in results['portuguese_search_results']) / len(results['portuguese_search_results']),
                'mixed': sum(r['avg_similarity'] for r in results['cross_lingual_results']) / len(results['cross_lingual_results'])
            }
        }
        
        logger.info(f"✅ Cross-lingual Search Results:")
        logger.info(f"   Total Searches: {results['search_performance']['total_searches']}")
        logger.info(f"   Total Time: {results['search_performance']['total_time']:.3f}s")
        logger.info(f"   Avg Time per Search: {results['search_performance']['avg_time_per_search']:.3f}s")
        logger.info(f"   Avg Results per Query - English: {results['search_performance']['avg_results_per_query']['english']:.1f}")
        logger.info(f"   Avg Results per Query - Portuguese: {results['search_performance']['avg_results_per_query']['portuguese']:.1f}")
        logger.info(f"   Avg Results per Query - Mixed: {results['search_performance']['avg_results_per_query']['mixed']:.1f}")
        logger.info(f"   Avg Similarity - English: {results['search_performance']['avg_similarity']['english']:.3f}")
        logger.info(f"   Avg Similarity - Portuguese: {results['search_performance']['avg_similarity']['portuguese']:.3f}")
        logger.info(f"   Avg Similarity - Mixed: {results['search_performance']['avg_similarity']['mixed']:.3f}")
        
        return results

    async def _ingest_test_data(self):
        """Ingest test data for search testing"""
        logger.info("📥 Ingesting test data for search testing...")
        
        # Create test chunks
        chunks = []
        for i, (en_text, pt_text) in enumerate(zip(self.english_content, self.portuguese_content)):
            # English chunk
            chunks.append({
                'content': en_text,
                'path': f'test_en_{i}.txt',
                'heading': 'Test Content',
                'chunk_index': i,
                'chunk_token_count': len(en_text.split()),
                'chunk_word_count': len(en_text.split()),
                'chunk_char_count': len(en_text),
                'file_word_count': len(en_text.split()),
                'file_char_count': len(en_text),
                'file_size': len(en_text.encode('utf-8')),
                'file_modified': int(time.time()),
                'file_created': int(time.time()),
                'frontmatter_tags': [],
                'content_tags': ['technical', 'english'],
                'has_frontmatter': False,
                'frontmatter_keys': [],
                'file_type': 'txt',
                'path_year': '2025',
                'path_month': '09',
                'path_category': 'test',
                'path_subcategory': 'multilingual',
                'content_type': 'technical',
                'links': []
            })
            
            # Portuguese chunk
            chunks.append({
                'content': pt_text,
                'path': f'test_pt_{i}.txt',
                'heading': 'Conteúdo de Teste',
                'chunk_index': i,
                'chunk_token_count': len(pt_text.split()),
                'chunk_word_count': len(pt_text.split()),
                'chunk_char_count': len(pt_text),
                'file_word_count': len(pt_text.split()),
                'file_char_count': len(pt_text),
                'file_size': len(pt_text.encode('utf-8')),
                'file_modified': int(time.time()),
                'file_created': int(time.time()),
                'frontmatter_tags': [],
                'content_tags': ['technical', 'portuguese'],
                'has_frontmatter': False,
                'frontmatter_keys': [],
                'file_type': 'txt',
                'path_year': '2025',
                'path_month': '09',
                'path_category': 'test',
                'path_subcategory': 'multilingual',
                'content_type': 'technical',
                'links': []
            })
        
        # Generate embeddings and store
        contents = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_service.batch_generate_embeddings(contents)
        
        # Store in ChromaDB
        self.chroma_service.store_embeddings(
            chunks=chunks,
            embeddings=embeddings
        )
        
        logger.info(f"✅ Ingested {len(chunks)} test chunks")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all multilingual tests and generate comprehensive report"""
        logger.info("🚀 Starting Comprehensive Multilingual Testing...")
        
        results = {
            'test_timestamp': time.time(),
            'language_detection': await self.test_language_detection(),
            'multilingual_embeddings': await self.test_multilingual_embeddings(),
            'query_expansion': await self.test_query_expansion_multilingual(),
            'cross_lingual_search': await self.test_cross_lingual_search()
        }
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        logger.info("🎉 Comprehensive Multilingual Testing Complete!")
        logger.info(f"📊 Summary: {results['summary']}")
        
        return results

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of all test results"""
        return {
            'language_detection_accuracy': results['language_detection']['accuracy']['overall'],
            'multilingual_model': results['multilingual_embeddings']['embedding_info']['is_multilingual'],
            'cross_lingual_similarity': results['multilingual_embeddings']['similarity_tests']['cross_lingual_avg_similarity'],
            'query_expansion_performance': results['query_expansion']['performance_metrics']['avg_time_per_query'],
            'search_performance': results['cross_lingual_search']['search_performance']['avg_time_per_search'],
            'overall_multilingual_capability': 'EXCELLENT' if results['language_detection']['accuracy']['overall'] > 0.8 and results['multilingual_embeddings']['embedding_info']['is_multilingual'] else 'GOOD'
        }

async def main():
    """Main test execution"""
    tester = MultilingualTester()
    results = await tester.run_comprehensive_test()
    
    # Print detailed results
    print("\n" + "="*80)
    print("🎯 MULTILINGUAL SEMANTIC FEATURES - COMPREHENSIVE TEST RESULTS")
    print("="*80)
    
    print(f"\n📊 LANGUAGE DETECTION:")
    print(f"   English Accuracy: {results['language_detection']['accuracy']['english']:.2%}")
    print(f"   Portuguese Accuracy: {results['language_detection']['accuracy']['portuguese']:.2%}")
    print(f"   Overall Accuracy: {results['language_detection']['accuracy']['overall']:.2%}")
    
    print(f"\n🧠 MULTILINGUAL EMBEDDINGS:")
    print(f"   Model: {results['multilingual_embeddings']['embedding_info']['model_name']}")
    print(f"   Multilingual: {results['multilingual_embeddings']['embedding_info']['is_multilingual']}")
    print(f"   Cross-lingual Similarity: {results['multilingual_embeddings']['similarity_tests']['cross_lingual_avg_similarity']:.3f}")
    
    print(f"\n🔍 QUERY EXPANSION:")
    print(f"   Avg Time per Query: {results['query_expansion']['performance_metrics']['avg_time_per_query']:.3f}s")
    print(f"   English Confidence: {results['query_expansion']['performance_metrics']['avg_confidence']['english']:.3f}")
    print(f"   Portuguese Confidence: {results['query_expansion']['performance_metrics']['avg_confidence']['portuguese']:.3f}")
    
    print(f"\n🔍 CROSS-LINGUAL SEARCH:")
    print(f"   Avg Time per Search: {results['cross_lingual_search']['search_performance']['avg_time_per_search']:.3f}s")
    print(f"   English Avg Similarity: {results['cross_lingual_search']['search_performance']['avg_similarity']['english']:.3f}")
    print(f"   Portuguese Avg Similarity: {results['cross_lingual_search']['search_performance']['avg_similarity']['portuguese']:.3f}")
    print(f"   Mixed Avg Similarity: {results['cross_lingual_search']['search_performance']['avg_similarity']['mixed']:.3f}")
    
    print(f"\n🎯 OVERALL SUMMARY:")
    print(f"   Multilingual Capability: {results['summary']['overall_multilingual_capability']}")
    print(f"   Language Detection: {results['summary']['language_detection_accuracy']:.2%}")
    print(f"   Cross-lingual Similarity: {results['summary']['cross_lingual_similarity']:.3f}")
    
    print("\n" + "="*80)
    print("✅ MULTILINGUAL TESTING COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
