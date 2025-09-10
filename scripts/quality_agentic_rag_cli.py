#!/usr/bin/env python3
"""
Quality-Enhanced Agentic RAG CLI
Phase 4: Quality Improvement with Evaluation Metrics and User Feedback
"""

import asyncio
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from collections import deque

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from agentic_rag_agent import AgenticRAGAgent
from quality_evaluator import QualityEvaluator

class QualityAgenticRAGCLI:
    """Enhanced RAG CLI with quality evaluation and user feedback"""
    
    def __init__(self, vault_path: str = "D:\\Nomade Milionario"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize core agent
        self.agent = AgenticRAGAgent(vault_path)
        
        # Initialize quality evaluator
        self.quality_evaluator = QualityEvaluator()
        
        # Quality tracking
        self.quality_history = []
        self.user_feedback_history = []
        self.quality_improvements = []
        
        # Interactive mode settings
        self.interactive_mode = True
        self.auto_evaluation = True
        self.feedback_collection = True
        
        self.logger.info("Quality-Enhanced Agentic RAG CLI initialized")
    
    async def process_query_with_quality(self, query: str, user_id: str = "default") -> Dict[str, Any]:
        """Process query with quality evaluation and feedback collection"""
        start_time = time.time()
        
        try:
            # Process query with agent
            agent_result = await self.agent.process_query(query, user_id)
            
            # Extract components for quality evaluation
            response = agent_result['response']
            search_results = agent_result['search_results']
            retrieved_docs = search_results.get('results', [])
            
            # Evaluate response quality
            quality_evaluation = None
            if self.auto_evaluation:
                quality_evaluation = self.quality_evaluator.evaluate_response(
                    query, response, retrieved_docs
                )
                self.quality_history.append(quality_evaluation)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Build enhanced result
            enhanced_result = {
                'query': query,
                'response': response,
                'agent_metrics': agent_result['agent_metrics'],
                'search_results': search_results,
                'quality_evaluation': quality_evaluation,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            
            # Add quality metrics to agent metrics
            if quality_evaluation:
                enhanced_result['agent_metrics']['quality_score'] = quality_evaluation['overall_score']
                enhanced_result['agent_metrics']['quality_level'] = quality_evaluation['quality_level']
            
            return enhanced_result
            
        except Exception as e:
            self.logger.error(f"Quality query processing error: {e}")
            return {
                'query': query,
                'response': f"Desculpe, ocorreu um erro ao processar sua consulta: {str(e)}",
                'error': True,
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    async def interactive_chat(self):
        """Interactive chat mode with quality feedback collection"""
        print("🤖 Quality-Enhanced Agentic RAG CLI")
        print("=" * 50)
        print("Digite 'quit' para sair, 'quality' para ver relatório de qualidade")
        print("Digite 'feedback' para ver feedback do usuário")
        print("Digite 'help' para ver comandos disponíveis")
        print()
        
        user_id = input("Digite seu ID de usuário (ou pressione Enter para 'default'): ").strip()
        if not user_id:
            user_id = "default"
        
        print(f"Bem-vindo, {user_id}! Como posso ajudá-lo hoje?")
        print()
        
        while True:
            try:
                # Get user input
                query = input(f"[{user_id}]> ").strip()
                
                if not query:
                    continue
                
                # Handle special commands
                if query.lower() == 'quit':
                    print("Obrigado por usar o Quality-Enhanced RAG CLI!")
                    break
                elif query.lower() == 'quality':
                    self._show_quality_report()
                    continue
                elif query.lower() == 'feedback':
                    self._show_feedback_summary()
                    continue
                elif query.lower() == 'help':
                    self._show_help()
                    continue
                
                # Process query
                print("🤔 Processando sua consulta...")
                result = await self.process_query_with_quality(query, user_id)
                
                # Display response
                print(f"\n🤖 Resposta:")
                print(f"{result['response']}")
                
                # Display quality metrics if available
                if result.get('quality_evaluation'):
                    quality = result['quality_evaluation']
                    print(f"\n📊 Métricas de Qualidade:")
                    print(f"   Pontuação Geral: {quality['overall_score']:.3f} ({quality['quality_level']})")
                    print(f"   Tempo de Processamento: {result['processing_time']:.3f}s")
                    print(f"   Documentos Utilizados: {quality['retrieved_docs_count']}")
                
                # Collect user feedback
                if self.feedback_collection and not result.get('error'):
                    self._collect_user_feedback(query, result['response'], user_id)
                
                print()
                
            except KeyboardInterrupt:
                print("\n\nSaindo...")
                break
            except Exception as e:
                print(f"Erro: {e}")
                continue
    
    def _collect_user_feedback(self, query: str, response: str, user_id: str):
        """Collect user feedback on response quality"""
        print("\n📝 A resposta foi útil? (👍/👎/😐 ou 'skip' para pular)")
        feedback_input = input("Feedback: ").strip().lower()
        
        if feedback_input == 'skip':
            return
        
        # Map feedback input to feedback type
        feedback_mapping = {
            '👍': 'positive',
            '👎': 'negative',
            '😐': 'neutral',
            'positive': 'positive',
            'negative': 'negative',
            'neutral': 'neutral'
        }
        
        feedback_type = feedback_mapping.get(feedback_input, 'neutral')
        
        # Collect additional notes if negative
        additional_notes = ""
        if feedback_type == 'negative':
            additional_notes = input("O que poderia ser melhorado? (opcional): ").strip()
        
        # Store feedback
        feedback = self.quality_evaluator.collect_user_feedback(
            query, response, feedback_type, additional_notes
        )
        
        self.user_feedback_history.append({
            'user_id': user_id,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"Obrigado pelo feedback! ({feedback_type})")
    
    def _show_quality_report(self):
        """Show quality report"""
        report = self.quality_evaluator.get_quality_report()
        
        print("\n📊 Relatório de Qualidade")
        print("=" * 40)
        print(f"Total de Avaliações: {report['total_evaluations']}")
        print(f"Pontuação Média: {report['avg_quality_score']:.3f}")
        
        if report['quality_distribution']:
            print(f"\nDistribuição de Qualidade:")
            for level, count in report['quality_distribution'].items():
                print(f"  {level.capitalize()}: {count}")
        
        if report['feedback_distribution']:
            print(f"\nDistribuição de Feedback:")
            for feedback_type, count in report['feedback_distribution'].items():
                print(f"  {feedback_type.capitalize()}: {count}")
        
        if report['recommendations']:
            print(f"\nRecomendações:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print()
    
    def _show_feedback_summary(self):
        """Show user feedback summary"""
        if not self.user_feedback_history:
            print("Nenhum feedback coletado ainda.")
            return
        
        print("\n📝 Resumo do Feedback do Usuário")
        print("=" * 40)
        
        # Group by user
        user_feedback = {}
        for item in self.user_feedback_history:
            user_id = item['user_id']
            if user_id not in user_feedback:
                user_feedback[user_id] = []
            user_feedback[user_id].append(item['feedback'])
        
        for user_id, feedbacks in user_feedback.items():
            print(f"\nUsuário: {user_id}")
            feedback_types = [f['feedback_type'] for f in feedbacks]
            feedback_count = len(feedbacks)
            positive_count = feedback_types.count('positive')
            negative_count = feedback_types.count('negative')
            neutral_count = feedback_types.count('neutral')
            
            print(f"  Total de Feedback: {feedback_count}")
            print(f"  Positivo: {positive_count} | Negativo: {negative_count} | Neutro: {neutral_count}")
            
            # Show recent feedback
            recent_feedbacks = feedbacks[-3:]  # Last 3
            for feedback in recent_feedbacks:
                print(f"    {feedback['feedback_type']}: {feedback['query'][:50]}...")
        
        print()
    
    def _show_help(self):
        """Show help information"""
        print("\n❓ Comandos Disponíveis")
        print("=" * 30)
        print("quit     - Sair do programa")
        print("quality  - Ver relatório de qualidade")
        print("feedback - Ver resumo do feedback")
        print("help     - Mostrar esta ajuda")
        print()
        print("Durante o chat:")
        print("  👍 - Feedback positivo")
        print("  👎 - Feedback negativo")
        print("  😐 - Feedback neutro")
        print("  skip   - Pular feedback")
        print()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_status = self.agent.get_agent_status()
        quality_report = self.quality_evaluator.get_quality_report()
        
        return {
            'agent_status': agent_status,
            'quality_metrics': quality_report,
            'interactive_mode': self.interactive_mode,
            'auto_evaluation': self.auto_evaluation,
            'feedback_collection': self.feedback_collection,
            'total_queries_processed': len(self.quality_history),
            'total_feedback_collected': len(self.user_feedback_history)
        }
    
    def export_quality_data(self, filename: str = None) -> str:
        """Export quality data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_data_{timestamp}.json"
        
        data = {
            'quality_history': self.quality_history,
            'user_feedback_history': self.user_feedback_history,
            'quality_analytics': self.quality_evaluator.quality_analytics,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename

# Test the quality-enhanced CLI
async def test_quality_agentic_rag_cli():
    """Test the quality-enhanced agentic RAG CLI"""
    print("🧪 Testing Quality-Enhanced Agentic RAG CLI")
    print("=" * 60)
    
    cli = QualityAgenticRAGCLI()
    
    # Test queries
    test_queries = [
        "What are machine learning algorithms?",
        "How does neural network training work?",
        "What is the philosophy of logic?",
        "Performance optimization techniques"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 40)
        
        # Process query
        result = await cli.process_query_with_quality(query)
        
        print(f"Response: {result['response'][:100]}...")
        print(f"Processing Time: {result['processing_time']:.3f}s")
        
        if result.get('quality_evaluation'):
            quality = result['quality_evaluation']
            print(f"Quality Score: {quality['overall_score']:.3f} ({quality['quality_level']})")
            print(f"Recommendations: {len(quality['recommendations'])}")
        
        # Simulate user feedback
        feedback_type = 'positive' if result.get('quality_evaluation', {}).get('overall_score', 0) > 0.6 else 'negative'
        cli.quality_evaluator.collect_user_feedback(query, result['response'], feedback_type)
    
    # Show quality report
    print(f"\n📊 Quality Report:")
    cli._show_quality_report()
    
    # Show system status
    status = cli.get_system_status()
    print(f"System Status:")
    print(f"  Queries Processed: {status['total_queries_processed']}")
    print(f"  Feedback Collected: {status['total_feedback_collected']}")
    print(f"  Average Quality: {status['quality_metrics']['avg_quality_score']:.3f}")
    
    # Export data
    export_file = cli.export_quality_data()
    print(f"Quality data exported to: {export_file}")

if __name__ == "__main__":
    # Run interactive chat
    cli = QualityAgenticRAGCLI()
    asyncio.run(cli.interactive_chat())
