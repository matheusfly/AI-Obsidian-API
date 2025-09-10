#!/usr/bin/env python3
"""
Tracing Analysis System for MCP Observability and LangSmith
Analyzes captured logs and traces to provide insights
"""

import json
import logging
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tracing_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TracingAnalysis:
    """Comprehensive tracing analysis system"""
    
    def __init__(self):
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "langsmith_analysis": {},
            "mcp_services_analysis": {},
            "performance_analysis": {},
            "error_analysis": {},
            "recommendations": []
        }
        
        # LangSmith configuration
        self.langsmith_api_key = "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"
        self.langsmith_project = "mcp-obsidian-integration"
        self.langsmith_base_url = "https://api.smith.langchain.com"
    
    def analyze_langsmith_traces(self, traces_data: List[Dict]) -> Dict:
        """Analyze LangSmith traces for patterns and insights"""
        logger.info("🔍 Analyzing LangSmith traces...")
        
        if not traces_data:
            return {"error": "No traces data provided"}
        
        analysis = {
            "total_traces": len(traces_data),
            "trace_ids": [trace.get("run_id") for trace in traces_data],
            "runs_analysis": [],
            "performance_metrics": {},
            "error_patterns": [],
            "usage_patterns": {}
        }
        
        # Analyze each trace
        for trace in traces_data:
            run_details = trace.get("run_details", {})
            events = trace.get("events", [])
            
            run_analysis = {
                "run_id": trace.get("run_id"),
                "status": run_details.get("status"),
                "start_time": run_details.get("start_time"),
                "end_time": run_details.get("end_time"),
                "total_events": len(events),
                "duration_ms": self.calculate_duration(run_details),
                "error_events": [e for e in events if e.get("event_type") == "error"],
                "tool_calls": [e for e in events if e.get("event_type") == "tool_call"],
                "llm_calls": [e for e in events if e.get("event_type") == "llm_call"]
            }
            
            analysis["runs_analysis"].append(run_analysis)
        
        # Calculate performance metrics
        durations = [r["duration_ms"] for r in analysis["runs_analysis"] if r["duration_ms"]]
        if durations:
            analysis["performance_metrics"] = {
                "avg_duration_ms": round(statistics.mean(durations), 2),
                "median_duration_ms": round(statistics.median(durations), 2),
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations),
                "std_deviation": round(statistics.stdev(durations) if len(durations) > 1 else 0, 2)
            }
        
        # Analyze error patterns
        all_errors = []
        for run in analysis["runs_analysis"]:
            all_errors.extend(run["error_events"])
        
        analysis["error_patterns"] = self.analyze_error_patterns(all_errors)
        
        # Analyze usage patterns
        analysis["usage_patterns"] = self.analyze_usage_patterns(analysis["runs_analysis"])
        
        logger.info(f"✅ Analyzed {len(traces_data)} LangSmith traces")
        return analysis
    
    def analyze_mcp_services(self, services_data: Dict) -> Dict:
        """Analyze MCP services data"""
        logger.info("🔗 Analyzing MCP services...")
        
        analysis = {
            "service_health": {},
            "performance_metrics": {},
            "error_analysis": {},
            "integration_status": {}
        }
        
        # Analyze each service
        for service_name, data in services_data.items():
            if not data:
                analysis["service_health"][service_name] = "NO_DATA"
                continue
            
            service_analysis = {
                "status": "HEALTHY" if data else "UNHEALTHY",
                "data_points": len(data) if isinstance(data, list) else 1,
                "last_update": datetime.now().isoformat()
            }
            
            # Analyze specific service data
            if service_name == "observability" and isinstance(data, dict):
                metrics = data.get("metrics", {})
                service_analysis["metrics"] = {
                    "total_requests": metrics.get("total_requests", 0),
                    "success_rate": metrics.get("success_rate", 0),
                    "avg_response_time": metrics.get("avg_response_time", 0)
                }
            
            elif service_name == "mcp_integration" and isinstance(data, dict):
                health = data.get("health", {})
                service_analysis["health_status"] = health.get("status", "unknown")
                service_analysis["servers_count"] = len(data.get("servers", {}).get("servers", []))
                service_analysis["tools_count"] = len(data.get("tools", {}).get("tools", []))
            
            analysis["service_health"][service_name] = service_analysis
        
        # Calculate overall health score
        healthy_services = sum(1 for s in analysis["service_health"].values() 
                             if isinstance(s, dict) and s.get("status") == "HEALTHY")
        total_services = len(analysis["service_health"])
        analysis["overall_health_score"] = round((healthy_services / total_services) * 100, 2) if total_services > 0 else 0
        
        logger.info(f"✅ Analyzed {len(services_data)} MCP services")
        return analysis
    
    def analyze_performance_metrics(self, system_metrics: Dict) -> Dict:
        """Analyze system performance metrics"""
        logger.info("💻 Analyzing performance metrics...")
        
        analysis = {
            "cpu_analysis": {},
            "memory_analysis": {},
            "network_analysis": {},
            "recommendations": []
        }
        
        # CPU analysis
        cpu_percent = system_metrics.get("cpu_percent", 0)
        analysis["cpu_analysis"] = {
            "current_usage": cpu_percent,
            "status": "HIGH" if cpu_percent > 80 else "NORMAL" if cpu_percent < 50 else "MODERATE",
            "recommendation": "Consider optimizing services" if cpu_percent > 80 else "CPU usage is normal"
        }
        
        # Memory analysis
        memory_percent = system_metrics.get("memory_percent", 0)
        analysis["memory_analysis"] = {
            "current_usage": memory_percent,
            "status": "HIGH" if memory_percent > 80 else "NORMAL" if memory_percent < 50 else "MODERATE",
            "recommendation": "Consider restarting services" if memory_percent > 80 else "Memory usage is normal"
        }
        
        # Network analysis
        network_traces = system_metrics.get("network_traces", [])
        if network_traces:
            response_times = [trace.get("response_time_ms", 0) for trace in network_traces if trace.get("response_time_ms")]
            analysis["network_analysis"] = {
                "total_connections": len(network_traces),
                "avg_response_time_ms": round(statistics.mean(response_times), 2) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0,
                "failed_connections": len([t for t in network_traces if "error" in t])
            }
        
        # Generate recommendations
        if cpu_percent > 80:
            analysis["recommendations"].append("High CPU usage detected - consider optimizing services")
        if memory_percent > 80:
            analysis["recommendations"].append("High memory usage detected - consider restarting services")
        if analysis["network_analysis"].get("failed_connections", 0) > 0:
            analysis["recommendations"].append("Network connection failures detected - check service availability")
        
        logger.info("✅ Performance analysis completed")
        return analysis
    
    def analyze_error_patterns(self, error_events: List[Dict]) -> Dict:
        """Analyze error patterns from events"""
        if not error_events:
            return {"total_errors": 0, "error_types": {}, "common_errors": []}
        
        error_types = Counter()
        error_messages = Counter()
        
        for error in error_events:
            error_type = error.get("event_type", "unknown")
            error_message = error.get("error", {}).get("message", "unknown error")
            
            error_types[error_type] += 1
            error_messages[error_message] += 1
        
        return {
            "total_errors": len(error_events),
            "error_types": dict(error_types),
            "common_errors": error_messages.most_common(5),
            "error_rate": len(error_events) / max(1, len(error_events)) * 100
        }
    
    def analyze_usage_patterns(self, runs_analysis: List[Dict]) -> Dict:
        """Analyze usage patterns from runs"""
        if not runs_analysis:
            return {"total_runs": 0, "tool_usage": {}, "llm_usage": {}}
        
        tool_usage = Counter()
        llm_usage = Counter()
        
        for run in runs_analysis:
            for tool_call in run.get("tool_calls", []):
                tool_name = tool_call.get("name", "unknown")
                tool_usage[tool_name] += 1
            
            for llm_call in run.get("llm_calls", []):
                model_name = llm_call.get("model", "unknown")
                llm_usage[model_name] += 1
        
        return {
            "total_runs": len(runs_analysis),
            "tool_usage": dict(tool_usage),
            "llm_usage": dict(llm_usage),
            "most_used_tools": tool_usage.most_common(5),
            "most_used_models": llm_usage.most_common(5)
        }
    
    def calculate_duration(self, run_details: Dict) -> Optional[float]:
        """Calculate duration of a run in milliseconds"""
        start_time = run_details.get("start_time")
        end_time = run_details.get("end_time")
        
        if not start_time or not end_time:
            return None
        
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).total_seconds() * 1000
            return round(duration, 2)
        except Exception:
            return None
    
    def generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # LangSmith recommendations
        langsmith_analysis = analysis_data.get("langsmith_analysis", {})
        if langsmith_analysis.get("total_traces", 0) == 0:
            recommendations.append("No LangSmith traces found - check API configuration and project setup")
        
        error_patterns = langsmith_analysis.get("error_patterns", {})
        if error_patterns.get("total_errors", 0) > 0:
            recommendations.append(f"Found {error_patterns['total_errors']} errors in traces - review error patterns")
        
        # MCP services recommendations
        mcp_analysis = analysis_data.get("mcp_services_analysis", {})
        health_score = mcp_analysis.get("overall_health_score", 0)
        if health_score < 80:
            recommendations.append(f"MCP services health score is {health_score}% - check service status")
        
        # Performance recommendations
        performance_analysis = analysis_data.get("performance_analysis", {})
        for rec in performance_analysis.get("recommendations", []):
            recommendations.append(rec)
        
        if not recommendations:
            recommendations.append("All systems appear to be functioning normally")
        
        return recommendations
    
    def analyze_captured_data(self, captured_data: Dict) -> Dict:
        """Analyze all captured data comprehensively"""
        logger.info("🚀 Starting comprehensive analysis...")
        
        # Analyze LangSmith traces
        langsmith_traces = captured_data.get("langsmith_traces", [])
        self.analysis_results["langsmith_analysis"] = self.analyze_langsmith_traces(langsmith_traces)
        
        # Analyze MCP services
        mcp_services_data = {
            "observability": captured_data.get("mcp_observability_logs"),
            "mcp_integration": captured_data.get("mcp_integration_logs"),
            "debug_dashboard": captured_data.get("debug_dashboard_logs"),
            "langgraph_studio": captured_data.get("langgraph_studio_logs")
        }
        self.analysis_results["mcp_services_analysis"] = self.analyze_mcp_services(mcp_services_data)
        
        # Analyze performance metrics
        system_metrics = captured_data.get("system_metrics", {})
        self.analysis_results["performance_analysis"] = self.analyze_performance_metrics(system_metrics)
        
        # Generate overall recommendations
        self.analysis_results["recommendations"] = self.generate_recommendations(self.analysis_results)
        
        # Add metadata
        self.analysis_results.update({
            "analysis_completed_at": datetime.now().isoformat(),
            "data_sources_analyzed": len([k for k, v in captured_data.items() if v]),
            "total_analysis_points": sum([
                len(self.analysis_results.get("langsmith_analysis", {}).get("trace_ids", [])),
                len(self.analysis_results.get("mcp_services_analysis", {}).get("service_health", {})),
                1 if self.analysis_results.get("performance_analysis") else 0
            ])
        })
        
        logger.info("✅ Comprehensive analysis completed")
        return self.analysis_results
    
    def save_analysis_report(self, filename: str = None) -> str:
        """Save analysis report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tracing_analysis_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Analysis report saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis report: {e}")
            return ""
    
    def print_summary_report(self):
        """Print a summary report to console"""
        print("\n📊 TRACING ANALYSIS SUMMARY")
        print("=" * 50)
        
        # LangSmith summary
        langsmith = self.analysis_results.get("langsmith_analysis", {})
        print(f"🔍 LangSmith Traces: {langsmith.get('total_traces', 0)}")
        if langsmith.get("performance_metrics"):
            perf = langsmith["performance_metrics"]
            print(f"   Avg Duration: {perf.get('avg_duration_ms', 0)}ms")
            print(f"   Max Duration: {perf.get('max_duration_ms', 0)}ms")
        
        # MCP Services summary
        mcp = self.analysis_results.get("mcp_services_analysis", {})
        print(f"🔗 MCP Services Health: {mcp.get('overall_health_score', 0)}%")
        for service, health in mcp.get("service_health", {}).items():
            if isinstance(health, dict):
                status = health.get("status", "UNKNOWN")
                print(f"   {service}: {status}")
        
        # Performance summary
        perf = self.analysis_results.get("performance_analysis", {})
        cpu = perf.get("cpu_analysis", {})
        memory = perf.get("memory_analysis", {})
        print(f"💻 System Performance:")
        print(f"   CPU: {cpu.get('current_usage', 0)}% ({cpu.get('status', 'UNKNOWN')})")
        print(f"   Memory: {memory.get('current_usage', 0)}% ({memory.get('status', 'UNKNOWN')})")
        
        # Recommendations
        recommendations = self.analysis_results.get("recommendations", [])
        print(f"\n💡 Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")

def main():
    """Main execution function"""
    print("🔍 TRACING ANALYSIS SYSTEM")
    print("=" * 50)
    
    # Check if we have captured data files
    data_files = [f for f in os.listdir('.') if f.startswith('raw_data_capture_') and f.endswith('.json')]
    
    if not data_files:
        print("❌ No captured data files found. Run raw_data_capture.py first.")
        return
    
    # Use the most recent data file
    latest_file = max(data_files, key=os.path.getctime)
    print(f"📁 Using data file: {latest_file}")
    
    try:
        # Load captured data
        with open(latest_file, 'r', encoding='utf-8') as f:
            captured_data = json.load(f)
        
        # Initialize analyzer
        analyzer = TracingAnalysis()
        
        # Analyze data
        analysis_results = analyzer.analyze_captured_data(captured_data)
        
        # Save analysis report
        report_filename = analyzer.save_analysis_report()
        
        # Print summary
        analyzer.print_summary_report()
        
        print(f"\n💾 Full analysis report saved to: {report_filename}")
        print("✅ Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}")
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()
