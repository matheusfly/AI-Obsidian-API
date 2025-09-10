#!/usr/bin/env python3
"""
Phase 1.2 - Advanced Chunking Strategy Validation
Tests structure-aware processing, overlap handling, and semantic chunking
"""

import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_structure_aware_chunking():
    """Test if chunking respects document structure (headings, sections)"""
    print("🧪 Phase 1.2 - Structure-Aware Chunking Test")
    print("=" * 50)
    
    try:
        from advanced_content_processor import AdvancedContentProcessor
        
        processor = AdvancedContentProcessor()
        
        # Test document with clear structure
        test_content = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on algorithms.

## Supervised Learning

Supervised learning uses labeled training data to learn patterns.

### Classification

Classification algorithms predict discrete categories.

### Regression

Regression algorithms predict continuous values.

## Unsupervised Learning

Unsupervised learning finds patterns in data without labels.

### Clustering

Clustering groups similar data points together.

### Dimensionality Reduction

Dimensionality reduction reduces the number of features.

# Conclusion

Machine learning has many applications in various fields.
"""
        
        # Process the content
        chunks = processor.chunk_content(test_content, {}, "test_document.md")
        
        results = {
            "total_chunks": len(chunks),
            "structure_preserved": True,
            "heading_chunks": 0,
            "content_chunks": 0,
            "chunk_analysis": []
        }
        
        print(f"Generated {len(chunks)} chunks from structured document")
        
        for i, chunk in enumerate(chunks):
            chunk_info = {
                "chunk_id": chunk.get('id', f'chunk_{i}'),
                "heading": chunk.get('heading', 'No heading'),
                "content_length": len(chunk.get('content', '')),
                "word_count": chunk.get('word_count', 0),
                "token_count": chunk.get('token_count', 0)
            }
            
            results["chunk_analysis"].append(chunk_info)
            
            # Check if chunk has proper heading
            if chunk.get('heading') and chunk.get('heading') != 'Introduction':
                results["heading_chunks"] += 1
            else:
                results["content_chunks"] += 1
            
            print(f"Chunk {i+1}: '{chunk.get('heading', 'No heading')}' ({chunk.get('word_count', 0)} words)")
        
        # Validate structure preservation
        expected_headings = [
            "Introduction to Machine Learning",
            "Supervised Learning", 
            "Classification",
            "Regression",
            "Unsupervised Learning",
            "Clustering",
            "Dimensionality Reduction",
            "Conclusion"
        ]
        
        found_headings = [chunk.get('heading') for chunk in chunks if chunk.get('heading')]
        structure_score = len(set(found_headings) & set(expected_headings)) / len(expected_headings)
        
        results["structure_score"] = structure_score
        results["structure_preserved"] = structure_score >= 0.7
        
        print(f"\nStructure Preservation Score: {structure_score:.2f}")
        print(f"Expected Headings: {len(expected_headings)}")
        print(f"Found Headings: {len(found_headings)}")
        print(f"Structure Preserved: {'✅ YES' if results['structure_preserved'] else '❌ NO'}")
        
        return results
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return {"error": str(e), "structure_preserved": False}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "structure_preserved": False}

def test_chunk_overlap_handling():
    """Test if chunking handles overlap correctly"""
    print(f"\n🔄 Phase 1.2 - Chunk Overlap Handling Test")
    print("-" * 45)
    
    try:
        from advanced_content_processor import AdvancedContentProcessor
        
        # Test with different overlap settings
        overlap_tests = [
            {"overlap": 0, "expected_overlap": 0},
            {"overlap": 50, "expected_overlap": 50},
            {"overlap": 100, "expected_overlap": 100}
        ]
        
        results = {
            "overlap_tests": [],
            "all_passed": True
        }
        
        # Long text that will be split into multiple chunks
        long_text = "This is a very long text that will be split into multiple chunks. " * 20
        
        for test in overlap_tests:
            processor = AdvancedContentProcessor(chunk_overlap=test["overlap"])
            chunks = processor.chunk_content(long_text, {}, "test_overlap.md")
            
            if len(chunks) > 1:
                # Calculate actual overlap between consecutive chunks
                chunk1_content = chunks[0].get('content', '')
                chunk2_content = chunks[1].get('content', '')
                
                # Simple overlap calculation (word-based)
                words1 = set(chunk1_content.split())
                words2 = set(chunk2_content.split())
                overlap_words = len(words1 & words2)
                total_words = len(words1 | words2)
                actual_overlap_ratio = overlap_words / total_words if total_words > 0 else 0
                
                test_result = {
                    "expected_overlap": test["expected_overlap"],
                    "chunks_generated": len(chunks),
                    "actual_overlap_ratio": actual_overlap_ratio,
                    "has_overlap": actual_overlap_ratio > 0.1,
                    "passed": actual_overlap_ratio > 0.1 if test["expected_overlap"] > 0 else actual_overlap_ratio < 0.1
                }
            else:
                test_result = {
                    "expected_overlap": test["expected_overlap"],
                    "chunks_generated": len(chunks),
                    "actual_overlap_ratio": 0,
                    "has_overlap": False,
                    "passed": test["expected_overlap"] == 0
                }
            
            results["overlap_tests"].append(test_result)
            
            if not test_result["passed"]:
                results["all_passed"] = False
            
            print(f"Overlap {test['expected_overlap']}: {len(chunks)} chunks, "
                  f"overlap ratio: {test_result['actual_overlap_ratio']:.2f} "
                  f"{'✅' if test_result['passed'] else '❌'}")
        
        print(f"Overlap Handling: {'✅ PASS' if results['all_passed'] else '❌ FAIL'}")
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "all_passed": False}

def test_semantic_chunking_quality():
    """Test semantic chunking quality and coherence"""
    print(f"\n🧠 Phase 1.2 - Semantic Chunking Quality Test")
    print("-" * 45)
    
    try:
        from advanced_content_processor import AdvancedContentProcessor
        
        processor = AdvancedContentProcessor()
        
        # Test with semantically coherent content
        semantic_content = """# Machine Learning Fundamentals

