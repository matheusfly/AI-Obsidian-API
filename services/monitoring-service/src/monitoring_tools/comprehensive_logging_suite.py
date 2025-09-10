#!/usr/bin/env python3
"""
Comprehensive Logging Suite for MCP Observability and LangSmith Tracing
Runs all logging, monitoring, and analysis tools
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_logging_suite.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveLoggingSuite:
    """Comprehensive logging and tracing suite"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            "suite_start_time": self.start_time.isoformat(),
            "raw_data_capture": {},
            "realtime_monitoring": {},
            "tracing_analysis": {},
            "summary": {}
        }
        
        # Script paths
        self.scripts = {
            "raw_data_capture": "raw_data_capture.py",
            "realtime_monitor": "realtime_log_monitor.py", 
            "tracing_analysis": "tracing_analysis.py"
        }
    
    async def run_raw_data_capture(self, duration_seconds: int = 60) -> Dict:
        """Run raw data capture for specified duration"""
        logger.info("🚀 Starting raw data capture...")
        
        try:
            # Run raw data capture
            result = subprocess.run([
                sys.executable, self.scripts["raw_data_capture"]
            ], capture_output=True, text=True, timeout=duration_seconds)
            
            capture_result = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_seconds": duration_seconds,
                "completed_at": datetime.now().isoformat()
            }
            
            if result.returncode == 0:
                logger.info("✅ Raw data capture completed successfully")
            else:
                logger.error(f"❌ Raw data capture failed: {result.stderr}")
            
            return capture_result
            
        except subprocess.TimeoutExpired:
            logger.warning(f"⚠️ Raw data capture timed out after {duration_seconds} seconds")
            return {"error": "timeout", "duration_seconds": duration_seconds}
        except Exception as e:
            logger.error(f"❌ Error running raw data capture: {e}")
            return {"error": str(e)}
    
    async def run_realtime_monitoring(self, duration_seconds: int = 120) -> Dict:
        """Run real-time monitoring for specified duration"""
        logger.info("📊 Starting real-time monitoring...")
        
        try:
            # Start real-time monitoring in background
            process = subprocess.Popen([
                sys.executable, self.scripts["realtime_monitor"]
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Let it run for specified duration
            await asyncio.sleep(duration_seconds)
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            monitoring_result = {
                "duration_seconds": duration_seconds,
                "process_pid": process.pid,
                "completed_at": datetime.now().isoformat()
            }
            
            logger.info("✅ Real-time monitoring completed")
            return monitoring_result
            
        except Exception as e:
            logger.error(f"❌ Error running real-time monitoring: {e}")
            return {"error": str(e)}
    
    async def run_tracing_analysis(self) -> Dict:
        """Run tracing analysis on captured data"""
        logger.info("🔍 Starting tracing analysis...")
        
        try:
            # Run tracing analysis
            result = subprocess.run([
                sys.executable, self.scripts["tracing_analysis"]
            ], capture_output=True, text=True, timeout=60)
            
            analysis_result = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "completed_at": datetime.now().isoformat()
            }
            
            if result.returncode == 0:
                logger.info("✅ Tracing analysis completed successfully")
            else:
                logger.error(f"❌ Tracing analysis failed: {result.stderr}")
            
            return analysis_result
            
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Tracing analysis timed out")
            return {"error": "timeout"}
        except Exception as e:
            logger.error(f"❌ Error running tracing analysis: {e}")
            return {"error": str(e)}
    
    def collect_generated_files(self) -> Dict:
        """Collect all generated files and their information"""
        logger.info("📁 Collecting generated files...")
        
        file_patterns = [
            "raw_data_capture_*.json",
            "realtime_logs_*.json", 
            "tracing_analysis_report_*.json",
            "*.log"
        ]
        
        generated_files = []
        
        for pattern in file_patterns:
            if "*" in pattern:
                # Find files matching pattern
                import glob
                matching_files = glob.glob(pattern)
                for file_path in matching_files:
                    try:
                        stat = os.stat(file_path)
                        generated_files.append({
                            "filename": file_path,
                            "size_bytes": stat.st_size,
                            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get stats for {file_path}: {e}")
            else:
                if os.path.exists(pattern):
                    try:
                        stat = os.stat(pattern)
                        generated_files.append({
                            "filename": pattern,
                            "size_bytes": stat.st_size,
                            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"⚠️ Could not get stats for {pattern}: {e}")
        
        logger.info(f"📁 Found {len(generated_files)} generated files")
        return {"files": generated_files, "total_files": len(generated_files)}
    
    def generate_summary_report(self) -> Dict:
        """Generate comprehensive summary report"""
        logger.info("📋 Generating summary report...")
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            "suite_execution_time": total_duration,
            "suite_completed_at": datetime.now().isoformat(),
            "components_executed": list(self.results.keys()),
            "successful_components": [],
            "failed_components": [],
            "generated_files": self.collect_generated_files(),
            "recommendations": []
        }
        
        # Analyze component results
        for component, result in self.results.items():
            if component == "summary":
                continue
                
            if isinstance(result, dict):
                if result.get("error"):
                    summary["failed_components"].append(component)
                else:
                    summary["successful_components"].append(component)
        
        # Generate recommendations
        if summary["failed_components"]:
            summary["recommendations"].append(f"Review failed components: {', '.join(summary['failed_components'])}")
        
        if not summary["successful_components"]:
            summary["recommendations"].append("No components executed successfully - check system configuration")
        
        if summary["generated_files"]["total_files"] == 0:
            summary["recommendations"].append("No files were generated - check script execution")
        
        summary["recommendations"].append("Review generated log files for detailed insights")
        summary["recommendations"].append("Use tracing analysis reports to optimize system performance")
        
        return summary
    
    async def run_comprehensive_suite(self, 
                                    raw_data_duration: int = 60,
                                    monitoring_duration: int = 120) -> Dict:
        """Run the complete comprehensive logging suite"""
        logger.info("🚀 Starting Comprehensive Logging Suite")
        logger.info("=" * 60)
        
        try:
            # Step 1: Raw Data Capture
            logger.info("Step 1/3: Raw Data Capture")
            self.results["raw_data_capture"] = await self.run_raw_data_capture(raw_data_duration)
            
            # Step 2: Real-time Monitoring
            logger.info("Step 2/3: Real-time Monitoring")
            self.results["realtime_monitoring"] = await self.run_realtime_monitoring(monitoring_duration)
            
            # Step 3: Tracing Analysis
            logger.info("Step 3/3: Tracing Analysis")
            self.results["tracing_analysis"] = await self.run_tracing_analysis()
            
            # Generate summary
            self.results["summary"] = self.generate_summary_report()
            
            # Save complete results
            results_filename = f"comprehensive_logging_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Complete results saved to: {results_filename}")
            
            return self.results
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive suite: {e}")
            self.results["error"] = str(e)
            return self.results
    
    def print_final_summary(self):
        """Print final summary to console"""
        summary = self.results.get("summary", {})
        
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE LOGGING SUITE - FINAL SUMMARY")
        print("=" * 60)
        
        print(f"⏱️  Total Execution Time: {summary.get('suite_execution_time', 0):.2f} seconds")
        print(f"✅ Successful Components: {len(summary.get('successful_components', []))}")
        print(f"❌ Failed Components: {len(summary.get('failed_components', []))}")
        print(f"📁 Generated Files: {summary.get('generated_files', {}).get('total_files', 0)}")
        
        if summary.get('successful_components'):
            print(f"\n✅ Successful Components:")
            for component in summary['successful_components']:
                print(f"   • {component}")
        
        if summary.get('failed_components'):
            print(f"\n❌ Failed Components:")
            for component in summary['failed_components']:
                print(f"   • {component}")
        
        print(f"\n📁 Generated Files:")
        for file_info in summary.get('generated_files', {}).get('files', []):
            size_kb = file_info['size_bytes'] / 1024
            print(f"   • {file_info['filename']} ({size_kb:.1f} KB)")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(summary.get('recommendations', []), 1):
            print(f"   {i}. {rec}")
        
        print("\n🎉 Comprehensive logging suite completed!")
        print("=" * 60)

async def main():
    """Main execution function"""
    print("🚀 COMPREHENSIVE LOGGING SUITE")
    print("=" * 60)
    print("This suite will:")
    print("1. Capture raw data from all MCP services and LangSmith")
    print("2. Run real-time monitoring for 2 minutes")
    print("3. Analyze all captured data and generate reports")
    print("=" * 60)
    
    # Initialize suite
    suite = ComprehensiveLoggingSuite()
    
    try:
        # Run comprehensive suite
        results = await suite.run_comprehensive_suite(
            raw_data_duration=60,    # 1 minute raw data capture
            monitoring_duration=120   # 2 minutes real-time monitoring
        )
        
        # Print final summary
        suite.print_final_summary()
        
        return results
        
    except KeyboardInterrupt:
        print("\n🛑 Suite interrupted by user")
        suite.print_final_summary()
        return suite.results
    except Exception as e:
        print(f"\n❌ Suite failed: {e}")
        return suite.results

if __name__ == "__main__":
    asyncio.run(main())
