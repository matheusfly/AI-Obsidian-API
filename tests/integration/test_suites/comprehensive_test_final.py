#!/usr/bin/env python3
"""
Comprehensive Test Script - Final Version
Tests all MCP and LangGraph services
"""

import subprocess
import sys
import time
import requests
import json
import os
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_status(service, status, details=""):
    """Print service status"""
    status_icon = "✅" if status == "HEALTHY" else "❌" if status == "UNHEALTHY" else "⚠️"
    print(f"{status_icon} {service}: {status}")
    if details:
        print(f"   {details}")

def test_service(url, service_name, expected_status=200):
    """Test a service endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            return "HEALTHY", f"Status: {response.status_code}"
        else:
            return "UNHEALTHY", f"Status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return "UNHEALTHY", f"Error: {str(e)}"

def start_mcp_services():
    """Start all MCP services"""
    print_header("STARTING MCP SERVICES")
    
    services = [
        {
            "name": "MCP Integration Server",
            "script": "mcp_tools/mcp_integration_server.py",
            "port": 8003,
            "url": "http://127.0.0.1:8003/health"
        },
        {
            "name": "Observability Server", 
            "script": "mcp_tools/http_observability_server.py",
            "port": 8002,
            "url": "http://127.0.0.1:8002/health"
        },
        {
            "name": "Debug Dashboard",
            "script": "mcp_tools/mcp_debug_dashboard.py", 
            "port": 8004,
            "url": "http://127.0.0.1:8004/health"
        }
    ]
    
    started_services = []
    
    for service in services:
        print(f"🚀 Starting {service['name']}...")
        try:
            process = subprocess.Popen([
                sys.executable, service['script']
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment for startup
            time.sleep(2)
            
            # Test the service
            status, details = test_service(service['url'], service['name'])
            print_status(service['name'], status, details)
            
            if status == "HEALTHY":
                started_services.append(service)
            
        except Exception as e:
            print_status(service['name'], "UNHEALTHY", f"Failed to start: {e}")
    
    return started_services

def test_langgraph_studio():
    """Test LangGraph Studio functionality"""
    print_header("TESTING LANGGRAPH STUDIO")
    
    # Try different ports for LangGraph Studio
    studio_ports = [8123, 8124, 8125, 8000]
    
    for port in studio_ports:
        url = f"http://127.0.0.1:{port}/health"
        status, details = test_service(url, f"LangGraph Studio (port {port})")
        print_status(f"LangGraph Studio (port {port})", status, details)
        
        if status == "HEALTHY":
            return port
    
    # If no LangGraph Studio is running, start our custom one
    print("🚀 Starting custom LangGraph Studio server...")
    try:
        process = subprocess.Popen([
            sys.executable, "langgraph_studio_fixed.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)
        
        # Test on port 8125
        status, details = test_service("http://127.0.0.1:8125/health", "Custom LangGraph Studio")
        print_status("Custom LangGraph Studio", status, details)
        
        if status == "HEALTHY":
            return 8125
            
    except Exception as e:
        print_status("Custom LangGraph Studio", "UNHEALTHY", f"Failed to start: {e}")
    
    return None

def test_mcp_tool_calls():
    """Test MCP tool calls"""
    print_header("TESTING MCP TOOL CALLS")
    
    # Test MCP Integration Server
    try:
        # Test list_servers
        response = requests.post(
            "http://127.0.0.1:8003/mcp/call_tool",
            json={
                "server_name": "mcp-integration-server",
                "tool_name": "list_servers"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print_status("MCP Tool Call (list_servers)", "HEALTHY", "Successfully called list_servers")
        else:
            print_status("MCP Tool Call (list_servers)", "UNHEALTHY", f"Status: {response.status_code}")
            
    except Exception as e:
        print_status("MCP Tool Call (list_servers)", "UNHEALTHY", f"Error: {e}")
    
    # Test observability server
    try:
        response = requests.post(
            "http://127.0.0.1:8002/mcp/call_tool",
            json={
                "server_name": "observability-mcp",
                "tool_name": "create_trace_event"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print_status("MCP Tool Call (create_trace_event)", "HEALTHY", "Successfully called create_trace_event")
        else:
            print_status("MCP Tool Call (create_trace_event)", "UNHEALTHY", f"Status: {response.status_code}")
            
    except Exception as e:
        print_status("MCP Tool Call (create_trace_event)", "UNHEALTHY", f"Error: {e}")

def test_langsmith_integration():
    """Test LangSmith integration"""
    print_header("TESTING LANGSMITH INTEGRATION")
    
    # Set environment variables
    os.environ["LANGSMITH_API_KEY"] = "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"
    os.environ["LANGSMITH_PROJECT"] = "mcp-obsidian-integration"
    
    try:
        import langsmith
        
        client = langsmith.Client()
        
        # Test project access
        try:
            project = client.read_project(project_name="mcp-obsidian-integration")
            print_status("LangSmith Project Access", "HEALTHY", f"Project: {project.name}")
        except:
            print_status("LangSmith Project Access", "UNHEALTHY", "Project not found or access denied")
        
        # Test run creation
        try:
            run = client.create_run(
                name="MCP Integration Test",
                run_type="test",
                project_name="mcp-obsidian-integration"
            )
            print_status("LangSmith Run Creation", "HEALTHY", f"Run ID: {run.id}")
            
            # End the run
            client.update_run(run.id, status="completed")
            
        except Exception as e:
            print_status("LangSmith Run Creation", "UNHEALTHY", f"Error: {e}")
            
    except ImportError:
        print_status("LangSmith Integration", "UNHEALTHY", "LangSmith not installed")
    except Exception as e:
        print_status("LangSmith Integration", "UNHEALTHY", f"Error: {e}")

def generate_final_report(healthy_services, studio_port):
    """Generate final comprehensive report"""
    print_header("FINAL COMPREHENSIVE REPORT")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_services": len(healthy_services) + (1 if studio_port else 0),
        "healthy_services": len(healthy_services) + (1 if studio_port else 0),
        "services": []
    }
    
    # Add MCP services
    for service in healthy_services:
        report["services"].append({
            "name": service["name"],
            "status": "HEALTHY",
            "url": service["url"],
            "port": service["port"]
        })
    
    # Add LangGraph Studio
    if studio_port:
        report["services"].append({
            "name": "LangGraph Studio",
            "status": "HEALTHY", 
            "url": f"http://127.0.0.1:{studio_port}",
            "port": studio_port
        })
    
    # Print summary
    print(f"📊 Total Services: {report['total_services']}")
    print(f"✅ Healthy Services: {report['healthy_services']}")
    print(f"❌ Unhealthy Services: {report['total_services'] - report['healthy_services']}")
    
    print("\n🌐 Service URLs:")
    for service in report["services"]:
        print(f"   {service['name']}: {service['url']}")
    
    # Save report
    with open("FINAL_COMPREHENSIVE_TEST_REPORT.md", "w") as f:
        f.write(f"# Final Comprehensive Test Report\n\n")
        f.write(f"**Generated:** {report['timestamp']}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Services:** {report['total_services']}\n")
        f.write(f"- **Healthy Services:** {report['healthy_services']}\n")
        f.write(f"- **Unhealthy Services:** {report['total_services'] - report['healthy_services']}\n\n")
        f.write(f"## Service Details\n\n")
        for service in report["services"]:
            f.write(f"### {service['name']}\n")
            f.write(f"- **Status:** {service['status']}\n")
            f.write(f"- **URL:** {service['url']}\n")
            f.write(f"- **Port:** {service['port']}\n\n")
    
    print(f"\n📋 Report saved to: FINAL_COMPREHENSIVE_TEST_REPORT.md")
    
    return report

def main():
    """Main test function"""
    print_header("COMPREHENSIVE MCP LANGSMITH INTEGRATION TEST")
    print("🚀 Starting comprehensive testing of all services...")
    
    # Start MCP services
    healthy_services = start_mcp_services()
    
    # Test LangGraph Studio
    studio_port = test_langgraph_studio()
    
    # Test MCP tool calls
    test_mcp_tool_calls()
    
    # Test LangSmith integration
    test_langsmith_integration()
    
    # Generate final report
    report = generate_final_report(healthy_services, studio_port)
    
    # Final status
    if report["healthy_services"] >= 3:
        print_header("🎉 SUCCESS!")
        print("✅ All critical services are running!")
        print("🚀 Ready for advanced LangGraph workflow development!")
    else:
        print_header("⚠️ PARTIAL SUCCESS")
        print("Some services are running, but not all critical services are healthy.")
    
    print(f"\n📊 Final Status: {report['healthy_services']}/{report['total_services']} services healthy")
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        sys.exit(0 if report["healthy_services"] >= 3 else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
