"""
API endpoints for content scraping functionality
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.models import News
from app.schemas.schemas import (
    ContentScrapeRequest, 
    ContentScrapeResponse,
    News as NewsSchema,
    NewsUpdate
)
from app.services.content_scraper import ContentScraper

router = APIRouter(prefix="/api/content", tags=["content"])

@router.post("/scrape/{news_id}", response_model=ContentScrapeResponse)
async def scrape_news_content(
    news_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Scrape content for a specific news article
    """
    # Get the news item
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News article not found")
    
    # Check if content is already scraped
    if news_item.is_content_scraped and news_item.full_content:
        return ContentScrapeResponse(
            success=True,
            message="Content already scraped",
            content_length=len(news_item.full_content)
        )
    
    try:
        # Initialize scraper
        scraper = ContentScraper()
        
        # Scrape content
        result = scraper.scrape_article_content(
            news_item.source_url, 
            news_item.content_language or 'zh'
        )
        
        if result['success']:
            # Update the news item with scraped content
            news_item.full_content = result['content']
            news_item.is_content_scraped = True
            news_item.content_scraped_at = result['scraped_at']
            
            # Handle translation if available
            if result.get('content_english'):
                news_item.full_content_english = result['content_english']
                news_item.is_content_translated = result.get('translation_success', False)
                news_item.content_translated_at = result.get('translated_at')
            
            db.commit()
            
            return ContentScrapeResponse(
                success=True,
                message=f"Content scraped successfully in {result['scraping_time_seconds']}s",
                content_length=result['content_length']
            )
        else:
            return ContentScrapeResponse(
                success=False,
                message=f"Failed to scrape content: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error scraping content: {str(e)}")
    finally:
        scraper.close()

@router.post("/scrape/batch", response_model=List[ContentScrapeResponse])
async def scrape_multiple_articles(
    news_ids: List[int],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Scrape content for multiple news articles
    """
    if len(news_ids) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 10 articles per batch")
    
    results = []
    scraper = ContentScraper()
    
    try:
        for news_id in news_ids:
            news_item = db.query(News).filter(News.id == news_id).first()
            if not news_item:
                results.append(ContentScrapeResponse(
                    success=False,
                    message=f"News article {news_id} not found"
                ))
                continue
            
            if news_item.is_content_scraped and news_item.full_content:
                results.append(ContentScrapeResponse(
                    success=True,
                    message="Content already scraped",
                    content_length=len(news_item.full_content)
                ))
                continue
            
            try:
                result = scraper.scrape_article_content(
                    news_item.source_url,
                    news_item.content_language or 'zh'
                )
                
                if result['success']:
                    news_item.full_content = result['content']
                    news_item.is_content_scraped = True
                    news_item.content_scraped_at = result['scraped_at']
                    
                    if result.get('content_english'):
                        news_item.full_content_english = result['content_english']
                        news_item.is_content_translated = result.get('translation_success', False)
                        news_item.content_translated_at = result.get('translated_at')
                    
                    results.append(ContentScrapeResponse(
                        success=True,
                        message=f"Content scraped successfully",
                        content_length=result['content_length']
                    ))
                else:
                    results.append(ContentScrapeResponse(
                        success=False,
                        message=f"Failed: {result.get('error', 'Unknown error')}"
                    ))
                    
            except Exception as e:
                results.append(ContentScrapeResponse(
                    success=False,
                    message=f"Error: {str(e)}"
                ))
        
        db.commit()
        return results
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Batch scraping error: {str(e)}")
    finally:
        scraper.close()

@router.get("/status/{news_id}")
async def get_content_status(news_id: int, db: Session = Depends(get_db)):
    """
    Get content scraping status for a news article
    """
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News article not found")
    
    return {
        "news_id": news_id,
        "title": news_item.title,
        "is_content_scraped": news_item.is_content_scraped,
        "is_content_translated": news_item.is_content_translated,
        "content_scraped_at": news_item.content_scraped_at,
        "content_translated_at": news_item.content_translated_at,
        "content_length": len(news_item.full_content) if news_item.full_content else 0,
        "translated_content_length": len(news_item.full_content_english) if news_item.full_content_english else 0,
        "source_domain": news_item.source_domain,
        "content_language": news_item.content_language
    }

@router.get("/preview/{news_id}")
async def preview_scraped_content(
    news_id: int, 
    language: str = "en",  # 'en' for English, 'zh' for Chinese
    max_length: int = 500,
    db: Session = Depends(get_db)
):
    """
    Get a preview of scraped content
    """
    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(status_code=404, detail="News article not found")
    
    if not news_item.is_content_scraped:
        raise HTTPException(status_code=400, detail="Content not scraped yet")
    
    # Choose content based on language preference
    if language == "en" and news_item.full_content_english:
        content = news_item.full_content_english
    elif language == "zh" and news_item.full_content:
        content = news_item.full_content
    elif news_item.full_content:
        content = news_item.full_content  # Fallback to original
    else:
        raise HTTPException(status_code=404, detail="No content available in requested language")
    
    # Create preview
    preview = content[:max_length]
    if len(content) > max_length:
        preview += "..."
    
    return {
        "news_id": news_id,
        "title": news_item.title,
        "language": language,
        "preview": preview,
        "full_length": len(content),
        "is_truncated": len(content) > max_length,
        "scraped_at": news_item.content_scraped_at,
        "translated_at": news_item.content_translated_at if language == "en" else None
    }

@router.get("/stats")
async def get_scraping_stats(db: Session = Depends(get_db)):
    """
    Get overall content scraping statistics
    """
    total_articles = db.query(News).count()
    scraped_articles = db.query(News).filter(News.is_content_scraped == True).count()
    translated_articles = db.query(News).filter(News.is_content_translated == True).count()
    
    # Get stats by domain
    from sqlalchemy import func
    domain_stats = db.query(
        News.source_domain,
        func.count(News.id).label('total'),
        func.sum(News.is_content_scraped).label('scraped'),
        func.sum(News.is_content_translated).label('translated')
    ).group_by(News.source_domain).all()
    
    domain_breakdown = []
    for domain, total, scraped, translated in domain_stats:
        domain_breakdown.append({
            "domain": domain,
            "total_articles": total,
            "scraped_articles": scraped or 0,
            "translated_articles": translated or 0,
            "scraping_percentage": round((scraped or 0) / total * 100, 1) if total > 0 else 0
        })
    
    return {
        "total_articles": total_articles,
        "scraped_articles": scraped_articles,
        "translated_articles": translated_articles,
        "scraping_percentage": round(scraped_articles / total_articles * 100, 1) if total_articles > 0 else 0,
        "translation_percentage": round(translated_articles / total_articles * 100, 1) if total_articles > 0 else 0,
        "domain_breakdown": domain_breakdown
    } 