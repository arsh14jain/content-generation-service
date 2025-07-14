# Educational Content Generation Service

A Python backend service for generating educational content snippets using the Gemini API. This service provides automated content generation for educational platforms with topic management, user feedback, and scheduled content creation.

## Features

- Topic Management: Create and manage educational topics with descriptions
- Automated Content Generation: Scheduled generation of educational snippets using Gemini API
- User Feedback System: Like, dislike, and deep-dive preferences for content personalization
- RESTful API: Complete API for topic and post management
- Background Scheduling: Configurable automated post generation every 6 hours
- Simple Database Setup: SQL schema for easy database initialization

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Gemini API key from Google

## Installation

1. Clone the repository
   ```bash
   git clone https://github.com/arsh14jain/content-generation-service.git
   cd content-generation-service
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL database
   ```bash
   # Create database
   createdb educational_content
   
   # Grant permissions (replace 'username' with your PostgreSQL username)
   psql educational_content -c "GRANT CREATE ON SCHEMA public TO username;"
   psql educational_content -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO username;"
   psql educational_content -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO username;"
   ```

5. Configure environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your actual values:
   # - Set GEMINI_API_KEY to your Gemini API key
   # - Set DATABASE_URL to your PostgreSQL connection string
   ```

6. Set up database tables
   ```bash
   psql educational_content -c "
   CREATE TABLE topics (
       id SERIAL PRIMARY KEY,
       topic_name VARCHAR(255) NOT NULL UNIQUE,
       topic_description TEXT,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   
   CREATE TABLE posts (
       post_id SERIAL PRIMARY KEY,
       topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
       post_content TEXT NOT NULL,
       timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
       like_status BOOLEAN DEFAULT FALSE,
       dislike_status BOOLEAN DEFAULT FALSE,
       deep_dive BOOLEAN DEFAULT FALSE
   );
   
   CREATE INDEX ix_topics_id ON topics(id);
   CREATE INDEX ix_topics_topic_name ON topics(topic_name);
   CREATE INDEX ix_posts_post_id ON posts(post_id);
   "
   ```

## Running the Service

### Development
```bash
python run.py
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The service will be available at `http://localhost:8000`

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Topics
- `POST /api/v1/topics` - Create a new topic
- `GET /api/v1/topics` - List all topics
- `GET /api/v1/topics/{topic_id}` - Get specific topic
- `GET /api/v1/topics/{topic_id}/posts` - Get topic with posts
- `DELETE /api/v1/topics/{topic_id}` - Delete topic

### Posts
- `GET /api/v1/posts` - Get posts with filtering options
- `GET /api/v1/posts/{post_id}` - Get specific post
- `PUT /api/v1/posts/{post_id}/feedback` - Update post feedback
- `POST /api/v1/posts/generate` - Manually trigger post generation
- `DELETE /api/v1/posts/{post_id}` - Delete post

### System
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /api/v1/scheduler/status` - Scheduler status
- `POST /api/v1/scheduler/trigger` - Manually trigger generation

## Configuration

Configure the service via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | Your Gemini API key |
| `DATABASE_URL` | Required | PostgreSQL connection string |
| `POST_GENERATION_INTERVAL_HOURS` | 6 | Hours between automatic generations |
| `POSTS_PER_TOPIC` | 10 | Number of posts to generate per topic |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `DEBUG` | True | Debug mode |
| `LOG_LEVEL` | INFO | Logging level |

## Database Schema

### Topics Table
```sql
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    topic_name VARCHAR(255) NOT NULL UNIQUE,
    topic_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Posts Table
```sql
CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    post_content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    like_status BOOLEAN DEFAULT FALSE,
    dislike_status BOOLEAN DEFAULT FALSE,
    deep_dive BOOLEAN DEFAULT FALSE
);
```

## Usage Examples

### Creating a Topic
```bash
curl -X POST "http://localhost:8000/api/v1/topics" \
     -H "Content-Type: application/json" \
     -d '{"topic_name": "Machine Learning", "topic_description": "Introduction to machine learning concepts"}'
```

### Getting Posts with Filtering
```bash
curl "http://localhost:8000/api/v1/posts?topic_id=1&like_status=true&limit=10"
```

### Updating Post Feedback
```bash
curl -X PUT "http://localhost:8000/api/v1/posts/1/feedback" \
     -H "Content-Type: application/json" \
     -d '{"like_status": true, "deep_dive": false}'
```

### Manual Post Generation
```bash
curl -X POST "http://localhost:8000/api/v1/posts/generate?topic_id=1"
```


## Development

### Project Structure
```
educational_content_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── models.py            # SQLAlchemy models & Pydantic schemas
│   ├── database.py          # Database connection
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── topics.py        # Topic-related endpoints
│   │   └── posts.py         # Post-related endpoints
│   └── services/
│       ├── __init__.py
│       ├── gemini_service.py # Gemini API integration
│       └── scheduler.py     # Background task scheduling
├── config.py                # Configuration settings
├── requirements.txt         # Dependencies
├── run.py                  # Application runner
└── README.md               # This file
```


## License

[Add your license information here]

## Support

[Add support information here]