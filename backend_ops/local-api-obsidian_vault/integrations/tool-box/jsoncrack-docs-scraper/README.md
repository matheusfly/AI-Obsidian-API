# JSON Crack Documentation Scraper

Advanced web scraping system for JSON Crack visualization tool with comprehensive pagination, MCP integration, and advanced features.

## 🎯 Overview

This scraper system extracts comprehensive documentation and features from JSON Crack, including:
- Interactive visualization features
- Data format support (JSON, YAML, CSV, XML, TOML)
- API documentation and examples
- GitHub repository content
- Code generation features
- Export capabilities

## 🚀 Features

### Core Scraping Capabilities
- **Multi-Engine Support**: Scrapfly, Playwright, Scrapy, Requests
- **JavaScript Rendering**: Full SPA support for dynamic content
- **Anti-Detection**: Advanced evasion techniques
- **Rate Limiting**: Intelligent request throttling
- **Error Recovery**: Robust retry mechanisms

### JSON Crack-Specific Features
- **Visualization Extraction**: Interactive graph visualizations
- **Data Format Analysis**: JSON, YAML, CSV, XML, TOML support
- **Code Generation**: TypeScript interfaces, Golang structs, JSON Schemas
- **Export Features**: PNG, JPEG, SVG export capabilities
- **API Integration**: Programmatic access to visualization engine

### MCP Integration
- **Real-time Processing**: Live scraping with MCP servers
- **Context Management**: Context7 integration
- **Performance Monitoring**: Advanced metrics and analytics
- **Distributed Processing**: Multi-server coordination

## 📁 Project Structure

```
jsoncrack-docs-scraper/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config/
│   └── settings.py             # Configuration settings
├── mcp_servers/
│   ├── jsoncrack_mcp_server.py # JSON Crack MCP server
│   └── context7_mcp_server.py  # Context7 integration
├── scrapers/
│   ├── base_scraper.py         # Base scraper class
│   ├── jsoncrack_scraper.py    # JSON Crack-specific scraper
│   ├── playwright_scraper.py   # Playwright implementation
│   └── scrapfly_scraper.py     # Scrapfly implementation
├── flows/
│   ├── jsoncrack_visual_flow.flyde    # Visual scraping flow
│   └── data_processing.flyde          # Data processing flow
├── web_ui/
│   ├── main.py                 # FastAPI web interface
│   ├── templates/              # HTML templates
│   └── static/                 # CSS/JS assets
├── data/                       # Scraped data storage
│   ├── visualizations/         # Extracted visualizations
│   ├── examples/               # Data examples
│   └── documentation/          # Documentation files
└── scripts/
    ├── launch_jsoncrack.ps1    # PowerShell launcher
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
cd tool-box\jsoncrack-docs-scraper

# Run setup script
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

# Run the scraper
python main.py
```

## 🎮 Usage

### Command Line Interface
```bash
# Basic scraping
python main.py --url https://jsoncrack.com/

# Advanced scraping with options
python main.py --url https://jsoncrack.com/ --engine playwright --extract-visualizations --screenshot

# Full documentation crawl
python main.py --crawl-all --output-format json --compress
```

### Web Interface
```bash
# Start web UI
python web_ui/main.py

# Access at http://localhost:8005
```

### Flyde Visual Flows
```bash
# Run visual scraping flow
node flows/run_jsoncrack_flow.js

# Or use PowerShell
.\scripts\launch_jsoncrack.ps1 -Flow
```

## 🔧 Configuration

### Environment Variables
```bash
# Context7 API (optional)
CONTEXT7_API_KEY=your_api_key

# Database connection
DATABASE_URL=postgresql://user:pass@localhost:5432/jsoncrack_docs

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
- **Main Site**: https://jsoncrack.com/
- **Editor**: https://jsoncrack.com/editor
- **GitHub**: https://github.com/AykutSarac/jsoncrack.com
- **Documentation**: https://jsoncrack.com/docs (if available)

### Secondary Targets
- **API Documentation**: https://jsoncrack.com/api
- **Examples**: https://jsoncrack.com/examples
- **Blog**: https://jsoncrack.com/blog (if available)

## 🎨 Flyde Visual Flows

### JSON Crack Visual Flow
Visual representation of the scraping process:
1. **Trigger**: Start scraping process
2. **URL Discovery**: Find all JSON Crack URLs
3. **Content Extraction**: Extract visualizations and examples
4. **Data Processing**: Process and structure data
5. **Storage**: Save to database and files
6. **Visualization**: Display results

### Data Processing Flow
Specialized flow for data processing:
1. **Data Input**: Accept various data formats
2. **Format Detection**: Identify data format type
3. **Visualization**: Generate interactive graphs
4. **Export**: Export in multiple formats
5. **Documentation**: Generate documentation

## 🔍 MCP Integration

### JSON Crack MCP Server
- **scrape_jsoncrack**: Main scraping function
- **extract_visualizations**: Extract interactive graphs
- **process_data_formats**: Process various data formats
- **generate_code**: Generate code from data
- **export_visualizations**: Export in multiple formats

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
python -m pytest tests/test_jsoncrack_scraper.py

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
.\scripts\launch_jsoncrack.ps1 -All

# Start specific service
.\scripts\launch_jsoncrack.ps1 -WebUI
.\scripts\launch_jsoncrack.ps1 -MCP
.\scripts\launch_jsoncrack.ps1 -Scraper
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

**Built with ❤️ for the JSON Crack community**