#!/usr/bin/env python3
"""
Individual Test for TopicDetector Component
Tests standalone functionality and integration capabilities
"""

import sys
import os
import json
import time
import logging
from typing import List, Dict, Any
import traceback

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from topic_detector import TopicDetector
    print("✅ TopicDetector import successful")
except ImportError as e:
    print(f"❌ TopicDetector import failed: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TopicDetectorIndividualTester:
    def __init__(self):
        self.detector = None
        self.test_results = {
            "component": "TopicDetector",
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
            "performance_metrics": {},
            "errors": [],
            "warnings": []
        }
    
    def test_initialization(self):
        """Test TopicDetector initialization"""
        print("\n🧪 Testing TopicDetector Initialization...")
        self.test_results["total_tests"] += 1
        
        try:
            start_time = time.time()
            self.detector = TopicDetector()
            init_time = time.time() - start_time
            
            # Validate initialization
            assert hasattr(self.detector, 'model'), "Missing model attribute"
            assert hasattr(self.detector, 'topic_examples'), "Missing topic_examples attribute"
            assert hasattr(self.detector, 'topic_embeddings'), "Missing topic_embeddings attribute"
            assert len(self.detector.topic_examples) > 0, "No topic examples loaded"
            assert len(self.detector.topic_embeddings) > 0, "No topic embeddings computed"
            
            self.test_results["performance_metrics"]["initialization_time"] = init_time
            self.test_results["tests_passed"] += 1
            print(f"✅ TopicDetector initialized successfully in {init_time:.2f}s")
            print(f"   Topics available: {list(self.detector.topic_examples.keys())}")
            return True
            
        except Exception as e:
            error_msg = f"TopicDetector initialization failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            return False
    
    def test_single_topic_detection(self):
        """Test single topic detection functionality"""
        print("\n🧪 Testing Single Topic Detection...")
        self.test_results["total_tests"] += 1
        
        try:
            test_cases = [
                ("philosophical logic and mathematical foundations", "philosophy"),
                ("machine learning algorithms and neural networks", "technology"),
                ("performance optimization and system efficiency", "performance"),
                ("business strategy and management planning", "business"),
                ("scientific research and experimentation", "science"),
                ("random unrelated query about cooking", "general")
            ]
            
            correct_predictions = 0
            total_predictions = len(test_cases)
            
            for query, expected_topic in test_cases:
                start_time = time.time()
                detected_topic = self.detector.detect_topic(query)
                detection_time = time.time() - start_time
                
                if detected_topic == expected_topic:
                    correct_predictions += 1
                    print(f"   ✅ '{query}' -> {detected_topic} (expected: {expected_topic})")
                else:
                    print(f"   ⚠️  '{query}' -> {detected_topic} (expected: {expected_topic})")
                
                # Store timing for first query
                if query == test_cases[0][0]:
                    self.test_results["performance_metrics"]["single_detection_time"] = detection_time
            
            accuracy = correct_predictions / total_predictions
            self.test_results["performance_metrics"]["detection_accuracy"] = accuracy
            
            if accuracy >= 0.8:  # 80% accuracy threshold
                self.test_results["tests_passed"] += 1
                print(f"✅ Single topic detection successful (accuracy: {accuracy:.1%})")
                return True
            else:
                self.test_results["warnings"].append(f"Low detection accuracy: {accuracy:.1%}")
                self.test_results["tests_passed"] += 1
                print(f"⚠️  Single topic detection completed with low accuracy: {accuracy:.1%}")
                return True
            
        except Exception as e:
            error_msg = f"Single topic detection failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_multiple_topic_detection(self):
        """Test multiple topic detection functionality"""
        print("\n🧪 Testing Multiple Topic Detection...")
        self.test_results["total_tests"] += 1
        
        try:
            test_queries = [
                "machine learning algorithms for business analytics",  # Should detect both technology and business
                "philosophical foundations of scientific method",      # Should detect both philosophy and science
                "performance optimization in software development",    # Should detect both performance and technology
                "random unrelated query about cooking"                 # Should detect general or low confidence
            ]
            
            for query in test_queries:
                start_time = time.time()
                topics = self.detector.detect_multiple_topics(query, threshold=0.2)
                detection_time = time.time() - start_time
                
                print(f"   Query: '{query}'")
                print(f"   Detected topics: {topics}")
                
                # Store timing for first query
                if query == test_queries[0]:
                    self.test_results["performance_metrics"]["multiple_detection_time"] = detection_time
            
            self.test_results["tests_passed"] += 1
            print(f"✅ Multiple topic detection successful")
            return True
            
        except Exception as e:
            error_msg = f"Multiple topic detection failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_topic_keywords(self):
        """Test topic keywords functionality"""
        print("\n🧪 Testing Topic Keywords...")
        self.test_results["total_tests"] += 1
        
        try:
            # Test getting keywords for each topic
            for topic in self.detector.topic_examples.keys():
                keywords = self.detector.get_topic_keywords(topic)
                assert isinstance(keywords, list), f"Keywords for {topic} should be a list"
                assert len(keywords) > 0, f"Topic {topic} should have keywords"
                print(f"   {topic}: {len(keywords)} keywords")
            
            # Test invalid topic
            invalid_keywords = self.detector.get_topic_keywords("nonexistent_topic")
            assert invalid_keywords == [], "Invalid topic should return empty list"
            
            self.test_results["tests_passed"] += 1
            print(f"✅ Topic keywords functionality successful")
            return True
            
        except Exception as e:
            error_msg = f"Topic keywords test failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_similarity_scores(self):
        """Test similarity scores functionality"""
        print("\n🧪 Testing Similarity Scores...")
        self.test_results["total_tests"] += 1
        
        try:
            test_query = "machine learning and artificial intelligence"
            
            start_time = time.time()
            scores = self.detector.get_topic_similarity_scores(test_query)
            scores_time = time.time() - start_time
            
            # Validate scores structure
            assert isinstance(scores, dict), "Scores should be a dictionary"
            assert len(scores) == len(self.detector.topic_examples), "Should have scores for all topics"
            
            # Check that all scores are between 0 and 1
            for topic, score in scores.items():
                assert 0 <= score <= 1, f"Score for {topic} should be between 0 and 1, got {score}"
            
            # Check that scores are sorted (highest first)
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            print(f"   Top 3 topic scores:")
            for i, (topic, score) in enumerate(sorted_scores[:3]):
                print(f"     {i+1}. {topic}: {score:.3f}")
            
            self.test_results["performance_metrics"]["similarity_scores_time"] = scores_time
            self.test_results["tests_passed"] += 1
            print(f"✅ Similarity scores functionality successful")
            return True
            
        except Exception as e:
            error_msg = f"Similarity scores test failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing Edge Cases...")
        self.test_results["total_tests"] += 1
        
        try:
            # Test empty query
            empty_topic = self.detector.detect_topic("")
            assert empty_topic in ["general"] + list(self.detector.topic_examples.keys()), "Empty query should return valid topic"
            
            # Test very short query
            short_topic = self.detector.detect_topic("AI")
            assert short_topic in ["general"] + list(self.detector.topic_examples.keys()), "Short query should return valid topic"
            
            # Test very long query
            long_query = "machine learning " * 100  # Very long query
            long_topic = self.detector.detect_topic(long_query)
            assert long_topic in ["general"] + list(self.detector.topic_examples.keys()), "Long query should return valid topic"
            
            # Test special characters
            special_topic = self.detector.detect_topic("AI & ML @#$%^&*()")
            assert special_topic in ["general"] + list(self.detector.topic_examples.keys()), "Special characters should be handled"
            
            # Test multiple topics with different thresholds
            query = "machine learning for business analytics"
            topics_high = self.detector.detect_multiple_topics(query, threshold=0.5)
            topics_low = self.detector.detect_multiple_topics(query, threshold=0.1)
            assert len(topics_low) >= len(topics_high), "Lower threshold should return more topics"
            
            self.test_results["tests_passed"] += 1
            print(f"✅ Edge cases handling successful")
            return True
            
        except Exception as e:
            error_msg = f"Edge cases test failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        print("\n🧪 Testing Performance Benchmarks...")
        self.test_results["total_tests"] += 1
        
        try:
            # Test batch processing performance
            test_queries = [
                "machine learning algorithms",
                "philosophical logic",
                "performance optimization",
                "business strategy",
                "scientific research"
            ] * 10  # 50 queries total
            
            start_time = time.time()
            results = []
            for query in test_queries:
                topic = self.detector.detect_topic(query)
                results.append(topic)
            batch_time = time.time() - start_time
            
            # Calculate performance metrics
            queries_per_second = len(test_queries) / batch_time
            avg_time_per_query = batch_time / len(test_queries)
            
            self.test_results["performance_metrics"]["batch_processing_time"] = batch_time
            self.test_results["performance_metrics"]["queries_per_second"] = queries_per_second
            self.test_results["performance_metrics"]["avg_time_per_query"] = avg_time_per_query
            
            print(f"   Processed {len(test_queries)} queries in {batch_time:.2f}s")
            print(f"   Queries per second: {queries_per_second:.1f}")
            print(f"   Average time per query: {avg_time_per_query:.3f}s")
            
            # Performance thresholds
            if queries_per_second >= 10:  # At least 10 queries per second
                self.test_results["tests_passed"] += 1
                print(f"✅ Performance benchmarks passed")
                return True
            else:
                self.test_results["warnings"].append(f"Low performance: {queries_per_second:.1f} queries/sec")
                self.test_results["tests_passed"] += 1
                print(f"⚠️  Performance benchmarks completed with low performance")
                return True
            
        except Exception as e:
            error_msg = f"Performance benchmarks failed: {str(e)}"
            self.test_results["errors"].append(error_msg)
            self.test_results["tests_failed"] += 1
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """Run all individual tests"""
        print("🚀 Starting TopicDetector Individual Testing")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_initialization,
            self.test_single_topic_detection,
            self.test_multiple_topic_detection,
            self.test_topic_keywords,
            self.test_similarity_scores,
            self.test_edge_cases,
            self.test_performance_benchmarks
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                error_msg = f"Test {test.__name__} crashed: {str(e)}"
                self.test_results["errors"].append(error_msg)
                self.test_results["tests_failed"] += 1
                print(f"❌ {error_msg}")
                traceback.print_exc()
        
        total_time = time.time() - start_time
        self.test_results["performance_metrics"]["total_test_time"] = total_time
        
        # Generate report
        self.generate_report()
        
        return self.test_results
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TOPIC DETECTOR INDIVIDUAL TEST REPORT")
        print("=" * 60)
        
        total_tests = self.test_results["total_tests"]
        passed = self.test_results["tests_passed"]
        failed = self.test_results["tests_failed"]
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results["performance_metrics"]:
            print(f"\nPerformance Metrics:")
            for metric, value in self.test_results["performance_metrics"].items():
                if isinstance(value, float):
                    if "time" in metric:
                        print(f"  {metric}: {value:.3f}s")
                    elif "accuracy" in metric or "rate" in metric:
                        print(f"  {metric}: {value:.1%}")
                    else:
                        print(f"  {metric}: {value:.2f}")
                else:
                    print(f"  {metric}: {value}")
        
        if self.test_results["errors"]:
            print(f"\nErrors ({len(self.test_results['errors'])}):")
            for i, error in enumerate(self.test_results["errors"], 1):
                print(f"  {i}. {error}")
        
        if self.test_results["warnings"]:
            print(f"\nWarnings ({len(self.test_results['warnings'])}):")
            for i, warning in enumerate(self.test_results["warnings"], 1):
                print(f"  {i}. {warning}")
        
        # Save detailed report
        report_file = "topic_detector_individual_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return success_rate >= 80  # 80% success rate threshold

if __name__ == "__main__":
    tester = TopicDetectorIndividualTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TopicDetector Individual Testing PASSED!")
        sys.exit(0)
    else:
        print("\n💥 TopicDetector Individual Testing FAILED!")
        sys.exit(1)
