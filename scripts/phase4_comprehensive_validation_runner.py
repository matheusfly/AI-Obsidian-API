#!/usr/bin/env python3
"""
Phase 4 Comprehensive Validation Runner
Run all Phase 4 validation tests with real data integration
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class Phase4ValidationRunner:
    """Comprehensive Phase 4 validation runner"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "phase": "Phase 4 Comprehensive Validation",
            "status": "running",
            "tests": {},
            "summary": {}
        }
        
        # Test scripts to run
        self.test_scripts = [
            {
                "name": "Quality Metrics Validation",
                "script": "phase4_quality_metrics_validation.py",
                "description": "Test Precision, MRR, NDCG calculation accuracy"
            },
            {
                "name": "User Feedback Collection Validation",
                "script": "phase4_feedback_validation.py",
                "description": "Test interactive feedback system and learning mechanisms"
            },
            {
                "name": "Response Quality Evaluation Validation",
                "script": "phase4_response_evaluation_validation.py",
                "description": "Test relevance scoring and response assessment"
            },
            {
                "name": "Performance Monitoring Validation",
                "script": "phase4_monitoring_validation.py",
                "description": "Test real-time metrics and system health monitoring"
            }
        ]
    
    def run_script(self, script_path: str) -> Dict[str, Any]:
        """Run a single validation script"""
        print(f"🚀 Running {script_path}...")
        
        try:
            # Run the script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            if result.returncode == 0:
                print(f"✅ {script_path} completed successfully")
                
                # Try to load JSON results if available
                result_file = script_path.replace('.py', '_results.json')
                if os.path.exists(result_file):
                    with open(result_file, 'r', encoding='utf-8') as f:
                        json_results = json.load(f)
                    return {
                        "status": "success",
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "json_results": json_results
                    }
                else:
                    return {
                        "status": "success",
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
            else:
                print(f"❌ {script_path} failed with return code {result.returncode}")
                return {
                    "status": "failed",
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {script_path} timed out")
            return {
                "status": "timeout",
                "return_code": -1,
                "stdout": "",
                "stderr": "Script timed out after 5 minutes"
            }
        except Exception as e:
            print(f"❌ Error running {script_path}: {e}")
            return {
                "status": "error",
                "return_code": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete Phase 4 validation"""
        print("🚀 Starting Phase 4 Comprehensive Validation")
        print("=" * 60)
        
        # Run each test script
        for test in self.test_scripts:
            print(f"\n📋 Running {test['name']}...")
            print(f"Description: {test['description']}")
            print("-" * 40)
            
            script_result = self.run_script(test['script'])
            
            self.results["tests"][test['name']] = {
                "script": test['script'],
                "description": test['description'],
                "result": script_result
            }
            
            # Print summary
            if script_result["status"] == "success":
                print(f"✅ {test['name']} - SUCCESS")
            elif script_result["status"] == "failed":
                print(f"❌ {test['name']} - FAILED")
                if script_result["stderr"]:
                    print(f"Error: {script_result['stderr']}")
            elif script_result["status"] == "timeout":
                print(f"⏰ {test['name']} - TIMEOUT")
            else:
                print(f"⚠️ {test['name']} - ERROR")
        
        # Calculate overall success
        successful_tests = sum(
            1 for test in self.results["tests"].values()
            if test["result"]["status"] == "success"
        )
        
        total_tests = len(self.test_scripts)
        overall_success = successful_tests == total_tests
        
        self.results["status"] = "completed" if overall_success else "failed"
        self.results["summary"] = {
            "overall_success": overall_success,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0
        }
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📊 Phase 4 Comprehensive Validation Summary:")
        print(f"Overall Success: {'✅ YES' if overall_success else '❌ NO'}")
        print(f"Total Tests: {total_tests}")
        print(f"Successful Tests: {successful_tests}")
        print(f"Failed Tests: {total_tests - successful_tests}")
        print(f"Success Rate: {successful_tests / total_tests * 100:.1f}%")
        
        return self.results

def main():
    """Main validation function"""
    runner = Phase4ValidationRunner()
    results = runner.run_validation()
    
    # Save results
    output_file = "phase4_comprehensive_validation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
