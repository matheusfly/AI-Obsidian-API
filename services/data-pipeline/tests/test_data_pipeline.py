"""
Comprehensive tests for Data Pipeline Service
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

# Import services
from src.ingestion.obsidian_client import ObsidianAPIClient
from src.processing.content_processor import ContentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vector.chroma_service import ChromaService
from src.search.search_service import SemanticSearchService
from src.llm.gemini_client import GeminiClient


class TestObsidianAPIClient:
    """Test Obsidian API Client"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Obsidian client"""
        with patch('httpx.AsyncClient') as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {"path": "test1.md", "size": 100},
                {"path": "test2.md", "size": 200}
            ]
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_httpx.return_value = mock_client_instance
            
            client = ObsidianAPIClient("test_key", "127.0.0.1", 27123)
            client.client = mock_client_instance
            return client
    
    @pytest.mark.asyncio
    async def test_list_vault_files(self, mock_client):
        """Test listing vault files"""
        files = await mock_client.list_vault_files()
        assert len(files) == 2
        assert files[0]["path"] == "test1.md"
    
    @pytest.mark.asyncio
    async def test_test_connection(self, mock_client):
        """Test connection testing"""
        result = await mock_client.test_connection()
        assert result is True


class TestContentProcessor:
    """Test Content Processor"""
    
    @pytest.fixture
    def processor(self):
        """Create content processor"""
        return ContentProcessor(chunk_size=512, chunk_overlap=50)
    
    def test_extract_frontmatter(self, processor):
        """Test frontmatter extraction"""
        content = """---
title: Test
tags: [test, example]
---

# Main Content
This is the main content."""
        
        frontmatter, clean_content = processor.extract_frontmatter(content)
        assert frontmatter["title"] == "Test"
        assert frontmatter["tags"] == ["test", "example"]
        assert "Main Content" in clean_content
    
    def test_extract_tags(self, processor):
        """Test tag extraction"""
        content = "This is a #test with #multiple #tags"
        tags = processor.extract_tags(content)
        assert "test" in tags
        assert "multiple" in tags
        assert "tags" in tags
    
    def test_extract_links(self, processor):
        """Test link extraction"""
        content = """
        This has [[wiki links]] and [markdown links](http://example.com)
        Also has https://external.com links
        """
        links = processor.extract_links(content)
        assert "wiki links" in links
        assert "http://example.com" in links
        assert "https://external.com" in links
    
    def test_chunk_by_headings(self, processor):
        """Test chunking by headings"""
        content = """# Heading 1
Content under heading 1

## Heading 2
Content under heading 2

# Heading 3
Content under heading 3"""
        
        chunks = processor.chunk_by_headings(content, "test.md")
        assert len(chunks) == 3
        assert chunks[0]["heading"] == "Heading 1"
        assert chunks[1]["heading"] == "Heading 2"
        assert chunks[2]["heading"] == "Heading 3"
    
    def test_process_file(self, processor):
        """Test file processing"""
        content = """# Test File
This is a test file with some content.

## Section 1
Content in section 1.

## Section 2
Content in section 2."""
        
        result = processor.process_file("test.md", content, "headings")
        assert result["file_path"] == "test.md"
        assert len(result["chunks"]) == 3
        assert result["total_chunks"] == 3


class TestEmbeddingService:
    """Test Embedding Service"""
    
    @pytest.fixture
    def embedding_service(self):
        """Create embedding service with mock model"""
        with patch('sentence_transformers.SentenceTransformer') as mock_model:
            mock_model_instance = Mock()
            mock_model_instance.encode.return_value = [[0.1, 0.2, 0.3] * 128]  # 384 dimensions
            mock_model.return_value = mock_model_instance
            
            service = EmbeddingService("test-model", cache_size=100)
            service.model = mock_model_instance
            return service
    
    def test_generate_embedding(self, embedding_service):
        """Test embedding generation"""
        embedding = embedding_service.generate_embedding("test text")
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
    
    def test_batch_generate_embeddings(self, embedding_service):
        """Test batch embedding generation"""
        texts = ["text 1", "text 2", "text 3"]
        embeddings = embedding_service.batch_generate_embeddings(texts)
        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)
    
    def test_cache_functionality(self, embedding_service):
        """Test caching functionality"""
        text = "test text"
        
        # First call should miss cache
        embedding1 = embedding_service.generate_embedding(text)
        assert embedding_service.cache_misses == 1
        
        # Second call should hit cache
        embedding2 = embedding_service.generate_embedding(text)
        assert embedding_service.cache_hits == 1
        
        # Embeddings should be identical
        assert embedding1 == embedding2


class TestChromaService:
    """Test ChromaDB Service"""
    
    @pytest.fixture
    def chroma_service(self):
        """Create ChromaDB service with mock client"""
        with patch('chromadb.PersistentClient') as mock_client:
            mock_collection = Mock()
            mock_client_instance = Mock()
            mock_client_instance.get_or_create_collection.return_value = mock_collection
            mock_client.return_value = mock_client_instance
            
            service = ChromaService("test_collection", "./test_data")
            service.client = mock_client_instance
            service.collection = mock_collection
            return service
    
    def test_store_chunks(self, chroma_service):
        """Test storing chunks"""
        chunks = [
            {
                "id": "test1",
                "content": "Test content 1",
                "path": "test1.md",
                "heading": "Test 1"
            }
        ]
        embeddings = [[0.1, 0.2, 0.3] * 128]  # 384 dimensions
        
        result = chroma_service.store_chunks(chunks, embeddings)
        assert result["stored"] == 1
        assert result["errors"] == 0
    
    def test_search_similar(self, chroma_service):
        """Test similarity search"""
        # Mock search results
        mock_results = {
            'ids': [['test1']],
            'documents': [['Test content']],
            'metadatas': [[{'path': 'test1.md'}]],
            'distances': [[0.1]]
        }
        chroma_service.collection.query.return_value = mock_results
        
        query_embedding = [0.1, 0.2, 0.3] * 128
        results = chroma_service.search_similar(query_embedding, 5)
        
        assert len(results) == 1
        assert results[0]["content"] == "Test content"
        assert results[0]["similarity"] == 0.9  # 1 - 0.1


