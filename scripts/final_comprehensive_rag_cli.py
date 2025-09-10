#!/usr/bin/env python3
"""
Final Comprehensive RAG CLI - Complete Integration of All Phase 1-5 Improvements
Integrates: Semantic Search, Re-ranking, Quality Evaluation, Agentic Capabilities, Validation
"""

import asyncio
import sys
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import all our Phase 1-5 components
from topic_extractor import TopicExtractor
from enhanced_content_processor import EnhancedContentProcessor
from smart_document_filter import SmartDocumentFilter
from reranker import ReRanker
from quality_evaluator import QualityEvaluator
from agentic_rag_agent import AgenticRAGAgent
from validation_quality_scoring import QualityScoringMetrics

class FinalComprehensiveRAGCLI:
    """
    Final Comprehensive RAG CLI integrating all Phase 1-5 improvements:
    - Phase 1: Critical Fixes (Semantic Search, Re-ranking, Chunking)
    - Phase 2: Advanced Intelligence (Smart Filtering, Topic Detection)
    - Phase 3: Agentic Transformation (Memory, Reasoning, Prompts)
    - Phase 4: Quality Improvement (Evaluation, Feedback, Metadata)
    - Phase 5: Validation & Testing (Quality Metrics, Performance)
    """
    
    def __init__(self, vault_path: str = "D:\\Nomade Milionario"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize all Phase 1-5 components
        self.topic_extractor = TopicExtractor()
        self.content_processor = EnhancedContentProcessor()
        self.document_filter = SmartDocumentFilter()
        self.reranker = ReRanker()
        self.quality_evaluator = QualityEvaluator()
        self.agentic_agent = AgenticRAGAgent()
        self.quality_scorer = QualityScoringMetrics()
        
        # System state
        self.vault_content = {}
        self.conversation_history = []
        self.current_context = {}
        self.user_preferences = {}
        self.quality_metrics = {}
        
        # Performance tracking
        self.query_count = 0
        self.total_search_time = 0
        self.quality_scores = []
        
        # Initialize system
        self._initialize_system()
        
        self.logger.info("Final Comprehensive RAG CLI initialized with all Phase 1-5 improvements")
    
    def _initialize_system(self):
        """Initialize the complete RAG system"""
        print("🚀 Initializing Final Comprehensive RAG CLI...")
        print("=" * 60)
        
        # Load vault content
        self._load_vault_content()
        
        # Initialize search service
        self._initialize_search_service()
        
        # Load conversation history
        self._load_conversation_history()
        
        print("✅ System initialization complete!")
        print(f"📁 Vault: {self.vault_path}")
        print(f"📄 Documents loaded: {len(self.vault_content)}")
        print(f"🧠 Memory: {len(self.conversation_history)} previous conversations")
        print()
    
    def _load_vault_content(self):
        """Load and process vault content with enhanced metadata"""
        print("📚 Loading vault content with enhanced processing...")
        
        try:
            # Process all markdown files
            for file_path in self.vault_path.rglob("*.md"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Process with enhanced content processor
                        processed_doc = self.content_processor.process_document(file_path, content)
                        
                        # Store with enhanced metadata
                        self.vault_content[str(file_path)] = {
                            'filename': file_path.name,
                            'path': str(file_path),
                            'content': content,
                            'processed_content': processed_doc['content'],
                            'chunks': processed_doc['chunks'],
                            'metadata': processed_doc['metadata'],
                            'topics': processed_doc['metadata'].get('topics', []),
                            'key_terms': processed_doc['metadata'].get('key_terms', []),
                            'file_size': len(content),
                            'word_count': len(content.split()),
                            'last_modified': file_path.stat().st_mtime
                        }
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing {file_path}: {e}")
                        continue
            
            print(f"✅ Loaded {len(self.vault_content)} documents")
            
        except Exception as e:
            self.logger.error(f"Error loading vault content: {e}")
            print(f"❌ Error loading vault content: {e}")
    
    def _initialize_search_service(self):
        """Initialize the semantic search service"""
        try:
            # Initialize sentence transformer for embeddings
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("✅ Semantic search service initialized")
        except Exception as e:
            self.logger.error(f"Error initializing search service: {e}")
            print(f"❌ Error initializing search service: {e}")
    
    def _load_conversation_history(self):
        """Load conversation history from file"""
        try:
            history_file = Path("conversation_history.json")
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
        except Exception as e:
            self.logger.warning(f"Error loading conversation history: {e}")
    
    def _save_conversation_history(self):
        """Save conversation history to file"""
        try:
            history_file = Path("conversation_history.json")
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, default=str)
        except Exception as e:
            self.logger.warning(f"Error saving conversation history: {e}")
    
    async def search_command(self, query: str) -> Dict[str, Any]:
        """
        Main search command integrating all Phase 1-5 improvements
        """
        start_time = time.time()
        self.query_count += 1
        
        print(f"\n🔍 Processing query: '{query}'")
        print("-" * 50)
        
        try:
            # Phase 1: Critical Fixes - Semantic Search
            # 1. Detect topic using advanced topic detection
            topic = self._detect_topic(query)
            print(f"🎯 Detected topic: {topic}")
            
            # 2. Filter documents by topic and other criteria
            filtered_docs = self._filter_documents(query, topic)
            print(f"📄 Filtered documents: {len(filtered_docs)}")
            
            # 3. Perform semantic search with real embeddings
            search_results = await self._semantic_search(query, filtered_docs, top_k=10)
            print(f"🔍 Search results: {len(search_results)}")
            
            # Phase 2: Advanced Intelligence - Re-ranking
            # 4. Apply cross-encoder re-ranking
            if self.reranker and len(search_results) > 1:
                search_results = self.reranker.search_with_rerank(
                    query, search_results, n_results=5, rerank_top_k=10
                )
                print(f"🔄 Re-ranked results: {len(search_results)}")
            
            # Phase 3: Agentic Transformation - Context Assembly
            # 5. Assemble context for LLM
            context = self._assemble_context(search_results)
            
            # 6. Generate agentic response using structured prompts
            response = await self._generate_agentic_response(query, context, search_results)
            
            # Phase 4: Quality Improvement - Evaluation
            # 7. Evaluate response quality
            quality_metrics = self._evaluate_response_quality(query, response, search_results)
            
            # 8. Display results with quality information
            self._display_results(query, response, search_results, quality_metrics)
            
            # Phase 5: Validation - Metrics Tracking
            # 9. Track performance metrics
            search_time = time.time() - start_time
            self._track_metrics(query, search_results, quality_metrics, search_time)
            
            # 10. Update context and memory
            self._update_context(query, response, search_results, quality_metrics)
            
            return {
                'query': query,
                'response': response,
                'results': search_results,
                'quality_metrics': quality_metrics,
                'search_time': search_time,
                'topic': topic
            }
            
        except Exception as e:
            self.logger.error(f"Error in search command: {e}")
            print(f"❌ Error processing query: {e}")
            return {'error': str(e)}
    
    def _detect_topic(self, query: str) -> str:
        """Detect topic using advanced topic detection"""
        try:
            # Use topic extractor for advanced topic detection
            topics = self.topic_extractor.extract_topics(query)
            return topics[0] if topics else 'general'
        except Exception as e:
            self.logger.warning(f"Error detecting topic: {e}")
            return 'general'
    
    def _filter_documents(self, query: str, topic: str) -> List[Dict[str, Any]]:
        """Filter documents using smart document filter"""
        try:
            # Apply smart filtering
            filtered_docs = []
            for doc in self.vault_content.values():
                if self.document_filter.should_include(doc, query, topic):
                    filtered_docs.append(doc)
            return filtered_docs
        except Exception as e:
            self.logger.warning(f"Error filtering documents: {e}")
            return list(self.vault_content.values())
    
    async def _semantic_search(self, query: str, documents: List[Dict], top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search with real embeddings"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Calculate similarities for all documents
            results = []
            for doc in documents:
                # Use processed content for better search
                content = doc.get('processed_content', doc['content'])
                
                # Generate document embedding
                doc_embedding = self.embedding_model.encode([content])[0]
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                )
                
                results.append({
                    'filename': doc['filename'],
                    'path': doc['path'],
                    'content': content[:500] + "..." if len(content) > 500 else content,
                    'similarity': float(similarity),
                    'metadata': doc['metadata'],
                    'topics': doc.get('topics', []),
                    'file_size': doc['file_size']
                })
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []
    
    def _assemble_context(self, search_results: List[Dict]) -> str:
        """Assemble context from search results"""
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"Documento {i}: {result['filename']}\n"
                f"Tópicos: {', '.join(result.get('topics', []))}\n"
                f"Conteúdo: {result['content']}\n"
                f"Similaridade: {result['similarity']:.3f}\n"
            )
        return "\n".join(context_parts)
    
    async def _generate_agentic_response(self, query: str, context: str, search_results: List[Dict]) -> str:
        """Generate agentic response using structured prompts"""
        try:
            # Use agentic agent for response generation
            response = await self.agentic_agent.generate_response(
                query=query,
                context=context,
                search_results=search_results,
                conversation_history=self.conversation_history
            )
            return response
        except Exception as e:
            self.logger.warning(f"Error generating agentic response: {e}")
            # Fallback to simple response
            return f"Com base nos documentos encontrados, aqui está uma resposta para '{query}':\n\n{context[:500]}..."
    
    def _evaluate_response_quality(self, query: str, response: str, search_results: List[Dict]) -> Dict[str, Any]:
        """Evaluate response quality using comprehensive metrics"""
        try:
            # Use quality evaluator for comprehensive assessment
            quality_metrics = self.quality_evaluator.evaluate_response(
                query=query,
                response=response,
                retrieved_docs=search_results
            )
            return quality_metrics
        except Exception as e:
            self.logger.warning(f"Error evaluating response quality: {e}")
            return {'overall_score': 0.5, 'metrics': {}}
    
    def _display_results(self, query: str, response: str, search_results: List[Dict], quality_metrics: Dict[str, Any]):
        """Display results with quality information"""
        print(f"\n🤖 Resposta:")
        print(f"{response}")
        
        print(f"\n📊 Métricas de Qualidade:")
        print(f"Score Geral: {quality_metrics.get('overall_score', 0):.3f}")
        if 'metrics' in quality_metrics:
            for metric, value in quality_metrics['metrics'].items():
                print(f"  {metric}: {value:.3f}")
        
        print(f"\n📄 Documentos Relevantes:")
        for i, result in enumerate(search_results[:3], 1):
            print(f"  {i}. {result['filename']} (similaridade: {result['similarity']:.3f})")
            print(f"     Tópicos: {', '.join(result.get('topics', []))}")
        
        # Show follow-up suggestions
        self._show_follow_up_suggestions(query, search_results)
    
    def _show_follow_up_suggestions(self, query: str, search_results: List[Dict]):
        """Show intelligent follow-up suggestions"""
        try:
            suggestions = self.agentic_agent.generate_follow_up_suggestions(
                query=query,
                search_results=search_results,
                conversation_history=self.conversation_history
            )
            
            if suggestions:
                print(f"\n💡 Sugestões de Follow-up:")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    print(f"  {i}. {suggestion}")
        except Exception as e:
            self.logger.warning(f"Error generating follow-up suggestions: {e}")
    
    def _track_metrics(self, query: str, search_results: List[Dict], quality_metrics: Dict[str, Any], search_time: float):
        """Track performance and quality metrics"""
        self.total_search_time += search_time
        
        # Store quality score
        overall_score = quality_metrics.get('overall_score', 0)
        self.quality_scores.append(overall_score)
        
        # Update quality metrics
        self.quality_metrics[query] = {
            'timestamp': datetime.now().isoformat(),
            'quality_score': overall_score,
            'search_time': search_time,
            'num_results': len(search_results),
            'avg_similarity': np.mean([r['similarity'] for r in search_results]) if search_results else 0
        }
        
        print(f"\n⏱️  Tempo de busca: {search_time:.2f}s")
        print(f"📈 Score de qualidade: {overall_score:.3f}")
    
    def _update_context(self, query: str, response: str, search_results: List[Dict], quality_metrics: Dict[str, Any]):
        """Update conversation context and memory"""
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'quality_score': quality_metrics.get('overall_score', 0),
            'num_results': len(search_results)
        })
        
        # Update current context
        self.current_context = {
            'last_query': query,
            'last_response': response,
            'last_quality_score': quality_metrics.get('overall_score', 0),
            'last_topics': [r.get('topics', []) for r in search_results[:3]]
        }
        
        # Save conversation history
        self._save_conversation_history()
    
    async def chat(self):
        """Start interactive chat session"""
        print("🤖 Final Comprehensive RAG CLI - All Phase 1-5 Improvements")
        print("=" * 70)
        print("Digite 'exit' para sair, 'help' para ajuda, 'stats' para estatísticas")
        print()
        
        while True:
            try:
                user_input = input("\nVocê: ").strip()
                
                if user_input.lower() == 'exit':
                    print("Até mais! 👋")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'stats':
                    self._show_stats()
                    continue
                elif not user_input:
                    continue
                
                # Process query with all improvements
                result = await self.search_command(user_input)
                
                # Collect user feedback
                self._collect_user_feedback(user_input, result)
                
            except KeyboardInterrupt:
                print("\n\nAté mais! 👋")
                break
            except Exception as e:
                self.logger.error(f"Error in chat loop: {e}")
                print(f"❌ Erro: {e}")
    
    def _show_help(self):
        """Show help information"""
        print("\n📚 Ajuda - Final Comprehensive RAG CLI")
        print("-" * 40)
        print("Comandos disponíveis:")
        print("  exit    - Sair do programa")
        print("  help    - Mostrar esta ajuda")
        print("  stats   - Mostrar estatísticas do sistema")
        print()
        print("Funcionalidades integradas:")
        print("  🔍 Busca semântica avançada")
        print("  🧠 Capacidades agênticas com memória")
        print("  📊 Avaliação de qualidade em tempo real")
        print("  🔄 Re-ranking com cross-encoder")
        print("  🎯 Detecção inteligente de tópicos")
        print("  📈 Métricas de performance")
        print("  💡 Sugestões de follow-up")
    
    def _show_stats(self):
        """Show system statistics"""
        print("\n📊 Estatísticas do Sistema")
        print("-" * 30)
        print(f"Consultas processadas: {self.query_count}")
        print(f"Documentos carregados: {len(self.vault_content)}")
        print(f"Conversas anteriores: {len(self.conversation_history)}")
        
        if self.query_count > 0:
            avg_search_time = self.total_search_time / self.query_count
            avg_quality = np.mean(self.quality_scores) if self.quality_scores else 0
            print(f"Tempo médio de busca: {avg_search_time:.2f}s")
            print(f"Score médio de qualidade: {avg_quality:.3f}")
        
        print(f"Tópicos detectados: {len(set(topic for doc in self.vault_content.values() for topic in doc.get('topics', [])))}")
    
    def _collect_user_feedback(self, query: str, result: Dict[str, Any]):
        """Collect user feedback for quality improvement"""
        try:
            print("\nA resposta foi útil? (👍/👎/😐)")
            feedback = input().strip().lower()
            
            if feedback in ["👍", "👎", "😐"]:
                # Store feedback
                feedback_data = {
                    'timestamp': datetime.now().isoformat(),
                    'query': query,
                    'quality_score': result.get('quality_metrics', {}).get('overall_score', 0),
                    'feedback': feedback
                }
                
                # Save feedback
                feedback_file = Path("user_feedback.jsonl")
                with open(feedback_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(feedback_data) + '\n')
                
                if feedback == "👎":
                    print("Obrigado pelo feedback. Vamos usar isso para melhorar.")
                else:
                    print("Obrigado pelo feedback!")
            else:
                print("Feedback inválido. Por favor, use 👍, 👎 ou 😐.")
                
        except Exception as e:
            self.logger.warning(f"Error collecting feedback: {e}")

# Main execution
async def main():
    """Main function to run the CLI"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and run CLI
    cli = FinalComprehensiveRAGCLI()
    await cli.chat()

if __name__ == "__main__":
    asyncio.run(main())
