from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from contextlib import asynccontextmanager

from config import config
from app.database import init_db
from app.routes import topics, posts
from app.services.scheduler import post_scheduler
from app.services.gemini_service import gemini_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up educational content service")
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Start the post generation scheduler
        await post_scheduler.start()
        logger.info("Post generation scheduler started")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down educational content service")
        
        try:
            # Stop the scheduler
            await post_scheduler.stop()
            logger.info("Post generation scheduler stopped")
            
            # Close Gemini service
            await gemini_service.close()
            logger.info("Gemini service closed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="Educational Content Generation Service",
    description="A backend service for generating educational content snippets using Gemini API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(topics.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Educational Content Generation Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        scheduler_status = post_scheduler.get_scheduler_status()
        
        return {
            "status": "healthy",
            "timestamp": "2023-01-01T00:00:00Z",  # Will be set by server
            "scheduler": scheduler_status,
            "database": "connected",
            "gemini_api": "configured" if config.GEMINI_API_KEY != "your_gemini_api_key_here" else "not_configured"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.get("/api/v1/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status"""
    return post_scheduler.get_scheduler_status()

@app.post("/api/v1/scheduler/trigger")
async def trigger_scheduler():
    """Manually trigger post generation"""
    try:
        await post_scheduler.trigger_manual_generation()
        return {"message": "Post generation triggered successfully"}
    except Exception as e:
        logger.error(f"Error triggering post generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger post generation")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )