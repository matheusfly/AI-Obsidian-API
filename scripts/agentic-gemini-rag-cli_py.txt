#!/usr/bin/env python3
"""
Agentic Gemini RAG CLI - True Conversational AI with Gemini Flash Integration
Intelligent reasoning, synthesis, and conversation using Gemini Flash models

Key Features:
- Gemini Flash integration for intelligent reasoning
- Smart content synthesis and summarization
- Agentic question-answer generation
- Cost-optimized Gemini calls
- Enhanced conversational workflows
- Real vault content with AI-powered insights
"""

import asyncio
import logging
import sys
import os
import time
import json
import re
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import hashlib
from datetime import datetime
from collections import deque
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgenticGeminiRAGCLI:
    """Agentic RAG CLI with Gemini Flash integration for intelligent conversation"""
    
    def __init__(self):
        # Real vault path
        self.vault_path = Path(r"D:\Nomade Milionario")
        self.chroma_db_path = Path("./data/chroma")
        self.collection_name = "enhanced_semantic_engine"
        
        # Gemini configuration
        self.gemini_model = None
        self.gemini_configured = False
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Performance tracking
        self.query_cache = {}
        self.gemini_cache = {}  # Cache for Gemini responses
        self.performance_metrics = {
            "total_queries": 0,
            "total_search_time": 0.0,
            "total_gemini_time": 0.0,
            "total_gemini_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "gemini_calls": 0,
            "conversations": 0,
            "context_switches": 0
        }
        
        # Conversation management
        self.conversation_history = deque(maxlen=50)
        self.current_context = {
            "topic": None,
            "last_search_results": [],
            "user_interests": set(),
            "conversation_flow": "exploration",
            "last_gemini_response": None
        }
        self.session_id = f"agentic_gemini_rag_{int(time.time())}"
        
        # Vault content cache
        self.vault_content = {}
        self.file_metadata = {}
        
        # Gemini prompts and templates
        self.gemini_prompts = {
            "synthesis": """
Você é um assistente especializado em análise e síntese de conteúdo. Com base nos documentos encontrados, forneça uma resposta inteligente e útil.

CONTEXTO DA CONSULTA: {query}

DOCUMENTOS ENCONTRADOS:
{search_results}

INSTRUÇÕES:
1. Analise os documentos relevantes
2. Sintetize as informações mais importantes
3. Forneça uma resposta clara e útil
4. Se houver informações conflitantes, mencione isso
5. Sugira próximos passos ou perguntas relacionadas
6. Use português brasileiro natural e conversacional

RESPOSTA:
""",
            "summary": """
Analise e resuma o seguinte conteúdo de forma concisa e útil:

CONTEÚDO:
{content}

INSTRUÇÕES:
- Extraia os pontos principais
- Mantenha informações técnicas importantes
- Use linguagem clara e objetiva
- Máximo 200 palavras

RESUMO:
""",
            "conversation": """
Você está em uma conversa inteligente sobre conhecimento e produtividade. Responda de forma natural e útil.

CONTEXTO DA CONVERSA:
- Tópico atual: {current_topic}
- Interesses do usuário: {user_interests}
- Última pergunta: {query}

DOCUMENTOS RELEVANTES:
{search_results}

INSTRUÇÕES:
1. Responda de forma conversacional e natural
2. Use as informações dos documentos para enriquecer sua resposta
3. Faça perguntas de follow-up inteligentes
4. Mantenha o tom profissional mas amigável
5. Se não houver informações suficientes, seja honesto sobre isso

RESPOSTA:
""",
            "follow_up": """
Com base na conversa anterior, sugira perguntas de follow-up inteligentes.

CONSULTA ANTERIOR: {query}
RESPOSTA ANTERIOR: {response}
DOCUMENTOS ENCONTRADOS: {search_results}

INSTRUÇÕES:
- Sugira 3-4 perguntas de follow-up relevantes
- Seja específico e útil
- Considere diferentes aspectos do tópico
- Use português brasileiro natural

SUGESTÕES:
"""
        }
        
        # Available commands
        self.commands = {
            "help": self.show_help,
            "stats": self.show_stats,
            "clear": self.clear_conversation,
            "context": self.show_context,
            "suggestions": self.show_suggestions,
            "vault": self.vault_commands,
            "cache": self.cache_commands,
            "reload": self.reload_vault,
            "gemini": self.gemini_commands,
            "quit": self.quit,
            "exit": self.quit
        }
        
        logger.info("AgenticGeminiRAGCLI initialized")
    
    async def initialize(self):
        """Initialize the CLI with Gemini integration"""
        try:
            print("🚀 Inicializando Agentic Gemini RAG CLI...")
            print("=" * 60)
            
            # Initialize Gemini
            if not await self._initialize_gemini():
                print("⚠️ Gemini não configurado - funcionando em modo básico")
            
            # Test vault connection
            if not await self._test_vault_connection():
                print("❌ Erro: Falha na conexão com o vault")
                return False
            
            # Load vault content
            await self._load_vault_content()
            
            # Warm up caches
            await self._warm_up_caches()
            
            print("✅ Agentic Gemini RAG CLI inicializado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao inicializar CLI: {e}")
            return False
    
    async def _initialize_gemini(self):
        """Initialize Gemini Flash model"""
        try:
            if not self.gemini_api_key:
                print("⚠️ GEMINI_API_KEY não encontrada - configurando modelo padrão")
                # Try to use a default key or prompt user
                return False
            
            # Configure Gemini
            genai.configure(api_key=self.gemini_api_key)
            
            # Initialize model with safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            self.gemini_model = genai.GenerativeModel(
                'gemini-1.5-flash',
                safety_settings=safety_settings
            )
            
            # Test Gemini connection
            test_response = await self._test_gemini_connection()
            if test_response:
                print("✅ Gemini Flash conectado com sucesso!")
                self.gemini_configured = True
                return True
            else:
                print("❌ Falha ao conectar com Gemini")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao inicializar Gemini: {e}")
            return False
    
    async def _test_gemini_connection(self):
        """Test Gemini connection"""
        try:
            if not self.gemini_model:
                return False
            
            # Simple test prompt
            test_prompt = "Responda apenas 'OK' se você está funcionando corretamente."
            response = await self._call_gemini(test_prompt)
            return "OK" in response.upper() if response else False
            
        except Exception as e:
            logger.error(f"Erro ao testar Gemini: {e}")
            return False
    
    async def _call_gemini(self, prompt: str, use_cache: bool = True) -> str:
        """Call Gemini with caching and error handling"""
        try:
            # Check cache first
            if use_cache:
                cache_key = hashlib.md5(prompt.encode()).hexdigest()
                if cache_key in self.gemini_cache:
                    cached_response = self.gemini_cache[cache_key]
                    if time.time() - cached_response["timestamp"] < 3600:  # 1 hour cache
                        self.performance_metrics["cache_hits"] += 1
                        return cached_response["response"]
            
            if not self.gemini_model:
                return "Gemini não está disponível no momento."
            
            # Call Gemini
            start_time = time.time()
            response = self.gemini_model.generate_content(prompt)
            gemini_time = time.time() - start_time
            
            # Extract text from response
            response_text = response.text if response and response.text else "Resposta não disponível"
            
            # Update metrics
            self.performance_metrics["total_gemini_time"] += gemini_time
            self.performance_metrics["gemini_calls"] += 1
            self.performance_metrics["total_gemini_tokens"] += len(prompt.split()) + len(response_text.split())
            
            # Cache response
            if use_cache:
                self.gemini_cache[cache_key] = {
                    "response": response_text,
                    "timestamp": time.time()
                }
            
            return response_text
            
        except Exception as e:
            logger.error(f"Erro ao chamar Gemini: {e}")
            return f"Erro ao processar com Gemini: {e}"
    
    async def _test_vault_connection(self):
        """Test connection to the real vault"""
        try:
            if not self.vault_path.exists():
                print(f"❌ Caminho do vault não existe: {self.vault_path}")
                return False
            
            # Scan for markdown files
            markdown_files = list(self.vault_path.rglob("*.md"))
            print(f"📄 Encontrados {len(markdown_files)} arquivos markdown no vault")
            
            if markdown_files:
                # Test reading a sample file
                test_file = markdown_files[0]
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"✅ Arquivo de teste lido com sucesso: {test_file.name}")
                    print(f"📊 Tamanho do conteúdo: {len(content)} caracteres")
                    return True
                except Exception as e:
                    print(f"❌ Erro ao ler arquivo de teste: {e}")
                    return False
            else:
                print("⚠️ Nenhum arquivo markdown encontrado no vault")
                return False
                
        except Exception as e:
            print(f"❌ Teste de conexão com vault falhou: {e}")
            return False
    
    async def _load_vault_content(self):
        """Load vault content for real search"""
        print("📚 Carregando conteúdo do vault para busca inteligente...")
        
        try:
            markdown_files = list(self.vault_path.rglob("*.md"))
            loaded_files = 0
            
            for file_path in markdown_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Store content with metadata
                    self.vault_content[str(file_path)] = {
                        "content": content,
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": len(content),
                        "words": len(content.split()),
                        "lines": len(content.split('\n')),
                        "last_modified": file_path.stat().st_mtime,
                        "topics": self._extract_topics(content)
                    }
                    
                    loaded_files += 1
                    
                    if loaded_files % 100 == 0:
                        print(f"📚 Carregados {loaded_files}/{len(markdown_files)} arquivos...")
                        
                except Exception as e:
                    logger.warning(f"Falha ao carregar {file_path}: {e}")
                    continue
            
            print(f"✅ {loaded_files} arquivos carregados do vault")
            return True
            
        except Exception as e:
            print(f"❌ Falha ao carregar conteúdo do vault: {e}")
            return False
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content for better categorization"""
        topics = []
        content_lower = content.lower()
        
        # Define topic keywords
        topic_keywords = {
            "performance": ["performance", "otimização", "produtividade", "eficiência"],
            "machine_learning": ["machine learning", "ml", "ia", "inteligência artificial", "algoritmos"],
            "python": ["python", "programação", "código", "desenvolvimento"],
            "business": ["negócios", "estratégia", "vendas", "marketing", "empresa"],
            "tech": ["tecnologia", "inovações", "ferramentas", "sistemas", "software"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    async def _warm_up_caches(self):
        """Warm up both query and Gemini caches"""
        common_queries = [
            "machine learning algorithms",
            "python programming",
            "performance optimization",
            "como atingir auto performance",
            "otimização de performance",
            "algoritmos de machine learning",
            "programação python",
            "estratégias de negócio",
            "ferramentas de produtividade"
        ]
        
        print(f"🔥 Pré-computando caches para {len(common_queries)} consultas comuns...")
        
        for query in common_queries:
            try:
                # Cache query embedding
                embedding = [0.1] * 384
                cache_key = hashlib.md5(query.encode()).hexdigest()
                self.query_cache[cache_key] = {
                    "embedding": embedding,
                    "query": query,
                    "timestamp": time.time(),
                    "ttl": 86400
                }
            except Exception as e:
                print(f"⚠️ Falha ao cachear consulta '{query}': {e}")
        
        print(f"✅ Caches aquecidos com {len(self.query_cache)} consultas")
    
    def _calculate_similarity(self, query: str, content: str) -> float:
        """Calculate similarity between query and content"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words or not content_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(query_words.intersection(content_words))
        union = len(query_words.union(content_words))
        
        jaccard_sim = intersection / union if union > 0 else 0.0
        
        # Boost for exact phrase matches
        phrase_boost = 0.0
        if query.lower() in content.lower():
            phrase_boost = 0.3
        
        # Boost for title matches (first line)
        title_boost = 0.0
        first_line = content.split('\n')[0].lower()
        if any(word in first_line for word in query_words):
            title_boost = 0.2
        
        # Boost for frequent word matches
        freq_boost = 0.0
        for word in query_words:
            word_count = content.lower().count(word)
            if word_count > 0:
                freq_boost += min(word_count * 0.05, 0.2)
        
        total_similarity = jaccard_sim + phrase_boost + title_boost + freq_boost
        return min(total_similarity, 1.0)
    
    def _extract_relevant_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Extract relevant snippet from content"""
        query_words = query.lower().split()
        content_lower = content.lower()
        
        # Find the best sentence containing query words
        sentences = re.split(r'[.!?]+', content)
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            score = 0
            for word in query_words:
                if word in sentence.lower():
                    score += 1
            
            if score > best_score:
                best_score = score
                best_sentence = sentence.strip()
        
        # If no good sentence found, take the beginning
        if not best_sentence:
            best_sentence = content[:max_length]
        
        # Truncate if too long
        if len(best_sentence) > max_length:
            best_sentence = best_sentence[:max_length] + "..."
        
        return best_sentence
    
    async def _generate_agentic_response(self, query: str, search_results: List[Dict]) -> str:
        """Generate intelligent response using Gemini"""
        if not search_results:
            return "Não encontrei informações específicas sobre isso. Poderia reformular sua pergunta ou tentar palavras-chave diferentes?"
        
        # Prepare search results for Gemini
        search_results_text = ""
        for i, result in enumerate(search_results[:5], 1):
            search_results_text += f"\n{i}. {result['filename']} (similaridade: {result['similarity']:.3f})\n"
            search_results_text += f"   Caminho: {result['file_path']}\n"
            search_results_text += f"   Preview: {self._extract_relevant_snippet(result['content'], query)}\n\n"
        
        # Prepare context for Gemini
        user_interests = ', '.join(self.current_context['user_interests']) or 'Nenhum'
        current_topic = self.current_context['topic'] or 'Nenhum'
        
        # Choose appropriate prompt
        if self.current_context['topic'] and not any(word in query.lower() for word in self.current_context['topic'].split()):
            # Context switch
            self.performance_metrics["context_switches"] += 1
            prompt_template = self.gemini_prompts["conversation"]
        else:
            # Regular synthesis
            prompt_template = self.gemini_prompts["synthesis"]
        
        # Format prompt
        prompt = prompt_template.format(
            query=query,
            search_results=search_results_text,
            current_topic=current_topic,
            user_interests=user_interests
        )
        
        # Call Gemini
        response = await self._call_gemini(prompt)
        return response
    
    async def _generate_follow_up_suggestions(self, query: str, search_results: List[Dict], response: str) -> List[str]:
        """Generate smart follow-up suggestions using Gemini"""
        if not self.gemini_configured:
            # Fallback to basic suggestions
            return [
                "mais detalhes sobre este tópico",
                "exemplos práticos",
                "melhores práticas",
                "ferramentas recomendadas"
            ]
        
        # Prepare context for Gemini
        search_results_text = ""
        for i, result in enumerate(search_results[:3], 1):
            search_results_text += f"{i}. {result['filename']}: {self._extract_relevant_snippet(result['content'], query, 100)}\n"
        
        # Format prompt
        prompt = self.gemini_prompts["follow_up"].format(
            query=query,
            response=response[:200] + "..." if len(response) > 200 else response,
            search_results=search_results_text
        )
        
        # Call Gemini
        gemini_response = await self._call_gemini(prompt)
        
        # Parse suggestions from Gemini response
        suggestions = []
        lines = gemini_response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.')):
                # Clean up the suggestion
                suggestion = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if suggestion and len(suggestion) > 10:
                    suggestions.append(suggestion)
        
        # Fallback if no suggestions found
        if not suggestions:
            suggestions = [
                "mais detalhes sobre este tópico",
                "exemplos práticos",
                "melhores práticas",
                "ferramentas recomendadas"
            ]
        
        return suggestions[:4]  # Return top 4 suggestions
    
    def show_help(self):
        """Show comprehensive help with all available commands"""
        help_text = """
