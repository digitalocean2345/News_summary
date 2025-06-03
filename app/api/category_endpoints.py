"""
Category Management API Endpoints
Handles saving articles to personal categories and managing saved summaries
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import News, Category, SavedSummary, Comment
from app.schemas.schemas import SaveSummaryRequest, SaveSummaryResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.post("/save-summary", response_model=SaveSummaryResponse)
async def save_summary_to_category(
    request: SaveSummaryRequest,
    db: Session = Depends(get_db)
):
    """Save an article summary to a personal category"""
    try:
        # Check if article exists and has a summary
        article = db.query(News).filter(News.id == request.news_id).first()
        if not article:
            raise HTTPException(
                status_code=404, 
                detail="Article not found"
            )
        
        if not article.is_summarized:
            raise HTTPException(
                status_code=400,
                detail="Article must be summarized before saving to category"
            )
        
        # Check if category exists
        category = db.query(Category).filter(Category.id == request.category_id).first()
        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )
        
        # Check if already saved to this category
        existing = db.query(SavedSummary).filter(
            SavedSummary.news_id == request.news_id,
            SavedSummary.category_id == request.category_id
        ).first()
        
        if existing:
            # Update existing entry
            existing.custom_title = request.custom_title or article.title
            existing.notes = request.notes or ""
            existing.is_favorite = request.is_favorite
            existing.saved_at = datetime.utcnow()
            saved_summary = existing
        else:
            # Create new entry
            saved_summary = SavedSummary(
                news_id=request.news_id,
                category_id=request.category_id,
                custom_title=request.custom_title or article.title,
                notes=request.notes or "",
                is_favorite=request.is_favorite,
                saved_at=datetime.utcnow()
            )
            db.add(saved_summary)
        
        db.commit()
        db.refresh(saved_summary)
        
        logger.info(f"Article {request.news_id} saved to category {request.category_id}")
        
        return SaveSummaryResponse(
            id=saved_summary.id,
            news_id=saved_summary.news_id,
            category_id=saved_summary.category_id,
            custom_title=saved_summary.custom_title,
            notes=saved_summary.notes,
            is_favorite=saved_summary.is_favorite,
            saved_at=saved_summary.saved_at,
            message="Article successfully saved to category"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving summary to category: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save article to category"
        )

@router.get("/saved-summaries/{category_id}")
async def get_saved_summaries_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get all saved summaries for a specific category"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        saved_summaries = db.query(SavedSummary).filter(
            SavedSummary.category_id == category_id
        ).all()
        
        result = []
        for saved in saved_summaries:
            article = db.query(News).filter(News.id == saved.news_id).first()
            if article:
                result.append({
                    "id": saved.id,
                    "custom_title": saved.custom_title,
                    "notes": saved.notes,
                    "is_favorite": saved.is_favorite,
                    "saved_at": saved.saved_at.isoformat() if saved.saved_at else None,
                    "article": {
                        "id": article.id,
                        "title": article.title,
                        "title_english": article.title_english,
                        "summary": article.summary,
                        "summary_english": article.summary_english,
                        "collection_date": article.collection_date.isoformat() if article.collection_date else None,
                        "source_url": article.source_url
                    }
                })
        
        return {
            "category": {
                "id": category.id,
                "name": category.name,
                "description": category.description
            },
            "saved_summaries": result,
            "total_count": len(result)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting saved summaries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get saved summaries")

@router.delete("/saved-summaries/{summary_id}")
async def remove_saved_summary(
    summary_id: int,
    db: Session = Depends(get_db)
):
    """Remove a saved summary from a category"""
    try:
        saved_summary = db.query(SavedSummary).filter(SavedSummary.id == summary_id).first()
        if not saved_summary:
            raise HTTPException(status_code=404, detail="Saved summary not found")
        
        db.delete(saved_summary)
        db.commit()
        
        logger.info(f"Saved summary {summary_id} removed")
        
        return {"message": "Saved summary removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing saved summary: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to remove saved summary")

@router.get("/stats")
async def get_category_stats(db: Session = Depends(get_db)):
    """Get statistics about categories and saved summaries"""
    try:
        categories = db.query(Category).all()
        total_saved = db.query(SavedSummary).count()
        
        category_stats = []
        for category in categories:
            count = db.query(SavedSummary).filter(SavedSummary.category_id == category.id).count()
            favorites_count = db.query(SavedSummary).filter(
                SavedSummary.category_id == category.id,
                SavedSummary.is_favorite == True
            ).count()
            
            category_stats.append({
                "id": category.id,
                "name": category.name,
                "saved_count": count,
                "favorites_count": favorites_count
            })
        
        return {
            "total_categories": len(categories),
            "total_saved_summaries": total_saved,
            "category_stats": category_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting category stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get category statistics")

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a category and all its associated saved summaries and comments"""
    try:
        # Check if category exists
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Count how many items will be affected
        saved_summaries_count = db.query(SavedSummary).filter(SavedSummary.category_id == category_id).count()
        
        # Import Comment model to count comments
        comments_count = db.query(Comment).filter(Comment.category_id == category_id).count()
        
        # Delete all saved summaries associated with this category
        db.query(SavedSummary).filter(SavedSummary.category_id == category_id).delete()
        
        # Delete all comments associated with this category
        db.query(Comment).filter(Comment.category_id == category_id).delete()
        
        # Delete the category itself
        db.delete(category)
        db.commit()
        
        logger.info(f"Category {category_id} deleted with {saved_summaries_count} saved summaries and {comments_count} comments")
        
        return {
            "message": f"Category '{category.name}' deleted successfully",
            "deleted_saved_summaries": saved_summaries_count,
            "deleted_comments": comments_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete category: {str(e)}") 