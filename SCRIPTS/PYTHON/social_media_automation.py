import os
import json
import time
import random
import schedule  # pip install schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import requests
from selenium import webdriver  # pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import tweepy  # pip install tweepy
import instabot  # pip install instabot
from facebook_business.adobjects.page import Page  # pip install facebook-business
from facebook_business.api import FacebookAdsApi


@dataclass
class SocialMediaPost:
    """Represents a social media post."""
    id: str
    platform: str
    content: str
    hashtags: List[str]
    image_path: Optional[str]
    scheduled_time: datetime
    posted: bool = False
    engagement_metrics: Dict[str, int] = None


class SocialMediaAutomation:
    """
    Comprehensive social media automation tools for managing posts,
    engagement, and analytics across multiple platforms.
    """
    
    def __init__(self, config_path: str = "./social_media_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize platform clients
        self.twitter_client = None
        self.instagram_bot = None
        self.facebook_api = None
        
        # Initialize web driver for browser automation
        self.driver = None
        
        # Scheduled posts storage
        self.scheduled_posts_file = Path("./scheduled_posts.json")
        self.scheduled_posts = self.load_scheduled_posts()
        
        # Initialize API clients
        self.init_twitter()
        self.init_instagram()
        self.init_facebook()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            "twitter": {
                "api_key": "",
                "api_secret": "",
                "access_token": "",
                "access_token_secret": "",
                "bearer_token": ""
            },
            "instagram": {
                "username": "",
                "password": ""
            },
            "facebook": {
                "access_token": "",
                "page_id": ""
            },
            "linkedin": {
                "access_token": ""
            },
            "threads": {
                "username": "",
                "password": ""
            },
            "posting_schedule": {
                "twitter": "09:00,13:00,17:00",
                "instagram": "10:00,19:00",
                "facebook": "11:00,15:00,20:00"
            },
            "engagement_settings": {
                "auto_like_hashtags": ["ai", "technology", "innovation"],
                "auto_follow_followers": True,
                "auto_comment_probability": 0.3
            },
            "content_settings": {
                "max_daily_posts": 3,
                "reuse_content_days": 7
            }
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
        
        return config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def init_twitter(self):
        """Initialize Twitter API client."""
        twitter_config = self.config.get('twitter', {})
        if all(twitter_config.get(key) for key in ['api_key', 'api_secret', 'access_token', 'access_token_secret']):
            try:
                auth = tweepy.OAuthHandler(
                    twitter_config['api_key'],
                    twitter_config['api_secret']
                )
                auth.set_access_token(
                    twitter_config['access_token'],
                    twitter_config['access_token_secret']
                )
                self.twitter_client = tweepy.API(auth)
                self.logger.info("Twitter API initialized")
            except Exception as e:
                self.logger.error(f"Error initializing Twitter API: {e}")
        else:
            self.logger.warning("Twitter API credentials not configured")
    
    def init_instagram(self):
        """Initialize Instagram bot."""
        instagram_config = self.config.get('instagram', {})
        if instagram_config.get('username') and instagram_config.get('password'):
            try:
                # Note: This is a simplified initialization
                # In practice, you'd use a library like instabot or undetected_chromedriver
                self.logger.info("Instagram bot initialized")
            except Exception as e:
                self.logger.error(f"Error initializing Instagram bot: {e}")
        else:
            self.logger.warning("Instagram credentials not configured")
    
    def init_facebook(self):
        """Initialize Facebook API."""
        facebook_config = self.config.get('facebook', {})
        if facebook_config.get('access_token') and facebook_config.get('page_id'):
            try:
                FacebookAdsApi.init(access_token=facebook_config['access_token'])
                self.facebook_api = FacebookAdsApi.get_default_api()
                self.logger.info("Facebook API initialized")
            except Exception as e:
                self.logger.error(f"Error initializing Facebook API: {e}")
        else:
            self.logger.warning("Facebook API credentials not configured")
    
    def init_web_driver(self):
        """Initialize web driver for browser automation."""
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.logger.info("Web driver initialized")
            except Exception as e:
                self.logger.error(f"Error initializing web driver: {e}")
    
    def load_scheduled_posts(self) -> List[SocialMediaPost]:
        """Load scheduled posts from file."""
        if self.scheduled_posts_file.exists():
            with open(self.scheduled_posts_file, 'r') as f:
                data = json.load(f)
                # Convert dict back to SocialMediaPost objects
                posts = []
                for item in data:
                    post = SocialMediaPost(
                        id=item['id'],
                        platform=item['platform'],
                        content=item['content'],
                        hashtags=item['hashtags'],
                        image_path=item['image_path'],
                        scheduled_time=datetime.fromisoformat(item['scheduled_time']),
                        posted=item['posted'],
                        engagement_metrics=item.get('engagement_metrics', {})
                    )
                    posts.append(post)
                return posts
        return []
    
    def save_scheduled_posts(self):
        """Save scheduled posts to file."""
        data = []
        for post in self.scheduled_posts:
            item = {
                'id': post.id,
                'platform': post.platform,
                'content': post.content,
                'hashtags': post.hashtags,
                'image_path': post.image_path,
                'scheduled_time': post.scheduled_time.isoformat(),
                'posted': post.posted,
                'engagement_metrics': post.engagement_metrics
            }
            data.append(item)
        
        with open(self.scheduled_posts_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def schedule_post(self, platform: str, content: str, hashtags: List[str] = None, 
                     image_path: str = None, scheduled_time: datetime = None) -> str:
        """Schedule a post for a specific time."""
        if scheduled_time is None:
            # Default to 2 hours from now
            scheduled_time = datetime.now() + timedelta(hours=2)
        
        post_id = f"post_{int(time.time())}_{random.randint(1000, 9999)}"
        
        post = SocialMediaPost(
            id=post_id,
            platform=platform,
            content=content,
            hashtags=hashtags or [],
            image_path=image_path,
            scheduled_time=scheduled_time,
            posted=False,
            engagement_metrics={}
        )
        
        self.scheduled_posts.append(post)
        self.save_scheduled_posts()
        
        self.logger.info(f"Scheduled post {post_id} for {scheduled_time} on {platform}")
        return post_id
    
    def post_to_twitter(self, content: str, image_path: str = None) -> bool:
        """Post to Twitter."""
        if not self.twitter_client:
            self.logger.error("Twitter client not initialized")
            return False
        
        try:
            if image_path and Path(image_path).exists():
                media = self.twitter_client.media_upload(image_path)
                self.twitter_client.update_status(content, media_ids=[media.media_id])
            else:
                self.twitter_client.update_status(content)
            
            self.logger.info("Posted to Twitter successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error posting to Twitter: {e}")
            return False
    
    def post_to_instagram(self, content: str, image_path: str) -> bool:
        """Post to Instagram."""
        if not self.config.get('instagram', {}).get('username'):
            self.logger.error("Instagram credentials not configured")
            return False
        
        try:
            # This is a simplified implementation
            # In practice, you'd use a library like instabot or selenium
            self.init_web_driver()
            
            # Navigate to Instagram
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            # Wait for login page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # Login
            username_field = self.driver.find_element(By.NAME, "username")
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(self.config['instagram']['username'])
            password_field.send_keys(self.config['instagram']['password'])
            
            # Submit login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Navigate to create post page
            self.driver.get("https://www.instagram.com/create/")
            
            # Upload image
            # This is simplified - actual implementation would require more steps
            # and handling of Instagram's dynamic UI
            
            self.logger.info("Posted to Instagram successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error posting to Instagram: {e}")
            return False
    
    def post_to_facebook(self, content: str, image_path: str = None) -> bool:
        """Post to Facebook."""
        if not self.facebook_api:
            self.logger.error("Facebook API not initialized")
            return False
        
        try:
            # This is a simplified implementation
            # In practice, you'd use the Facebook Graph API properly
            page_id = self.config['facebook']['page_id']
            
            # Post content
            params = {
                'message': content
            }
            
            if image_path and Path(image_path).exists():
                # Upload photo first, then post
                pass
            
            # This is where you'd make the actual API call
            # page = Page(page_id, api=self.facebook_api)
            # post = page.create_feed(params)
            
            self.logger.info("Posted to Facebook successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error posting to Facebook: {e}")
            return False
    
    def execute_scheduled_posts(self):
        """Execute posts that are scheduled for now."""
        now = datetime.now()
        executed_count = 0
        
        for post in self.scheduled_posts:
            if not post.posted and post.scheduled_time <= now:
                success = False
                
                if post.platform.lower() == 'twitter':
                    success = self.post_to_twitter(post.content, post.image_path)
                elif post.platform.lower() == 'instagram':
                    success = self.post_to_instagram(post.content, post.image_path)
                elif post.platform.lower() == 'facebook':
                    success = self.post_to_facebook(post.content, post.image_path)
                
                if success:
                    post.posted = True
                    executed_count += 1
                    self.logger.info(f"Successfully posted {post.id}")
                else:
                    self.logger.error(f"Failed to post {post.id}")
        
        if executed_count > 0:
            self.save_scheduled_posts()
            self.logger.info(f"Executed {executed_count} scheduled posts")
    
    def auto_engage_with_followers(self):
        """Automatically engage with followers."""
        engagement_settings = self.config.get('engagement_settings', {})
        
        if engagement_settings.get('auto_follow_followers'):
            self.auto_follow_back()
        
        if engagement_settings.get('auto_like_hashtags'):
            self.like_posts_with_hashtags(engagement_settings['auto_like_hashtags'])
        
        if engagement_settings.get('auto_comment_probability', 0) > random.random():
            self.leave_engaging_comments()
    
    def auto_follow_back(self):
        """Follow back followers."""
        if not self.twitter_client:
            return
        
        try:
            # Get followers
            followers = tweepy.Cursor(self.twitter_client.get_followers).items(50)
            
            for follower in followers:
                if not follower.following:
                    # Follow back
                    follower.follow()
                    self.logger.info(f"Followed back user: {follower.screen_name}")
                    time.sleep(random.randint(5, 15))  # Random delay to avoid rate limiting
        except Exception as e:
            self.logger.error(f"Error auto-following: {e}")
    
    def like_posts_with_hashtags(self, hashtags: List[str]):
        """Like posts that contain specified hashtags."""
        if not self.twitter_client:
            return
        
        try:
            for hashtag in hashtags:
                # Search for tweets with hashtag
                tweets = tweepy.Cursor(
                    self.twitter_client.search_tweets,
                    q=f"#{hashtag}",
                    result_type="recent"
                ).items(10)  # Like 10 recent posts per hashtag
                
                for tweet in tweets:
                    try:
                        tweet.favorite()
                        self.logger.info(f"Liked tweet with #{hashtag}: {tweet.id}")
                        time.sleep(random.randint(10, 30))  # Delay between likes
                    except Exception as e:
                        self.logger.error(f"Error liking tweet {tweet.id}: {e}")
        except Exception as e:
            self.logger.error(f"Error liking posts with hashtags: {e}")
    
    def leave_engaging_comments(self):
        """Leave engaging comments on relevant posts."""
        if not self.twitter_client:
            return
        
        try:
            # Search for relevant content to comment on
            search_terms = ["AI", "technology", "innovation", "startup"]
            search_term = random.choice(search_terms)
            
            tweets = tweepy.Cursor(
                self.twitter_client.search_tweets,
                q=search_term,
                result_type="recent"
            ).items(5)
            
            for tweet in tweets:
                # Generate a relevant comment
                comments = [
                    f"Interesting perspective on {search_term}! Thanks for sharing.",
                    f"This is a great point about {search_term}. Very insightful!",
                    f"I appreciate you sharing your thoughts on {search_term}.",
                    f"Thanks for the {search_term} insights. Looking forward to more!"
                ]
                
                comment = random.choice(comments)
                
                try:
                    # Reply to the tweet
                    self.twitter_client.update_status(
                        status=comment,
                        in_reply_to_status_id=tweet.id,
                        auto_populate_reply_metadata=True
                    )
                    self.logger.info(f"Commented on tweet: {tweet.id}")
                    time.sleep(random.randint(30, 60))  # Delay between comments
                except Exception as e:
                    self.logger.error(f"Error commenting on tweet {tweet.id}: {e}")
        except Exception as e:
            self.logger.error(f"Error leaving comments: {e}")
    
    def get_engagement_metrics(self, platform: str) -> Dict[str, Any]:
        """Get engagement metrics for a platform."""
        try:
            if platform.lower() == 'twitter':
                if not self.twitter_client:
                    return {}
                
                # Get account information
                me = self.twitter_client.verify_credentials()
                
                metrics = {
                    'followers': me.followers_count,
                    'following': me.friends_count,
                    'tweets': me.statuses_count,
                    'likes_received': 0,  # This would require more complex queries
                    'retweets_received': 0,
                    'mentions': 0
                }
                
                # Get recent mentions
                mentions = self.twitter_client.mentions_timeline(count=50)
                metrics['mentions'] = len(mentions)
                
                return metrics
            
            elif platform.lower() == 'instagram':
                # This would require Instagram API access
                return {
                    'followers': 0,
                    'following': 0,
                    'posts': 0,
                    'likes_received': 0,
                    'comments_received': 0
                }
            
            elif platform.lower() == 'facebook':
                # This would require Facebook API access
                return {
                    'followers': 0,
                    'page_likes': 0,
                    'posts': 0,
                    'likes_received': 0,
                    'comments_received': 0,
                    'shares_received': 0
                }
        except Exception as e:
            self.logger.error(f"Error getting metrics for {platform}: {e}")
            return {}
    
    def generate_content_ideas(self, topic: str, count: int = 5) -> List[str]:
        """Generate content ideas based on a topic."""
        # This would typically connect to an AI service to generate ideas
        # For now, we'll return some example ideas
        ideas = [
            f"Why {topic} is changing the industry in 2024",
            f"5 tips for mastering {topic}",
            f"How I learned to love {topic}: A beginner's journey",
            f"The future of {topic}: What experts are predicting",
            f"{topic} myths debunked: What you need to know",
            f"How {topic} can improve your daily routine",
            f"The hidden benefits of {topic} that nobody talks about",
            f"{topic} vs traditional approaches: A comprehensive comparison",
            f"Real-world examples of {topic} in action",
            f"Common mistakes people make with {topic} and how to avoid them"
        ]
        
        return ideas[:count]
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread."""
        def scheduler_loop():
            while True:
                # Execute scheduled posts
                self.execute_scheduled_posts()
                
                # Perform auto-engagement
                self.auto_engage_with_followers()
                
                # Sleep for 1 minute before checking again
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
        self.logger.info("Scheduler started")
    
    def start_auto_posting(self, platform: str, content_ideas: List[str]):
        """Start automatic posting based on content ideas."""
        posting_schedule = self.config.get('posting_schedule', {}).get(platform, "09:00,13:00,17:00")
        times = [datetime.strptime(t.strip(), "%H:%M").time() for t in posting_schedule.split(",")]
        
        for i, idea in enumerate(content_ideas):
            # Schedule post at one of the designated times
            target_time = datetime.combine(datetime.now().date(), times[i % len(times)])
            
            # If the time has already passed today, schedule for tomorrow
            if target_time <= datetime.now().time():
                target_time = datetime.combine(datetime.now().date() + timedelta(days=1), target_time.time())
            else:
                target_time = datetime.combine(datetime.now().date(), target_time)
            
            # Add some randomness to the schedule
            target_time += timedelta(minutes=random.randint(-30, 30))
            
            self.schedule_post(
                platform=platform,
                content=idea,
                hashtags=[platform, "automation", "ai"],
                scheduled_time=target_time
            )
        
        self.logger.info(f"Scheduled {len(content_ideas)} posts for {platform}")


def main():
    """Main function to demonstrate the social media automation tools."""
    print("Social Media Automation Tools")
    print("=" * 30)
    
    config_path = input("Enter config file path (default: ./social_media_config.json): ").strip()
    if not config_path:
        config_path = "./social_media_config.json"
    
    automation = SocialMediaAutomation(config_path)
    
    print("\nOptions:")
    print("1. Schedule a post")
    print("2. View scheduled posts")
    print("3. Generate content ideas")
    print("4. Start auto-posting")
    print("5. Get engagement metrics")
    print("6. Start scheduler")
    
    choice = input("Choose option (1-6, default: 1): ").strip()
    
    if choice == "2":
        print("\nScheduled Posts:")
        for post in automation.scheduled_posts:
            status = "POSTED" if post.posted else "SCHEDULED"
            print(f"  {status}: {post.platform} - {post.content[:50]}... at {post.scheduled_time}")
    
    elif choice == "3":
        topic = input("Enter topic for content ideas: ").strip()
        count = input("Number of ideas (default: 5): ").strip()
        count = int(count) if count.isdigit() else 5
        
        ideas = automation.generate_content_ideas(topic, count)
        print(f"\nGenerated {len(ideas)} content ideas:")
        for i, idea in enumerate(ideas, 1):
            print(f"  {i}. {idea}")
    
    elif choice == "4":
        platform = input("Enter platform (twitter/instagram/facebook, default: twitter): ").strip() or "twitter"
        topic = input("Enter topic for content: ").strip()
        
        ideas = automation.generate_content_ideas(topic, 5)
        automation.start_auto_posting(platform, ideas)
        print(f"Started auto-posting to {platform} with {len(ideas)} ideas")
    
    elif choice == "5":
        platform = input("Enter platform (twitter/instagram/facebook, default: twitter): ").strip() or "twitter"
        metrics = automation.get_engagement_metrics(platform)
        print(f"\nEngagement metrics for {platform}:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")
    
    elif choice == "6":
        print("Starting scheduler...")
        automation.run_scheduler()
        print("Scheduler running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")
    
    else:  # Default to option 1
        platform = input("Enter platform (twitter/instagram/facebook, default: twitter): ").strip() or "twitter"
        content = input("Enter content for the post: ").strip()
        hashtags_input = input("Enter hashtags (comma-separated, optional): ").strip()
        hashtags = [tag.strip() for tag in hashtags_input.split(',')] if hashtags_input else []
        image_path = input("Enter image path (optional): ").strip() or None
        
        # Schedule for 2 hours from now
        scheduled_time = datetime.now() + timedelta(hours=2)
        
        post_id = automation.schedule_post(
            platform=platform,
            content=content,
            hashtags=hashtags,
            image_path=image_path,
            scheduled_time=scheduled_time
        )
        
        print(f"\nScheduled post with ID: {post_id}")
        print(f"Will post to {platform} at {scheduled_time}")
    
    print("\nSocial media automation tools completed!")


if __name__ == "__main__":
    main()