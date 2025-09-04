# Unified Documentation Scraper System

Comprehensive web scraping system that combines all tools (Motia, Flyde, ChartDB, JSON Crack) with advanced pagination, MCP integration, and performance optimization.

## 🎯 Overview

This unified scraper system provides complete documentation coverage for:
- **Motia**: Unified backend framework
- **Flyde**: Visual flow-based programming
- **ChartDB**: Database diagram visualization
- **JSON Crack**: Data format visualization

## 🚀 Features

### Unified Scraping Capabilities
- **Multi-Tool Support**: Single system for all documentation
- **Comprehensive Pagination**: Full coverage of all documentation
- **Advanced Custom Features**: AI processing, semantic search
- **Performance Optimization**: Concurrent processing, caching
- **MCP Integration**: Real-time processing and monitoring

### Tool-Specific Features
- **Motia**: API docs, workflow examples, backend patterns
- **Flyde**: Visual flows, node documentation, examples
- **ChartDB**: Database diagrams, templates, schemas
- **JSON Crack**: Visualizations, data formats, code generation

### Advanced Features
- **AI Processing**: Content enhancement and categorization
- **Semantic Search**: Intelligent content discovery
- **Relationship Mapping**: Cross-tool connections
- **Auto-Categorization**: Smart content organization
- **Performance Monitoring**: Real-time metrics and analytics

## 📁 Project Structure

```
unified-docs-scraper/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config/
│   ├── settings.py             # Unified configuration
│   ├── motia_config.py         # Motia-specific settings
│   ├── flyde_config.py         # Flyde-specific settings
│   ├── chartdb_config.py       # ChartDB-specific settings
│   └── jsoncrack_config.py     # JSON Crack-specific settings
├── mcp_servers/
│   ├── unified_mcp_server.py   # Unified MCP server
│   ├── motia_mcp_server.py     # Motia MCP server
│   ├── flyde_mcp_server.py     # Flyde MCP server
│   ├── chartdb_mcp_server.py   # ChartDB MCP server
│   ├── jsoncrack_mcp_server.py # JSON Crack MCP server
│   └── context7_mcp_server.py  # Context7 integration
├── scrapers/
│   ├── base_scraper.py         # Base scraper class
│   ├── unified_scraper.py      # Unified scraper orchestrator
│   ├── motia_scraper.py        # Motia scraper
│   ├── flyde_scraper.py        # Flyde scraper
│   ├── chartdb_scraper.py      # ChartDB scraper
│   ├── jsoncrack_scraper.py    # JSON Crack scraper
│   ├── playwright_scraper.py   # Playwright implementation
│   └── scrapfly_scraper.py     # Scrapfly implementation
├── flows/
│   ├── unified_flow.flyde      # Unified scraping flow
│   ├── motia_flow.flyde        # Motia-specific flow
│   ├── flyde_flow.flyde        # Flyde-specific flow
│   ├── chartdb_flow.flyde      # ChartDB-specific flow
│   └── jsoncrack_flow.flyde    # JSON Crack-specific flow
├── web_ui/
│   ├── main.py                 # FastAPI web interface
│   ├── templates/              # HTML templates
│   └── static/                 # CSS/JS assets
├── data/                       # Scraped data storage
│   ├── motia/                  # Motia documentation
│   ├── flyde/                  # Flyde documentation
│   ├── chartdb/                # ChartDB documentation
│   ├── jsoncrack/              # JSON Crack documentation
│   └── unified/                # Unified processed data
├── scripts/
│   ├── launch_unified.ps1      # PowerShell launcher
│   ├── launch_motia.ps1        # Motia launcher
│   ├── launch_flyde.ps1        # Flyde launcher
│   ├── launch_chartdb.ps1      # ChartDB launcher
│   └── launch_jsoncrack.ps1    # JSON Crack launcher
└── tests/
    ├── test_unified_scraper.py # Unified scraper tests
    ├── test_motia_scraper.py   # Motia scraper tests
    ├── test_flyde_scraper.py   # Flyde scraper tests
    ├── test_chartdb_scraper.py # ChartDB scraper tests
    └── test_jsoncrack_scraper.py # JSON Crack scraper tests
```

