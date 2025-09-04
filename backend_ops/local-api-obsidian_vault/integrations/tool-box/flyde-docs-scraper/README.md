# 🚀 Flyde Docs Scraper

A comprehensive web scraping system for Flyde documentation, featuring multiple scraping engines, MCP integration, and a web UI for testing and debugging.

## 🎯 Features

- **Multiple Scraping Engines**: Scrapfly, Playwright, and Scrapy
- **MCP Integration**: Tool calling and data processing
- **Web UI**: Interactive testing and debugging interface
- **Monitoring**: Sentry integration for error tracking
- **Context Management**: Context7 for managing scraped data
- **Rate Limiting**: Respectful scraping with configurable delays
- **Error Handling**: Robust error handling and retry logic
- **Data Processing**: Clean text extraction and metadata parsing

## 🏗️ Architecture

```
flyde-docs-scraper/
├── scrapers/           # Scraping engines
│   ├── base_scraper.py
│   ├── scrapfly_scraper.py
│   ├── playwright_scraper.py
│   └── scrapy_scraper.py
├── mcp_servers/        # MCP server implementations
│   └── scraper_mcp_server.py
├── web_ui/            # FastAPI web interface
│   └── main.py
├── config/            # Configuration files
│   ├── settings.py
│   └── logging.py
├── data/              # Scraped data storage
├── tests/             # Test files
├── main.py            # Main orchestrator
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## 🚀 Quick Start

### 1. Hello World Example

Run the hello world example to test the scraper:

```powershell
.\run_hello_world.ps1
```

This will:
- Set up the Python environment
- Install dependencies
- Run a test scrape of `https://flyde.dev/playground/blog-generator`
- Save results to the `data/` folder

### 2. Web UI

Launch the interactive web UI:

```powershell
.\launch_web_ui.ps1
```

Then open your browser to:
- **Main UI**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your configuration:

```env
# Debug mode
DEBUG=true

# Server configuration
HOST=0.0.0.0
PORT=8000

# Scrapfly Configuration (optional)
SCRAPFLY_API_KEY=your_scrapfly_api_key
SCRAPFLY_ACCOUNT=your_scrapfly_account

# Sentry Configuration (optional)
SENTRY_DSN=your_sentry_dsn
SENTRY_ENVIRONMENT=development

# Scraping Configuration
MAX_CONCURRENT_REQUESTS=10
REQUEST_DELAY=1.0
TIMEOUT=30
MAX_RETRIES=3
REQUESTS_PER_MINUTE=60
```

### Target URLs

The scraper is configured to target:
- **Main Docs**: https://flyde.dev/docs
- **GitHub**: https://github.com/flydelabs/flyde
- **Playground**: https://flyde.dev/playground

## 🛠️ Usage

### Python API

```python
from main import FlydeDocsScraper

# Initialize scraper
scraper = FlydeDocsScraper()

# Run hello world example
result = await scraper.hello_world_example()

# Run comprehensive scraping
result = await scraper.run_comprehensive_scraping()
```

### Web UI API

```bash
# Scrape single URL
curl -X POST "http://localhost:8000/api/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://flyde.dev/docs", "scraper": "scrapfly"}'

# Scrape multiple URLs
curl -X POST "http://localhost:8000/api/scrape-multiple" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://flyde.dev/docs", "https://flyde.dev/playground"], "scraper": "playwright"}'

# Get statistics
curl "http://localhost:8000/api/stats"
```

## 🔍 Scraping Engines

### 1. Scrapfly Scraper
- **Pros**: Anti-scraping protection, high success rate
- **Cons**: Requires API key, rate limits
- **Best for**: Production scraping, complex sites

### 2. Playwright Scraper
- **Pros**: JavaScript rendering, browser automation
- **Cons**: Slower, more resource intensive
- **Best for**: JavaScript-heavy sites, screenshots

### 3. Scrapy Scraper
- **Pros**: Fast, efficient, built-in features
- **Cons**: More complex setup
- **Best for**: Large-scale scraping, custom spiders

## 📊 Monitoring

### Sentry Integration

Enable Sentry for error tracking:

```python
import sentry_sdk
sentry_sdk.init(
    dsn="your_sentry_dsn",
    environment="development"
)
```

### Logging

Structured logging with correlation IDs:

```python
from config.logging import get_logger

logger = get_logger(__name__)
logger.info("Scraping started", url=url, scraper=scraper_name)
```

## 🧪 Testing

Run tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## 📁 Data Output

Scraped data is saved in JSON format:

```json
{
  "metadata": {
    "scraper": "scrapfly",
    "timestamp": "20250109_143022",
    "total_pages": 15,
    "successful_pages": 14,
    "failed_pages": 1
  },
  "results": [
    {
      "url": "https://flyde.dev/docs",
      "title": "Flyde Documentation",
      "description": "Visual programming toolkit",
      "text_content": "Clean extracted text...",
      "html_content": "<html>...</html>",
      "metadata": {
        "keywords": ["visual", "programming"],
        "language": "en"
      },
      "scraping_metadata": {
        "status_code": 200,
        "timestamp": 1704823822.123,
        "headers": {...}
      }
    }
  ]
}
```

## 🔗 Integration

### MCP Server

The scraper includes an MCP server for tool calling:

```python
# Start MCP server
python mcp_servers/scraper_mcp_server.py
```

Available tools:
- `scrape_url`: Scrape single URL
- `scrape_multiple`: Scrape multiple URLs
- `extract_links`: Extract links from HTML
- `extract_text`: Extract clean text
- `get_scraper_stats`: Get statistics

### Context7 Integration

For context management:

```python
# Store scraped data in context
from context7 import ContextManager

context = ContextManager()
context.store("flyde_docs", scraped_data)
```

## 🚨 Error Handling

The scraper includes comprehensive error handling:

- **Rate Limiting**: Automatic delays between requests
- **Retry Logic**: Exponential backoff for failed requests
- **Circuit Breakers**: Prevent cascading failures
- **Error Classification**: Distinguish between transient and permanent errors

## 📈 Performance

### Optimization Tips

1. **Use appropriate scraper**: Scrapfly for production, Playwright for JS-heavy sites
2. **Configure concurrency**: Adjust `MAX_CONCURRENT_REQUESTS` based on target site
3. **Enable caching**: Use Redis for caching frequently accessed data
4. **Monitor resources**: Watch memory usage with Playwright

### Benchmarks

Typical performance (on local machine):
- **Scrapfly**: ~100 requests/minute
- **Playwright**: ~20 requests/minute
- **Scrapy**: ~200 requests/minute

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the inline code comments
- **Community**: Join the Flyde Discord server

---

**Happy Scraping! 🕷️**