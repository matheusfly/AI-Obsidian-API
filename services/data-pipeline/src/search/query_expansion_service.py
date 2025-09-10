#!/usr/bin/env python3
"""
Query Expansion and Understanding Service
Enhances search capabilities by expanding ambiguous or short queries
"""
import logging
import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
import os

logger = logging.getLogger(__name__)

class ExpansionStrategy(Enum):
    """Query expansion strategies"""
    RULE_BASED = "rule_based"
    LLM_BASED = "llm_based"
    HYBRID = "hybrid"

@dataclass
class QueryAnalysis:
    """Analysis result of a query"""
    original_query: str
    expanded_query: str
    intent: str
    entities: List[str]
    expansion_confidence: float
    strategy_used: ExpansionStrategy
    expansion_reasoning: str

class QueryExpansionService:
    """Service for expanding and understanding user queries"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.expansion_rules = self._initialize_expansion_rules()
        self.synonym_library = self._initialize_synonym_library()
        self.intent_patterns = self._initialize_intent_patterns()
        
        # Initialize Gemini if API key is available
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini model initialized for query expansion")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Gemini: {e}")
                self.gemini_model = None
        else:
            logger.warning("⚠️ No Gemini API key provided, LLM-based expansion disabled")
            self.gemini_model = None
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection for English and Portuguese.
        Returns 'en', 'pt', or 'unknown'.
        """
        # Portuguese indicators
        pt_indicators = [
            r'\b(que|para|com|uma|dos|das|não|mais|muito|sobre|entre|através|durante|após|antes|depois|quando|onde|como|porque|porquê|porquê)\b',
            r'\b(é|são|foi|foram|será|serão|tem|têm|tinha|tinham|terá|terão)\b',
            r'\b(de|da|do|em|na|no|pela|pelo|pelas|pelos)\b',
            r'ção\b', r'ões\b', r'ães\b', r'ães\b', r'ões\b'
        ]
        
        # English indicators
        en_indicators = [
            r'\b(the|and|for|are|but|not|you|all|can|had|her|was|one|our|out|day|get|has|him|his|how|its|may|new|now|old|see|two|way|who|boy|did|man|men|put|say|she|too|use)\b',
            r'\b(is|was|were|been|have|has|had|will|would|could|should|may|might|must|shall)\b',
            r'\b(ing\b|tion\b|ness\b|ment\b|able\b|ible\b)'
        ]
        
        text_lower = text.lower()
        
        pt_score = sum(len(re.findall(pattern, text_lower)) for pattern in pt_indicators)
        en_score = sum(len(re.findall(pattern, text_lower)) for pattern in en_indicators)
        
        if pt_score > en_score and pt_score > 0:
            return 'pt'
        elif en_score > pt_score and en_score > 0:
            return 'en'
        else:
            return 'unknown'
    
    def _initialize_expansion_rules(self) -> Dict[str, str]:
        """Initialize rule-based expansion patterns for English and Portuguese"""
        return {
            # English Programming and technical terms
            "tips": "tips, tricks, best practices, guidelines",
            "how to": "how to, guide, tutorial, steps for, instructions",
            "tutorial": "tutorial, guide, walkthrough, step-by-step",
            "examples": "examples, sample code, demonstrations, use cases",
            "setup": "setup, installation, configuration, getting started",
            "debug": "debug, troubleshooting, fix, resolve, error handling",
            "optimize": "optimize, performance, efficiency, improve, enhance",
            "security": "security, authentication, authorization, protection",
            "testing": "testing, unit tests, integration tests, test cases",
            
            # Portuguese Programming and technical terms
            "dicas": "dicas, truques, melhores práticas, diretrizes",
            "como fazer": "como fazer, guia, tutorial, passos para, instruções",
            "tutorial": "tutorial, guia, passo a passo, instruções detalhadas",
            "exemplos": "exemplos, código de exemplo, demonstrações, casos de uso",
            "configuração": "configuração, instalação, setup, configuração inicial",
            "depuração": "depuração, solução de problemas, corrigir, resolver, tratamento de erros",
            "otimizar": "otimizar, performance, eficiência, melhorar, aprimorar",
            "segurança": "segurança, autenticação, autorização, proteção",
            "testes": "testes, testes unitários, testes de integração, casos de teste",
            
            # English General terms
            "learn": "learn, study, understand, master, get started with",
            "beginner": "beginner, basic, fundamentals, introduction, getting started",
            "advanced": "advanced, expert, complex, sophisticated, professional",
            "quick": "quick, fast, rapid, efficient, time-saving",
            "easy": "easy, simple, straightforward, beginner-friendly",
            "difficult": "difficult, challenging, complex, advanced, expert-level",
            
            # Portuguese General terms
            "aprender": "aprender, estudar, entender, dominar, começar com",
            "iniciante": "iniciante, básico, fundamentos, introdução, começando",
            "avançado": "avançado, especialista, complexo, sofisticado, profissional",
            "rápido": "rápido, veloz, eficiente, que economiza tempo",
            "fácil": "fácil, simples, direto, amigável para iniciantes",
            "difícil": "difícil, desafiador, complexo, avançado, nível especialista",
            
            # English Data and analysis terms
            "analyze": "analyze, analysis, examine, investigate, study",
            "visualize": "visualize, visualization, charts, graphs, plots",
            "process": "process, processing, transform, manipulate, handle",
            "store": "store, storage, save, persist, database",
            "retrieve": "retrieve, fetch, get, access, query",
            
            # Portuguese Data and analysis terms
            "analisar": "analisar, análise, examinar, investigar, estudar",
            "visualizar": "visualizar, visualização, gráficos, charts, plots",
            "processar": "processar, processamento, transformar, manipular, lidar com",
            "armazenar": "armazenar, armazenamento, salvar, persistir, banco de dados",
            "recuperar": "recuperar, buscar, obter, acessar, consultar",
            
            # English AI and ML terms
            "model": "model, algorithm, machine learning, AI, neural network",
            "train": "train, training, learning, fit, optimize",
            "predict": "predict, prediction, forecast, estimate, inference",
            "embedding": "embedding, vector, representation, encoding",
            "similarity": "similarity, distance, matching, comparison, relevance",
            
            # Portuguese AI and ML terms
            "modelo": "modelo, algoritmo, machine learning, IA, rede neural",
            "treinar": "treinar, treinamento, aprendizado, ajustar, otimizar",
            "prever": "prever, predição, previsão, estimar, inferência",
            "embedding": "embedding, vetor, representação, codificação",
            "similaridade": "similaridade, distância, correspondência, comparação, relevância"
        }
    
    def _initialize_synonym_library(self) -> Dict[str, List[str]]:
        """Initialize synonym library for term expansion (English and Portuguese)"""
        return {
            # English Technical Terms
            "python": ["python", "py", "python3", "python programming"],
            "javascript": ["javascript", "js", "node.js", "nodejs"],
            "react": ["react", "reactjs", "react.js", "react frontend"],
            "vue": ["vue", "vuejs", "vue.js", "vue frontend"],
            "angular": ["angular", "angularjs", "angular.js"],
            "fastapi": ["fastapi", "fast api", "fastapi framework"],
            "django": ["django", "django framework", "django web"],
            "flask": ["flask", "flask framework", "flask web"],
            "sql": ["sql", "database", "db", "sqlite", "postgresql", "mysql"],
            "mongodb": ["mongodb", "mongo", "nosql", "document database"],
            "redis": ["redis", "cache", "caching", "memory store"],
            "docker": ["docker", "container", "containerization"],
            "kubernetes": ["kubernetes", "k8s", "orchestration"],
            "aws": ["aws", "amazon web services", "cloud"],
            "azure": ["azure", "microsoft azure", "cloud"],
            "gcp": ["gcp", "google cloud", "google cloud platform"],
            "git": ["git", "version control", "github", "gitlab"],
            "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
            "api": ["api", "rest api", "web api", "endpoint"],
            "microservices": ["microservices", "microservice", "service architecture"],
            "machine learning": ["machine learning", "ml", "ai", "artificial intelligence"],
            "deep learning": ["deep learning", "neural networks", "deep neural networks"],
            "nlp": ["nlp", "natural language processing", "text processing"],
            "computer vision": ["computer vision", "cv", "image processing"],
            "data science": ["data science", "data analysis", "data engineering"],
            "pandas": ["pandas", "dataframe", "data manipulation"],
            "numpy": ["numpy", "numerical computing", "arrays"],
            "tensorflow": ["tensorflow", "tf", "deep learning framework"],
            "pytorch": ["pytorch", "torch", "deep learning framework"],
            "scikit-learn": ["scikit-learn", "sklearn", "machine learning library"],
            "jupyter": ["jupyter", "jupyter notebook", "notebook"],
            "anaconda": ["anaconda", "conda", "python distribution"],
            "pip": ["pip", "package manager", "python packages"],
            "virtual environment": ["virtual environment", "venv", "conda env"],
            "requirements": ["requirements", "dependencies", "packages"],
            "deployment": ["deployment", "deploy", "production", "hosting"],
            "monitoring": ["monitoring", "logging", "observability", "metrics"],
            "testing": ["testing", "unit tests", "integration tests", "test cases"],
            "documentation": ["documentation", "docs", "readme", "api docs"],
            "performance": ["performance", "optimization", "speed", "efficiency"],
            "scalability": ["scalability", "scaling", "load balancing", "horizontal scaling"],
            "security": ["security", "authentication", "authorization", "encryption"],
            "error handling": ["error handling", "exception handling", "error management"],
            "logging": ["logging", "logs", "debugging", "troubleshooting"],
            "configuration": ["configuration", "config", "settings", "environment variables"],
            "environment": ["environment", "env", "development", "production", "staging"],
            
            # Portuguese Technical Terms
            "python": ["python", "py", "python3", "programação python"],
            "javascript": ["javascript", "js", "node.js", "nodejs"],
            "react": ["react", "reactjs", "react.js", "frontend react"],
            "vue": ["vue", "vuejs", "vue.js", "frontend vue"],
            "angular": ["angular", "angularjs", "angular.js"],
            "fastapi": ["fastapi", "fast api", "framework fastapi"],
            "django": ["django", "framework django", "web django"],
            "flask": ["flask", "framework flask", "web flask"],
            "sql": ["sql", "banco de dados", "bd", "sqlite", "postgresql", "mysql"],
            "mongodb": ["mongodb", "mongo", "nosql", "banco de documentos"],
            "redis": ["redis", "cache", "cache", "armazenamento em memória"],
            "docker": ["docker", "container", "containerização"],
            "kubernetes": ["kubernetes", "k8s", "orquestração"],
            "aws": ["aws", "amazon web services", "nuvem"],
            "azure": ["azure", "microsoft azure", "nuvem"],
            "gcp": ["gcp", "google cloud", "google cloud platform"],
            "git": ["git", "controle de versão", "github", "gitlab"],
            "ci/cd": ["ci/cd", "integração contínua", "deploy contínuo"],
            "api": ["api", "rest api", "web api", "endpoint"],
            "microserviços": ["microserviços", "microserviço", "arquitetura de serviços"],
            "machine learning": ["machine learning", "ml", "ia", "inteligência artificial"],
            "deep learning": ["deep learning", "redes neurais", "redes neurais profundas"],
            "nlp": ["nlp", "processamento de linguagem natural", "processamento de texto"],
            "computer vision": ["computer vision", "cv", "processamento de imagem"],
            "data science": ["data science", "análise de dados", "engenharia de dados"],
            "pandas": ["pandas", "dataframe", "manipulação de dados"],
            "numpy": ["numpy", "computação numérica", "arrays"],
            "tensorflow": ["tensorflow", "tf", "framework deep learning"],
            "pytorch": ["pytorch", "torch", "framework deep learning"],
            "scikit-learn": ["scikit-learn", "sklearn", "biblioteca machine learning"],
            "jupyter": ["jupyter", "jupyter notebook", "notebook"],
            "anaconda": ["anaconda", "conda", "distribuição python"],
            "pip": ["pip", "gerenciador de pacotes", "pacotes python"],
            "virtual environment": ["ambiente virtual", "venv", "conda env"],
            "requirements": ["requirements", "dependências", "pacotes"],
            "deployment": ["deployment", "deploy", "produção", "hospedagem"],
            "monitoring": ["monitoring", "logging", "observabilidade", "métricas"],
            "testing": ["testing", "testes unitários", "testes de integração", "casos de teste"],
            "documentation": ["documentação", "docs", "readme", "docs api"],
            "performance": ["performance", "otimização", "velocidade", "eficiência"],
            "scalability": ["escalabilidade", "escalonamento", "balanceamento de carga", "escalonamento horizontal"],
            "security": ["segurança", "autenticação", "autorização", "criptografia"],
            "error handling": ["tratamento de erros", "gerenciamento de exceções", "gerenciamento de erros"],
            "logging": ["logging", "logs", "debugging", "solução de problemas"],
            "configuration": ["configuração", "config", "configurações", "variáveis de ambiente"],
            "environment": ["ambiente", "env", "desenvolvimento", "produção", "staging"]
        }
    
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for query intent detection (English and Portuguese)"""
        return {
            "how_to": [
                # English patterns
                r"how to", r"how do i", r"how can i", r"steps to", r"guide to",
                r"tutorial", r"walkthrough", r"instructions",
                # Portuguese patterns
                r"como fazer", r"como posso", r"passos para", r"guia para",
                r"tutorial", r"passo a passo", r"instruções"
            ],
            "what_is": [
                # English patterns
                r"what is", r"what are", r"define", r"definition", r"explain",
                r"meaning of", r"concept of",
                # Portuguese patterns
                r"o que é", r"o que são", r"definir", r"definição", r"explicar",
                r"significado de", r"conceito de"
            ],
            "examples": [
                # English patterns
                r"example", r"sample", r"demo", r"demonstration", r"show me",
                r"code example", r"usage example",
                # Portuguese patterns
                r"exemplo", r"amostra", r"demo", r"demonstração", r"mostre",
                r"exemplo de código", r"exemplo de uso"
            ],
            "troubleshooting": [
                # English patterns
                r"error", r"bug", r"issue", r"problem", r"fix", r"resolve",
                r"debug", r"troubleshoot", r"not working",
                # Portuguese patterns
                r"erro", r"bug", r"problema", r"corrigir", r"resolver",
                r"debug", r"depurar", r"não funciona"
            ],
            "comparison": [
                # English patterns
                r"vs", r"versus", r"compare", r"difference", r"better",
                r"which is", r"pros and cons",
                # Portuguese patterns
                r"vs", r"versus", r"comparar", r"diferença", r"melhor",
                r"qual é", r"prós e contras"
            ],
            "best_practices": [
                # English patterns
                r"best practice", r"recommended", r"optimal", r"efficient",
                r"good practice", r"standard", r"convention",
                # Portuguese patterns
                r"melhor prática", r"recomendado", r"ótimo", r"eficiente",
                r"boa prática", r"padrão", r"convenção"
            ],
            "implementation": [
                # English patterns
                r"implement", r"build", r"create", r"develop", r"setup",
                r"install", r"configure", r"deploy",
                # Portuguese patterns
                r"implementar", r"construir", r"criar", r"desenvolver", r"configurar",
                r"instalar", r"configurar", r"deploy"
            ]
        }
    
    def analyze_query_intent(self, query: str) -> str:
        """Analyze query intent based on patterns"""
        query_lower = query.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return "general"
    
    def extract_entities(self, query: str) -> List[str]:
        """Extract key entities from the query"""
        entities = []
        query_lower = query.lower()
        
        # Extract technical terms from synonym library
        for term, synonyms in self.synonym_library.items():
            if term in query_lower:
                entities.append(term)
            else:
                for synonym in synonyms:
                    if synonym in query_lower:
                        entities.append(term)
                        break
        
        # Extract expansion terms
        for expansion_term in self.expansion_rules.keys():
            if expansion_term in query_lower:
                entities.append(expansion_term)
        
        return list(set(entities))  # Remove duplicates
    
    def rule_based_expansion(self, query: str) -> Tuple[str, float]:
        """Expand query using rule-based patterns"""
        expanded_query = query
        expansion_count = 0
        
        # Apply expansion rules
        for pattern, expansion in self.expansion_rules.items():
            if pattern in query.lower():
                expanded_query = expanded_query.replace(pattern, expansion)
                expansion_count += 1
        
        # Apply synonym expansion
        for term, synonyms in self.synonym_library.items():
            if term in query.lower():
                # Add synonyms if not already present
                for synonym in synonyms:
                    if synonym not in expanded_query.lower():
                        expanded_query += f", {synonym}"
                        expansion_count += 1
        
        # Calculate confidence based on number of expansions
        confidence = min(0.9, 0.3 + (expansion_count * 0.1))
        
        return expanded_query, confidence
    
    async def llm_based_expansion(self, query: str) -> Tuple[str, float]:
        """Expand query using LLM (Gemini)"""
        if not self.gemini_model:
            logger.warning("LLM model not available, falling back to rule-based expansion")
            return self.rule_based_expansion(query)
        
        try:
            prompt = f"""
            Expand and enhance the following search query to make it more comprehensive and specific. 
            Add relevant synonyms, related terms, and context to improve search results.
            
            Original query: "{query}"
            
            Please provide:
            1. An expanded query with synonyms and related terms
            2. A brief explanation of the expansion reasoning
            
            Format your response as:
            EXPANDED: [expanded query]
            REASONING: [brief explanation]
            """
            
            response = await asyncio.to_thread(
                self.gemini_model.generate_content, prompt
            )
            
            response_text = response.text.strip()
            
            # Parse the response
            if "EXPANDED:" in response_text and "REASONING:" in response_text:
                expanded_part = response_text.split("EXPANDED:")[1].split("REASONING:")[0].strip()
                reasoning_part = response_text.split("REASONING:")[1].strip()
                
                # Clean up the expanded query
                expanded_query = expanded_part.replace("[", "").replace("]", "").strip()
                
                # Calculate confidence based on response quality
                confidence = 0.8 if len(expanded_query) > len(query) * 1.5 else 0.6
                
                return expanded_query, confidence
            else:
                # Fallback if parsing fails
                logger.warning("Failed to parse LLM response, using original query")
                return query, 0.3
                
        except Exception as e:
            logger.error(f"LLM expansion failed: {e}")
            return self.rule_based_expansion(query)
    
    def hybrid_expansion(self, query: str, rule_confidence: float, llm_confidence: float) -> Tuple[str, float]:
        """Combine rule-based and LLM-based expansions"""
        # Use the expansion with higher confidence
        if llm_confidence > rule_confidence:
            return self.llm_based_expansion(query)
        else:
            return self.rule_based_expansion(query)
    
    async def expand_query(self, query: str, strategy: ExpansionStrategy = ExpansionStrategy.HYBRID) -> QueryAnalysis:
        """Main method to expand and analyze a query"""
        logger.info(f"Expanding query: '{query}' using strategy: {strategy.value}")
        
        # Analyze query components
        intent = self.analyze_query_intent(query)
        entities = self.extract_entities(query)
        
        # Perform expansion based on strategy
        if strategy == ExpansionStrategy.RULE_BASED:
            expanded_query, confidence = self.rule_based_expansion(query)
            reasoning = "Rule-based expansion using synonym library and expansion patterns"
        elif strategy == ExpansionStrategy.LLM_BASED:
            expanded_query, confidence = await self.llm_based_expansion(query)
            reasoning = "LLM-based expansion using Gemini model"
        else:  # HYBRID
            rule_expanded, rule_conf = self.rule_based_expansion(query)
            llm_expanded, llm_conf = await self.llm_based_expansion(query)
            
            if llm_conf > rule_conf:
                expanded_query, confidence = llm_expanded, llm_conf
                reasoning = f"Hybrid expansion: LLM-based (confidence: {llm_conf:.2f})"
            else:
                expanded_query, confidence = rule_expanded, rule_conf
                reasoning = f"Hybrid expansion: Rule-based (confidence: {rule_conf:.2f})"
        
        # Create analysis result
        analysis = QueryAnalysis(
            original_query=query,
            expanded_query=expanded_query,
            intent=intent,
            entities=entities,
            expansion_confidence=confidence,
            strategy_used=strategy,
            expansion_reasoning=reasoning
        )
        
        logger.info(f"Query expansion complete: '{query}' → '{expanded_query}' (confidence: {confidence:.2f})")
        return analysis
    
    def get_expansion_suggestions(self, query: str) -> List[str]:
        """Get expansion suggestions for a query without applying them"""
        suggestions = []
        
        # Get rule-based suggestions
        for pattern, expansion in self.expansion_rules.items():
            if pattern in query.lower():
                suggestions.append(f"Add '{expansion}' for '{pattern}'")
        
        # Get synonym suggestions
        for term, synonyms in self.synonym_library.items():
            if term in query.lower():
                for synonym in synonyms:
                    if synonym not in query.lower():
                        suggestions.append(f"Add '{synonym}' as synonym for '{term}'")
        
        return suggestions[:5]  # Limit to 5 suggestions

# Example usage and testing
async def test_query_expansion():
    """Test the query expansion service"""
    service = QueryExpansionService()
    
    test_queries = [
        "Python tips",
        "how to debug React",
        "machine learning examples",
        "API security",
        "docker setup"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing: '{query}' ---")
        
        # Test rule-based expansion
        analysis = await service.expand_query(query, ExpansionStrategy.RULE_BASED)
        print(f"Rule-based: '{analysis.expanded_query}'")
        print(f"Intent: {analysis.intent}")
        print(f"Entities: {analysis.entities}")
        print(f"Confidence: {analysis.expansion_confidence:.2f}")
        
        # Test LLM-based expansion (if available)
        if service.gemini_model:
            analysis_llm = await service.expand_query(query, ExpansionStrategy.LLM_BASED)
            print(f"LLM-based: '{analysis_llm.expanded_query}'")
            print(f"Confidence: {analysis_llm.expansion_confidence:.2f}")

if __name__ == "__main__":
    asyncio.run(test_query_expansion())
