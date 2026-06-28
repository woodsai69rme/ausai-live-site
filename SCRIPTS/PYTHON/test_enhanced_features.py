#!/usr/bin/env python3
"""
Enhanced Test Suite for YouTube Enhancement Tools

This script performs comprehensive testing of all implemented YouTube enhancement tools
with focus on the new security and logging features.
"""

import os
import sys
import subprocess
import json
import unittest
import tempfile
from pathlib import Path
import time
from unittest.mock import patch, MagicMock

# Import our main implementation
sys.path.append('.')
from youtube_enhancement_tools import (
    load_config, save_config, check_dependencies,
    download_youtube_video, auto_edit_video, extract_video_info,
    generate_ai_summary, process_youtube_video, validate_youtube_url,
    extract_video_id_from_url, YouTubeToolError, DownloadError
)

class TestSecurityFeatures(unittest.TestCase):
    """Test security enhancements"""

    def test_url_validation_security(self):
        """Test that security checks work for URL validation"""
        # Valid URLs should pass
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(validate_youtube_url(url))

        # Suspicious URLs should fail
        suspicious_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ../../../etc/passwd",
            "https://www.youtube.com/watch?v=<script>alert('xss')</script>",
            "https://www.youtube.com/watch?v=data:text/html,<script>alert('xss')</script>",
            "https://www.youtube.com/watch?v=javascript:alert('xss')",
            "https://not-youtube.com/watch?v=test"  # Invalid domain
        ]
        
        for url in suspicious_urls:
            with self.subTest(url=url):
                self.assertFalse(validate_youtube_url(url))

    def test_extremely_long_url(self):
        """Test that extremely long URLs are rejected"""
        long_url = "https://www.youtube.com/watch?v=" + "a" * 3000  # Much longer than 2048
        self.assertFalse(validate_youtube_url(long_url))


class TestEnhancedFunctions(unittest.TestCase):
    """Test enhanced functions with better error handling"""

    def test_extract_video_id_from_url(self):
        """Test video ID extraction from various URL formats"""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                result = extract_video_id_from_url(url)
                self.assertEqual(result, expected_id)

    def test_download_youtube_video_error_handling(self):
        """Test that download function raises proper exceptions"""
        with patch('youtube_enhancement_tools.validate_youtube_url') as mock_validate:
            mock_validate.return_value = False  # Simulate invalid URL
            
            with self.assertRaises(ValueError):
                download_youtube_video("invalid_url", "output.mp4")

    def test_download_youtube_video_quality_options(self):
        """Test that different quality options work correctly"""
        with patch('subprocess.run') as mock_run, \
             patch('youtube_enhancement_tools.validate_youtube_url') as mock_validate:
            
            mock_validate.return_value = True
            mock_run.return_value = MagicMock()
            mock_run.return_value.check_returncode.return_value = None

            # Test different quality options
            qualities = ['480p', '720p', '1080p', 'invalid']
            expected_formats = [
                'best[height<=480]',
                'best[height<=720]',
                'best[height<=1080]',
                'best'  # For invalid quality
            ]
            
            for quality, expected_format in zip(qualities, expected_formats):
                with self.subTest(quality=quality):
                    download_youtube_video("https://www.youtube.com/watch?v=test", "output.mp4", quality)
                    
                    # Check that the correct format option was used
                    args, kwargs = mock_run.call_args
                    cmd = args[0]
                    self.assertIn(expected_format, cmd)


class TestConfiguration(unittest.TestCase):
    """Test configuration functionality"""

    def setUp(self):
        """Set up test configuration"""
        self.test_config = {
            "api_keys": {
                "openai": "",
                "youtube": "",
                "elevenlabs": ""
            },
            "settings": {
                "download_dir": "./test_downloads/",
                "output_dir": "./test_output/",
                "temp_dir": "./test_temp/",
                "default_quality": "480p",
                "batch_size": 2,
                "max_retries": 3,
                "timeout_seconds": 300,
                "auto_edit_settings": {
                    "silent_threshold": 0.05,
                    "video_speed": 1.5
                }
            }
        }

    def tearDown(self):
        """Clean up test configuration file"""
        if os.path.exists('test_config.json'):
            os.remove('test_config.json')

    def test_config_save_load(self):
        """Test saving and loading configuration"""
        save_config(self.test_config)
        self.assertTrue(os.path.exists('youtube_tools_config.json'))
        
        loaded_config = load_config()
        self.assertEqual(loaded_config, self.test_config)

    def test_default_config_values(self):
        """Test that default configuration values are properly set"""
        from youtube_enhancement_tools import DEFAULT_CONFIG
        
        # Check that the new config values are present
        self.assertIn('max_retries', DEFAULT_CONFIG['settings'])
        self.assertIn('timeout_seconds', DEFAULT_CONFIG['settings'])
        self.assertIn('auto_edit_settings', DEFAULT_CONFIG['settings'])
        self.assertIn('silent_threshold', DEFAULT_CONFIG['settings']['auto_edit_settings'])
        self.assertIn('video_speed', DEFAULT_CONFIG['settings']['auto_edit_settings'])


class TestErrorHandling(unittest.TestCase):
    """Test error handling functionality"""

    def test_custom_exceptions(self):
        """Test that custom exceptions are properly defined"""
        # Test base exception
        with self.assertRaises(YouTubeToolError):
            raise YouTubeToolError("Test error")
        
        # Test derived exceptions
        with self.assertRaises(DownloadError):
            raise DownloadError("Test download error")
        
        with self.assertRaises(YouTubeToolError):
            # DownloadError should also be caught as YouTubeToolError
            raise DownloadError("Test download error")


def run_enhanced_tests():
    """Run all enhanced tests"""
    print("Starting Enhanced Test Suite for YouTube Enhancement Tools")
    print("=" * 65)

    # Create test suite
    loader = unittest.TestLoader()
    
    # Add all test cases
    security_suite = loader.loadTestsFromTestCase(TestSecurityFeatures)
    enhanced_suite = loader.loadTestsFromTestCase(TestEnhancedFunctions)
    config_suite = loader.loadTestsFromTestCase(TestConfiguration)
    error_suite = loader.loadTestsFromTestCase(TestErrorHandling)
    
    # Combine all suites
    all_tests = unittest.TestSuite([
        security_suite,
        enhanced_suite,
        config_suite,
        error_suite
    ])
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(all_tests)

    # Print summary
    print(f"\nEnhanced Test Suite Summary:")
    print("=" * 30)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, trace in result.failures:
            print(f"  {test}: {trace}")
    
    if result.errors:
        print("\nErrors:")
        for test, trace in result.errors:
            print(f"  {test}: {trace}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_enhanced_tests()
    sys.exit(0 if success else 1)