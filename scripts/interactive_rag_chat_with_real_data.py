#!/usr/bin/env python3
"""
Interactive RAG Chat with Real Data
Complete system using real data-pipeline services, local embeddings, and Gemini chat
"""

import sys
import os
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from datetime import datetime

# Add data-pipeline services to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

print("🚀 Interactive RAG Chat with Real Data")
print("=" * 50)

# Import real data-pipeline services
try:
    from embeddings.embedding_service import EmbeddingService
    from vector.chroma_service import ChromaService
    from search.semantic_search_service import SemanticSearchService
    from processing.content_processor import ContentProcessor
    print("✅ Real data-pipeline services imported successfully")
except ImportError as e:
    print(f"❌ Error importing data-pipeline services: {e}")
    print("Using mock services for demonstration...")
    
    # Mock services for demonstration
    class MockEmbeddingService:
        def __init__(self):
            self.model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
            print(f"🔧 Mock EmbeddingService: {self.model_name}")
        
        def embed_text(self, text: str):
            import numpy as np
            return np.random.rand(384)
        
        def embed_texts(self, texts: List[str]):
            return [self.embed_text(text) for text in texts]
    
    class MockChromaService:
        def __init__(self):
            self.documents = []
            self.embeddings = []
            self.metadatas = []
            self.ids = []
            print("🔧 Mock ChromaService initialized")
        
        def store_embeddings(self, documents, embeddings, metadatas, ids):
            self.documents.extend(documents)
            self.embeddings.extend(embeddings)
            self.metadatas.extend(metadatas)
            self.ids.extend(ids)
            return True
        
        def query_embeddings(self, query_embedding, n_results=5, where_metadata=None):
            if not self.embeddings:
                return []
            
            import numpy as np
            similarities = []
            for doc_embedding in self.embeddings:
                similarity = np.dot(query_embedding, doc_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                )
                similarities.append(similarity)
            
            ranked_indices = np.argsort(similarities)[::-1]
            results = []
            
            for idx in ranked_indices[:n_results]:
                results.append({
                    "content": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "similarity": float(similarities[idx]),
                    "id": self.ids[idx]
                })
            return results
    
    class MockSemanticSearchService:
        def __init__(self, chroma_service, embedding_service):
            self.chroma_service = chroma_service
            self.embedding_service = embedding_service
        
        def search(self, query: str, n_results: int = 5):
            query_embedding = self.embedding_service.embed_text(query)
            return self.chroma_service.query_embeddings(query_embedding, n_results)
    
    class MockContentProcessor:
        def __init__(self):
            print("🔧 Mock ContentProcessor initialized")
        
        def process_content(self, content: str, file_path: str):
            return {
                'chunks': [content],
                'metadata': {'filename': Path(file_path).name, 'path': file_path}
            }
    
    # Use mock services
    EmbeddingService = MockEmbeddingService
    ChromaService = MockChromaService
    SemanticSearchService = MockSemanticSearchService
    ContentProcessor = MockContentProcessor

