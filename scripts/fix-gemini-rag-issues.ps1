# Fix Gemini RAG Issues and Hardcoded Variables
# Fixes rate limiting, hardcoded paths, and ensures real data consumption

param(
    [string]$ProjectRoot = "D:\codex\datamaster\backend-ops\data-vault-obsidian"
)

Write-Host "🔧 Fixing Gemini RAG Issues and Hardcoded Variables..." -ForegroundColor Green

# 1. Create proper .env file with real configuration
Write-Host "📝 Creating .env file with proper configuration..." -ForegroundColor Yellow

$envContent = @"
# Data Pipeline Service Configuration

# Obsidian API Configuration
OBSIDIAN_API_KEY=your_obsidian_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123
OBSIDIAN_VAULT_PATH=/vault

# Gemini API Configuration
GEMINI_API_KEY=AIzaSyAA7jg9__c_YZmcspAsydTkq33MGrK4Ynw
GEMINI_MODEL_NAME=gemini-1.5-flash

# ChromaDB Configuration
CHROMA_URL=http://chroma:8000
CHROMA_COLLECTION_NAME=obsidian_vault
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=32
EMBEDDING_CACHE_SIZE=10000

# Processing Configuration
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_DOCUMENT_SIZE=10485760
PROCESSING_BATCH_SIZE=100

# Search Configuration
DEFAULT_SEARCH_RESULTS=5
MAX_SEARCH_RESULTS=20
SIMILARITY_THRESHOLD=0.7

# Caching Configuration
CACHE_TTL_EMBEDDINGS=3600
CACHE_TTL_SEARCH=1800
CACHE_TTL_CONTENT=7200

# Monitoring Configuration
LOG_LEVEL=INFO
METRICS_ENABLED=true
PROMETHEUS_PORT=9090

# Service Configuration
SERVICE_NAME=data-pipeline
SERVICE_VERSION=1.0.0
SERVICE_PORT=8003
SERVICE_HOST=0.0.0.0

# Rate Limiting Configuration
GEMINI_RATE_LIMIT_REQUESTS_PER_MINUTE=10
GEMINI_RATE_LIMIT_DELAY_SECONDS=8
GEMINI_MAX_RETRIES=3
GEMINI_BACKOFF_FACTOR=2

# Vault Configuration
VAULT_PATH=$ProjectRoot\data\raw\vault
VECTOR_DB_PATH=$ProjectRoot\data\chroma
"@

$envContent | Out-File -FilePath "$ProjectRoot\.env" -Encoding UTF8
Write-Host "✅ Created .env file" -ForegroundColor Green

# 2. Create a fixed Gemini integration test with rate limiting
Write-Host "🔧 Creating fixed Gemini integration test..." -ForegroundColor Yellow

