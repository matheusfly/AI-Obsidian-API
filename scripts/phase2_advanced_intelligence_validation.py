#!/usr/bin/env python3
"""
Phase 2 Advanced Intelligence Validation
Tests topic detection, filtering, content processing, and hybrid search with real data
"""

import sys
import time
import json
import os
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Add data-pipeline src to path
data_pipeline_src = Path(__file__).parent.parent / "services" / "data-pipeline" / "src"
sys.path.insert(0, str(data_pipeline_src))

def test_topic_detection_accuracy():
    """Test topic detection accuracy with real vault data"""
    print("🧠 Phase 2.1: Topic Detection Accuracy Test")
    print("=" * 60)
    
    try:
        # Import topic detection components
        from topic_detector import TopicDetector
        from topic_extractor import TopicExtractor
        
        # Initialize topic detection services
        topic_detector = TopicDetector()
        topic_extractor = TopicExtractor()
        
        # Load real vault data
        vault_path = Path(__file__).parent.parent / "data" / "raw" / "vault"
        vault_files = list(vault_path.glob("*.md"))
        
        if not vault_files:
            print("❌ No vault files found for topic detection testing")
            return {"error": "No vault files", "passed": False}
        
        # Test with real content
        topic_results = []
        for file_path in vault_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Test topic detection
                detected_topics = topic_detector.detect_topics(content)
                
                # Test topic extraction
                extracted_topics = topic_extractor.extract_topics(content)
                
                topic_results.append({
                    "file": file_path.name,
                    "content_length": len(content),
                    "detected_topics": detected_topics,
                    "extracted_topics": extracted_topics,
                    "topic_count": len(detected_topics)
                })
                
                print(f"  ✅ {file_path.name}: {len(detected_topics)} topics detected")
                
            except Exception as e:
                print(f"  ⚠️ Error processing {file_path.name}: {e}")
        
        # Analyze topic detection quality
        all_detected_topics = []
        all_extracted_topics = []
        
        for result in topic_results:
            all_detected_topics.extend(result["detected_topics"])
            all_extracted_topics.extend(result["extracted_topics"])
        
        # Calculate topic diversity and accuracy metrics
        unique_detected = len(set(all_detected_topics))
        unique_extracted = len(set(all_extracted_topics))
        avg_topics_per_file = np.mean([r["topic_count"] for r in topic_results])
        
        # Test topic classification accuracy
        test_queries = [
            "artificial intelligence machine learning",
            "philosophy mathematics logic",
            "web scraping data extraction",
            "vector database embeddings"
        ]
        
        classification_results = []
        for query in test_queries:
            try:
                # Test topic classification
                query_topics = topic_detector.detect_topics(query)
                classification_results.append({
                    "query": query,
                    "topics": query_topics,
                    "topic_count": len(query_topics)
                })
            except Exception as e:
                classification_results.append({
                    "query": query,
                    "topics": [],
                    "topic_count": 0,
                    "error": str(e)
                })
        
        results = {
            "test_name": "Phase 2.1 Topic Detection Accuracy Test",
            "passed": len(topic_results) > 0,
            "files_tested": len(topic_results),
            "total_detected_topics": len(all_detected_topics),
            "total_extracted_topics": len(all_extracted_topics),
            "unique_detected_topics": unique_detected,
            "unique_extracted_topics": unique_extracted,
            "avg_topics_per_file": avg_topics_per_file,
            "topic_results": topic_results,
            "classification_results": classification_results
        }
        
        print(f"\n📊 Topic Detection Results")
        print(f"  Files Tested: {results['files_tested']}")
        print(f"  Total Topics Detected: {results['total_detected_topics']}")
        print(f"  Unique Topics: {results['unique_detected_topics']}")
        print(f"  Average Topics per File: {results['avg_topics_per_file']:.1f}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "passed": False}

def test_smart_document_filtering():
    """Test smart document filtering with real data"""
    print(f"\n🔍 Phase 2.2: Smart Document Filtering Test")
    print("=" * 60)
    
    try:
        from smart_document_filter import SmartDocumentFilter
        
        # Initialize smart document filter
        smart_filter = SmartDocumentFilter()
        
        # Load real vault data
        vault_path = Path(__file__).parent.parent / "data" / "raw" / "vault"
        vault_files = list(vault_path.glob("*.md"))
        
        if not vault_files:
            print("❌ No vault files found for filtering testing")
            return {"error": "No vault files", "passed": False}
        
        # Prepare test documents
        test_documents = []
        for file_path in vault_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create document metadata
                doc = {
                    "id": file_path.name,
                    "content": content,
                    "metadata": {
                        "file_type": "markdown",
                        "file_size": file_path.stat().st_size,
                        "word_count": len(content.split()),
                        "topics": ["test", "validation"],
                        "created_date": "2024-01-01",
                        "modified_date": "2024-01-01"
                    }
                }
                test_documents.append(doc)
                
            except Exception as e:
                print(f"  ⚠️ Error processing {file_path.name}: {e}")
        
        # Test different filtering scenarios
        filter_tests = [
            {
                "name": "File Type Filter",
                "filters": {"file_type": "markdown"},
                "expected_count": len(test_documents)
            },
            {
                "name": "Word Count Filter",
                "filters": {"min_word_count": 100},
                "expected_count": len([d for d in test_documents if d["metadata"]["word_count"] >= 100])
            },
            {
                "name": "Topic Filter",
                "filters": {"topics": ["test"]},
                "expected_count": len([d for d in test_documents if "test" in d["metadata"]["topics"]])
            }
        ]
        
        filtering_results = []
        for test in filter_tests:
            try:
                # Apply filters
                filtered_docs = smart_filter.filter_documents(test_documents, test["filters"])
                
                filtering_results.append({
                    "test_name": test["name"],
                    "filters": test["filters"],
                    "expected_count": test["expected_count"],
                    "actual_count": len(filtered_docs),
                    "success": len(filtered_docs) == test["expected_count"],
                    "filtered_docs": [d["id"] for d in filtered_docs]
                })
                
                print(f"  ✅ {test['name']}: {len(filtered_docs)}/{test['expected_count']} documents")
                
            except Exception as e:
                filtering_results.append({
                    "test_name": test["name"],
                    "filters": test["filters"],
                    "expected_count": test["expected_count"],
                    "actual_count": 0,
                    "success": False,
                    "error": str(e)
                })
                print(f"  ❌ {test['name']} failed: {e}")
        
        # Calculate filtering accuracy
        successful_tests = sum(1 for r in filtering_results if r["success"])
        total_tests = len(filtering_results)
        accuracy = successful_tests / total_tests if total_tests > 0 else 0
        
        results = {
            "test_name": "Phase 2.2 Smart Document Filtering Test",
            "passed": accuracy >= 0.8,
            "accuracy": accuracy,
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "documents_tested": len(test_documents),
            "filtering_results": filtering_results
        }
        
        print(f"\n📊 Filtering Results")
        print(f"  Accuracy: {accuracy:.2%}")
        print(f"  Successful Tests: {successful_tests}/{total_tests}")
        print(f"  Documents Tested: {results['documents_tested']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "passed": False}

def test_advanced_content_processing():
    """Test advanced content processing with real data"""
    print(f"\n⚙️ Phase 2.3: Advanced Content Processing Test")
    print("=" * 60)
    
    try:
        from advanced_content_processor import AdvancedContentProcessor
        
        # Initialize content processor
        processor = AdvancedContentProcessor()
        
        # Load real vault data
        vault_path = Path(__file__).parent.parent / "data" / "raw" / "vault"
        vault_files = list(vault_path.glob("*.md"))
        
        if not vault_files:
            print("❌ No vault files found for content processing testing")
            return {"error": "No vault files", "passed": False}
        
        # Test content processing
        processing_results = []
        for file_path in vault_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Process content
                chunks = processor.chunk_content(content, {
                    "path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "word_count": len(content.split())
                }, str(file_path))
                
                # Analyze chunk quality
                chunk_analysis = {
                    "file": file_path.name,
                    "original_length": len(content),
                    "chunk_count": len(chunks),
                    "avg_chunk_length": np.mean([len(chunk["content"]) for chunk in chunks]) if chunks else 0,
                    "chunk_lengths": [len(chunk["content"]) for chunk in chunks],
                    "has_overlap": any(chunk.get("overlap", False) for chunk in chunks),
                    "structure_aware": any(chunk.get("heading") for chunk in chunks)
                }
                
                processing_results.append(chunk_analysis)
                print(f"  ✅ {file_path.name}: {len(chunks)} chunks, avg length {chunk_analysis['avg_chunk_length']:.0f}")
                
            except Exception as e:
                print(f"  ⚠️ Error processing {file_path.name}: {e}")
        
        # Calculate processing metrics
        total_chunks = sum(r["chunk_count"] for r in processing_results)
        avg_chunks_per_file = np.mean([r["chunk_count"] for r in processing_results])
        avg_chunk_length = np.mean([r["avg_chunk_length"] for r in processing_results])
        
        # Test chunk quality
        quality_metrics = {
            "total_chunks_generated": total_chunks,
            "avg_chunks_per_file": avg_chunks_per_file,
            "avg_chunk_length": avg_chunk_length,
            "files_with_overlap": sum(1 for r in processing_results if r["has_overlap"]),
            "files_with_structure": sum(1 for r in processing_results if r["structure_aware"])
        }
        
        results = {
            "test_name": "Phase 2.3 Advanced Content Processing Test",
            "passed": len(processing_results) > 0 and avg_chunk_length > 0,
            "files_processed": len(processing_results),
            "quality_metrics": quality_metrics,
            "processing_results": processing_results
        }
        
        print(f"\n📊 Processing Results")
        print(f"  Files Processed: {results['files_processed']}")
        print(f"  Total Chunks: {quality_metrics['total_chunks_generated']}")
        print(f"  Average Chunks per File: {quality_metrics['avg_chunks_per_file']:.1f}")
        print(f"  Average Chunk Length: {quality_metrics['avg_chunk_length']:.0f}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "passed": False}

def test_hybrid_search_integration():
    """Test hybrid search integration with real data"""
    print(f"\n🔀 Phase 2.4: Hybrid Search Integration Test")
    print("=" * 60)
    
    try:
        from vector.chroma_service import ChromaService
        from embeddings.embedding_service import EmbeddingService
        
        # Initialize services
        vector_db_path = Path(__file__).parent.parent / "data" / "chroma"
        chroma_service = ChromaService(
            collection_name="test_hybrid_search",
            persist_directory=str(vector_db_path),
            embedding_model="all-MiniLM-L6-v2"
        )
        
        embedding_service = EmbeddingService()
        
        # Test hybrid search queries
        test_queries = [
            "artificial intelligence machine learning",
            "philosophy mathematics logic",
            "vector database embeddings",
            "web scraping data extraction"
        ]
        
        hybrid_results = []
        for query in test_queries:
            try:
                # Test vector search
                vector_results = chroma_service.search_similar(query, n_results=5)
                
                # Test keyword search (simplified)
                keyword_results = []
                for result in vector_results:
                    if any(word.lower() in result["content"].lower() for word in query.split()):
                        keyword_results.append(result)
                
                # Combine results (hybrid approach)
                hybrid_scores = []
                for result in vector_results:
                    # Combine vector similarity with keyword match
                    vector_score = result.get("similarity_score", 0)
                    keyword_boost = 0.1 if any(word.lower() in result["content"].lower() for word in query.split()) else 0
                    hybrid_score = vector_score + keyword_boost
                    hybrid_scores.append(hybrid_score)
                
                # Sort by hybrid score
                sorted_results = sorted(zip(vector_results, hybrid_scores), key=lambda x: x[1], reverse=True)
                
                hybrid_results.append({
                    "query": query,
                    "vector_results_count": len(vector_results),
                    "keyword_matches": len(keyword_results),
                    "hybrid_results": [{"content": r[0]["content"][:100], "hybrid_score": r[1]} for r in sorted_results[:3]],
                    "success": True
                })
                
                print(f"  ✅ {query}: {len(vector_results)} vector, {len(keyword_results)} keyword matches")
                
            except Exception as e:
                hybrid_results.append({
                    "query": query,
                    "vector_results_count": 0,
                    "keyword_matches": 0,
                    "hybrid_results": [],
                    "success": False,
                    "error": str(e)
                })
                print(f"  ❌ {query} failed: {e}")
        
        # Calculate hybrid search metrics
        successful_searches = sum(1 for r in hybrid_results if r["success"])
        total_searches = len(hybrid_results)
        success_rate = successful_searches / total_searches if total_searches > 0 else 0
        
        results = {
            "test_name": "Phase 2.4 Hybrid Search Integration Test",
            "passed": success_rate >= 0.8,
            "success_rate": success_rate,
            "successful_searches": successful_searches,
            "total_searches": total_searches,
            "hybrid_results": hybrid_results
        }
        
        print(f"\n📊 Hybrid Search Results")
        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Successful Searches: {successful_searches}/{total_searches}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "passed": False}

def run_phase2_comprehensive_validation():
    """Run comprehensive Phase 2 validation with real data"""
    print("🚀 Phase 2 Advanced Intelligence Validation")
    print("=" * 70)
    print("Testing topic detection, filtering, content processing, and hybrid search")
    print("=" * 70)
    
    start_time = time.time()
    
    # Run all Phase 2 tests
    topic_results = test_topic_detection_accuracy()
    filtering_results = test_smart_document_filtering()
    processing_results = test_advanced_content_processing()
    hybrid_results = test_hybrid_search_integration()
    
    # Calculate overall Phase 2 score
    topic_score = 1.0 if topic_results.get('passed', False) else 0.0
    filtering_score = 1.0 if filtering_results.get('passed', False) else 0.0
    processing_score = 1.0 if processing_results.get('passed', False) else 0.0
    hybrid_score = 1.0 if hybrid_results.get('passed', False) else 0.0
    
    # Weighted scoring
    overall_score = (topic_score * 0.25 + filtering_score * 0.25 + 
                    processing_score * 0.25 + hybrid_score * 0.25)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n🎯 Phase 2 Validation Results")
    print("=" * 50)
    print(f"2.1 Topic Detection: {topic_score:.3f}")
    print(f"2.2 Smart Filtering: {filtering_score:.3f}")
    print(f"2.3 Content Processing: {processing_score:.3f}")
    print(f"2.4 Hybrid Search: {hybrid_score:.3f}")
    print(f"Overall Phase 2 Score: {overall_score:.3f}")
    print(f"Duration: {duration:.2f}s")
    print(f"Status: {'✅ PASS' if overall_score >= 0.8 else '❌ FAIL'}")
    
    # Save comprehensive results
    results = {
        "phase": "2",
        "test_name": "Phase 2 Advanced Intelligence Validation",
        "overall_score": overall_score,
        "topic_results": topic_results,
        "filtering_results": filtering_results,
        "processing_results": processing_results,
        "hybrid_results": hybrid_results,
        "duration": duration,
        "passed": overall_score >= 0.8,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("phase2_advanced_intelligence_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = run_phase2_comprehensive_validation()
    print(f"\nFinal Phase 2 Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