class TestSemanticSearchService:
    """Test Semantic Search Service"""
    
    @pytest.fixture
    def search_service(self):
        """Create search service with mocks"""
        mock_chroma_service = Mock()
        mock_embedding_service = Mock()
        
        # Mock embedding generation
        mock_embedding_service.generate_embedding.return_value = [0.1, 0.2, 0.3] * 128
        
        # Mock ChromaDB search
        mock_chroma_service.search_similar.return_value = [
            {
                "id": "test1",
                "content": "Test content",
                "metadata": {"path": "test1.md"},
                "similarity": 0.9
            }
        ]
        
        service = SemanticSearchService(mock_chroma_service, mock_embedding_service)
        return service
    
    def test_search_similar(self, search_service):
        """Test semantic search"""
        results = search_service.search_similar("test query", 5)
        
        assert len(results) == 1
        assert results[0]["content"] == "Test content"
        assert results[0]["similarity"] == 0.9
    
    def test_search_by_keywords(self, search_service):
        """Test keyword search"""
        keywords = ["test", "content"]
        results = search_service.search_by_keywords(keywords, 5)
        
        assert len(results) == 1
        assert "keyword_score" in results[0]
    
    def test_hybrid_search(self, search_service):
        """Test hybrid search"""
        results = search_service.hybrid_search("test query", 5)
        
        assert len(results) == 1
        assert "combined_score" in results[0]


class TestGeminiClient:
    """Test Gemini Client"""
    
    @pytest.fixture
    def gemini_client(self):
        """Create Gemini client with mock"""
        with patch('google.generativeai.GenerativeModel') as mock_model:
            mock_model_instance = Mock()
            mock_response = Mock()
            mock_response.text = "This is a test response from Gemini"
            mock_model_instance.generate_content.return_value = mock_response
            mock_model.return_value = mock_model_instance
            
            client = GeminiClient("test_api_key", "gemini-pro")
            client.model = mock_model_instance
            return client
    
    @pytest.mark.asyncio
    async def test_process_content(self, gemini_client):
        """Test content processing with Gemini"""
        context_chunks = [
            {
                "content": "Test context content",
                "metadata": {"path": "test.md", "heading": "Test"},
                "similarity": 0.9
            }
        ]
        
        result = await gemini_client.process_content("test query", context_chunks)
        
        assert "answer" in result
        assert "sources" in result
        assert "processing_time" in result
        assert result["answer"] == "This is a test response from Gemini"
    
    @pytest.mark.asyncio
    async def test_summarize_content(self, gemini_client):
        """Test content summarization"""
        content = "This is a long piece of content that needs to be summarized."
        summary = await gemini_client.summarize_content(content)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    @pytest.mark.asyncio
    async def test_extract_key_points(self, gemini_client):
        """Test key point extraction"""
        content = "This content has several key points that should be extracted."
        key_points = await gemini_client.extract_key_points(content)
        
        assert isinstance(key_points, list)
        assert len(key_points) > 0


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # This would test the complete workflow from Obsidian API
        # through content processing, embedding generation, storage,
        # search, and Gemini processing
        
        # Mock all external dependencies
        with patch('httpx.AsyncClient'), \
             patch('sentence_transformers.SentenceTransformer'), \
             patch('chromadb.PersistentClient'), \
             patch('google.generativeai.GenerativeModel'):
            
            # Initialize services
            obsidian_client = ObsidianAPIClient("test_key")
            content_processor = ContentProcessor()
            embedding_service = EmbeddingService("test-model")
            chroma_service = ChromaService("test_collection")
            search_service = SemanticSearchService(chroma_service, embedding_service)
            gemini_client = GeminiClient("test_api_key")
            
            # Test workflow
            # 1. Get content from Obsidian
            # 2. Process content into chunks
            # 3. Generate embeddings
            # 4. Store in ChromaDB
            # 5. Search for similar content
            # 6. Process with Gemini
            
            assert True  # Placeholder for actual integration test


# Performance tests
class TestPerformance:
    """Performance tests"""
    
    def test_embedding_generation_performance(self):
        """Test embedding generation performance"""
        import time
        
        with patch('sentence_transformers.SentenceTransformer') as mock_model:
            mock_model_instance = Mock()
            mock_model_instance.encode.return_value = [[0.1, 0.2, 0.3] * 128]
            mock_model.return_value = mock_model_instance
            
            service = EmbeddingService("test-model")
            service.model = mock_model_instance
            
            # Test single embedding
            start_time = time.time()
            service.generate_embedding("test text")
            single_time = time.time() - start_time
            
            # Test batch embeddings
            texts = ["text " + str(i) for i in range(100)]
            start_time = time.time()
            service.batch_generate_embeddings(texts)
            batch_time = time.time() - start_time
            
            # Batch should be faster per embedding
            assert batch_time < single_time * 100
    
    def test_search_performance(self):
        """Test search performance"""
        # This would test search performance with large datasets
        assert True  # Placeholder for performance test


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