Machine learning is a powerful approach to artificial intelligence that enables computers to learn from data without being explicitly programmed.

## Types of Machine Learning

There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.

### Supervised Learning

Supervised learning algorithms learn from labeled training data to make predictions on new, unseen data. Common algorithms include linear regression, decision trees, and neural networks.

### Unsupervised Learning

Unsupervised learning algorithms find hidden patterns in data without labeled examples. Examples include clustering algorithms like K-means and dimensionality reduction techniques like PCA.

### Reinforcement Learning

Reinforcement learning involves training agents to make decisions through trial and error, receiving rewards or penalties for their actions.

## Applications

Machine learning has numerous applications across various industries, from healthcare and finance to transportation and entertainment.
"""
        
        chunks = processor.chunk_content(semantic_content, {}, "test_semantic.md")
        
        results = {
            "total_chunks": len(chunks),
            "coherent_chunks": 0,
            "average_chunk_size": 0,
            "chunk_quality_scores": []
        }
        
        total_words = 0
        coherent_count = 0
        
        for i, chunk in enumerate(chunks):
            content = chunk.get('content', '')
            word_count = chunk.get('word_count', 0)
            total_words += word_count
            
            # Simple coherence check (contains complete sentences)
            sentences = content.split('.')
            complete_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
            # Quality score based on content length and completeness
            quality_score = min(1.0, word_count / 50) if word_count > 0 else 0
            is_coherent = len(complete_sentences) > 0 and word_count > 20
            
            if is_coherent:
                coherent_count += 1
            
            chunk_quality = {
                "chunk_id": chunk.get('id', f'chunk_{i}'),
                "word_count": word_count,
                "quality_score": quality_score,
                "is_coherent": is_coherent,
                "complete_sentences": len(complete_sentences)
            }
            
            results["chunk_quality_scores"].append(chunk_quality)
            
            print(f"Chunk {i+1}: {word_count} words, quality: {quality_score:.2f}, "
                  f"coherent: {'✅' if is_coherent else '❌'}")
        
        results["coherent_chunks"] = coherent_count
        results["average_chunk_size"] = total_words / len(chunks) if chunks else 0
        results["coherence_ratio"] = coherent_count / len(chunks) if chunks else 0
        
        print(f"\nSemantic Chunking Quality:")
        print(f"Total Chunks: {len(chunks)}")
        print(f"Coherent Chunks: {coherent_count}")
        print(f"Coherence Ratio: {results['coherence_ratio']:.2f}")
        print(f"Average Chunk Size: {results['average_chunk_size']:.1f} words")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "coherence_ratio": 0}

def test_chunking_performance():
    """Test chunking performance with large documents"""
    print(f"\n⚡ Phase 1.2 - Chunking Performance Test")
    print("-" * 45)
    
    try:
        from advanced_content_processor import AdvancedContentProcessor
        import time
        
        processor = AdvancedContentProcessor()
        
        # Create a large document for performance testing
        large_content = "# Performance Test Document\n\n"
        for i in range(100):  # 100 sections
            large_content += f"## Section {i+1}\n\n"
            large_content += f"This is section {i+1} content. " * 50  # 50 words per section
            large_content += "\n\n"
        
        print(f"Testing with document of {len(large_content.split())} words")
        
        start_time = time.time()
        chunks = processor.chunk_content(large_content, {}, "test_performance.md")
        end_time = time.time()
        
        processing_time = end_time - start_time
        words_per_second = len(large_content.split()) / processing_time if processing_time > 0 else 0
        
        results = {
            "document_size_words": len(large_content.split()),
            "chunks_generated": len(chunks),
            "processing_time": processing_time,
            "words_per_second": words_per_second,
            "performance_acceptable": words_per_second > 1000  # At least 1000 words/second
        }
        
        print(f"Performance Results:")
        print(f"Document Size: {len(large_content.split())} words")
        print(f"Chunks Generated: {len(chunks)}")
        print(f"Processing Time: {processing_time:.2f}s")
        print(f"Words/Second: {words_per_second:.0f}")
        print(f"Performance: {'✅ ACCEPTABLE' if results['performance_acceptable'] else '❌ POOR'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "performance_acceptable": False}

def run_comprehensive_chunking_validation():
    """Run comprehensive chunking strategy validation"""
    print("🚀 Phase 1.2 - Comprehensive Chunking Strategy Validation")
    print("=" * 65)
    
    start_time = time.time()
    
    # Run all tests
    structure_results = test_structure_aware_chunking()
    overlap_results = test_chunk_overlap_handling()
    semantic_results = test_semantic_chunking_quality()
    performance_results = test_chunking_performance()
    
    # Calculate overall score
    structure_score = 1.0 if structure_results.get('structure_preserved', False) else 0.0
    overlap_score = 1.0 if overlap_results.get('all_passed', False) else 0.0
    semantic_score = semantic_results.get('coherence_ratio', 0)
    performance_score = 1.0 if performance_results.get('performance_acceptable', False) else 0.0
    
    overall_score = (structure_score * 0.3 + overlap_score * 0.2 + semantic_score * 0.3 + performance_score * 0.2)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n🎯 Phase 1.2 Overall Results")
    print("=" * 40)
    print(f"Structure Score: {structure_score:.3f}")
    print(f"Overlap Score: {overlap_score:.3f}")
    print(f"Semantic Score: {semantic_score:.3f}")
    print(f"Performance Score: {performance_score:.3f}")
    print(f"Overall Score: {overall_score:.3f}")
    print(f"Duration: {duration:.2f}s")
    print(f"Status: {'✅ PASS' if overall_score >= 0.7 else '❌ FAIL'}")
    
    # Save results
    results = {
        "phase": "1.2",
        "test_name": "Chunking Strategy Validation",
        "overall_score": overall_score,
        "structure_results": structure_results,
        "overlap_results": overlap_results,
        "semantic_results": semantic_results,
        "performance_results": performance_results,
        "duration": duration,
        "passed": overall_score >= 0.7
    }
    
    with open("phase1_chunking_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_chunking_validation()
    print(f"\nFinal Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
