#!/usr/bin/env python3
"""
Agentic RAG CLI - Interactive Vector Database Reasoning with Gemini Flash
Advanced CLI system for agentic retrieval-augmented generation with vector database integration
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agentic-rag-cli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgenticRAGCLI:
    """Interactive CLI for Agentic RAG with Vector Database Reasoning"""
    
    def __init__(self):
        self.project_root = project_root
        self.vector_db_path = self.project_root / "data" / "chroma"
        self.obsidian_vault_path = self.project_root / "data" / "raw" / "vault"
        self.mcp_server_url = None  # MCP disabled
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.session_id = f"rag_session_{int(time.time())}"
        self.conversation_history = []
        self.context_cache = {}
        self.conversation_chains = []
        self.current_chain = None
        self.query_intent = None
        self.follow_up_suggestions = []
        
        # Initialize components
        self.setup_environment()
        self.initialize_components()
        
    def setup_environment(self):
        """Setup environment and create necessary directories"""
        # Create logs directory
        (self.project_root / "logs").mkdir(exist_ok=True)
        
        # Create temp directory for active scripts
        temp_dir = self.project_root / "scripts" / "temp" / "agentic-rag"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ["CHROMA_PERSIST_DIRECTORY"] = str(self.vector_db_path)
        os.environ["OBSIDIAN_VAULT_PATH"] = str(self.obsidian_vault_path)
        
    def initialize_components(self):
        """Initialize vector database and other components"""
        try:
            # Initialize ChromaDB with updated configuration
            import chromadb
            from chromadb.config import Settings
            
            # Use the new configuration format to avoid deprecation warnings
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.vector_db_path)
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="obsidian_notes",
                metadata={"description": "Obsidian vault notes for RAG"}
            )
            
            logger.info(f"Vector database initialized with {self.collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            self.chroma_client = None
            self.collection = None
    
    async def start_interactive_session(self):
        """Start the interactive CLI session"""
        print("🚀 Agentic RAG CLI - Interactive Vector Database Reasoning")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Vector DB: {self.vector_db_path}")
        print(f"Obsidian Vault: {self.obsidian_vault_path}")
        print("=" * 60)
        
        # Check system health
        await self.check_system_health()
        
        # Main interactive loop
        while True:
            try:
                # Display prompt
                self.display_prompt()
                
                # Get user input with proper EOF handling
                try:
                    user_input = input().strip()
                except EOFError:
                    print("\n👋 Input stream closed. Goodbye!")
                    break
                except KeyboardInterrupt:
                    print("\n👋 Interrupted by user. Goodbye!")
                    break
                
                if not user_input:
                    continue
                    
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye! Session saved.")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'status':
                    await self.show_status()
                    continue
                elif user_input.lower() == 'clear':
                    self.conversation_history.clear()
                    self.conversation_chains.clear()
                    self.current_chain = None
                    print("🧹 Conversation history and chains cleared.")
                    continue
                elif user_input.lower() == 'chains':
                    self.show_conversation_chains()
                    continue
                elif user_input.lower().startswith('chain '):
                    await self.switch_to_chain(user_input[6:])
                    continue
                elif user_input.lower().startswith('load '):
                    await self.load_documents(user_input[5:])
                    continue
                elif user_input.lower().startswith('search '):
                    await self.search_documents(user_input[7:])
                    continue
                elif user_input.lower().startswith('reason '):
                    await self.reason_with_gemini(user_input[7:])
                    continue
                elif user_input.lower().startswith('rag '):
                    await self.rag_query(user_input[4:])
                    continue
                elif user_input.lower().startswith('follow '):
                    await self.handle_follow_up(user_input[7:])
                    continue
                # elif user_input.lower().startswith('mcp '):
                #     await self.mcp_query(user_input[4:])  # MCP disabled
                #     continue
                else:
                    # Default to conversational RAG query
                    await self.conversational_rag_query(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Session saved.")
                break
            except Exception as e:
                logger.error(f"Error in interactive session: {e}")
                print(f"❌ Error: {e}")
    
    def display_prompt(self):
        """Display the interactive prompt"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 🤖 RAG> ", end="", flush=True)
    
    def show_help(self):
        """Show help information"""
        help_text = """
🔧 Agentic RAG CLI Commands:

📚 Document Management:
  load <path>           Load documents from path into vector database
  search <query>        Search documents in vector database
  status                Show system status and metrics

🧠 Reasoning & RAG:
  reason <query>        Use Gemini Flash for pure reasoning
  rag <query>           Full RAG pipeline with vector search + Gemini
  <query>               Conversational RAG (default mode)

💬 Conversational Features:
  chains                Show conversation chains
  chain <name>          Switch to specific conversation chain
  follow <number>       Follow up on suggestion by number
  clear                 Clear conversation history and chains

🛠️ System Commands:
  help                  Show this help message
  status                Show system status
  exit/quit/q          Exit the CLI

💡 Examples:
  load docs/architecture/
  search "authentication patterns"
  reason "How should I implement JWT authentication?"
  rag "What are the best practices for API security?"
  
  # Conversational mode (default):
  "How do I implement JWT authentication?"
  "What are the security considerations?"
  "Can you show me a code example?"
  
  # Chain management:
  chains
  chain "authentication_discussion"
  follow 1
        """
        print(help_text)
    
    async def check_system_health(self):
        """Check system health and dependencies"""
        print("🔍 Checking system health...")
        
        # Check vector database
        if self.collection:
            doc_count = self.collection.count()
            print(f"✅ Vector Database: {doc_count} documents")
        else:
            print("❌ Vector Database: Not available")
        
        # Check MCP server (disabled)
        # try:
        #     import httpx
        #     async with httpx.AsyncClient() as client:
        #         response = await client.get(f"{self.mcp_server_url}/health", timeout=5.0)
        #         if response.status_code == 200:
        #             print("✅ MCP Server: Available")
        #         else:
        #             print("⚠️ MCP Server: Responding but unhealthy")
        # except Exception as e:
        #     print(f"❌ MCP Server: Not available ({e})")
        print("ℹ️ MCP Server: Disabled")
        
        # Check Gemini API key
        if self.gemini_api_key:
            print("✅ Gemini API: Key configured")
        else:
            print("⚠️ Gemini API: Key not configured (set GEMINI_API_KEY)")
        
        # Check Obsidian vault
        if self.obsidian_vault_path.exists():
            vault_files = list(self.obsidian_vault_path.rglob("*.md"))
            print(f"✅ Obsidian Vault: {len(vault_files)} markdown files")
        else:
            print("❌ Obsidian Vault: Not found")
    
    async def show_status(self):
        """Show current system status"""
        print("\n📊 System Status:")
        print("-" * 40)
        
        # Vector database status
        if self.collection:
            doc_count = self.collection.count()
            print(f"Vector Database: {doc_count} documents")
        else:
            print("Vector Database: Not available")
        
        # Conversation history
        print(f"Conversation History: {len(self.conversation_history)} messages")
        
        # Context cache
        print(f"Context Cache: {len(self.context_cache)} items")
        
        # Session info
        print(f"Session ID: {self.session_id}")
        print(f"Project Root: {self.project_root}")
    
    async def load_documents(self, path: str):
        """Load documents from path into vector database"""
        print(f"📚 Loading documents from: {path}")
        
        try:
            # Resolve path
            if not os.path.isabs(path):
                path = str(self.project_root / path)
            
            path_obj = Path(path)
            if not path_obj.exists():
                print(f"❌ Path not found: {path}")
                return
            
            # Find markdown files
            md_files = list(path_obj.rglob("*.md"))
            if not md_files:
                print(f"❌ No markdown files found in: {path}")
                return
            
            print(f"Found {len(md_files)} markdown files")
            
            # Process files
            documents = []
            metadatas = []
            ids = []
            
            for i, file_path in enumerate(md_files):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create metadata
                    metadata = {
                        "source": str(file_path.relative_to(self.project_root)),
                        "filename": file_path.name,
                        "directory": str(file_path.parent.relative_to(self.project_root)),
                        "size": len(content),
                        "loaded_at": datetime.now().isoformat()
                    }
                    
                    documents.append(content)
                    metadatas.append(metadata)
                    ids.append(f"doc_{i}_{file_path.stem}")
                    
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")
                    continue
            
            if not documents:
                print("❌ No documents could be loaded")
                return
            
            # Add to vector database
            print(f"Adding {len(documents)} documents to vector database...")
            
            # Generate embeddings (simplified - in production, use proper embedding model)
            embeddings = [[0.1] * 384 for _ in documents]  # Placeholder embeddings
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Successfully loaded {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            print(f"❌ Error loading documents: {e}")
    
    async def search_documents(self, query: str):
        """Search documents in vector database"""
        print(f"🔍 Searching for: {query}")
        
        try:
            if not self.collection:
                print("❌ Vector database not available")
                return
            
            # Search in vector database
            results = self.collection.query(
                query_texts=[query],
                n_results=5
            )
            
            if not results['documents'] or not results['documents'][0]:
                print("❌ No documents found")
                return
            
            print(f"Found {len(results['documents'][0])} relevant documents:")
            print("-" * 50)
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                print(f"\n📄 Result {i+1} (similarity: {1-distance:.3f}):")
                print(f"   File: {metadata.get('source', 'Unknown')}")
                print(f"   Preview: {doc[:200]}...")
                
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            print(f"❌ Error searching documents: {e}")
    
    async def reason_with_gemini(self, query: str):
        """Use Gemini Flash for pure reasoning"""
        print(f"🧠 Reasoning with Gemini Flash: {query}")
        
        try:
            if not self.gemini_api_key:
                print("❌ Gemini API key not configured")
                return
            
            # Prepare context from conversation history
            context = self.build_context()
            
            # Create reasoning prompt
            prompt = f"""
You are an expert software engineer and technical advisor. Use your knowledge to provide detailed, actionable reasoning for the following query.

Context from previous conversation:
{context}

Query: {query}

Please provide:
1. Analysis of the problem
2. Multiple solution approaches
3. Trade-offs and considerations
4. Recommended approach with justification
5. Implementation considerations

Be specific, technical, and actionable.
"""
            
            # Call Gemini API (simplified - in production, use proper API client)
            print("🤖 Calling Gemini Flash...")
            
            # Simulate API call (replace with actual Gemini API call)
            response = await self.simulate_gemini_call(prompt)
            
            print("\n💡 Gemini Flash Response:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
            # Store in conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "reasoning",
                "query": query,
                "response": response
            })
            
        except Exception as e:
            logger.error(f"Failed to reason with Gemini: {e}")
            print(f"❌ Error reasoning with Gemini: {e}")
    
    async def conversational_rag_query(self, query: str):
        """Enhanced conversational RAG with chain management and dynamic responses"""
        print(f"💬 Conversational Query: {query}")
        print("=" * 60)
        
        try:
            # Analyze query intent and context
            self.query_intent = self.analyze_query_intent(query)
            print(f"🎯 Detected Intent: {self.query_intent}")
            
            # Check if this continues an existing chain
            if self.current_chain and self.is_chain_continuation(query):
                print(f"🔗 Continuing chain: {self.current_chain['name']}")
                await self.continue_conversation_chain(query)
            else:
                # Start new conversation or chain
                await self.start_new_conversation(query)
            
        except Exception as e:
            logger.error(f"Failed conversational RAG query: {e}")
            print(f"❌ Error in conversational query: {e}")
    
    async def rag_query(self, query: str):
        """Full RAG pipeline with vector search + Gemini"""
        print(f"🔍 RAG Query: {query}")
        print("=" * 60)
        
        try:
            # Step 1: Search vector database with detailed logging
            print("📚 Searching vector database...")
            print("🔍 Vector Search Details:")
            print("-" * 40)
            
            relevant_docs = await self.search_vector_db(query)
            
            if not relevant_docs:
                print("❌ No relevant documents found in vector database")
                print("💡 Try loading documents first with 'load <directory>'")
                return
            
            # Step 2: Build context
            print("\n🧠 Building context from retrieved documents...")
            context = self.build_rag_context(query, relevant_docs)
            
            # Step 3: Generate response with Gemini
            print("🤖 Generating response with Gemini Flash...")
            print("💭 Processing query with AI reasoning...")
            
            response = await self.generate_rag_response(query, context)
            
            print("\n💡 RAG Response:")
            print("=" * 60)
            print(response)
            print("=" * 60)
            
            # Store in conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "rag",
                "query": query,
                "context_docs": len(relevant_docs),
                "response": response
            })
            
            # Show follow-up suggestions
            print("\n💬 Follow-up suggestions:")
            print("   • Ask for more details about any specific point")
            print("   • Request code examples or implementation details")
            print("   • Ask related questions to explore the topic further")
            print("   • Use 'search <term>' to find more specific information")
            
        except Exception as e:
            logger.error(f"Failed RAG query: {e}")
            print(f"❌ Error in RAG query: {e}")
    
    # async def mcp_query(self, query: str):
    #     """Use MCP servers for enhanced capabilities (disabled)"""
    #     print(f"🔧 MCP Query: {query}")
    #     
    #     try:
    #         import httpx
    #         
    #         # Check available MCP servers
    #         async with httpx.AsyncClient() as client:
    #             response = await client.get(f"{self.mcp_server_url}/mcp/servers")
    #             if response.status_code != 200:
    #                 print("❌ MCP server not available")
    #                 return
    #             
    #             servers = response.json()["servers"]
    #             print(f"Available MCP servers: {', '.join(servers)}")
    #             
    #             # Use first available server (simplified)
    #             if servers:
    #                 server_name = servers[0]
    #                 print(f"Using MCP server: {server_name}")
    #                 
    #                 # Call MCP tool
    #                 mcp_request = {
    #                     "server_name": server_name,
    #                     "tool_name": "search_notes",  # Example tool
    #                     "arguments": {"query": query}
    #                 }
    #                 
    #                 response = await client.post(
    #                     f"{self.mcp_server_url}/mcp/call",
    #                     json=mcp_request
    #                 )
    #                 
    #                 if response.status_code == 200:
    #                     result = response.json()
    #                     print("\n🔧 MCP Response:")
    #                     print("=" * 50)
    #                     print(json.dumps(result, indent=2))
    #                     print("=" * 50)
    #                 else:
    #                     print(f"❌ MCP call failed: {response.text}")
    #             else:
    #                 print("❌ No MCP servers available")
    #                 
    #     except Exception as e:
    #         logger.error(f"Failed MCP query: {e}")
    #         print(f"❌ Error in MCP query: {e}")
    
    async def search_vector_db(self, query: str) -> List[Dict[str, Any]]:
        """Search vector database and return relevant documents with detailed logging"""
        if not self.collection:
            print("❌ Vector database collection not available")
            return []
        
        try:
            print(f"🔍 Query: '{query}'")
            print(f"📊 Searching for top 5 most similar documents...")
            
            results = self.collection.query(
                query_texts=[query],
                n_results=5
            )
            
            relevant_docs = []
            if results['documents'] and results['documents'][0]:
                print(f"✅ Found {len(results['documents'][0])} documents")
                print("\n📋 Search Results:")
                print("-" * 50)
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    similarity = 1 - distance
                    title = metadata.get('title', 'Untitled')
                    source = metadata.get('source', 'Unknown')
                    size = metadata.get('size', 0)
                    
                    print(f"📄 Result {i+1}:")
                    print(f"   📝 Title: {title}")
                    print(f"   📁 Source: {source}")
                    print(f"   📏 Size: {size} characters")
                    print(f"   🎯 Similarity: {similarity:.3f} ({similarity*100:.1f}%)")
                    print(f"   📏 Distance: {distance:.3f}")
                    print(f"   👀 Preview: {doc[:150]}...")
                    print()
                    
                    relevant_docs.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity": similarity,
                        "distance": distance
                    })
            else:
                print("❌ No documents found in vector database")
                print("💡 Try loading documents first with 'load <directory>'")
            
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Failed to search vector database: {e}")
            print(f"❌ Error searching vector database: {e}")
            return []
    
    def build_context(self) -> str:
        """Build context from conversation history"""
        if not self.conversation_history:
            return "No previous context available."
        
        context_parts = []
        for entry in self.conversation_history[-5:]:  # Last 5 entries
            context_parts.append(f"[{entry['type']}] {entry['query']}: {entry['response'][:200]}...")
        
        return "\n".join(context_parts)
    
    def build_rag_context(self, query: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """Build context for RAG from relevant documents"""
        context_parts = [f"Query: {query}\n"]
        
        if relevant_docs:
            context_parts.append("Relevant Documents:")
            for i, doc in enumerate(relevant_docs, 1):
                context_parts.append(f"\nDocument {i} (similarity: {doc['similarity']:.3f}):")
                context_parts.append(f"Source: {doc['metadata'].get('source', 'Unknown')}")
                context_parts.append(f"Content: {doc['content'][:500]}...")
        else:
            context_parts.append("No relevant documents found in vector database.")
        
        return "\n".join(context_parts)
    
    async def generate_rag_response(self, query: str, context: str) -> str:
        """Generate RAG response using Gemini with dynamic prompts"""
        if not self.gemini_api_key:
            return "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        
        # Dynamic prompt generation based on query type
        prompt = self.generate_dynamic_prompt(query, context)
        
        # Simulate Gemini API call (replace with actual implementation)
        return await self.simulate_gemini_call(prompt)
    
    def analyze_query_intent(self, query: str) -> str:
        """Analyze query intent for conversational flow"""
        query_lower = query.lower()
        
        # Intent detection patterns
        if any(word in query_lower for word in ['how', 'implement', 'create', 'build', 'develop', 'make']):
            return "implementation"
        elif any(word in query_lower for word in ['what', 'explain', 'describe', 'define', 'tell me about']):
            return "explanation"
        elif any(word in query_lower for word in ['why', 'reason', 'rationale', 'justify', 'because']):
            return "analysis"
        elif any(word in query_lower for word in ['fix', 'debug', 'error', 'problem', 'issue', 'troubleshoot']):
            return "troubleshooting"
        elif any(word in query_lower for word in ['best', 'practice', 'recommend', 'suggest', 'should i']):
            return "recommendation"
        elif any(word in query_lower for word in ['show', 'example', 'code', 'demo', 'sample']):
            return "demonstration"
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference', 'better']):
            return "comparison"
        elif any(word in query_lower for word in ['when', 'where', 'which', 'who']):
            return "clarification"
        else:
            return "general"
    
    def is_chain_continuation(self, query: str) -> bool:
        """Check if query continues current conversation chain"""
        if not self.current_chain:
            return False
        
        # Simple continuation detection
        continuation_words = ['also', 'and', 'furthermore', 'additionally', 'moreover', 'besides', 'what about', 'how about']
        query_lower = query.lower()
        
        return any(word in query_lower for word in continuation_words) or len(self.current_chain['messages']) > 0
    
    async def start_new_conversation(self, query: str):
        """Start a new conversation or chain"""
        # Search vector database with detailed logging
        print("📚 Searching vector database...")
        print("🔍 Vector Search Details:")
        print("-" * 40)
        
        relevant_docs = await self.search_vector_db(query)
        
        if not relevant_docs:
            print("❌ No relevant documents found in vector database")
            print("💡 Try loading documents first with 'load <directory>'")
            return
        
        # Build enhanced context
        print("\n🧠 Building conversational context...")
        context = self.build_conversational_context(query, relevant_docs)
        
        # Generate dynamic response
        print("🤖 Generating conversational response...")
        response = await self.generate_conversational_response(query, context)
        
        print("\n💡 Response:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        
        # Create or update conversation chain
        chain_name = self.generate_chain_name(query)
        if not self.current_chain or self.current_chain['name'] != chain_name:
            self.current_chain = {
                'name': chain_name,
                'topic': self.extract_topic(query),
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
            self.conversation_chains.append(self.current_chain)
        
        # Add to chain
        self.current_chain['messages'].append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'intent': self.query_intent
        })
        
        # Store in conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "conversational_rag",
            "query": query,
            "context_docs": len(relevant_docs),
            "response": response,
            "chain": chain_name
        })
        
        # Generate follow-up suggestions
        self.follow_up_suggestions = self.generate_follow_up_suggestions(query, self.query_intent)
        self.show_follow_up_suggestions()
    
    async def continue_conversation_chain(self, query: str):
        """Continue existing conversation chain"""
        print(f"🔗 Continuing chain: {self.current_chain['name']}")
        
        # Get chain context
        chain_context = self.build_chain_context()
        
        # Search for relevant documents
        print("📚 Searching vector database...")
        relevant_docs = await self.search_vector_db(query)
        
        # Build enhanced context with chain history
        context = self.build_conversational_context(query, relevant_docs, chain_context)
        
        # Generate response
        print("🤖 Generating chain response...")
        response = await self.generate_conversational_response(query, context)
        
        print("\n💡 Chain Response:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        
        # Add to chain
        self.current_chain['messages'].append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'intent': self.query_intent
        })
        
        # Generate follow-up suggestions
        self.follow_up_suggestions = self.generate_follow_up_suggestions(query, self.query_intent)
        self.show_follow_up_suggestions()
    
    def generate_chain_name(self, query: str) -> str:
        """Generate a meaningful chain name from query"""
        # Extract key topic words
        words = query.lower().split()
        topic_words = [w for w in words if len(w) > 3 and w not in ['what', 'how', 'why', 'when', 'where', 'tell', 'me', 'about', 'the', 'and', 'or', 'but']]
        
        if topic_words:
            return f"{topic_words[0]}_discussion"
        else:
            return f"conversation_{len(self.conversation_chains) + 1}"
    
    def extract_topic(self, query: str) -> str:
        """Extract main topic from query"""
        # Simple topic extraction
        words = query.lower().split()
        topic_words = [w for w in words if len(w) > 3 and w not in ['what', 'how', 'why', 'when', 'where', 'tell', 'me', 'about', 'the', 'and', 'or', 'but']]
        return ' '.join(topic_words[:3]) if topic_words else "general discussion"
    
    def build_chain_context(self) -> str:
        """Build context from current conversation chain"""
        if not self.current_chain or not self.current_chain['messages']:
            return ""
        
        context_parts = [f"Conversation Chain: {self.current_chain['name']}"]
        context_parts.append(f"Topic: {self.current_chain['topic']}")
        context_parts.append("Previous Messages:")
        
        for i, msg in enumerate(self.current_chain['messages'][-3:], 1):  # Last 3 messages
            context_parts.append(f"  {i}. Q: {msg['query']}")
            context_parts.append(f"     A: {msg['response'][:200]}...")
        
        return "\n".join(context_parts)
    
    def build_conversational_context(self, query: str, relevant_docs: List[Dict[str, Any]], chain_context: str = "") -> str:
        """Build enhanced context for conversational responses"""
        context_parts = [f"Query: {query}"]
        context_parts.append(f"Intent: {self.query_intent}")
        
        if chain_context:
            context_parts.append(f"\nChain Context:\n{chain_context}")
        
        if relevant_docs:
            context_parts.append("\nRelevant Documents:")
            for i, doc in enumerate(relevant_docs, 1):
                context_parts.append(f"\nDocument {i} (similarity: {doc['similarity']:.3f}):")
                context_parts.append(f"Source: {doc['metadata'].get('source', 'Unknown')}")
                context_parts.append(f"Content: {doc['content'][:300]}...")
        else:
            context_parts.append("\nNo relevant documents found in vector database.")
        
        return "\n".join(context_parts)
    
    def generate_follow_up_suggestions(self, query: str, intent: str) -> List[str]:
        """Generate contextual follow-up suggestions"""
        suggestions = []
        
        if intent == "implementation":
            suggestions = [
                "Show me a code example",
                "What are the security considerations?",
                "How do I test this implementation?",
                "What are the performance implications?",
                "Are there any common pitfalls to avoid?"
            ]
        elif intent == "explanation":
            suggestions = [
                "Can you provide a real-world example?",
                "How does this relate to [related concept]?",
                "What are the key benefits?",
                "Are there any alternatives?",
                "What should I learn next?"
            ]
        elif intent == "troubleshooting":
            suggestions = [
                "What are other potential causes?",
                "How can I prevent this in the future?",
                "Are there monitoring tools I should use?",
                "What's the escalation path?",
                "Can you show me how to debug this?"
            ]
        elif intent == "recommendation":
            suggestions = [
                "What are the trade-offs?",
                "How do I implement this?",
                "What are the alternatives?",
                "What's the timeline?",
                "How do I measure success?"
            ]
        else:
            suggestions = [
                "Can you elaborate on that?",
                "What are the next steps?",
                "How does this work?",
                "What should I consider?",
                "Are there any examples?"
            ]
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def show_follow_up_suggestions(self):
        """Display follow-up suggestions"""
        if not self.follow_up_suggestions:
            return
        
        print("\n💬 Follow-up suggestions:")
        for i, suggestion in enumerate(self.follow_up_suggestions, 1):
            print(f"   {i}. {suggestion}")
        print("   • Use 'follow <number>' to ask a suggestion")
        print("   • Or just ask your own question")
    
    async def handle_follow_up(self, suggestion_number: str):
        """Handle follow-up suggestion selection"""
        try:
            index = int(suggestion_number) - 1
            if 0 <= index < len(self.follow_up_suggestions):
                suggestion = self.follow_up_suggestions[index]
                print(f"💬 Following up: {suggestion}")
                await self.conversational_rag_query(suggestion)
            else:
                print("❌ Invalid suggestion number")
        except ValueError:
            print("❌ Please provide a valid number")
    
    def show_conversation_chains(self):
        """Show available conversation chains"""
        if not self.conversation_chains:
            print("📝 No conversation chains available")
            return
        
        print("🔗 Available Conversation Chains:")
        print("-" * 50)
        for i, chain in enumerate(self.conversation_chains, 1):
            status = " (current)" if chain == self.current_chain else ""
            print(f"{i}. {chain['name']}{status}")
            print(f"   Topic: {chain['topic']}")
            print(f"   Messages: {len(chain['messages'])}")
            print(f"   Created: {chain['created_at']}")
            print()
    
    async def switch_to_chain(self, chain_name: str):
        """Switch to a specific conversation chain"""
        chain = next((c for c in self.conversation_chains if c['name'] == chain_name), None)
        if chain:
            self.current_chain = chain
            print(f"🔗 Switched to chain: {chain_name}")
            print(f"📝 Topic: {chain['topic']}")
            print(f"💬 Messages: {len(chain['messages'])}")
        else:
            print(f"❌ Chain '{chain_name}' not found")
            print("💡 Use 'chains' to see available chains")

    def analyze_query_intent(self, query: str) -> str:
        """Analyze query intent for conversational flow"""
        query_lower = query.lower()
        
        # Intent detection patterns
        if any(word in query_lower for word in ['how', 'implement', 'create', 'build', 'develop', 'make']):
            return "implementation"
        elif any(word in query_lower for word in ['what', 'explain', 'describe', 'define', 'tell me about']):
            return "explanation"
        elif any(word in query_lower for word in ['why', 'reason', 'rationale', 'justify', 'because']):
            return "analysis"
        elif any(word in query_lower for word in ['fix', 'debug', 'error', 'problem', 'issue', 'troubleshoot']):
            return "troubleshooting"
        elif any(word in query_lower for word in ['best', 'practice', 'recommend', 'suggest', 'advice']):
            return "recommendation"
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference', 'contrast']):
            return "comparison"
        else:
            return "general"
    
    def generate_dynamic_prompt(self, query: str, context: str, intent: str = "general") -> str:
        """Generate dynamic prompts based on query type and context"""
        
        # Base system prompt
        base_prompt = f"""You are an expert AI assistant with access to a comprehensive knowledge base. 
You excel at providing detailed, actionable responses based on the provided context.

Query: {query}
Context: {context}

"""
        
        # Intent-specific prompts
        if intent == "implementation":
            return base_prompt + """
Focus on providing step-by-step implementation guidance:
- Break down the solution into clear, actionable steps
- Include code examples and best practices
- Address potential challenges and edge cases
- Suggest testing and validation approaches
- Consider scalability and maintainability
"""
        elif intent == "explanation":
            return base_prompt + """
Focus on clear, comprehensive explanations:
- Define key concepts and terminology
- Provide context and background information
- Use examples and analogies to clarify complex topics
- Address common misconceptions
- Suggest related topics for deeper understanding
"""
        elif intent == "analysis":
            return base_prompt + """
Focus on analytical reasoning and insights:
- Examine the underlying principles and mechanisms
- Identify patterns, trends, and relationships
- Provide evidence-based reasoning
- Consider multiple perspectives and viewpoints
- Highlight implications and consequences
"""
        elif intent == "troubleshooting":
            return base_prompt + """
Focus on problem-solving and debugging:
- Identify potential root causes
- Provide systematic debugging approaches
- Suggest diagnostic steps and tools
- Offer multiple solution strategies
- Include prevention strategies for the future
"""
        elif intent == "recommendation":
            return base_prompt + """
Focus on best practices and recommendations:
- Evaluate different options and approaches
- Consider trade-offs and constraints
- Provide evidence-based recommendations
- Include implementation considerations
- Suggest monitoring and evaluation criteria
"""
        elif intent == "comparison":
            return base_prompt + """
Focus on comparative analysis:
- Highlight key differences and similarities
- Evaluate pros and cons of each option
- Consider use cases and contexts
- Provide decision-making criteria
- Suggest when to use each approach
"""
        else:
            return base_prompt + """
Provide a comprehensive, well-structured response that:
- Directly addresses the query
- Leverages the provided context effectively
- Offers practical, actionable insights
- Considers multiple perspectives
- Suggests next steps or follow-up questions
"""
    
    def create_conversational_chain(self, chain_name: str, initial_message: str = None) -> str:
        """Create a new conversational chain"""
        if chain_name in self.conversational_chains:
            return f"❌ Chain '{chain_name}' already exists"
        
        self.conversational_chains[chain_name] = {
            "messages": [],
            "created_at": time.time(),
            "last_updated": time.time()
        }
        
        if initial_message:
            self.conversational_chains[chain_name]["messages"].append({
                "role": "user",
                "content": initial_message,
                "timestamp": time.time()
            })
        
        return f"✅ Created chain '{chain_name}' with {len(self.conversational_chains[chain_name]['messages'])} messages"
    
    def add_to_chain(self, chain_name: str, message: str, role: str = "user") -> str:
        """Add a message to a conversational chain"""
        if chain_name not in self.conversational_chains:
            return f"❌ Chain '{chain_name}' not found"
        
        self.conversational_chains[chain_name]["messages"].append({
            "role": role,
            "content": message,
            "timestamp": time.time()
        })
        self.conversational_chains[chain_name]["last_updated"] = time.time()
        
        return f"✅ Added {role} message to chain '{chain_name}'"
    
    def get_chain_context(self, chain_name: str) -> str:
        """Get conversation context from a chain"""
        if chain_name not in self.conversational_chains:
            return ""
        
        context_parts = []
        for msg in self.conversational_chains[chain_name]["messages"][-5:]:  # Last 5 messages
            context_parts.append(f"{msg['role'].title()}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def list_conversational_chains(self) -> str:
        """List all conversational chains"""
        if not self.conversational_chains:
            return "📝 No conversational chains found"
        
        chains_info = []
        for name, chain in self.conversational_chains.items():
            age = time.time() - chain["created_at"]
            chains_info.append(f"🔗 {name}: {len(chain['messages'])} messages (created {age:.0f}s ago)")
        
        return "\n".join(chains_info)
    
    def show_chain_details(self, chain_name: str) -> str:
        """Show detailed information about a specific chain"""
        if chain_name not in self.conversational_chains:
            return f"❌ Chain '{chain_name}' not found"
        
        chain = self.conversational_chains[chain_name]
        details = [f"🔗 Chain: {chain_name}"]
        details.append(f"📊 Messages: {len(chain['messages'])}")
        details.append(f"⏰ Created: {time.ctime(chain['created_at'])}")
        details.append(f"🔄 Last Updated: {time.ctime(chain['last_updated'])}")
        details.append("\n💬 Recent Messages:")
        
        for i, msg in enumerate(chain["messages"][-3:], 1):
            details.append(f"  {i}. [{msg['role'].title()}] {msg['content'][:100]}...")
        
        return "\n".join(details)
    
    async def simulate_gemini_call(self, prompt: str) -> str:
        """Simulate Gemini API call with dynamic responses (replace with actual implementation)"""
        # This is a placeholder - in production, implement actual Gemini API call
        await asyncio.sleep(1)  # Simulate API delay
        
        # Extract query type from prompt for dynamic response
        query_type = "general"
        if "Query Type: Implementation" in prompt:
            query_type = "implementation"
        elif "Query Type: Explanation" in prompt:
            query_type = "explanation"
        elif "Query Type: Analysis" in prompt:
            query_type = "analysis"
        elif "Query Type: Troubleshooting" in prompt:
            query_type = "troubleshooting"
        elif "Query Type: Recommendation" in prompt:
            query_type = "recommendation"
        
        # Generate dynamic response based on query type
        if query_type == "implementation":
            return self.generate_implementation_response()
        elif query_type == "explanation":
            return self.generate_explanation_response()
        elif query_type == "analysis":
            return self.generate_analysis_response()
        elif query_type == "troubleshooting":
            return self.generate_troubleshooting_response()
        elif query_type == "recommendation":
            return self.generate_recommendation_response()
        else:
            return self.generate_general_response()
    
    def generate_implementation_response(self) -> str:
        """Generate implementation-focused response"""
        return """
🚀 **Implementation Guide**

Based on the context provided, here's a comprehensive implementation approach:

**Architecture Overview:**
- Clean separation of concerns
- Modular design for maintainability
- Scalable infrastructure considerations

**Step-by-Step Implementation:**

1. **Foundation Setup**
   - Initialize project structure
   - Configure development environment
   - Set up version control and CI/CD

2. **Core Development**
   - Implement business logic layer
   - Create data access layer
   - Build API endpoints

3. **Integration & Testing**
   - Unit tests for core functionality
   - Integration tests for API endpoints
   - End-to-end testing scenarios

4. **Deployment & Monitoring**
   - Production deployment strategy
   - Monitoring and logging setup
   - Performance optimization

**Code Example:**
```python
# Example implementation structure
class ServiceImplementation:
    def __init__(self, config):
        self.config = config
    
    async def process_request(self, data):
        # Implementation logic here
        pass
```

**Best Practices:**
- Follow SOLID principles
- Implement proper error handling
- Use dependency injection
- Write comprehensive tests

**Next Steps:**
- Review specific requirements
- Identify potential challenges
- Plan testing strategy
- Set up monitoring

Would you like me to dive deeper into any specific aspect of the implementation?
"""
    
    def generate_explanation_response(self) -> str:
        """Generate explanation-focused response"""
        return """
📚 **Comprehensive Explanation**

Let me break down this concept for you:

**Core Concept:**
The topic you're asking about is a fundamental aspect of modern software development that combines multiple disciplines and best practices.

**Key Components:**
1. **Theoretical Foundation** - Understanding the underlying principles
2. **Practical Application** - How it's used in real-world scenarios
3. **Best Practices** - Industry-standard approaches and patterns
4. **Common Pitfalls** - What to avoid and why

**Why It Matters:**
- Improves code quality and maintainability
- Reduces technical debt
- Enhances team productivity
- Enables better scalability

**Real-World Example:**
Consider a typical scenario where this concept applies:
- Problem: [Specific challenge]
- Solution: [How the concept addresses it]
- Result: [Benefits achieved]

**Related Concepts:**
- [Related topic 1] - How it connects
- [Related topic 2] - Complementary approaches
- [Related topic 3] - Advanced applications

**Learning Path:**
1. Start with the basics
2. Practice with simple examples
3. Apply to real projects
4. Explore advanced patterns

**Common Misconceptions:**
- [Misconception 1] - Why it's incorrect
- [Misconception 2] - The right approach
- [Misconception 3] - Best practices

Would you like me to elaborate on any specific aspect or provide more examples?
"""
    
    def generate_analysis_response(self) -> str:
        """Generate analysis-focused response"""
        return """
🔍 **Deep Analysis**

Let me provide a thorough analysis of this topic:

**Root Cause Analysis:**
The underlying factors driving this situation include:
- Technical constraints and limitations
- Business requirements and priorities
- Resource availability and allocation
- Timeline and delivery pressures

**Multiple Perspectives:**

**Technical Perspective:**
- Performance implications
- Scalability considerations
- Security requirements
- Maintainability factors

**Business Perspective:**
- Cost-benefit analysis
- Risk assessment
- Market positioning
- Competitive advantages

**User Perspective:**
- User experience impact
- Accessibility considerations
- Performance expectations
- Feature requirements

**Trade-off Analysis:**
| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Option A | [Benefits] | [Drawbacks] | [Use cases] |
| Option B | [Benefits] | [Drawbacks] | [Use cases] |
| Option C | [Benefits] | [Drawbacks] | [Use cases] |

**Risk Assessment:**
- **High Risk:** [Specific risks and mitigation]
- **Medium Risk:** [Moderate risks and strategies]
- **Low Risk:** [Minor concerns and monitoring]

**Long-term Implications:**
- Technical debt considerations
- Scalability requirements
- Maintenance overhead
- Future evolution paths

**Recommendations:**
Based on this analysis, I recommend [specific approach] because [justification].

Would you like me to explore any specific aspect in more detail?
"""
    
    def generate_troubleshooting_response(self) -> str:
        """Generate troubleshooting-focused response"""
        return """
🔧 **Troubleshooting Guide**

Let me help you systematically resolve this issue:

**Diagnostic Steps:**

1. **Initial Assessment**
   - Check system status and logs
   - Verify recent changes
   - Identify error patterns

2. **Root Cause Analysis**
   - Examine error messages
   - Check configuration settings
   - Verify dependencies

3. **Solution Implementation**
   - Apply targeted fixes
   - Test in isolated environment
   - Validate resolution

**Common Causes & Solutions:**

**Issue Category 1: Configuration Problems**
- **Symptoms:** [Specific indicators]
- **Causes:** [Common reasons]
- **Solutions:** [Step-by-step fixes]
- **Prevention:** [How to avoid]

**Issue Category 2: Dependency Issues**
- **Symptoms:** [Specific indicators]
- **Causes:** [Common reasons]
- **Solutions:** [Step-by-step fixes]
- **Prevention:** [How to avoid]

**Issue Category 3: Performance Problems**
- **Symptoms:** [Specific indicators]
- **Causes:** [Common reasons]
- **Solutions:** [Step-by-step fixes]
- **Prevention:** [How to avoid]

**Debugging Checklist:**
- [ ] Check error logs
- [ ] Verify configuration
- [ ] Test in isolation
- [ ] Check dependencies
- [ ] Monitor performance
- [ ] Validate fixes

**Escalation Path:**
If initial solutions don't work:
1. Gather detailed error information
2. Check system documentation
3. Consult with team members
4. Consider external support

**Prevention Strategies:**
- Implement monitoring
- Regular health checks
- Automated testing
- Documentation updates

Would you like me to help you work through any specific step?
"""
    
    def generate_recommendation_response(self) -> str:
        """Generate recommendation-focused response"""
        return """
💡 **Expert Recommendations**

Based on your context and requirements, here are my recommendations:

**Option Evaluation:**

**Option 1: [Primary Recommendation]**
- **Pros:** [Key benefits]
- **Cons:** [Potential drawbacks]
- **Effort:** [Implementation complexity]
- **Timeline:** [Estimated duration]
- **Best For:** [Ideal scenarios]

**Option 2: [Alternative Approach]**
- **Pros:** [Key benefits]
- **Cons:** [Potential drawbacks]
- **Effort:** [Implementation complexity]
- **Timeline:** [Estimated duration]
- **Best For:** [Ideal scenarios]

**Option 3: [Conservative Approach]**
- **Pros:** [Key benefits]
- **Cons:** [Potential drawbacks]
- **Effort:** [Implementation complexity]
- **Timeline:** [Estimated duration]
- **Best For:** [Ideal scenarios]

**Decision Criteria:**
- Technical feasibility: [Assessment]
- Resource requirements: [Analysis]
- Timeline constraints: [Evaluation]
- Risk tolerance: [Consideration]
- Long-term impact: [Assessment]

**Recommended Approach:**
I recommend **Option 1** because:
1. [Primary reason]
2. [Secondary reason]
3. [Tertiary reason]

**Implementation Roadmap:**
- **Phase 1:** [Initial steps and timeline]
- **Phase 2:** [Core implementation and timeline]
- **Phase 3:** [Testing and validation and timeline]
- **Phase 4:** [Deployment and monitoring and timeline]

**Success Metrics:**
- [Quantifiable metric 1]
- [Quantifiable metric 2]
- [Quantifiable metric 3]

**Risk Mitigation:**
- [Risk 1]: [Mitigation strategy]
- [Risk 2]: [Mitigation strategy]
- [Risk 3]: [Mitigation strategy]

Would you like me to elaborate on any specific recommendation or help you plan the implementation?
"""
    
    def generate_general_response(self) -> str:
        """Generate general conversational response"""
        return """
🤖 **Comprehensive Response**

Thank you for your question! Let me provide a thorough response based on the context available:

**Understanding Your Query:**
I can see you're looking for guidance on [topic area]. This is an important aspect of [broader context] that requires careful consideration.

**Key Insights:**
1. **Current State:** [Assessment of current situation]
2. **Opportunities:** [Potential improvements or solutions]
3. **Challenges:** [Obstacles to consider]
4. **Next Steps:** [Recommended actions]

**Practical Guidance:**
- Start with [specific first step]
- Consider [important factor]
- Be mindful of [potential issue]
- Plan for [future consideration]

**Resources & Tools:**
- [Tool 1]: [How it helps]
- [Tool 2]: [How it helps]
- [Tool 3]: [How it helps]

**Common Questions:**
- **Q:** [Frequently asked question]
- **A:** [Helpful answer]

- **Q:** [Another common question]
- **A:** [Helpful answer]

**Follow-up Suggestions:**
- Explore [related topic] for deeper understanding
- Consider [alternative approach] for different scenarios
- Look into [advanced concept] for future growth

**I'm here to help!** Feel free to ask:
- More specific questions about any aspect
- For clarification on any point
- About related topics or alternatives
- For step-by-step guidance

What would you like to explore further?
"""

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agentic RAG CLI - Interactive Vector Database Reasoning")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--load-vault", action="store_true", help="Load Obsidian vault on startup")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create CLI instance
    cli = AgenticRAGCLI()
    
    # Load vault if requested
    if args.load_vault:
        print("📚 Loading Obsidian vault...")
        asyncio.run(cli.load_documents("data/raw/vault"))
    
    # Start interactive session
    asyncio.run(cli.start_interactive_session())

if __name__ == "__main__":
    main()
