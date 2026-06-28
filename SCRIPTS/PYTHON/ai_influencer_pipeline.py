import os
import openai
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
import datetime
import random
import string
from PIL import Image, ImageDraw, ImageFont  # pip install Pillow
import textwrap
import logging
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Types of content that can be generated."""
    POST = "post"
    CAPTION = "caption"
    BLOG = "blog"
    VIDEO_SCRIPT = "video_script"
    REEL_SCRIPT = "reel_script"
    STORY = "story"
    COMMENT = "comment"


@dataclass
class ContentPiece:
    """Represents a piece of generated content."""
    id: str
    type: ContentType
    content: str
    platform: str
    hashtags: List[str]
    timestamp: str
    metadata: Dict[str, Any]


class AIInfluencerPipeline:
    """
    A comprehensive AI influencer content creation pipeline that generates
    various types of content for social media platforms.
    """
    
    def __init__(self, config_path: str = "./ai_influencer_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        # Initialize OpenAI client
        openai.api_key = self.config.get('openai_api_key', os.getenv('OPENAI_API_KEY'))
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Content templates
        self.post_templates = [
            "Here's an interesting perspective on {topic}: {insight}",
            "Just discovered something fascinating about {topic} - {insight}",
            "Thoughts on {topic}? Here's what I think: {insight}",
            "Breaking down {topic} in simple terms: {insight}",
            "Why {topic} matters in today's world: {insight}"
        ]
        
        self.caption_templates = [
            "{hook}\n\n{value_prop}\n\n{call_to_action}\n\n#{hashtags}",
            "{statement}\n\n{explanation}\n\n{question_for_engagement}\n\n#{hashtags}",
            "{achievement_or_fact}\n\n{process_or_reasoning}\n\n{result_or_impact}\n\n#{hashtags}"
        ]
        
        self.hashtag_sets = {
            'tech': ['ai', 'technology', 'innovation', 'future', 'digital', 'startup', 'coding', 'programming'],
            'business': ['entrepreneurship', 'business', 'leadership', 'growth', 'success', 'productivity', 'marketing'],
            'lifestyle': ['lifestyle', 'motivation', 'inspiration', 'wellness', 'mindfulness', 'personaldevelopment'],
            'creative': ['creativity', 'design', 'art', 'photography', 'contentcreation', 'aigenerated']
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            "openai_api_key": "",
            "model": "gpt-3.5-turbo",
            "image_generation_model": "dall-e-2",  # or "dall-e-3"
            "default_platform": "instagram",
            "content_style": "professional",  # Options: professional, casual, inspirational
            "target_audience": "general",
            "max_tokens": 500,
            "temperature": 0.7,
            "image_size": "1024x1024",
            "output_directory": "./generated_content/"
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
        else:
            config = default_config
            self.save_config(config)
        
        # Create output directory
        Path(config.get('output_directory', './generated_content/')).mkdir(parents=True, exist_ok=True)
        
        return config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def generate_post_content(self, topic: str, style: str = None) -> str:
        """Generate a social media post about a specific topic."""
        style = style or self.config.get('content_style', 'professional')
        
        # Create a prompt for the AI
        prompt = f"""
        Write a compelling social media post about {topic}. The style should be {style}.
        The post should be engaging and informative, approximately 100-150 words.
        Focus on providing value to the reader.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.get('max_tokens', 200),
                temperature=self.config.get('temperature', 0.7)
            )
            
            return response.choices[0].message['content'].strip()
        except Exception as e:
            self.logger.error(f"Error generating post content: {e}")
            return f"Check out this interesting topic: {topic}"
    
    def generate_caption(self, content_summary: str, platform: str = "instagram") -> str:
        """Generate a caption for social media."""
        # Determine hashtags based on content
        hashtags = self.generate_hashtags(content_summary)
        
        # Select template based on platform
        if platform.lower() == "twitter":
            # Twitter has character limits, so shorter captions
            caption = f"{content_summary}\n\n{self.generate_cta()}\n\n#{' #'.join(hashtags[:5])}"  # Limit hashtags on Twitter
        else:
            # Instagram/Facebook allow more hashtags
            caption = f"{content_summary}\n\n{self.generate_cta()}\n\n#{' #'.join(hashtags)}"
        
        return caption
    
    def generate_hashtags(self, content: str) -> List[str]:
        """Generate relevant hashtags based on content."""
        # Simple approach: extract keywords and map to hashtag sets
        content_lower = content.lower()
        
        relevant_tags = []
        for category, tags in self.hashtag_sets.items():
            # Count how many tags from this category appear in content
            count = sum(1 for tag in tags if tag in content_lower)
            if count > 0:
                relevant_tags.extend(tags[:3])  # Add top 3 from relevant categories
        
        # If no relevant tags found, use general tags
        if not relevant_tags:
            relevant_tags = self.hashtag_sets['creative'][:5]
        
        # Add some trending tags
        trending_tags = ['ai', 'aigenerated', 'contentcreator', 'fyp', 'foryou']
        relevant_tags.extend(trending_tags)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in relevant_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        
        return unique_tags[:15]  # Limit to 15 hashtags
    
    def generate_cta(self) -> str:
        """Generate a call-to-action."""
        ctas = [
            "What are your thoughts? Comment below! 👇",
            "Follow for more insights like this!",
            "Share this if you found it valuable!",
            "Tag someone who needs to see this!",
            "Double tap if you agree! ❤️",
            "Save this post for later! 📌"
        ]
        return random.choice(ctas)
    
    def generate_blog_post(self, topic: str, word_count: int = 500) -> str:
        """Generate a blog post on a specific topic."""
        prompt = f"""
        Write a comprehensive blog post about {topic}. The post should be approximately {word_count} words.
        Include an introduction, main points with subheadings, and a conclusion.
        Make it engaging and informative for readers interested in this topic.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.get('max_tokens', 1000),
                temperature=self.config.get('temperature', 0.7)
            )
            
            return response.choices[0].message['content'].strip()
        except Exception as e:
            self.logger.error(f"Error generating blog post: {e}")
            return f"# Blog Post: {topic}\n\nThis is a sample blog post about {topic}."
    
    def generate_video_script(self, topic: str, duration_minutes: int = 2) -> str:
        """Generate a script for a video about the given topic."""
        prompt = f"""
        Write a script for a {duration_minutes}-minute educational video about {topic}.
        The script should include:
        1. An engaging hook for the first 10 seconds
        2. Main content broken into sections
        3. Visual cues for the video
        4. A strong call-to-action at the end
        5. Estimated timing for each section
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config.get('model', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.get('max_tokens', 800),
                temperature=self.config.get('temperature', 0.7)
            )
            
            return response.choices[0].message['content'].strip()
        except Exception as e:
            self.logger.error(f"Error generating video script: {e}")
            return f"Video Script: {topic}\n\nHook: Why {topic} matters\nMain content: Key points about {topic}\nCTA: Subscribe for more"
    
    def generate_image_prompt(self, content_description: str, style: str = "modern") -> str:
        """Generate a prompt for image generation based on content."""
        image_prompt = f"A {style} visual representation of: {content_description}. "
        image_prompt += "Professional, high-quality, engaging, suitable for social media."
        
        return image_prompt
    
    def generate_image(self, prompt: str, filename: str = None) -> str:
        """Generate an image based on a prompt using DALL-E."""
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size=self.config.get('image_size', '1024x1024'),
                response_format="url"
            )
            
            image_url = response['data'][0]['url']
            
            # Download and save the image
            if not filename:
                filename = f"generated_image_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            output_dir = Path(self.config.get('output_directory', './generated_content/'))
            filepath = output_dir / filename
            
            # Download image
            img_data = requests.get(image_url).content
            with open(filepath, 'wb') as handler:
                handler.write(img_data)
            
            self.logger.info(f"Image saved to {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            return ""
    
    def create_visual_content(self, text: str, filename: str = None) -> str:
        """Create a simple visual graphic with text overlay."""
        try:
            # Create a new image with a background color
            width, height = 1080, 1080
            bg_colors = [
                (255, 240, 245),  # Light pink
                (240, 248, 255),  # Alice blue
                (250, 250, 240),  # Ivory
                (245, 245, 245),  # White smoke
                (255, 250, 240)   # Floral white
            ]
            
            bg_color = random.choice(bg_colors)
            img = Image.new('RGB', (width, height), color=bg_color)
            d = ImageDraw.Draw(img)
            
            # Try to use a system font, fallback to default if not available
            try:
                # On Windows
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                try:
                    # On Mac
                    font = ImageFont.truetype("Arial.ttf", 60)
                except:
                    # Use default font
                    font = ImageFont.load_default()
            
            # Wrap text to fit within the image
            wrapped_text = textwrap.fill(text, width=40)  # Adjust width as needed
            
            # Calculate text position (centered)
            bbox = d.textbbox((0, 0), wrapped_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) / 2
            y = (height - text_height) / 2
            
            # Add text to image
            d.text((x, y), wrapped_text, fill=(0, 0, 0), font=font)
            
            # Save image
            if not filename:
                filename = f"visual_content_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            output_dir = Path(self.config.get('output_directory', './generated_content/'))
            filepath = output_dir / filename
            
            img.save(filepath)
            
            self.logger.info(f"Visual content saved to {filepath}")
            return str(filepath)
        except Exception as e:
            self.logger.error(f"Error creating visual content: {e}")
            return ""
    
    def generate_content_piece(self, content_type: ContentType, topic: str, platform: str = "instagram") -> ContentPiece:
        """Generate a complete content piece with all necessary components."""
        content_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        
        if content_type == ContentType.POST:
            content = self.generate_post_content(topic)
        elif content_type == ContentType.CAPTION:
            content = self.generate_caption(topic, platform)
        elif content_type == ContentType.BLOG:
            content = self.generate_blog_post(topic)
        elif content_type == ContentType.VIDEO_SCRIPT:
            content = self.generate_video_script(topic)
        elif content_type == ContentType.REEL_SCRIPT:
            content = self.generate_video_script(topic, duration_minutes=1)  # Shorter for reels
        else:
            content = f"Content about {topic}"
        
        # Generate hashtags
        hashtags = self.generate_hashtags(topic)
        
        # Create content piece
        content_piece = ContentPiece(
            id=content_id,
            type=content_type,
            content=content,
            platform=platform,
            hashtags=hashtags,
            timestamp=datetime.datetime.now().isoformat(),
            metadata={
                'topic': topic,
                'style': self.config.get('content_style', 'professional'),
                'target_audience': self.config.get('target_audience', 'general')
            }
        )
        
        return content_piece
    
    def generate_complete_post(self, topic: str, platform: str = "instagram", include_visual: bool = True) -> Dict[str, Any]:
        """Generate a complete social media post with text and visual content."""
        # Generate the main content
        post_content = self.generate_post_content(topic)
        
        # Generate a caption
        caption = self.generate_caption(post_content, platform)
        
        # Generate hashtags
        hashtags = self.generate_hashtags(post_content)
        
        # Generate visual content if requested
        visual_path = ""
        if include_visual:
            # Create visual based on the post content
            visual_prompt = self.generate_image_prompt(post_content)
            visual_path = self.create_visual_content(post_content)
            
            # If creating visual failed, try generating an image with DALL-E
            if not visual_path:
                visual_path = self.generate_image(visual_prompt)
        
        # Create the complete post package
        post_package = {
            'topic': topic,
            'platform': platform,
            'post_content': post_content,
            'caption': caption,
            'hashtags': hashtags,
            'visual_path': visual_path,
            'timestamp': datetime.datetime.now().isoformat(),
            'content_id': ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        }
        
        # Save to file
        output_dir = Path(self.config.get('output_directory', './generated_content/'))
        filename = f"post_{post_package['content_id']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(post_package, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Complete post package saved to {filepath}")
        
        return post_package
    
    def generate_content_calendar(self, topics: List[str], days: int = 7) -> List[Dict[str, Any]]:
        """Generate a content calendar with posts scheduled over a period."""
        calendar = []
        
        # Distribute topics across the specified number of days
        topics_per_day = max(1, len(topics) // days)
        
        for day_offset in range(days):
            day_date = (datetime.datetime.now() + datetime.timedelta(days=day_offset)).strftime('%Y-%m-%d')
            
            # Select topics for this day
            start_idx = day_offset * topics_per_day
            end_idx = start_idx + topics_per_day
            day_topics = topics[start_idx:end_idx]
            
            if not day_topics and day_offset < len(topics):
                # If we run out of topics before days, cycle through remaining topics
                day_topics = [topics[day_offset % len(topics)]]
            
            day_posts = []
            for topic in day_topics:
                post = self.generate_complete_post(topic, include_visual=random.choice([True, False]))
                day_posts.append(post)
            
            calendar.append({
                'date': day_date,
                'posts': day_posts
            })
        
        # Save calendar to file
        output_dir = Path(self.config.get('output_directory', './generated_content/'))
        filename = f"content_calendar_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(calendar, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Content calendar saved to {filepath}")
        
        return calendar


