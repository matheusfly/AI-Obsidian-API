"""
Ultra Performance Optimizer for Enhanced Observability
Advanced performance optimization with real-time monitoring and intelligent scaling
"""

import asyncio
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import aiohttp
import asyncpg
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizationLevel(Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ULTRA = "ultra"

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    response_time: float
    throughput: float
    error_rate: float
    queue_depth: int
    cache_hit_ratio: float
    db_connection_pool: int
    active_connections: int

@dataclass
class OptimizationRecommendation:
    category: str
    priority: int  # 1-5, 5 being highest
    title: str
    description: str
    impact_score: float  # 0-1
    implementation_effort: str  # low, medium, high
    estimated_improvement: str
    code_example: Optional[str] = None

class UltraPerformanceOptimizer:
    """Ultra Performance Optimizer with ML-based anomaly detection"""
    
    def __init__(self, 
                 optimization_level: OptimizationLevel = OptimizationLevel.BALANCED,
                 prometheus_port: int = 8002,
                 database_url: Optional[str] = None):
        
        self.optimization_level = optimization_level
        self.prometheus_port = prometheus_port
        self.database_url = database_url
        
        # Performance tracking
        self.metrics_history: List[PerformanceMetrics] = []
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Optimization thresholds based on level
        self.thresholds = self._get_thresholds()
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # Performance optimization rules
        self.optimization_rules = self._initialize_optimization_rules()
        
        logger.info(f"Ultra Performance Optimizer initialized with {optimization_level.value} level")
    
    def _get_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get performance thresholds based on optimization level"""
        
        base_thresholds = {
            "cpu": {"warning": 70, "critical": 90},
            "memory": {"warning": 80, "critical": 95},
            "response_time": {"warning": 1000, "critical": 5000},
            "error_rate": {"warning": 1, "critical": 5},
            "throughput": {"warning": 100, "critical": 50},
            "cache_hit_ratio": {"warning": 80, "critical": 60}
        }
        
        if self.optimization_level == OptimizationLevel.CONSERVATIVE:
            return {k: {kk: vv * 0.8 for kk, vv in v.items()} for k, v in base_thresholds.items()}
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            return {k: {kk: vv * 1.2 for kk, vv in v.items()} for k, v in base_thresholds.items()}
        elif self.optimization_level == OptimizationLevel.ULTRA:
            return {k: {kk: vv * 1.5 for kk, vv in v.items()} for k, v in base_thresholds.items()}
        else:
            return base_thresholds
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for performance monitoring"""
        
        # System performance metrics
        self.cpu_usage_gauge = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage_gauge = Gauge(
            'system_memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        
        self.response_time_histogram = Histogram(
            'system_response_time_seconds',
            'Response time in seconds',
            ['service', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
            registry=self.registry
        )
        
        self.throughput_counter = Counter(
            'system_throughput_total',
            'Total throughput',
            ['service'],
            registry=self.registry
        )
        
        self.error_rate_gauge = Gauge(
            'system_error_rate_percent',
            'Error rate percentage',
            ['service'],
            registry=self.registry
        )
        
        # Optimization metrics
        self.optimization_score_gauge = Gauge(
            'optimization_score',
            'Current optimization score (0-100)',
            registry=self.registry
        )
        
        self.anomaly_score_gauge = Gauge(
            'anomaly_score',
            'Anomaly detection score',
            registry=self.registry
        )
        
        # Performance improvements
        self.performance_improvement_counter = Counter(
            'performance_improvements_total',
            'Total performance improvements applied',
            ['category', 'type'],
            registry=self.registry
        )
    
    def _initialize_optimization_rules(self) -> List[Dict[str, Any]]:
        """Initialize optimization rules based on best practices"""
        
        return [
            {
                "name": "database_connection_pooling",
                "category": "database",
                "priority": 5,
                "condition": lambda m: m.db_connection_pool < 10,
                "action": "increase_connection_pool",
                "description": "Increase database connection pool size"
            },
            {
                "name": "cache_optimization",
                "category": "caching",
                "priority": 4,
                "condition": lambda m: m.cache_hit_ratio < 80,
                "action": "optimize_cache_strategy",
                "description": "Optimize cache hit ratio"
            },
            {
                "name": "memory_optimization",
                "category": "memory",
                "priority": 5,
                "condition": lambda m: m.memory_usage > 85,
                "action": "optimize_memory_usage",
                "description": "Optimize memory usage patterns"
            },
            {
                "name": "cpu_optimization",
                "category": "cpu",
                "priority": 4,
                "condition": lambda m: m.cpu_usage > 80,
                "action": "optimize_cpu_usage",
                "description": "Optimize CPU-intensive operations"
            },
            {
                "name": "response_time_optimization",
                "category": "performance",
                "priority": 5,
                "condition": lambda m: m.response_time > 2000,
                "action": "optimize_response_time",
                "description": "Optimize response time"
            },
            {
                "name": "throughput_optimization",
                "category": "performance",
                "priority": 4,
                "condition": lambda m: m.throughput < 100,
                "action": "optimize_throughput",
                "description": "Optimize system throughput"
            }
        ]
    
    async def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive performance metrics"""
        
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_io_counters()
            network = psutil.net_io_counters()
            
            # Process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            process_cpu = process.cpu_percent()
            
            # Calculate derived metrics
            memory_usage = memory.percent
            disk_io = (disk.read_bytes + disk.write_bytes) / 1024 / 1024  # MB
            network_io = (network.bytes_sent + network.bytes_recv) / 1024 / 1024  # MB
            
            # Simulate other metrics (in real implementation, these would come from actual services)
            response_time = await self._measure_response_time()
            throughput = await self._measure_throughput()
            error_rate = await self._measure_error_rate()
            queue_depth = await self._measure_queue_depth()
            cache_hit_ratio = await self._measure_cache_hit_ratio()
            db_connection_pool = await self._measure_db_connections()
            active_connections = await self._measure_active_connections()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=cpu_percent,
                memory_usage=memory_usage,
                disk_io=disk_io,
                network_io=network_io,
                response_time=response_time,
                throughput=throughput,
                error_rate=error_rate,
                queue_depth=queue_depth,
                cache_hit_ratio=cache_hit_ratio,
                db_connection_pool=db_connection_pool,
                active_connections=active_connections
            )
            
            # Update Prometheus metrics
            self.cpu_usage_gauge.set(cpu_percent)
            self.memory_usage_gauge.set(memory_usage)
            self.response_time_histogram.labels(service="main", endpoint="all").observe(response_time / 1000)
            self.throughput_counter.labels(service="main").inc(throughput)
            self.error_rate_gauge.labels(service="main").set(error_rate)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
            return None
    
    async def _measure_response_time(self) -> float:
        """Measure average response time"""
        # Simulate response time measurement
        # In real implementation, this would measure actual API response times
        return np.random.normal(500, 100)  # ms
    
    async def _measure_throughput(self) -> float:
        """Measure system throughput"""
        # Simulate throughput measurement
        return np.random.poisson(150)  # requests per second
    
    async def _measure_error_rate(self) -> float:
        """Measure error rate"""
        # Simulate error rate measurement
        return np.random.exponential(0.5)  # percentage
    
    async def _measure_queue_depth(self) -> int:
        """Measure queue depth"""
        # Simulate queue depth measurement
        return np.random.poisson(5)
    
    async def _measure_cache_hit_ratio(self) -> float:
        """Measure cache hit ratio"""
        # Simulate cache hit ratio measurement
        return np.random.uniform(70, 95)  # percentage
    
    async def _measure_db_connections(self) -> int:
        """Measure database connection pool usage"""
        # Simulate DB connection measurement
        return np.random.randint(5, 20)
    
    async def _measure_active_connections(self) -> int:
        """Measure active connections"""
        # Simulate active connections measurement
        return np.random.randint(10, 100)
    
    async def train_anomaly_detector(self, training_data: Optional[List[PerformanceMetrics]] = None):
        """Train ML-based anomaly detector"""
        
        try:
            if training_data is None:
                training_data = self.metrics_history[-1000:]  # Use last 1000 data points
            
            if len(training_data) < 50:
                logger.warning("Insufficient training data for anomaly detection")
                return
            
            # Prepare features
            features = []
            for metrics in training_data:
                feature_vector = [
                    metrics.cpu_usage,
                    metrics.memory_usage,
                    metrics.disk_io,
                    metrics.network_io,
                    metrics.response_time,
                    metrics.throughput,
                    metrics.error_rate,
                    metrics.queue_depth,
                    metrics.cache_hit_ratio,
                    metrics.db_connection_pool,
                    metrics.active_connections
                ]
                features.append(feature_vector)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train isolation forest
            self.anomaly_detector = IsolationForest(
                contamination=0.1,  # 10% of data expected to be anomalies
                random_state=42
            )
            self.anomaly_detector.fit(features_scaled)
            self.is_trained = True
            
            logger.info("Anomaly detector trained successfully")
            
        except Exception as e:
            logger.error(f"Failed to train anomaly detector: {e}")
    
    async def detect_anomalies(self, metrics: PerformanceMetrics) -> Tuple[bool, float]:
        """Detect performance anomalies using ML"""
        
        if not self.is_trained or self.anomaly_detector is None:
            return False, 0.0
        
        try:
            # Prepare feature vector
            feature_vector = [
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.disk_io,
                metrics.network_io,
                metrics.response_time,
                metrics.throughput,
                metrics.error_rate,
                metrics.queue_depth,
                metrics.cache_hit_ratio,
                metrics.db_connection_pool,
                metrics.active_connections
            ]
            
            # Scale features
            feature_scaled = self.scaler.transform([feature_vector])
            
            # Predict anomaly
            anomaly_score = self.anomaly_detector.decision_function(feature_scaled)[0]
            is_anomaly = self.anomaly_detector.predict(feature_scaled)[0] == -1
            
            # Update Prometheus metrics
            self.anomaly_score_gauge.set(anomaly_score)
            
            return is_anomaly, anomaly_score
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return False, 0.0
    
    async def analyze_performance(self, metrics: PerformanceMetrics) -> List[OptimizationRecommendation]:
        """Analyze performance and generate optimization recommendations"""
        
        recommendations = []
        
        try:
            # Check each optimization rule
            for rule in self.optimization_rules:
                if rule["condition"](metrics):
                    recommendation = OptimizationRecommendation(
                        category=rule["category"],
                        priority=rule["priority"],
                        title=rule["name"].replace("_", " ").title(),
                        description=rule["description"],
                        impact_score=self._calculate_impact_score(rule, metrics),
                        implementation_effort=self._estimate_effort(rule),
                        estimated_improvement=self._estimate_improvement(rule, metrics),
                        code_example=self._generate_code_example(rule)
                    )
                    recommendations.append(recommendation)
            
            # Sort by priority and impact
            recommendations.sort(key=lambda x: (x.priority, x.impact_score), reverse=True)
            
            # Update Prometheus metrics
            for rec in recommendations:
                self.performance_improvement_counter.labels(
                    category=rec.category,
                    type=rec.title.lower().replace(" ", "_")
                ).inc()
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to analyze performance: {e}")
            return []
    
    def _calculate_impact_score(self, rule: Dict[str, Any], metrics: PerformanceMetrics) -> float:
        """Calculate impact score for optimization recommendation"""
        
        # Base impact scores by category
        category_impacts = {
            "database": 0.8,
            "caching": 0.7,
            "memory": 0.9,
            "cpu": 0.8,
            "performance": 0.9
        }
        
        base_impact = category_impacts.get(rule["category"], 0.5)
        
        # Adjust based on current metrics severity
        if rule["category"] == "memory" and metrics.memory_usage > 90:
            base_impact *= 1.2
        elif rule["category"] == "cpu" and metrics.cpu_usage > 90:
            base_impact *= 1.2
        elif rule["category"] == "performance" and metrics.response_time > 5000:
            base_impact *= 1.3
        
        return min(base_impact, 1.0)
    
    def _estimate_effort(self, rule: Dict[str, Any]) -> str:
        """Estimate implementation effort for optimization"""
        
        effort_mapping = {
            "database_connection_pooling": "low",
            "cache_optimization": "medium",
            "memory_optimization": "high",
            "cpu_optimization": "high",
            "response_time_optimization": "medium",
            "throughput_optimization": "medium"
        }
        
        return effort_mapping.get(rule["name"], "medium")
    
    def _estimate_improvement(self, rule: Dict[str, Any], metrics: PerformanceMetrics) -> str:
        """Estimate performance improvement"""
        
        improvements = {
            "database_connection_pooling": "20-30% faster DB queries",
            "cache_optimization": "40-60% faster cache hits",
            "memory_optimization": "15-25% memory reduction",
            "cpu_optimization": "20-35% CPU reduction",
            "response_time_optimization": "30-50% faster responses",
            "throughput_optimization": "25-40% higher throughput"
        }
        
        return improvements.get(rule["name"], "10-20% improvement")
    
    def _generate_code_example(self, rule: Dict[str, Any]) -> str:
        """Generate code example for optimization"""
        
        examples = {
            "database_connection_pooling": """
# Increase database connection pool
DATABASE_CONFIG = {
    'min_connections': 10,
    'max_connections': 50,
    'connection_timeout': 30
}
""",
            "cache_optimization": """
# Implement Redis caching
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key):
    cached = cache.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cached_data(key, data, ttl=3600):
    cache.setex(key, ttl, json.dumps(data))
""",
            "memory_optimization": """
# Optimize memory usage
import gc
import weakref

# Use weak references for large objects
large_object_ref = weakref.ref(large_object)

# Force garbage collection
gc.collect()

# Use generators instead of lists for large datasets
def process_large_dataset(data):
    for item in data:
        yield process_item(item)
""",
            "cpu_optimization": """
# Optimize CPU usage with async/await
import asyncio
import aiohttp

async def process_requests_async(requests):
    async with aiohttp.ClientSession() as session:
        tasks = [process_request(session, req) for req in requests]
        return await asyncio.gather(*tasks)
""",
            "response_time_optimization": """
# Optimize response time with connection pooling
import httpx

async with httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
) as client:
    response = await client.get(url)
""",
            "throughput_optimization": """
# Optimize throughput with batch processing
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_batch_async(items, batch_size=100):
    with ThreadPoolExecutor(max_workers=10) as executor:
        batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
        tasks = [executor.submit(process_batch, batch) for batch in batches]
        return await asyncio.gather(*[asyncio.wrap_future(task) for task in tasks])
"""
        }
        
        return examples.get(rule["name"], "# Code example not available")
    
    async def calculate_optimization_score(self, metrics: PerformanceMetrics) -> float:
        """Calculate overall optimization score (0-100)"""
        
        try:
            # Weighted scoring based on different metrics
            scores = {
                "cpu": max(0, 100 - metrics.cpu_usage),
                "memory": max(0, 100 - metrics.memory_usage),
                "response_time": max(0, 100 - (metrics.response_time / 100)),  # Convert ms to score
                "error_rate": max(0, 100 - (metrics.error_rate * 10)),  # Convert % to score
                "throughput": min(100, metrics.throughput),
                "cache_hit_ratio": metrics.cache_hit_ratio
            }
            
            # Weighted average
            weights = {
                "cpu": 0.2,
                "memory": 0.2,
                "response_time": 0.25,
                "error_rate": 0.15,
                "throughput": 0.1,
                "cache_hit_ratio": 0.1
            }
            
            total_score = sum(scores[metric] * weights[metric] for metric in scores)
            
            # Update Prometheus metrics
            self.optimization_score_gauge.set(total_score)
            
            return total_score
            
        except Exception as e:
            logger.error(f"Failed to calculate optimization score: {e}")
            return 0.0
    
    async def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data"""
        
        try:
            # Collect current metrics
            current_metrics = await self.collect_performance_metrics()
            if not current_metrics:
                return {"error": "Failed to collect metrics"}
            
            # Calculate optimization score
            optimization_score = await self.calculate_optimization_score(current_metrics)
            
            # Detect anomalies
            is_anomaly, anomaly_score = await self.detect_anomalies(current_metrics)
            
            # Generate recommendations
            recommendations = await self.analyze_performance(current_metrics)
            
            # Historical trends (last 24 hours)
            recent_metrics = [m for m in self.metrics_history 
                            if (datetime.utcnow() - m.timestamp).total_seconds() < 86400]
            
            trends = {
                "cpu_trend": [m.cpu_usage for m in recent_metrics[-24:]],
                "memory_trend": [m.memory_usage for m in recent_metrics[-24:]],
                "response_time_trend": [m.response_time for m in recent_metrics[-24:]],
                "throughput_trend": [m.throughput for m in recent_metrics[-24:]]
            }
            
            return {
                "timestamp": current_metrics.timestamp.isoformat(),
                "current_metrics": {
                    "cpu_usage": current_metrics.cpu_usage,
                    "memory_usage": current_metrics.memory_usage,
                    "response_time": current_metrics.response_time,
                    "throughput": current_metrics.throughput,
                    "error_rate": current_metrics.error_rate,
                    "cache_hit_ratio": current_metrics.cache_hit_ratio
                },
                "optimization_score": optimization_score,
                "anomaly_detected": is_anomaly,
                "anomaly_score": anomaly_score,
                "recommendations": [
                    {
                        "title": rec.title,
                        "category": rec.category,
                        "priority": rec.priority,
                        "impact_score": rec.impact_score,
                        "effort": rec.implementation_effort,
                        "improvement": rec.estimated_improvement
                    }
                    for rec in recommendations[:10]  # Top 10 recommendations
                ],
                "trends": trends,
                "optimization_level": self.optimization_level.value,
                "total_recommendations": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
    
    async def start_continuous_monitoring(self, interval_seconds: int = 30):
        """Start continuous performance monitoring"""
        
        logger.info(f"Starting continuous performance monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                # Collect metrics
                metrics = await self.collect_performance_metrics()
                if metrics:
                    self.metrics_history.append(metrics)
                    
                    # Keep only last 24 hours of data
                    cutoff_time = datetime.utcnow() - timedelta(hours=24)
                    self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff_time]
                    
                    # Train anomaly detector periodically
                    if len(self.metrics_history) % 100 == 0 and len(self.metrics_history) >= 50:
                        await self.train_anomaly_detector()
                    
                    # Log performance summary
                    optimization_score = await self.calculate_optimization_score(metrics)
                    logger.info(f"Performance Score: {optimization_score:.1f}/100 | "
                              f"CPU: {metrics.cpu_usage:.1f}% | "
                              f"Memory: {metrics.memory_usage:.1f}% | "
                              f"Response Time: {metrics.response_time:.1f}ms")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(interval_seconds)

# Example usage
async def main():
    """Example usage of the Ultra Performance Optimizer"""
    
    optimizer = UltraPerformanceOptimizer(
        optimization_level=OptimizationLevel.ULTRA,
        prometheus_port=8002
    )
    
    # Start continuous monitoring
    await optimizer.start_continuous_monitoring(interval_seconds=30)

if __name__ == "__main__":
    asyncio.run(main())