## 🛠 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+ (for Flyde flows)
- PowerShell 7+ (for Windows)
- Redis (for caching)
- PostgreSQL/Yugabyte (for data storage)

### Quick Setup
```powershell
# Navigate to project directory
cd tool-box\unified-docs-scraper

# Run unified setup script
.\scripts\launch_unified.ps1 -Setup

# Or setup individual tools
.\scripts\launch_motia.ps1 -Setup
.\scripts\launch_flyde.ps1 -Setup
.\scripts\launch_chartdb.ps1 -Setup
.\scripts\launch_jsoncrack.ps1 -Setup
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Run the unified scraper
python main.py
```

## 🎮 Usage

### Unified Scraping
```bash
# Scrape all tools
python main.py --unified --all-tools

# Scrape specific tools
python main.py --tools motia,flyde

# Advanced unified scraping
python main.py --unified --all-tools --ai-processing --semantic-search
```

### Individual Tool Scraping
```bash
# Motia only
python main.py --tool motia --crawl-all

# Flyde only
python main.py --tool flyde --extract-flows

# ChartDB only
python main.py --tool chartdb --extract-diagrams

# JSON Crack only
python main.py --tool jsoncrack --extract-visualizations
```

### Web Interface
```bash
# Start unified web UI
python web_ui/main.py

# Access at http://localhost:8000
```

### Flyde Visual Flows
```bash
# Run unified flow
node flows/run_unified_flow.js

# Run individual tool flows
node flows/run_motia_flow.js
node flows/run_flyde_flow.js
node flows/run_chartdb_flow.js
node flows/run_jsoncrack_flow.js
```

## 🔧 Configuration

### Unified Settings
Edit `config/settings.py` for global configuration:
- Database connections
- MCP server settings
- Performance parameters
- AI processing options

### Tool-Specific Settings
Each tool has its own configuration file:
- `config/motia_config.py`: Motia-specific settings
- `config/flyde_config.py`: Flyde-specific settings
- `config/chartdb_config.py`: ChartDB-specific settings
- `config/jsoncrack_config.py`: JSON Crack-specific settings

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/unified_docs
REDIS_URL=redis://localhost:6379

# MCP Servers
MOTIA_MCP_PORT=8001
FLYDE_MCP_PORT=8002
CHARTDB_MCP_PORT=8003
JSONCRACK_MCP_PORT=8004
CONTEXT7_MCP_PORT=8005

# AI Processing
OPENAI_API_KEY=your_api_key
CONTEXT7_API_KEY=your_api_key

# Performance
MAX_CONCURRENT_REQUESTS=50
REQUEST_DELAY=0.3
TIMEOUT=30
```

## 📊 Target URLs

### Motia URLs
- https://www.motia.dev/
- https://www.motia.dev/docs
- https://www.motia.dev/manifesto
- https://github.com/MotiaDev/motia

### Flyde URLs
- https://flyde.dev/
- https://flyde.dev/docs
- https://flyde.dev/playground
- https://github.com/flydelabs/flyde

### ChartDB URLs
- https://chartdb.io/
- https://docs.chartdb.io/
- https://api.chartdb.io/
- https://github.com/chartdb/chartdb

### JSON Crack URLs
- https://jsoncrack.com/
- https://jsoncrack.com/editor
- https://github.com/AykutSarac/jsoncrack.com

## 🎨 Flyde Visual Flows

### Unified Flow
Complete scraping workflow for all tools:
1. **Initialization**: Setup and configuration
2. **Tool Discovery**: Identify available tools
3. **Parallel Scraping**: Scrape all tools concurrently
4. **Data Processing**: Process and enhance data
5. **Storage**: Save to unified database
6. **Visualization**: Display unified results

### Individual Tool Flows
Specialized flows for each tool:
- **Motia Flow**: Backend framework documentation
- **Flyde Flow**: Visual programming documentation
- **ChartDB Flow**: Database visualization documentation
- **JSON Crack Flow**: Data visualization documentation

## 🔍 MCP Integration

### Unified MCP Server
- **scrape_all_tools**: Scrape all tools
- **scrape_tool**: Scrape specific tool
- **get_scraping_status**: Get current status
- **get_tool_metrics**: Get tool-specific metrics
- **process_unified_data**: Process unified data

### Tool-Specific MCP Servers
Each tool has its own MCP server with specialized functions:
- **Motia MCP**: Backend framework functions
- **Flyde MCP**: Visual flow functions
- **ChartDB MCP**: Database diagram functions
- **JSON Crack MCP**: Data visualization functions

### Context7 Integration
- **Unified Context**: Store all tool contexts
- **Cross-Tool Search**: Search across all tools
- **Relationship Mapping**: Map relationships between tools
- **Knowledge Graph**: Build unified knowledge graph

## 📈 Performance Features

### Optimization
- **Concurrent Processing**: Multi-threaded scraping
- **Intelligent Caching**: Redis-based caching
- **Data Compression**: Efficient storage
- **Rate Limiting**: Respectful scraping
- **Load Balancing**: Distribute load across servers

### Monitoring
- **Real-time Metrics**: Live performance monitoring
- **Tool-Specific Metrics**: Individual tool performance
- **Error Tracking**: Comprehensive error logging
- **Progress Tracking**: Visual progress indicators
- **Resource Usage**: Memory and CPU monitoring

## 🧪 Testing

### Test Suite
```bash
# Run all tests
python -m pytest tests/

