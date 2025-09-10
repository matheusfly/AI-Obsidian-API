#!/usr/bin/env python3
"""
Agentic RAG Agent - Phase 3 Implementation
Transforms RAG into a true agent with prompt engineering and memory
"""

import asyncio
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from collections import deque

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from enhanced_agentic_rag_cli import EnhancedAgenticRAGCLI
from topic_detector import TopicDetector
from smart_document_filter import SmartDocumentFilter
from reranker import ReRanker
from advanced_content_processor import AdvancedContentProcessor
from rag_quality_validator import RAGQualityValidator

class AgenticRAGAgent:
    def __init__(self, vault_path: str = "D:\\Nomade Milionario"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize core RAG system
        self.rag_system = EnhancedAgenticRAGCLI(vault_path)
        
        # Initialize agent-specific components
        self.conversation_history = deque(maxlen=50)  # Keep last 50 interactions
        self.current_context = {}
        self.user_preferences = {}
        self.session_metrics = {
            'queries_processed': 0,
            'avg_response_time': 0,
            'user_satisfaction': 0,
            'topics_discussed': set()
        }
        
        # Initialize prompt templates
        self.prompt_templates = self._initialize_prompt_templates()
        
        self.logger.info(f"Agentic RAG Agent initialized with {len(self.rag_system.documents)} document chunks")
    
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize structured prompt templates for different scenarios"""
        return {
            "general": """
Você é um assistente especializado em síntese e análise de conteúdo.
Com base APENAS nos documentos fornecidos, responda à pergunta do usuário.

DOCUMENTOS RELEVANTES:
{documents}

PERGUNTA: {query}

INSTRUÇÕES:
- Seja conciso e direto.
- Cite as fontes quando possível.
- Se os documentos não contêm a resposta, diga "Não encontrei informações sobre isso".
- Não invente respostas.

RESPOSTA:
""",
            
            "philosophy": """
Você é um especialista em filosofia e lógica matemática.
Analise os documentos fornecidos e forneça uma resposta fundamentada.

DOCUMENTOS RELEVANTES:
{documents}

PERGUNTA: {query}

INSTRUÇÕES:
- Foque em aspectos filosóficos e lógicos.
- Explique conceitos complexos de forma clara.
- Cite filósofos e teorias mencionadas.
- Se não houver informações suficientes, indique isso claramente.

RESPOSTA:
""",
            
            "technology": """
Você é um especialista em tecnologia e desenvolvimento.
Forneça uma resposta técnica precisa baseada nos documentos.

DOCUMENTOS RELEVANTES:
{documents}

PERGUNTA: {query}

INSTRUÇÕES:
- Use terminologia técnica apropriada.
- Forneça exemplos práticos quando possível.
- Explique conceitos técnicos de forma acessível.
- Se não houver informações técnicas suficientes, indique isso.

RESPOSTA:
""",
            
            "performance": """
Você é um especialista em otimização de performance e eficiência.
Analise os documentos e forneça conselhos práticos.

DOCUMENTOS RELEVANTES:
{documents}

PERGUNTA: {query}

INSTRUÇÕES:
- Foque em aspectos de performance e otimização.
- Forneça métricas e benchmarks quando disponíveis.
- Sugira melhorias práticas.
- Se não houver informações sobre performance, indique isso.

RESPOSTA:
""",
            
            "business": """
Você é um especialista em estratégia de negócios e gestão.
Forneça insights estratégicos baseados nos documentos.

DOCUMENTOS RELEVANTES:
{documents}

PERGUNTA: {query}

INSTRUÇÕES:
- Foque em aspectos estratégicos e de gestão.
- Forneça insights práticos para negócios.
- Explique conceitos de forma clara e aplicável.
- Se não houver informações de negócios, indique isso.

RESPOSTA:
"""
        }
    
    async def process_query(self, query: str, user_id: str = "default") -> Dict[str, Any]:
        """Process a user query with agentic capabilities"""
        start_time = time.time()
        
        try:
            # Update session metrics
            self.session_metrics['queries_processed'] += 1
            
            # Detect query topic and complexity
            topic = self.rag_system.topic_detector.detect_topic(query)
            complexity = self._analyze_query_complexity(query)
            
            # Update context
            self.current_context.update({
                'current_query': query,
                'detected_topic': topic,
                'query_complexity': complexity,
                'timestamp': datetime.now().isoformat()
            })
            
            # Search for relevant documents
            search_results = await self.rag_system.search_with_analysis(query, top_k=5)
            
            # Build context from search results
            context = self._build_agentic_context(query, search_results)
            
            # Generate agentic response
            response = await self._generate_agentic_response(query, context, topic)
            
            # Update conversation history
            self._update_conversation_history(query, response, search_results)
            
            # Calculate response time
            response_time = time.time() - start_time
            self._update_response_time(response_time)
            
            # Update user preferences
            self._update_user_preferences(user_id, query, response, search_results)
            
            # Generate follow-up suggestions
            follow_ups = self._generate_follow_up_suggestions(query, search_results)
            
            return {
                'query': query,
                'response': response,
                'context': context,
                'search_results': search_results,
                'follow_up_suggestions': follow_ups,
                'agent_metrics': {
                    'response_time': response_time,
                    'topic': topic,
                    'complexity': complexity,
                    'sources_used': len(search_results.get('results', [])),
                    'confidence': self._calculate_response_confidence(search_results)
                },
                'conversation_context': self._get_conversation_context()
            }
            
        except Exception as e:
            self.logger.error(f"Agent query processing error: {e}")
            return {
                'query': query,
                'response': f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}",
                'error': True,
                'agent_metrics': {
                    'response_time': time.time() - start_time,
                    'error': str(e)
                }
            }
    
    def _analyze_query_complexity(self, query: str) -> str:
        """Analyze query complexity for appropriate response level"""
        query_lower = query.lower()
        
        # Simple queries
        if len(query.split()) <= 3 and not any(word in query_lower for word in ['explain', 'analyze', 'compare', 'discuss']):
            return 'simple'
        
        # Complex queries
        if any(word in query_lower for word in ['explain', 'analyze', 'compare', 'discuss', 'evaluate', 'critique']):
            return 'complex'
        
        # Multi-step queries
        if any(word in query_lower for word in ['step by step', 'how to', 'process', 'workflow']):
            return 'multi_step'
        
        return 'medium'
    
    def _build_agentic_context(self, query: str, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build rich context for agentic response generation"""
        results = search_results.get('results', [])
        analysis = search_results.get('analysis', {})
        
        # Build document context
        documents_context = []
        for i, result in enumerate(results, 1):
            documents_context.append({
                'id': i,
                'content': result['content'],
                'heading': result.get('heading', 'No heading'),
                'file_path': result.get('file_path', 'Unknown'),
                'similarity': result.get('final_score', result.get('similarity', 0)),
                'metadata': result.get('metadata', {})
            })
        
        # Build conversation context
        conversation_context = self._get_conversation_context()
        
        # Build topic context
        topic_context = {
            'primary_topic': analysis.get('primary_topic', 'general'),
            'detected_topics': analysis.get('detected_topics', []),
            'topic_coverage': analysis.get('topic_coverage', 0)
        }
        
        return {
            'documents': documents_context,
            'conversation': conversation_context,
            'topic': topic_context,
            'quality_metrics': analysis,
            'query_analysis': {
                'complexity': self._analyze_query_complexity(query),
                'intent': self._analyze_query_intent(query),
                'entities': self._extract_entities(query)
            }
        }
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze user intent from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['what', 'what is', 'define', 'explain']):
            return 'definition'
        elif any(word in query_lower for word in ['how', 'how to', 'steps', 'process']):
            return 'how_to'
        elif any(word in query_lower for word in ['why', 'why is', 'reason', 'cause']):
            return 'explanation'
        elif any(word in query_lower for word in ['compare', 'difference', 'vs', 'versus']):
            return 'comparison'
        elif any(word in query_lower for word in ['example', 'instance', 'case']):
            return 'example'
        else:
            return 'general'
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract key entities from query"""
        # Simple entity extraction - can be enhanced with NER
        entities = []
        query_lower = query.lower()
        
        # Common technical terms
        tech_terms = ['machine learning', 'neural network', 'algorithm', 'data structure', 'database']
        for term in tech_terms:
            if term in query_lower:
                entities.append(term)
        
        # Philosophy terms
        philosophy_terms = ['logic', 'reasoning', 'argument', 'premise', 'conclusion']
        for term in philosophy_terms:
            if term in query_lower:
                entities.append(term)
        
        return entities
    
    async def _generate_agentic_response(self, query: str, context: Dict[str, Any], topic: str) -> str:
        """Generate agentic response using structured prompts"""
        # Select appropriate prompt template
        prompt_template = self.prompt_templates.get(topic, self.prompt_templates['general'])
        
        # Format documents for prompt
        documents_text = self._format_documents_for_prompt(context['documents'])
        
        # Format prompt
        formatted_prompt = prompt_template.format(
            documents=documents_text,
            query=query
        )
        
        # Add conversation context if available
        if context['conversation']:
            conversation_context = self._format_conversation_context(context['conversation'])
            formatted_prompt = f"CONTEXTO DA CONVERSA:\n{conversation_context}\n\n{formatted_prompt}"
        
        # Generate response (placeholder for Gemini integration)
        response = await self._call_llm(formatted_prompt, query, context)
        
        return response
    
    def _format_documents_for_prompt(self, documents: List[Dict[str, Any]]) -> str:
        """Format documents for prompt input"""
        if not documents:
            return "Nenhum documento relevante encontrado."
        
        formatted_docs = []
        for doc in documents:
            formatted_docs.append(f"""
