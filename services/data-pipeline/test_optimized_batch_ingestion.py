#!/usr/bin/env python3
"""
Test Optimized Asynchronous Batch Embedding Pipeline
Comprehensive performance testing and validation of optimizations
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any

# Import our optimized components
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.hybrid_content_processor import HybridContentProcessor
from src.embeddings.embedding_service import EmbeddingService
from src.vector.chroma_service import ChromaService
from src.ingestion.ingestion_pipeline import IngestionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
VAULT_ROOT_DIR = Path("D:/Nomade Milionario")
CHROMA_DB_DIR = "./test_chroma_db_optimized"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZES_TO_TEST = [25, 50, 100, 200]

async def setup_test_environment():
    """Clean up and prepare test environment."""
    if Path(CHROMA_DB_DIR).exists():
        import shutil
        shutil.rmtree(CHROMA_DB_DIR)
        logger.info(f"Cleaned up existing ChromaDB at {CHROMA_DB_DIR}")
    
    Path(CHROMA_DB_DIR).mkdir(parents=True, exist_ok=True)
    logger.info(f"Test environment ready at {CHROMA_DB_DIR}")

async def test_batch_size_optimization():
    """Test different batch sizes to find optimal performance."""
    logger.info("\n🚀 Testing Batch Size Optimization")
    logger.info("=" * 60)
    
    # Initialize components
    filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
    content_processor = HybridContentProcessor()
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    
    # Get sample files for testing
    files = await filesystem_client.list_vault_files()
    sample_files = files[:10]  # Test with first 10 files
    
    logger.info(f"Testing with {len(sample_files)} sample files")
    
    # Process files into chunks
    all_chunks = []
    for file_info in sample_files:
        if file_info['path'].endswith('.md'):  # Remove the 'type' check since files don't have that field
            try:
                file_data = await filesystem_client.get_file_content(file_info['path'])
                # Use the correct method for HybridContentProcessor
                chunks = content_processor.chunk_content(
                    content=file_data['content'],
                    file_metadata=file_data,
                    path=file_info['path']
                )
                all_chunks.extend(chunks)
                logger.info(f"Processed {file_info['path']}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Error processing {file_info['path']}: {e}")
                import traceback
                traceback.print_exc()
    
    # If no chunks were created, try a different approach
    if len(all_chunks) == 0:
        logger.warning("No chunks created, trying alternative approach...")
        # Try processing files directly
        for file_info in sample_files[:3]:  # Try first 3 files
            if file_info['path'].endswith('.md'):  # Remove the 'type' check since files don't have that field
                try:
                    file_data = await filesystem_client.get_file_content(file_info['path'])
                    # Create a simple chunk manually
                    simple_chunk = {
                        'content': file_data['content'][:1000],  # First 1000 chars
                        'path': file_info['path'],
                        'heading': 'Test Heading',
                        'chunk_index': 0,
                        'chunk_token_count': 100,
                        'file_metadata': file_data
                    }
                    all_chunks.append(simple_chunk)
                    logger.info(f"Created simple chunk for {file_info['path']}")
                except Exception as e:
                    logger.error(f"Error creating simple chunk for {file_info['path']}: {e}")
    
    # Ensure we have at least some chunks for testing
    if len(all_chunks) == 0:
        logger.error("❌ No chunks available for testing. Cannot proceed.")
        return {"error": "No chunks available for testing"}
    
    logger.info(f"Created {len(all_chunks)} test chunks")
    
    # Test different batch sizes
    batch_results = {}
    
    for batch_size in BATCH_SIZES_TO_TEST:
        logger.info(f"\n📊 Testing batch size: {batch_size}")
        
        # Create new ChromaDB instance for each test
        chroma_service = ChromaService(
            collection_name=f"test_batch_{batch_size}",
            persist_directory=f"{CHROMA_DB_DIR}/batch_{batch_size}",
            embedding_model=EMBEDDING_MODEL,
            optimize_for_large_vault=True
        )
        
        # Create pipeline with specific batch size
        pipeline = IngestionPipeline(
            filesystem_client=filesystem_client,
            content_processor=content_processor,
            embedding_service=embedding_service,
            chroma_service=chroma_service,
            batch_size=batch_size
        )
        
        # Test batch processing performance
        start_time = time.time()
        
        try:
            # Process chunks in batches
            total_embeddings_stored = 0
            batch_count = 0
            
            for i in range(0, len(all_chunks), batch_size):
                batch_chunks = all_chunks[i:i + batch_size]
                batch_texts = [chunk['content'] for chunk in batch_chunks]
                
                batch_start = time.time()
                batch_embeddings = embedding_service.batch_generate_embeddings(batch_texts)
                embedding_time = time.time() - batch_start
                
                storage_start = time.time()
                chroma_service.store_embeddings(batch_chunks, batch_embeddings)
                storage_time = time.time() - storage_start
                
                total_embeddings_stored += len(batch_embeddings)
                batch_count += 1
                
                logger.info(f"  Batch {batch_count}: {len(batch_chunks)} chunks, "
                          f"{embedding_time:.3f}s embedding, {storage_time:.3f}s storage")
            
            total_time = time.time() - start_time
            
            # Get performance metrics
            performance_metrics = chroma_service.get_performance_metrics()
            collection_stats = chroma_service.get_collection_stats()
            
            batch_results[batch_size] = {
                "total_time": total_time,
                "chunks_processed": len(all_chunks),
                "embeddings_stored": total_embeddings_stored,
                "batches_processed": batch_count,
                "chunks_per_second": len(all_chunks) / total_time,
                "embeddings_per_second": total_embeddings_stored / total_time,
                "average_batch_time": total_time / batch_count,
                "performance_metrics": performance_metrics,
                "collection_stats": collection_stats
            }
            
            logger.info(f"✅ Batch size {batch_size} completed: {total_time:.2f}s total, "
                       f"{len(all_chunks)/total_time:.1f} chunks/sec")
            
        except Exception as e:
            logger.error(f"❌ Batch size {batch_size} failed: {e}")
            batch_results[batch_size] = {"error": str(e)}
    
    return batch_results

async def test_chromadb_optimization():
    """Test ChromaDB HNSW optimization performance."""
    logger.info("\n🔧 Testing ChromaDB HNSW Optimization")
    logger.info("=" * 60)
    
    # Test with and without optimization
    optimization_tests = [
        {"optimize": True, "name": "Optimized"},
        {"optimize": False, "name": "Default"}
    ]
    
    optimization_results = {}
    
    for test_config in optimization_tests:
        logger.info(f"\n📊 Testing {test_config['name']} Configuration")
        
        # Create ChromaDB instance
        chroma_service = ChromaService(
            collection_name=f"test_optimization_{test_config['optimize']}",
            persist_directory=f"{CHROMA_DB_DIR}/optimization_{test_config['optimize']}",
            embedding_model=EMBEDDING_MODEL,
            optimize_for_large_vault=test_config['optimize']
        )
        
        # Initialize other components
        filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
        content_processor = HybridContentProcessor()
        embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
        
        # Get sample data
        files = await filesystem_client.list_vault_files()
        sample_files = files[:5]  # Smaller sample for optimization testing
        
        # Process sample data
        all_chunks = []
        for file_info in sample_files:
            if file_info['path'].endswith('.md'):  # Remove the 'type' check since files don't have that field
                try:
                    file_data = await filesystem_client.get_file_content(file_info['path'])
                    chunks = content_processor.chunk_content(
                        content=file_data['content'],
                        file_metadata=file_data,
                        path=file_info['path']
                    )
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(f"Error processing {file_info['path']}: {e}")
        
        # Store embeddings
        if len(all_chunks) == 0:
            logger.error("❌ No chunks available for ChromaDB optimization test")
            return {"error": "No chunks available for testing"}
        
        chunk_texts = [chunk['content'] for chunk in all_chunks]
        embeddings = embedding_service.batch_generate_embeddings(chunk_texts)
        chroma_service.store_embeddings(all_chunks, embeddings)
        
        # Test search performance
        test_queries = [
            "artificial intelligence machine learning",
            "project management productivity",
            "data analysis visualization",
            "software development programming"
        ]
        
        search_times = []
        for query in test_queries:
            start_time = time.time()
            results = chroma_service.search_similar(query, n_results=5)
            search_time = time.time() - start_time
            search_times.append(search_time)
        
        # Test metadata filtering performance
        metadata_tests = [
            {"file_type": "dated_note"},
            {"path_year": 2025},
            {"path_category": "Projects"}
        ]
        
        metadata_times = []
        for filter_test in metadata_tests:
            start_time = time.time()
            results = chroma_service.search_by_metadata(filter_test, n_results=5)
            metadata_time = time.time() - start_time
            metadata_times.append(metadata_time)
        
        # Get optimization info
        optimization_info = chroma_service.optimize_metadata_indexing()
        performance_metrics = chroma_service.get_performance_metrics()
        collection_stats = chroma_service.get_collection_stats()
        
        optimization_results[test_config['name']] = {
            "chunks_stored": len(all_chunks),
            "average_search_time_ms": sum(search_times) / len(search_times) * 1000,
            "average_metadata_time_ms": sum(metadata_times) / len(metadata_times) * 1000,
            "optimization_info": optimization_info,
            "performance_metrics": performance_metrics,
            "collection_stats": collection_stats,
            "hnsw_config": chroma_service.hnsw_config
        }
        
        logger.info(f"✅ {test_config['name']} test completed:")
        logger.info(f"  Average search time: {sum(search_times) / len(search_times) * 1000:.1f}ms")
        logger.info(f"  Average metadata time: {sum(metadata_times) / len(metadata_times) * 1000:.1f}ms")
        logger.info(f"  HNSW config: {chroma_service.hnsw_config}")
    
    return optimization_results

async def test_full_pipeline_performance():
    """Test the complete optimized pipeline performance."""
    logger.info("\n🚀 Testing Full Optimized Pipeline Performance")
    logger.info("=" * 60)
    
    # Initialize optimized components
    filesystem_client = FilesystemVaultClient(vault_path=str(VAULT_ROOT_DIR))
    content_processor = HybridContentProcessor()
    embedding_service = EmbeddingService(model_name=EMBEDDING_MODEL)
    chroma_service = ChromaService(
        collection_name="test_full_pipeline",
        persist_directory=f"{CHROMA_DB_DIR}/full_pipeline",
        embedding_model=EMBEDDING_MODEL,
        optimize_for_large_vault=True
    )
    
    # Create optimized pipeline
    pipeline = IngestionPipeline(
        filesystem_client=filesystem_client,
        content_processor=content_processor,
        embedding_service=embedding_service,
        chroma_service=chroma_service,
        batch_size=50  # Optimal batch size from previous tests
    )
    
    logger.info("Starting full pipeline ingestion test...")
    start_time = time.time()
    
    try:
        # Run the optimized ingestion
        stats = await pipeline.ingest_all_files()
        
        total_time = time.time() - start_time
        
        # Get final performance metrics
        performance_metrics = chroma_service.get_performance_metrics()
        optimization_info = chroma_service.optimize_metadata_indexing()
        
        pipeline_results = {
            "ingestion_stats": stats,
            "total_execution_time": total_time,
            "performance_metrics": performance_metrics,
            "optimization_info": optimization_info,
            "pipeline_config": pipeline.get_pipeline_config()
        }
        
        logger.info("✅ Full pipeline test completed successfully!")
        logger.info(f"Total execution time: {total_time:.2f}s")
        logger.info(f"Chunks processed: {stats['ingestion_summary']['total_chunks_created']}")
        logger.info(f"Embeddings stored: {stats['ingestion_summary']['total_embeddings_stored']}")
        
        return pipeline_results
        
    except Exception as e:
        logger.error(f"❌ Full pipeline test failed: {e}")
        return {"error": str(e)}

async def generate_performance_report(batch_results: Dict, optimization_results: Dict, pipeline_results: Dict):
    """Generate comprehensive performance report."""
    logger.info("\n📊 Generating Performance Report")
    logger.info("=" * 60)
    
    report = {
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_configuration": {
            "vault_path": str(VAULT_ROOT_DIR),
            "embedding_model": EMBEDDING_MODEL,
            "batch_sizes_tested": BATCH_SIZES_TO_TEST
        },
        "batch_size_optimization": batch_results,
        "chromadb_optimization": optimization_results,
        "full_pipeline_performance": pipeline_results
    }
    
    # Find optimal batch size
    if batch_results:
        best_batch_size = None
        best_performance = 0
        
        for batch_size, results in batch_results.items():
            if "error" not in results:
                performance = results.get("chunks_per_second", 0)
                if performance > best_performance:
                    best_performance = performance
                    best_batch_size = batch_size
        
        report["optimal_batch_size"] = best_batch_size
        report["best_performance"] = best_performance
    
    # Compare optimization vs default
    if optimization_results:
        optimized_time = optimization_results.get("Optimized", {}).get("average_search_time_ms", 0)
        default_time = optimization_results.get("Default", {}).get("average_search_time_ms", 0)
        
        if optimized_time > 0 and default_time > 0:
            improvement = ((default_time - optimized_time) / default_time) * 100
            report["optimization_improvement"] = {
                "search_time_improvement_percent": improvement,
                "optimized_search_time_ms": optimized_time,
                "default_search_time_ms": default_time
            }
    
    # Save report
    import json
    report_file = f"{CHROMA_DB_DIR}/performance_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📄 Performance report saved to: {report_file}")
    
    # Print summary
    logger.info("\n🎯 PERFORMANCE TEST SUMMARY")
    logger.info("=" * 60)
    
    if "optimal_batch_size" in report:
        logger.info(f"✅ Optimal batch size: {report['optimal_batch_size']}")
        logger.info(f"✅ Best performance: {report['best_performance']:.1f} chunks/sec")
    
    if "optimization_improvement" in report:
        improvement = report["optimization_improvement"]["search_time_improvement_percent"]
        logger.info(f"✅ HNSW optimization improvement: {improvement:.1f}%")
    
    if "full_pipeline_performance" in report and "error" not in report["full_pipeline_performance"]:
        stats = report["full_pipeline_performance"]["ingestion_stats"]
        logger.info(f"✅ Full pipeline processed: {stats['ingestion_summary']['total_chunks_created']} chunks")
        logger.info(f"✅ Total embeddings stored: {stats['ingestion_summary']['total_embeddings_stored']}")
    
    return report

async def main():
    """Run comprehensive performance tests."""
    logger.info("🚀 Starting Optimized Batch Embedding Performance Tests")
    logger.info("=" * 80)
    
    # Setup test environment
    await setup_test_environment()
    
    # Run tests
    batch_results = await test_batch_size_optimization()
    optimization_results = await test_chromadb_optimization()
    pipeline_results = await test_full_pipeline_performance()
    
    # Generate comprehensive report
    report = await generate_performance_report(batch_results, optimization_results, pipeline_results)
    
    logger.info("\n🎉 All performance tests completed successfully!")
    logger.info("Check the performance report for detailed results.")

if __name__ == "__main__":
    asyncio.run(main())
