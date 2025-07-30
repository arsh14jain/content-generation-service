from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import logging

from app.database import get_db
from app.models import Post, Topic, PostResponse, PostWithTopic, PostFeedback, PostCreate
from app.services.gemini_service import gemini_service
from app.auth import get_api_key_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/", response_model=List[PostWithTopic])
async def get_posts(
    topic_id: Optional[int] = Query(None, description="Filter by topic ID"),
    like_status: Optional[bool] = Query(None, description="Filter by like status"),
    dislike_status: Optional[bool] = Query(None, description="Filter by dislike status"),
    deep_dive: Optional[bool] = Query(None, description="Filter by deep dive status"),
    limit: int = Query(50, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    db: Session = Depends(get_db),
    _: None = get_api_key_dependency()
):
    """Get posts with optional filtering"""
    try:
        query = db.query(Post).options(joinedload(Post.topic))
        
        # Apply filters
        if topic_id is not None:
            query = query.filter(Post.topic_id == topic_id)
        if like_status is not None:
            query = query.filter(Post.like_status == like_status)
        if dislike_status is not None:
            query = query.filter(Post.dislike_status == dislike_status)
        if deep_dive is not None:
            query = query.filter(Post.deep_dive == deep_dive)
        
        # Apply pagination and ordering
        query = query.order_by(Post.timestamp.desc()).offset(offset).limit(limit)
        posts = query.all()
        
        return [
            PostWithTopic(
                post_id=post.post_id,
                topic_id=post.topic_id,
                post_content=post.post_content,
                timestamp=post.timestamp,
                like_status=post.like_status,
                dislike_status=post.dislike_status,
                deep_dive=post.deep_dive,
                topic={
                    "id": post.topic.id,
                    "topic_name": post.topic.topic_name,
                    "topic_description": post.topic.topic_description,
                    "created_at": post.topic.created_at
                }
            )
            for post in posts
        ]
        
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch posts"
        )

@router.get("/{post_id}", response_model=PostWithTopic)
async def get_post(post_id: int, db: Session = Depends(get_db), _: None = get_api_key_dependency()):
    """Get a specific post by ID"""
    try:
        post = db.query(Post).options(joinedload(Post.topic)).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found"
            )
        
        return PostWithTopic(
            post_id=post.post_id,
            topic_id=post.topic_id,
            post_content=post.post_content,
            timestamp=post.timestamp,
            like_status=post.like_status,
            dislike_status=post.dislike_status,
            deep_dive=post.deep_dive,
            topic={
                "id": post.topic.id,
                "topic_name": post.topic.topic_name,
                "topic_description": post.topic.topic_description,
                "created_at": post.topic.created_at
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch post"
        )

@router.put("/{post_id}/feedback", response_model=PostResponse)
async def update_post_feedback(
    post_id: int, 
    feedback: PostFeedback, 
    db: Session = Depends(get_db),
    _: None = get_api_key_dependency()
):
    """Update post feedback (like, dislike, deep dive status)"""
    try:
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found"
            )
        
        # Update feedback fields if provided
        if feedback.like_status is not None:
            post.like_status = feedback.like_status
            # Reset opposing statuses
            if feedback.like_status:
                post.dislike_status = False
        
        if feedback.dislike_status is not None:
            post.dislike_status = feedback.dislike_status
            # Reset opposing statuses
            if feedback.dislike_status:
                post.like_status = False
        
        if feedback.deep_dive is not None:
            post.deep_dive = feedback.deep_dive
        
        db.commit()
        db.refresh(post)
        
        logger.info(f"Updated feedback for post {post_id}")
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating post {post_id} feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post feedback"
        )

@router.post("/generate", response_model=dict)
async def generate_posts_manually(
    topic_id: Optional[int] = Query(None, description="Generate posts for specific topic, or all topics if not provided"),
    db: Session = Depends(get_db),
    _: None = get_api_key_dependency()
):
    """Manually trigger post generation for testing"""
    try:
        if topic_id:
            # Generate for specific topic
            topic = db.query(Topic).filter(Topic.id == topic_id).first()
            if not topic:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Topic with ID {topic_id} not found"
                )
            topics = [topic]
        else:
            # Generate for all topics
            topics = db.query(Topic).all()
        
        if not topics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No topics found to generate posts for"
            )
        
        total_generated = 0
        results = []
        
        for topic in topics:
            try:
                # Get existing posts for this topic
                existing_posts = db.query(Post).filter(Post.topic_id == topic.id).all()
                
                # Generate new posts
                new_post_contents = await gemini_service.generate_posts(
                    topic.topic_name,
                    topic.topic_description or "",
                    existing_posts
                )
                
                # Save new posts to database
                saved_count = 0
                for content in new_post_contents:
                    if content and content.strip():
                        new_post = Post(
                            topic_id=topic.id,
                            post_content=content.strip()
                        )
                        db.add(new_post)
                        saved_count += 1
                
                db.commit()
                total_generated += saved_count
                
                results.append({
                    "topic_id": topic.id,
                    "topic_name": topic.topic_name,
                    "posts_generated": saved_count
                })
                
                logger.info(f"Generated {saved_count} posts for topic '{topic.topic_name}'")
                
            except Exception as e:
                db.rollback()
                logger.error(f"Error generating posts for topic '{topic.topic_name}': {e}")
                results.append({
                    "topic_id": topic.id,
                    "topic_name": topic.topic_name,
                    "posts_generated": 0,
                    "error": str(e)
                })
        
        return {
            "message": f"Post generation completed. Generated {total_generated} posts total.",
            "total_posts_generated": total_generated,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in manual post generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate posts"
        )

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db), _: None = get_api_key_dependency()):
    """Delete a specific post"""
    try:
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with ID {post_id} not found"
            )
        
        db.delete(post)
        db.commit()
        
        logger.info(f"Deleted post {post_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete post"
        )