#!/usr/bin/env python3
"""
Hybrid Intelligent Content Processor
Intelligently selects between Simple and Advanced chunking based on document characteristics
"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from .content_processor import ContentProcessor

logger = logging.getLogger(__name__)

class SimpleChunkingProcessor:
    """
    Simple chunking approach: Fixed-size chunks with basic overlap
    Optimized for speed and token efficiency
    """
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', 
                 max_chunk_size: int = 512, chunk_overlap: int = 128):
        from transformers import AutoTokenizer
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
        Optimized for speed and token efficiency
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
        """Create a chunk with comprehensive metadata including enhanced fields."""
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
            # Enhanced Metadata Fields
            "path_year": file_metadata.get("path_year"),
            "path_month": file_metadata.get("path_month"),
            "path_day": file_metadata.get("path_day"),
            "path_category": file_metadata.get("path_category", ""),
            "path_subcategory": file_metadata.get("path_subcategory", ""),
            "file_type": file_metadata.get("file_type", ""),
            "content_type": file_metadata.get("content_type", ""),
            "links": file_metadata.get("links", []),
            "chunk_token_count": self._count_tokens(content),
            "chunk_word_count": len(content.split()),
            "chunk_char_count": len(content),
            "file_metadata": file_metadata,
            "file_tags": file_metadata.get("in_content_tags", []) + list(file_metadata.get("frontmatter", {}).get("tags", [])),
            "chunking_method": "simple"  # Mark the method used
        }

class DocumentAnalyzer:
    """Analyzes document characteristics to determine optimal chunking strategy"""
    
    def __init__(self):
        self.heading_patterns = [
            r'^#{1,6}\s+',  # Markdown headings
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS headings
            r'^\d+\.\s+',  # Numbered sections
            r'^[A-Z]\.\s+',  # Lettered sections
        ]
    
    def analyze_document(self, content: str, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze document characteristics to determine optimal chunking strategy
        Returns analysis with recommended approach
        """
        analysis = {
            "file_size": len(content),
            "word_count": len(content.split()),
            "line_count": len(content.split('\n')),
            "heading_count": 0,
            "structure_score": 0.0,
            "complexity_score": 0.0,
            "recommended_method": "simple",
            "confidence": 0.0,
            "reasons": []
        }
        
        # Count headings
        heading_count = 0
        for pattern in self.heading_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            heading_count += len(matches)
        
        analysis["heading_count"] = heading_count
        
        # Calculate structure score (0-1)
        if analysis["line_count"] > 0:
            heading_density = heading_count / analysis["line_count"]
            analysis["structure_score"] = min(1.0, heading_density * 10)  # Scale up heading density
        
        # Calculate complexity score
        # Factors: file size, heading density, frontmatter presence, content tags
        complexity_factors = []
        
        # File size factor (larger files are more complex)
        size_factor = min(1.0, analysis["file_size"] / 10000)  # Normalize to 10KB
        complexity_factors.append(size_factor * 0.3)
        
        # Structure factor (more headings = more structured)
        complexity_factors.append(analysis["structure_score"] * 0.3)
        
        # Frontmatter factor
        if file_metadata.get("has_frontmatter", False):
            complexity_factors.append(0.2)
        
        # Content tags factor
        if file_metadata.get("content_tags"):
            complexity_factors.append(0.2)
        
        analysis["complexity_score"] = sum(complexity_factors)
        
        # Determine recommended method
        if analysis["structure_score"] > 0.1 and analysis["complexity_score"] > 0.3:
            analysis["recommended_method"] = "advanced"
            analysis["confidence"] = min(1.0, analysis["structure_score"] + analysis["complexity_score"])
            analysis["reasons"].append("High structure score and complexity")
        elif analysis["structure_score"] > 0.05:
            analysis["recommended_method"] = "advanced"
            analysis["confidence"] = analysis["structure_score"]
            analysis["reasons"].append("Moderate structure detected")
        else:
            analysis["recommended_method"] = "simple"
            analysis["confidence"] = 1.0 - analysis["structure_score"]
            analysis["reasons"].append("Low structure, simple chunking optimal")
        
        # Override for very large files (use simple for speed)
        if analysis["file_size"] > 50000:  # 50KB+
            analysis["recommended_method"] = "simple"
            analysis["confidence"] = 0.9
            analysis["reasons"].append("Large file, prioritizing speed")
        
        # Override for very small files (use simple)
        if analysis["file_size"] < 1000:  # 1KB
            analysis["recommended_method"] = "simple"
            analysis["confidence"] = 0.9
            analysis["reasons"].append("Small file, simple chunking sufficient")
        
        return analysis