class InteractiveRAGChat:
    """Interactive RAG Chat with Real Data Integration"""
    
    def __init__(self):
        self.vault_path = "D:/Nomade Milionario"
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService()
        self.search_service = SemanticSearchService(self.chroma_service, self.embedding_service)
        self.content_processor = ContentProcessor()
        
        # Initialize Gemini
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini API configured")
        else:
            print("⚠️ GEMINI_API_KEY not found, using mock responses")
            self.gemini_model = None
        
        # Conversation state
        self.conversation_history = []
        self.context_cache = {}
        
        # Performance tracking
        self.query_count = 0
        self.total_response_time = 0.0
        
    def load_vault_data(self):
        """Load real data from Obsidian vault"""
        print(f"📚 Loading vault data from: {self.vault_path}")
        
        if not os.path.exists(self.vault_path):
            print(f"❌ Vault path not found: {self.vault_path}")
            print("Using sample data for demonstration...")
            return self.load_sample_data()
        
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        # Load markdown files from vault
        for file_path in Path(self.vault_path).rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content.strip()) < 50:  # Skip very short files
                    continue
                
                # Process content
                processed = self.content_processor.process_content(content, str(file_path))
                
                for i, chunk in enumerate(processed['chunks']):
                    documents.append(chunk)
                    metadatas.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'chunk_index': i,
                        'file_size': len(content),
                        'topics': self.extract_topics(chunk)
                    })
                    ids.append(f"{file_path.stem}_{i}")
                
                print(f"   ✅ Loaded: {file_path.name} ({len(processed['chunks'])} chunks)")
                
            except Exception as e:
                print(f"   ❌ Error loading {file_path}: {e}")
        
        if not documents:
            print("❌ No documents loaded from vault")
            return self.load_sample_data()
        
        # Generate embeddings
        print(f"🔄 Generating embeddings for {len(documents)} chunks...")
        embeddings = self.embedding_service.embed_texts(documents)
        
        # Store in ChromaDB
        print("💾 Storing in vector database...")
        self.chroma_service.store_embeddings(documents, embeddings, metadatas, ids)
        
        print(f"✅ Vault data loaded: {len(documents)} chunks from {len(set(m['filename'] for m in metadatas))} files")
        return True
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        print("📚 Loading sample data for demonstration...")
        
        sample_docs = [
            {
                "content": "Philosophy of mathematics examines the nature of mathematical objects and truth. It explores questions about the existence and nature of mathematical entities, the relationship between mathematics and reality, and the methods of mathematical reasoning.",
                "metadata": {"filename": "philosophy_of_math.md", "topics": ["philosophy", "mathematics"]}
            },
            {
                "content": "Reading techniques like speed reading and comprehension strategies help improve learning efficiency and knowledge retention. These methods include skimming, scanning, active reading, and note-taking techniques.",
                "metadata": {"filename": "reading_techniques.md", "topics": ["reading", "learning"]}
            },
            {
                "content": "Python programming involves writing code with functions and variables. It's a versatile language for software development, data analysis, machine learning, and web development. Python emphasizes code readability and simplicity.",
                "metadata": {"filename": "python_programming.md", "topics": ["programming", "python"]}
            },
            {
                "content": "Data analysis involves examining, cleaning, transforming, and modeling data to discover useful information and support decision-making. It includes statistical analysis, data visualization, and machine learning techniques.",
                "metadata": {"filename": "data_analysis.md", "topics": ["data", "analysis", "statistics"]}
            },
            {
                "content": "Professional knowledge refers to the specialized knowledge, skills, and expertise required for a particular profession or field of work. It includes both theoretical knowledge and practical experience.",
                "metadata": {"filename": "professional_knowledge.md", "topics": ["professional", "knowledge", "skills"]}
            }
        ]
        
        documents = [doc["content"] for doc in sample_docs]
        metadatas = [doc["metadata"] for doc in sample_docs]
        ids = [f"sample_{i}" for i in range(len(sample_docs))]
        
        # Generate embeddings
        embeddings = self.embedding_service.embed_texts(documents)
        
        # Store in ChromaDB
        self.chroma_service.store_embeddings(documents, embeddings, metadatas, ids)
        
        print(f"✅ Sample data loaded: {len(documents)} documents")
        return True
    
    def extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        topics = []
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['philosophy', 'philosophical', 'logic', 'mathematics']):
            topics.append('philosophy')
        if any(word in content_lower for word in ['reading', 'comprehension', 'learning', 'study']):
            topics.append('reading')
        if any(word in content_lower for word in ['programming', 'python', 'code', 'software']):
            topics.append('programming')
        if any(word in content_lower for word in ['data', 'analysis', 'statistics', 'research']):
            topics.append('data')
        if any(word in content_lower for word in ['professional', 'knowledge', 'skills', 'career']):
            topics.append('professional')
        
        return topics if topics else ['general']
    
    def detect_query_intent(self, query: str) -> Dict[str, Any]:
        """Detect query intent and characteristics"""
        query_lower = query.lower()
        
        intent = {
            'type': 'question',
            'topic': 'general',
            'complexity': 'medium',
            'keywords': query_lower.split(),
            'confidence': 0.8
        }
        
        # Detect topic
        if any(word in query_lower for word in ['philosophy', 'philosophical', 'logic', 'mathematics']):
            intent['topic'] = 'philosophy'
        elif any(word in query_lower for word in ['reading', 'comprehension', 'learning', 'study']):
            intent['topic'] = 'reading'
        elif any(word in query_lower for word in ['programming', 'python', 'code', 'software']):
            intent['topic'] = 'programming'
        elif any(word in query_lower for word in ['data', 'analysis', 'statistics', 'research']):
            intent['topic'] = 'data'
        elif any(word in query_lower for word in ['professional', 'knowledge', 'skills', 'career']):
            intent['topic'] = 'professional'
        
        # Detect complexity
        word_count = len(query.split())
        if word_count > 15:
            intent['complexity'] = 'high'
        elif word_count < 5:
            intent['complexity'] = 'low'
        
        return intent
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search documents using real vector search"""
        print(f"🔍 Searching for: '{query}'")
        
        # Detect intent
        intent = self.detect_query_intent(query)
        print(f"   🎯 Intent: {intent['topic']} ({intent['complexity']} complexity)")
        
        # Search using real semantic search
        results = self.search_service.search(query, n_results)
        
        print(f"   📊 Found {len(results)} documents")
        for i, result in enumerate(results, 1):
            similarity = result.get('similarity', 0)
            filename = result.get('metadata', {}).get('filename', 'Unknown')
            print(f"   {i}. {filename} (similarity: {similarity:.3f})")
        
        return results
    
    def generate_gemini_response(self, query: str, documents: List[Dict]) -> str:
        """Generate response using Gemini"""
        if not self.gemini_model:
            return self.generate_mock_response(query, documents)
        
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"**{doc.get('metadata', {}).get('filename', 'Document')}** (similarity: {doc.get('similarity', 0):.3f}):\n{doc.get('content', '')[:500]}..."
                for doc in documents[:3]
            ])
            
            # Create prompt
            prompt = f"""You are an intelligent assistant helping with knowledge retrieval and synthesis.

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- Answer based on the provided context
- Be concise and helpful
- If the context doesn't contain relevant information, say so
- Cite the source documents when possible
- Provide practical insights when appropriate