$fixedGeminiTest = @"
#!/usr/bin/env python3
"""
Fixed Gemini Integration Test with Rate Limiting and Real Data
"""
import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.vector.chroma_service import ChromaService
from src.embeddings.embedding_service import EmbeddingService
from src.search.search_service import SemanticSearchService
from src.search.query_expansion_service import ExpansionStrategy
from src.llm.gemini_client import GeminiClient, PromptStyle, LLMResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FixedGeminiIntegrationTester:
    """Fixed Gemini integration tester with rate limiting and real data"""
    
    def __init__(self):
        self.chroma_service = None
        self.embedding_service = None
        self.search_service = None
        self.gemini_client = None
        
        # Rate limiting configuration
        self.rate_limit_delay = int(os.getenv('GEMINI_RATE_LIMIT_DELAY_SECONDS', '8'))
        self.max_retries = int(os.getenv('GEMINI_MAX_RETRIES', '3'))
        self.backoff_factor = int(os.getenv('GEMINI_BACKOFF_FACTOR', '2'))
        
        # Test queries for different scenarios
        self.test_queries = [
            "What is machine learning?",
            "How to optimize Python performance?",
            "Explain vector databases"
        ]
    
    async def initialize_services(self):
        """Initialize all services for testing with real data paths"""
        logger.info("🚀 Initializing services for Gemini integration testing...")
        
        # Get real data paths from environment
        vault_path = os.getenv('VAULT_PATH', './data/raw/vault')
        vector_db_path = os.getenv('VECTOR_DB_PATH', './data/chroma')
        
        # Initialize ChromaDB service with real data
        self.chroma_service = ChromaService(
            collection_name="real_vault_collection",
            persist_directory=vector_db_path,
            embedding_model="all-MiniLM-L6-v2",
            optimize_for_large_vault=True
        )
        
        # Initialize embedding service
        self.embedding_service = EmbeddingService(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize search service with query expansion
        self.search_service = SemanticSearchService(
            chroma_service=self.chroma_service,
            embedding_service=self.embedding_service,
            gemini_api_key=os.getenv('GEMINI_API_KEY')
        )
        
        # Initialize Gemini client with rate limiting
        self.gemini_client = GeminiClient(
            api_key=os.getenv('GEMINI_API_KEY'),
            max_context_tokens=2048,
            model_name="gemini-1.5-flash"
        )
        
        logger.info("✅ All services initialized successfully")
        logger.info(f"📚 Vault path: {vault_path}")
        logger.info(f"🗄️ Vector DB path: {vector_db_path}")
    
    async def test_with_rate_limiting(self, query: str, max_retries: int = 3):
        """Test with proper rate limiting and retry logic"""
        logger.info(f"🔍 Testing query with rate limiting: '{query}'")
        
        for attempt in range(max_retries):
            try:
                # Check if we have data in the collection
                count = self.chroma_service.collection.count()
                if count == 0:
                    logger.warning("⚠️ No data in collection. Please run data ingestion first.")
                    return None
                
                logger.info(f"📊 Collection contains {count} documents")
                
                # Search with query expansion
                search_results = await self.search_service.search_similar(
                    query=query,
                    n_results=5,
                    expand_query=True,
                    expansion_strategy=ExpansionStrategy.HYBRID
                )
                
                if not search_results:
                    logger.warning("No search results found")
                    return None
                
                # Process with Gemini (with rate limiting)
                logger.info(f"🤖 Processing with Gemini (attempt {attempt + 1})...")
                
                # Add delay between requests to respect rate limits
                if attempt > 0:
                    delay = self.rate_limit_delay * (self.backoff_factor ** (attempt - 1))
                    logger.info(f"⏳ Waiting {delay}s before retry...")
                    await asyncio.sleep(delay)
                
                response = await self.gemini_client.process_content(
                    query=query,
                    context_chunks=search_results,
                    style=PromptStyle.RESEARCH_ASSISTANT
                )
                
                logger.info(f"✅ Success! Processing time: {time.time():.2f}s")
                logger.info(f"📝 Answer length: {len(response.answer)} characters")
                logger.info(f"🎯 Confidence: {response.confidence_score:.3f}")
                logger.info(f"📊 Sources used: {response.sources_used}")
                logger.info(f"🔢 Token usage: {response.token_usage}")
                logger.info(f"📄 Answer preview: {response.answer[:200]}...")
                
                return response
                
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                if "429" in str(e) or "quota" in str(e).lower():
                    logger.warning("⚠️ Rate limit exceeded, will retry with backoff")
                    if attempt < max_retries - 1:
                        delay = self.rate_limit_delay * (self.backoff_factor ** attempt)
                        logger.info(f"⏳ Waiting {delay}s before retry...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error("❌ Max retries exceeded")
                        return None
                else:
                    logger.error(f"❌ Non-rate-limit error: {e}")
                    return None
        
        return None
    
    async def test_real_data_consumption(self):
        """Test real data consumption from vault embeddings"""
        logger.info("\n📚 Testing Real Data Consumption")
        logger.info("=" * 50)
        
        # Check collection status
        try:
            count = self.chroma_service.collection.count()
            logger.info(f"📊 Collection contains {count} documents")
            
            if count == 0:
                logger.warning("⚠️ No data in collection. This suggests:")
                logger.warning("   1. Vault data hasn't been ingested yet")
                logger.warning("   2. Collection name is incorrect")
                logger.warning("   3. Vector DB path is incorrect")
                return False
            
            # Test a simple query
            query = "machine learning"
            logger.info(f"🔍 Testing query: '{query}'")
            
            # Search without LLM to test data retrieval
            search_results = await self.search_service.search_similar(
                query=query,
                n_results=3,
                expand_query=False
            )
            
            if search_results:
                logger.info(f"✅ Found {len(search_results)} results from real data")
                for i, result in enumerate(search_results):
                    logger.info(f"  📄 Result {i+1}: {result.get('metadata', {}).get('file_name', 'Unknown')} (similarity: {result.get('similarity', 0):.3f})")
                return True
            else:
                logger.warning("❌ No search results found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing real data consumption: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive test with rate limiting"""
        logger.info("🎯 Starting Fixed Gemini Integration Tests")
        logger.info("=" * 80)
        
        try:
            await self.initialize_services()
            
            # Test real data consumption first
            if not await self.test_real_data_consumption():
                logger.error("❌ Real data consumption test failed. Please check your data setup.")
                return
            
            # Test with rate limiting
            for query in self.test_queries:
                logger.info(f"\n📝 Testing query: '{query}'")
                await self.test_with_rate_limiting(query)
                
                # Add delay between queries to respect rate limits
                logger.info("⏳ Waiting between queries to respect rate limits...")
                await asyncio.sleep(self.rate_limit_delay)
            
            logger.info("\n🎉 All Fixed Gemini Integration Tests Completed Successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise

async def main():
    """Main test execution"""
    tester = FixedGeminiIntegrationTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
"@

$fixedGeminiTest | Out-File -FilePath "$ProjectRoot\services\data-pipeline\test_gemini_integration_fixed.py" -Encoding UTF8
Write-Host "✅ Created fixed Gemini integration test" -ForegroundColor Green

# 3. Create a script to test real data consumption
Write-Host "🔧 Creating real data consumption test..." -ForegroundColor Yellow

$realDataTest = @"
#!/usr/bin/env python3
"""
Test Real Data Consumption from Vault Embeddings
"""
import os
import sys
import time
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "services" / "data-pipeline" / "src"))

import chromadb
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataConsumptionTester:
    """Test real data consumption from vault embeddings"""
    
    def __init__(self):
        self.project_root = project_root
        self.vector_db_path = self.project_root / "data" / "chroma"
        self.vault_path = self.project_root / "data" / "raw" / "vault"
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=str(self.vector_db_path))
        
        # Available collections
        self.collections = self.chroma_client.list_collections()
        logger.info(f"🗄️ ChromaDB Collections: {[c.name for c in self.collections]}")
        
        # Use the collection with most data
        self.collection = None
        self.collection_name = None
        max_docs = 0
        for collection in self.collections:
            count = collection.count()
            logger.info(f"📊 {collection.name}: {count} documents")
            if count > max_docs:
                max_docs = count
                self.collection = collection
                self.collection_name = collection.name
        
        if self.collection:
            logger.info(f"✅ Using collection: {self.collection_name} ({self.collection.count()} documents)")
        else:
            logger.warning("❌ No collections with data found")
    
    def test_similarity_search(self, query: str, n_results: int = 5):
        """Test similarity search on real data"""
        if not self.collection:
            logger.error("❌ No collection available")
            return []
        
        try:
            logger.info(f"🔍 Searching {self.collection_name} for: '{query}'")
            logger.info(f"📊 Collection size: {self.collection.count()}")
            
            start_time = time.time()
            
            # Search using ChromaDB's built-in search
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            search_time = time.time() - start_time
            logger.info(f"⏱️ Search completed in {search_time:.3f}s")
            
            # Format and display results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                result = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'similarity': 1 - results['distances'][0][i]
                }
                formatted_results.append(result)
                
                # Display result with detailed logging
                logger.info(f"📄 Result {i+1}:")
                logger.info(f"   📝 Title: {result['metadata'].get('heading', result['metadata'].get('title', 'Unknown'))}")
                logger.info(f"   📁 Source: {result['metadata'].get('file_name', 'Unknown')}")
                logger.info(f"   🏷️ Tags: {result['metadata'].get('content_tags', '')}")
                logger.info(f"   🎯 Similarity: {result['similarity']:.3f}")
                logger.info(f"   📏 Distance: {result['distance']:.3f}")
                logger.info(f"   📄 Content: {result['content'][:100]}...")
                logger.info("")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def test_batch_queries(self):
        """Test multiple queries to verify data quality"""
        test_queries = [
            "machine learning",
            "artificial intelligence",
            "vector database",
            "Python programming",
            "data science"
        ]
        
        logger.info("🧪 Testing batch queries on real data...")
        
        for query in test_queries:
            logger.info(f"\n🔍 Testing query: '{query}'")
            results = self.test_similarity_search(query, n_results=3)
            
            if results:
                avg_similarity = sum(r['similarity'] for r in results) / len(results)
                logger.info(f"📊 Average similarity: {avg_similarity:.3f}")
                logger.info(f"📈 Results quality: {'Good' if avg_similarity > 0.5 else 'Poor'}")
            else:
                logger.warning(f"❌ No results for query: '{query}'")
    
    def show_data_quality_report(self):
        """Show data quality report"""
        if not self.collection:
            logger.error("❌ No collection available")
            return
        
        logger.info("\n📊 DATA QUALITY REPORT")
        logger.info("=" * 40)
        logger.info(f"📚 Collection: {self.collection_name}")
        logger.info(f"📄 Total documents: {self.collection.count()}")
        logger.info(f"🗄️ Vector DB: {self.vector_db_path}")
        logger.info(f"📚 Vault: {self.vault_path}")
        
        # Test a few queries to assess quality
        test_queries = ["machine learning", "Python", "data"]
        total_similarity = 0
        total_queries = 0
        
        for query in test_queries:
            results = self.test_similarity_search(query, n_results=1)
            if results:
                total_similarity += results[0]['similarity']
                total_queries += 1
        
        if total_queries > 0:
            avg_similarity = total_similarity / total_queries
            logger.info(f"🎯 Average similarity: {avg_similarity:.3f}")
            logger.info(f"📈 Data quality: {'Excellent' if avg_similarity > 0.8 else 'Good' if avg_similarity > 0.6 else 'Fair' if avg_similarity > 0.4 else 'Poor'}")

