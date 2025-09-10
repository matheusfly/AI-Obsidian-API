#!/usr/bin/env python3
"""
Phase 1.3 - Advanced Vector Search Performance Validation
Tests retrieval accuracy, similarity scoring, and ranking quality
"""

import sys
import time
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_retrieval_accuracy():
    """Test vector search retrieval accuracy with known queries"""
    print("🧪 Phase 1.3 - Vector Search Retrieval Accuracy Test")
    print("=" * 55)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test documents with known topics
        test_documents = [
            {
                "id": "doc_1",
                "content": "Machine learning algorithms use statistical methods to find patterns in data and make predictions about future outcomes.",
                "topic": "machine_learning",
                "expected_relevance": "high"
            },
            {
                "id": "doc_2", 
                "content": "Philosophy of mathematics examines the nature of mathematical objects, truth, and the relationship between mathematics and reality.",
                "topic": "philosophy",
                "expected_relevance": "high"
            },
            {
                "id": "doc_3",
                "content": "Web scraping with Python involves using libraries like BeautifulSoup and Scrapy to extract data from websites.",
                "topic": "web_scraping",
                "expected_relevance": "medium"
            },
            {
                "id": "doc_4",
                "content": "Business strategy focuses on competitive advantage, market positioning, and long-term organizational planning.",
                "topic": "business",
                "expected_relevance": "low"
            },
            {
                "id": "doc_5",
                "content": "Cooking recipes often involve precise measurements, timing, and technique to achieve the desired culinary result.",
                "topic": "cooking",
                "expected_relevance": "low"
            }
        ]
        
        # Test queries with expected results
        test_queries = [
            {
                "query": "What are machine learning algorithms?",
                "expected_top_doc": "doc_1",
                "expected_topic": "machine_learning",
                "min_similarity": 0.6
            },
            {
                "query": "Philosophy of mathematics and mathematical truth",
                "expected_top_doc": "doc_2", 
                "expected_topic": "philosophy",
                "min_similarity": 0.6
            },
            {
                "query": "How to scrape websites with Python?",
                "expected_top_doc": "doc_3",
                "expected_topic": "web_scraping", 
                "min_similarity": 0.5
            }
        ]
        
        results = {
            "total_queries": len(test_queries),
            "passed_queries": 0,
            "failed_queries": 0,
            "query_results": [],
            "overall_accuracy": 0.0
        }
        
        for i, test_query in enumerate(test_queries, 1):
            print(f"\nTest Query {i}: '{test_query['query']}'")
            
            # Generate query embedding
            query_embedding = model.encode([test_query['query']])
            
            # Generate document embeddings
            doc_contents = [doc['content'] for doc in test_documents]
            doc_embeddings = model.encode(doc_contents)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
            
            # Get ranked results
            ranked_indices = np.argsort(similarities)[::-1]
            ranked_results = []
            
            for idx in ranked_indices:
                doc = test_documents[idx]
                ranked_results.append({
                    "doc_id": doc['id'],
                    "content": doc['content'][:100] + "...",
                    "topic": doc['topic'],
                    "similarity": float(similarities[idx])
                })
            
            # Check if expected document is in top results
            top_doc_id = ranked_results[0]['doc_id']
            top_similarity = ranked_results[0]['similarity']
            expected_doc_found = top_doc_id == test_query['expected_top_doc']
            similarity_acceptable = top_similarity >= test_query['min_similarity']
            
            query_result = {
                "query": test_query['query'],
                "expected_doc": test_query['expected_top_doc'],
                "actual_top_doc": top_doc_id,
                "top_similarity": top_similarity,
                "expected_doc_found": expected_doc_found,
                "similarity_acceptable": similarity_acceptable,
                "passed": expected_doc_found and similarity_acceptable,
                "all_results": ranked_results
            }
            
            results["query_results"].append(query_result)
            
            if query_result["passed"]:
                results["passed_queries"] += 1
                print(f"✅ PASS - Top doc: {top_doc_id}, Similarity: {top_similarity:.3f}")
            else:
                results["failed_queries"] += 1
                print(f"❌ FAIL - Expected: {test_query['expected_top_doc']}, Got: {top_doc_id}, Similarity: {top_similarity:.3f}")
            
            # Show top 3 results
            print("Top 3 results:")
            for j, result in enumerate(ranked_results[:3]):
                print(f"  {j+1}. {result['doc_id']} ({result['topic']}) - {result['similarity']:.3f}")
        
        results["overall_accuracy"] = results["passed_queries"] / results["total_queries"]
        
        print(f"\n📊 Retrieval Accuracy Summary")
        print(f"Total Queries: {results['total_queries']}")
        print(f"Passed: {results['passed_queries']}")
        print(f"Failed: {results['failed_queries']}")
        print(f"Accuracy: {results['overall_accuracy']:.1%}")
        print(f"Status: {'✅ PASS' if results['overall_accuracy'] >= 0.8 else '❌ FAIL'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "overall_accuracy": 0}

def test_similarity_scoring_quality():
    """Test similarity scoring quality and distribution"""
    print(f"\n📊 Phase 1.3 - Similarity Scoring Quality Test")
    print("-" * 45)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test with different similarity levels
        test_pairs = [
            {
                "text1": "Machine learning algorithms",
                "text2": "Machine learning algorithms",  # Identical
                "expected_similarity": "high",
                "min_threshold": 0.95
            },
            {
                "text1": "Machine learning algorithms",
                "text2": "AI and machine learning methods",  # Very similar
                "expected_similarity": "high",
                "min_threshold": 0.7
            },
            {
                "text1": "Machine learning algorithms", 
                "text2": "Data science and analytics",  # Related
                "expected_similarity": "medium",
                "min_threshold": 0.3
            },
            {
                "text1": "Machine learning algorithms",
                "text2": "Cooking recipes and techniques",  # Unrelated
                "expected_similarity": "low",
                "min_threshold": 0.0
            }
        ]
        
        results = {
            "total_pairs": len(test_pairs),
            "passed_pairs": 0,
            "similarity_distribution": [],
            "scoring_quality": 0.0
        }
        
        similarities = []
        
        for i, pair in enumerate(test_pairs, 1):
            embeddings = model.encode([pair['text1'], pair['text2']])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            similarities.append(similarity)
            
            is_acceptable = similarity >= pair['min_threshold']
            if is_acceptable:
                results["passed_pairs"] += 1
            
            pair_result = {
                "text1": pair['text1'],
                "text2": pair['text2'],
                "similarity": float(similarity),
                "expected_level": pair['expected_similarity'],
                "min_threshold": pair['min_threshold'],
                "passed": is_acceptable
            }
            
            results["similarity_distribution"].append(pair_result)
            
            print(f"Pair {i}: {similarity:.3f} ({pair['expected_similarity']}) {'✅' if is_acceptable else '❌'}")
        
        # Calculate scoring quality metrics
        results["scoring_quality"] = results["passed_pairs"] / results["total_pairs"]
        results["similarity_range"] = {
            "min": float(np.min(similarities)),
            "max": float(np.max(similarities)),
            "mean": float(np.mean(similarities)),
            "std": float(np.std(similarities))
        }
        
        print(f"\nSimilarity Distribution:")
        print(f"Range: {results['similarity_range']['min']:.3f} - {results['similarity_range']['max']:.3f}")
        print(f"Mean: {results['similarity_range']['mean']:.3f}")
        print(f"Std: {results['similarity_range']['std']:.3f}")
        print(f"Quality: {'✅ GOOD' if results['scoring_quality'] >= 0.8 else '❌ POOR'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "scoring_quality": 0}

def test_ranking_quality():
    """Test ranking quality and order preservation"""
    print(f"\n🏆 Phase 1.3 - Ranking Quality Test")
    print("-" * 40)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Test query
        query = "Machine learning and artificial intelligence"
        
        # Documents with known relevance order
        documents = [
            {
                "id": "doc_1",
                "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models.",
                "expected_rank": 1,
                "relevance": "highest"
            },
            {
                "id": "doc_2", 
                "content": "Artificial intelligence encompasses machine learning, deep learning, and other computational approaches.",
                "expected_rank": 2,
                "relevance": "high"
            },
            {
                "id": "doc_3",
                "content": "Data science involves machine learning, statistics, and domain expertise to extract insights.",
                "expected_rank": 3,
                "relevance": "medium"
            },
            {
                "id": "doc_4",
                "content": "Computer programming involves writing code to solve problems and create applications.",
                "expected_rank": 4,
                "relevance": "low"
            },
            {
                "id": "doc_5",
                "content": "Cooking involves following recipes and techniques to prepare food.",
                "expected_rank": 5,
                "relevance": "lowest"
            }
        ]
        
        # Generate embeddings
        query_embedding = model.encode([query])
        doc_contents = [doc['content'] for doc in documents]
        doc_embeddings = model.encode(doc_contents)
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
        
        # Create ranked results
        ranked_indices = np.argsort(similarities)[::-1]
        ranked_results = []
        
        for i, idx in enumerate(ranked_indices):
            doc = documents[idx]
            ranked_results.append({
                "doc_id": doc['id'],
                "content": doc['content'][:80] + "...",
                "expected_rank": doc['expected_rank'],
                "actual_rank": i + 1,
                "similarity": float(similarities[idx]),
                "relevance": doc['relevance']
            })
        
        # Calculate ranking quality metrics
        correct_ranks = sum(1 for result in ranked_results if result['actual_rank'] == result['expected_rank'])
        rank_correlation = np.corrcoef([r['expected_rank'] for r in ranked_results], 
                                     [r['actual_rank'] for r in ranked_results])[0, 1]
        
        results = {
            "total_docs": len(documents),
            "correct_ranks": correct_ranks,
            "rank_accuracy": correct_ranks / len(documents),
            "rank_correlation": float(rank_correlation),
            "ranked_results": ranked_results,
            "ranking_quality": (correct_ranks / len(documents) + abs(rank_correlation)) / 2
        }
        
        print(f"Ranking Quality Results:")
        print(f"Correct Ranks: {correct_ranks}/{len(documents)}")
        print(f"Rank Accuracy: {results['rank_accuracy']:.2f}")
        print(f"Rank Correlation: {results['rank_correlation']:.3f}")
        print(f"Overall Quality: {results['ranking_quality']:.3f}")
        
        print(f"\nActual Ranking:")
        for result in ranked_results:
            status = "✅" if result['actual_rank'] == result['expected_rank'] else "❌"
            print(f"  {result['actual_rank']}. {result['doc_id']} (expected: {result['expected_rank']}) - {result['similarity']:.3f} {status}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "ranking_quality": 0}

def test_search_performance():
    """Test vector search performance and scalability"""
    print(f"\n⚡ Phase 1.3 - Search Performance Test")
    print("-" * 40)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create test documents of varying sizes
        document_sizes = [10, 50, 100, 500, 1000]
        query = "Machine learning algorithms and artificial intelligence"
        
        results = {
            "performance_tests": [],
            "scalability_acceptable": True
        }
        
        for size in document_sizes:
            # Generate test documents
            documents = []
            for i in range(size):
                documents.append({
                    "id": f"doc_{i}",
                    "content": f"Document {i} about machine learning, artificial intelligence, and data science applications in various domains."
                })
            
            # Measure search performance
            start_time = time.time()
            
            # Generate query embedding
            query_embedding = model.encode([query])
            
            # Generate document embeddings
            doc_contents = [doc['content'] for doc in documents]
            doc_embeddings = model.encode(doc_contents)
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
            
            # Rank results
            ranked_indices = np.argsort(similarities)[::-1]
            
            end_time = time.time()
            
            search_time = end_time - start_time
            docs_per_second = size / search_time if search_time > 0 else 0
            
            performance_test = {
                "document_count": size,
                "search_time": search_time,
                "docs_per_second": docs_per_second,
                "performance_acceptable": docs_per_second > 100  # At least 100 docs/second
            }
            
            results["performance_tests"].append(performance_test)
            
            if not performance_test["performance_acceptable"]:
                results["scalability_acceptable"] = False
            
            print(f"Size {size}: {search_time:.3f}s ({docs_per_second:.0f} docs/s) {'✅' if performance_test['performance_acceptable'] else '❌'}")
        
        print(f"\nPerformance Summary:")
        print(f"Scalability: {'✅ ACCEPTABLE' if results['scalability_acceptable'] else '❌ POOR'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e), "scalability_acceptable": False}

def run_comprehensive_vector_search_validation():
    """Run comprehensive vector search performance validation"""
    print("🚀 Phase 1.3 - Comprehensive Vector Search Performance Validation")
    print("=" * 70)
    
    start_time = time.time()
    
    # Run all tests
    accuracy_results = test_retrieval_accuracy()
    scoring_results = test_similarity_scoring_quality()
    ranking_results = test_ranking_quality()
    performance_results = test_search_performance()
    
    # Calculate overall score
    accuracy_score = accuracy_results.get('overall_accuracy', 0)
    scoring_score = scoring_results.get('scoring_quality', 0)
    ranking_score = ranking_results.get('ranking_quality', 0)
    performance_score = 1.0 if performance_results.get('scalability_acceptable', False) else 0.0
    
    overall_score = (accuracy_score * 0.4 + scoring_score * 0.2 + ranking_score * 0.2 + performance_score * 0.2)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n🎯 Phase 1.3 Overall Results")
    print("=" * 40)
    print(f"Accuracy Score: {accuracy_score:.3f}")
    print(f"Scoring Score: {scoring_score:.3f}")
    print(f"Ranking Score: {ranking_score:.3f}")
    print(f"Performance Score: {performance_score:.3f}")
    print(f"Overall Score: {overall_score:.3f}")
    print(f"Duration: {duration:.2f}s")
    print(f"Status: {'✅ PASS' if overall_score >= 0.7 else '❌ FAIL'}")
    
    # Save results
    results = {
        "phase": "1.3",
        "test_name": "Vector Search Performance Validation",
        "overall_score": overall_score,
        "accuracy_results": accuracy_results,
        "scoring_results": scoring_results,
        "ranking_results": ranking_results,
        "performance_results": performance_results,
        "duration": duration,
        "passed": overall_score >= 0.7
    }
    
    with open("phase1_vector_search_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_vector_search_validation()
    print(f"\nFinal Result: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
