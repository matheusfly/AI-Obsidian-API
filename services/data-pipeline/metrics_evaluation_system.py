#!/usr/bin/env python3
"""
Metrics Evaluation System
Comprehensive tracking of success, quality, and performance metrics
"""

import asyncio
import logging
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SearchMetrics:
    """Metrics for search operations"""
    query: str
    search_time_ms: float
    top_similarity: float
    avg_similarity: float
    results_count: int
    files_retrieved: List[str]
    timestamp: str

@dataclass
class PipelineMetrics:
    """Metrics for pipeline operations"""
    operation: str
    duration_ms: float
    success: bool
    error_message: Optional[str]
    files_processed: int
    chunks_generated: int
    embeddings_created: int
    timestamp: str

@dataclass
class QualityMetrics:
    """Metrics for quality assessment"""
    test_name: str
    relevance_score: float
    completeness_score: float
    accuracy_score: float
    performance_score: float
    overall_score: float
    timestamp: str

@dataclass
class SystemMetrics:
    """System-level metrics"""
    total_files: int
    total_chunks: int
    total_embeddings: int
    collection_size_mb: float
    memory_usage_mb: float
    disk_usage_mb: float
    timestamp: str

class MetricsEvaluator:
    """Comprehensive metrics evaluation system"""
    
    def __init__(self, metrics_file: str = "metrics_history.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_history = self._load_metrics_history()
        
    def _load_metrics_history(self) -> Dict[str, List[Dict]]:
        """Load existing metrics history"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load metrics history: {e}")
        
        return {
            "search_metrics": [],
            "pipeline_metrics": [],
            "quality_metrics": [],
            "system_metrics": []
        }
    
    def _save_metrics_history(self):
        """Save metrics history to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metrics history: {e}")
    
    def record_search_metrics(self, metrics: SearchMetrics):
        """Record search operation metrics"""
        self.metrics_history["search_metrics"].append(asdict(metrics))
        self._save_metrics_history()
        logger.info(f"📊 Search metrics recorded: {metrics.query} - {metrics.top_similarity:.3f}")
    
    def record_pipeline_metrics(self, metrics: PipelineMetrics):
        """Record pipeline operation metrics"""
        self.metrics_history["pipeline_metrics"].append(asdict(metrics))
        self._save_metrics_history()
        logger.info(f"🔧 Pipeline metrics recorded: {metrics.operation} - {metrics.duration_ms:.1f}ms")
    
    def record_quality_metrics(self, metrics: QualityMetrics):
        """Record quality assessment metrics"""
        self.metrics_history["quality_metrics"].append(asdict(metrics))
        self._save_metrics_history()
        logger.info(f"⭐ Quality metrics recorded: {metrics.test_name} - {metrics.overall_score:.3f}")
    
    def record_system_metrics(self, metrics: SystemMetrics):
        """Record system-level metrics"""
        self.metrics_history["system_metrics"].append(asdict(metrics))
        self._save_metrics_history()
        logger.info(f"🖥️ System metrics recorded: {metrics.total_files} files, {metrics.total_chunks} chunks")
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        cutoff_datetime = datetime.now() - timedelta(days=days)
        
        trends = {
            "search_performance": self._analyze_search_trends(cutoff_datetime),
            "pipeline_performance": self._analyze_pipeline_trends(cutoff_datetime),
            "quality_trends": self._analyze_quality_trends(cutoff_datetime),
            "system_health": self._analyze_system_health(cutoff_datetime)
        }
        
        return trends
    
    def _analyze_search_trends(self, cutoff_datetime: datetime) -> Dict[str, Any]:
        """Analyze search performance trends"""
        recent_metrics = [
            m for m in self.metrics_history["search_metrics"]
            if datetime.fromisoformat(m["timestamp"]) > cutoff_datetime
        ]
        
        if not recent_metrics:
            return {"status": "no_data", "message": "No recent search metrics"}
        
        # Calculate trends
        similarities = [m["top_similarity"] for m in recent_metrics]
        search_times = [m["search_time_ms"] for m in recent_metrics]
        
        return {
            "status": "data_available",
            "avg_similarity": sum(similarities) / len(similarities),
            "max_similarity": max(similarities),
            "min_similarity": min(similarities),
            "avg_search_time": sum(search_times) / len(search_times),
            "total_searches": len(recent_metrics),
            "trend": "improving" if similarities[-1] > similarities[0] else "declining"
        }
    
    def _analyze_pipeline_trends(self, cutoff_datetime: datetime) -> Dict[str, Any]:
        """Analyze pipeline performance trends"""
        recent_metrics = [
            m for m in self.metrics_history["pipeline_metrics"]
            if datetime.fromisoformat(m["timestamp"]) > cutoff_datetime
        ]
        
        if not recent_metrics:
            return {"status": "no_data", "message": "No recent pipeline metrics"}
        
        # Calculate trends
        durations = [m["duration_ms"] for m in recent_metrics]
        success_rate = sum(1 for m in recent_metrics if m["success"]) / len(recent_metrics)
        
        return {
            "status": "data_available",
            "avg_duration_ms": sum(durations) / len(durations),
            "success_rate": success_rate,
            "total_operations": len(recent_metrics),
            "trend": "improving" if durations[-1] < durations[0] else "declining"
        }
    
    def _analyze_quality_trends(self, cutoff_datetime: datetime) -> Dict[str, Any]:
        """Analyze quality trends"""
        recent_metrics = [
            m for m in self.metrics_history["quality_metrics"]
            if datetime.fromisoformat(m["timestamp"]) > cutoff_datetime
        ]
        
        if not recent_metrics:
            return {"status": "no_data", "message": "No recent quality metrics"}
        
        # Calculate trends
        overall_scores = [m["overall_score"] for m in recent_metrics]
        
        return {
            "status": "data_available",
            "avg_quality": sum(overall_scores) / len(overall_scores),
            "max_quality": max(overall_scores),
            "min_quality": min(overall_scores),
            "total_tests": len(recent_metrics),
            "trend": "improving" if overall_scores[-1] > overall_scores[0] else "declining"
        }
    
    def _analyze_system_health(self, cutoff_datetime: datetime) -> Dict[str, Any]:
        """Analyze system health trends"""
        recent_metrics = [
            m for m in self.metrics_history["system_metrics"]
            if datetime.fromisoformat(m["timestamp"]) > cutoff_datetime
        ]
        
        if not recent_metrics:
            return {"status": "no_data", "message": "No recent system metrics"}
        
        # Calculate trends
        latest = recent_metrics[-1]
        
        return {
            "status": "data_available",
            "total_files": latest["total_files"],
            "total_chunks": latest["total_chunks"],
            "total_embeddings": latest["total_embeddings"],
            "collection_size_mb": latest["collection_size_mb"],
            "memory_usage_mb": latest["memory_usage_mb"],
            "disk_usage_mb": latest["disk_usage_mb"]
        }
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        trends = self.get_performance_trends()
        
        report = f"""
# 📊 PERFORMANCE METRICS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔍 Search Performance Trends
"""
        
        if trends["search_performance"]["status"] == "no_data":
            report += "No recent search metrics available.\n"
        else:
            sp = trends["search_performance"]
            report += f"""
- **Average Similarity**: {sp['avg_similarity']:.3f}
- **Max Similarity**: {sp['max_similarity']:.3f}
- **Min Similarity**: {sp['min_similarity']:.3f}
- **Average Search Time**: {sp['avg_search_time']:.1f}ms
- **Total Searches**: {sp['total_searches']}
- **Trend**: {sp['trend']}
"""
        
        report += "\n## 🔧 Pipeline Performance Trends\n"
        
        if trends["pipeline_performance"]["status"] == "no_data":
            report += "No recent pipeline metrics available.\n"
        else:
            pp = trends["pipeline_performance"]
            report += f"""
- **Average Duration**: {pp['avg_duration_ms']:.1f}ms
- **Success Rate**: {pp['success_rate']:.1%}
- **Total Operations**: {pp['total_operations']}
- **Trend**: {pp['trend']}
"""
        
        report += "\n## ⭐ Quality Trends\n"
        
        if trends["quality_trends"]["status"] == "no_data":
            report += "No recent quality metrics available.\n"
        else:
            qt = trends["quality_trends"]
            report += f"""
- **Average Quality**: {qt['avg_quality']:.3f}
- **Max Quality**: {qt['max_quality']:.3f}
- **Min Quality**: {qt['min_quality']:.3f}
- **Total Tests**: {qt['total_tests']}
- **Trend**: {qt['trend']}
"""
        
        report += "\n## 🖥️ System Health\n"
        
        if trends["system_health"]["status"] == "no_data":
            report += "No recent system metrics available.\n"
        else:
            sh = trends["system_health"]
            report += f"""
- **Total Files**: {sh['total_files']}
- **Total Chunks**: {sh['total_chunks']}
- **Total Embeddings**: {sh['total_embeddings']}
- **Collection Size**: {sh['collection_size_mb']:.1f} MB
- **Memory Usage**: {sh['memory_usage_mb']:.1f} MB
- **Disk Usage**: {sh['disk_usage_mb']:.1f} MB
"""
        
        return report
    
    def benchmark_current_performance(self) -> Dict[str, Any]:
        """Run a comprehensive benchmark of current performance"""
        logger.info("🚀 Starting comprehensive performance benchmark...")
        
        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test 1: Search Performance
        logger.info("🔍 Testing search performance...")
        search_test = self._benchmark_search_performance()
        benchmark_results["tests"]["search_performance"] = search_test
        
        # Test 2: Pipeline Performance
        logger.info("🔧 Testing pipeline performance...")
        pipeline_test = self._benchmark_pipeline_performance()
        benchmark_results["tests"]["pipeline_performance"] = pipeline_test
        
        # Test 3: Quality Assessment
        logger.info("⭐ Testing quality assessment...")
        quality_test = self._benchmark_quality_assessment()
        benchmark_results["tests"]["quality_assessment"] = quality_test
        
        # Test 4: System Health
        logger.info("🖥️ Testing system health...")
        system_test = self._benchmark_system_health()
        benchmark_results["tests"]["system_health"] = system_test
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(benchmark_results)
        benchmark_results["overall_score"] = overall_score
        
        logger.info(f"✅ Benchmark completed! Overall Score: {overall_score:.3f}")
        
        return benchmark_results
    
    def _benchmark_search_performance(self) -> Dict[str, Any]:
        """Benchmark search performance"""
        # This would integrate with your actual search service
        # For now, return mock data
        return {
            "avg_search_time_ms": 15.2,
            "avg_similarity_score": 0.285,
            "success_rate": 1.0,
            "status": "excellent"
        }
    
    def _benchmark_pipeline_performance(self) -> Dict[str, Any]:
        """Benchmark pipeline performance"""
        # This would integrate with your actual pipeline
        # For now, return mock data
        return {
            "avg_processing_time_ms": 1250.0,
            "success_rate": 1.0,
            "throughput_chunks_per_second": 0.8,
            "status": "good"
        }
    
    def _benchmark_quality_assessment(self) -> Dict[str, Any]:
        """Benchmark quality assessment"""
        # This would integrate with your actual quality tests
        # For now, return mock data
        return {
            "relevance_score": 0.85,
            "completeness_score": 0.90,
            "accuracy_score": 0.88,
            "overall_quality": 0.88,
            "status": "excellent"
        }
    
    def _benchmark_system_health(self) -> Dict[str, Any]:
        """Benchmark system health"""
        # This would integrate with your actual system metrics
        # For now, return mock data
        return {
            "memory_efficiency": 0.75,
            "disk_efficiency": 0.80,
            "collection_health": 0.95,
            "overall_health": 0.83,
            "status": "good"
        }
    
    def _calculate_overall_score(self, benchmark_results: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        tests = benchmark_results["tests"]
        
        # Weighted scoring
        weights = {
            "search_performance": 0.3,
            "pipeline_performance": 0.25,
            "quality_assessment": 0.25,
            "system_health": 0.2
        }
        
        total_score = 0
        for test_name, weight in weights.items():
            if test_name in tests:
                test_score = self._extract_test_score(tests[test_name])
                total_score += test_score * weight
        
        return total_score
    
    def _extract_test_score(self, test_data: Dict[str, Any]) -> float:
        """Extract a normalized score from test data"""
        # This is a simplified scoring mechanism
        # In practice, you'd have more sophisticated scoring logic
        
        if "overall_score" in test_data:
            return test_data["overall_score"]
        elif "overall_quality" in test_data:
            return test_data["overall_quality"]
        elif "overall_health" in test_data:
            return test_data["overall_health"]
        else:
            # Default to 0.5 if no clear score
            return 0.5

async def main():
    """Main function to demonstrate the metrics system"""
    evaluator = MetricsEvaluator()
    
    # Record some sample metrics
    search_metrics = SearchMetrics(
        query="performance optimization",
        search_time_ms=16.5,
        top_similarity=0.369,
        avg_similarity=0.285,
        results_count=5,
        files_retrieved=["Flask/Dash optimization", "Performance strategies"],
        timestamp=datetime.now().isoformat()
    )
    
    evaluator.record_search_metrics(search_metrics)
    
    # Generate performance report
    report = evaluator.generate_performance_report()
    print(report)
    
    # Run benchmark
    benchmark_results = evaluator.benchmark_current_performance()
    print(f"\n🎯 Overall Benchmark Score: {benchmark_results['overall_score']:.3f}")

if __name__ == "__main__":
    asyncio.run(main())
