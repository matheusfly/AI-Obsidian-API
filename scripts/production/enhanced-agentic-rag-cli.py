#!/usr/bin/env python3
"""
Enhanced Agentic RAG CLI with Conversational Capabilities
- Dynamic prompts based on query intent
- Detailed vector search logging
- Conversational chain management
- Real-time search process visibility
"""

import asyncio
import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class EnhancedAgenticRAGCLI:
    """Enhanced Interactive CLI for Agentic RAG with Conversational Capabilities"""
    
    def __init__(self):
        self.project_root = project_root
        self.vector_db_path = self.project_root / "data" / "chroma"
        self.obsidian_vault_path = self.project_root / "data" / "raw" / "vault"
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.session_id = f"rag_session_{int(time.time())}"
        self.conversation_history = []
        self.conversational_chains = {}
        self.context_cache = {}
        
        # Initialize components
        self.setup_environment()
        self.initialize_components()
        
        print("🚀 Enhanced Agentic RAG CLI Initialized")
        print(f"📊 Session ID: {self.session_id}")
        print(f"🗄️ Vector DB: {self.vector_db_path}")
        print(f"📚 Obsidian Vault: {self.obsidian_vault_path}")
    
    def setup_environment(self):
        """Setup environment and create necessary directories"""
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.obsidian_vault_path.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables
        os.environ["CHROMA_PERSIST_DIRECTORY"] = str(self.vector_db_path)
        os.environ["OBSIDIAN_VAULT_PATH"] = str(self.obsidian_vault_path)
    
    def initialize_components(self):
        """Initialize vector database and other components"""
        try:
            # Initialize ChromaDB with proper configuration
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.vector_db_path)
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="obsidian_documents",
                metadata={"description": "Obsidian vault documents for RAG"}
            )
            
            print("✅ Vector database initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing vector database: {e}")
            self.collection = None
    
    async def run(self):
        """Main CLI loop with enhanced conversational capabilities"""
        print("\n" + "="*60)
        print("🤖 Enhanced Agentic RAG CLI - Conversational Mode")
        print("="*60)
        print("Type 'help' for available commands or start chatting!")
        print("="*60)
        
        while True:
            try:
                # Get user input with proper EOF handling
                try:
                    user_input = input("\n💬 You: ").strip()
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
                    print("🧹 Conversation history cleared.")
                    continue
                elif user_input.lower().startswith('load '):
                    await self.load_documents(user_input[5:])
                    continue
                elif user_input.lower().startswith('search '):
                    await self.search_documents(user_input[7:])
                    continue
                elif user_input.lower().startswith('reason '):
                    await self.reason_query(user_input[7:])
                    continue
                elif user_input.lower().startswith('rag '):
                    await self.rag_query(user_input[4:])
                    continue
                elif user_input.lower().startswith('chain create '):
                    chain_name = user_input[13:].strip()
                    result = self.create_conversational_chain(chain_name)
                    print(result)
                    continue
                elif user_input.lower().startswith('chain add '):
                    parts = user_input[10:].split(' ', 1)
                    if len(parts) == 2:
                        chain_name, message = parts
                        result = self.add_to_chain(chain_name, message)
                        print(result)
                    else:
                        print("❌ Usage: chain add <chain_name> <message>")
                    continue
                elif user_input.lower() == 'chains':
                    print(self.list_conversational_chains())
                    continue
                elif user_input.lower().startswith('chain show '):
                    chain_name = user_input[11:].strip()
                    print(self.show_chain_details(chain_name))
                    continue
                elif user_input.lower().startswith('chain use '):
                    chain_name = user_input[10:].strip()
                    await self.use_chain_for_query(chain_name, user_input)
                    continue
                else:
                    # Default to conversational RAG query
                    await self.conversational_rag_query(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    def show_help(self):
        """Show enhanced help information"""
        help_text = """
🔧 Enhanced Agentic RAG CLI Commands:

📚 Document Management:
  load <path>           Load documents from path into vector database
  search <query>        Search documents in vector database with detailed logging
  status                Show system status and metrics

🧠 Reasoning & RAG:
  reason <query>        Use Gemini Flash for pure reasoning
  rag <query>           Full RAG pipeline with vector search + Gemini
  <query>               Conversational RAG query (default mode)

🔗 Conversational Chains:
  chain create <name>   Create a new conversational chain
  chain add <name> <msg> Add message to a chain
  chain use <name> <query> Use chain context for query
  chains                List all chains
  chain show <name>     Show chain details

🛠️ System Commands:
  help                  Show this help message
  clear                 Clear conversation history
  status                Show system status
  exit/quit/q          Exit the CLI

💡 Examples:
  load docs/architecture/
  search "authentication patterns"
  reason "How should I implement JWT authentication?"
  rag "What are the best practices for microservices?"
  chain create "auth_discussion"
  chain add "auth_discussion" "Let's discuss authentication"
  chain use "auth_discussion" "What about OAuth2?"
  "How do I implement user authentication?" (conversational mode)
"""
        print(help_text)
    
    async def show_status(self):
        """Show enhanced system status"""
        print("\n📊 Enhanced Agentic RAG CLI Status")
        print("=" * 40)
        
        # Vector database status
        if self.collection:
            try:
                count = self.collection.count()
                print(f"✅ Vector Database: {count} documents")
            except:
                print("❌ Vector Database: Error getting count")
        else:
            print("❌ Vector Database: Not initialized")
        
        # API status
        if self.gemini_api_key:
            print("✅ Gemini API: Configured")
        else:
            print("❌ Gemini API: Not configured (set GEMINI_API_KEY)")
        
        # Session info
        print(f"🆔 Session ID: {self.session_id}")
        print(f"💬 Conversation History: {len(self.conversation_history)} messages")
        print(f"🔗 Active Chains: {len(self.conversational_chains)}")
        
        # Chain details
        if self.conversational_chains:
            print("\n🔗 Conversational Chains:")
            for name, chain in self.conversational_chains.items():
                print(f"  - {name}: {len(chain['messages'])} messages")
    
    async def load_documents(self, path: str):
        """Load documents with enhanced logging"""
        print(f"📚 Loading documents from: {path}")
        
        if not self.collection:
            print("❌ Vector database not initialized")
            return
        
        try:
            # Simulate document loading (replace with actual implementation)
            print("🔍 Scanning directory...")
            await asyncio.sleep(1)
            
            # Mock document loading
            mock_docs = [
                {
                    "content": "Authentication patterns in microservices architecture",
                    "metadata": {"source": "auth-guide.md", "title": "Authentication Guide"}
                },
                {
                    "content": "Best practices for API design and implementation",
                    "metadata": {"source": "api-design.md", "title": "API Design Guide"}
                }
            ]
            
            print(f"📄 Found {len(mock_docs)} documents")
            
            # Add to collection
            for i, doc in enumerate(mock_docs):
                self.collection.add(
                    documents=[doc["content"]],
                    metadatas=[doc["metadata"]],
                    ids=[f"doc_{i}"]
                )
                print(f"  ✅ Added: {doc['metadata']['title']}")
            
            print(f"🎉 Successfully loaded {len(mock_docs)} documents")
            
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
    
    async def search_documents(self, query: str):
        """Search documents with detailed logging"""
        print(f"🔍 Searching for: {query}")
        print("=" * 50)
        
        if not self.collection:
            print("❌ Vector database not initialized")
            return
        
        try:
            print("📊 Vector Search Process:")
            print("-" * 30)
            
            # Perform search with detailed logging
            results = self.collection.query(
                query_texts=[query],
                n_results=5
            )
            
            print(f"🔢 Query processed: '{query}'")
            print(f"📈 Results found: {len(results['documents'][0]) if results['documents'][0] else 0}")
            print(f"⚙️ Search parameters: n_results=5")
            print()
            
            if results['documents'] and results['documents'][0]:
                print("📋 Search Results:")
                print("-" * 30)
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ), 1):
                    similarity = 1 - distance
                    print(f"\n📄 Result #{i}:")
                    print(f"  📝 Title: {metadata.get('title', 'Untitled')}")
                    print(f"  📁 Source: {metadata.get('source', 'Unknown')}")
                    print(f"  🎯 Similarity: {similarity:.3f} ({similarity*100:.1f}%)")
                    print(f"  📏 Distance: {distance:.3f}")
                    print(f"  📄 Content: {doc[:100]}...")
                    print(f"  📊 Content Length: {len(doc)} characters")
            else:
                print("❌ No documents found")
                print("💡 Try loading documents first with 'load <directory>'")
            
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
    
    async def reason_query(self, query: str):
        """Pure reasoning query with Gemini"""
        print(f"🧠 Reasoning Query: {query}")
        print("=" * 50)
        
        if not self.gemini_api_key:
            print("❌ Gemini API key not configured")
            return
        
        try:
            print("🤖 Generating reasoning response...")
            response = await self.simulate_gemini_call(query, "reasoning")
            
            print("\n💡 Reasoning Response:")
            print("=" * 50)
            print(response)
            print("=" * 50)
            
            # Store in conversation history
            self.conversation_history.append({
                "type": "reasoning",
                "query": query,
                "response": response,
                "timestamp": time.time()
            })
            
        except Exception as e:
            print(f"❌ Error in reasoning query: {e}")
    
    async def rag_query(self, query: str):
        """Full RAG pipeline with enhanced logging"""
        print(f"🔍 RAG Query: {query}")
        print("=" * 60)
        
        try:
            # Step 1: Search vector database with detailed logging
            print("📚 Step 1: Vector Database Search")
            print("-" * 40)
            
            relevant_docs = await self.search_vector_db_detailed(query)
            
            if not relevant_docs:
                print("❌ No relevant documents found")
                print("💡 Try loading documents first with 'load <directory>'")
                return
            
            # Step 2: Build context
            print("\n🧠 Step 2: Building Context")
            print("-" * 40)
            context = self.build_rag_context(query, relevant_docs)
            print(f"📄 Context built: {len(context)} characters")
            
            # Step 3: Analyze query intent
            print("\n🎯 Step 3: Query Intent Analysis")
            print("-" * 40)
            intent = self.analyze_query_intent(query)
            print(f"🔍 Detected intent: {intent}")
            
            # Step 4: Generate response
            print("\n🤖 Step 4: Generating Response")
            print("-" * 40)
            response = await self.generate_rag_response(query, context, intent)
            
            print("\n💡 RAG Response:")
            print("=" * 60)
            print(response)
            print("=" * 60)
            
            # Store in conversation history
            self.conversation_history.append({
                "type": "rag",
                "query": query,
                "context_docs": len(relevant_docs),
                "intent": intent,
                "response": response,
                "timestamp": time.time()
            })
            
        except Exception as e:
            print(f"❌ Error in RAG query: {e}")
    
    async def conversational_rag_query(self, query: str):
        """Conversational RAG query with context awareness"""
        print(f"💬 Conversational Query: {query}")
        print("=" * 60)
        
        # Check for active chains
        active_chains = [name for name, chain in self.conversational_chains.items() 
                        if len(chain['messages']) > 0]
        
        if active_chains:
            print(f"🔗 Active chains detected: {', '.join(active_chains)}")
            print("💡 Use 'chain use <name> <query>' to use chain context")
            print()
        
        # Proceed with regular RAG query
        await self.rag_query(query)
    
    async def search_vector_db_detailed(self, query: str) -> List[Dict[str, Any]]:
        """Search vector database with detailed logging"""
        if not self.collection:
            return []
        
        try:
            print(f"🔍 Query: '{query}'")
            print(f"⚙️ Search parameters: n_results=5")
            
            results = self.collection.query(
                query_texts=[query],
                n_results=5
            )
            
            print(f"📊 Raw results: {len(results['documents'][0]) if results['documents'][0] else 0} documents")
            
            relevant_docs = []
            if results['documents'] and results['documents'][0]:
                print("\n📋 Document Analysis:")
                print("-" * 30)
                
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                ), 1):
                    similarity = 1 - distance
                    
                    doc_info = {
                        "content": doc,
                        "metadata": metadata,
                        "similarity": similarity,
                        "distance": distance
                    }
                    relevant_docs.append(doc_info)
                    
                    print(f"  📄 Doc #{i}:")
                    print(f"    📝 Title: {metadata.get('title', 'Untitled')}")
                    print(f"    📁 Source: {metadata.get('source', 'Unknown')}")
                    print(f"    🎯 Similarity: {similarity:.3f} ({similarity*100:.1f}%)")
                    print(f"    📏 Distance: {distance:.3f}")
                    print(f"    📄 Content Preview: {doc[:80]}...")
                    print()
            
            print(f"✅ Retrieved {len(relevant_docs)} relevant documents")
            return relevant_docs
            
        except Exception as e:
            print(f"❌ Error in vector search: {e}")
            return []
    
    def build_rag_context(self, query: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """Build context from relevant documents"""
        context_parts = [f"Query: {query}\n"]
        context_parts.append("Relevant Documents:")
        
        for i, doc in enumerate(relevant_docs, 1):
            context_parts.append(f"\n--- Document {i} ---")
            context_parts.append(f"Title: {doc['metadata'].get('title', 'Untitled')}")
            context_parts.append(f"Source: {doc['metadata'].get('source', 'Unknown')}")
            context_parts.append(f"Similarity: {doc['similarity']:.3f}")
            context_parts.append(f"Content: {doc['content']}")
        
        return "\n".join(context_parts)
    
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
    
    async def generate_rag_response(self, query: str, context: str, intent: str) -> str:
        """Generate RAG response using dynamic prompts"""
        if not self.gemini_api_key:
            return "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        
        # Generate dynamic prompt based on intent
        prompt = self.generate_dynamic_prompt(query, context, intent)
        
        # Simulate Gemini API call
        return await self.simulate_gemini_call(prompt, intent)
    
    def generate_dynamic_prompt(self, query: str, context: str, intent: str) -> str:
        """Generate dynamic prompts based on query intent"""
        
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
    
    async def simulate_gemini_call(self, prompt: str, intent: str = "general") -> str:
        """Simulate Gemini API call with dynamic responses"""
        await asyncio.sleep(1)  # Simulate API delay
        
        # Generate dynamic response based on intent
        if intent == "implementation":
            return self.generate_implementation_response()
        elif intent == "explanation":
            return self.generate_explanation_response()
        elif intent == "analysis":
            return self.generate_analysis_response()
        elif intent == "troubleshooting":
            return self.generate_troubleshooting_response()
        elif intent == "recommendation":
            return self.generate_recommendation_response()
        elif intent == "comparison":
            return self.generate_comparison_response()
        else:
            return self.generate_general_response()
    
    def generate_implementation_response(self) -> str:
        """Generate implementation-focused response"""
        return """
🚀 **Implementation Guide**

Based on the provided context, here's a comprehensive implementation approach:

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

**Problem Analysis:**
Based on the symptoms described, this appears to be a [type of issue] that commonly occurs in [context].

**Most Likely Causes:**
1. **Configuration Issue** - [Specific config problem]
2. **Resource Constraint** - [Memory/CPU/storage issue]
3. **Dependency Problem** - [Version conflict or missing dependency]
4. **Environment Issue** - [Development vs production difference]

**Diagnostic Steps:**
1. **Check Logs** - Look for error messages and stack traces
2. **Verify Configuration** - Ensure all settings are correct
3. **Test Dependencies** - Verify all required components are available
4. **Monitor Resources** - Check CPU, memory, and disk usage

**Solution Strategies:**

**Quick Fix:**
- [Immediate action to resolve the issue]
- [Verification steps]

**Comprehensive Fix:**
- [Long-term solution approach]
- [Prevention measures]

**Alternative Approaches:**
- [Backup solution if primary doesn't work]
- [Workaround for temporary relief]

**Prevention:**
- [Steps to avoid this issue in the future]
- [Monitoring and alerting setup]

**Verification:**
- [How to confirm the fix worked]
- [Testing procedures]

Would you like me to help you implement any of these solutions?
"""
    
    def generate_recommendation_response(self) -> str:
        """Generate recommendation-focused response"""
        return """
💡 **Expert Recommendations**

Based on the context and requirements, here are my recommendations:

**Primary Recommendation:**
[Main recommended approach] - This is the best option because:
- [Key benefit 1]
- [Key benefit 2]
- [Key benefit 3]

**Alternative Options:**

**Option A: [Name]**
- **Pros:** [Advantages]
- **Cons:** [Disadvantages]
- **Best for:** [Use cases]
- **Implementation effort:** [Low/Medium/High]

**Option B: [Name]**
- **Pros:** [Advantages]
- **Cons:** [Disadvantages]
- **Best for:** [Use cases]
- **Implementation effort:** [Low/Medium/High]

**Decision Criteria:**
Consider these factors when choosing:
- **Performance requirements** - [Specific needs]
- **Scalability needs** - [Growth expectations]
- **Maintenance overhead** - [Long-term considerations]
- **Team expertise** - [Skill requirements]
- **Budget constraints** - [Cost considerations]

**Implementation Roadmap:**
1. **Phase 1** - [Initial steps and timeline]
2. **Phase 2** - [Development and testing]
3. **Phase 3** - [Deployment and monitoring]

**Success Metrics:**
- [Measurable outcome 1]
- [Measurable outcome 2]
- [Measurable outcome 3]

**Risk Mitigation:**
- [Potential risk 1] - [Mitigation strategy]
- [Potential risk 2] - [Mitigation strategy]

Would you like me to elaborate on any of these recommendations?
"""
    
    def generate_comparison_response(self) -> str:
        """Generate comparison-focused response"""
        return """
⚖️ **Comparative Analysis**

Let me provide a detailed comparison of the options:

**Comparison Matrix:**

| Feature | Option A | Option B | Option C |
|---------|----------|----------|----------|
| Performance | [Rating] | [Rating] | [Rating] |
| Scalability | [Rating] | [Rating] | [Rating] |
| Ease of Use | [Rating] | [Rating] | [Rating] |
| Cost | [Rating] | [Rating] | [Rating] |
| Maintenance | [Rating] | [Rating] | [Rating] |

**Detailed Analysis:**

**Option A: [Name]**
- **Strengths:** [Key advantages]
- **Weaknesses:** [Key disadvantages]
- **Best Use Cases:** [When to choose this]
- **Not Ideal For:** [When to avoid this]

**Option B: [Name]**
- **Strengths:** [Key advantages]
- **Weaknesses:** [Key disadvantages]
- **Best Use Cases:** [When to choose this]
- **Not Ideal For:** [When to avoid this]

**Option C: [Name]**
- **Strengths:** [Key advantages]
- **Weaknesses:** [Key disadvantages]
- **Best Use Cases:** [When to choose this]
- **Not Ideal For:** [When to avoid this]

**Decision Framework:**
Choose **Option A** if: [Specific criteria]
Choose **Option B** if: [Specific criteria]
Choose **Option C** if: [Specific criteria]

**Hybrid Approach:**
Consider combining elements from different options:
- [How to mix approaches]
- [Benefits of hybrid solution]

**Migration Considerations:**
- [Ease of switching between options]
- [Data migration requirements]
- [Downtime considerations]

Would you like me to dive deeper into any specific comparison?
"""
    
    def generate_general_response(self) -> str:
        """Generate general response"""
        return """
💬 **Comprehensive Response**

Based on the provided context, here's my analysis and recommendations:

**Key Insights:**
- [Main insight 1 based on context]
- [Main insight 2 based on context]
- [Main insight 3 based on context]

**Practical Recommendations:**
1. **Immediate Actions** - [What to do now]
2. **Short-term Goals** - [Next steps]
3. **Long-term Strategy** - [Future planning]

**Implementation Considerations:**
- **Technical Requirements** - [What's needed technically]
- **Resource Needs** - [People, time, tools required]
- **Timeline** - [Realistic timeframes]

**Potential Challenges:**
- [Challenge 1] - [How to address it]
- [Challenge 2] - [How to address it]
- [Challenge 3] - [How to address it]

**Success Metrics:**
- [How to measure success]
- [Key performance indicators]
- [Monitoring approach]

**Next Steps:**
1. [Immediate next action]
2. [Follow-up actions]
3. [Long-term considerations]

**Related Topics:**
- [Related concept 1] - [Why it's relevant]
- [Related concept 2] - [How it connects]
- [Related concept 3] - [Advanced applications]

Would you like me to explore any specific aspect in more detail?
"""
    
    # Conversational Chain Management Methods
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
    
    async def use_chain_for_query(self, chain_name: str, query: str):
        """Use chain context for a query"""
        if chain_name not in self.conversational_chains:
            print(f"❌ Chain '{chain_name}' not found")
            return
        
        # Get chain context
        chain_context = self.get_chain_context(chain_name)
        
        print(f"🔗 Using chain '{chain_name}' context")
        print(f"📝 Chain context: {len(chain_context)} characters")
        
        # Add user query to chain
        self.add_to_chain(chain_name, query, "user")
        
        # Perform RAG query with chain context
        await self.rag_query_with_context(query, chain_context)

async def main():
    """Main entry point"""
    cli = EnhancedAgenticRAGCLI()
    await cli.run()

if __name__ == "__main__":
    asyncio.run(main())
