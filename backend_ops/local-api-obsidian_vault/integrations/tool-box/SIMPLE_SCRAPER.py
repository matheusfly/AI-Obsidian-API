#!/usr/bin/env python3
"""
Simple Documentation Scraper
Quick working scraper for all tools
"""

import requests
import json
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class SimpleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.results = []
    
    def scrape_url(self, url, tool_name):
        """Scrape a single URL"""
        try:
            print(f"🌐 Scraping {tool_name}: {url}")
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract basic information
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else "No title"
                
                # Extract links
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') or href.startswith('/'):
                        full_url = urljoin(url, href)
                        links.append(full_url)
                
                # Extract text content
                text_content = soup.get_text(strip=True)
                
                result = {
                    'tool': tool_name,
                    'url': url,
                    'title': title_text,
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'text_length': len(text_content),
                    'links_count': len(links),
                    'links': links[:10],  # First 10 links
                    'scraped_at': datetime.now().isoformat()
                }
                
                self.results.append(result)
                print(f"✅ Success: {result['content_length']} bytes, {result['links_count']} links")
                return result
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None
    
    def scrape_all_tools(self):
        """Scrape all tools"""
        print("🚀 Starting comprehensive documentation scraping...")
        
        # Define tool URLs
        tools = {
            'Motia': [
                'https://www.motia.dev/',
                'https://www.motia.dev/docs',
                'https://www.motia.dev/manifesto',
                'https://github.com/MotiaDev/motia'
            ],
            'Flyde': [
                'https://flyde.dev/',
                'https://flyde.dev/docs',
                'https://flyde.dev/playground',
                'https://github.com/flydelabs/flyde'
            ],
            'ChartDB': [
                'https://chartdb.io/',
                'https://docs.chartdb.io/',
                'https://api.chartdb.io/',
                'https://github.com/chartdb/chartdb'
            ],
            'JSON Crack': [
                'https://jsoncrack.com/',
                'https://jsoncrack.com/editor',
                'https://github.com/AykutSarac/jsoncrack.com'
            ]
        }
        
        # Scrape each tool
        for tool_name, urls in tools.items():
            print(f"\n🔧 Scraping {tool_name}...")
            for url in urls:
                self.scrape_url(url, tool_name)
                time.sleep(1)  # Be respectful
        
        print(f"\n🎉 Scraping completed! Total pages: {len(self.results)}")
        return self.results
    
    def save_results(self, filename=None):
        """Save results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraping_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        return filename
    
    def print_summary(self):
        """Print scraping summary"""
        print("\n📊 SCRAPING SUMMARY")
        print("=" * 50)
        
        # Group by tool
        tool_stats = {}
        for result in self.results:
            tool = result['tool']
            if tool not in tool_stats:
                tool_stats[tool] = {
                    'pages': 0,
                    'total_bytes': 0,
                    'total_links': 0
                }
            
            tool_stats[tool]['pages'] += 1
            tool_stats[tool]['total_bytes'] += result['content_length']
            tool_stats[tool]['total_links'] += result['links_count']
        
        # Print stats
        for tool, stats in tool_stats.items():
            print(f"\n{tool}:")
            print(f"  Pages: {stats['pages']}")
            print(f"  Total bytes: {stats['total_bytes']:,}")
            print(f"  Total links: {stats['total_links']}")
        
        print(f"\nOverall:")
        print(f"  Total pages: {len(self.results)}")
        print(f"  Total bytes: {sum(r['content_length'] for r in self.results):,}")
        print(f"  Total links: {sum(r['links_count'] for r in self.results)}")

def main():
    """Main function"""
    print("🚀 Simple Documentation Scraper")
    print("=" * 40)
    
    scraper = SimpleScraper()
    
    # Scrape all tools
    results = scraper.scrape_all_tools()
    
    # Save results
    filename = scraper.save_results()
    
    # Print summary
    scraper.print_summary()
    
    print(f"\n✅ Scraping completed successfully!")
    print(f"📁 Results saved to: {filename}")

if __name__ == "__main__":
    main()