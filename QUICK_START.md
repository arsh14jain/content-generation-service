# Quick Start Guide: Educational Content Service with Mobile App

This guide will help you get both the FastAPI backend and React Native mobile app running quickly.

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- PostgreSQL 12+ installed
- Expo CLI installed globally: `npm install -g expo-cli`
- Gemini API key from Google

## Step 1: Backend Setup

1. **Create virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Setup PostgreSQL database:**
   ```bash
   createdb educational_content
   psql educational_content -c "GRANT CREATE ON SCHEMA public TO $(whoami);"
   psql educational_content -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $(whoami);"
   psql educational_content -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $(whoami);"
   ```

3. **Create database tables:**
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

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your values:
   # GEMINI_API_KEY=your_actual_gemini_api_key
   # DATABASE_URL=postgresql://username:password@localhost/educational_content
   ```

5. **Start the backend server:**
   ```bash
   python run.py
   ```

The backend will be running at `http://localhost:8000`

## Step 2: Add Some Sample Data

1. **Create a topic:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/topics" \
        -H "Content-Type: application/json" \
        -d '{"topic_name": "Machine Learning", "topic_description": "Introduction to ML concepts"}'
   ```

2. **Generate some posts:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/posts/generate"
   ```

3. **Verify posts were created:**
   ```bash
   curl "http://localhost:8000/api/v1/posts?limit=5"
   ```

## Step 3: Mobile App Setup

1. **Navigate to mobile app directory:**
   ```bash
   cd mobile-app
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

3. **Or manually install dependencies:**
   ```bash
   npm install
   ```

4. **Start the development server:**
   ```bash
   npm start
   ```

5. **Test the app:**
   - **iOS**: Press `i` in terminal or scan QR code with iPhone Camera
   - **Android**: Press `a` in terminal or scan QR code with Expo Go app
   - **Web**: Press `w` in terminal for web version

## Step 4: Using the Mobile App

1. The app will show a dark-themed scrolling feed of educational posts
2. You can like/dislike posts by tapping the heart/thumbs-down icons
3. Pull down to refresh the feed
4. The app will automatically load more posts as you scroll

## API Endpoints

### Backend API (http://localhost:8000/docs)
- `GET /api/v1/posts` - Get all posts
- `PUT /api/v1/posts/{id}/feedback` - Update post feedback
- `POST /api/v1/topics` - Create new topic
- `POST /api/v1/posts/generate` - Generate new posts

### Mobile-Optimized API
- `GET /api/v1/mobile/feed` - Mobile-optimized feed with pagination
- `PUT /api/v1/mobile/posts/{id}/feedback` - Mobile feedback updates
- `GET /api/v1/mobile/stats` - App statistics

## Troubleshooting

### Backend Issues
- Check if PostgreSQL is running: `pg_ctl status`
- Verify database connection in `.env` file
- Check logs in terminal for specific errors

### Mobile App Issues
- **"Network Error"**: Make sure backend is running on port 8000
- **"Connection refused"**: For physical devices, update `BASE_URL` in `src/constants/config.js` to use your computer's IP address instead of `localhost`
- **"Cannot connect to Metro"**: Make sure you're on the same WiFi network

### Common Solutions
1. **Physical device testing**: Replace `localhost` with your computer's IP in `mobile-app/src/constants/config.js`
2. **Firewall issues**: Allow connections to port 8000
3. **Database permissions**: Re-run the GRANT commands from Step 1

## Next Steps

1. **Add more topics**: Use the API or create a simple admin interface
2. **Customize the mobile app**: Modify colors, layouts, or add new features
3. **Deploy to production**: Set up proper database, domain, and mobile app distribution
4. **Add authentication**: Implement user accounts and personalized feeds

## Development Tips

- Use `http://localhost:8000/docs` for interactive API documentation
- Check React Native debugger for mobile app issues
- Use `expo logs` to see device logs
- Database queries can be tested directly in psql

## Support

- Backend logs appear in the terminal where you ran `python run.py`
- Mobile app logs appear in the Expo dev tools
- Use the interactive API docs at `/docs` to test endpoints