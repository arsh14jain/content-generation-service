from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# SQLAlchemy Models
class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String(255), nullable=False, unique=True, index=True)
    topic_description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    posts = relationship("Post", back_populates="topic", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"
    
    post_id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    post_content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    like_status = Column(Boolean, default=False)
    dislike_status = Column(Boolean, default=False)
    deep_dive = Column(Boolean, default=False)
    
    topic = relationship("Topic", back_populates="posts")

# Pydantic Models for API
class TopicBase(BaseModel):
    topic_name: str
    topic_description: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class TopicResponse(TopicBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    post_content: str
    like_status: Optional[bool] = False
    dislike_status: Optional[bool] = False
    deep_dive: Optional[bool] = False

class PostCreate(PostBase):
    topic_id: int

class PostUpdate(BaseModel):
    like_status: Optional[bool] = None
    dislike_status: Optional[bool] = None
    deep_dive: Optional[bool] = None

class PostResponse(PostBase):
    post_id: int
    topic_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class PostWithTopic(PostResponse):
    topic: TopicResponse

class TopicWithPosts(TopicResponse):
    posts: List[PostResponse] = []

class PostFeedback(BaseModel):
    like_status: Optional[bool] = None
    dislike_status: Optional[bool] = None
    deep_dive: Optional[bool] = None