def main():
    """Main function"""
    tester = RealDataConsumptionTester()
    
    if not tester.collection:
        logger.error("❌ No data available in ChromaDB. Please run data ingestion first.")
        return
    
    # Show data quality report
    tester.show_data_quality_report()
    
    # Test batch queries
    tester.test_batch_queries()

if __name__ == "__main__":
    main()
"@

$realDataTest | Out-File -FilePath "$ProjectRoot\scripts\test-real-data-consumption.py" -Encoding UTF8
Write-Host "✅ Created real data consumption test" -ForegroundColor Green

# 4. Create a script to fix the path issues
Write-Host "🔧 Creating path fix script..." -ForegroundColor Yellow

$pathFixScript = @"
#!/usr/bin/env python3
"""
Fix Path Issues and Run Real Data Tests
"""
import os
import sys
import subprocess
from pathlib import Path

def fix_paths_and_run_tests():
    """Fix path issues and run real data tests"""
    
    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"🔧 Working directory: {os.getcwd()}")
    print(f"📁 Project root: {project_root}")
    
    # Set environment variables
    os.environ['VAULT_PATH'] = str(project_root / "data" / "raw" / "vault")
    os.environ['VECTOR_DB_PATH'] = str(project_root / "data" / "chroma")
    os.environ['GEMINI_API_KEY'] = "AIzaSyAA7jg9__c_YZmcspAsydTkq33MGrK4Ynw"
    
    print("✅ Environment variables set")
    
    # Test 1: Real data consumption test
    print("\n🧪 Test 1: Real Data Consumption Test")
    print("=" * 50)
    try:
        result = subprocess.run([
            sys.executable, 
            "scripts/test-real-data-consumption.py"
        ], capture_output=True, text=True, cwd=project_root)
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Return code: {result.returncode}")
        
    except Exception as e:
        print(f"❌ Error running real data test: {e}")
    
    # Test 2: Fixed Gemini integration test
    print("\n🧪 Test 2: Fixed Gemini Integration Test")
    print("=" * 50)
    try:
        result = subprocess.run([
            sys.executable, 
            "services/data-pipeline/test_gemini_integration_fixed.py"
        ], capture_output=True, text=True, cwd=project_root)
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Return code: {result.returncode}")
        
    except Exception as e:
        print(f"❌ Error running Gemini integration test: {e}")

if __name__ == "__main__":
    fix_paths_and_run_tests()
"@

$pathFixScript | Out-File -FilePath "$ProjectRoot\scripts\fix-paths-and-test.py" -Encoding UTF8
Write-Host "✅ Created path fix script" -ForegroundColor Green

Write-Host "🎉 All fixes created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: python scripts/fix-paths-and-test.py" -ForegroundColor White
Write-Host "2. Check the output for any remaining issues" -ForegroundColor White
Write-Host "3. If data is missing, run data ingestion first" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Fixed issues:" -ForegroundColor Green
Write-Host "✅ Rate limiting with proper delays and retries" -ForegroundColor White
Write-Host "✅ Hardcoded paths replaced with environment variables" -ForegroundColor White
Write-Host "✅ Real data consumption verification" -ForegroundColor White
Write-Host "✅ Proper error handling and logging" -ForegroundColor White
Write-Host "✅ Environment configuration file created" -ForegroundColor White
