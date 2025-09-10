#!/usr/bin/env python3
"""
Deep Technical Comparison: Advanced vs Simple Chunking Approaches
Comprehensive analysis of chunking techniques, performance, and use cases
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Iterator
from transformers import AutoTokenizer
import re
from pathlib import Path

# Import our existing components
from src.ingestion.filesystem_client import FilesystemVaultClient
from src.processing.content_processor import ContentProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleChunkingProcessor:
    """
    Simple chunking approach: Fixed-size chunks with basic overlap
    This represents the traditional approach used in most RAG systems
    """
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', 
                 max_chunk_size: int = 512, chunk_overlap: int = 128):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Initialized SimpleChunkingProcessor: {model_name}, max_chunk_size: {max_chunk_size}, chunk_overlap: {chunk_overlap}")

    def _count_tokens(self, text: str) -> int:
        """Count tokens using the embedding model's tokenizer."""
        return len(self.tokenizer.encode(text, truncation=False, add_special_tokens=False))

    def chunk_content(self, content: str, file_metadata: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
        """
        Simple chunking: Fixed-size sliding window with character-based overlap
        """
        chunks = []
        chunk_index = 0
        
        # Simple sliding window approach
        words = content.split()
        current_chunk_words = []
        current_tokens = 0
        
        for word in words:
            word_tokens = self._count_tokens(word + " ")
            
            if current_tokens + word_tokens > self.max_chunk_size and current_chunk_words:
                # Create chunk
                chunk_text = " ".join(current_chunk_words)
                chunks.append(self._create_chunk_dict(
                    content=chunk_text,
                    heading=f"Chunk {chunk_index + 1}",
                    path=path,
                    file_metadata=file_metadata,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
                
                # Simple overlap: keep last N words
                overlap_words = int(len(current_chunk_words) * 0.25)  # 25% overlap
                current_chunk_words = current_chunk_words[-overlap_words:] + [word]
                current_tokens = self._count_tokens(" ".join(current_chunk_words))
            else:
                current_chunk_words.append(word)
                current_tokens += word_tokens
        
        # Add final chunk
        if current_chunk_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append(self._create_chunk_dict(
                content=chunk_text,
                heading=f"Chunk {chunk_index + 1}",
                path=path,
                file_metadata=file_metadata,
                chunk_index=chunk_index
            ))
        
        logger.info(f"Simple chunking created {len(chunks)} chunks for file: {path}")
        return chunks

    def _create_chunk_dict(self, content: str, heading: str, path: str, file_metadata: Dict, chunk_index: int) -> Dict[str, Any]:
        """Create a chunk with basic metadata."""
        return {
            "content": content,
            "heading": heading,
            "path": path,
            "chunk_index": chunk_index,
            "file_name": file_metadata.get("file_name", ""),
            "file_extension": file_metadata.get("file_extension", ""),
            "directory_path": file_metadata.get("directory_path", ""),
            "file_size": file_metadata.get("file_size", 0),
            "file_modified": file_metadata.get("file_modified", 0),
            "file_created": file_metadata.get("file_created", 0),
            "file_word_count": file_metadata.get("file_word_count", 0),
            "file_char_count": file_metadata.get("file_char_count", 0),
            "has_frontmatter": file_metadata.get("has_frontmatter", False),
            "frontmatter_keys": file_metadata.get("frontmatter_keys", []),
            "frontmatter_tags": file_metadata.get("frontmatter_tags", []),
            "content_tags": file_metadata.get("content_tags", []),
            "chunk_token_count": self._count_tokens(content),
            "chunk_word_count": len(content.split()),
            "chunk_char_count": len(content),
            "file_metadata": file_metadata,
            "file_tags": file_metadata.get("in_content_tags", []) + list(file_metadata.get("frontmatter", {}).get("tags", []))
        }

class ChunkingAnalyzer:
    """Analyzes and compares chunking approaches"""
    
    def __init__(self):
        self.metrics = {}
    
    def analyze_chunks(self, chunks: List[Dict[str, Any]], approach_name: str) -> Dict[str, Any]:
        """Analyze chunk quality and characteristics"""
        if not chunks:
            return {"error": "No chunks to analyze"}
        
        # Basic metrics
        token_counts = [chunk['chunk_token_count'] for chunk in chunks]
        word_counts = [chunk['chunk_word_count'] for chunk in chunks]
        char_counts = [chunk['chunk_char_count'] for chunk in chunks]
        
        # Size distribution analysis
        size_stats = {
            "total_chunks": len(chunks),
            "avg_tokens": sum(token_counts) / len(token_counts),
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
            "std_tokens": self._calculate_std(token_counts),
            "avg_words": sum(word_counts) / len(word_counts),
            "avg_chars": sum(char_counts) / len(char_counts),
        }
        
        # Content coherence analysis
        headings = [chunk['heading'] for chunk in chunks]
        unique_headings = len(set(headings))
        heading_diversity = unique_headings / len(chunks) if chunks else 0
        
        # Token efficiency (how well we utilize the target size)
        target_size = 512  # Default target
        size_efficiency = sum(min(token, target_size) for token in token_counts) / (len(chunks) * target_size)
        
        # Overlap analysis
        overlap_analysis = self._analyze_overlap(chunks)
        
        # Content structure preservation
        structure_preservation = self._analyze_structure_preservation(chunks)
        
        return {
            "approach": approach_name,
            "size_stats": size_stats,
            "heading_diversity": heading_diversity,
            "size_efficiency": size_efficiency,
            "overlap_analysis": overlap_analysis,
            "structure_preservation": structure_preservation,
            "sample_chunks": chunks[:3]  # First 3 chunks for inspection
        }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) <= 1:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _analyze_overlap(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overlap between consecutive chunks"""
        if len(chunks) < 2:
            return {"overlap_detected": False, "avg_overlap": 0}
        
        overlaps = []
        for i in range(len(chunks) - 1):
            current_words = set(chunks[i]['content'].lower().split())
            next_words = set(chunks[i + 1]['content'].lower().split())
            
            if current_words and next_words:
                overlap_ratio = len(current_words & next_words) / len(current_words | next_words)
                overlaps.append(overlap_ratio)
        
        return {
            "overlap_detected": len(overlaps) > 0,
            "avg_overlap": sum(overlaps) / len(overlaps) if overlaps else 0,
            "overlap_samples": overlaps[:3] if overlaps else []
        }
    
    def _analyze_structure_preservation(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well document structure is preserved"""
        # Check for heading preservation
        heading_chunks = [chunk for chunk in chunks if chunk['heading'] != f"Chunk {chunks.index(chunk) + 1}"]
        heading_preservation = len(heading_chunks) / len(chunks) if chunks else 0
        
        # Check for markdown structure
        markdown_elements = 0
        for chunk in chunks:
            content = chunk['content']
            if any(marker in content for marker in ['# ', '## ', '### ', '- ', '* ', '1. ']):
                markdown_elements += 1
        
        structure_preservation = markdown_elements / len(chunks) if chunks else 0
        
        return {
            "heading_preservation": heading_preservation,
            "markdown_structure_preservation": structure_preservation,
            "structured_chunks": len(heading_chunks)
        }
    
    def compare_approaches(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple chunking approaches"""
        comparison = {
            "approaches": results,
            "winner": None,
            "recommendations": []
        }
        
        if len(results) < 2:
            return comparison
        
        # Compare key metrics
        metrics_comparison = {}
        for result in results:
            approach = result['approach']
            metrics_comparison[approach] = {
                "size_efficiency": result['size_efficiency'],
                "heading_diversity": result['heading_diversity'],
                "structure_preservation": result['structure_preservation']['heading_preservation'],
                "avg_tokens": result['size_stats']['avg_tokens'],
                "std_tokens": result['size_stats']['std_tokens']
            }
        
        # Determine winner based on multiple criteria
        scores = {}
        for approach, metrics in metrics_comparison.items():
            score = (
                metrics['size_efficiency'] * 0.3 +  # 30% weight
                metrics['heading_diversity'] * 0.25 +  # 25% weight
                metrics['structure_preservation'] * 0.25 +  # 25% weight
                (1 - metrics['std_tokens'] / metrics['avg_tokens']) * 0.2  # 20% weight for consistency
            )
            scores[approach] = score
        
        winner = max(scores, key=scores.get)
        comparison['winner'] = winner
        comparison['scores'] = scores
        
        # Generate recommendations
        if scores.get('Advanced', 0) > scores.get('Simple', 0):
            comparison['recommendations'].append("Advanced chunking is better for structured documents")
        else:
            comparison['recommendations'].append("Simple chunking might be sufficient for unstructured text")
        
        return comparison

async def run_deep_comparison():
    """Run comprehensive comparison between chunking approaches"""
    logger.info("🔬 Starting Deep Technical Comparison of Chunking Approaches")
    
    # Setup
    client = FilesystemVaultClient('D:/Nomade Milionario')
    analyzer = ChunkingAnalyzer()
    
    # Get test file
    files = await client.list_vault_files()
    if not files:
        logger.error("No files found for comparison")
        return
    
    test_file = files[0]['path']
    file_data = await client.get_file_content(test_file)
    
    logger.info(f"📄 Testing with file: {test_file}")
    logger.info(f"   File size: {len(file_data['content'])} characters")
    logger.info(f"   File tokens: {len(file_data['content'].split())} words")
    
    # Test configurations
    configs = [
        {"max_chunk_size": 256, "chunk_overlap": 64, "name": "Small"},
        {"max_chunk_size": 512, "chunk_overlap": 128, "name": "Medium"},
        {"max_chunk_size": 1024, "chunk_overlap": 256, "name": "Large"}
    ]
    
    all_results = []
    
    for config in configs:
        logger.info(f"\n📊 Testing Configuration: {config['name']} Chunks")
        logger.info(f"   Max Chunk Size: {config['max_chunk_size']} tokens")
        logger.info(f"   Chunk Overlap: {config['chunk_overlap']} tokens")
        
        # Test Simple Chunking
        logger.info("   🔧 Testing Simple Chunking...")
        start_time = time.time()
        simple_processor = SimpleChunkingProcessor(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            max_chunk_size=config['max_chunk_size'],
            chunk_overlap=config['chunk_overlap']
        )
        simple_chunks = simple_processor.chunk_content(file_data['content'], file_data['metadata'], test_file)
        simple_time = time.time() - start_time
        
        # Test Advanced Chunking
        logger.info("   🧠 Testing Advanced Chunking...")
        start_time = time.time()
        advanced_processor = ContentProcessor(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            max_chunk_size=config['max_chunk_size'],
            chunk_overlap=config['chunk_overlap']
        )
        advanced_chunks = advanced_processor.chunk_content(file_data['content'], file_data['metadata'], test_file)
        advanced_time = time.time() - start_time
        
        # Analyze results
        simple_analysis = analyzer.analyze_chunks(simple_chunks, f"Simple-{config['name']}")
        advanced_analysis = analyzer.analyze_chunks(advanced_chunks, f"Advanced-{config['name']}")
        
        # Add timing information
        simple_analysis['processing_time'] = simple_time
        advanced_analysis['processing_time'] = advanced_time
        
        all_results.extend([simple_analysis, advanced_analysis])
        
        # Log detailed comparison
        logger.info(f"   📈 Simple Chunking Results:")
        logger.info(f"      Chunks: {simple_analysis['size_stats']['total_chunks']}")
        logger.info(f"      Avg tokens: {simple_analysis['size_stats']['avg_tokens']:.1f}")
        logger.info(f"      Size efficiency: {simple_analysis['size_efficiency']:.3f}")
        logger.info(f"      Processing time: {simple_time:.3f}s")
        
        logger.info(f"   📈 Advanced Chunking Results:")
        logger.info(f"      Chunks: {advanced_analysis['size_stats']['total_chunks']}")
        logger.info(f"      Avg tokens: {advanced_analysis['size_stats']['avg_tokens']:.1f}")
        logger.info(f"      Size efficiency: {advanced_analysis['size_efficiency']:.3f}")
        logger.info(f"      Heading diversity: {advanced_analysis['heading_diversity']:.3f}")
        logger.info(f"      Processing time: {advanced_time:.3f}s")
        
        # Performance comparison
        speed_ratio = simple_time / advanced_time if advanced_time > 0 else 0
        logger.info(f"   ⚡ Speed comparison: Simple is {speed_ratio:.2f}x {'faster' if speed_ratio > 1 else 'slower'}")
    
    # Overall comparison
    logger.info(f"\n🏆 OVERALL COMPARISON RESULTS")
    logger.info("=" * 60)
    
    # Group results by approach
    simple_results = [r for r in all_results if r['approach'].startswith('Simple')]
    advanced_results = [r for r in all_results if r['approach'].startswith('Advanced')]
    
    # Calculate averages
    def avg_metric(results, metric_path):
        values = []
        for result in results:
            current = result
            for key in metric_path.split('.'):
                current = current.get(key, {})
            if isinstance(current, (int, float)):
                values.append(current)
        return sum(values) / len(values) if values else 0
    
    simple_avg_efficiency = avg_metric(simple_results, 'size_efficiency')
    advanced_avg_efficiency = avg_metric(advanced_results, 'size_efficiency')
    
    simple_avg_diversity = avg_metric(simple_results, 'heading_diversity')
    advanced_avg_diversity = avg_metric(advanced_results, 'heading_diversity')
    
    simple_avg_time = avg_metric(simple_results, 'processing_time')
    advanced_avg_time = avg_metric(advanced_results, 'processing_time')
    
    logger.info(f"📊 SIMPLE CHUNKING AVERAGES:")
    logger.info(f"   Size Efficiency: {simple_avg_efficiency:.3f}")
    logger.info(f"   Heading Diversity: {simple_avg_diversity:.3f}")
    logger.info(f"   Processing Time: {simple_avg_time:.3f}s")
    
    logger.info(f"📊 ADVANCED CHUNKING AVERAGES:")
    logger.info(f"   Size Efficiency: {advanced_avg_efficiency:.3f}")
    logger.info(f"   Heading Diversity: {advanced_avg_diversity:.3f}")
    logger.info(f"   Processing Time: {advanced_avg_time:.3f}s")
    
    # Determine winner
    if advanced_avg_efficiency > simple_avg_efficiency and advanced_avg_diversity > simple_avg_diversity:
        winner = "Advanced Chunking"
        logger.info(f"🏆 WINNER: {winner}")
        logger.info(f"   ✅ Better size efficiency: {advanced_avg_efficiency:.3f} vs {simple_avg_efficiency:.3f}")
        logger.info(f"   ✅ Better structure preservation: {advanced_avg_diversity:.3f} vs {simple_avg_diversity:.3f}")
    elif simple_avg_efficiency > advanced_avg_efficiency:
        winner = "Simple Chunking"
        logger.info(f"🏆 WINNER: {winner}")
        logger.info(f"   ✅ Better size efficiency: {simple_avg_efficiency:.3f} vs {advanced_avg_efficiency:.3f}")
    else:
        winner = "Tie - Both approaches have merits"
        logger.info(f"🏆 RESULT: {winner}")
    
    # Recommendations
    logger.info(f"\n💡 RECOMMENDATIONS:")
    logger.info(f"   🔧 Keep BOTH approaches available!")
    logger.info(f"   📚 Use Advanced chunking for:")
    logger.info(f"      - Structured documents (markdown, technical docs)")
    logger.info(f"      - When semantic coherence is critical")
    logger.info(f"      - Long documents with clear sections")
    logger.info(f"   ⚡ Use Simple chunking for:")
    logger.info(f"      - Unstructured text (chat logs, raw data)")
    logger.info(f"      - When speed is more important than structure")
    logger.info(f"      - Simple documents without headings")
    logger.info(f"   🎯 Hybrid approach: Use Advanced as default, Simple as fallback")
    
    return {
        "simple_results": simple_results,
        "advanced_results": advanced_results,
        "winner": winner,
        "recommendations": "Keep both approaches with intelligent selection"
    }

if __name__ == "__main__":
    asyncio.run(run_deep_comparison())
