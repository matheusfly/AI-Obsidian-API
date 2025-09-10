#!/usr/bin/env python3
"""
Test the Hybrid Content Processor
"""

import asyncio
import logging
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.hybrid_content_processor import HybridContentProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_hybrid_processor():
    """Test the hybrid processor with different configurations"""
    logger.info("🧪 Testing Hybrid Content Processor")
    
    # Setup
    client = FilesystemVaultClient('D:/Nomade Milionario')
    
    # Test configurations
    configs = [
        {"max_chunk_size": 256, "chunk_overlap": 64, "name": "Small"},
        {"max_chunk_size": 512, "chunk_overlap": 128, "name": "Medium"},
        {"force_method": "simple", "name": "Force Simple"},
        {"force_method": "advanced", "name": "Force Advanced"}
    ]
    
    # Get test files
    files = await client.list_vault_files()
    if not files:
        logger.error("No files found for testing")
        return
    
    # Test with first file
    test_file = files[0]['path']
    file_data = await client.get_file_content(test_file)
    
    logger.info(f"📄 Testing with file: {test_file}")
    logger.info(f"   File size: {len(file_data['content'])} characters")
    logger.info(f"   Word count: {len(file_data['content'].split())} words")
    
    results = []
    
    for config in configs:
        logger.info(f"\n🔧 Testing Configuration: {config['name']}")
        
        # Create processor
        processor = HybridContentProcessor(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            max_chunk_size=config.get('max_chunk_size', 512),
            chunk_overlap=config.get('chunk_overlap', 128),
            force_method=config.get('force_method')
        )
        
        # Process content
        chunks = processor.chunk_content(
            content=file_data['content'],
            file_metadata=file_data['metadata'],
            path=test_file
        )
        
        # Analyze results
        if chunks:
            method = chunks[0]['chunking_method']
            confidence = chunks[0]['method_confidence']
            structure_score = chunks[0]['document_analysis']['structure_score']
            complexity_score = chunks[0]['document_analysis']['complexity_score']
            
            # Calculate chunk statistics
            token_counts = [chunk['chunk_token_count'] for chunk in chunks]
            avg_tokens = sum(token_counts) / len(token_counts)
            max_tokens = max(token_counts)
            min_tokens = min(token_counts)
            
            result = {
                "config": config['name'],
                "method": method,
                "confidence": confidence,
                "structure_score": structure_score,
                "complexity_score": complexity_score,
                "chunks": len(chunks),
                "avg_tokens": avg_tokens,
                "max_tokens": max_tokens,
                "min_tokens": min_tokens
            }
            results.append(result)
            
            logger.info(f"   Method: {method}")
            logger.info(f"   Confidence: {confidence:.3f}")
            logger.info(f"   Structure Score: {structure_score:.3f}")
            logger.info(f"   Complexity Score: {complexity_score:.3f}")
            logger.info(f"   Chunks: {len(chunks)}")
            logger.info(f"   Avg Tokens: {avg_tokens:.1f}")
            logger.info(f"   Token Range: {min_tokens}-{max_tokens}")
        else:
            logger.warning(f"   No chunks generated for {config['name']}")
    
    # Summary
    logger.info(f"\n📊 SUMMARY RESULTS")
    logger.info("=" * 60)
    
    for result in results:
        logger.info(f"{result['config']:15} | {result['method']:8} | {result['chunks']:3} chunks | {result['avg_tokens']:6.1f} avg tokens | {result['confidence']:.3f} conf")
    
    # Recommendations
    logger.info(f"\n💡 RECOMMENDATIONS:")
    
    # Find best performing configurations
    auto_results = [r for r in results if not r['config'].startswith('Force')]
    if auto_results:
        best_auto = max(auto_results, key=lambda x: x['confidence'])
        logger.info(f"   🎯 Best auto-selection: {best_auto['config']} ({best_auto['method']})")
    
    simple_results = [r for r in results if r['method'] == 'simple']
    advanced_results = [r for r in results if r['method'] == 'advanced']
    
    if simple_results and advanced_results:
        avg_simple_tokens = sum(r['avg_tokens'] for r in simple_results) / len(simple_results)
        avg_advanced_tokens = sum(r['avg_tokens'] for r in advanced_results) / len(advanced_results)
        
        logger.info(f"   📈 Simple chunking average: {avg_simple_tokens:.1f} tokens")
        logger.info(f"   📈 Advanced chunking average: {avg_advanced_tokens:.1f} tokens")
        
        if avg_simple_tokens > avg_advanced_tokens:
            logger.info(f"   ✅ Simple chunking is more token-efficient")
        else:
            logger.info(f"   ✅ Advanced chunking is more token-efficient")
    
    logger.info(f"   🔧 Recommendation: Keep both methods with intelligent auto-selection!")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_hybrid_processor())
