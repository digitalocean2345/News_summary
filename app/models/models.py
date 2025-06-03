from sqlalchemy import Column, Integer, String, Date, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)  # Allow duplicate titles
    title_english = Column(Text, nullable=True)  # Store English translation
    source_url = Column(Text, nullable=False, unique=True)  # Make URLs unique
    source_section = Column(String(255))  # Add this new field
    collection_date = Column(Date, nullable=False)
    
    # Content fields for enhanced functionality
    full_content = Column(Text, nullable=True)  # Store scraped article content (original language)
    full_content_english = Column(Text, nullable=True)  # Store translated content for Chinese articles
    summary = Column(Text, nullable=True)  # Store LLM-generated summary
    summary_english = Column(Text, nullable=True)  # Store English summary (if generated from Chinese content)
    
    # Language and source tracking
    content_language = Column(String(5), nullable=True)  # 'zh', 'en', etc.
    source_domain = Column(String(100), nullable=True)  # e.g., 'people.com.cn'
    
    # Status tracking
    is_content_scraped = Column(Boolean, default=False, nullable=False)  # Track if content has been fetched
    is_content_translated = Column(Boolean, default=False, nullable=False)  # Track if content has been translated
    is_summarized = Column(Boolean, default=False, nullable=False)  # Track if summary has been generated
    
    # Timestamp tracking
    content_scraped_at = Column(DateTime, nullable=True)  # When content was scraped
    content_translated_at = Column(DateTime, nullable=True)  # When content was translated
    summarized_at = Column(DateTime, nullable=True)  # When summary was generated
    
    # Relationship to saved summaries and comments
    saved_summaries = relationship("SavedSummary", back_populates="news")
    comments = relationship("Comment", back_populates="news")

    def __repr__(self):
        return f"<News(title='{self.title}', date='{self.collection_date}')>"


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)  # Optional description for the category
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    color = Column(String(7), nullable=True)  # Hex color code for UI (e.g., #FF5733)
    
    # Relationship to saved summaries and comments
    saved_summaries = relationship("SavedSummary", back_populates="category")
    comments = relationship("Comment", back_populates="category")
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class SavedSummary(Base):
    __tablename__ = "saved_summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    custom_title = Column(String(200), nullable=True)  # User can give custom title to saved summary
    notes = Column(Text, nullable=True)  # User can add personal notes
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)  # User can mark as favorite
    
    # Relationships
    news = relationship("News", back_populates="saved_summaries")
    category = relationship("Category", back_populates="saved_summaries")
    
    def __repr__(self):
        return f"<SavedSummary(news_id={self.news_id}, category_id={self.category_id})>"


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # Optional category tagging
    comment_text = Column(Text, nullable=False)
    user_name = Column(String(100), nullable=True)  # Optional user attribution
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    news = relationship("News", back_populates="comments")
    category = relationship("Category", back_populates="comments")
    
    def __repr__(self):
        return f"<Comment(id={self.id}, news_id={self.news_id}, category_id={self.category_id})>"
