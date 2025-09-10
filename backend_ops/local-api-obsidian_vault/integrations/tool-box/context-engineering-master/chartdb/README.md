# ChartDB Documentation Scraper

Advanced web scraping system for ChartDB database visualization tool with MCP integration, performance optimization, and comprehensive documentation extraction.

## 🎯 Overview

This scraper system extracts comprehensive documentation and features from ChartDB, including:
- Database diagram templates
- Interactive visualization features
- Documentation and tutorials
- API references and examples
- GitHub repository content

## 🚀 Features

### Core Scraping Capabilities
- **Multi-Engine Support**: Scrapfly, Playwright, Scrapy, Requests
- **JavaScript Rendering**: Full SPA support for dynamic content
- **Anti-Detection**: Advanced evasion techniques
- **Rate Limiting**: Intelligent request throttling
- **Error Recovery**: Robust retry mechanisms

### ChartDB-Specific Features
- **Diagram Extraction**: Database ERD and schema diagrams
- **Template Collection**: Pre-built diagram templates
- **Feature Analysis**: Interactive visualization capabilities
- **Documentation Mining**: Complete docs coverage
- **Screenshot Capture**: Visual documentation

### MCP Integration
- **Real-time Processing**: Live scraping with MCP servers
- **Context Management**: Context7 integration
- **Performance Monitoring**: Advanced metrics and analytics
- **Distributed Processing**: Multi-server coordination

## 📁 Project Structure

```
chartdb-docs-scraper/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config/
│   └── settings.py             # Configuration settings
├── mcp_servers/
│   ├── chartdb_mcp_server.py   # ChartDB MCP server
│   └── context7_mcp_server.py  # Context7 integration
├── scrapers/
│   ├── base_scraper.py         # Base scraper class
│   ├── chartdb_scraper.py      # ChartDB-specific scraper
│   ├── playwright_scraper.py   # Playwright implementation
│   └── scrapfly_scraper.py     # Scrapfly implementation
├── flows/
│   ├── chartdb_visual_flow.flyde    # Visual scraping flow
│   └── diagram_extraction.flyde     # Diagram extraction flow
├── web_ui/
│   ├── main.py                 # FastAPI web interface
│   ├── templates/              # HTML templates
│   └── static/                 # CSS/JS assets
├── data/                       # Scraped data storage
│   ├── diagrams/               # Extracted diagrams
│   ├── templates/              # Diagram templates
│   └── documentation/          # Documentation files
└── scripts/
    ├── launch_chartdb.ps1      # PowerShell launcher
    └── test_scraper.py         # Test scripts
```

## 🛠 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+ (for Flyde flows)
- PowerShell 7+ (for Windows)

### Quick Setup
```powershell
# Navigate to project directory
cd tool-box\chartdb-docs-scraper

# Run setup script
.\scripts\launch_chartdb.ps1 -Setup
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

# Run the scraper
python main.py
```

## 🎮 Usage

### Command Line Interface
```bash
# Basic scraping
python main.py --url https://chartdb.io/

# Advanced scraping with options
python main.py --url https://chartdb.io/ --engine playwright --extract-diagrams --screenshot

# Full documentation crawl
python main.py --crawl-all --output-format json --compress
```

### Web Interface
```bash
# Start web UI
python web_ui/main.py

# Access at http://localhost:8002
```

### Flyde Visual Flows
```bash
# Run visual scraping flow
node flows/run_chartdb_flow.js

# Or use PowerShell
.\scripts\launch_chartdb.ps1 -Flow
```

## 🔧 Configuration

### Environment Variables
```bash
# Scrapfly API (optional)
SCRAPFLY_API_KEY=your_api_key

# Context7 API (optional)
CONTEXT7_API_KEY=your_api_key

# Database connection
DATABASE_URL=postgresql://user:pass@localhost:5432/chartdb_docs

# Performance settings
MAX_CONCURRENT_REQUESTS=20
REQUEST_DELAY=0.5
TIMEOUT=30
```

