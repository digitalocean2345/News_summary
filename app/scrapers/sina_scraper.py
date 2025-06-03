from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import re

class SinaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://news.sina.com.cn/"
        # Alternative sources for better article discovery
        self.sources = {
            "Sina News Main": "https://news.sina.com.cn/",
            "Sina Domestic": "https://news.sina.com.cn/china/",
            "Sina International": "https://news.sina.com.cn/world/",
            "Sina Finance": "https://finance.sina.com.cn/",
        }

    def get_source_name(self) -> str:
        return "Sina News"

    async def get_news(self) -> List[Dict]:
        articles = []
        
        for source_name, source_url in self.sources.items():
            try:
                print(f"\n=== Fetching from {source_name} ===")
                content = await self.fetch_page(source_url)
                
                if not content:
                    print(f"Failed to fetch content from {source_url}")
                    continue

                soup = BeautifulSoup(content, 'html.parser')
                
                # Multiple selectors to try for different page layouts
                selectors = [
                    'a[href*="/china/"]',    # News links containing '/china/'
                    'a[href*="/world/"]',    # International news
                    'a[href*="/finance/"]',  # Finance news
                    'a[href*="/news/"]',     # General news links
                    '.news-item a',          # Generic news item links
                    '.tit a',                # Title links
                    'h3 a',                  # Header links
                    'h2 a',                  # Header links
                ]
                
                found_links = []
                for selector in selectors:
                    links = soup.select(selector)
                    if links:
                        found_links.extend(links)
                        print(f"Found {len(links)} links with selector: {selector}")
                
                # Remove duplicates by href
                unique_links = {}
                for link in found_links:
                    href = link.get('href', '')
                    if href and href not in unique_links:
                        unique_links[href] = link
                
                print(f"Total unique links found: {len(unique_links)}")
                
                # Process the links
                for href, link in list(unique_links.items())[:15]:  # Limit to 15 articles per source
                    try:
                        title = link.get_text(strip=True)
                        
                        if not title or len(title) < 10:  # Skip if title too short
                            continue
                            
                        # Ensure absolute URL
                        if href.startswith('//'):
                            href = f"https:{href}"
                        elif href.startswith('/'):
                            href = f"https://news.sina.com.cn{href}"
                        elif not href.startswith('http'):
                            continue  # Skip relative URLs we can't resolve
                        
                        print(f"Processing: {title[:50]}...")
                        
                        # Fetch full article content
                        article_content = await self.fetch_page(href)
                        content_text = ""
                        
                        if article_content:
                            article_soup = BeautifulSoup(article_content, 'html.parser')
                            
                            # Try different content selectors for Sina articles
                            content_selectors = [
                                '.article-content',     # Common article content class
                                '.art_content',         # Sina specific content class
                                '.content',             # Generic content class
                                '#article_content',     # ID-based selector
                                '.article_text',        # Article text class
                                'div[class*="content"]',# Any div with 'content' in class
                                '.main-content'         # Main content area
                            ]
                            
                            for selector in content_selectors:
                                content_div = article_soup.select_one(selector)
                                if content_div:
                                    # Remove script and style elements
                                    for element in content_div.select('script, style'):
                                        element.decompose()
                                    
                                    content_text = content_div.get_text(separator=' ', strip=True)
                                    if len(content_text) > 100:  # Only use if substantial content
                                        break
                            
                            # If no content found with selectors, try to extract from paragraphs
                            if len(content_text) < 100:
                                paragraphs = article_soup.find_all('p')
                                if paragraphs:
                                    content_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                        
                        # Clean up the content text
                        if content_text:
                            # Remove excessive whitespace
                            content_text = re.sub(r'\s+', ' ', content_text)
                            content_text = content_text.strip()
                        
                        articles.append({
                            'title': title,
                            'content': content_text,
                            'source_url': href,
                            'category': self._determine_category(href, title),
                            'language': 'zh'
                        })
                        
                    except Exception as e:
                        print(f"Error processing article {href}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error fetching from {source_name}: {str(e)}")
                continue

        print(f"Total articles collected: {len(articles)}")
        return articles
    
    def _determine_category(self, url: str, title: str) -> str:
        """Determine article category based on URL and title"""
        if '/china/' in url or '国内' in title:
            return 'domestic'
        elif '/world/' in url or '国际' in title:
            return 'international'
        elif '/finance/' in url or '财经' in title or '经济' in title:
            return 'finance'
        elif '/tech/' in url or '科技' in title:
            return 'technology'
        elif '/sports/' in url or '体育' in title:
            return 'sports'
        else:
            return 'general'