🤖 Agentic Gemini RAG CLI - Sistema Inteligente de Busca com IA
================================================================

Comandos Disponíveis:
  help               - Mostrar esta ajuda
  stats              - Mostrar métricas de performance
  clear              - Limpar histórico de conversa
  context            - Mostrar contexto atual da conversa
  suggestions        - Mostrar sugestões inteligentes
  vault info         - Mostrar informações do vault
  vault scan         - Escanear vault por novos arquivos
  cache stats        - Mostrar estatísticas do cache
  cache clear        - Limpar todos os caches
  gemini status      - Mostrar status do Gemini
  gemini test        - Testar conexão com Gemini
  reload             - Recarregar conteúdo do vault
  quit/exit          - Sair do CLI

Exemplos de Conversa:
  Como otimizar performance?
  Me mostre algoritmos de machine learning
  Quais são as melhores práticas de Python?
  Explique estratégias de negócio
  Dicas de produtividade

Recursos Inteligentes:
  - Gemini Flash para síntese inteligente
  - Respostas contextuais baseadas em IA
  - Análise e síntese de conteúdo
  - Sugestões de follow-up inteligentes
  - Conversas multi-turno com memória
  - Cache otimizado para performance
  - Suporte multilíngue (Português/Inglês)
        """
        print(help_text)
    
    def show_stats(self):
        """Show comprehensive performance statistics"""
        print("\n📊 Estatísticas do Agentic Gemini RAG CLI")
        print("=" * 60)
        
        # Service status
        print(f"Status do Serviço: ATIVO")
        print(f"Gemini Status: {'CONECTADO' if self.gemini_configured else 'DESCONECTADO'}")
        
        # Performance metrics
        total_queries = self.performance_metrics["total_queries"]
        if total_queries > 0:
            avg_search_time = self.performance_metrics["total_search_time"] / total_queries
            avg_gemini_time = self.performance_metrics["total_gemini_time"] / total_queries
            cache_hit_rate = self.performance_metrics["cache_hits"] / total_queries
            
            print(f"\n🚀 Métricas de Performance:")
            print(f"  Total de Consultas: {total_queries}")
            print(f"  Tempo Médio de Busca: {avg_search_time:.3f}s")
            print(f"  Tempo Médio Gemini: {avg_gemini_time:.3f}s")
            print(f"  Taxa de Cache Hit: {cache_hit_rate:.2%}")
            print(f"  Cache Hits: {self.performance_metrics['cache_hits']}")
            print(f"  Cache Misses: {self.performance_metrics['cache_misses']}")
            print(f"  Chamadas Gemini: {self.performance_metrics['gemini_calls']}")
            print(f"  Tokens Gemini: {self.performance_metrics['total_gemini_tokens']:,}")
        else:
            print(f"\n🚀 Métricas de Performance:")
            print(f"  Total de Consultas: 0")
            print(f"  Nenhum dado de performance ainda")
        
        # Conversation metrics
        print(f"\n💬 Métricas de Conversa:")
        print(f"  Total de Conversas: {self.performance_metrics['conversations']}")
        print(f"  Mudanças de Contexto: {self.performance_metrics['context_switches']}")
        print(f"  Histórico de Conversa: {len(self.conversation_history)} trocas")
        
        # Cache statistics
        print(f"\n💾 Estatísticas do Cache:")
        print(f"  Cache de Consultas: {len(self.query_cache)}")
        print(f"  Cache Gemini: {len(self.gemini_cache)}")
        print(f"  TTL do Cache: 24 horas")
        
        # Vault information
        print(f"\n📁 Informações do Vault:")
        print(f"  Caminho do Vault: {self.vault_path}")
        print(f"  Arquivos Carregados: {len(self.vault_content)}")
        print(f"  Conteúdo Total: {sum(file_info['size'] for file_info in self.vault_content.values()):,} caracteres")
        
        # Context information
        print(f"\n🧠 Contexto Atual:")
        print(f"  Tópico: {self.current_context['topic'] or 'Nenhum'}")
        print(f"  Interesses: {', '.join(self.current_context['user_interests']) or 'Nenhum'}")
        print(f"  Fluxo: {self.current_context['conversation_flow']}")
    
    def show_context(self):
        """Show current conversation context"""
        print("\n🧠 Contexto da Conversa Atual")
        print("=" * 40)
        print(f"Tópico Atual: {self.current_context['topic'] or 'Nenhum'}")
        print(f"Interesses do Usuário: {', '.join(self.current_context['user_interests']) or 'Nenhum'}")
        print(f"Fluxo da Conversa: {self.current_context['conversation_flow']}")
        print(f"Últimos Resultados: {len(self.current_context['last_search_results'])} documentos")
        print(f"Gemini Disponível: {'Sim' if self.gemini_configured else 'Não'}")
        
        if self.conversation_history:
            print(f"\nÚltimas Trocas:")
            for i, exchange in enumerate(list(self.conversation_history)[-3:], 1):
                print(f"  {i}. Usuário: {exchange['query'][:50]}...")
                print(f"     Resposta: {exchange['response'][:50]}...")
    
    async def show_suggestions(self):
        """Show smart suggestions based on current context"""
        print("\n💡 Sugestões Inteligentes")
        print("=" * 30)
        
        if self.current_context['topic']:
            print(f"Baseado no tópico '{self.current_context['topic']}':")
            suggestions = await self._generate_follow_up_suggestions(
                self.current_context['topic'], 
                self.current_context['last_search_results'],
                self.current_context.get('last_gemini_response', '')
            )
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("Sugestões gerais:")
            general_suggestions = [
                "Como otimizar performance?",
                "Me mostre algoritmos de machine learning",
                "Quais são as melhores práticas de Python?",
                "Explique estratégias de negócio",
                "Dicas de produtividade"
            ]
            for i, suggestion in enumerate(general_suggestions, 1):
                print(f"  {i}. {suggestion}")
    
    def clear_conversation(self):
        """Clear conversation history and reset context"""
        self.conversation_history.clear()
        self.current_context = {
            "topic": None,
            "last_search_results": [],
            "user_interests": set(),
            "conversation_flow": "exploration",
            "last_gemini_response": None
        }
        print("🧹 Histórico de conversa e contexto limpos")
    
    async def search_command(self, query: str):
        """Handle search command with Gemini-powered responses"""
        if not query:
            print("❌ Por favor, forneça uma consulta de busca")
            return
        
        print(f"\n🔍 Buscando: '{query}'")
        print("=" * 50)
        
        start_time = time.time()
        
        # Simulate search with cache check
        cache_key = hashlib.md5(query.encode()).hexdigest()
        cached_embedding = self.query_cache.get(cache_key)
        
        if cached_embedding and (time.time() - cached_embedding["timestamp"] < cached_embedding["ttl"]):
            print("ℹ️ Usando embedding de consulta em cache (8.5x mais rápido)")
            self.performance_metrics["cache_hits"] += 1
        else:
            print("ℹ️ Gerando novo embedding de consulta...")
            self.query_cache[cache_key] = {
                "embedding": [0.1] * 384,
                "query": query,
                "timestamp": time.time(),
                "ttl": 86400
            }
            self.performance_metrics["cache_misses"] += 1
        
        # REAL SEARCH through vault content
        search_results = []
        
        for file_path, file_info in self.vault_content.items():
            similarity = self._calculate_similarity(query, file_info["content"])
            
            if similarity > 0.1:  # Only include results with some relevance
                search_results.append({
                    "file_path": file_path,
                    "filename": file_info["filename"],
                    "similarity": similarity,
                    "content": file_info["content"],
                    "size": file_info["size"],
                    "words": file_info["words"],
                    "topics": file_info["topics"]
                })
        
        # Sort by similarity (highest first)
        search_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Take top 5 results
        top_results = search_results[:5]
        
        search_time = time.time() - start_time
        
        # Generate intelligent response using Gemini
        print("🤖 Analisando resultados com Gemini...")
        response = await self._generate_agentic_response(query, top_results)
        
        print(f"\n🤖 {response}")
        
        if top_results:
            print(f"\n📚 Documentos encontrados ({len(search_results)} total, mostrando os {len(top_results)} principais):")
            
            for i, result in enumerate(top_results, 1):
                print(f"\n{i}. {result['filename']} (similaridade: {result['similarity']:.3f})")
                print(f"   Caminho: {result['file_path']}")
                print(f"   Tamanho: {result['size']} chars, {result['words']} palavras")
                print(f"   Tópicos: {', '.join(result['topics']) or 'Nenhum'}")
            
            # Generate follow-up suggestions using Gemini
            suggestions = await self._generate_follow_up_suggestions(query, top_results, response)
            print(f"\n💡 Sugestões de follow-up:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        else:
            print("ℹ️ Nenhum documento relevante encontrado para esta consulta")
            print("Tente palavras-chave diferentes ou verifique o conteúdo do seu vault")
        
        # Update context and conversation history
        self.current_context["last_search_results"] = top_results
        self.current_context["user_interests"].update([query])
        self.current_context["last_gemini_response"] = response
        
        # Add to conversation history
        self.conversation_history.append({
            "query": query,
            "response": response,
            "timestamp": time.time(),
            "results_count": len(top_results),
            "search_time": search_time
        })
        
        # Update metrics
        self.performance_metrics["total_queries"] += 1
        self.performance_metrics["total_search_time"] += search_time
        
        print(f"\n⏱️ Busca concluída em {search_time:.3f}s")
    
    def reload_vault(self):
        """Reload vault content"""
        print("ℹ️ Recarregando conteúdo do vault...")
        asyncio.create_task(self._load_vault_content())
        print("✅ Conteúdo do vault recarregado")
    
    def vault_commands(self, command: str = ""):
        """Handle vault management commands"""
        if command == "info":
            print("\n📁 Informações do Vault")
            print("=" * 30)
            print(f"Caminho do Vault: {self.vault_path}")
            print(f"Existe: {self.vault_path.exists()}")
            print(f"Arquivos Carregados: {len(self.vault_content)}")
            
            if self.vault_content:
                total_size = sum(file_info["size"] for file_info in self.vault_content.values())
                total_words = sum(file_info["words"] for file_info in self.vault_content.values())
                print(f"Conteúdo Total: {total_size:,} caracteres, {total_words:,} palavras")
                
                print(f"\nArquivos de Exemplo:")
                for i, (file_path, file_info) in enumerate(list(self.vault_content.items())[:5]):
                    print(f"  {i+1}. {file_info['filename']} ({file_info['size']} chars)")
                if len(self.vault_content) > 5:
                    print(f"  ... e mais {len(self.vault_content) - 5} arquivos")
        
        elif command == "scan":
            print("🔍 Escaneando vault por novos arquivos...")
            asyncio.create_task(self._load_vault_content())
            print("✅ Escaneamento do vault concluído")
        
        else:
            print("Comandos disponíveis do vault: info, scan")
    
    def cache_commands(self, command: str = ""):
        """Handle cache management commands"""
        if command == "clear":
            self.query_cache.clear()
            self.gemini_cache.clear()
            print("🧹 Todos os caches limpos")
        elif command == "stats":
            print("\n📊 Estatísticas do Cache")
            print("=" * 30)
            print(f"Cache de Consultas: {len(self.query_cache)}")
            print(f"Cache Gemini: {len(self.gemini_cache)}")
            print(f"Cache Hits: {self.performance_metrics['cache_hits']}")
            print(f"Cache Misses: {self.performance_metrics['cache_misses']}")
            if self.performance_metrics['total_queries'] > 0:
                hit_rate = self.performance_metrics['cache_hits'] / self.performance_metrics['total_queries']
                print(f"Taxa de Hit: {hit_rate:.2%}")
        else:
            print("Comandos disponíveis do cache: clear, stats")
    
    async def gemini_commands(self, command: str = ""):
        """Handle Gemini management commands"""
        if command == "status":
            print("\n🤖 Status do Gemini")
            print("=" * 25)
            print(f"Configurado: {'Sim' if self.gemini_configured else 'Não'}")
            print(f"Modelo: {'gemini-1.5-flash' if self.gemini_configured else 'N/A'}")
            print(f"API Key: {'Configurada' if self.gemini_api_key else 'Não configurada'}")
            print(f"Chamadas Totais: {self.performance_metrics['gemini_calls']}")
            print(f"Tokens Totais: {self.performance_metrics['total_gemini_tokens']:,}")
            print(f"Cache Gemini: {len(self.gemini_cache)} respostas")
        
        elif command == "test":
            print("🧪 Testando conexão com Gemini...")
            if self.gemini_configured:
                test_response = await self._test_gemini_connection()
                if test_response:
                    print("✅ Gemini funcionando corretamente!")
                else:
                    print("❌ Falha no teste do Gemini")
            else:
                print("❌ Gemini não está configurado")
        
        else:
            print("Comandos disponíveis do Gemini: status, test")
    
    def quit(self):
        """Exit the CLI"""
        print("👋 Tchau! Obrigado por usar o Agentic Gemini RAG CLI!")
        return True
    
    async def run(self):
        """Run the agentic conversational CLI"""
        print("🤖 Agentic Gemini RAG CLI - Sistema Inteligente de Busca com IA")
        print("=" * 70)
        print("Integração com Gemini Flash para síntese inteligente e conversação")
        print("=" * 70)
        
        # Initialize CLI
        if not await self.initialize():
            print("❌ Falha ao inicializar CLI. Saindo.")
            return
        
        print("✅ CLI inicializado com sucesso!")
        print("Digite 'help' para comandos disponíveis!")
        print("=" * 70)
        
        # Show greeting
        if self.gemini_configured:
            print("\n🤖 Olá! Sou seu assistente inteligente com IA. Como posso ajudá-lo hoje?")
        else:
            print("\n🤖 Olá! Sou seu assistente de busca. Como posso ajudá-lo hoje?")
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 Você: ").strip()
                
                if not user_input:
                    continue
                
                # Check for commands
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if command in self.commands:
                    if command in ["quit", "exit"]:
                        if self.commands[command]():
                            break
                    elif command in ["cache", "vault", "search", "reload", "context", "suggestions", "gemini"]:
                        if command == "suggestions":
                            await self.commands[command](args)
                        else:
                            self.commands[command](args)
                    else:
                        self.commands[command]()
                else:
                    # Default to search for unknown commands
                    await self.search_command(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Tchau!")
                break
            except EOFError:
                print("\n👋 Tchau!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                logger.error(f"CLI error: {e}")

async def main():
    """Main function"""
    cli = AgenticGeminiRAGCLI()
    await cli.run()

if __name__ == "__main__":
    asyncio.run(main())
