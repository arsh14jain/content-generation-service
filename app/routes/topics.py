from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.database import get_db
from app.models import Topic, TopicCreate, TopicResponse, TopicWithPosts
from app.auth import get_api_key_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/topics", tags=["topics"])

@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(topic: TopicCreate, db: Session = Depends(get_db), _: None = get_api_key_dependency()):
    """Create a new topic"""
    try:
        db_topic = Topic(
            topic_name=topic.topic_name,
            topic_description=topic.topic_description
        )
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        
        logger.info(f"Created new topic: {topic.topic_name}")
        return db_topic
        
    except IntegrityError:
        db.rollback()
        logger.warning(f"Attempted to create duplicate topic: {topic.topic_name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Topic '{topic.topic_name}' already exists"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating topic: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create topic"
        )

@router.get("/", response_model=List[TopicResponse])
async def get_topics(db: Session = Depends(get_db), _: None = get_api_key_dependency()):
    """Get all topics"""
    try:
        topics = db.query(Topic).order_by(Topic.created_at.desc()).all()
        return topics
    except Exception as e:
        logger.error(f"Error fetching topics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch topics"
        )

@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(topic_id: int, db: Session = Depends(get_db), _: None = get_api_key_dependency()):
    """Get a specific topic by ID"""
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with ID {topic_id} not found"
            )
        return topic
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching topic {topic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch topic"
        )

@router.get("/{topic_id}/posts", response_model=TopicWithPosts)
async def get_topic_with_posts(
    topic_id: int, 
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: None = get_api_key_dependency()
):
    """Get a topic with its posts"""
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with ID {topic_id} not found"
            )
        
        # Load posts with pagination
        posts_query = db.query(topic.posts).order_by(topic.posts.timestamp.desc())
        if limit:
            posts_query = posts_query.limit(limit)
        if offset:
            posts_query = posts_query.offset(offset)
        
        # Create response with paginated posts
        from app.models import TopicWithPosts, PostResponse
        
        posts = [PostResponse.from_orm(post) for post in topic.posts[offset:offset+limit]]
        
        return TopicWithPosts(
            id=topic.id,
            topic_name=topic.topic_name,
            topic_description=topic.topic_description,
            created_at=topic.created_at,
            posts=posts
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching topic {topic_id} with posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch topic with posts"
        )

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(topic_id: int, db: Session = Depends(get_db), _: None = get_api_key_dependency()):
    """Delete a topic and all its posts"""
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Topic with ID {topic_id} not found"
            )
        
        topic_name = topic.topic_name
        db.delete(topic)
        db.commit()
        
        logger.info(f"Deleted topic: {topic_name}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting topic {topic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete topic"
        )