# Run unified tests
python -m pytest tests/test_unified_scraper.py

# Run tool-specific tests
python -m pytest tests/test_motia_scraper.py
python -m pytest tests/test_flyde_scraper.py
python -m pytest tests/test_chartdb_scraper.py
python -m pytest tests/test_jsoncrack_scraper.py

# Run with coverage
python -m pytest --cov=scrapers tests/
```

### Test Scripts
```bash
# Quick functionality test
python scripts/test_unified_scraper.py

# Performance test
python scripts/performance_test.py

# Integration test
python scripts/integration_test.py
```

## 🚀 Deployment

### Local Development
```bash
# Start all services
.\scripts\launch_unified.ps1 -All

# Start specific tool
.\scripts\launch_motia.ps1 -All
.\scripts\launch_flyde.ps1 -All
.\scripts\launch_chartdb.ps1 -All
.\scripts\launch_jsoncrack.ps1 -All
```

### Production Deployment
```bash
# Docker deployment
docker-compose up -d

# Kubernetes deployment
kubectl apply -f k8s/

# Cloud deployment
.\scripts\deploy_cloud.ps1
```

## 📚 Documentation

### Generated Documentation
- **Unified API Reference**: Complete API documentation
- **Tool-Specific Guides**: Individual tool guides
- **Integration Guide**: Cross-tool integration
- **Performance Guide**: Optimization guide
- **Troubleshooting**: Common issues and solutions

### Data Outputs
- **JSON**: Structured data export
- **Markdown**: Human-readable documentation
- **HTML**: Interactive documentation
- **CSV**: Tabular data export
- **Database**: Unified database storage

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

### Code Standards
- **Python**: PEP 8 compliance
- **Type Hints**: Full type annotation
- **Documentation**: Comprehensive docstrings
- **Testing**: 90%+ test coverage

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

### Troubleshooting
- Check logs in `logs/` directory
- Review configuration files
- Run diagnostic script: `python scripts/diagnose.py`

### Getting Help
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: Project Wiki
- **Community**: Discord/Telegram

## 🔄 Updates

### Version History
- **v1.0.0**: Initial release with basic unified scraping
- **v1.1.0**: Added MCP integration
- **v1.2.0**: Added Flyde visual flows
- **v1.3.0**: Added web UI and advanced features
- **v1.4.0**: Added AI processing and semantic search

### Roadmap
- **v1.5.0**: Advanced relationship mapping
- **v1.6.0**: Cloud deployment support
- **v2.0.0**: Multi-tool integration platform
- **v2.1.0**: Advanced AI processing
- **v3.0.0**: Enterprise features

---

**Built with ❤️ for the unified documentation community**