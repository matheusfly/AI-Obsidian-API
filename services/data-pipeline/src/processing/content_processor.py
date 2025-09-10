#!/usr/bin/env python3
"""
Advanced Intelligent Content Processor
Context-aware chunking with hybrid strategy: heading-based splitting, sliding window with overlap, and sentence boundary detection
"""

from typing import List, Dict, Any, Iterator
from transformers import AutoTokenizer
import logging
import re

logger = logging.getLogger(__name__)

class ContentProcessor:
    """Advanced intelligent content processor with hybrid chunking strategy"""
    
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', max_chunk_size: int = 512, chunk_overlap: int = 128):
        """
        Initialize the content processor with advanced chunking capabilities.
        Args:
            model_name (str): The name of the embedding model for its tokenizer.
            max_chunk_size (int): Maximum number of tokens per chunk.
            chunk_overlap (int): Number of tokens to overlap between chunks.
        """
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Initialized Advanced ContentProcessor with model: {model_name}, max_chunk_size: {max_chunk_size}, chunk_overlap: {chunk_overlap}")

    def _count_tokens(self, text: str) -> int:
        """Count tokens using the embedding model's tokenizer."""
        return len(self.tokenizer.encode(text, truncation=False, add_special_tokens=False))

    def _split_text_by_tokens(self, text: str) -> Iterator[str]:
        """
        Advanced sliding window text splitting with proper tokenization and overlap.
        Uses sentence boundary detection for better chunk boundaries.
        """
        if not text.strip():
            return

        # First, try to split by sentences for better boundaries
        sentences = self._split_by_sentences(text)
        
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_tokens = self.tokenizer.encode(sentence, truncation=False, add_special_tokens=False)
            sentence_size = len(sentence_tokens)
            
            # If adding this sentence would exceed max_chunk_size and we have content
            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                # Yield current chunk
                chunk_text = " ".join(current_chunk).strip()
                if chunk_text:
                    yield chunk_text
                
                # Start new chunk with overlap from previous chunk
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences + [sentence]
                current_size = sum(len(self.tokenizer.encode(s, truncation=False, add_special_tokens=False)) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # Yield final chunk if it has content
        if current_chunk:
            chunk_text = " ".join(current_chunk).strip()
            if chunk_text:
                yield chunk_text

    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentence boundaries using regex patterns."""
        # Enhanced sentence splitting regex that handles common cases
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\s*\n\s*(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences

    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get overlap sentences from the end of current chunk."""
        if not sentences:
            return []
        
        # Calculate how many sentences we need for overlap
        overlap_tokens = 0
        overlap_sentences = []
        
        # Start from the end and work backwards
        for sentence in reversed(sentences):
            sentence_tokens = len(self.tokenizer.encode(sentence, truncation=False, add_special_tokens=False))
            if overlap_tokens + sentence_tokens <= self.chunk_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break
        
        return overlap_sentences

    def chunk_content(self, content: str, file_metadata: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
        """
        Advanced chunking using hybrid strategy: heading-based splitting with sliding window and overlap.
        Args:
            content (str): The markdown content of the file.
            file_metadata (Dict): Metadata extracted by the FilesystemVaultClient.
            path (str): The file's path.
        Returns:
            List[Dict]: A list of chunk dictionaries.
        """
        return self.chunk_by_headings_and_size(content, path, file_metadata)

    def chunk_by_headings_and_size(self, content: str, path: str, file_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Advanced chunking strategy: Primary by headings, secondary by sliding window with overlap.
        """
        chunks = []
        current_section = {"heading": "Introduction", "content": ""}
        chunk_index = 0

        for line in content.split('\n'):
            if line.startswith(('# ', '## ', '### ')):  # H1, H2, H3
                # Finalize the previous section
                if current_section["content"].strip():
                    chunk_index = self._process_section(chunks, current_section, path, file_metadata, chunk_index)
                
                # Start a new section
                heading_text = line.strip('# ').strip()
                current_section = {
                    "heading": heading_text,
                    "content": line + '\n'
                }
            else:
                current_section["content"] += line + '\n'

        # Process the final section
        if current_section["content"].strip():
            self._process_section(chunks, current_section, path, file_metadata, chunk_index)

        logger.info(f"Created {len(chunks)} chunks for file: {path}")
        return chunks

    def _process_section(self, chunks: List[Dict], section: Dict, path: str, file_metadata: Dict[str, Any], chunk_index: int) -> int:
        """
        Process a section: split into smaller chunks if necessary using advanced sliding window.
        Returns updated chunk_index.
        """
        section_content = section["content"].strip()
        if not section_content:
            return chunk_index

        section_tokens = self._count_tokens(section_content)
        
        if section_tokens > self.max_chunk_size:
            # Section is too big, split it using advanced sliding window
            logger.debug(f"Splitting large section '{section['heading']}' ({section_tokens} tokens) into smaller chunks")
            
            for i, small_chunk in enumerate(self._split_text_by_tokens(section_content)):
                chunks.append(self._create_chunk_dict(
                    content=small_chunk,
                    heading=f"{section['heading']} (Part {i+1})",
                    path=path,
                    file_metadata=file_metadata,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
        else:
            # Section is a good size
            chunks.append(self._create_chunk_dict(
                content=section_content,
                heading=section["heading"],
                path=path,
                file_metadata=file_metadata,
                chunk_index=chunk_index
            ))
            chunk_index += 1
        
        return chunk_index


    def _create_chunk_dict(self, content: str, heading: str, path: str, file_metadata: Dict, chunk_index: int) -> Dict[str, Any]:
        """Create a chunk with comprehensive inherited and computed metadata."""
        return {
            # Core Chunk Data
            "content": content,
            "heading": heading,
            "path": path,
            "chunk_index": chunk_index,  # This is the ACTUAL index from the chunking logic
            # Inherited File Metadata (Propagated from FilesystemVaultClient)
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
            # Computed Chunk Metadata
            "chunk_token_count": self._count_tokens(content),  # Pre-computed for ChromaDB
            "chunk_word_count": len(content.split()),
            "chunk_char_count": len(content),
            # Legacy fields for backward compatibility
            "file_metadata": file_metadata,
            "file_tags": file_metadata.get("in_content_tags", []) + list(file_metadata.get("frontmatter", {}).get("tags", []))
        }

    def process_multiple_files(self, file_contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple files and return all chunks.
        Args:
            file_contents (List[Dict]): List of file content dictionaries from FilesystemVaultClient.
        Returns:
            List[Dict]: List of all chunks from all files.
        """
        all_chunks = []
        for file_content in file_contents:
            chunks = self.chunk_content(
                content=file_content["content"],
                file_metadata=file_content["metadata"],
                path=file_content["path"]
            )
            all_chunks.extend(chunks)
        
        logger.info(f"Processed {len(file_contents)} files into {len(all_chunks)} total chunks")
        return all_chunks


class BatchContentProcessor:
    """Batch content processor for handling multiple files efficiently"""
    
    def __init__(self, content_processor: ContentProcessor):
        """
        Initialize batch processor with a content processor instance.
        Args:
            content_processor (ContentProcessor): The content processor to use for chunking.
        """
        self.content_processor = content_processor
        logger.info("Initialized BatchContentProcessor")
    
    def process_batch(self, file_contents: List[Dict[str, Any]], batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Process multiple files in batches for better memory management.
        Args:
            file_contents (List[Dict]): List of file content dictionaries.
            batch_size (int): Number of files to process in each batch.
        Returns:
            List[Dict]: List of all chunks from all files.
        """
        all_chunks = []
        total_files = len(file_contents)
        
        for i in range(0, total_files, batch_size):
            batch = file_contents[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size} ({len(batch)} files)")
            
            batch_chunks = self.content_processor.process_multiple_files(batch)
            all_chunks.extend(batch_chunks)
            
            logger.info(f"Batch completed: {len(batch_chunks)} chunks created")
        
        logger.info(f"Batch processing complete: {total_files} files processed into {len(all_chunks)} total chunks")
        return all_chunks