def main():
    """Main function to demonstrate the AI influencer content creation pipeline."""
    print("AI Influencer Content Creation Pipeline")
    print("=" * 45)
    
    config_path = input("Enter config file path (default: ./ai_influencer_config.json): ").strip()
    if not config_path:
        config_path = "./ai_influencer_config.json"
    
    pipeline = AIInfluencerPipeline(config_path)
    
    print("\nOptions:")
    print("1. Generate a single post")
    print("2. Generate a complete post package (content + visual)")
    print("3. Generate a content calendar")
    print("4. Generate different types of content")
    
    choice = input("Choose option (1-4, default: 1): ").strip()
    
    if choice == "2":
        topic = input("Enter topic for the post: ").strip()
        platform = input("Enter platform (default: instagram): ").strip() or "instagram"
        include_visual = input("Include visual content? (y/N): ").strip().lower() == 'y'
        
        print(f"\nGenerating complete post about '{topic}' for {platform}...")
        post_package = pipeline.generate_complete_post(topic, platform, include_visual)
        
        print(f"\nGenerated post package:")
        print(f"  Topic: {post_package['topic']}")
        print(f"  Platform: {post_package['platform']}")
        print(f"  Content preview: {post_package['post_content'][:100]}...")
        print(f"  Hashtags: #{' #'.join(post_package['hashtags'][:5])}")
        print(f"  Visual: {post_package['visual_path'] if post_package['visual_path'] else 'None'}")
        print(f"  Saved to: {post_package['content_id']}")
    
    elif choice == "3":
        topics_input = input("Enter topics (comma-separated): ").strip()
        topics = [t.strip() for t in topics_input.split(',') if t.strip()]
        
        if not topics:
            topics = ["AI Trends", "Productivity Tips", "Tech Innovation", "Future of Work", "Digital Marketing"]
        
        days = input("Number of days for calendar (default: 7): ").strip()
        days = int(days) if days.isdigit() else 7
        
        print(f"\nGenerating content calendar for {days} days with {len(topics)} topics...")
        calendar = pipeline.generate_content_calendar(topics, days)
        
        print(f"\nGenerated content calendar for {len(calendar)} days")
        print(f"Total posts: {sum(len(day['posts']) for day in calendar)}")
        print(f"Calendar saved to file")
    
    elif choice == "4":
        print("\nContent types available:")
        print("1. Post")
        print("2. Caption")
        print("3. Blog Post")
        print("4. Video Script")
        
        content_choice = input("Choose content type (1-4): ").strip()
        topic = input("Enter topic: ").strip()
        
        if content_choice == "1":
            content = pipeline.generate_post_content(topic)
            print(f"\nGenerated post:\n{content}")
        elif content_choice == "2":
            content = pipeline.generate_caption(topic)
            print(f"\nGenerated caption:\n{content}")
        elif content_choice == "3":
            content = pipeline.generate_blog_post(topic)
            print(f"\nGenerated blog post:\n{content[:200]}...")
        elif content_choice == "4":
            content = pipeline.generate_video_script(topic)
            print(f"\nGenerated video script:\n{content[:200]}...")
        else:
            print("Invalid choice")
    
    else:  # Default to option 1
        topic = input("Enter topic for the post: ").strip()
        
        print(f"\nGenerating post about '{topic}'...")
        content = pipeline.generate_post_content(topic)
        
        print(f"\nGenerated content:\n{content}")
    
    print("\nAI influencer content creation pipeline completed!")


if __name__ == "__main__":
    main()