### Settings File
Edit `config/settings.py` to customize:
- Target URLs
- Scraping engines
- Output formats
- Performance parameters
- MCP server configurations

## 📊 Target URLs

### Primary Targets
- **Main Site**: https://chartdb.io/
- **Templates**: https://chartdb.io/templates
- **GitHub**: https://github.com/chartdb/chartdb
- **Documentation**: https://chartdb.io/docs (if available)

### Secondary Targets
- **API Documentation**: https://chartdb.io/api
- **Examples**: https://chartdb.io/examples
- **Blog**: https://chartdb.io/blog (if available)

## 🎨 Flyde Visual Flows

### ChartDB Visual Flow
Visual representation of the scraping process:
1. **Trigger**: Start scraping process
2. **URL Discovery**: Find all ChartDB URLs
3. **Content Extraction**: Extract diagrams and templates
4. **Data Processing**: Process and structure data
5. **Storage**: Save to database and files
6. **Visualization**: Display results

### Diagram Extraction Flow
Specialized flow for diagram extraction:
1. **Page Analysis**: Analyze page structure
2. **Diagram Detection**: Find diagram elements
3. **Template Extraction**: Extract diagram templates
4. **Schema Analysis**: Analyze database schemas
5. **Documentation**: Generate documentation

## 🔍 MCP Integration

### ChartDB MCP Server
- **scrape_chartdb**: Main scraping function
- **extract_database_diagrams**: Extract diagrams from content
- **extract_templates**: Extract diagram templates
- **analyze_database_schema**: Analyze database schemas
- **generate_schema_documentation**: Generate documentation

### Context7 Integration
- **Context Management**: Store and retrieve scraping context
- **Knowledge Graph**: Build knowledge relationships
- **Semantic Search**: Find related content
- **Version Control**: Track changes over time

## 📈 Performance Features

### Optimization
- **Concurrent Processing**: Multi-threaded scraping
- **Caching**: Intelligent content caching
- **Compression**: Data compression for storage
- **Rate Limiting**: Respectful scraping practices

### Monitoring
- **Real-time Metrics**: Live performance monitoring
- **Error Tracking**: Comprehensive error logging
- **Progress Tracking**: Visual progress indicators
- **Resource Usage**: Memory and CPU monitoring

## 🧪 Testing

### Test Suite
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_chartdb_scraper.py

# Run with coverage
python -m pytest --cov=scrapers tests/
```

### Test Scripts
```bash
# Quick functionality test
python scripts/test_scraper.py

# Performance test
python scripts/performance_test.py

# Integration test
python scripts/integration_test.py
```

## 🚀 Deployment

### Local Development
```bash
# Start all services
.\scripts\launch_chartdb.ps1 -All

# Start specific service
.\scripts\launch_chartdb.ps1 -WebUI
.\scripts\launch_chartdb.ps1 -MCP
.\scripts\launch_chartdb.ps1 -Scraper
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
- **API Reference**: Complete API documentation
- **User Guide**: Step-by-step usage guide
- **Developer Guide**: Technical implementation details
- **Troubleshooting**: Common issues and solutions

### Data Outputs
- **JSON**: Structured data export
- **Markdown**: Human-readable documentation
- **HTML**: Interactive documentation
- **CSV**: Tabular data export

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
- Review configuration in `config/settings.py`
- Run diagnostic script: `python scripts/diagnose.py`

### Getting Help
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: Project Wiki
- **Community**: Discord/Telegram

## 🔄 Updates

### Version History
- **v1.0.0**: Initial release with basic scraping
- **v1.1.0**: Added MCP integration
- **v1.2.0**: Added Flyde visual flows
- **v1.3.0**: Added web UI and advanced features

### Roadmap
- **v1.4.0**: Advanced AI processing
- **v1.5.0**: Cloud deployment support
- **v2.0.0**: Multi-tool integration platform

---

**Built with ❤️ for the ChartDB community**