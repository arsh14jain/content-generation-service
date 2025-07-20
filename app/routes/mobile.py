from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging

from app.database import get_db
from app.models import Post, Topic, PostResponse, PostWithTopic, PostFeedback
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile", tags=["mobile"])

class MobilePostResponse(BaseModel):
    """Optimized post response for mobile clients"""
    post_id: int
    post_content: str
    timestamp: str
    like_status: bool
    dislike_status: bool
    topic: dict
    
    class Config:
        from_attributes = True

class MobileFeedResponse(BaseModel):
    """Feed response with metadata for mobile clients"""
    posts: List[MobilePostResponse]
    total_count: int
    has_more: bool
    next_offset: Optional[int] = None

@router.get("/feed", response_model=MobileFeedResponse)
async def get_mobile_feed(
    limit: int = Query(20, ge=1, le=50, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    db: Session = Depends(get_db)
):
    """Get optimized feed for mobile clients with metadata"""
    try:
        # Build query
        query = db.query(Post).options(joinedload(Post.topic))
        
        if topic_id is not None:
            query = query.filter(Post.topic_id == topic_id)
        
        # Get total count for pagination metadata
        total_count = query.count()
        
        # Apply pagination and ordering
        posts = query.order_by(Post.timestamp.desc()).offset(offset).limit(limit).all()
        
        # Transform to mobile response format
        mobile_posts = []
        for post in posts:
            mobile_posts.append(MobilePostResponse(
                post_id=post.post_id,
                post_content=post.post_content,
                timestamp=post.timestamp.isoformat(),
                like_status=post.like_status,
                dislike_status=post.dislike_status,
                topic={
                    "id": post.topic.id,
                    "topic_name": post.topic.topic_name
                }
            ))
        
        # Calculate pagination metadata
        has_more = (offset + len(posts)) < total_count
        next_offset = offset + len(posts) if has_more else None
        
        return MobileFeedResponse(
            posts=mobile_posts,
            total_count=total_count,
            has_more=has_more,
            next_offset=next_offset
        )
        
    except Exception as e:
        logger.error(f"Error fetching mobile feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch mobile feed"
        )

@router.put("/posts/{post_id}/feedback", response_model=dict)
async def update_mobile_post_feedback(
    post_id: int,
    feedback: PostFeedback,
    db: Session = Depends(get_db)
):
    """Update post feedback optimized for mobile clients"""
    try:
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found"
            )
        
        # Update feedback fields with mobile-specific logic
        if feedback.like_status is not None:
            post.like_status = feedback.like_status
            # Reset opposing status
            if feedback.like_status:
                post.dislike_status = False
        
        if feedback.dislike_status is not None:
            post.dislike_status = feedback.dislike_status
            # Reset opposing status
            if feedback.dislike_status:
                post.like_status = False
        
        if feedback.deep_dive is not None:
            post.deep_dive = feedback.deep_dive
        
        db.commit()
        db.refresh(post)
        
        # Return simplified response for mobile
        return {
            "success": True,
            "post_id": post.post_id,
            "like_status": post.like_status,
            "dislike_status": post.dislike_status,
            "deep_dive": post.deep_dive,
            "message": "Feedback updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating mobile post feedback {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post feedback"
        )

@router.get("/stats", response_model=dict)
async def get_mobile_stats(db: Session = Depends(get_db)):
    """Get basic statistics for mobile dashboard"""
    try:
        total_posts = db.query(Post).count()
        total_topics = db.query(Topic).count()
        liked_posts = db.query(Post).filter(Post.like_status == True).count()
        disliked_posts = db.query(Post).filter(Post.dislike_status == True).count()
        
        return {
            "total_posts": total_posts,
            "total_topics": total_topics,
            "liked_posts": liked_posts,
            "disliked_posts": disliked_posts,
            "engagement_rate": round((liked_posts + disliked_posts) / total_posts * 100, 1) if total_posts > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching mobile stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )