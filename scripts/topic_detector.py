#!/usr/bin/env python3
"""
Topic Detection Service for Enhanced RAG System
"""

from typing import List, Dict, Optional
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class TopicDetector:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.topic_examples = {
            "philosophy": [
                "philosophical logic", "mathematical logic", "formal logic",
                "propositional logic", "predicate logic", "modal logic",
                "mathematical foundations", "set theory", "proof theory",
                "logical reasoning", "deductive reasoning", "inductive reasoning",
                "philosophy of mathematics", "mathematical philosophy",
                "epistemology", "metaphysics", "ethics", "aesthetics"
            ],
            "technology": [
                "machine learning", "neural networks", "deep learning",
                "artificial intelligence", "data science", "algorithms",
                "programming", "software development", "web development",
                "database", "cloud computing", "cybersecurity"
            ],
            "performance": [
                "performance optimization", "speed", "efficiency",
                "productivity", "optimization", "scalability",
                "system performance", "response time", "throughput",
                "memory optimization", "cpu optimization", "gpu optimization"
            ],
            "business": [
                "business strategy", "management", "planning",
                "marketing", "sales", "finance", "economics",
                "entrepreneurship", "leadership", "team management"
            ],
            "science": [
                "scientific method", "research", "experimentation",
                "hypothesis", "theory", "observation", "analysis",
                "physics", "chemistry", "biology", "mathematics"
            ]
        }
        
        # Pre-compute topic embeddings
        self.topic_embeddings = self._compute_topic_embeddings()
    
    def _compute_topic_embeddings(self) -> Dict[str, np.ndarray]:
        """Pre-compute embeddings for topic examples"""
        topic_embeddings = {}
        for topic, examples in self.topic_examples.items():
            # Combine all examples for this topic
            combined_text = " ".join(examples)
            topic_embeddings[topic] = self.model.encode(combined_text)
        return topic_embeddings
    
    def detect_topic(self, query: str) -> str:
        """Detect the most relevant topic for a query"""
        # Generate embedding for the query
        query_embedding = self.model.encode(query)
        
        # Calculate similarity with each topic
        similarities = {}
        for topic, topic_embedding in self.topic_embeddings.items():
            similarity = cosine_similarity([query_embedding], [topic_embedding])[0][0]
            similarities[topic] = similarity
        
        # Return the topic with highest similarity
        best_topic = max(similarities, key=similarities.get)
        
        # Only return topic if similarity is above threshold
        if similarities[best_topic] > 0.3:
            return best_topic
        else:
            return "general"
    
    def detect_multiple_topics(self, query: str, threshold: float = 0.2) -> List[str]:
        """Detect multiple relevant topics for a query"""
        query_embedding = self.model.encode(query)
        
        relevant_topics = []
        for topic, topic_embedding in self.topic_embeddings.items():
            similarity = cosine_similarity([query_embedding], [topic_embedding])[0][0]
            if similarity > threshold:
                relevant_topics.append((topic, similarity))
        
        # Sort by similarity and return topic names
        relevant_topics.sort(key=lambda x: x[1], reverse=True)
        return [topic for topic, _ in relevant_topics]
    
    def get_topic_keywords(self, topic: str) -> List[str]:
        """Get keywords associated with a topic"""
        return self.topic_examples.get(topic, [])
    
    def get_topic_similarity_scores(self, query: str) -> Dict[str, float]:
        """Get similarity scores for all topics"""
        query_embedding = self.model.encode(query)
        similarities = {}
        
        for topic, topic_embedding in self.topic_embeddings.items():
            similarity = cosine_similarity([query_embedding], [topic_embedding])[0][0]
            similarities[topic] = float(similarity)
        
        return similarities

# Test the topic detector
if __name__ == "__main__":
    detector = TopicDetector()
    
    test_queries = [
        "philosophical currents of logic and mathematics",
        "machine learning algorithms and neural networks",
        "performance optimization techniques",
        "business strategy and management",
        "scientific research methods"
    ]
    
    print("🧠 Topic Detection Test")
    print("=" * 50)
    
    for query in test_queries:
        primary_topic = detector.detect_topic(query)
        all_topics = detector.detect_multiple_topics(query)
        scores = detector.get_topic_similarity_scores(query)
        
        print(f"\nQuery: '{query}'")
        print(f"Primary Topic: {primary_topic}")
        print(f"All Topics: {all_topics}")
        print(f"Top 3 Scores: {dict(sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3])}")