class HybridContentProcessor:
    """
    Hybrid Content Processor that intelligently selects between Simple and Advanced chunking
    based on document characteristics and performance requirements
    """
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', 
                 max_chunk_size: int = 512, chunk_overlap: int = 128,
                 force_method: Optional[str] = None):
        """
        Initialize hybrid processor with intelligent method selection
        
        Args:
            model_name: Embedding model name
            max_chunk_size: Maximum tokens per chunk
            chunk_overlap: Overlap tokens between chunks
            force_method: Force specific method ('simple', 'advanced', or None for auto)
        """
        self.model_name = model_name
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.force_method = force_method
        
        # Initialize processors
        self.simple_processor = SimpleChunkingProcessor(
            model_name=model_name,
            max_chunk_size=max_chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.advanced_processor = ContentProcessor(
            model_name=model_name,
            max_chunk_size=max_chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.analyzer = DocumentAnalyzer()
        
        logger.info(f"Initialized HybridContentProcessor with model: {model_name}, max_chunk_size: {max_chunk_size}, chunk_overlap: {chunk_overlap}")
        if force_method:
            logger.info(f"Force method: {force_method}")
        else:
            logger.info("Auto-selection enabled")

    def chunk_content(self, content: str, file_metadata: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
        """
        Intelligently chunk content using the optimal method
        
        Args:
            content: Document content
            file_metadata: File metadata
            path: File path
            
        Returns:
            List of chunks with method metadata
        """
        # Analyze document if auto-selection is enabled
        if self.force_method:
            method = self.force_method
            confidence = 1.0
            analysis = {"recommended_method": method, "confidence": confidence, "reasons": ["Forced method"]}
        else:
            analysis = self.analyzer.analyze_document(content, file_metadata)
            method = analysis["recommended_method"]
            confidence = analysis["confidence"]
        
        logger.info(f"Document analysis for {path}:")
        logger.info(f"  Structure score: {analysis.get('structure_score', 0):.3f}")
        logger.info(f"  Complexity score: {analysis.get('complexity_score', 0):.3f}")
        logger.info(f"  Recommended method: {method} (confidence: {confidence:.3f})")
        logger.info(f"  Reasons: {', '.join(analysis.get('reasons', []))}")
        
        # Select and execute chunking method
        if method == "advanced":
            chunks = self.advanced_processor.chunk_content(content, file_metadata, path)
            logger.info(f"Used Advanced chunking: {len(chunks)} chunks")
        else:
            chunks = self.simple_processor.chunk_content(content, file_metadata, path)
            logger.info(f"Used Simple chunking: {len(chunks)} chunks")
        
        # Add method metadata to all chunks
        for chunk in chunks:
            chunk["chunking_method"] = method
            chunk["method_confidence"] = confidence
            chunk["document_analysis"] = {
                "structure_score": analysis.get("structure_score", 0),
                "complexity_score": analysis.get("complexity_score", 0),
                "heading_count": analysis.get("heading_count", 0)
            }
        
        return chunks

    def get_method_stats(self) -> Dict[str, Any]:
        """Get statistics about method usage"""
        return {
            "available_methods": ["simple", "advanced"],
            "current_config": {
                "model_name": self.model_name,
                "max_chunk_size": self.max_chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "force_method": self.force_method
            },
            "analyzer_config": {
                "heading_patterns": len(self.analyzer.heading_patterns),
                "auto_selection": self.force_method is None
            }
        }

    def process_multiple_files(self, file_contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple files with intelligent method selection for each
        
        Args:
            file_contents: List of file content dictionaries
            
        Returns:
            List of all chunks from all files with method metadata
        """
        all_chunks = []
        method_usage = {"simple": 0, "advanced": 0}
        
        for file_content in file_contents:
            chunks = self.chunk_content(
                content=file_content["content"],
                file_metadata=file_content["metadata"],
                path=file_content["path"]
            )
            all_chunks.extend(chunks)
            
            # Track method usage
            if chunks:
                method = chunks[0]["chunking_method"]
                method_usage[method] += 1
        
        logger.info(f"Processed {len(file_contents)} files into {len(all_chunks)} total chunks")
        logger.info(f"Method usage: Simple={method_usage['simple']}, Advanced={method_usage['advanced']}")
        
        return all_chunks

# Convenience function for easy testing
async def test_hybrid_processor():
    """Test the hybrid processor with sample data"""
    from src.ingestion.filesystem_client import FilesystemVaultClient
    
    logger.info("🧪 Testing Hybrid Content Processor")
    
    # Setup
    client = FilesystemVaultClient('D:/Nomade Milionario')
    processor = HybridContentProcessor(
        model_name='sentence-transformers/all-MiniLM-L6-v2',
        max_chunk_size=512,
        chunk_overlap=128
    )
    
    # Get test files
    files = await client.list_vault_files()
    if not files:
        logger.error("No files found for testing")
        return
    
    # Test with first few files
    test_files = files[:3]
    
    for file_info in test_files:
        file_data = await client.get_file_content(file_info['path'])
        
        logger.info(f"\n📄 Testing file: {file_info['path']}")
        
        chunks = processor.chunk_content(
            content=file_data['content'],
            file_metadata=file_data['metadata'],
            path=file_info['path']
        )
        
        logger.info(f"   Generated {len(chunks)} chunks")
        logger.info(f"   Method used: {chunks[0]['chunking_method'] if chunks else 'none'}")
        logger.info(f"   Confidence: {chunks[0]['method_confidence'] if chunks else 'none'}")
    
    # Test batch processing
    logger.info(f"\n📦 Testing batch processing with {len(test_files)} files")
    file_contents = []
    for file_info in test_files:
        file_data = await client.get_file_content(file_info['path'])
        file_contents.append({
            "content": file_data['content'],
            "metadata": file_data['metadata'],
            "path": file_info['path']
        })
    
    all_chunks = processor.process_multiple_files(file_contents)
    logger.info(f"   Total chunks: {len(all_chunks)}")
    
    # Analyze method distribution
    method_counts = {}
    for chunk in all_chunks:
        method = chunk['chunking_method']
        method_counts[method] = method_counts.get(method, 0) + 1
    
    logger.info(f"   Method distribution: {method_counts}")
    
    return all_chunks

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_hybrid_processor())
