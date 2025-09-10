#!/usr/bin/env python3
"""
Enhanced Embedding Service
Optimized embedding generation with intelligent batching and caching
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import hashlib
import logging
import re
import time

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Enhanced embedding service with batching and caching"""
    
    def __init__(self, model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', max_batch_tokens: int = 4096):
        """
        Initialize the embedding service.
        Args:
            model_name (str): The name of the embedding model. Default is multilingual model supporting 50+ languages.
            max_batch_tokens (int): Maximum tokens per batch for efficient processing.
        """
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.max_batch_tokens = max_batch_tokens
        self.cache = {}
        self.is_multilingual = 'multilingual' in model_name.lower()
        logger.info(f"Initialized EmbeddingService with model: {model_name} (Multilingual: {self.is_multilingual})")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text with caching."""
        start_time = time.time()
        status = "success"
        
        try:
            cache_key = hashlib.md5(text.encode()).hexdigest()
            if cache_key in self.cache:
                logger.debug(f"Cache hit for text: {text[:50]}...")
                try:
                    from ..monitoring.metrics import get_metrics
                    metrics = get_metrics()
                    metrics.record_embedding_cache_hit(self.model_name)
                except Exception as e:
                    logger.warning(f"Failed to record cache hit metrics: {e}")
                return self.cache[cache_key]

            embedding = self.model.encode(text, convert_to_tensor=False).tolist()
            self.cache[cache_key] = embedding
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            
            # Record cache miss
            try:
                from ..monitoring.metrics import get_metrics
                metrics = get_metrics()
                metrics.record_embedding_cache_miss(self.model_name)
            except Exception as e:
                logger.warning(f"Failed to record cache miss metrics: {e}")
                
            return embedding
        except Exception as e:
            status = "error"
            logger.error(f"Failed to generate embedding: {e}")
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            try:
                from ..monitoring.metrics import get_metrics
                metrics = get_metrics()
                metrics.record_embedding_request(self.model_name, duration, status)
            except Exception as e:
                logger.warning(f"Failed to record embedding metrics: {e}")

    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings in batches based on total token count."""
        start_time = time.time()
        status = "success"
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts in batches")
            
            # Record batch size metric
            try:
                from ..monitoring.metrics import get_metrics
                metrics = get_metrics()
                metrics.record_embedding_batch(self.model_name, len(texts))
            except Exception as e:
                logger.warning(f"Failed to record batch size metrics: {e}")
            
            # Get tokenizer from the model for accurate batching
            tokenizer = self.model.tokenizer

            all_embeddings = []
            current_batch = []
            current_batch_tokens = 0
            batch_count = 0

            for i, text in enumerate(texts):
                # Check cache first
                cache_key = hashlib.md5(text.encode()).hexdigest()
                if cache_key in self.cache:
                    all_embeddings.append(self.cache[cache_key])
                    continue

                # Estimate token count (this is faster than encoding for batching purposes)
                token_count = len(tokenizer.encode(text, truncation=False))

                if current_batch and (current_batch_tokens + token_count > self.max_batch_tokens):
                    # Process current batch
                    batch_count += 1
                    logger.debug(f"Processing batch {batch_count} with {len(current_batch)} texts")
                    
                    embeddings = self.model.encode(current_batch, convert_to_tensor=False)
                    for j, emb in enumerate(embeddings):
                        # Cache the embeddings
                        cache_key = hashlib.md5(current_batch[j].encode()).hexdigest()
                        self.cache[cache_key] = emb.tolist()
                        all_embeddings.append(emb.tolist())
                    
                    current_batch = []
                    current_batch_tokens = 0

                current_batch.append(text)
                current_batch_tokens += token_count

            # Process final batch
            if current_batch:
                batch_count += 1
                logger.debug(f"Processing final batch {batch_count} with {len(current_batch)} texts")
                
                embeddings = self.model.encode(current_batch, convert_to_tensor=False)
                for j, emb in enumerate(embeddings):
                    # Cache the embeddings
                    cache_key = hashlib.md5(current_batch[j].encode()).hexdigest()
                    self.cache[cache_key] = emb.tolist()
                    all_embeddings.append(emb.tolist())

            logger.info(f"Generated {len(all_embeddings)} embeddings in {batch_count} batches")
            return all_embeddings
        except Exception as e:
            status = "error"
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            try:
                from ..monitoring.metrics import get_metrics
                metrics = get_metrics()
                metrics.record_embedding_request(self.model_name, duration, status)
            except Exception as e:
                logger.warning(f"Failed to record batch embedding metrics: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.cache),
            "model_name": self.model_name,
            "max_batch_tokens": self.max_batch_tokens
        }

    def clear_cache(self):
        """Clear the embedding cache."""
        self.cache.clear()
        logger.info("Embedding cache cleared")

    def detect_language(self, text: str) -> str:
        """
        Simple language detection for English and Portuguese.
        Returns 'en', 'pt', or 'unknown'.
        """
        # Portuguese indicators
        pt_indicators = [
            r'\b(que|para|com|uma|dos|das|não|mais|muito|sobre|entre|através|durante|após|antes|depois|quando|onde|como|porque|porquê|porquê)\b',
            r'\b(é|são|foi|foram|será|serão|tem|têm|tinha|tinham|terá|terão)\b',
            r'\b(de|da|do|em|na|no|pela|pelo|pelas|pelos)\b',
            r'ção\b', r'ões\b', r'ães\b', r'ães\b', r'ões\b'
        ]
        
        # English indicators
        en_indicators = [
            r'\b(the|and|for|are|but|not|you|all|can|had|her|was|one|our|out|day|get|has|him|his|how|its|may|new|now|old|see|two|way|who|boy|did|man|men|put|say|she|too|use)\b',
            r'\b(is|was|were|been|have|has|had|will|would|could|should|may|might|must|shall)\b',
            r'\b(ing\b|tion\b|ness\b|ment\b|able\b|ible\b)'
        ]
        
        text_lower = text.lower()
        
        pt_score = sum(len(re.findall(pattern, text_lower)) for pattern in pt_indicators)
        en_score = sum(len(re.findall(pattern, text_lower)) for pattern in en_indicators)
        
        if pt_score > en_score and pt_score > 0:
            return 'pt'
        elif en_score > pt_score and en_score > 0:
            return 'en'
        else:
            return 'unknown'

    def get_multilingual_info(self) -> Dict[str, Any]:
        """Get information about multilingual capabilities."""
        return {
            "is_multilingual": self.is_multilingual,
            "model_name": self.model_name,
            "supported_languages": ["en", "pt", "es", "fr", "de", "it", "ru", "zh", "ja", "ko"] if self.is_multilingual else ["en"],
            "cross_lingual_capable": self.is_multilingual
        }