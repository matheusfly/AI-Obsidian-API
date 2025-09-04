#!/usr/bin/env python3
"""
Simple test script for Flyde Docs Scraper
This version doesn't require complex dependencies
"""

import requests
import json
from datetime import datetime
from pathlib import Path

def simple_scrape(url):
    """Simple web scraping using requests"""
    try:
        print(f"🌐 Scraping: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return {
            'url': url,
            'status_code': response.status_code,
            'content': response.text,
            'headers': dict(response.headers),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def extract_text(html_content):
    """Simple text extraction"""
    import re
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html_content)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters
    text = text.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    
    return text.strip()

def extract_links(html_content, base_url):
    """Simple link extraction"""
    import re
    from urllib.parse import urljoin
    
    links = []
    link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>'
    
    for match in re.finditer(link_pattern, html_content, re.IGNORECASE):
        href = match.group(1)
        
        # Convert relative URLs to absolute
        if href.startswith('/'):
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        elif href.startswith('http'):
            links.append(href)
    
    return list(set(links))  # Remove duplicates

def main():
    """Main function"""
    print("🚀 Flyde Docs Scraper - Simple Test")
    print("Target URL: https://flyde.dev/playground/blog-generator")
    print("")
    
    # Target URL
    target_url = "https://flyde.dev/playground/blog-generator"
    
    # Scrape the URL
    result = simple_scrape(target_url)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"✅ Successfully scraped!")
    print(f"Status Code: {result['status_code']}")
    print(f"Content Length: {len(result['content'])} characters")
    
    # Extract text
    text_content = extract_text(result['content'])
    print(f"Text Length: {len(text_content)} characters")
    
    # Extract links
    links = extract_links(result['content'], target_url)
    print(f"Links Found: {len(links)}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    output_file = data_dir / f"simple_test_{timestamp}.json"
    
    output_data = {
        'metadata': {
            'timestamp': timestamp,
            'url': target_url,
            'status_code': result['status_code']
        },
        'content': {
            'html': result['content'][:1000] + '...' if len(result['content']) > 1000 else result['content'],
            'text': text_content[:500] + '...' if len(text_content) > 500 else text_content,
            'links': links[:10]  # First 10 links
        },
        'statistics': {
            'content_length': len(result['content']),
            'text_length': len(text_content),
            'links_count': len(links)
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_file}")
    print("")
    print("📊 Summary:")
    print(f"  Content Length: {output_data['statistics']['content_length']}")
    print(f"  Text Length: {output_data['statistics']['text_length']}")
    print(f"  Links Found: {output_data['statistics']['links_count']}")
    print("")
    print("🎉 Simple test completed successfully!")

if __name__ == "__main__":
    main()