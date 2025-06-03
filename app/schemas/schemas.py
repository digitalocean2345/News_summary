from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

# News Schemas
class NewsBase(BaseModel):
    title: str
    title_english: Optional[str] = None
    source_url: str
    collection_date: date

class NewsCreate(NewsBase):
    pass

class NewsUpdate(BaseModel):
    full_content: Optional[str] = None
    full_content_english: Optional[str] = None
    summary: Optional[str] = None
    summary_english: Optional[str] = None
    content_language: Optional[str] = None
    source_domain: Optional[str] = None
    is_content_scraped: Optional[bool] = None
    is_content_translated: Optional[bool] = None
    is_summarized: Optional[bool] = None
    content_scraped_at: Optional[datetime] = None
    content_translated_at: Optional[datetime] = None
    summarized_at: Optional[datetime] = None

class News(NewsBase):
    id: int
    full_content: Optional[str] = None
    full_content_english: Optional[str] = None
    summary: Optional[str] = None
    summary_english: Optional[str] = None
    content_language: Optional[str] = None
    source_domain: Optional[str] = None
    is_content_scraped: bool = False
    is_content_translated: bool = False
    is_summarized: bool = False
    content_scraped_at: Optional[datetime] = None
    content_translated_at: Optional[datetime] = None
    summarized_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# SavedSummary Schemas
class SavedSummaryBase(BaseModel):
    news_id: int
    category_id: int
    custom_title: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: bool = False

class SavedSummaryCreate(SavedSummaryBase):
    pass

class SavedSummaryUpdate(BaseModel):
    category_id: Optional[int] = None
    custom_title: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None

class SavedSummary(SavedSummaryBase):
    id: int
    saved_at: datetime

    class Config:
        from_attributes = True

# Response schemas with relationships
class NewsWithSummaries(News):
    saved_summaries: List[SavedSummary] = []

class CategoryWithSummaries(Category):
    saved_summaries: List[SavedSummary] = []

class SavedSummaryWithDetails(SavedSummary):
    news: News
    category: Category

# Content scraping request/response schemas
class ContentScrapeRequest(BaseModel):
    news_id: int

class ContentScrapeResponse(BaseModel):
    success: bool
    message: str
    content_length: Optional[int] = None

# Summary generation request/response schemas
class SummaryGenerateRequest(BaseModel):
    news_id: int
    length: Optional[str] = "medium"  # short, medium, detailed

class SummaryGenerateResponse(BaseModel):
    success: bool
    message: str
    summary: Optional[str] = None
    summary_length: Optional[int] = None

# Legacy schemas for backward compatibility (if needed)
class NewsSourceBase(BaseModel):
    name: str
    url: str
    description: Optional[str] = None

class NewsSourceCreate(NewsSourceBase):
    pass

class NewsSource(NewsSourceBase):
    id: str

    class Config:
        from_attributes = True

# Category Management API Schemas
class SaveSummaryRequest(BaseModel):
    news_id: int
    category_id: int
    custom_title: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: bool = False

class SaveSummaryResponse(BaseModel):
    id: int
    news_id: int
    category_id: int
    custom_title: str
    notes: str
    is_favorite: bool
    saved_at: datetime
    message: str

# Comment Schemas
class CommentBase(BaseModel):
    news_id: int
    comment_text: str
    category_id: Optional[int] = None
    user_name: Optional[str] = None

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    comment_text: Optional[str] = None
    category_id: Optional[int] = None
    user_name: Optional[str] = None

class Comment(CommentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CommentWithDetails(Comment):
    news: News
    category: Optional[Category] = None

# Comment API Request/Response Schemas
class CommentCreateRequest(BaseModel):
    comment_text: str
    category_id: Optional[int] = None
    user_name: Optional[str] = None

class CommentResponse(BaseModel):
    id: int
    news_id: int
    comment_text: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime
    news_title: str
    news_title_english: Optional[str] = None
    news_url: str
