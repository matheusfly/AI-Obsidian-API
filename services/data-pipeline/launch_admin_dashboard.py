#!/usr/bin/env python3
"""
Admin Dashboard Launcher for Data Vault Obsidian
Launches the enterprise monitoring and analytics dashboard
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Launch the admin dashboard"""
    print("🚀 Launching Data Vault Obsidian Admin Dashboard...")
    print("=" * 60)
    print("📊 Enterprise monitoring and analytics dashboard")
    print("🌐 Dashboard will be available at: http://localhost:8000")
    print("📈 API endpoints available at: http://localhost:8000/api/")
    print("=" * 60)
    print("Press Ctrl+C to stop the dashboard")
    print()
    
    try:
        # Start the admin dashboard
        uvicorn.run(
            "src.admin.api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Admin dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting admin dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
