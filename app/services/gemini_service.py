import logging
import os
from typing import List, Dict, Any
from google import genai
from config import config
from app.models import Post

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        # Set the API key for the Google Gemini client
        os.environ['GEMINI_API_KEY'] = config.GEMINI_API_KEY
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"
    
    async def close(self):
        """Close the client (no-op for Google Gemini client)"""
        pass
    
    def _build_prompt(self, topic_name: str, topic_description: str, past_posts: List[Post]) -> str:
        """Build the prompt for Gemini API"""
        
        base_prompt = """### **Prompt: Educational Content Snippet Creator**

**Role:** You are an educational content creator for a learning platform. Your task is to write engaging, concise, and informative educational snippets. These are not for social media, but for an internal learning environment.

-----

**Task:** Create 10 new, unique educational snippets for the given topic, addressing user preferences and content goals.

-----

**Input Structure:**
The user will provide a topic and examples of liked, disliked, and "dive deep" content.

  - `topic`: Includes the name and a detailed **description** that captures the specific "flavor" of content the user is interested in.
  - `preferences`:
      - `liked_snippets`: Examples of style, tone, and content to be inspired by.
      - `disliked_snippets`: Examples to avoid in style, tone, or content.
      - `dive_deep_topics`: Specific sub-topics requiring more detailed but still concise explanation.

-----

**Rules for Snippet Creation:**

1.  **Length:** Limit each snippet to a maximum of **100 words**. Vary the length of the snippets to avoid a monotonous feel.
2.  **Style & Variety:** Do not make all snippets similar. The snippets should be inspired by the `liked_snippets` and avoid the `disliked_snippets`, but they should not be clones. Randomize the content type (e.g., a surprising fact, a question-and-answer, a simple definition, a practical application) and tone.
3.  **Content Focus:** Give significant importance to the `topic` **description** to capture its unique content "flavor."
4.  **In-depth Topics:** Address the `dive_deep_topics` directly by providing simplified explanations of complex concepts, even if it requires a longer snippet within the word limit.
5.  **Engagement:** Use intriguing questions, surprising facts, or appropriate emojis to capture attention.
6.  **Tone:** Maintain a clear, educational, and non-sensational tone. Avoid overly academic language or rephrasing past examples.
7.  **Avoid:** Sensationalism, misleading information, jargon without simple explanation, or social media-specific elements like hashtags.

-----

**Output Format:**
Present the 10 snippets as a numbered list.

-----"""
        
        topic_section = f"""
topic:
    name: "{topic_name}"
    description: "{topic_description or 'Educational content focused on practical understanding and real-world applications.'}"
preferences:"""
        
        if not past_posts:
            topic_section += """
    liked_snippets: []
    disliked_snippets: []
    dive_deep_topics: []
    (No past snippets available - create diverse, engaging educational content)"""
        else:
            # Categorize posts by feedback type
            liked_posts = [post for post in past_posts if post.like_status]
            disliked_posts = [post for post in past_posts if post.dislike_status]
            dive_deep_posts = [post for post in past_posts if post.deep_dive]
            
            topic_section += "\n    liked_snippets:"
            if liked_posts:
                for post in liked_posts:
                    topic_section += f'\n        - "{post.post_content}"'
            else:
                topic_section += "\n        []"
            
            topic_section += "\n    disliked_snippets:"
            if disliked_posts:
                for post in disliked_posts:
                    topic_section += f'\n        - "{post.post_content}"'
            else:
                topic_section += "\n        []"
            
            topic_section += "\n    dive_deep_topics:"
            if dive_deep_posts:
                for post in dive_deep_posts:
                    topic_section += f'\n        - "{post.post_content}"'
            else:
                topic_section += "\n        []"
        
        return base_prompt + topic_section
    
    async def generate_posts(self, topic_name: str, topic_description: str, past_posts: List[Post]) -> List[str]:
        """Generate educational posts using Gemini API"""
        try:
            prompt = self._build_prompt(topic_name, topic_description, past_posts)
            
            logger.info(f"Generating posts for topic: {topic_name}")
            logger.info("=" * 80)
            logger.info("GEMINI API PROMPT:")
            logger.info("=" * 80)
            logger.info(prompt)
            logger.info("=" * 80)
            
            # Use the Google Gemini client
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if not response.text:
                logger.error("No content generated by Gemini API")
                return []
            
            content = response.text
            logger.info("=" * 80)
            logger.info("GEMINI API RESPONSE:")
            logger.info("=" * 80)
            logger.info(content)
            logger.info("=" * 80)
            
            posts = self._parse_posts_from_response(content)
            
            logger.info(f"Generated {len(posts)} posts for topic: {topic_name}")
            return posts
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return []
    
    def _parse_posts_from_response(self, content: str) -> List[str]:
        """Parse individual posts from Gemini's response"""
        posts = []
        lines = content.strip().split('\n')
        
        # Look for numbered list items
        current_post = ""
        for line in lines:
            line = line.strip()
            
            # Check if this is the start of a new numbered item
            if line and line[0].isdigit() and ('.' in line or ')' in line):
                # Save previous post if it exists
                if current_post:
                    # Count words (rough approximation for 100-word limit)
                    word_count = len(current_post.split())
                    if word_count <= 120 and len(current_post.strip()) > 20:  # Allow some buffer
                        posts.append(current_post.strip())
                
                # Start new post by removing numbering
                import re
                clean_line = re.sub(r'^\d+[.)]\s*', '', line)
                current_post = clean_line
            elif current_post and line:
                # Continue building current post
                current_post += " " + line
            elif line and not current_post:
                # Handle cases where numbering might be different
                if line.startswith(('•', '-', '*')):
                    clean_line = re.sub(r'^[•\-*]\s*', '', line)
                    current_post = clean_line
        
        # Don't forget the last post
        if current_post:
            word_count = len(current_post.split())
            if word_count <= 120 and len(current_post.strip()) > 20:
                posts.append(current_post.strip())
        
        # Fallback: if no numbered items found, try to split by double newlines or sentences
        if not posts:
            paragraphs = content.split('\n\n')
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                word_count = len(paragraph.split())
                if paragraph and word_count <= 120 and word_count >= 5:
                    posts.append(paragraph)
        
        return posts[:config.POSTS_PER_TOPIC]  # Limit to configured number

gemini_service = GeminiService()