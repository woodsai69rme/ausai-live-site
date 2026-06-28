"""
Enhanced Command-Line Interface for YouTube Enhancement Tools
This module provides an improved CLI with better UX, progress indicators, and configuration wizards.
"""

import argparse
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import threading
import re
from urllib.parse import urlparse

# Import from the main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from youtube_enhancement_tools import (
    validate_youtube_url,
    extract_video_info,
    download_youtube_video,
    auto_edit_video,
    process_youtube_video,
    batch_process_urls,
    setup_config_interactively,
    acknowledge_tos,
    load_config,
    check_dependencies
)
from advanced_video_processing import (
    add_watermark_to_video,
    generate_thumbnail_from_video,
    add_subtitles_to_video
)
from multi_platform_support import process_cross_platform_video
from ai_content_analysis import analyze_video_content
from automation_scheduler import ContentAutomationPipeline
from performance_optimizer import optimized_processor
from enhanced_logging_monitoring import (
    advanced_logger,
    operation_tracker,
    log_application_event
)


class ProgressBar:
    """Simple progress bar for CLI"""
    
    def __init__(self, total: int, width: int = 50):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, step_description: str = ""):
        """Update the progress bar"""
        self.current += 1
        percentage = (self.current / self.total) * 100
        filled_width = int(self.width * self.current // self.total)
        bar = '█' * filled_width + '-' * (self.width - filled_width)
        
        print(f'\r|{bar}| {percentage:.1f}% {step_description}', end='', flush=True)
        
        if self.current == self.total:
            print()  # New line when complete


class CLIHelper:
    """Helper class for CLI operations"""
    
    @staticmethod
    def print_header(title: str):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f"{title:^60}")
        print("="*60)
    
    @staticmethod
    def print_success(message: str):
        """Print a success message"""
        print(f"✅ {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print an error message"""
        print(f"❌ {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Print a warning message"""
        print(f"⚠️  {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print an info message"""
        print(f"ℹ️  {message}")
    
    @staticmethod
    def get_user_confirmation(prompt: str) -> bool:
        """Get yes/no confirmation from user"""
        while True:
            response = input(f"{prompt} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")


class ConfigurationWizard:
    """Interactive configuration wizard"""
    
    def __init__(self):
        self.config_file = "youtube_tools_config.json"
        self.default_config = {
            "settings": {
                "download_dir": "./downloads/",
                "output_dir": "./output/",
                "temp_dir": "./temp/",
                "default_quality": "720p",
                "batch_size": 5,
                "max_retries": 3,
                "timeout_seconds": 300,
                "auto_edit_settings": {
                    "silent_threshold": 0.04,
                    "video_speed": 1.25
                }
            },
            "api_keys": {
                "openai": "",
                "youtube": "",
                "elevenlabs": ""
            }
        }
    
    def run_wizard(self):
        """Run the configuration wizard"""
        CLIHelper.print_header("Configuration Wizard")
        print("Let's set up your YouTube Enhancement Tools configuration.")
        print("You can always change these settings later by editing the config file.\n")
        
        config = self.default_config.copy()
        
        # Get API keys (with security warning)
        print("API Keys (leave empty if using environment variables):")
        CLIHelper.print_warning("For security, it's recommended to use environment variables instead of storing API keys in the config file.")
        
        config['api_keys']['openai'] = input("OpenAI API Key (optional): ").strip()
        config['api_keys']['youtube'] = input("YouTube API Key (optional): ").strip()
        config['api_keys']['elevenlabs'] = input("ElevenLabs API Key (optional): ").strip()
        
        print("\nDirectory Settings:")
        download_dir = input(f"Download directory (default: {config['settings']['download_dir']}): ").strip()
        if download_dir:
            config['settings']['download_dir'] = download_dir

        output_dir = input(f"Output directory (default: {config['settings']['output_dir']}): ").strip()
        if output_dir:
            config['settings']['output_dir'] = output_dir

        temp_dir = input(f"Temporary directory (default: {config['settings']['temp_dir']}): ").strip()
        if temp_dir:
            config['settings']['temp_dir'] = temp_dir
        
        print("\nProcessing Settings:")
        quality = input(f"Default quality (480p/720p/1080p, default: {config['settings']['default_quality']}): ").strip()
        if quality in ['480p', '720p', '1080p']:
            config['settings']['default_quality'] = quality
        
        # Create directories if they don't exist
        for dir_key in ['download_dir', 'output_dir', 'temp_dir']:
            dir_path = config['settings'][dir_key]
            os.makedirs(dir_path, exist_ok=True)
        
        # Save configuration
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        CLIHelper.print_success(f"Configuration saved to {self.config_file}")
        return config


class EnhancedCLI:
    """Enhanced CLI with improved UX"""
    
    def __init__(self):
        self.config = None
        self.pipeline = ContentAutomationPipeline()
    
    def setup_arg_parser(self) -> argparse.ArgumentParser:
        """Setup the argument parser with enhanced options"""
        parser = argparse.ArgumentParser(
            description="Enhanced YouTube Enhancement Tools with improved UX",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --url "https://youtube.com/watch?v=example" --enhance
  %(prog)s --batch-file urls.txt --analyze
  %(prog)s --setup
  %(prog)s --wizard
  %(prog)s --dashboard
            """
        )
        
        # Main operation modes
        parser.add_argument('--url', type=str, help='Single YouTube URL to process')
        parser.add_argument('--batch-file', type=str, help='File containing multiple URLs (one per line)')
        parser.add_argument('--setup', action='store_true', help='Run interactive setup')
        parser.add_argument('--wizard', action='store_true', help='Run configuration wizard')
        
        # Enhancement options
        enhancement_group = parser.add_argument_group('enhancement options')
        enhancement_group.add_argument('--enhance', action='store_true', help='Apply enhancements to the video')
        enhancement_group.add_argument('--watermark', type=str, help='Add watermark image to video')
        enhancement_group.add_argument('--thumbnail', action='store_true', help='Generate thumbnail')
        enhancement_group.add_argument('--analyze', action='store_true', help='Analyze content with AI')
        enhancement_group.add_argument('--auto-edit', action='store_true', help='Auto-edit video to remove silence')
        
        # Processing options
        processing_group = parser.add_argument_group('processing options')
        processing_group.add_argument('--quality', choices=['480p', '720p', '1080p'], 
                                   help='Video quality (overrides config)')
        processing_group.add_argument('--no-tos-check', action='store_true', 
                                   help='Skip Terms of Service check')
        processing_group.add_argument('--check-deps', action='store_true', 
                                   help='Check dependencies only')
        processing_group.add_argument('--dashboard', action='store_true', 
                                   help='Launch web dashboard (if available)')
        
        # Advanced options
        advanced_group = parser.add_argument_group('advanced options')
        advanced_group.add_argument('--config', type=str, default='youtube_tools_config.json',
                                  help='Configuration file path')
        
        return parser
    
    def validate_and_sanitize_url(self, url: str) -> Optional[str]:
        """Validate and sanitize URL with user feedback"""
        if not url:
            return None
        
        # Basic validation
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validate using the existing function
        if not validate_youtube_url(url):
            CLIHelper.print_error(f"Invalid YouTube URL: {url}")
            return None
        
        return url
    
    def process_single_url(self, url: str, enhance: bool = False, watermark: str = None, 
                          thumbnail: bool = False, analyze: bool = False, auto_edit: bool = False) -> bool:
        """Process a single URL with enhanced UX"""
        CLIHelper.print_header("Processing Video")
        print(f"URL: {url}")
        
        # Validate URL
        validated_url = self.validate_and_sanitize_url(url)
        if not validated_url:
            return False
        
        # Load config
        if not self.config:
            try:
                self.config = load_config()
            except Exception as e:
                CLIHelper.print_error(f"Error loading configuration: {e}")
                return False
        
        # Show video info
        print("\nFetching video information...")
        try:
            video_info = extract_video_info(validated_url)
            if video_info:
                print(f"Title: {video_info['title']}")
                print(f"Uploader: {video_info['uploader']}")
                print(f"Duration: {video_info['duration']} seconds")
                print(f"Views: {video_info['view_count']:,}")
        except Exception as e:
            CLIHelper.print_warning(f"Could not fetch video info: {e}")
        
        # Process with progress tracking
        op_id = f"process_video_{int(time.time())}"
        operation_tracker.start_operation(
            op_id, 
            "Video Processing", 
            {"url": validated_url, "enhance": enhance}
        )
        
        try:
            # Use the enhanced processor
            success = process_youtube_video(validated_url, self.config)
            
            if success:
                CLIHelper.print_success("Video processed successfully!")
                
                # Apply enhancements if requested
                if enhance or watermark or thumbnail or analyze or auto_edit:
                    self.apply_enhancements(
                        validated_url, enhance, watermark, thumbnail, analyze, auto_edit
                    )
            else:
                CLIHelper.print_error("Video processing failed!")
                
            duration = operation_tracker.end_operation(op_id, success=success)
            log_application_event(
                "PROCESS_COMPLETE", 
                f"Processed video in {duration:.2f}s", 
                {"url": validated_url, "success": success, "duration": duration}
            )
            
            return success
            
        except Exception as e:
            operation_tracker.end_operation(op_id, success=False, result=str(e))
            CLIHelper.print_error(f"Error processing video: {e}")
            return False
    
    def apply_enhancements(self, url: str, enhance: bool, watermark: str, 
                          thumbnail: bool, analyze: bool, auto_edit: bool):
        """Apply requested enhancements to the processed video"""
        CLIHelper.print_header("Applying Enhancements")
        
        # Extract video ID to locate the processed file
        from youtube_enhancement_tools import extract_video_id_from_url
        video_id = extract_video_id_from_url(url)
        if not video_id:
            CLIHelper.print_error("Could not extract video ID for enhancements")
            return
        
        # Locate the processed video file
        output_dir = self.config['settings']['output_dir']
        processed_video_path = os.path.join(output_dir, f"{video_id}_edited.mp4")
        
        if not os.path.exists(processed_video_path):
            CLIHelper.print_error(f"Processed video not found: {processed_video_path}")
            return
        
        enhanced_video_path = processed_video_path.replace("_edited.mp4", "_enhanced.mp4")
        
        # Apply watermark if requested
        if watermark:
            CLIHelper.print_info("Adding watermark...")
            if add_watermark_to_video(processed_video_path, enhanced_video_path, watermark):
                CLIHelper.print_success("Watermark added successfully!")
                # Replace the original processed file with the enhanced one
                os.replace(enhanced_video_path, processed_video_path)
            else:
                CLIHelper.print_error("Failed to add watermark")
        
        # Generate thumbnail if requested
        if thumbnail:
            CLIHelper.print_info("Generating thumbnail...")
            thumbnail_path = processed_video_path.replace("_edited.mp4", "_thumbnail.jpg")
            if generate_thumbnail_from_video(processed_video_path, thumbnail_path):
                CLIHelper.print_success(f"Thumbnail generated: {thumbnail_path}")
            else:
                CLIHelper.print_error("Failed to generate thumbnail")
        
        # Analyze content if requested
        if analyze:
            CLIHelper.print_info("Analyzing content with AI...")
            # Get video info for analysis
            video_info = extract_video_info(url)
            if video_info:
                analysis = analyze_video_content(
                    video_info.get('title', ''),
                    video_info.get('description', ''),
                    ""  # No transcript available
                )
                CLIHelper.print_success("Content analysis completed!")
                print("\nAnalysis Results:")
                print(f"Sentiment: {analysis['sentiment_analysis']}")
                print(f"Suggestions: {analysis['content_suggestions'][:3]}...")  # Show first 3
                print(f"Tags: {analysis['recommended_tags'][:5]}...")  # Show first 5
            else:
                CLIHelper.print_error("Could not analyze content - no video info available")
        
        CLIHelper.print_success("All requested enhancements applied!")
    
    def process_batch_file(self, batch_file: str, enhance: bool = False, 
                          watermark: str = None, thumbnail: bool = False, 
                          analyze: bool = False, auto_edit: bool = False) -> bool:
        """Process a batch file with enhanced UX"""
        CLIHelper.print_header("Batch Processing")
        print(f"Processing URLs from: {batch_file}")
        
        if not os.path.exists(batch_file):
            CLIHelper.print_error(f"Batch file not found: {batch_file}")
            return False
        
        # Read URLs
        try:
            with open(batch_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                CLIHelper.print_error("No URLs found in batch file")
                return False
            
            print(f"Found {len(urls)} URLs to process")
            
            # Confirm with user
            if not CLIHelper.get_user_confirmation(f"Process {len(urls)} videos?"):
                print("Batch processing cancelled.")
                return False
            
            # Process each URL with progress tracking
            progress_bar = ProgressBar(len(urls), width=40)
            successful = 0
            failed = 0
            
            for i, url in enumerate(urls, 1):
                print(f"\nProcessing {i}/{len(urls)}: {url[:50]}...")
                
                if self.process_single_url(url, enhance, watermark, thumbnail, analyze, auto_edit):
                    successful += 1
                    progress_bar.update(f"({successful}/{len(urls)} success)")
                else:
                    failed += 1
                    progress_bar.update(f"({failed} failed)")
            
            CLIHelper.print_header("Batch Processing Complete")
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")
            print(f"Total: {len(urls)}")
            
            return True
            
        except Exception as e:
            CLIHelper.print_error(f"Error reading batch file: {e}")
            return False
    
    def run_dashboard(self):
        """Placeholder for web dashboard functionality"""
        CLIHelper.print_header("Web Dashboard")
        CLIHelper.print_info("Web dashboard functionality would be launched here.")
        CLIHelper.print_info("This would provide a GUI for managing YouTube Enhancement Tools.")
        # In a real implementation, this would start a web server
        print("\nNote: Web dashboard implementation is planned for a future release.")
    
    def run_setup(self):
        """Run the setup process"""
        CLIHelper.print_header("Setup Process")
        
        # Check dependencies first
        print("Checking dependencies...")
        if not check_dependencies():
            CLIHelper.print_error("Missing dependencies. Please install them before continuing.")
            print("\nRequired dependencies:")
            print("- yt-dlp")
            print("- auto-editor")
            print("- moviepy")
            print("- openai (for AI features)")
            return False
        
        CLIHelper.print_success("All dependencies are available!")
        
        # Run configuration wizard
        wizard = ConfigurationWizard()
        self.config = wizard.run_wizard()
        
        CLIHelper.print_success("Setup completed successfully!")
        return True
    
    def run_wizard(self):
        """Run the configuration wizard"""
        wizard = ConfigurationWizard()
        self.config = wizard.run_wizard()
    
    def run_check_deps(self):
        """Check dependencies only"""
        CLIHelper.print_header("Dependency Check")
        success = check_dependencies()
        if success:
            CLIHelper.print_success("All dependencies are available!")
        else:
            CLIHelper.print_error("Some dependencies are missing!")
        return success
    
    def run(self):
        """Main run method"""
        # Setup argument parser
        parser = self.setup_arg_parser()
        args = parser.parse_args()
        
        # Setup logging
        log_application_event("CLI_START", "Enhanced CLI started", {"args": sys.argv[1:]})
        
        try:
            # Handle special commands first
            if args.setup:
                return self.run_setup()
            
            if args.wizard:
                self.run_wizard()
                return True
            
            if args.check_deps:
                return self.run_check_deps()
            
            if args.dashboard:
                self.run_dashboard()
                return True
            
            # Load config
            try:
                self.config = load_config()
            except Exception as e:
                CLIHelper.print_warning(f"Could not load configuration: {e}")
                # Try to run configuration wizard
                if CLIHelper.get_user_confirmation("Run configuration wizard now?"):
                    self.run_wizard()
                    self.config = load_config()
                else:
                    CLIHelper.print_error("Configuration is required to proceed.")
                    return False
            
            # Check Terms of Service if not skipped
            if not args.no_tos_check:
                if not acknowledge_tos():
                    CLIHelper.print_error("Terms of Service not accepted. Exiting.")
                    return False
            
            # Main processing based on arguments
            if args.url:
                return self.process_single_url(
                    args.url, 
                    enhance=args.enhance,
                    watermark=args.watermark,
                    thumbnail=args.thumbnail,
                    analyze=args.analyze,
                    auto_edit=args.auto_edit
                )
            
            elif args.batch_file:
                return self.process_batch_file(
                    args.batch_file,
                    enhance=args.enhance,
                    watermark=args.watermark,
                    thumbnail=args.thumbnail,
                    analyze=args.analyze,
                    auto_edit=args.auto_edit
                )
            
            else:
                # Show help if no arguments provided
                parser.print_help()
                return False
        
        except KeyboardInterrupt:
            CLIHelper.print_info("\nOperation interrupted by user.")
            return False
        
        except Exception as e:
            CLIHelper.print_error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main function to run the enhanced CLI"""
    cli = EnhancedCLI()
    success = cli.run()
    
    if success:
        log_application_event("CLI_SUCCESS", "Enhanced CLI completed successfully")
    else:
        log_application_event("CLI_ERROR", "Enhanced CLI completed with errors")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()