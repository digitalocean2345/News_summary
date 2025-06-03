"""
Configuration for content scraping selectors
Maps source domains and subcategories to their specific CSS selectors
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class SelectorConfig:
    """Configuration for a specific website's content selectors"""
    content_selector: str  # Main content CSS selector
    title_selector: Optional[str] = None  # Optional title selector (fallback)
    remove_selectors: List[str] = None  # Selectors for elements to remove (ads, etc.)
    date_selector: Optional[str] = None  # Date/time selector
    author_selector: Optional[str] = None  # Author selector
    
    def __post_init__(self):
        if self.remove_selectors is None:
            self.remove_selectors = []

# Configuration mapping for different news sources
SCRAPER_CONFIG: Dict[str, Dict[str, SelectorConfig]] = {
    
    # People's Daily configurations
    "renshi.people.com.cn": {
        "default": SelectorConfig(
            content_selector="div.show_text p",
            title_selector="h1.title, h1",
            remove_selectors=[
                "script", "style", ".ad", ".advertisement", 
                ".related-articles", ".comments", ".social-share"
            ],
            date_selector=".time, .date, .publish-time",
            author_selector=".author, .source"
        )
    },
    
    "fanfu.people.com.cn": {
        "default": SelectorConfig(
            content_selector="div.show_text p",
            title_selector="h1.title, h1",
            remove_selectors=[
                "script", "style", ".ad", ".advertisement",
                ".related-articles", ".comments", ".social-share"
            ],
            date_selector=".time, .date, .publish-time",
            author_selector=".author, .source"
        )
    },
    
    "world.people.com.cn": {
        "default": SelectorConfig(
            content_selector="div.rm_txt_con p",
            title_selector="h1.title, h1",
            remove_selectors=[
                "script", "style", ".ad", ".advertisement", 
                ".related-articles", ".comments", ".social-share"
            ],
            date_selector=".time, .date, .publish-time",
            author_selector=".author, .source"
        ),
        "international": SelectorConfig(
            content_selector="div.rm_txt_con p",
            title_selector="h1.title",
            remove_selectors=[
                "script", "style", ".ad", ".advertisement",
                "div.edit", "div.page_copyright"
            ]
        )
    },
    
    "society.people.com.cn": {
        "default": SelectorConfig(
            content_selector="div.rm_txt_con p",
            title_selector="h1.title, h1",
            remove_selectors=[
                "script", "style", ".ad", ".advertisement",
                ".related-news", ".hot-news"
            ]
        )
    },
    
    "finance.people.com.cn": {
        "default": SelectorConfig(
            content_selector="div.rm_txt_con p",
            title_selector="h1.title, h1",
            remove_selectors=[
                "script", "style", ".ad", ".advertisement",
                ".related-news", ".hot-news"
            ]
        )
    },
    
    "politics.people.com.cn": {
        "default": SelectorConfig(
            content_selector="div.rm_txt_con, div.show_text, div.article_content",
            title_selector="h1.title",
            remove_selectors=["script", "style", ".ad"]
        )
    },
    
    # Xinhua News configurations
    "www.xinhuanet.com": {
        "default": SelectorConfig(
            content_selector="div.article-content, div#detail, span.detail",
            title_selector="h1.title, h1",
            remove_selectors=[
                "script", "style", ".ad", ".advertisement",
                ".share-box", ".related-articles"
            ]
        )
    },
    
    # CCTV configurations  
    "news.cctv.com": {
        "default": SelectorConfig(
            content_selector="div.cnt_bd, div.content_area",
            title_selector="h1.title, h1",
            remove_selectors=[
                "script", "style", ".ad", ".advertisement",
                ".video-player", ".related-video"
            ]
        )
    },
    
    # Fallback configuration for unknown domains
    "default": {
        "default": SelectorConfig(
            content_selector="article, .article, .content, .post-content, .entry-content, main, #main",
            title_selector="h1, .title, .post-title, .entry-title",
            remove_selectors=[
                "script", "style", "nav", "header", "footer", 
                ".sidebar", ".ad", ".advertisement", ".comments",
                ".related", ".share", ".social"
            ]
        )
    }
}

def get_selector_config(domain: str, subcategory: str = "default") -> SelectorConfig:
    """
    Get the appropriate selector configuration for a domain and subcategory
    
    Args:
        domain: The website domain (e.g., 'world.people.com.cn')
        subcategory: The subcategory or section (e.g., 'international', 'politics')
    
    Returns:
        SelectorConfig object with the appropriate selectors
    """
    
    # Try to get domain-specific config first
    if domain in SCRAPER_CONFIG:
        domain_config = SCRAPER_CONFIG[domain]
        
        # Try to get subcategory-specific config
        if subcategory in domain_config:
            return domain_config[subcategory]
        
        # Fall back to default for this domain
        if "default" in domain_config:
            return domain_config["default"]
    
    # Fall back to global default configuration
    return SCRAPER_CONFIG["default"]["default"]

def get_all_configured_domains() -> List[str]:
    """Get list of all configured domains"""
    return [domain for domain in SCRAPER_CONFIG.keys() if domain != "default"]

def add_domain_config(domain: str, config: Dict[str, SelectorConfig]):
    """
    Add or update configuration for a new domain
    
    Args:
        domain: The website domain
        config: Dictionary mapping subcategories to SelectorConfig objects
    """
    SCRAPER_CONFIG[domain] = config

# Language-specific configurations
LANGUAGE_CONFIG = {
    "zh": {
        "require_translation": True,
        "translation_service": "microsoft",  # or "google", "openai"
        "encoding": "utf-8"
    },
    "en": {
        "require_translation": False,
        "encoding": "utf-8"
    }
}

def get_language_config(language: str) -> Dict:
    """Get language-specific configuration"""
    return LANGUAGE_CONFIG.get(language, LANGUAGE_CONFIG["en"]) 