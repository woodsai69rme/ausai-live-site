"""
Automation and Scheduling Module for YouTube Enhancement Tools
This module adds scheduling features, recurring workflows, social media automation, and notification systems.
"""

import os
import schedule
import time
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Callable, Any
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Enum for task statuses"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Data class for scheduled tasks"""
    id: str
    name: str
    function: Callable
    args: tuple
    kwargs: dict
    schedule_time: datetime
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class TaskScheduler:
    """Class to manage scheduled tasks"""
    
    def __init__(self):
        self.tasks = {}
        self.scheduler_thread = None
        self.running = False
        self.scheduler = schedule.Scheduler()
    
    def add_task(self, task_id: str, name: str, func: Callable, 
                 args: tuple = (), kwargs: dict = None, 
                 run_at: datetime = None, 
                 interval_minutes: int = None) -> ScheduledTask:
        """
        Add a task to be scheduled
        
        Args:
            task_id (str): Unique identifier for the task
            name (str): Name of the task
            func (callable): Function to execute
            args (tuple): Arguments to pass to the function
            kwargs (dict): Keyword arguments to pass to the function
            run_at (datetime): Specific time to run the task
            interval_minutes (int): Interval in minutes for recurring tasks
            
        Returns:
            ScheduledTask: The created task object
        """
        if kwargs is None:
            kwargs = {}
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            function=func,
            args=args,
            kwargs=kwargs,
            schedule_time=run_at or datetime.now(),
            status=TaskStatus.PENDING
        )
        
        self.tasks[task_id] = task
        
        if interval_minutes:
            # Schedule recurring task
            self.scheduler.every(interval_minutes).minutes.do(
                self._execute_task_wrapper, task
            )
        else:
            # Schedule one-time task
            delay = (run_at - datetime.now()).total_seconds()
            if delay > 0:
                threading.Timer(delay, self._execute_task_wrapper, args=(task,)).start()
            else:
                # If the time has already passed, run immediately
                self._execute_task_wrapper(task)
        
        logger.info(f"Task '{name}' scheduled with ID: {task_id}")
        return task
    
    def _execute_task_wrapper(self, task: ScheduledTask):
        """Wrapper to execute a task and update its status"""
        task.status = TaskStatus.RUNNING
        try:
            logger.info(f"Executing task: {task.name}")
            result = task.function(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            logger.info(f"Task '{task.name}' completed successfully")
            return result
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            logger.error(f"Task '{task.name}' failed: {e}")
            raise
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.CANCELLED
            logger.info(f"Task '{task.name}' (ID: {task_id}) cancelled")
            return True
        return False
    
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get the status of a task"""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            logger.info("Task scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Task scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            self.scheduler.run_pending()
            time.sleep(1)  # Check every second


class SocialMediaPoster:
    """Class to handle social media posting automation"""
    
    def __init__(self):
        self.enabled_platforms = []
        self.credentials = {}
    
    def setup_platform(self, platform: str, credentials: Dict[str, str]):
        """Setup credentials for a social media platform"""
        self.credentials[platform] = credentials
        if platform not in self.enabled_platforms:
            self.enabled_platforms.append(platform)
        logger.info(f"Setup credentials for {platform}")
    
    def post_to_platform(self, platform: str, content: str, media_path: str = None):
        """Post content to a specific platform"""
        if platform not in self.enabled_platforms:
            logger.error(f"Platform {platform} not configured")
            return False
        
        try:
            if platform == "twitter":
                return self._post_to_twitter(content, media_path)
            elif platform == "facebook":
                return self._post_to_facebook(content, media_path)
            elif platform == "linkedin":
                return self._post_to_linkedin(content, media_path)
            elif platform == "mastodon":
                return self._post_to_mastodon(content, media_path)
            else:
                logger.error(f"Platform {platform} not supported")
                return False
        except Exception as e:
            logger.error(f"Error posting to {platform}: {e}")
            return False
    
    def _post_to_twitter(self, content: str, media_path: str = None):
        """Post to Twitter (placeholder implementation)"""
        # In a real implementation, you would use the Twitter API
        logger.info(f"Posting to Twitter: {content[:50]}...")
        if media_path:
            logger.info(f"Attaching media: {media_path}")
        # Placeholder for actual Twitter API call
        return True
    
    def _post_to_facebook(self, content: str, media_path: str = None):
        """Post to Facebook (placeholder implementation)"""
        # In a real implementation, you would use the Facebook API
        logger.info(f"Posting to Facebook: {content[:50]}...")
        if media_path:
            logger.info(f"Attaching media: {media_path}")
        # Placeholder for actual Facebook API call
        return True
    
    def _post_to_linkedin(self, content: str, media_path: str = None):
        """Post to LinkedIn (placeholder implementation)"""
        # In a real implementation, you would use the LinkedIn API
        logger.info(f"Posting to LinkedIn: {content[:50]}...")
        if media_path:
            logger.info(f"Attaching media: {media_path}")
        # Placeholder for actual LinkedIn API call
        return True
    
    def _post_to_mastodon(self, content: str, media_path: str = None):
        """Post to Mastodon (placeholder implementation)"""
        # In a real implementation, you would use the Mastodon API
        logger.info(f"Posting to Mastodon: {content[:50]}...")
        if media_path:
            logger.info(f"Attaching media: {media_path}")
        # Placeholder for actual Mastodon API call
        return True
    
    def post_to_all_platforms(self, content: str, media_path: str = None):
        """Post content to all configured platforms"""
        results = {}
        for platform in self.enabled_platforms:
            results[platform] = self.post_to_platform(platform, content, media_path)
        return results


class NotificationManager:
    """Class to manage notifications"""
    
    def __init__(self):
        self.email_config = {}
        self.webhook_urls = []
        self.notification_methods = []
    
    def setup_email_notifications(self, smtp_server: str, smtp_port: int, 
                                username: str, password: str, 
                                sender_email: str, recipient_emails: List[str]):
        """Setup email notifications"""
        self.email_config = {
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password,
            'sender_email': sender_email,
            'recipient_emails': recipient_emails
        }
        if 'email' not in self.notification_methods:
            self.notification_methods.append('email')
        logger.info("Email notifications configured")
    
    def setup_webhook_notifications(self, webhook_urls: List[str]):
        """Setup webhook notifications"""
        self.webhook_urls = webhook_urls
        if 'webhook' not in self.notification_methods:
            self.notification_methods.append('webhook')
        logger.info("Webhook notifications configured")
    
    def send_notification(self, subject: str, message: str, notification_types: List[str] = None):
        """Send notification using configured methods"""
        if notification_types is None:
            notification_types = self.notification_methods
        
        results = {}
        
        if 'email' in notification_types and self.email_config:
            results['email'] = self._send_email_notification(subject, message)
        
        if 'webhook' in notification_types and self.webhook_urls:
            results['webhook'] = self._send_webhook_notification(subject, message)
        
        return results
    
    def _send_email_notification(self, subject: str, message: str) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(self.email_config['recipient_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'], 
                          self.email_config['recipient_emails'], text)
            server.quit()
            
            logger.info("Email notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _send_webhook_notification(self, subject: str, message: str) -> bool:
        """Send webhook notification"""
        import requests
        
        success_count = 0
        for url in self.webhook_urls:
            try:
                payload = {
                    'subject': subject,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    success_count += 1
                    logger.info(f"Webhook notification sent to {url}")
                else:
                    logger.error(f"Failed to send webhook notification to {url}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error sending webhook notification to {url}: {e}")
        
        return success_count > 0


class ContentAutomationPipeline:
    """Class to manage content automation workflows"""
    
    def __init__(self):
        self.scheduler = TaskScheduler()
        self.social_media_poster = SocialMediaPoster()
        self.notification_manager = NotificationManager()
        self.workflows = {}
    
    def create_upload_workflow(self, video_path: str, title: str, description: str, 
                             tags: List[str], publish_datetime: datetime,
                             social_media_posts: List[Dict[str, str]] = None):
        """Create a workflow for uploading and promoting content"""
        
        workflow_id = f"upload_workflow_{int(time.time())}"
        
        # Step 1: Schedule the upload
        upload_task_id = f"{workflow_id}_upload"
        self.scheduler.add_task(
            task_id=upload_task_id,
            name=f"Upload video: {title}",
            func=self._perform_upload,
            kwargs={
                'video_path': video_path,
                'title': title,
                'description': description,
                'tags': tags
            },
            run_at=publish_datetime
        )
        
        # Step 2: Schedule social media posts after upload
        if social_media_posts:
            for i, post in enumerate(social_media_posts):
                post_delay = timedelta(minutes=post.get('delay_after_upload', 30))
                post_time = publish_datetime + post_delay
                
                post_task_id = f"{workflow_id}_social_{i}"
                self.scheduler.add_task(
                    task_id=post_task_id,
                    name=f"Social media post: {post.get('content', '')[:30]}...",
                    func=self._perform_social_media_post,
                    kwargs={
                        'platform': post['platform'],
                        'content': post['content'],
                        'media_path': video_path if post.get('include_video') else None
                    },
                    run_at=post_time
                )
        
        # Step 3: Schedule notification about upload
        notify_delay = timedelta(minutes=5)  # Notify 5 minutes after upload
        notify_time = publish_datetime + notify_delay
        
        notify_task_id = f"{workflow_id}_notify"
        self.scheduler.add_task(
            task_id=notify_task_id,
            name="Send upload notification",
            func=self._send_upload_notification,
            kwargs={
                'title': title,
                'publish_datetime': publish_datetime
            },
            run_at=notify_time
        )
        
        self.workflows[workflow_id] = {
            'video_path': video_path,
            'title': title,
            'description': description,
            'tags': tags,
            'publish_datetime': publish_datetime,
            'tasks': [upload_task_id, notify_task_id] + 
                     [f"{workflow_id}_social_{i}" for i in range(len(social_media_posts or []))]
        }
        
        logger.info(f"Upload workflow created: {workflow_id}")
        return workflow_id
    
    def _perform_upload(self, video_path: str, title: str, description: str, tags: List[str]):
        """Perform the actual upload (placeholder implementation)"""
        logger.info(f"Uploading video: {title}")
        logger.info(f"Video path: {video_path}")
        logger.info(f"Description: {description[:100]}...")
        logger.info(f"Tags: {tags}")
        
        # In a real implementation, this would upload to the desired platform
        # For now, we'll just log the action
        return True
    
    def _perform_social_media_post(self, platform: str, content: str, media_path: str = None):
        """Perform social media post"""
        return self.social_media_poster.post_to_platform(platform, content, media_path)
    
    def _send_upload_notification(self, title: str, publish_datetime: datetime):
        """Send notification about upload"""
        subject = f"Video Uploaded: {title}"
        message = f"The video '{title}' was successfully uploaded at {publish_datetime}."
        return self.notification_manager.send_notification(subject, message)
    
    def create_recurring_workflow(self, workflow_func: Callable, 
                                interval_minutes: int, 
                                workflow_name: str,
                                *args, **kwargs):
        """Create a recurring workflow"""
        
        workflow_id = f"recurring_{workflow_name}_{int(time.time())}"
        
        self.scheduler.add_task(
            task_id=workflow_id,
            name=f"Recurring: {workflow_name}",
            func=workflow_func,
            args=args,
            kwargs=kwargs,
            interval_minutes=interval_minutes
        )
        
        logger.info(f"Recurring workflow created: {workflow_id}")
        return workflow_id
    
    def start_automation(self):
        """Start the automation system"""
        self.scheduler.start_scheduler()
        logger.info("Content automation system started")
    
    def stop_automation(self):
        """Stop the automation system"""
        self.scheduler.stop_scheduler()
        logger.info("Content automation system stopped")


def setup_automation_example():
    """Example of setting up automation"""
    # Create automation pipeline
    pipeline = ContentAutomationPipeline()
    
    # Setup social media accounts
    pipeline.social_media_poster.setup_platform(
        "twitter", 
        {"api_key": "your_api_key", "api_secret": "your_api_secret"}
    )
    pipeline.social_media_poster.setup_platform(
        "mastodon", 
        {"access_token": "your_access_token", "api_base_url": "https://mastodon.instance"}
    )
    
    # Setup notifications
    pipeline.notification_manager.setup_email_notifications(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        username="your_email@gmail.com",
        password="your_app_password",
        sender_email="your_email@gmail.com",
        recipient_emails=["recipient@example.com"]
    )
    
    # Create a sample upload workflow
    video_path = "/path/to/video.mp4"
    title = "My Awesome Video"
    description = "Check out this awesome video I created!"
    tags = ["awesome", "video", "tutorial"]
    publish_time = datetime.now() + timedelta(days=1)  # Publish tomorrow
    
    social_media_posts = [
        {
            'platform': 'twitter',
            'content': f'Just published a new video: {title} #NewVideo #Tutorial',
            'delay_after_upload': 15,  # Post 15 minutes after upload
            'include_video': False
        },
        {
            'platform': 'mastodon',
            'content': f'New video alert! 🎥 {title}\n\n{description}',
            'delay_after_upload': 30,  # Post 30 minutes after upload
            'include_video': False
        }
    ]
    
    workflow_id = pipeline.create_upload_workflow(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        publish_datetime=publish_time,
        social_media_posts=social_media_posts
    )
    
    # Start the automation
    pipeline.start_automation()
    
    print(f"Automation workflow created with ID: {workflow_id}")
    print(f"Video will be published at: {publish_time}")
    
    # Keep the script running to allow scheduled tasks to execute
    try:
        while True:
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nStopping automation...")
        pipeline.stop_automation()


if __name__ == "__main__":
    # Example usage
    print("YouTube Enhancement Tools - Automation and Scheduling Module")
    print("=" * 60)
    
    # Show available classes and functions
    print("Available components:")
    print("- TaskScheduler: For scheduling tasks")
    print("- SocialMediaPoster: For posting to social media")
    print("- NotificationManager: For sending notifications")
    print("- ContentAutomationPipeline: For complete workflows")
    
    # Uncomment the line below to run the example
    # setup_automation_example()