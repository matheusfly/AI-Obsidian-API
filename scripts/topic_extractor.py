#!/usr/bin/env python3
"""
Advanced Topic Extractor with NLP-based Topic Tagging
Fix #4: Improve Metadata Extraction & Topic Tagging
"""

import re
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from collections import Counter
from pathlib import Path

# Try to import spaCy, install if not available
try:
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS
except ImportError:
    print("spaCy not found. Installing...")
    os.system("pip install spacy")
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS

# Try to load English model, download if not available
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("English spaCy model not found. Downloading...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:
    print("scikit-learn not found. Installing...")
    os.system("pip install scikit-learn")
    from sklearn.feature_extraction.text import TfidfVectorizer

class TopicExtractor:
    """Advanced topic extractor using spaCy and TF-IDF"""
    
    def __init__(self, top_n_topics: int = 3, min_word_length: int = 3):
        self.top_n_topics = top_n_topics
        self.min_word_length = min_word_length
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.8
        )
        self.logger = logging.getLogger(__name__)
        
        # Common terms to filter out
        self.common_terms = {
            'note', 'file', 'document', 'section', 'chapter', 'topic', 'content',
            'text', 'data', 'information', 'details', 'example', 'case', 'study',
            'method', 'approach', 'technique', 'strategy', 'solution', 'problem',
            'issue', 'challenge', 'opportunity', 'benefit', 'advantage', 'disadvantage',
            'pros', 'cons', 'point', 'aspect', 'feature', 'characteristic', 'property',
            'element', 'component', 'part', 'piece', 'item', 'thing', 'object',
            'concept', 'idea', 'thought', 'notion', 'understanding', 'knowledge',
            'learning', 'education', 'training', 'development', 'improvement',
            'enhancement', 'optimization', 'performance', 'efficiency', 'effectiveness'
        }
        
        # Technical terms that should be prioritized
        self.technical_terms = {
            'machine learning', 'artificial intelligence', 'neural network', 'deep learning',
            'algorithm', 'data structure', 'database', 'programming', 'software',
            'hardware', 'system', 'architecture', 'framework', 'library', 'api',
            'interface', 'protocol', 'standard', 'specification', 'implementation',
            'deployment', 'configuration', 'optimization', 'performance', 'scalability',
            'security', 'authentication', 'authorization', 'encryption', 'cryptography',
            'blockchain', 'distributed', 'microservices', 'containerization', 'docker',
            'kubernetes', 'cloud', 'aws', 'azure', 'gcp', 'devops', 'ci/cd',
            'testing', 'quality assurance', 'monitoring', 'logging', 'analytics',
            'business intelligence', 'data science', 'statistics', 'mathematics',
            'physics', 'chemistry', 'biology', 'medicine', 'healthcare', 'finance',
            'economics', 'marketing', 'sales', 'customer', 'user', 'experience',
            'design', 'ui', 'ux', 'frontend', 'backend', 'fullstack', 'mobile',
            'web', 'desktop', 'application', 'platform', 'service', 'product'
        }
        
        self.logger.info("TopicExtractor initialized with spaCy and TF-IDF")
    
    def extract_topics(self, content: str) -> List[str]:
        """
        Extract meaningful topics from content using NLP
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of extracted topics
        """
        if not content or len(content.strip()) < 10:
            return ['general']
        
        try:
            # Process with spaCy
            doc = nlp(content)
            
            # Extract noun phrases and entities
            topics = []
            
            # 1. Extract noun phrases
            noun_phrases = self._extract_noun_phrases(doc)
            topics.extend(noun_phrases)
            
            # 2. Extract named entities
            entities = self._extract_entities(doc)
            topics.extend(entities)
            
            # 3. Extract key terms using TF-IDF
            key_terms = self._extract_key_terms_tfidf(content)
            topics.extend(key_terms)
            
            # 4. Extract technical terms
            technical = self._extract_technical_terms(content)
            topics.extend(technical)
            
            # 5. Filter and rank topics
            filtered_topics = self._filter_and_rank_topics(topics)
            
            return filtered_topics[:self.top_n_topics]
            
        except Exception as e:
            self.logger.error(f"Topic extraction failed: {e}")
            return ['general']
    
    def _extract_noun_phrases(self, doc) -> List[str]:
        """Extract noun phrases from spaCy document"""
        noun_phrases = []
        
        for chunk in doc.noun_chunks:
            # Clean and filter noun phrases
            text = chunk.text.lower().strip()
            
            # Skip if too short or common
            if (len(text) < self.min_word_length or 
                text in self.common_terms or
                any(char.isdigit() for char in text) or
                len(text.split()) > 4):  # Skip very long phrases
                continue
            
            # Check if it contains meaningful words
            words = text.split()
            meaningful_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
            
            if len(meaningful_words) >= 1:
                noun_phrases.append(text)
        
        return noun_phrases
    
    def _extract_entities(self, doc) -> List[str]:
        """Extract named entities from spaCy document"""
        entities = []
        
        for ent in doc.ents:
            # Filter entity types
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'TECHNOLOGY', 'EVENT']:
                text = ent.text.lower().strip()
                
                # Skip if too short or common
                if (len(text) < self.min_word_length or 
                    text in self.common_terms or
                    any(char.isdigit() for char in text)):
                    continue
                
                entities.append(text)
        
        return entities
    
    def _extract_key_terms_tfidf(self, content: str) -> List[str]:
        """Extract key terms using TF-IDF"""
        try:
            # Split content into sentences
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            if len(sentences) < 2:
                return []
            
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.vectorizer.fit_transform(sentences)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top terms
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            top_indices = np.argsort(mean_scores)[-20:]  # Top 20 terms
            
            key_terms = []
            for idx in top_indices:
                term = feature_names[idx]
                if (len(term) >= self.min_word_length and 
                    term not in self.common_terms and
                    not any(char.isdigit() for char in term)):
                    key_terms.append(term)
            
            return key_terms
            
        except Exception as e:
            self.logger.error(f"TF-IDF extraction failed: {e}")
            return []
    
    def _extract_technical_terms(self, content: str) -> List[str]:
        """Extract technical terms from content"""
        content_lower = content.lower()
        found_terms = []
        
        for term in self.technical_terms:
            if term in content_lower:
                found_terms.append(term)
        
        return found_terms
    
    def _filter_and_rank_topics(self, topics: List[str]) -> List[str]:
        """Filter and rank topics by relevance and frequency"""
        if not topics:
            return ['general']
        
        # Count frequency
        topic_counts = Counter(topics)
        
        # Filter out very common or very rare topics
        total_topics = len(topics)
        filtered_topics = []
        
        for topic, count in topic_counts.items():
            frequency = count / total_topics
            
            # Keep topics that appear at least once and aren't too common
            if 0.01 <= frequency <= 0.5:  # 1% to 50% frequency
                filtered_topics.append((topic, count, frequency))
        
        # Sort by frequency and length (prefer shorter, more frequent terms)
        filtered_topics.sort(key=lambda x: (x[1], -len(x[0])), reverse=True)
        
        # Extract just the topic names
        ranked_topics = [topic for topic, count, freq in filtered_topics]
        
        # Ensure we have at least one topic
        if not ranked_topics:
            ranked_topics = ['general']
        
        return ranked_topics
    
    def extract_metadata(self, content: str, file_path: Path, stat: os.stat_result) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from content and file
        
        Args:
            content: File content
            file_path: Path to file
            stat: File statistics
            
        Returns:
            Dictionary with extracted metadata
        """
        try:
            # Basic file metadata
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_extension': file_path.suffix.lower(),
                'file_size': stat.st_size,
                'word_count': len(content.split()),
                'character_count': len(content),
                'line_count': len(content.splitlines()),
                'last_modified': stat.st_mtime,
                'created_time': stat.st_ctime
            }
            
            # Extract topics
            topics = self.extract_topics(content)
            metadata['topics'] = topics
            metadata['primary_topic'] = topics[0] if topics else 'general'
            
            # Extract key terms
            key_terms = self._extract_key_terms_tfidf(content)
            metadata['key_terms'] = key_terms[:10]  # Top 10 key terms
            
            # Generate content summary
            summary = self._generate_summary(content)
            metadata['content_summary'] = summary
            
            # Extract technical terms
            technical_terms = self._extract_technical_terms(content)
            metadata['technical_terms'] = technical_terms
            
            # Extract language indicators
            language = self._detect_language(content)
            metadata['language'] = language
            
            # Extract content type
            content_type = self._classify_content_type(content, file_path)
            metadata['content_type'] = content_type
            
            # Extract complexity metrics
            complexity = self._calculate_complexity(content)
            metadata['complexity'] = complexity
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'topics': ['general'],
                'primary_topic': 'general',
                'error': str(e)
            }
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a summary of the content"""
        if not content:
            return ""
        
        # Split into sentences
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        if len(sentences) <= 2:
            return content[:max_length] + "..." if len(content) > max_length else content
        
        # Take first few sentences as summary
        summary_sentences = []
        current_length = 0
        
        for sentence in sentences[:5]:  # Max 5 sentences
            if current_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence)
            else:
                break
        
        summary = '. '.join(summary_sentences)
        return summary + "..." if len(summary) < len(content) else summary
    
    def _detect_language(self, content: str) -> str:
        """Detect the primary language of the content"""
        # Simple language detection based on common words
        english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        portuguese_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'nas', 'nos'}
        
        content_lower = content.lower()
        words = content_lower.split()
        
        if len(words) < 10:
            return 'unknown'
        
        english_count = sum(1 for word in words if word in english_words)
        portuguese_count = sum(1 for word in words if word in portuguese_words)
        
        if english_count > portuguese_count:
            return 'english'
        elif portuguese_count > english_count:
            return 'portuguese'
        else:
            return 'mixed'
    
    def _classify_content_type(self, content: str, file_path: Path) -> str:
        """Classify the type of content"""
        file_ext = file_path.suffix.lower()
        content_lower = content.lower()
        
        # File extension based classification
        if file_ext in ['.md', '.txt']:
            if any(word in content_lower for word in ['#', '##', '###', 'markdown']):
                return 'markdown'
            else:
                return 'text'
        elif file_ext in ['.py']:
            return 'python_code'
        elif file_ext in ['.js', '.ts']:
            return 'javascript_code'
        elif file_ext in ['.html', '.htm']:
            return 'html'
        elif file_ext in ['.css']:
            return 'css'
        elif file_ext in ['.json']:
            return 'json'
        elif file_ext in ['.xml']:
            return 'xml'
        elif file_ext in ['.yaml', '.yml']:
            return 'yaml'
        else:
            return 'unknown'
    
    def _calculate_complexity(self, content: str) -> Dict[str, float]:
        """Calculate content complexity metrics"""
        if not content:
            return {'score': 0.0, 'level': 'simple'}
        
        words = content.split()
        sentences = [s for s in content.split('.') if s.strip()]
        
        if not words or not sentences:
            return {'score': 0.0, 'level': 'simple'}
        
        # Basic complexity metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Calculate complexity score (0-1)
        complexity_score = min(1.0, (avg_sentence_length / 20) + (avg_word_length / 10))
        
        # Determine complexity level
        if complexity_score < 0.3:
            level = 'simple'
        elif complexity_score < 0.6:
            level = 'medium'
        else:
            level = 'complex'
        
        return {
            'score': complexity_score,
            'level': level,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length
        }

# Test the topic extractor
if __name__ == "__main__":
    extractor = TopicExtractor()
    
    # Test content
    test_content = """
    Machine learning algorithms are computational methods that enable computers to learn patterns from data without being explicitly programmed. 
    They include supervised learning, unsupervised learning, and reinforcement learning approaches. 
    Neural networks are a subset of machine learning algorithms inspired by biological neural networks. 
    Deep learning uses multiple layers of neural networks to solve complex problems in computer vision, natural language processing, and speech recognition.
    """
    
    print("🧪 Topic Extractor Test")
    print("=" * 50)
    
    # Extract topics
    topics = extractor.extract_topics(test_content)
    print(f"Extracted Topics: {topics}")
    
    # Extract metadata
    from pathlib import Path
    import os
    
    test_file = Path("test_content.txt")
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    stat = os.stat(test_file)
    metadata = extractor.extract_metadata(test_content, test_file, stat)
    
    print(f"\nExtracted Metadata:")
    for key, value in metadata.items():
        if key not in ['file_path']:  # Skip file path for cleaner output
            print(f"  {key}: {value}")
    
    # Clean up
    test_file.unlink()
