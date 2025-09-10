"""
Intelligent Alerting System with ML-based Anomaly Detection
Advanced alerting with machine learning for predictive monitoring
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import aiohttp
import asyncpg
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertType(Enum):
    SYSTEM = "system"
    SERVICE = "service"
    AI_AGENT = "ai_agent"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ANOMALY = "anomaly"
    PREDICTIVE = "predictive"

@dataclass
class Alert:
    id: str
    title: str
    description: str
    severity: AlertSeverity
    alert_type: AlertType
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    confidence_score: float = 0.0
    anomaly_score: float = 0.0
    predicted_impact: str = "unknown"

@dataclass
class MetricData:
    timestamp: datetime
    metric_name: str
    value: float
    labels: Dict[str, str] = None
    source: str = "unknown"

class AnomalyDetector:
    """Machine Learning-based Anomaly Detection"""
    
    def __init__(self, contamination=0.1, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=random_state
        )
        self.scaler = StandardScaler()
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        self.is_trained = False
        self.training_data = []
        self.feature_names = []
        
    def add_training_data(self, data: List[MetricData]):
        """Add training data for anomaly detection"""
        self.training_data.extend(data)
        logger.info(f"Added {len(data)} training samples. Total: {len(self.training_data)}")
    
    def prepare_features(self, data: List[MetricData]) -> np.ndarray:
        """Prepare features for ML models"""
        if not data:
            return np.array([])
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame([{
            'timestamp': d.timestamp,
            'value': d.value,
            'hour': d.timestamp.hour,
            'day_of_week': d.timestamp.weekday(),
            'is_weekend': 1 if d.timestamp.weekday() >= 5 else 0
        } for d in data])
        
        # Calculate additional features
        df['value_diff'] = df['value'].diff().fillna(0)
        df['value_rolling_mean'] = df['value'].rolling(window=5, min_periods=1).mean()
        df['value_rolling_std'] = df['value'].rolling(window=5, min_periods=1).std().fillna(0)
        df['value_zscore'] = (df['value'] - df['value'].mean()) / df['value'].std()
        
        # Select features for training
        feature_columns = ['value', 'hour', 'day_of_week', 'is_weekend', 
                          'value_diff', 'value_rolling_mean', 'value_rolling_std', 'value_zscore']
        
        self.feature_names = feature_columns
        return df[feature_columns].fillna(0).values
    
    def train(self):
        """Train the anomaly detection models"""
        if len(self.training_data) < 100:
            logger.warning("Insufficient training data. Need at least 100 samples.")
            return False
        
        try:
            # Prepare features
            X = self.prepare_features(self.training_data)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Isolation Forest
            self.isolation_forest.fit(X_scaled)
            
            # Train DBSCAN for clustering
            self.dbscan.fit(X_scaled)
            
            self.is_trained = True
            logger.info("Anomaly detection models trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to train anomaly detection models: {e}")
            return False
    
    def detect_anomalies(self, data: List[MetricData]) -> List[Tuple[MetricData, float, float]]:
        """Detect anomalies in the given data"""
        if not self.is_trained:
            logger.warning("Models not trained yet. Training with available data...")
            if not self.train():
                return []
        
        try:
            # Prepare features
            X = self.prepare_features(data)
            if X.size == 0:
                return []
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Get anomaly scores from Isolation Forest
            anomaly_scores = self.isolation_forest.decision_function(X_scaled)
            is_anomaly = self.isolation_forest.predict(X_scaled)
            
            # Get cluster assignments from DBSCAN
            cluster_labels = self.dbscan.fit_predict(X_scaled)
            
            # Combine results
            results = []
            for i, metric in enumerate(data):
                if is_anomaly[i] == -1:  # Anomaly detected
                    confidence = abs(anomaly_scores[i])
                    anomaly_score = 1.0 - (anomaly_scores[i] + 1) / 2  # Normalize to 0-1
                    results.append((metric, confidence, anomaly_score))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    def get_anomaly_explanation(self, metric: MetricData, confidence: float, anomaly_score: float) -> str:
        """Generate explanation for detected anomaly"""
        explanations = []
        
        if anomaly_score > 0.8:
            explanations.append("Extreme outlier detected")
        elif anomaly_score > 0.6:
            explanations.append("Significant deviation from normal pattern")
        else:
            explanations.append("Minor deviation detected")
        
        if confidence > 0.9:
            explanations.append("High confidence in anomaly detection")
        elif confidence > 0.7:
            explanations.append("Medium confidence in anomaly detection")
        else:
            explanations.append("Low confidence in anomaly detection")
        
        return "; ".join(explanations)

class IntelligentAlertingSystem:
    """Intelligent Alerting System with ML-based Anomaly Detection"""
    
    def __init__(self, 
                 database_url: Optional[str] = None,
                 prometheus_port: int = 8002,
                 alert_webhook_url: Optional[str] = None):
        self.database_url = database_url
        self.prometheus_port = prometheus_port
        self.alert_webhook_url = alert_webhook_url
        
        # Initialize components
        self.anomaly_detector = AnomalyDetector()
        self.alert_history: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.metric_history: Dict[str, List[MetricData]] = {}
        
        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()
        
        # Alert rules and thresholds
        self.alert_rules = self._initialize_alert_rules()
        self.alert_cooldowns: Dict[str, datetime] = {}
        
        logger.info("Intelligent Alerting System initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for alerting system"""
        
        self.alert_counter = Counter(
            'intelligent_alerts_total',
            'Total number of alerts generated',
            ['severity', 'alert_type', 'source'],
            registry=self.registry
        )
        
        self.anomaly_detection_accuracy = Gauge(
            'anomaly_detection_accuracy',
            'Accuracy of anomaly detection',
            registry=self.registry
        )
        
        self.active_alerts_gauge = Gauge(
            'active_alerts_count',
            'Number of active alerts',
            ['severity'],
            registry=self.registry
        )
        
        self.alert_resolution_time = Histogram(
            'alert_resolution_time_seconds',
            'Time taken to resolve alerts',
            ['alert_type'],
            buckets=[60, 300, 600, 1800, 3600, 7200, 86400],
            registry=self.registry
        )
    
    def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize alert rules and thresholds"""
        return {
            'cpu_usage': {
                'warning_threshold': 70.0,
                'critical_threshold': 85.0,
                'emergency_threshold': 95.0,
                'cooldown_minutes': 5
            },
            'memory_usage': {
                'warning_threshold': 80.0,
                'critical_threshold': 90.0,
                'emergency_threshold': 95.0,
                'cooldown_minutes': 5
            },
            'response_time': {
                'warning_threshold': 1000.0,  # ms
                'critical_threshold': 3000.0,
                'emergency_threshold': 10000.0,
                'cooldown_minutes': 2
            },
            'error_rate': {
                'warning_threshold': 1.0,  # %
                'critical_threshold': 5.0,
                'emergency_threshold': 10.0,
                'cooldown_minutes': 1
            },
            'ai_agent_failure': {
                'warning_threshold': 1,
                'critical_threshold': 3,
                'emergency_threshold': 5,
                'cooldown_minutes': 10
            },
            'token_usage_spike': {
                'warning_threshold': 2.0,  # 2x normal
                'critical_threshold': 5.0,
                'emergency_threshold': 10.0,
                'cooldown_minutes': 15
            }
        }
    
    async def add_metric_data(self, 
                            metric_name: str, 
                            value: float, 
                            source: str = "unknown",
                            labels: Dict[str, str] = None):
        """Add metric data for monitoring and anomaly detection"""
        
        metric_data = MetricData(
            timestamp=datetime.utcnow(),
            metric_name=metric_name,
            value=value,
            labels=labels or {},
            source=source
        )
        
        # Store in history
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = []
        
        self.metric_history[metric_name].append(metric_data)
        
        # Keep only recent data (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.metric_history[metric_name] = [
            m for m in self.metric_history[metric_name] 
            if m.timestamp >= cutoff_time
        ]
        
        # Add to anomaly detection training data
        self.anomaly_detector.add_training_data([metric_data])
        
        # Check for threshold-based alerts
        await self._check_threshold_alerts(metric_data)
        
        # Check for anomalies
        await self._check_anomaly_alerts(metric_name)
    
    async def _check_threshold_alerts(self, metric_data: MetricData):
        """Check for threshold-based alerts"""
        
        metric_name = metric_data.metric_name
        value = metric_data.value
        
        if metric_name not in self.alert_rules:
            return
        
        rules = self.alert_rules[metric_name]
        cooldown_key = f"{metric_name}_{metric_data.source}"
        
        # Check cooldown
        if cooldown_key in self.alert_cooldowns:
            if (datetime.utcnow() - self.alert_cooldowns[cooldown_key]).total_seconds() < rules['cooldown_minutes'] * 60:
                return
        
        # Determine severity
        severity = None
        if value >= rules.get('emergency_threshold', float('inf')):
            severity = AlertSeverity.EMERGENCY
        elif value >= rules.get('critical_threshold', float('inf')):
            severity = AlertSeverity.CRITICAL
        elif value >= rules.get('warning_threshold', float('inf')):
            severity = AlertSeverity.WARNING
        
        if severity:
            await self._create_alert(
                title=f"{metric_name.replace('_', ' ').title()} Alert",
                description=f"{metric_name} is {value} (threshold: {rules[f'{severity.value}_threshold']})",
                severity=severity,
                alert_type=AlertType.PERFORMANCE,
                source=metric_data.source,
                metadata={
                    'metric_name': metric_name,
                    'value': value,
                    'threshold': rules[f'{severity.value}_threshold'],
                    'labels': metric_data.labels
                }
            )
            
            # Set cooldown
            self.alert_cooldowns[cooldown_key] = datetime.utcnow()
    
    async def _check_anomaly_alerts(self, metric_name: str):
        """Check for anomaly-based alerts"""
        
        if metric_name not in self.metric_history:
            return
        
        # Get recent data for anomaly detection
        recent_data = self.metric_history[metric_name][-50:]  # Last 50 data points
        
        if len(recent_data) < 10:
            return
        
        # Detect anomalies
        anomalies = self.anomaly_detector.detect_anomalies(recent_data)
        
        for metric, confidence, anomaly_score in anomalies:
            # Only alert on high-confidence anomalies
            if confidence > 0.7 and anomaly_score > 0.6:
                await self._create_alert(
                    title=f"Anomaly Detected in {metric_name.replace('_', ' ').title()}",
                    description=f"Unusual pattern detected: {self.anomaly_detector.get_anomaly_explanation(metric, confidence, anomaly_score)}",
                    severity=AlertSeverity.WARNING,
                    alert_type=AlertType.ANOMALY,
                    source=metric.source,
                    metadata={
                        'metric_name': metric_name,
                        'value': metric.value,
                        'confidence': confidence,
                        'anomaly_score': anomaly_score,
                        'labels': metric.labels
                    },
                    confidence_score=confidence,
                    anomaly_score=anomaly_score
                )
    
    async def _create_alert(self, 
                          title: str,
                          description: str,
                          severity: AlertSeverity,
                          alert_type: AlertType,
                          source: str,
                          metadata: Dict[str, Any] = None,
                          confidence_score: float = 1.0,
                          anomaly_score: float = 0.0) -> Alert:
        """Create a new alert"""
        
        alert_id = f"{alert_type.value}_{source}_{int(datetime.utcnow().timestamp())}"
        
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            alert_type=alert_type,
            source=source,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            confidence_score=confidence_score,
            anomaly_score=anomaly_score
        )
        
        # Add to history
        self.alert_history.append(alert)
        self.active_alerts[alert_id] = alert
        
        # Update Prometheus metrics
        self.alert_counter.labels(
            severity=severity.value,
            alert_type=alert_type.value,
            source=source
        ).inc()
        
        # Update active alerts gauge
        self._update_active_alerts_gauge()
        
        # Send webhook notification
        if self.alert_webhook_url:
            await self._send_webhook_notification(alert)
        
        logger.info(f"Alert created: {alert_id} - {title}")
        return alert
    
    async def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification for alert"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'alert_id': alert.id,
                    'title': alert.title,
                    'description': alert.description,
                    'severity': alert.severity.value,
                    'alert_type': alert.alert_type.value,
                    'source': alert.source,
                    'timestamp': alert.timestamp.isoformat(),
                    'metadata': alert.metadata,
                    'confidence_score': alert.confidence_score,
                    'anomaly_score': alert.anomaly_score
                }
                
                async with session.post(
                    self.alert_webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent for alert {alert.id}")
                    else:
                        logger.warning(f"Webhook notification failed for alert {alert.id}: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    def _update_active_alerts_gauge(self):
        """Update active alerts gauge"""
        for severity in AlertSeverity:
            count = len([a for a in self.active_alerts.values() if a.severity == severity])
            self.active_alerts_gauge.labels(severity=severity.value).set(count)
    
    async def resolve_alert(self, alert_id: str, resolution_notes: str = ""):
        """Resolve an alert"""
        
        if alert_id not in self.active_alerts:
            logger.warning(f"Alert {alert_id} not found in active alerts")
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        
        # Calculate resolution time
        resolution_time = (alert.resolved_at - alert.timestamp).total_seconds()
        
        # Update Prometheus metrics
        self.alert_resolution_time.labels(
            alert_type=alert.alert_type.value
        ).observe(resolution_time)
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        self._update_active_alerts_gauge()
        
        logger.info(f"Alert {alert_id} resolved in {resolution_time:.2f} seconds")
        return True
    
    async def get_alert_summary(self, 
                              severity_filter: Optional[AlertSeverity] = None,
                              alert_type_filter: Optional[AlertType] = None,
                              hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for dashboard"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter alerts
        filtered_alerts = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time and
            (severity_filter is None or alert.severity == severity_filter) and
            (alert_type_filter is None or alert.alert_type == alert_type_filter)
        ]
        
        # Calculate statistics
        total_alerts = len(filtered_alerts)
        active_alerts = len([a for a in filtered_alerts if not a.resolved])
        resolved_alerts = len([a for a in filtered_alerts if a.resolved])
        
        # Group by severity
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len([a for a in filtered_alerts if a.severity == severity])
        
        # Group by type
        type_counts = {}
        for alert_type in AlertType:
            type_counts[alert_type.value] = len([a for a in filtered_alerts if a.alert_type == alert_type])
        
        # Calculate average resolution time
        resolved_with_time = [a for a in filtered_alerts if a.resolved and a.resolved_at]
        avg_resolution_time = 0
        if resolved_with_time:
            resolution_times = [(a.resolved_at - a.timestamp).total_seconds() for a in resolved_with_time]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        return {
            'time_window_hours': hours,
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'resolution_rate': (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0,
            'average_resolution_time_seconds': avg_resolution_time,
            'severity_breakdown': severity_counts,
            'type_breakdown': type_counts,
            'recent_alerts': [asdict(a) for a in filtered_alerts[-10:]]  # Last 10 alerts
        }
    
    async def train_anomaly_detection(self):
        """Train the anomaly detection models"""
        logger.info("Training anomaly detection models...")
        
        # Collect training data from all metrics
        all_training_data = []
        for metric_data_list in self.metric_history.values():
            all_training_data.extend(metric_data_list)
        
        if len(all_training_data) < 100:
            logger.warning("Insufficient data for training. Need at least 100 samples.")
            return False
        
        # Train the models
        success = self.anomaly_detector.train()
        
        if success:
            logger.info("Anomaly detection models trained successfully")
        else:
            logger.error("Failed to train anomaly detection models")
        
        return success
    
    async def get_anomaly_insights(self) -> Dict[str, Any]:
        """Get insights about detected anomalies"""
        
        # Analyze recent anomalies
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.alert_type == AlertType.ANOMALY and
            alert.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ]
        
        if not recent_alerts:
            return {"message": "No recent anomalies detected"}
        
        # Calculate anomaly statistics
        avg_confidence = sum(a.confidence_score for a in recent_alerts) / len(recent_alerts)
        avg_anomaly_score = sum(a.anomaly_score for a in recent_alerts) / len(recent_alerts)
        
        # Group by source
        source_counts = {}
        for alert in recent_alerts:
            source = alert.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Group by metric
        metric_counts = {}
        for alert in recent_alerts:
            metric = alert.metadata.get('metric_name', 'unknown')
            metric_counts[metric] = metric_counts.get(metric, 0) + 1
        
        return {
            'total_anomalies': len(recent_alerts),
            'average_confidence': avg_confidence,
            'average_anomaly_score': avg_anomaly_score,
            'sources_with_anomalies': source_counts,
            'metrics_with_anomalies': metric_counts,
            'recent_anomalies': [asdict(a) for a in recent_alerts[-5:]]  # Last 5 anomalies
        }
    
    async def export_metrics_to_prometheus(self):
        """Start Prometheus metrics server"""
        try:
            from prometheus_client import start_http_server
            start_http_server(self.prometheus_port, registry=self.registry)
            logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")

# Example usage and testing
async def main():
    """Example usage of the Intelligent Alerting System"""
    
    # Initialize the alerting system
    alerting_system = IntelligentAlertingSystem(
        prometheus_port=8002,
        alert_webhook_url="http://localhost:8080/webhook"  # Optional webhook URL
    )
    
    # Start Prometheus metrics server
    await alerting_system.export_metrics_to_prometheus()
    
    # Simulate some metric data
    for i in range(100):
        # Normal CPU usage
        cpu_usage = 50 + np.random.normal(0, 10)
        await alerting_system.add_metric_data("cpu_usage", max(0, min(100, cpu_usage)), "server-1")
        
        # Normal memory usage
        memory_usage = 60 + np.random.normal(0, 15)
        await alerting_system.add_metric_data("memory_usage", max(0, min(100, memory_usage)), "server-1")
        
        # Normal response time
        response_time = 500 + np.random.normal(0, 100)
        await alerting_system.add_metric_data("response_time", max(0, response_time), "api-server")
        
        # Simulate some anomalies
        if i % 20 == 0:
            # High CPU spike
            await alerting_system.add_metric_data("cpu_usage", 95, "server-1")
        
        if i % 30 == 0:
            # High memory usage
            await alerting_system.add_metric_data("memory_usage", 92, "server-1")
        
        await asyncio.sleep(0.1)
    
    # Train anomaly detection
    await alerting_system.train_anomaly_detection()
    
    # Get alert summary
    summary = await alerting_system.get_alert_summary()
    print("Alert Summary:", json.dumps(summary, indent=2, default=str))
    
    # Get anomaly insights
    insights = await alerting_system.get_anomaly_insights()
    print("Anomaly Insights:", json.dumps(insights, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
