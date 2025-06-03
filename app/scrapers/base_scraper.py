from abc import ABC, abstractmethod
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import chardet

class BaseScraper(ABC):
    def __init__(self):
        self.session = None

    async def init_session(self):
        if not self.session:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            self.session = aiohttp.ClientSession(
                connector=connector, 
                timeout=timeout, 
                headers=headers
            )

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_page(self, url: str) -> str:
        """Fetch page content with proper Chinese encoding handling"""
        await self.init_session()
        try:
            async with self.session.get(url) as response:
                # Get the raw bytes first
                content_bytes = await response.read()
                
                # Try to get encoding from response headers
                encoding = None
                content_type = response.headers.get('content-type', '').lower()
                
                if 'charset=' in content_type:
                    encoding = content_type.split('charset=')[-1].strip()
                    # Normalize encoding names
                    if encoding.lower() in ['gb2312', 'gbk']:
                        encoding = 'gb2312'
                    elif encoding.lower() in ['utf-8', 'utf8']:
                        encoding = 'utf-8'
                
                # If no encoding found in headers, try to detect it
                if not encoding:
                    detected = chardet.detect(content_bytes)
                    if detected and detected['confidence'] > 0.7:
                        encoding = detected['encoding']
                
                # Fallback encodings for Chinese sites
                if not encoding:
                    # Try common Chinese encodings
                    for fallback_encoding in ['utf-8', 'gb2312', 'gbk', 'big5']:
                        try:
                            return content_bytes.decode(fallback_encoding)
                        except UnicodeDecodeError:
                            continue
                    
                    # If all else fails, use utf-8 with error handling
                    return content_bytes.decode('utf-8', errors='ignore')
                
                try:
                    return content_bytes.decode(encoding)
                except (UnicodeDecodeError, LookupError):
                    # If specified encoding fails, try utf-8 with error handling
                    return content_bytes.decode('utf-8', errors='ignore')
                    
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""

    @abstractmethod
    async def get_news(self) -> List[Dict]:
        """Get news articles from the source"""
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of the news source"""
        pass
