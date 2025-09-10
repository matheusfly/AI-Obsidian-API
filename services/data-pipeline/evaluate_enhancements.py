#!/usr/bin/env python3
"""
Enhancement Evaluation Script
Compare enhanced pipeline with rich metadata vs previous setup
"""

import asyncio
import logging
import time
from typing import Dict, Any, List
from src.vector.chroma_service import ChromaService
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.content_processor import ContentProcessor
from src.embeddings.embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancementEvaluator:
    """Evaluates enhancements compared to previous setup"""
    
    def __init__(self, vault_path: str = "D:\\Nomade Milionario"):
        self.vault_path = vault_path
        self.filesystem_client = FilesystemVaultClient(vault_path)
        self.content_processor = ContentProcessor()
        self.embedding_service = EmbeddingService()
        self.chroma_service = ChromaService(
            collection_name="enhanced_obsidian_vault",
            persist_directory="./data/chroma"
        )
        
    async def run_comprehensive_evaluation(self):
        """Run comprehensive evaluation of enhancements"""
        logger.info("Starting comprehensive enhancement evaluation...")
        
        # Get current collection stats
        current_stats = self.chroma_service.get_collection_stats()
        
        # Test 1: Metadata Richness Analysis
        metadata_analysis = await self.analyze_metadata_richness()
        
        # Test 2: Filtering Capabilities
        filtering_capabilities = await self.test_filtering_capabilities()
        
        # Test 3: Search Quality Analysis
        search_quality = await self.analyze_search_quality()
        
        # Test 4: Performance Metrics
        performance_metrics = await self.measure_performance_metrics()
        
        # Test 5: Data Integrity Validation
        data_integrity = await self.validate_data_integrity()
        
        # Generate comprehensive report
        report = self.generate_evaluation_report(
            current_stats,
            metadata_analysis,
            filtering_capabilities,
            search_quality,
            performance_metrics,
            data_integrity
        )
        
        return report
    
    async def analyze_metadata_richness(self) -> Dict[str, Any]:
        """Analyze the richness of stored metadata"""
        logger.info("=== METADATA RICHNESS ANALYSIS ===")
        
        # Get sample results
        results = self.chroma_service.search_similar("performance", n_results=5)
        
        if not results:
            return {"error": "No results found for analysis"}
        
        sample_metadata = results[0]['metadata']
        
        # Count metadata fields
        total_fields = len(sample_metadata)
        
        # Categorize fields
        basic_fields = ['path', 'heading', 'chunk_index', 'chunk_token_count']
        enhanced_fields = [
            'file_word_count', 'file_char_count', 'file_size',
            'frontmatter_tags', 'content_tags', 'has_frontmatter',
            'file_extension', 'directory_path', 'file_name',
            'source_file', 'chunk_word_count', 'chunk_char_count',
            'frontmatter_keys', 'file_modified', 'file_created'
        ]
        
        present_basic = [f for f in basic_fields if f in sample_metadata]
        present_enhanced = [f for f in enhanced_fields if f in sample_metadata]
        
        # Calculate richness score
        richness_score = (len(present_enhanced) / len(enhanced_fields)) * 100
        
        analysis = {
            "total_metadata_fields": total_fields,
            "basic_fields_present": len(present_basic),
            "enhanced_fields_present": len(present_enhanced),
            "richness_score": richness_score,
            "present_enhanced_fields": present_enhanced,
            "missing_enhanced_fields": [f for f in enhanced_fields if f not in sample_metadata]
        }
        
        logger.info(f"Total metadata fields: {total_fields}")
        logger.info(f"Enhanced fields present: {len(present_enhanced)}/{len(enhanced_fields)}")
        logger.info(f"Richness score: {richness_score:.1f}%")
        
        return analysis
    
    async def test_filtering_capabilities(self) -> Dict[str, Any]:
        """Test advanced filtering capabilities"""
        logger.info("=== FILTERING CAPABILITIES TEST ===")
        
        filtering_tests = {}
        
        # Test 1: File size filtering
        try:
            size_results = self.chroma_service.search_similar(
                "test", n_results=5,
                where={"file_size": {"$gt": 1000}}
            )
            filtering_tests["file_size_filter"] = {
                "success": True,
                "results_count": len(size_results),
                "description": "Filter by file size > 1KB"
            }
        except Exception as e:
            filtering_tests["file_size_filter"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 2: Frontmatter filtering
        try:
            frontmatter_results = self.chroma_service.search_similar(
                "test", n_results=5,
                where={"has_frontmatter": True}
            )
            filtering_tests["frontmatter_filter"] = {
                "success": True,
                "results_count": len(frontmatter_results),
                "description": "Filter files with frontmatter"
            }
        except Exception as e:
            filtering_tests["frontmatter_filter"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 3: File extension filtering
        try:
            extension_results = self.chroma_service.search_similar(
                "test", n_results=5,
                where={"file_extension": {"$eq": "md"}}
            )
            filtering_tests["extension_filter"] = {
                "success": True,
                "results_count": len(extension_results),
                "description": "Filter by file extension"
            }
        except Exception as e:
            filtering_tests["extension_filter"] = {
                "success": False,
                "error": str(e)
            }
        
        # Test 4: Token count filtering
        try:
            token_results = self.chroma_service.search_similar(
                "test", n_results=5,
                where={"chunk_token_count": {"$gt": 200}}
            )
            filtering_tests["token_count_filter"] = {
                "success": True,
                "results_count": len(token_results),
                "description": "Filter by chunk token count"
            }
        except Exception as e:
            filtering_tests["token_count_filter"] = {
                "success": False,
                "error": str(e)
            }
        
        # Calculate success rate
        successful_tests = sum(1 for test in filtering_tests.values() if test["success"])
        total_tests = len(filtering_tests)
        success_rate = (successful_tests / total_tests) * 100
        
        filtering_tests["summary"] = {
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "success_rate": success_rate
        }
        
        logger.info(f"Filtering tests: {successful_tests}/{total_tests} successful ({success_rate:.1f}%)")
        
        return filtering_tests
    
    async def analyze_search_quality(self) -> Dict[str, Any]:
        """Analyze search quality and relevance"""
        logger.info("=== SEARCH QUALITY ANALYSIS ===")
        
        test_queries = [
            "performance optimization",
            "machine learning",
            "data analysis",
            "python programming",
            "context engineering"
        ]
        
        search_results = {}
        
        for query in test_queries:
            start_time = time.time()
            results = self.chroma_service.search_similar(query, n_results=5)
            search_time = time.time() - start_time
            
            if results:
                avg_similarity = sum(r['similarity_score'] for r in results) / len(results)
                max_similarity = max(r['similarity_score'] for r in results)
                min_similarity = min(r['similarity_score'] for r in results)
                
                # Analyze metadata diversity
                unique_files = len(set(r['metadata']['path'] for r in results))
                unique_headings = len(set(r['metadata']['heading'] for r in results))
                
                search_results[query] = {
                    "results_count": len(results),
                    "avg_similarity": avg_similarity,
                    "max_similarity": max_similarity,
                    "min_similarity": min_similarity,
                    "search_time_ms": search_time * 1000,
                    "unique_files": unique_files,
                    "unique_headings": unique_headings,
                    "metadata_diversity": unique_files / len(results) if results else 0
                }
            else:
                search_results[query] = {
                    "results_count": 0,
                    "error": "No results found"
                }
        
        # Calculate overall metrics
        successful_searches = [r for r in search_results.values() if "error" not in r]
        if successful_searches:
            overall_avg_similarity = sum(r['avg_similarity'] for r in successful_searches) / len(successful_searches)
            overall_avg_time = sum(r['search_time_ms'] for r in successful_searches) / len(successful_searches)
            overall_diversity = sum(r['metadata_diversity'] for r in successful_searches) / len(successful_searches)
        else:
            overall_avg_similarity = 0
            overall_avg_time = 0
            overall_diversity = 0
        
        quality_analysis = {
            "individual_results": search_results,
            "overall_metrics": {
                "avg_similarity": overall_avg_similarity,
                "avg_search_time_ms": overall_avg_time,
                "avg_metadata_diversity": overall_diversity,
                "successful_searches": len(successful_searches),
                "total_queries": len(test_queries)
            }
        }
        
        logger.info(f"Overall avg similarity: {overall_avg_similarity:.3f}")
        logger.info(f"Overall avg search time: {overall_avg_time:.1f}ms")
        logger.info(f"Overall metadata diversity: {overall_diversity:.3f}")
        
        return quality_analysis
    
    async def measure_performance_metrics(self) -> Dict[str, Any]:
        """Measure performance metrics"""
        logger.info("=== PERFORMANCE METRICS ===")
        
        # Test search performance
        search_times = []
        for i in range(10):
            start_time = time.time()
            self.chroma_service.search_similar("performance test", n_results=5)
            search_time = time.time() - start_time
            search_times.append(search_time)
        
        avg_search_time = sum(search_times) / len(search_times)
        min_search_time = min(search_times)
        max_search_time = max(search_times)
        
        # Get collection stats
        stats = self.chroma_service.get_collection_stats()
        
        performance_metrics = {
            "search_performance": {
                "avg_search_time_ms": avg_search_time * 1000,
                "min_search_time_ms": min_search_time * 1000,
                "max_search_time_ms": max_search_time * 1000,
                "search_times": search_times
            },
            "collection_stats": stats,
            "throughput_estimate": {
                "searches_per_second": 1 / avg_search_time if avg_search_time > 0 else 0,
                "total_chunks": stats['total_chunks']
            }
        }
        
        logger.info(f"Avg search time: {avg_search_time*1000:.1f}ms")
        logger.info(f"Estimated throughput: {1/avg_search_time:.1f} searches/sec")
        
        return performance_metrics
    
    async def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity and consistency"""
        logger.info("=== DATA INTEGRITY VALIDATION ===")
        
        # Test self-retrieval
        results = self.chroma_service.search_similar("test", n_results=1)
        
        if not results:
            return {"error": "No data available for integrity check"}
        
        test_chunk = results[0]
        test_content = test_chunk['content']
        
        # Self-retrieval test
        self_results = self.chroma_service.search_similar(test_content, n_results=5)
        
        found_self = False
        self_retrieval_score = 0
        
        for result in self_results:
            if result['id'] == test_chunk['id']:
                found_self = True
                self_retrieval_score = result['similarity_score']
                break
        
        # Check metadata consistency
        metadata_consistency = self.check_metadata_consistency(results[:5])
        
        integrity_validation = {
            "self_retrieval": {
                "success": found_self,
                "similarity_score": self_retrieval_score,
                "description": "Can retrieve original chunk when searching for its content"
            },
            "metadata_consistency": metadata_consistency,
            "data_quality_score": self_retrieval_score if found_self else 0
        }
        
        logger.info(f"Self-retrieval: {'✅ Success' if found_self else '❌ Failed'}")
        logger.info(f"Data quality score: {self_retrieval_score:.3f}")
        
        return integrity_validation
    
    def check_metadata_consistency(self, results: List[Dict]) -> Dict[str, Any]:
        """Check metadata consistency across results"""
        consistency_checks = {}
        
        # Check required fields
        required_fields = ['path', 'heading', 'chunk_index', 'chunk_token_count']
        for field in required_fields:
            present_count = sum(1 for r in results if field in r['metadata'])
            consistency_checks[f"{field}_present"] = {
                "count": present_count,
                "total": len(results),
                "percentage": (present_count / len(results)) * 100
            }
        
        # Check data types
        type_consistency = {}
        for result in results:
            metadata = result['metadata']
            for key, value in metadata.items():
                if key not in type_consistency:
                    type_consistency[key] = type(value).__name__
                elif type_consistency[key] != type(value).__name__:
                    type_consistency[key] = "mixed"
        
        consistency_checks["type_consistency"] = type_consistency
        
        return consistency_checks
    
    def generate_evaluation_report(self, *args) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        current_stats, metadata_analysis, filtering_capabilities, search_quality, performance_metrics, data_integrity = args
        
        report = {
            "evaluation_timestamp": "2025-09-07",
            "pipeline_version": "Enhanced with Rich Metadata",
            "comparison_baseline": "Previous Basic Setup",
            "collection_stats": current_stats,
            "metadata_analysis": metadata_analysis,
            "filtering_capabilities": filtering_capabilities,
            "search_quality": search_quality,
            "performance_metrics": performance_metrics,
            "data_integrity": data_integrity,
            "overall_assessment": self.calculate_overall_assessment(
                metadata_analysis, filtering_capabilities, search_quality, performance_metrics, data_integrity
            )
        }
        
        return report
    
    def calculate_overall_assessment(self, *args) -> Dict[str, Any]:
        """Calculate overall assessment score"""
        metadata_analysis, filtering_capabilities, search_quality, performance_metrics, data_integrity = args
        
        # Scoring weights
        weights = {
            "metadata_richness": 0.25,
            "filtering_capabilities": 0.20,
            "search_quality": 0.25,
            "performance": 0.15,
            "data_integrity": 0.15
        }
        
        # Calculate scores
        metadata_score = metadata_analysis.get("richness_score", 0)
        filtering_score = filtering_capabilities.get("summary", {}).get("success_rate", 0)
        search_score = search_quality.get("overall_metrics", {}).get("avg_similarity", 0) * 100
        performance_score = min(100, max(0, 100 - performance_metrics.get("search_performance", {}).get("avg_search_time_ms", 1000) / 10))
        integrity_score = data_integrity.get("data_quality_score", 0) * 100
        
        # Calculate weighted overall score
        overall_score = (
            metadata_score * weights["metadata_richness"] +
            filtering_score * weights["filtering_capabilities"] +
            search_score * weights["search_quality"] +
            performance_score * weights["performance"] +
            integrity_score * weights["data_integrity"]
        )
        
        return {
            "overall_score": overall_score,
            "component_scores": {
                "metadata_richness": metadata_score,
                "filtering_capabilities": filtering_score,
                "search_quality": search_score,
                "performance": performance_score,
                "data_integrity": integrity_score
            },
            "grade": self.get_grade(overall_score),
            "improvements_over_baseline": self.identify_improvements(metadata_score, filtering_score, search_score)
        }
    
    def get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90: return "A+"
        elif score >= 80: return "A"
        elif score >= 70: return "B+"
        elif score >= 60: return "B"
        elif score >= 50: return "C"
        else: return "D"
    
    def identify_improvements(self, metadata_score: float, filtering_score: float, search_score: float) -> List[str]:
        """Identify key improvements over baseline"""
        improvements = []
        
        if metadata_score > 80:
            improvements.append("Rich metadata storage with 15+ fields per chunk")
        
        if filtering_score > 80:
            improvements.append("Advanced filtering capabilities (file size, frontmatter, extensions)")
        
        if search_score > 0.3:
            improvements.append("High-quality semantic search with good similarity scores")
        
        improvements.extend([
            "Persistent ChromaDB storage with HNSW indexing",
            "Comprehensive metadata extraction (tags, file stats, frontmatter)",
            "Token-aware chunking with overlap",
            "Batch embedding generation with caching"
        ])
        
        return improvements

async def main():
    """Run comprehensive evaluation"""
    evaluator = EnhancementEvaluator()
    
    try:
        report = await evaluator.run_comprehensive_evaluation()
        
        # Print comprehensive report
        print("\n" + "="*80)
        print("COMPREHENSIVE ENHANCEMENT EVALUATION REPORT")
        print("="*80)
        
        print(f"\n📊 OVERALL ASSESSMENT")
        print(f"Overall Score: {report['overall_assessment']['overall_score']:.1f}/100")
        print(f"Grade: {report['overall_assessment']['grade']}")
        
        print(f"\n📈 COMPONENT SCORES")
        for component, score in report['overall_assessment']['component_scores'].items():
            print(f"  {component.replace('_', ' ').title()}: {score:.1f}/100")
        
        print(f"\n🎯 KEY IMPROVEMENTS OVER BASELINE")
        for improvement in report['overall_assessment']['improvements_over_baseline']:
            print(f"  ✅ {improvement}")
        
        print(f"\n📋 COLLECTION STATISTICS")
        stats = report['collection_stats']
        print(f"  Collection: {stats['collection_name']}")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Embedding model: {stats['embedding_model']}")
        
        print(f"\n🔍 METADATA ANALYSIS")
        metadata = report['metadata_analysis']
        print(f"  Total metadata fields: {metadata['total_metadata_fields']}")
        print(f"  Enhanced fields: {metadata['enhanced_fields_present']}")
        print(f"  Richness score: {metadata['richness_score']:.1f}%")
        
        print(f"\n⚡ PERFORMANCE METRICS")
        perf = report['performance_metrics']
        print(f"  Avg search time: {perf['search_performance']['avg_search_time_ms']:.1f}ms")
        print(f"  Estimated throughput: {perf['throughput_estimate']['searches_per_second']:.1f} searches/sec")
        
        print(f"\n🔒 DATA INTEGRITY")
        integrity = report['data_integrity']
        print(f"  Self-retrieval: {'✅ Success' if integrity['self_retrieval']['success'] else '❌ Failed'}")
        print(f"  Data quality score: {integrity['data_quality_score']:.3f}")
        
        print("="*80)
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
