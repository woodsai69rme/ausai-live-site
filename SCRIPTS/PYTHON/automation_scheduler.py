"""
Automation and Scheduling Module for YouTube Enhancement Tools
This module adds scheduling features, recurring workflows, social media automation, and notification systems.
"""

import argparse
import os
import schedule
import subprocess
import sys
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
            # Schedule one-time task. ``schedule_time`` is normalized to now
            # when run_at is omitted, so run-now tasks execute immediately
            # without attempting arithmetic with None.
            delay = (task.schedule_time - datetime.now()).total_seconds()
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
            # If the task function returns a running thread, wait for it in the
            # background so the scheduler loop stays responsive, then mark the
            # task as completed (or failed) when the thread actually finishes.
            if isinstance(result, threading.Thread):
                def _wait_for_thread():
                    result.join()
                    exc = getattr(result, "exception", None)
                    if exc is not None:
                        task.status = TaskStatus.FAILED
                        task.completed_at = datetime.now()
                        logger.exception(f"Task '{task.name}' failed: {exc}")
                    else:
                        task.status = TaskStatus.COMPLETED
                        task.completed_at = datetime.now()
                        logger.info(f"Task '{task.name}' completed successfully")
                threading.Thread(target=_wait_for_thread, daemon=True).start()
                return result
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


