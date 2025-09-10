#!/usr/bin/env python3
"""
Advanced Content Processor for Semantic Chunking
"""

from typing import List, Dict, Optional
from transformers import AutoTokenizer
import re
from pathlib import Path
from datetime import datetime

class AdvancedContentProcessor:
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2', 
                 max_chunk_size: int = 512, chunk_overlap: int = 50):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_content(self, content: str, file_metadata: dict, path: str) -> List[dict]:
        """Intelligently chunk content by respecting document structure"""
        chunks = []
        current_section = {"heading": "Introduction", "content_lines": []}
        lines = content.split('\n')
        
        for line in lines:
            # Detect heading levels (H1, H2, H3)
            if line.startswith('# '):
                self._finalize_section(chunks, current_section, file_metadata, path)
                current_section = {"heading": line[2:].strip(), "content_lines": [line]}
            elif line.startswith('## '):
                self._finalize_section(chunks, current_section, file_metadata, path)
                current_section = {"heading": line[3:].strip(), "content_lines": [line]}
            elif line.startswith('### '):
                self._finalize_section(chunks, current_section, file_metadata, path)
                current_section = {"heading": line[4:].strip(), "content_lines": [line]}
            else:
                current_section["content_lines"].append(line)
        
        # Finalize the last section
        self._finalize_section(chunks, current_section, file_metadata, path)
        return chunks

    def _finalize_section(self, chunks: List[dict], section: dict, 
                         file_metadata: dict, path: str):
        """Process a section, splitting if too large"""
        if not section["content_lines"]:
            return
            
        section_content = '\n'.join(section["content_lines"]).strip()
        if not section_content:
            return
            
        # Check if section is too large
        token_count = self._count_tokens(section_content)
        if token_count > self.max_chunk_size:
            # Split into smaller chunks with overlap
            sub_chunks = self._split_text_by_tokens(section_content)
            for i, sub_chunk in enumerate(sub_chunks):
                chunks.append(self._create_chunk(
                    content=sub_chunk,
                    heading=f"{section['heading']} (Part {i+1})",
                    path=path,
                    file_metadata=file_metadata,
                    chunk_index=i
                ))
        else:
            chunks.append(self._create_chunk(
                content=section_content,
                heading=section["heading"],
                path=path,
                file_metadata=file_metadata,
                chunk_index=0
            ))
    
    def _split_text_by_tokens(self, text: str) -> List[str]:
        """Split text into chunks based on token count with overlap"""
        tokens = self.tokenizer.encode(text, truncation=False, add_special_tokens=False)
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + self.max_chunk_size
            if end > len(tokens):
                end = len(tokens)
                
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            chunks.append(chunk_text.strip())
            
            if end == len(tokens):
                break
                
            # Move start for next chunk, accounting for overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
                
        return chunks
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text, truncation=False, add_special_tokens=False))
    
    def _create_chunk(self, content: str, heading: str, path: str, 
                     file_metadata: dict, chunk_index: int) -> dict:
        """Create a chunk with metadata"""
        return {
            "content": content,
            "heading": heading,
            "path": path,
            "chunk_index": chunk_index,
            "word_count": len(content.split()),
            "token_count": self._count_tokens(content),
            "metadata": {
                **file_metadata,
                "chunk_heading": heading,
                "chunk_index": chunk_index,
                "created_at": datetime.now().isoformat()
            }
        }
    
    def process_file(self, file_path: str) -> List[dict]:
        """Process a single file and return chunks"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract basic metadata
            file_metadata = self._extract_file_metadata(file_path, content)
            
            # Chunk the content
            chunks = self.chunk_content(content, file_metadata, file_path)
            
            return chunks
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []
    
    def _extract_file_metadata(self, file_path: str, content: str) -> dict:
        """Extract metadata from file"""
        path_obj = Path(file_path)
        
        # Extract frontmatter if present
        frontmatter_data = {}
        if content.startswith('---'):
            try:
                import frontmatter
                post = frontmatter.loads(content)
                frontmatter_data = post.metadata
            except:
                pass
        
        # Extract tags from content
        tag_pattern = r'#(\w+)'
        tags = re.findall(tag_pattern, content)
        
        return {
            "file_name": path_obj.name,
            "file_stem": path_obj.stem,
            "file_path": str(file_path),
            "file_size": path_obj.stat().st_size,
            "word_count": len(content.split()),
            "tags": tags,
            "frontmatter": frontmatter_data,
            "created_at": datetime.now().isoformat()
        }

# Test the advanced content processor
if __name__ == "__main__":
    processor = AdvancedContentProcessor()
    
    # Test with sample content
    sample_content = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.

## Types of Machine Learning

### Supervised Learning
Supervised learning uses labeled training data to learn a mapping from inputs to outputs.

### Unsupervised Learning
Unsupervised learning finds hidden patterns in data without labeled examples.

## Applications

Machine learning has applications in:
- Computer vision
- Natural language processing
- Recommendation systems
- Predictive analytics

# Conclusion

Machine learning is transforming how we approach complex problems in technology.
"""
    
    print("🔧 Advanced Content Processor Test")
    print("=" * 50)
    
    chunks = processor.chunk_content(
        sample_content, 
        {"title": "ML Guide", "topic": "technology"}, 
        "/test/ml_guide.md"
    )
    
    print(f"Generated {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"  Heading: {chunk['heading']}")
        print(f"  Word Count: {chunk['word_count']}")
        print(f"  Token Count: {chunk['token_count']}")
        print(f"  Content Preview: {chunk['content'][:100]}...")
