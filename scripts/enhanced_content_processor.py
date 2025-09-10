#!/usr/bin/env python3
"""
Enhanced Content Processor with Improved Metadata Extraction
Integrates TopicExtractor for better topic tagging and metadata
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import frontmatter
from transformers import AutoTokenizer

# Add current directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent))

from topic_extractor import TopicExtractor

class EnhancedContentProcessor:
    """Enhanced content processor with improved metadata extraction"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2',
                 max_chunk_size: int = 512, 
                 chunk_overlap: int = 50):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.topic_extractor = TopicExtractor()
        self.logger = logging.getLogger(__name__)
        
        # Content type patterns
        self.content_patterns = {
            'code': r'```[\s\S]*?```|`[^`]+`',
            'headings': r'^#+\s+.+$',
            'lists': r'^\s*[-*+]\s+|^\s*\d+\.\s+',
            'links': r'\[([^\]]+)\]\([^)]+\)',
            'images': r'!\[([^\]]*)\]\([^)]+\)',
            'tables': r'\|.*\|',
            'math': r'\$\$[\s\S]*?\$\$|\$[^$]+\$'
        }
        
        self.logger.info("Enhanced Content Processor initialized")
    
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a single file and return enhanced chunks with metadata
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            List of enhanced chunks with metadata
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file statistics
            stat = file_path.stat()
            
            # Extract comprehensive metadata
            metadata = self.topic_extractor.extract_metadata(content, file_path, stat)
            
            # Parse frontmatter if present
            frontmatter_data = self._extract_frontmatter(content)
            if frontmatter_data:
                metadata.update(frontmatter_data)
            
            # Extract additional content features
            content_features = self._extract_content_features(content)
            metadata.update(content_features)
            
            # Chunk the content
            chunks = self._chunk_content_enhanced(content, metadata, file_path)
            
            # Enhance each chunk with metadata
            enhanced_chunks = []
            for i, chunk in enumerate(chunks):
                enhanced_chunk = self._enhance_chunk(chunk, metadata, i, file_path)
                enhanced_chunks.append(enhanced_chunk)
            
            self.logger.info(f"Processed {file_path.name}: {len(enhanced_chunks)} chunks")
            return enhanced_chunks
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return []
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract frontmatter from content"""
        try:
            post = frontmatter.loads(content)
            if post.metadata:
                return {
                    'frontmatter': post.metadata,
                    'has_frontmatter': True,
                    'frontmatter_keys': list(post.metadata.keys())
                }
        except Exception as e:
            self.logger.debug(f"Frontmatter extraction failed: {e}")
        
        return {'has_frontmatter': False}
    
    def _extract_content_features(self, content: str) -> Dict[str, Any]:
        """Extract additional content features"""
        features = {}
        
        # Extract content patterns
        for pattern_name, pattern in self.content_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            features[f'{pattern_name}_count'] = len(matches)
            if matches:
                features[f'{pattern_name}_examples'] = matches[:3]  # First 3 examples
        
        # Extract structural features
        features['has_headings'] = bool(re.search(r'^#+\s+', content, re.MULTILINE))
        features['has_lists'] = bool(re.search(r'^\s*[-*+]\s+|^\s*\d+\.\s+', content, re.MULTILINE))
        features['has_code'] = bool(re.search(r'```|`[^`]+`', content))
        features['has_links'] = bool(re.search(r'\[([^\]]+)\]\([^)]+\)', content))
        features['has_images'] = bool(re.search(r'!\[([^\]]*)\]\([^)]+\)', content))
        features['has_tables'] = bool(re.search(r'\|.*\|', content))
        features['has_math'] = bool(re.search(r'\$\$|\$[^$]+\$', content))
        
        # Extract reading level indicators
        features['reading_level'] = self._estimate_reading_level(content)
        
        # Extract content structure
        features['structure'] = self._analyze_content_structure(content)
        
        return features
    
    def _estimate_reading_level(self, content: str) -> str:
        """Estimate the reading level of the content"""
        words = content.split()
        sentences = [s for s in content.split('.') if s.strip()]
        
        if not words or not sentences:
            return 'unknown'
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple reading level estimation
        if avg_sentence_length < 10 and avg_word_length < 5:
            return 'beginner'
        elif avg_sentence_length < 15 and avg_word_length < 6:
            return 'intermediate'
        elif avg_sentence_length < 20 and avg_word_length < 7:
            return 'advanced'
        else:
            return 'expert'
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of the content"""
        lines = content.splitlines()
        
        structure = {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'heading_levels': {},
            'paragraph_count': 0,
            'list_count': 0,
            'code_block_count': 0
        }
        
        # Count heading levels
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                structure['heading_levels'][f'h{level}'] = structure['heading_levels'].get(f'h{level}', 0) + 1
        
        # Count paragraphs (consecutive non-empty lines)
        in_paragraph = False
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('-') and not line.startswith('*'):
                if not in_paragraph:
                    structure['paragraph_count'] += 1
                    in_paragraph = True
            else:
                in_paragraph = False
        
        # Count lists
        structure['list_count'] = len([line for line in lines if line.strip().startswith(('-', '*', '+'))])
        
        # Count code blocks
        structure['code_block_count'] = content.count('```')
        
        return structure
    
    def _chunk_content_enhanced(self, content: str, metadata: Dict[str, Any], file_path: Path) -> List[Dict[str, Any]]:
        """Enhanced content chunking with structure awareness"""
        chunks = []
        
        # Split by headings first
        sections = self._split_by_headings(content)
        
        for section in sections:
            section_chunks = self._process_section(section, metadata, file_path)
            chunks.extend(section_chunks)
        
        return chunks
    
    def _split_by_headings(self, content: str) -> List[Dict[str, Any]]:
        """Split content by headings"""
        lines = content.splitlines()
        sections = []
        current_section = {'heading': '', 'content': '', 'level': 0}
        
        for line in lines:
            if line.startswith('#'):
                # Save previous section if it has content
                if current_section['content'].strip():
                    sections.append(current_section)
                
                # Start new section
                level = len(line) - len(line.lstrip('#'))
                heading = line.lstrip('#').strip()
                current_section = {
                    'heading': heading,
                    'content': line + '\n',
                    'level': level
                }
            else:
                current_section['content'] += line + '\n'
        
        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _process_section(self, section: Dict[str, Any], metadata: Dict[str, Any], file_path: Path) -> List[Dict[str, Any]]:
        """Process a section into chunks"""
        content = section['content']
        heading = section['heading']
        level = section['level']
        
        # Check if section needs to be split further
        tokens = self.tokenizer.encode(content)
        
        if len(tokens) <= self.max_chunk_size:
            # Section fits in one chunk
            return [{
                'content': content.strip(),
                'heading': heading,
                'level': level,
                'is_complete_section': True
            }]
        else:
            # Split section into smaller chunks
            return self._split_text_by_tokens(content, heading, level)
    
    def _split_text_by_tokens(self, text: str, heading: str, level: int) -> List[Dict[str, Any]]:
        """Split text by token count with overlap"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.tokenizer.encode(sentence)
            
            if current_tokens + len(sentence_tokens) > self.max_chunk_size and current_chunk:
                # Save current chunk
                chunk_content = '. '.join(current_chunk) + '.'
                chunks.append({
                    'content': chunk_content,
                    'heading': heading,
                    'level': level,
                    'is_complete_section': False
                })
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_tokens = sum(len(self.tokenizer.encode(s)) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_tokens += len(sentence_tokens)
        
        # Add final chunk
        if current_chunk:
            chunk_content = '. '.join(current_chunk) + '.'
            chunks.append({
                'content': chunk_content,
                'heading': heading,
                'level': level,
                'is_complete_section': False
            })
        
        return chunks
    
    def _enhance_chunk(self, chunk: Dict[str, Any], metadata: Dict[str, Any], chunk_index: int, file_path: Path) -> Dict[str, Any]:
        """Enhance a chunk with additional metadata"""
        enhanced_chunk = {
            'content': chunk['content'],
            'heading': chunk['heading'],
            'level': chunk['level'],
            'is_complete_section': chunk['is_complete_section'],
            'chunk_index': chunk_index,
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_extension': file_path.suffix.lower(),
            'chunk_size': len(chunk['content']),
            'chunk_word_count': len(chunk['content'].split()),
            'chunk_character_count': len(chunk['content']),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add file-level metadata
        enhanced_chunk.update({
            'file_size': metadata.get('file_size', 0),
            'file_word_count': metadata.get('word_count', 0),
            'file_character_count': metadata.get('character_count', 0),
            'file_line_count': metadata.get('line_count', 0),
            'last_modified': metadata.get('last_modified', 0),
            'created_time': metadata.get('created_time', 0)
        })
        
        # Add topic information
        enhanced_chunk.update({
            'topics': metadata.get('topics', ['general']),
            'primary_topic': metadata.get('primary_topic', 'general'),
            'key_terms': metadata.get('key_terms', []),
            'technical_terms': metadata.get('technical_terms', [])
        })
        
        # Add content features
        enhanced_chunk.update({
            'language': metadata.get('language', 'unknown'),
            'content_type': metadata.get('content_type', 'unknown'),
            'reading_level': metadata.get('reading_level', 'unknown'),
            'complexity': metadata.get('complexity', {'score': 0.0, 'level': 'simple'})
        })
        
        # Add structural information
        structure = metadata.get('structure', {})
        enhanced_chunk.update({
            'has_headings': metadata.get('has_headings', False),
            'has_lists': metadata.get('has_lists', False),
            'has_code': metadata.get('has_code', False),
            'has_links': metadata.get('has_links', False),
            'has_images': metadata.get('has_images', False),
            'has_tables': metadata.get('has_tables', False),
            'has_math': metadata.get('has_math', False),
            'total_lines': structure.get('total_lines', 0),
            'paragraph_count': structure.get('paragraph_count', 0),
            'list_count': structure.get('list_count', 0),
            'code_block_count': structure.get('code_block_count', 0)
        })
        
        # Add frontmatter information
        enhanced_chunk.update({
            'has_frontmatter': metadata.get('has_frontmatter', False),
            'frontmatter_keys': metadata.get('frontmatter_keys', [])
        })
        
        return enhanced_chunk

# Test the enhanced content processor
if __name__ == "__main__":
    processor = EnhancedContentProcessor()
    
    # Test content
    test_content = """