Documento {doc['id']} (Relevância: {doc['similarity']:.3f}):
Título: {doc['heading']}
Arquivo: {doc['file_path']}
Conteúdo: {doc['content'][:500]}...
""")
        
        return "\n".join(formatted_docs)
    
    def _format_conversation_context(self, conversation: List[Dict[str, Any]]) -> str:
        """Format conversation context for prompt"""
        if not conversation:
            return "Nenhum contexto de conversa anterior."
        
        context_parts = []
        for i, turn in enumerate(conversation[-3:], 1):  # Last 3 turns
            context_parts.append(f"Turno {i}:")
            context_parts.append(f"  Pergunta: {turn['query']}")
            context_parts.append(f"  Resposta: {turn['response'][:200]}...")
        
        return "\n".join(context_parts)
    
    async def _call_llm(self, prompt: str, query: str, context: Dict[str, Any]) -> str:
        """Call LLM (placeholder for Gemini integration)"""
        # This is where you would integrate with Gemini or another LLM
        # For now, return a structured response based on the context
        
        documents = context['documents']
        topic = context['topic']['primary_topic']
        complexity = context['query_analysis']['complexity']
        
        if not documents:
            return "Não encontrei informações relevantes sobre sua pergunta nos documentos disponíveis."
        
        # Generate response based on context
        response_parts = []
        
        # Add topic-specific introduction
        if topic == 'philosophy':
            response_parts.append("Com base nos documentos filosóficos encontrados:")
        elif topic == 'technology':
            response_parts.append("Com base na documentação técnica disponível:")
        elif topic == 'performance':
            response_parts.append("Com base nas informações de performance encontradas:")
        else:
            response_parts.append("Com base nos documentos relevantes encontrados:")
        
        # Add main response
        if complexity == 'simple':
            response_parts.append(f"A resposta para '{query}' é:")
        elif complexity == 'complex':
            response_parts.append(f"Vou analisar sua pergunta '{query}' em detalhes:")
        else:
            response_parts.append(f"Sobre '{query}':")
        
        # Add document insights
        for i, doc in enumerate(documents[:3], 1):
            response_parts.append(f"\n{i}. {doc['heading']} (Relevância: {doc['similarity']:.3f})")
            response_parts.append(f"   {doc['content'][:200]}...")
        
        # Add conclusion
        response_parts.append(f"\nEstas são as informações mais relevantes que encontrei sobre '{query}'.")
        
        return "\n".join(response_parts)
    
    def _update_conversation_history(self, query: str, response: str, search_results: Dict[str, Any]):
        """Update conversation history with new interaction"""
        interaction = {
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'search_results': search_results,
            'topic': search_results.get('analysis', {}).get('primary_topic', 'general'),
            'sources_count': len(search_results.get('results', []))
        }
        
        self.conversation_history.append(interaction)
        
        # Update session metrics
        self.session_metrics['topics_discussed'].add(interaction['topic'])
    
    def _update_response_time(self, response_time: float):
        """Update average response time"""
        current_avg = self.session_metrics['avg_response_time']
        queries_count = self.session_metrics['queries_processed']
        
        if queries_count == 1:
            self.session_metrics['avg_response_time'] = response_time
        else:
            self.session_metrics['avg_response_time'] = (current_avg * (queries_count - 1) + response_time) / queries_count
    
    def _update_user_preferences(self, user_id: str, query: str, response: str, search_results: Dict[str, Any]):
        """Update user preferences based on interaction"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'preferred_topics': set(),
                'query_patterns': [],
                'satisfaction_scores': []
            }
        
        user_prefs = self.user_preferences[user_id]
        
        # Update preferred topics
        topic = search_results.get('analysis', {}).get('primary_topic', 'general')
        user_prefs['preferred_topics'].add(topic)
        
        # Update query patterns
        user_prefs['query_patterns'].append({
            'query': query,
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        })
    
    def _generate_follow_up_suggestions(self, query: str, search_results: Dict[str, Any]) -> List[str]:
        """Generate intelligent follow-up suggestions"""
        suggestions = []
        topic = search_results.get('analysis', {}).get('primary_topic', 'general')
        results = search_results.get('results', [])
        
        # Topic-specific suggestions
        if topic == 'philosophy':
            suggestions.extend([
                "Gostaria de saber mais sobre algum filósofo específico mencionado?",
                "Posso explicar melhor algum conceito filosófico?",
                "Há alguma teoria ou argumento que você gostaria de explorar?"
            ])
        elif topic == 'technology':
            suggestions.extend([
                "Posso fornecer exemplos práticos de implementação?",
                "Gostaria de saber sobre alguma tecnologia relacionada?",
                "Posso explicar melhor algum conceito técnico?"
            ])
        elif topic == 'performance':
            suggestions.extend([
                "Posso sugerir técnicas específicas de otimização?",
                "Gostaria de saber sobre métricas de performance?",
                "Posso explicar melhor algum conceito de eficiência?"
            ])
        else:
            suggestions.extend([
                "Posso fornecer mais detalhes sobre algum aspecto específico?",
                "Gostaria de explorar algum tópico relacionado?",
                "Posso explicar melhor algum conceito mencionado?"
            ])
        
        # Add general suggestions
        if len(results) > 0:
            suggestions.append("Posso buscar informações mais específicas sobre algum dos tópicos encontrados?")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _get_conversation_context(self) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        return list(self.conversation_history)[-3:]  # Last 3 interactions
    
    def _calculate_response_confidence(self, search_results: Dict[str, Any]) -> float:
        """Calculate confidence score for response"""
        results = search_results.get('results', [])
        analysis = search_results.get('analysis', {})
        
        if not results:
            return 0.0
        
        # Calculate confidence based on similarity scores and quality metrics
        similarities = [r.get('final_score', r.get('similarity', 0)) for r in results]
        avg_similarity = sum(similarities) / len(similarities)
        
        quality_score = analysis.get('quality_score', 0.5)
        topic_coverage = analysis.get('topic_coverage', 0)
        
        # Combine factors for confidence score
        confidence = (avg_similarity * 0.4 + quality_score * 0.4 + min(topic_coverage / 3, 1.0) * 0.2)
        
        return min(max(confidence, 0.0), 1.0)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            'conversation_length': len(self.conversation_history),
            'session_metrics': dict(self.session_metrics),
            'current_context': self.current_context,
            'user_preferences_count': len(self.user_preferences),
            'rag_system_stats': self.rag_system.get_system_stats(),
            'agent_capabilities': {
                'structured_prompts': len(self.prompt_templates),
                'conversation_memory': True,
                'topic_detection': True,
                'follow_up_suggestions': True,
                'user_preferences': True
            }
        }

# Test the agentic RAG agent
async def test_agentic_rag_agent():
    """Test the agentic RAG agent"""
    print("🤖 Testing Agentic RAG Agent")
    print("=" * 50)
    
    agent = AgenticRAGAgent()
    
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
        
        # Process query
        result = await agent.process_query(query)
        
        print(f"Response: {result['response'][:200]}...")
        print(f"Confidence: {result['agent_metrics']['confidence']:.3f}")
        print(f"Response Time: {result['agent_metrics']['response_time']:.3f}s")
        print(f"Sources Used: {result['agent_metrics']['sources_used']}")
        print(f"Follow-ups: {len(result['follow_up_suggestions'])}")
    
    # Show agent status
    status = agent.get_agent_status()
    print(f"\n📊 Agent Status:")
    print(f"  Conversations: {status['conversation_length']}")
    print(f"  Queries Processed: {status['session_metrics']['queries_processed']}")
    print(f"  Avg Response Time: {status['session_metrics']['avg_response_time']:.3f}s")
    print(f"  Topics Discussed: {len(status['session_metrics']['topics_discussed'])}")

if __name__ == "__main__":
    asyncio.run(test_agentic_rag_agent())
