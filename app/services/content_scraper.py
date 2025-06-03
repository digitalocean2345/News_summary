"""
Content Scraper Service
Extracts full article content from news URLs using domain-specific selectors
Handles translation for Chinese content
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Tuple
from datetime import datetime
import logging
from urllib.parse import urlparse, urljoin
import urllib.parse

from app.services.scraper_config import get_selector_config, get_language_config
from app.services.translator import MicrosoftTranslator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentScraper:
    """Main content scraper with domain-specific selector support"""
    
    def __init__(self, delay_between_requests: float = 1.0):
        """
        Initialize the content scraper
        
        Args:
            delay_between_requests: Delay between requests to be respectful to servers
        """
        self.delay = delay_between_requests
        self.translator = MicrosoftTranslator()
        self.session = requests.Session()
        
        # Set user agent to appear more like a regular browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_domain_and_subcategory(self, url: str) -> Tuple[str, str]:
        """
        Extract domain and determine subcategory from URL
        
        Args:
            url: The article URL
            
        Returns:
            Tuple of (domain, subcategory)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Determine subcategory from URL path
            path = parsed.path.lower()
            if 'international' in path or 'world' in path:
                subcategory = 'international'
            elif 'politics' in path or 'political' in path:
                subcategory = 'politics'
            elif 'society' in path or 'social' in path:
                subcategory = 'society'
            else:
                subcategory = 'default'
                
            return domain, subcategory
            
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return "unknown", "default"
    
    def fetch_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse the webpage content
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Fetching content from: {url}")
            
            # Add delay to be respectful
            if hasattr(self, '_last_request_time'):
                elapsed = time.time() - self._last_request_time
                if elapsed < self.delay:
                    time.sleep(self.delay - elapsed)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            self._last_request_time = time.time()
            
            # Handle encoding properly for Chinese content
            if not response.encoding or response.encoding == 'ISO-8859-1':
                # Try to detect proper encoding
                detected_encoding = response.apparent_encoding
                if detected_encoding:
                    response.encoding = detected_encoding
                elif 'people.com.cn' in url:
                    # Use GB2312 for People's Daily sites
                    response.encoding = 'gb2312'
                else:
                    response.encoding = 'utf-8'
            
            # Use the properly decoded text instead of raw bytes
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing content from {url}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text content
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common unwanted patterns
        patterns_to_remove = [
            r'责任编辑[：:][^\n]*',  # Chinese editor information
            r'编辑[：:][^\n]*',      # Editor information
            r'来源[：:][^\n]*',      # Source information
            r'原标题[：:][^\n]*',    # Original title
            r'\(责编[：:][^)]*\)',   # Editor in parentheses
            r'点击进入专题',         # Click to enter topic
            r'更多精彩内容',         # More exciting content
            r'相关新闻',            # Related news
            r'【.*?】',             # Content in square brackets
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Clean up extra spaces again
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_content_with_selectors(self, soup: BeautifulSoup, config) -> Dict[str, str]:
        """
        Extract content using domain-specific selectors
        
        Args:
            soup: BeautifulSoup object
            config: SelectorConfig object
            
        Returns:
            Dictionary with extracted content
        """
        result = {
            'content': '',
            'title': '',
            'author': '',
            'date': ''
        }
        
        try:
            # Remove unwanted elements first
            for selector in config.remove_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            # Extract main content
            content_elements = soup.select(config.content_selector)
            if content_elements:
                # Combine text from all matching elements
                content_parts = []
                for element in content_elements:
                    text = element.get_text(separator=' ', strip=True)
                    if text and len(text) > 20:  # Only include substantial text
                        content_parts.append(text)
                
                result['content'] = ' '.join(content_parts)
            
            # Extract title if selector provided
            if config.title_selector:
                title_elements = soup.select(config.title_selector)
                if title_elements:
                    result['title'] = title_elements[0].get_text(strip=True)
            
            # Extract author if selector provided
            if config.author_selector:
                author_elements = soup.select(config.author_selector)
                if author_elements:
                    result['author'] = author_elements[0].get_text(strip=True)
            
            # Extract date if selector provided
            if config.date_selector:
                date_elements = soup.select(config.date_selector)
                if date_elements:
                    result['date'] = date_elements[0].get_text(strip=True)
            
            # Clean all extracted text
            for key in result:
                result[key] = self.clean_text(result[key])
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting content with selectors: {e}")
            return result
    
    def scrape_article_content(self, url: str, content_language: str = 'zh') -> Dict[str, any]:
        """
        Main method to scrape article content from URL
        
        Args:
            url: Article URL
            content_language: Language of the content ('zh' or 'en')
            
        Returns:
            Dictionary with scraped content and metadata
        """
        start_time = time.time()
        
        try:
            # Extract domain and subcategory
            domain, subcategory = self.extract_domain_and_subcategory(url)
            logger.info(f"Scraping {domain} ({subcategory}) - {url}")
            
            # Get appropriate selector configuration
            config = get_selector_config(domain, subcategory)
            
            # Fetch page content
            soup = self.fetch_page_content(url)
            if not soup:
                return {
                    'success': False,
                    'error': 'Failed to fetch page content',
                    'url': url
                }
            
            # Extract content using selectors
            extracted = self.extract_content_with_selectors(soup, config)
            
            if not extracted['content'] or len(extracted['content']) < 100:
                return {
                    'success': False,
                    'error': 'No substantial content found',
                    'url': url,
                    'content_length': len(extracted['content'])
                }
            
            # Prepare result
            result = {
                'success': True,
                'url': url,
                'domain': domain,
                'subcategory': subcategory,
                'content_language': content_language,
                'scraped_at': datetime.utcnow(),
                'scraping_time_seconds': round(time.time() - start_time, 2),
                'content': extracted['content'],
                'content_length': len(extracted['content']),
                'extracted_title': extracted['title'],
                'extracted_author': extracted['author'],
                'extracted_date': extracted['date']
            }
            
            # Handle translation for Chinese content
            if content_language == 'zh':
                lang_config = get_language_config(content_language)
                if lang_config.get('require_translation', False):
                    try:
                        logger.info(f"Translating content to English...")
                        translated_content = self.translator.translate(extracted['content'])
                        
                        result['content_english'] = translated_content
                        result['translation_success'] = True
                        result['translated_at'] = datetime.utcnow()
                        
                        logger.info(f"Translation completed. Original: {len(extracted['content'])} chars, Translated: {len(translated_content)} chars")
                        
                    except Exception as e:
                        logger.error(f"Translation failed: {e}")
                        result['translation_success'] = False
                        result['translation_error'] = str(e)
                        result['content_english'] = None
            
            return result
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()

# Utility function for standalone use
def scrape_single_article(url: str, content_language: str = 'zh') -> Dict[str, any]:
    """
    Scrape a single article (convenience function)
    
    Args:
        url: Article URL
        content_language: Language of content
        
    Returns:
        Scraping result dictionary
    """
    scraper = ContentScraper()
    try:
        return scraper.scrape_article_content(url, content_language)
    finally:
        scraper.close() 