RESPONSE:"""
            
            # Generate response
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"❌ Error generating Gemini response: {e}")
            return self.generate_mock_response(query, documents)
    
    def generate_mock_response(self, query: str, documents: List[Dict]) -> str:
        """Generate mock response when Gemini is not available"""
        if not documents:
            return "I couldn't find relevant information to answer your question. Please try rephrasing your query."
        
        # Simple response based on retrieved documents
        response_parts = []
        response_parts.append(f"Based on the available information, here's what I found about '{query}':")
        
        for i, doc in enumerate(documents[:3], 1):
            content = doc.get('content', '')[:200]
            filename = doc.get('metadata', {}).get('filename', 'Document')
            similarity = doc.get('similarity', 0)
            response_parts.append(f"\n{i}. From {filename} (relevance: {similarity:.3f}): {content}...")
        
        response_parts.append(f"\n\nI found {len(documents)} relevant documents. The most relevant ones are shown above.")
        
        return "\n".join(response_parts)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query and return comprehensive results"""
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"💬 Processing Query: '{query}'")
        print(f"{'='*60}")
        
        # Search documents
        documents = self.search_documents(query, n_results=5)
        
        # Generate response
        response = self.generate_gemini_response(query, documents)
        
        # Calculate metrics
        response_time = time.time() - start_time
        avg_similarity = sum(doc.get('similarity', 0) for doc in documents) / len(documents) if documents else 0
        quality_score = min(1.0, avg_similarity + 0.2)  # Simple quality scoring
        
        # Update conversation history
        self.conversation_history.append({
            'query': query,
            'response': response,
            'documents': documents,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update performance metrics
        self.query_count += 1
        self.total_response_time += response_time
        
        # Prepare result
        result = {
            'query': query,
            'response': response,
            'documents': documents,
            'metrics': {
                'response_time': response_time,
                'avg_similarity': avg_similarity,
                'quality_score': quality_score,
                'documents_found': len(documents)
            },
            'intent': self.detect_query_intent(query)
        }
        
        print(f"\n📊 QUERY METRICS:")
        print(f"   Response Time: {response_time:.3f}s")
        print(f"   Average Similarity: {avg_similarity:.3f}")
        print(f"   Quality Score: {quality_score:.3f}")
        print(f"   Documents Found: {len(documents)}")
        
        return result
    
    def show_system_status(self):
        """Show current system status"""
        print(f"\n🔧 SYSTEM STATUS:")
        print(f"   Vault Path: {self.vault_path}")
        print(f"   Embedding Service: {self.embedding_service.model_name}")
        print(f"   Documents Loaded: {len(self.chroma_service.documents)}")
        print(f"   Queries Processed: {self.query_count}")
        print(f"   Avg Response Time: {self.total_response_time / max(1, self.query_count):.3f}s")
        print(f"   Gemini Available: {'Yes' if self.gemini_model else 'No'}")
    
    def run_interactive_chat(self):
        """Run interactive chat session"""
        print(f"\n🚀 Starting Interactive RAG Chat Session")
        print(f"{'='*60}")
        
        # Load data
        if not self.load_vault_data():
            print("❌ Failed to load data")
            return
        
        # Show system status
        self.show_system_status()
        
        print(f"\n💬 Interactive Chat Started!")
        print(f"Type your questions or 'quit' to exit")
        print(f"{'='*60}")
        
        while True:
            try:
                # Get user input
                query = input(f"\n[Query {self.query_count + 1}] 🤖 RAG> ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Process query
                result = self.process_query(query)
                
                # Show response
                print(f"\n🤖 RESPONSE:")
                print(f"{'-'*40}")
                print(result['response'])
                print(f"{'-'*40}")
                
                # Show follow-up suggestions
                if result['documents']:
                    print(f"\n💡 FOLLOW-UP SUGGESTIONS:")
                    suggestions = [
                        "Tell me more about this topic",
                        "What are the key concepts?",
                        "How does this relate to other subjects?",
                        "What are the practical applications?"
                    ]
                    for i, suggestion in enumerate(suggestions[:2], 1):
                        print(f"   {i}. {suggestion}")
                
            except KeyboardInterrupt:
                print(f"\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        # Show final statistics
        print(f"\n📊 SESSION STATISTICS:")
        print(f"   Total Queries: {self.query_count}")
        print(f"   Avg Response Time: {self.total_response_time / max(1, self.query_count):.3f}s")
        print(f"   Conversation History: {len(self.conversation_history)} entries")

def main():
    """Main function"""
    print("🚀 Interactive RAG Chat with Real Data")
    print("=" * 50)
    
    # Check for Gemini API key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ GEMINI_API_KEY not found in environment variables")
        print("   Set it with: set GEMINI_API_KEY=your_key_here")
        print("   Continuing with mock responses...")
    
    # Create and run chat
    chat = InteractiveRAGChat()
    chat.run_interactive_chat()

if __name__ == "__main__":
    main()