def run_ui_vision_macro_server(
    macro_name: str,
    port: int = 8000,
    timeout: int = 300,
    run_macro_path: Path | None = None,
) -> subprocess.Popen:
    """Start the local HTTP server for a UI Vision macro and return the process handle.

    This wraps ``RPA/ui-vision/run_macro.py <macro> --no-open --timeout <timeout>``
    so a scheduler can keep the dashboard available for a UI Vision macro run.

    Args:
        macro_name: Name of the UI Vision macro to make available.
        port: Port for the local HTTP server.
        timeout: How many seconds the server should stay alive.
        run_macro_path: Optional path to ``run_macro.py``. If omitted, a relative
            path from this script is used.

    Returns:
        subprocess.Popen: The running run_macro.py process.
    """
    if run_macro_path is None:
        # This script lives at SCRIPTS/PYTHON/automation_scheduler.py
        run_macro_path = Path(__file__).resolve().parent.parent.parent / "RPA" / "ui-vision" / "run_macro.py"

    logger.info(f"Starting UI Vision server for macro '{macro_name}' on port {port} (timeout={timeout}s)")
    process = subprocess.Popen(
        [
            sys.executable,
            str(run_macro_path),
            macro_name,
            "--no-open",
            "--port", str(port),
            "--timeout", str(timeout),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return process


class ContentAutomationPipeline:
    """Class to manage content automation workflows"""
    
    # Environment variable names for SMTP configuration
    ENV_SMTP_SERVER = "SMTP_SERVER"
    ENV_SMTP_PORT = "SMTP_PORT"
    ENV_SMTP_USERNAME = "SMTP_USERNAME"
    ENV_SMTP_PASSWORD = "SMTP_PASSWORD"
    ENV_SMTP_SENDER = "SMTP_SENDER"
    ENV_SMTP_RECIPIENTS = "SMTP_RECIPIENTS"

    def __init__(self):
        self.scheduler = TaskScheduler()
        self.social_media_poster = SocialMediaPoster()
        self.notification_manager = NotificationManager()
        self.workflows = {}
        self._configure_email_from_env()

    def _configure_email_from_env(self) -> bool:
        """Auto-configure email notifications from environment variables.

        Reads ``SMTP_SERVER``, ``SMTP_PORT``, ``SMTP_USERNAME``,
        ``SMTP_PASSWORD``, ``SMTP_SENDER``, ``SMTP_RECIPIENTS`` from the
        environment. If all required vars are present, calls
        ``setup_email_notifications()`` automatically.

        ``SMTP_RECIPIENTS`` is a comma-separated list of email addresses.

        Returns:
            True if email was configured, False if env vars are missing.
        """
        server = os.environ.get(self.ENV_SMTP_SERVER)
        port_str = os.environ.get(self.ENV_SMTP_PORT)
        username = os.environ.get(self.ENV_SMTP_USERNAME)
        password = os.environ.get(self.ENV_SMTP_PASSWORD)
        sender = os.environ.get(self.ENV_SMTP_SENDER)
        recipients_str = os.environ.get(self.ENV_SMTP_RECIPIENTS)

        # All required: server, username, password, sender, at least one recipient
        if not all([server, username, password, sender, recipients_str]):
            return False

        try:
            port = int(port_str) if port_str else 587
        except (ValueError, TypeError):
            port = 587

        recipients = [r.strip() for r in recipients_str.split(",") if r.strip()]
        if not recipients:
            return False

        self.notification_manager.setup_email_notifications(
            smtp_server=server,
            smtp_port=port,
            username=username,
            password=password,
            sender_email=sender,
            recipient_emails=recipients,
        )
        logger.info(
            f"Email notifications auto-configured from env: "
            f"{server}:{port} -> {recipients[0]}..."
        )
        return True

    def is_email_configured(self) -> bool:
        """Check if email notifications are configured."""
        return bool(self.notification_manager.email_config)

    def send_test_email(self, recipient: str | None = None) -> dict:
        """Send a test email to verify SMTP configuration.

        Args:
            recipient: Override recipient. Uses configured recipients if None.

        Returns:
            Dict with 'email' key containing success/failure status.
        """
        if not self.is_email_configured():
            return {"email": False, "error": "Email not configured. Set SMTP_* env vars or use --setup-smtp."}

        # Temporarily override recipients if a specific address is given
        saved_recipients = None
        if recipient:
            saved_recipients = self.notification_manager.email_config.get("recipient_emails", [])
            self.notification_manager.email_config["recipient_emails"] = [recipient]

        result = self.notification_manager.send_notification(
            subject="[Test] Automation Scheduler SMTP Test",
            message=(
                "This is a test email from the Content Automation Pipeline.\n\n"
                f"Sent at: {datetime.now().isoformat()}\n"
                "If you received this, SMTP configuration is working correctly.\n"
            ),
        )

        # Restore original recipients
        if saved_recipients is not None:
            self.notification_manager.email_config["recipient_emails"] = saved_recipients

        return result
    
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
    
    @staticmethod
    def _extract_macro_url(macro_name: str) -> str | None:
        """Extract the dashboard URL from a UI Vision macro JSON."""
        path = _ui_vision_macro_path(macro_name)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for cmd in data.get("Commands", []):
                if cmd.get("Command") == "open":
                    return cmd.get("Target")
        except (json.JSONDecodeError, OSError):
            pass
        return None

    def schedule_ui_vision_macro(self,
                                  macro_name: str,
                                  run_at: datetime = None,
                                  interval_minutes: int = None,
                                  port: int = 8000,
                                  timeout: int = 300) -> str:
        """Schedule a UI Vision macro server session.

        Starts ``RPA/ui-vision/run_macro.py <macro> --no-open --timeout <timeout>``
        so the dashboard is available for the UI Vision browser extension to run
        the macro. The macro itself is still executed by UI Vision; this only
        keeps the local HTTP server alive for the scheduled window.

        Args:
            macro_name: Name of the macro (must match a JSON file in
                ``RPA/ui-vision/macros/`` without the ``.json`` extension).
            run_at: Specific datetime for a one-time run. Ignored if
                ``interval_minutes`` is provided.
            interval_minutes: Recurring interval in minutes. If provided, the
                macro server will be started repeatedly at this interval.
            port: Port for the local HTTP server.
            timeout: How long, in seconds, to keep the server alive for each
                scheduled run.

        Returns:
            str: The scheduled task ID.
        """
        macro_path = _ui_vision_macro_path(macro_name)
        if not macro_path.exists():
            raise FileNotFoundError(
                f"UI Vision macro '{macro_name}' not found at {macro_path}"
            )

        if interval_minutes is not None and interval_minutes * 60 < timeout:
            logger.warning(
                f"interval_minutes ({interval_minutes}) is shorter than timeout "
                f"({timeout}s); subsequent runs may fail with a port conflict."
            )

        def _start_server() -> None:
            process = run_ui_vision_macro_server(
                macro_name, port=port, timeout=timeout
            )
            try:
                stdout, stderr = process.communicate(timeout=timeout + 15)
                if process.returncode != 0:
                    logger.error(
                        f"UI Vision server for '{macro_name}' exited with "
                        f"code {process.returncode}: {stderr}"
                    )
                else:
                    logger.info(
                        f"UI Vision server for '{macro_name}' finished cleanly"
                    )
            except subprocess.TimeoutExpired:
                logger.warning(
                    f"UI Vision server for '{macro_name}' did not stop in "
                    f"time; terminating."
                )
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()

        def _start_server_nonblocking() -> threading.Thread:
            """Start the UI Vision server in its own thread so the scheduler loop stays responsive."""
            def _run_target() -> None:
                try:
                    _start_server()
                except BaseException as exc:
                    thread.exception = exc

            thread = threading.Thread(target=_run_target, daemon=True)
            thread.exception = None  # type: ignore[attr-defined]
            thread.start()
            return thread

        task_id = f"uivision_{macro_name}_{int(time.time())}"
        self.scheduler.add_task(
            task_id=task_id,
            name=f"UI Vision macro: {macro_name}",
            func=_start_server_nonblocking,
            run_at=run_at,
            interval_minutes=interval_minutes,
        )
        logger.info(
            f"Scheduled UI Vision macro '{macro_name}' (task ID: {task_id})"
        )
        return task_id

    # Path to wigolo_client.py for lazy import
    _WIGOLO_CLIENT_DIR = str(
        Path(__file__).resolve().parent.parent.parent / "RPA" / "ui-vision"
    )

    def schedule_web_research(self,
                                question: str,
                                run_at: datetime = None,
                                interval_minutes: int = None,
                                depth: str = "standard",
                                output_path: str | Path = None,
                                wigolo_port: int = 3333,
                                notify: bool = False) -> str:
        """Schedule a wigolo-powered web research task.

        Uses wigolo's local-first web intelligence (search, fetch, research)
        to research a question and optionally save the brief to disk.

        Requires wigolo to be running on the configured port (default 3333).

        Args:
            question: The research question to investigate.
            run_at: Specific datetime for a one-time run.
            interval_minutes: Recurring interval in minutes.
            depth: Research depth ("quick", "standard", "deep").
            output_path: Optional path to save the research brief.
            wigolo_port: wigolo server port (default: 3333).
            notify: If True, send the research brief via configured notifications.

        Returns:
            str: The scheduled task ID.

        Raises:
            ImportError: If wigolo_client module is not found.
        """
        # Ensure wigolo_client is importable at schedule time (fail fast)
        _wigolo_dir = self._WIGOLO_CLIENT_DIR
        if _wigolo_dir not in sys.path:
            sys.path.insert(0, _wigolo_dir)
        try:
            from wigolo_client import WigoloClient as _WC
            _WC  # reference to prevent unused-import lint
        except ImportError:
            logger.error(
                f"wigolo_client not found at {_wigolo_dir}. "
                f"Is wigolo_client.py in RPA/ui-vision/?"
            )
            raise

        def _do_research_notifying() -> dict:
            # Re-import inside the closure to get a fresh reference
            if self._WIGOLO_CLIENT_DIR not in sys.path:
                sys.path.insert(0, self._WIGOLO_CLIENT_DIR)
            from wigolo_client import WigoloClient

            _client = WigoloClient(base_url=f"http://127.0.0.1:{wigolo_port}")
            logger.info(f"Starting wigolo research: {question[:80]}...")
            result = _client.research(question, depth=depth, time_budget=60)

            brief = result.get("brief", "No brief returned.")
            sources = result.get("sources", [])

            logger.info(
                f"Research complete: {len(brief)} chars, "
                f"{len(sources)} sources"
            )

            if output_path:
                out = Path(output_path) if isinstance(output_path, str) else output_path
                out.parent.mkdir(parents=True, exist_ok=True)
                import json
                out.write_text(
                    json.dumps(result, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                logger.info(f"Research saved to {out}")

            # Send notification if configured
            if notify:
                source_lines = []
                displayed = min(len(sources), 10)
                for s in sources[:displayed]:
                    title = s.get("title", "?")
                    url = s.get("url", "")
                    source_lines.append(f"  - {title}: {url}")
                source_text = "\n".join(source_lines)

                header = f"Sources ({len(sources)})" if displayed == len(sources) else f"Sources ({displayed} of {len(sources)})"

                message = (
                    f"Research Question: {question}\n\n"
                    f"{brief}\n\n"
                    f"{header}:\n{source_text}\n\n"
                    f"Depth: {depth} | Sources: {len(sources)}"
                )

                results = self.notification_manager.send_notification(
                    subject=f"[Research] {question[:80]}",
                    message=message,
                )
                logger.info(f"Notification results: {results}")

            return result

        task_id = f"wigolo_research_{int(time.time())}"
        self.scheduler.add_task(
            task_id=task_id,
            name=f"Web research: {question[:50]}",
            func=_do_research_notifying,
            run_at=run_at,
            interval_minutes=interval_minutes,
        )
        logger.info(
            f"Scheduled wigolo research '{question[:60]}' (task ID: {task_id})"
        )
        return task_id

    def schedule_capture_and_analyze(
        self,
        macro_name: str,
        analysis_question: str,
        run_at: datetime | None = None,
        analyze_delay_minutes: int = 5,
        port: int = 8000,
        timeout: int = 300,
        wigolo_port: int = 3333,
        notify: bool = False,
        output_dir: str | Path | None = None,
    ) -> tuple[str, str]:
        """Schedule a combined macro-capture + wigolo-analysis pipeline.

        At ``run_at``, starts the UI Vision macro server so the dashboard is
        available. At ``run_at + analyze_delay_minutes``, uses wigolo to fetch
        the dashboard URL and research the content per ``analysis_question``.

        Args:
            macro_name: Name of the UI Vision macro (determines dashboard URL).
            analysis_question: Question for wigolo research to answer.
            run_at: When to run the capture (06:00). If omitted, runs now.
            analyze_delay_minutes: Minutes after capture to start analysis.
            port: HTTP server port for the macro.
            timeout: Timeout in seconds for the macro server.
            wigolo_port: wigolo server port (default: 3333).
            notify: If True, send analysis results via notifications.
            output_dir: Directory to save analysis results.

        Returns:
            Tuple[str, str]: (capture_task_id, analysis_task_id).

        Raises:
            FileNotFoundError: If the macro JSON is missing.
            ValueError: If the macro has no open command target.
        """
        # Resolve the dashboard URL from the macro
        dashboard_url = self._extract_macro_url(macro_name)
        if not dashboard_url:
            raise ValueError(
                f"Macro '{macro_name}' not found or has no 'open' command. "
                f"Looked in: {_ui_vision_macro_path(macro_name)}"
            )

        analysis_time = (
            run_at + timedelta(minutes=analyze_delay_minutes)
            if run_at
            else datetime.now() + timedelta(minutes=analyze_delay_minutes)
        )

        # Step 1 — schedule the UI Vision macro server
        capture_id = self.schedule_ui_vision_macro(
            macro_name=macro_name,
            run_at=run_at,
            port=port,
            timeout=timeout,
        )

        # Step 2 — schedule wigolo analysis
        def _do_analysis() -> dict:
            if self._WIGOLO_CLIENT_DIR not in sys.path:
                sys.path.insert(0, self._WIGOLO_CLIENT_DIR)
            from wigolo_client import WigoloClient

            _client = WigoloClient(base_url=f"http://127.0.0.1:{wigolo_port}")

            # 2a. Fetch the dashboard
            logger.info(f"Fetching dashboard for analysis: {dashboard_url}")
            fetch_result = _client.fetch(dashboard_url, render_js=True)
            title = fetch_result.get("title", "Dashboard")
            content = fetch_result.get("content", "")
            logger.info(f"Fetched '{title}': {len(content)} chars")

            # 2b. Research the question with the fetched context
            research_question = (
                f"I am looking at a dashboard at {dashboard_url}. "
                f"Title: {title}.\n\n"
                f"{analysis_question}"
            )
            logger.info(f"Running analysis: {analysis_question[:80]}...")
            research_result = _client.research(
                research_question, depth="standard", time_budget=60
            )

            brief = research_result.get("brief", "No analysis returned.")
            sources = research_result.get("sources", [])

            # 2c. Save results
            out_dir = Path(output_dir) if output_dir else Path("analysis_output")
            out_dir.mkdir(parents=True, exist_ok=True)
            ts = int(time.time())

            # Save fetched content
            fetch_path = out_dir / f"{macro_name}_fetch_{ts}.md"
            fetch_path.write_text(
                f"# {title}\n\n"
                f"Dashboard URL: {dashboard_url}\n"
                f"Fetched at: {datetime.now().isoformat()}\n\n"
                f"{content}",
                encoding="utf-8",
            )

            # Save analysis (brief + sources)
            analysis_path = out_dir / f"{macro_name}_analysis_{ts}.json"
            analysis_path.write_text(
                json.dumps(research_result, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            logger.info(
                f"Analysis saved: {analysis_path} "
                f"({len(brief)} chars, {len(sources)} sources)"
            )

            # 2d. Notify if requested
            if notify:
                source_lines = []
                displayed = min(len(sources), 10)
                for s in sources[:displayed]:
                    title_s = s.get("title", "?")
                    url_s = s.get("url", "")
                    source_lines.append(f"  - {title_s}: {url_s}")
                source_text = "\n".join(source_lines)
                header = (
                    f"Sources ({len(sources)})"
                    if displayed == len(sources)
                    else f"Sources ({displayed} of {len(sources)})"
                )
                message = (
                    f"Dashboard: {dashboard_url}\n"
                    f"Question: {analysis_question}\n\n"
                    f"=== Brief ===\n{brief}\n\n"
                    f"{header}:\n{source_text}\n\n"
                    f"Fetch: {len(content)} chars | "
                    f"Output: {analysis_path}"
                )
                notif_results = self.notification_manager.send_notification(
                    subject=f"[Analysis] {macro_name}: {analysis_question[:60]}",
                    message=message,
                )
                logger.info(f"Notification results: {notif_results}")

            return research_result

        analysis_id = f"analysis_{macro_name}_{int(time.time())}"
        self.scheduler.add_task(
            task_id=analysis_id,
            name=f"Analysis: {macro_name} — {analysis_question[:40]}",
            func=_do_analysis,
            run_at=analysis_time,
        )

        logger.info(
            f"Combined pipeline scheduled:\n"
            f"  Capture: '{macro_name}' at {run_at or 'now'}\n"
            f"  Analysis: '{analysis_question[:60]}' at {analysis_time}\n"
            f"  Dashboard: {dashboard_url}"
        )
        return capture_id, analysis_id

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


def _ui_vision_macro_path(macro_name: str) -> Path:
    """Return the expected macro JSON file path for a UI Vision macro."""
    return (
        Path(__file__).resolve().parent.parent.parent
        / "RPA"
        / "ui-vision"
        / "macros"
        / f"{macro_name}.json"
    )


def _interactive_smtp_setup(env_file: str = "interactive") -> None:
    """Interactive wizard to configure SMTP email notifications.

    Prompts for SMTP_* settings and writes them to ``.env`` (or a custom path).

    Args:
        env_file: Path to write env vars to. "interactive" prompts for the path.
    """
    import getpass

    print("=" * 60)
    print("  SMTP Email Configuration Wizard")
    print("=" * 60)
    print()
    print("You need:")
    print("  - SMTP server address (e.g., smtp.gmail.com, smtp.elasticemail.com)")
    print("  - SMTP port (587 for TLS, 465 for SSL)")
    print("  - Username (often your full email address)")
    print("  - Password or App Password")
    print("  - Sender email address")
    print("  - Recipient email address(es) (comma-separated)")
    print()
    print("Free options:")
    print("  1) Gmail SMTP (smtp.gmail.com:587) — requires App Password")
    print("  2) Elastic Email (smtp.elasticemail.com:2525) — 500 free emails/mo")
    print("  3) Resend (smtp.resend.com:587) — 100 free emails/day")
    print("  4) Mailtrap (sandbox) — for testing only, emails are previewed")
    print()

    # Determine output path
    if env_file == "interactive":
        default_path = Path(__file__).resolve().parent.parent.parent / ".env"
        path_str = input(f"Env file path [{default_path}]: ").strip()
        env_path = Path(path_str) if path_str else default_path
    else:
        env_path = Path(env_file)

    print(f"\nWriting SMTP config to: {env_path}")
    print()

    # Collect values
    server = input("SMTP server [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
    port_str = input("SMTP port [587]: ").strip() or "587"
    try:
        port = int(port_str)
    except ValueError:
        port = 587
    username = input("Username (often your email): ").strip()
    password = getpass.getpass("Password / App Password: ").strip()
    sender = input("Sender email: ").strip()
    recipients_str = input("Recipient email(s) (comma-separated): ").strip()

    if not all([username, password, sender, recipients_str]):
        print("\n[FAIL] All fields except server/port are required. Aborting.")
        sys.exit(1)

    # Build the env snippet
    lines = [
        f"# SMTP Email Configuration — added by setup-smtp wizard on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"{ContentAutomationPipeline.ENV_SMTP_SERVER}={server}",
        f"{ContentAutomationPipeline.ENV_SMTP_PORT}={port}",
        f"{ContentAutomationPipeline.ENV_SMTP_USERNAME}={username}",
        f"{ContentAutomationPipeline.ENV_SMTP_PASSWORD}={password}",
        f"{ContentAutomationPipeline.ENV_SMTP_SENDER}={sender}",
        f"{ContentAutomationPipeline.ENV_SMTP_RECIPIENTS}={recipients_str}",
        "",
    ]

    # Read existing .env if it exists, append to it
    existing = ""
    if env_path.exists():
        existing = env_path.read_text(encoding="utf-8")
        # Check if SMTP vars already exist
        if any(line.startswith("SMTP_") for line in existing.split("\n")):
            overwrite = input("\nSMTP_* vars already exist in this file. Overwrite? [y/N]: ").strip().lower()
            if overwrite != "y":
                print("Aborted. No changes made.")
                return
            # Remove existing SMTP_* lines
            new_lines = [line for line in existing.split("\n") if not line.startswith("SMTP_")]
            existing = "\n".join(new_lines).rstrip("\n") + "\n"

    with open(env_path, "a", encoding="utf-8") as f:
        if existing:
            f.write("\n")
        f.writelines(lines)

    print(f"\n[OK] SMTP configuration written to {env_path}")
    print()
    print("Next steps:")
    print(f"  1. Reload env:  source {env_path}  (or restart shell)")
    print("  2. Test email:  python automation_scheduler.py --test-email")
    print("  3. Run research with notifications:")
    print("       python automation_scheduler.py --wigolo-research \"your question\" --notify")


def _load_env_file(env_path: Path | None = None) -> None:
    """Load .env file into os.environ if python-dotenv is available.

    Only sets vars that are NOT already set in the environment, so manually
    exported vars take precedence.

    Args:
        env_path: Path to .env file. Defaults to looking for .env in the
            repo root and the current working directory.
    """
    candidates = []
    if env_path:
        candidates.append(env_path)
    else:
        repo_env = Path(__file__).resolve().parent.parent.parent / ".env"
        cwd_env = Path.cwd() / ".env"
        candidates = [repo_env, cwd_env]

    try:
        from dotenv import load_dotenv
        for candidate in candidates:
            if candidate.exists():
                loaded = load_dotenv(dotenv_path=candidate, override=False)
                if loaded:
                    logger.debug(f"Loaded env vars from {candidate}")
                break
    except ImportError:
        pass  # python-dotenv not installed, no-op


def _run_cli() -> None:
    """CLI entry point for scheduling tasks."""
    # Load .env before arg parsing so SMTP vars are available
    _load_env_file()

    parser = argparse.ArgumentParser(
        description="Schedule automation tasks: UI Vision macros, wigolo research, or combined capture+analysis pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Schedule UI Vision macro server:\n"
            "  python automation_scheduler.py --ui-vision-macro Read_Open_AI_Dashboard --interval 60\n\n"
            "  # Schedule wigolo web research:\n"
            "  python automation_scheduler.py --wigolo-research \"latest AI RPA trends\" --depth quick\n\n"
            "  # Combined pipeline: macro capture at 06:00 + wigolo analysis at 06:05:\n"
            "  python automation_scheduler.py --combined-pipeline Read_Open_AI_Dashboard \\\n"
            "      --analysis-question \"Summarize the key metrics shown\" --capture-at 06:00\n"
            "  # All times are 24h HH:MM format, defaults to now if omitted\n"
        ),
    )
    parser.add_argument(
        "--ui-vision-macro",
        default=None,
        help="Name of the UI Vision macro to schedule (e.g., Read_Open_AI_Dashboard)",
    )
    parser.add_argument(
        "--wigolo-research",
        default=None,
        help="Research question for wigolo web intelligence",
    )
    parser.add_argument(
        "--combined-pipeline",
        default=None,
        metavar="MACRO_NAME",
        help="Run a combined macro-capture + wigolo-analysis pipeline on this macro",
    )
    parser.add_argument(
        "--analysis-question",
        default="Summarize the key metrics, status indicators, and actionable items visible on this dashboard.",
        help="Question for wigolo to answer about the dashboard content (combined pipeline only)",
    )
    parser.add_argument(
        "--capture-at",
        default=None,
        metavar="HH:MM",
        help="24-hour time (HH:MM) to start the capture. Defaults to now if omitted.",
    )
    parser.add_argument(
        "--analyze-delay",
        type=int,
        default=5,
        help="Minutes after capture to start analysis (default: 5)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Recurring interval in minutes (default: 60)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the local HTTP server (default: 8000)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="How long, in seconds, to keep the server alive (default: 300)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for research results",
    )
    parser.add_argument(
        "--depth",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Research depth for wigolo (default: standard)",
    )
    parser.add_argument(
        "--wigolo-port",
        type=int,
        default=3333,
        help="wigolo server port (default: 3333)",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Send results via configured notifications (email/webhook)",
    )
    parser.add_argument(
        "--setup-smtp",
        default=None,
        nargs="?",
        const="interactive",
        metavar="ENV_FILE",
        help=(
            "Interactive SMTP setup. Writes SMTP_* env vars to .env or the "
            "specified file. Run with --setup-smtp to start the wizard."
        ),
    )
    parser.add_argument(
        "--test-email",
        default=None,
        nargs="?",
        const="self",
        metavar="RECIPIENT",
        help="Send a test email to verify SMTP config. Defaults to the configured recipient.",
    )
    args = parser.parse_args()

    pipeline = ContentAutomationPipeline()

    # --setup-smtp: interactive wizard
    if args.setup_smtp:
        _interactive_smtp_setup(args.setup_smtp)
        return

    # --test-email: quick SMTP test
    if args.test_email is not None:
        recipient = None if args.test_email == "self" else args.test_email
        if not pipeline.is_email_configured() and recipient is None:
            print("Email not configured. Run --setup-smtp first or set SMTP_* env vars.")
            sys.exit(1)
        result = pipeline.send_test_email(recipient=recipient)
        email_ok = result.get("email", False)
        if email_ok:
            print(f"[OK] Test email sent successfully to {recipient or 'configured recipients'}.")
        else:
            print(f"[FAIL] Test email failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        return

    # --notify without any scheduled task: warn
    if args.notify and not any([args.combined_pipeline, args.ui_vision_macro, args.wigolo_research]):
        print("Warning: --notify requires --combined-pipeline, --ui-vision-macro, or --wigolo-research.")
        print("Use --test-email to verify SMTP config separately.")
        sys.exit(1)

    if args.notify and not pipeline.is_email_configured():
        print("Warning: --notify flag set but email is NOT configured.")
        print("  Set SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, SMTP_SENDER, SMTP_RECIPIENTS env vars")
        print("  Or run: python automation_scheduler.py --setup-smtp")
        print()
        print("  Continuing without email notifications...")

    # Parse --capture-at into a datetime
    run_at: datetime | None = None
    if args.capture_at:
        try:
            hour, minute = args.capture_at.split(":")
            now = datetime.now()
            run_at = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
            if run_at < now:
                run_at += timedelta(days=1)  # Schedule for tomorrow if time has passed today
        except (ValueError, IndexError):
            print(f"Error: invalid --capture-at format '{args.capture_at}'. Use HH:MM (24h).", file=sys.stderr)
            sys.exit(1)

    if args.combined_pipeline:
        capture_id, analysis_id = pipeline.schedule_capture_and_analyze(
            macro_name=args.combined_pipeline,
            analysis_question=args.analysis_question,
            run_at=run_at,
            analyze_delay_minutes=args.analyze_delay,
            port=args.port,
            timeout=args.timeout,
            wigolo_port=args.wigolo_port,
            notify=args.notify,
            output_dir=args.output or None,
        )
        time_str = run_at.strftime("%H:%M") if run_at else "now"
        analysis_time_str = (
            (run_at + timedelta(minutes=args.analyze_delay)).strftime("%H:%M")
            if run_at
            else f"now + {args.analyze_delay}min"
        )
        print(f"[PIPELINE] Combined capture+analysis pipeline scheduled:")
        print(f"  Capture:  {args.combined_pipeline} at {time_str}  (task: {capture_id})")
        print(f"  Analysis: {args.analysis_question[:60]}... at {analysis_time_str}  (task: {analysis_id})")

    if args.ui_vision_macro:
        task_id = pipeline.schedule_ui_vision_macro(
            macro_name=args.ui_vision_macro,
            run_at=run_at,
            interval_minutes=args.interval,
            port=args.port,
            timeout=args.timeout,
        )
        print(f"Scheduled UI Vision macro: {args.ui_vision_macro} (task: {task_id})")

    if args.wigolo_research:
        pipeline.schedule_web_research(
            question=args.wigolo_research,
            run_at=run_at,
            interval_minutes=args.interval,
            depth=args.depth,
            output_path=args.output or None,
            wigolo_port=args.wigolo_port,
            notify=args.notify,
        )
        print(f"Scheduled wigolo research: {args.wigolo_research[:60]}...")

    pipeline.start_automation()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        pipeline.stop_automation()


if __name__ == "__main__":
    # Examples:
    #   python automation_scheduler.py --ui-vision-macro Read_Open_AI_Dashboard --interval 60 --timeout 300
    #   python automation_scheduler.py --wigolo-research "latest AI RPA trends" --depth quick
    #   python automation_scheduler.py --combined-pipeline Read_Open_AI_Dashboard --analysis-question "..." --capture-at 06:00
    cli_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    cli_parser.add_argument("--ui-vision-macro", default=None)
    cli_parser.add_argument("--wigolo-research", default=None)
    cli_parser.add_argument("--combined-pipeline", default=None)
    cli_args, remaining = cli_parser.parse_known_args()
    if '--help' in remaining or '-h' in remaining:
        # Route to the full-featured parser
        sys.argv = [sys.argv[0]] + remaining
        _run_cli()
    elif cli_args.ui_vision_macro or cli_args.wigolo_research or cli_args.combined_pipeline:
        _run_cli()
    else:
        print("YouTube Enhancement Tools - Automation and Scheduling Module")
        print("=" * 60)

        print("Available components:")
        print("- TaskScheduler: For scheduling tasks")
        print("- SocialMediaPoster: For posting to social media")
        print("- NotificationManager: For sending notifications")
        print("- ContentAutomationPipeline: For complete workflows")
        print("- schedule_ui_vision_macro: Schedule UI Vision macro server sessions")
        print("- schedule_web_research: Schedule wigolo web research tasks")
        print()
        print("Usage:")
        print("  python automation_scheduler.py --ui-vision-macro Read_Open_AI_Dashboard")
        print("  python automation_scheduler.py --wigolo-research \"your question\" --depth standard")