# Machine Learning Algorithms

Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed.

## Supervised Learning

Supervised learning uses labeled data to train models for prediction tasks. Common algorithms include:

- Linear regression
- Decision trees
- Random forests
- Support vector machines
- Neural networks

## Unsupervised Learning

Unsupervised learning finds patterns in data without labeled examples. Common algorithms include:

- K-means clustering
- Hierarchical clustering
- Principal component analysis
- Autoencoders

## Deep Learning

Deep learning uses multiple layers of neural networks to solve complex problems in computer vision, natural language processing, and speech recognition.

```python
import tensorflow as tf
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])
```

## Applications

Machine learning has applications in:
- Healthcare
- Finance
- Transportation
- Entertainment
- Education
"""
    
    print("🧪 Enhanced Content Processor Test")
    print("=" * 50)
    
    # Create test file
    test_file = Path("test_ml_content.md")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Process file
    chunks = processor.process_file(test_file)
    
    print(f"Processed {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"  Heading: {chunk['heading']}")
        print(f"  Level: {chunk['level']}")
        print(f"  Topics: {chunk['topics']}")
        print(f"  Primary Topic: {chunk['primary_topic']}")
        print(f"  Key Terms: {chunk['key_terms'][:5]}")  # First 5
        print(f"  Content Type: {chunk['content_type']}")
        print(f"  Reading Level: {chunk['reading_level']}")
        print(f"  Has Code: {chunk['has_code']}")
        print(f"  Content: {chunk['content'][:100]}...")
    
    # Clean up
    test_file.unlink()
