#!/usr/bin/env python3
"""
Smart Document Filter for Enhanced RAG System
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from datetime import datetime, timedelta

class SmartDocumentFilter:
    def __init__(self, topic_detector):
        self.topic_detector = topic_detector
    
    def filter_by_topic(self, documents: List[Dict], topic: str) -> List[Dict]:
        """Filter documents by topic with intelligent matching"""
        if topic == "general":
            return documents
        
        topic_keywords = self.topic_detector.get_topic_keywords(topic)
        filtered_docs = []
        
        for doc in documents:
            content_lower = doc['content'].lower()
            metadata = doc.get('metadata', {})
            
            # Check content for topic keywords
            keyword_matches = sum(1 for keyword in topic_keywords 
                                if keyword.lower() in content_lower)
            
            # Check metadata for topic classification
            doc_topic = metadata.get('topic', '')
            topic_match = topic.lower() in doc_topic.lower()
            
            # Check tags for topic relevance
            tags = metadata.get('tags', [])
            tag_match = any(topic.lower() in tag.lower() for tag in tags)
            
            # Score the document's relevance to the topic
            relevance_score = 0
            if keyword_matches > 0:
                relevance_score += min(keyword_matches * 0.1, 0.5)
            if topic_match:
                relevance_score += 0.3
            if tag_match:
                relevance_score += 0.2
            
            # Include document if it has some relevance to the topic
            if relevance_score > 0.1:
                doc['topic_relevance'] = relevance_score
                filtered_docs.append(doc)
        
        # Sort by topic relevance
        filtered_docs.sort(key=lambda x: x.get('topic_relevance', 0), reverse=True)
        return filtered_docs
    
    def filter_by_date_range(self, documents: List[Dict], 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[Dict]:
        """Filter documents by date range"""
        if not start_date and not end_date:
            return documents
        
        filtered_docs = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            doc_date = metadata.get('created_date')
            
            if not doc_date:
                continue
            
            try:
                if isinstance(doc_date, str):
                    doc_date = datetime.fromisoformat(doc_date.replace('Z', '+00:00'))
                
                if start_date and doc_date < start_date:
                    continue
                if end_date and doc_date > end_date:
                    continue
                
                filtered_docs.append(doc)
            except (ValueError, TypeError):
                continue
        
        return filtered_docs
    
    def filter_by_file_type(self, documents: List[Dict], file_types: List[str]) -> List[Dict]:
        """Filter documents by file type"""
        if not file_types:
            return documents
        
        filtered_docs = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            doc_file_type = metadata.get('file_type', 'general')
            
            if doc_file_type in file_types:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def filter_by_word_count(self, documents: List[Dict], 
                           min_words: Optional[int] = None,
                           max_words: Optional[int] = None) -> List[Dict]:
        """Filter documents by word count"""
        if not min_words and not max_words:
            return documents
        
        filtered_docs = []
        for doc in documents:
            word_count = doc.get('word_count', 0)
            
            if min_words and word_count < min_words:
                continue
            if max_words and word_count > max_words:
                continue
            
            filtered_docs.append(doc)
        
        return filtered_docs
    
    def filter_by_heading(self, documents: List[Dict], heading_keywords: List[str]) -> List[Dict]:
        """Filter documents by heading keywords"""
        if not heading_keywords:
            return documents
        
        filtered_docs = []
        for doc in documents:
            heading = doc.get('heading', '').lower()
            
            if any(keyword.lower() in heading for keyword in heading_keywords):
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def filter_by_content_quality(self, documents: List[Dict], 
                                 min_quality_score: float = 0.3) -> List[Dict]:
        """Filter documents by content quality"""
        filtered_docs = []
        for doc in documents:
            # Calculate basic quality metrics
            word_count = doc.get('word_count', 0)
            content = doc.get('content', '')
            
            # Quality factors
            has_heading = bool(doc.get('heading', '').strip())
            has_paragraphs = len(content.split('\n\n')) > 1
            reasonable_length = 50 <= word_count <= 2000
            
            # Calculate quality score
            quality_score = 0
            if has_heading:
                quality_score += 0.3
            if has_paragraphs:
                quality_score += 0.3
            if reasonable_length:
                quality_score += 0.4
            
            if quality_score >= min_quality_score:
                doc['content_quality_score'] = quality_score
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def smart_filter(self, documents: List[Dict], query: str, 
                    filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Apply intelligent filtering based on query and filters"""
        if not filters:
            filters = {}
        
        # Start with all documents
        filtered_docs = documents
        
        # Detect topic from query
        topic = self.topic_detector.detect_topic(query)
        if topic != "general":
            filtered_docs = self.filter_by_topic(filtered_docs, topic)
        
        # Apply additional filters
        if 'file_types' in filters:
            filtered_docs = self.filter_by_file_type(filtered_docs, filters['file_types'])
        
        if 'date_range' in filters:
            date_range = filters['date_range']
            filtered_docs = self.filter_by_date_range(
                filtered_docs, 
                date_range.get('start_date'),
                date_range.get('end_date')
            )
        
        if 'word_count' in filters:
            word_count = filters['word_count']
            filtered_docs = self.filter_by_word_count(
                filtered_docs,
                word_count.get('min_words'),
                word_count.get('max_words')
            )
        
        if 'heading_keywords' in filters:
            filtered_docs = self.filter_by_heading(filtered_docs, filters['heading_keywords'])
        
        if 'min_quality_score' in filters:
            filtered_docs = self.filter_by_content_quality(
                filtered_docs, 
                filters['min_quality_score']
            )
        
        return filtered_docs
    
    def get_filter_stats(self, original_count: int, filtered_count: int) -> Dict[str, Any]:
        """Get statistics about filtering results"""
        return {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "reduction_percentage": ((original_count - filtered_count) / original_count * 100) if original_count > 0 else 0,
            "filter_efficiency": filtered_count / original_count if original_count > 0 else 0
        }

