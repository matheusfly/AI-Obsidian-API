#!/usr/bin/env python3
"""
Production Deployment Configuration for Final RAG CLI
Production-ready setup with monitoring, logging, and performance optimization
"""

import asyncio
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import argparse
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from final_comprehensive_rag_cli import FinalComprehensiveRAGCLI

class ProductionRAGCLI:
    """Production-ready RAG CLI with monitoring and optimization"""
    
    def __init__(self, config_file: str = "production_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        # Set up production logging
        self._setup_production_logging()
        
        # Initialize CLI with production settings
        self.cli = FinalComprehensiveRAGCLI(
            vault_path=self.config.get('vault_path', 'D:\\Nomade Milionario')
        )
        
        # Production metrics
        self.metrics = {
            'start_time': time.time(),
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'average_response_time': 0,
            'quality_scores': [],
            'error_log': []
        }
        
        self.logger.info("Production RAG CLI initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load production configuration"""
        default_config = {
            'vault_path': 'D:\\Nomade Milionario',
            'log_level': 'INFO',
            'max_conversation_history': 100,
            'quality_threshold': 0.6,
            'performance_monitoring': True,
            'error_reporting': True,
            'backup_enabled': True,
            'backup_interval': 3600,  # 1 hour
            'max_response_time': 10.0,  # seconds
            'quality_alert_threshold': 0.4
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge with defaults
                default_config.update(config)
            except Exception as e:
                print(f"Warning: Error loading config file: {e}")
                print("Using default configuration")
        
        return default_config
    
    def _setup_production_logging(self):
        """Set up production logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        
        # Create logs directory
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Set up file logging
        log_file = logs_dir / f"rag_cli_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Production logging initialized - Level: {log_level}")
    
    async def start_production_server(self):
        """Start production server with monitoring"""
        print("🚀 Starting Production RAG CLI Server")
        print("=" * 50)
        print(f"Configuration: {self.config_file}")
        print(f"Vault Path: {self.config['vault_path']}")
        print(f"Log Level: {self.config['log_level']}")
        print(f"Quality Threshold: {self.config['quality_threshold']}")
        print()
        
        try:
            # Start monitoring tasks
            if self.config.get('performance_monitoring', True):
                asyncio.create_task(self._monitor_performance())
            
            if self.config.get('backup_enabled', True):
                asyncio.create_task(self._backup_system())
            
            # Start main chat loop
            await self._production_chat_loop()
            
        except KeyboardInterrupt:
            print("\n🛑 Production server shutting down...")
            await self._shutdown_production_server()
        except Exception as e:
            self.logger.error(f"Production server error: {e}")
            print(f"❌ Production server error: {e}")
    
    async def _production_chat_loop(self):
        """Production chat loop with monitoring"""
        print("🤖 Production RAG CLI - Ready for queries")
        print("Commands: 'exit' to quit, 'status' for metrics, 'config' for settings")
        print()
        
        while True:
            try:
                user_input = input("\nQuery: ").strip()
                
                if user_input.lower() == 'exit':
                    print("🛑 Shutting down production server...")
                    break
                elif user_input.lower() == 'status':
                    self._show_production_status()
                    continue
                elif user_input.lower() == 'config':
                    self._show_production_config()
                    continue
                elif not user_input:
                    continue
                
                # Process query with production monitoring
                await self._process_production_query(user_input)
                
            except KeyboardInterrupt:
                print("\n🛑 Production server interrupted")
                break
            except Exception as e:
                self.logger.error(f"Error in production chat loop: {e}")
                self.metrics['failed_queries'] += 1
                self.metrics['error_log'].append({
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e),
                    'query': user_input if 'user_input' in locals() else 'unknown'
                })
                print(f"❌ Error processing query: {e}")
    
    async def _process_production_query(self, query: str):
        """Process query with production monitoring"""
        start_time = time.time()
        self.metrics['total_queries'] += 1
        
        try:
            # Process query
            result = await self.cli.search_command(query)
            
            # Calculate response time
            response_time = time.time() - start_time
            self.metrics['successful_queries'] += 1
            
            # Update metrics
            self._update_production_metrics(result, response_time)
            
            # Check performance thresholds
            self._check_performance_thresholds(response_time, result)
            
            # Log successful query
            self.logger.info(f"Query processed successfully: {query[:50]}... (time: {response_time:.2f}s)")
            
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics['failed_queries'] += 1
            self.metrics['error_log'].append({
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'query': query,
                'response_time': response_time
            })
            
            self.logger.error(f"Query failed: {query[:50]}... - {e}")
            print(f"❌ Query failed: {e}")
    
    def _update_production_metrics(self, result: Dict[str, Any], response_time: float):
        """Update production metrics"""
        # Update average response time
        total_queries = self.metrics['total_queries']
        current_avg = self.metrics['average_response_time']
        self.metrics['average_response_time'] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )
        
        # Update quality scores
        if 'quality_metrics' in result:
            quality_score = result['quality_metrics'].get('overall_score', 0)
            self.metrics['quality_scores'].append(quality_score)
            
            # Keep only last 100 quality scores
            if len(self.metrics['quality_scores']) > 100:
                self.metrics['quality_scores'] = self.metrics['quality_scores'][-100:]
    
    def _check_performance_thresholds(self, response_time: float, result: Dict[str, Any]):
        """Check performance thresholds and alert if needed"""
        # Check response time threshold
        max_response_time = self.config.get('max_response_time', 10.0)
        if response_time > max_response_time:
            self.logger.warning(f"Slow response time: {response_time:.2f}s > {max_response_time}s")
        
        # Check quality threshold
        quality_threshold = self.config.get('quality_threshold', 0.6)
        if 'quality_metrics' in result:
            quality_score = result['quality_metrics'].get('overall_score', 0)
            if quality_score < quality_threshold:
                self.logger.warning(f"Low quality response: {quality_score:.3f} < {quality_threshold}")
        
        # Check quality alert threshold
        quality_alert_threshold = self.config.get('quality_alert_threshold', 0.4)
        if 'quality_metrics' in result:
            quality_score = result['quality_metrics'].get('overall_score', 0)
            if quality_score < quality_alert_threshold:
                self.logger.error(f"CRITICAL: Very low quality response: {quality_score:.3f} < {quality_alert_threshold}")
    
    async def _monitor_performance(self):
        """Monitor system performance"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Calculate current performance metrics
                uptime = time.time() - self.metrics['start_time']
                success_rate = (
                    self.metrics['successful_queries'] / self.metrics['total_queries']
                    if self.metrics['total_queries'] > 0 else 0
                )
                
                avg_quality = (
                    sum(self.metrics['quality_scores']) / len(self.metrics['quality_scores'])
                    if self.metrics['quality_scores'] else 0
                )
                
                # Log performance metrics
                self.logger.info(
                    f"Performance Monitor - Uptime: {uptime:.0f}s, "
                    f"Queries: {self.metrics['total_queries']}, "
                    f"Success Rate: {success_rate:.1%}, "
                    f"Avg Response Time: {self.metrics['average_response_time']:.2f}s, "
                    f"Avg Quality: {avg_quality:.3f}"
                )
                
                # Check for performance issues
                if success_rate < 0.8:
                    self.logger.warning(f"Low success rate: {success_rate:.1%}")
                
                if self.metrics['average_response_time'] > 5.0:
                    self.logger.warning(f"High average response time: {self.metrics['average_response_time']:.2f}s")
                
                if avg_quality < 0.5:
                    self.logger.warning(f"Low average quality: {avg_quality:.3f}")
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
    
    async def _backup_system(self):
        """Backup system data"""
        backup_interval = self.config.get('backup_interval', 3600)  # 1 hour
        
        while True:
            try:
                await asyncio.sleep(backup_interval)
                
                # Create backup directory
                backup_dir = Path('backups')
                backup_dir.mkdir(exist_ok=True)
                
                # Backup conversation history
                if hasattr(self.cli, 'conversation_history'):
                    backup_file = backup_dir / f"conversation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(self.cli.conversation_history, f, indent=2, default=str)
                
                # Backup metrics
                metrics_file = backup_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    json.dump(self.metrics, f, indent=2, default=str)
                
                self.logger.info(f"System backup completed: {backup_file}")
                
            except Exception as e:
                self.logger.error(f"Error in backup system: {e}")
    
    def _show_production_status(self):
        """Show production status"""
        uptime = time.time() - self.metrics['start_time']
        success_rate = (
            self.metrics['successful_queries'] / self.metrics['total_queries']
            if self.metrics['total_queries'] > 0 else 0
        )
        avg_quality = (
            sum(self.metrics['quality_scores']) / len(self.metrics['quality_scores'])
            if self.metrics['quality_scores'] else 0
        )
        
        print("\n📊 Production Status")
        print("-" * 30)
        print(f"Uptime: {uptime:.0f} seconds")
        print(f"Total Queries: {self.metrics['total_queries']}")
        print(f"Successful: {self.metrics['successful_queries']}")
        print(f"Failed: {self.metrics['failed_queries']}")
        print(f"Success Rate: {success_rate:.1%}")
        print(f"Average Response Time: {self.metrics['average_response_time']:.2f}s")
        print(f"Average Quality: {avg_quality:.3f}")
        print(f"Recent Errors: {len(self.metrics['error_log'])}")
    
    def _show_production_config(self):
        """Show production configuration"""
        print("\n⚙️ Production Configuration")
        print("-" * 35)
        for key, value in self.config.items():
            print(f"{key}: {value}")
    
    async def _shutdown_production_server(self):
        """Shutdown production server gracefully"""
        print("🛑 Shutting down production server...")
        
        # Save final metrics
        metrics_file = Path('final_production_metrics.json')
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, default=str)
        
        # Save conversation history
        if hasattr(self.cli, 'conversation_history'):
            self.cli._save_conversation_history()
        
        print("✅ Production server shutdown complete")
        print(f"📁 Final metrics saved to: {metrics_file}")

def main():
    """Main function for production deployment"""
    parser = argparse.ArgumentParser(description='Production RAG CLI Server')
    parser.add_argument('--config', default='production_config.json', help='Configuration file')
    parser.add_argument('--vault', help='Vault path override')
    
    args = parser.parse_args()
    
    # Create production configuration if it doesn't exist
    config_file = Path(args.config)
    if not config_file.exists():
        default_config = {
            'vault_path': args.vault or 'D:\\Nomade Milionario',
            'log_level': 'INFO',
            'max_conversation_history': 100,
            'quality_threshold': 0.6,
            'performance_monitoring': True,
            'error_reporting': True,
            'backup_enabled': True,
            'backup_interval': 3600,
            'max_response_time': 10.0,
            'quality_alert_threshold': 0.4
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"Created default configuration: {config_file}")
    
    # Start production server
    production_cli = ProductionRAGCLI(args.config)
    asyncio.run(production_cli.start_production_server())

if __name__ == "__main__":
    main()
