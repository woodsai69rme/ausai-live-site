"""
Multi-Platform Support Module for YouTube Enhancement Tools
This module adds support for platforms beyond YouTube including Vimeo, TikTok, Instagram, etc.
"""

import os
import requests
import json
from typing import Dict, List, Optional
from pathlib import Path
import subprocess
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PlatformInterface(ABC):
    """
    Abstract base class for platform interfaces
    """
    
    @abstractmethod
    def download_video(self, url: str, output_path: str) -> bool:
        """
        Download a video from the platform
        
        Args:
            url (str): URL of the video to download
            output_path (str): Path to save the downloaded video
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get information about a video
        
        Args:
            url (str): URL of the video
            
        Returns:
            dict: Video information or None if failed
        """
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is valid for this platform
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass


class VimeoInterface(PlatformInterface):
    """
    Interface for Vimeo platform
    """
    
    def __init__(self):
        self.base_url = "https://api.vimeo.com"
        self.access_token = os.getenv('VIMEO_ACCESS_TOKEN')
    
    def download_video(self, url: str, output_path: str) -> bool:
        """
        Download a video from Vimeo
        Note: Vimeo has strict policies against scraping/downloading
        This is a placeholder implementation
        """
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                logger.error(f"Could not extract video ID from URL: {url}")
                return False
            
            # Use yt-dlp to download Vimeo video
            cmd = [
                "yt-dlp",
                "-o", output_path,
                url
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Successfully downloaded Vimeo video to: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error downloading Vimeo video: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading Vimeo video: {e}")
            return False
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get information about a Vimeo video
        """
        try:
            # Use yt-dlp to get video info
            cmd = [
                "yt-dlp",
                "--dump-json",
                url
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            video_info = json.loads(result.stdout)
            
            return {
                "title": video_info.get("title", ""),
                "description": video_info.get("description", ""),
                "uploader": video_info.get("uploader", ""),
                "duration": video_info.get("duration", 0),
                "view_count": video_info.get("view_count", 0),
                "upload_date": video_info.get("upload_date", ""),
                "thumbnail": video_info.get("thumbnail", "")
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Error getting Vimeo video info: {e}")
            return None
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid Vimeo URL
        """
        import re
        vimeo_pattern = r'^https?://(www\.)?vimeo\.com/\d+'
        return bool(re.match(vimeo_pattern, url))
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from Vimeo URL
        """
        import re
        match = re.search(r'vimeo\.com/(\d+)', url)
        return match.group(1) if match else None


class TikTokInterface(PlatformInterface):
    """
    Interface for TikTok platform
    """
    
    def __init__(self):
        self.base_url = "https://www.tiktok.com"
    
    def download_video(self, url: str, output_path: str) -> bool:
        """
        Download a video from TikTok
        """
        try:
            cmd = [
                "yt-dlp",
                "-o", output_path,
                "--no-watermark",  # Try to download without watermark
                url
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Successfully downloaded TikTok video to: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error downloading TikTok video: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading TikTok video: {e}")
            return False
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get information about a TikTok video
        """
        try:
            cmd = [
                "yt-dlp",
                "--dump-json",
                url
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            video_info = json.loads(result.stdout)
            
            return {
                "title": video_info.get("title", ""),
                "description": video_info.get("description", ""),
                "uploader": video_info.get("uploader", ""),
                "duration": video_info.get("duration", 0),
                "view_count": video_info.get("view_count", 0),
                "like_count": video_info.get("like_count", 0),
                "comment_count": video_info.get("comment_count", 0),
                "share_count": video_info.get("repost_count", 0)
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Error getting TikTok video info: {e}")
            return None
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid TikTok URL
        """
        import re
        tiktok_pattern = r'^https?://(www\.)?tiktok\.com/@[\w.-]+/video/\d+'
        return bool(re.match(tiktok_pattern, url))


class InstagramInterface(PlatformInterface):
    """
    Interface for Instagram platform
    """
    
    def __init__(self):
        self.base_url = "https://www.instagram.com"
    
    def download_video(self, url: str, output_path: str) -> bool:
        """
        Download a video from Instagram
        """
        try:
            cmd = [
                "yt-dlp",
                "-o", output_path,
                url
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Successfully downloaded Instagram video to: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error downloading Instagram video: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading Instagram video: {e}")
            return False
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get information about an Instagram video
        """
        try:
            cmd = [
                "yt-dlp",
                "--dump-json",
                url
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            video_info = json.loads(result.stdout)
            
            return {
                "title": video_info.get("title", ""),
                "description": video_info.get("description", ""),
                "uploader": video_info.get("uploader", ""),
                "duration": video_info.get("duration", 0),
                "view_count": video_info.get("view_count", 0),
                "like_count": video_info.get("like_count", 0),
                "comment_count": video_info.get("comment_count", 0)
            }
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Error getting Instagram video info: {e}")
            return None
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid Instagram URL
        """
        import re
        instagram_pattern = r'^https?://(www\.)?instagram\.com/(p|reel)/[\w-]+/'
        return bool(re.match(instagram_pattern, url))


class MultiPlatformProcessor:
    """
    Processor that handles multiple platforms
    """
    
    def __init__(self):
        self.platforms = {
            'vimeo': VimeoInterface(),
            'tiktok': TikTokInterface(),
            'instagram': InstagramInterface()
        }
    
    def detect_platform(self, url: str) -> Optional[str]:
        """
        Detect which platform a URL belongs to
        
        Args:
            url (str): URL to analyze
            
        Returns:
            str: Platform name or None if not recognized
        """
        url_lower = url.lower()
        
        if 'vimeo.com' in url_lower:
            return 'vimeo'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        else:
            return None
    
    def download_video(self, url: str, output_path: str) -> bool:
        """
        Download a video from any supported platform
        
        Args:
            url (str): URL of the video to download
            output_path (str): Path to save the downloaded video
            
        Returns:
            bool: True if successful, False otherwise
        """
        platform = self.detect_platform(url)
        
        if not platform:
            logger.error(f"Unsupported platform for URL: {url}")
            return False
        
        platform_interface = self.platforms[platform]
        return platform_interface.download_video(url, output_path)
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get information about a video from any supported platform
        
        Args:
            url (str): URL of the video
            
        Returns:
            dict: Video information or None if failed
        """
        platform = self.detect_platform(url)
        
        if not platform:
            logger.error(f"Unsupported platform for URL: {url}")
            return None
        
        platform_interface = self.platforms[platform]
        return platform_interface.get_video_info(url)
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is valid for any supported platform
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        platform = self.detect_platform(url)
        
        if not platform:
            return False
        
        platform_interface = self.platforms[platform]
        return platform_interface.validate_url(url)
    
    def get_supported_platforms(self) -> List[str]:
        """
        Get list of supported platforms
        
        Returns:
            list: List of supported platform names
        """
        return list(self.platforms.keys())


class CrossPlatformUploader:
    """
    Class to handle uploading videos to multiple platforms
    """
    
    def __init__(self):
        self.supported_platforms = ['youtube', 'vimeo', 'tiktok', 'instagram']
    
    def upload_to_platforms(self, video_path: str, title: str, description: str, 
                           platforms: List[str], tags: List[str] = None) -> Dict[str, bool]:
        """
        Upload a video to multiple platforms
        
        Args:
            video_path (str): Path to the video file to upload
            title (str): Title for the video
            description (str): Description for the video
            platforms (list): List of platforms to upload to
            tags (list, optional): Tags for the video
            
        Returns:
            dict: Upload results for each platform
        """
        results = {}
        
        for platform in platforms:
            if platform.lower() not in self.supported_platforms:
                logger.warning(f"Platform {platform} not supported for upload")
                results[platform] = False
                continue
            
            try:
                if platform.lower() == 'youtube':
                    results[platform] = self._upload_to_youtube(video_path, title, description, tags)
                elif platform.lower() == 'vimeo':
                    results[platform] = self._upload_to_vimeo(video_path, title, description, tags)
                elif platform.lower() == 'tiktok':
                    results[platform] = self._upload_to_tiktok(video_path, title, description, tags)
                elif platform.lower() == 'instagram':
                    results[platform] = self._upload_to_instagram(video_path, title, description, tags)
                else:
                    results[platform] = False
                    
            except Exception as e:
                logger.error(f"Error uploading to {platform}: {e}")
                results[platform] = False
        
        return results
    
    def _upload_to_youtube(self, video_path: str, title: str, description: str, 
                          tags: List[str] = None) -> bool:
        """
        Upload to YouTube (placeholder implementation)
        """
        logger.info(f"Uploading to YouTube: {title}")
        # Actual implementation would use YouTube Data API
        # This is a placeholder
        return True
    
    def _upload_to_vimeo(self, video_path: str, title: str, description: str, 
                        tags: List[str] = None) -> bool:
        """
        Upload to Vimeo (placeholder implementation)
        """
        logger.info(f"Uploading to Vimeo: {title}")
        # Actual implementation would use Vimeo API
        # This is a placeholder
        return True
    
    def _upload_to_tiktok(self, video_path: str, title: str, description: str, 
                         tags: List[str] = None) -> bool:
        """
        Upload to TikTok (placeholder implementation)
        """
        logger.info(f"Uploading to TikTok: {title}")
        # Actual implementation would use TikTok API or automation
        # This is a placeholder
        return True
    
    def _upload_to_instagram(self, video_path: str, title: str, description: str, 
                            tags: List[str] = None) -> bool:
        """
        Upload to Instagram (placeholder implementation)
        """
        logger.info(f"Uploading to Instagram: {title}")
        # Actual implementation would use Instagram API or automation
        # This is a placeholder
        return True


def process_cross_platform_video(url: str, config: Dict) -> bool:
    """
    Process a video from any supported platform with the same workflow as YouTube videos
    
    Args:
        url (str): URL of the video to process
        config (dict): Configuration settings
        
    Returns:
        bool: True if successful, False otherwise
    """
    processor = MultiPlatformProcessor()
    
    # Validate URL
    if not processor.validate_url(url):
        logger.error(f"Invalid or unsupported URL: {url}")
        return False
    
    logger.info(f"Starting cross-platform processing for: {url}")
    
    # Create output directories
    os.makedirs(config['settings']['download_dir'], exist_ok=True)
    os.makedirs(config['settings']['output_dir'], exist_ok=True)
    os.makedirs(config['settings']['temp_dir'], exist_ok=True)
    
    # Extract video ID
    platform = processor.detect_platform(url)
    video_id = f"{platform}_video"  # Simplified ID for demo
    
    # Define file paths
    original_path = os.path.join(config['settings']['download_dir'], f"{video_id}_original.mp4")
    edited_path = os.path.join(config['settings']['output_dir'], f"{video_id}_edited.mp4")
    
    try:
        # Step 1: Get video info
        video_info = processor.get_video_info(url)
        if not video_info:
            logger.error("Could not extract video information")
            return False
        
        print(f"Title: {video_info['title']}")
        print(f"Uploader: {video_info['uploader']}")
        print(f"Duration: {video_info['duration']} seconds")
        
        # Step 2: Download video
        if not processor.download_video(url, original_path):
            logger.error("Failed to download video")
            return False
        
        # Step 3: Auto-edit video (using the original YouTube function)
        from youtube_enhancement_tools import auto_edit_video
        if not auto_edit_video(original_path, edited_path, config):
            logger.error("Failed to auto-edit video")
            return False
        
        logger.info(f"Cross-platform processing complete! Output saved to: {edited_path}")
        print(f"\n✓ Cross-platform processing complete! Output saved to: {edited_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error processing video {url}: {e}")
        print(f"✗ Unexpected error processing video: {e}")
        return False


# Example usage
if __name__ == "__main__":
    # Example usage of multi-platform processor
    processor = MultiPlatformProcessor()
    
    print("Supported platforms:", processor.get_supported_platforms())
    
    # Example URL validation
    test_urls = [
        "https://vimeo.com/123456789",
        "https://www.tiktok.com/@user/video/1234567890123456789",
        "https://www.instagram.com/p/Ck123abcDEF/",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ]
    
    for url in test_urls:
        platform = processor.detect_platform(url)
        is_valid = processor.validate_url(url)
        print(f"URL: {url}")
        print(f"  Detected platform: {platform}")
        print(f"  Valid: {is_valid}")
        print()
    
    # Example cross-platform uploader
    uploader = CrossPlatformUploader()
    print("Supported platforms for upload:", uploader.supported_platforms)