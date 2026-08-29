#!/usr/bin/env python3
"""
Simple web browser for Freebuff
Fetches and displays web page content
"""

import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def fetch_page(url, max_length=5000):
    """Fetch a web page and return its content"""
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Get links
        links = []
        for link in soup.find_all('a', href=True)[:20]:
            href = link.get('href')
            if href and not href.startswith(('#', 'javascript:')):
                full_url = urljoin(url, href)
                links.append(f"  - {link.get_text(strip=True)[:50]}: {full_url}")
        
        # Get images
        images = []
        for img in soup.find_all('img', src=True)[:10]:
            src = urljoin(url, img.get('src'))
            alt = img.get('alt', 'No alt text')
            images.append(f"  - {alt[:50]}: {src}")
        
        return {
            'url': url,
            'title': soup.title.string if soup.title else 'No title',
            'content': text[:max_length],
            'links': links,
            'images': images,
            'status': response.status_code
        }
        
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'status': 'error'
        }

def display_page(result):
    """Display the fetched page content"""
    print(f"\n{'='*60}")
    print(f"URL: {result['url']}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Title: {result.get('title', 'N/A')}")
    print(f"{'='*60}\n")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    print("CONTENT:")
    print("-" * 40)
    print(result.get('content', 'No content'))
    
    if result.get('links'):
        print(f"\n\nLINKS ({len(result['links'])} shown):")
        print("-" * 40)
        for link in result['links']:
            print(link)
    
    if result.get('images'):
        print(f"\n\nIMAGES ({len(result['images'])} shown):")
        print("-" * 40)
        for img in result['images']:
            print(img)
    
    print(f"\n{'='*60}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python browse.py <url>")
        print("Example: python browse.py https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    result = fetch_page(url)
    display_page(result)