# Test the smart document filter
if __name__ == "__main__":
    from topic_detector import TopicDetector
    
    # Initialize topic detector
    topic_detector = TopicDetector()
    filter_system = SmartDocumentFilter(topic_detector)
    
    # Sample documents for testing
    sample_docs = [
        {
            "content": "Machine learning algorithms are transforming how we approach data analysis and pattern recognition.",
            "heading": "Introduction to ML",
            "word_count": 15,
            "metadata": {
                "topic": "technology",
                "tags": ["ai", "ml"],
                "file_type": "tutorial"
            }
        },
        {
            "content": "Philosophical logic deals with the nature of reasoning and argumentation in philosophical contexts.",
            "heading": "Philosophical Logic",
            "word_count": 12,
            "metadata": {
                "topic": "philosophy",
                "tags": ["logic", "philosophy"],
                "file_type": "academic"
            }
        },
        {
            "content": "Performance optimization techniques can significantly improve system efficiency and response times.",
            "heading": "Performance Tips",
            "word_count": 11,
            "metadata": {
                "topic": "performance",
                "tags": ["optimization", "performance"],
                "file_type": "guide"
            }
        }
    ]
    
    print("🔍 Smart Document Filter Test")
    print("=" * 50)
    
    # Test topic filtering
    tech_docs = filter_system.filter_by_topic(sample_docs, "technology")
    print(f"Technology documents: {len(tech_docs)}")
    
    # Test smart filtering
    filters = {
        "file_types": ["tutorial", "guide"],
        "min_quality_score": 0.5
    }
    
    filtered_docs = filter_system.smart_filter(sample_docs, "machine learning algorithms", filters)
    print(f"Smart filtered documents: {len(filtered_docs)}")
    
    # Show filter stats
    stats = filter_system.get_filter_stats(len(sample_docs), len(filtered_docs))
    print(f"Filter stats: {stats}")
