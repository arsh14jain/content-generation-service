from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
import logging
import asyncio
from datetime import datetime

from config import config
from app.database import SessionLocal
from app.models import Topic, Post
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class PostGenerationScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def start(self):
        """Start the scheduler"""
        if not self.is_running:
            # Add the post generation job
            self.scheduler.add_job(
                func=self._generate_posts_for_all_topics,
                trigger=IntervalTrigger(hours=config.POST_GENERATION_INTERVAL_HOURS),
                id='post_generation_job',
                name='Generate educational posts for all topics',
                replace_existing=True,
                next_run_time=datetime.now()  # Run immediately on startup
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info(f"Post generation scheduler started. Will run every {config.POST_GENERATION_INTERVAL_HOURS} hours.")
        else:
            logger.warning("Scheduler is already running")
    
    async def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Post generation scheduler stopped")
        else:
            logger.warning("Scheduler is not running")
    
    async def _generate_posts_for_all_topics(self):
        """Background job to generate posts for all topics"""
        logger.info("Starting scheduled post generation for all topics")
        
        db = SessionLocal()
        try:
            # Get all topics
            topics = db.query(Topic).all()
            
            if not topics:
                logger.info("No topics found for post generation")
                return
            
            total_generated = 0
            
            for topic in topics:
                try:
                    logger.info(f"Generating posts for topic: {topic.topic_name}")
                    
                    # Get existing posts for this topic
                    existing_posts = db.query(Post).filter(Post.topic_id == topic.id).all()
                    
                    # Generate new posts using Gemini API
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
                    
                    if saved_count > 0:
                        db.commit()
                        total_generated += saved_count
                        logger.info(f"Generated and saved {saved_count} posts for topic '{topic.topic_name}'")
                    else:
                        logger.warning(f"No valid posts generated for topic '{topic.topic_name}'")
                
                except Exception as e:
                    logger.error(f"Error generating posts for topic '{topic.topic_name}': {e}")
                    db.rollback()
                    continue
            
            logger.info(f"Scheduled post generation completed. Total posts generated: {total_generated}")
            
        except Exception as e:
            logger.error(f"Error in scheduled post generation: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def trigger_manual_generation(self):
        """Manually trigger post generation (for testing)"""
        logger.info("Manually triggering post generation")
        await self._generate_posts_for_all_topics()
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        job = self.scheduler.get_job('post_generation_job')
        if job:
            return job.next_run_time
        return None
    
    def get_scheduler_status(self):
        """Get scheduler status information"""
        return {
            "running": self.is_running,
            "next_run_time": self.get_next_run_time(),
            "interval_hours": config.POST_GENERATION_INTERVAL_HOURS,
            "posts_per_topic": config.POSTS_PER_TOPIC
        }

# Global scheduler instance
post_scheduler = PostGenerationScheduler()