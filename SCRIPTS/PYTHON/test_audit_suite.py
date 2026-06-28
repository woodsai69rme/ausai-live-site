#!/usr/bin/env python3
"""
Comprehensive Test Suite for YouTube Enhancement Tools

This script performs comprehensive testing of all implemented YouTube enhancement tools
to validate functionality, performance, and security aspects.
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
    generate_ai_summary, process_youtube_video
)

class TestYouTubeEnhancementTools(unittest.TestCase):
    """Test suite for YouTube Enhancement Tools"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_config = {
            "api_keys": {
                "openai": "",
                "youtube": "",
                "elevenlabs": ""
            },
            "settings": {
                "download_dir": "./test_downloads/",
                "output_dir": "./test_output/",
                "temp_dir": "./test_temp/",
                "default_quality": "480p",  # Using lower quality for faster tests
                "batch_size": 2
            }
        }
        
        # Create test directories
        for dir_path in [cls.test_config['settings']['download_dir'], 
                         cls.test_config['settings']['output_dir'],
                         cls.test_config['settings']['temp_dir']]:
            os.makedirs(dir_path, exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        for dir_path in [cls.test_config['settings']['download_dir'], 
                         cls.test_config['settings']['output_dir'],
                         cls.test_config['settings']['temp_dir']]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
    
    def test_config_functions(self):
        """Test configuration loading and saving"""
        # Test save config
        save_config(self.test_config)
        self.assertTrue(os.path.exists('youtube_tools_config.json'))
        
        # Test load config
        loaded_config = load_config()
        self.assertEqual(loaded_config, self.test_config)
    
    def test_dependency_checking(self):
        """Test dependency checking functionality"""
        # This test will check if our dependency checking function works
        # without actually requiring all dependencies to be installed
        with patch('subprocess.run') as mock_run:
            # Mock successful command execution
            mock_run.return_value = MagicMock()
            mock_run.return_value.check_returncode.return_value = None
            
            result = check_dependencies()
            # The result depends on whether dependencies are actually installed
            # but the function should execute without errors
            self.assertIsInstance(result, bool)
    
    def test_extract_video_info(self):
        """Test video info extraction with a known URL pattern"""
        # Test with a mock URL (we're not actually downloading)
        mock_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # Since this requires actual yt-dlp execution, we'll mock it
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            mock_run.return_value.stdout = json.dumps({
                "title": "Test Video",
                "description": "Test Description",
                "uploader": "Test Uploader",
                "duration": 100,
                "view_count": 1000
            })
            mock_run.return_value.check_returncode.return_value = None
            
            result = extract_video_info(mock_url)
            
            self.assertEqual(result["title"], "Test Video")
            self.assertEqual(result["uploader"], "Test Uploader")
    
    def test_download_youtube_video(self):
        """Test YouTube video download functionality"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            mock_run.return_value.check_returncode.return_value = None
            
            result = download_youtube_video(
                "https://www.youtube.com/watch?v=test",
                "./test_output/test.mp4"
            )
            
            self.assertTrue(result)
            mock_run.assert_called_once()
    
    def test_auto_edit_video(self):
        """Test auto-edit functionality"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            mock_run.return_value.check_returncode.return_value = None
            
            result = auto_edit_video(
                "./test_input/test.mp4",
                "./test_output/test_edited.mp4"
            )
            
            self.assertTrue(result)
            mock_run.assert_called_once()
    
    def test_generate_ai_summary(self):
        """Test AI summary generation"""
        # This is a placeholder function, so we'll just test that it runs
        result = generate_ai_summary("Test content", "test_api_key")
        self.assertIsInstance(result, str)
        self.assertIn("AI-generated summary", result)
    
    def test_process_youtube_video(self):
        """Test complete video processing workflow"""
        # Mock all external dependencies
        with patch('subprocess.run') as mock_subprocess, \
             patch('youtube_enhancement_tools.extract_video_info') as mock_extract, \
             patch('youtube_enhancement_tools.download_youtube_video') as mock_download, \
             patch('youtube_enhancement_tools.auto_edit_video') as mock_edit:
            
            # Setup mocks
            mock_subprocess.return_value = MagicMock()
            mock_subprocess.return_value.stdout = json.dumps({
                "title": "Test Video",
                "description": "Test Description",
                "uploader": "Test Uploader",
                "duration": 100,
                "view_count": 1000
            })
            mock_subprocess.return_value.check_returncode.return_value = None
            
            mock_extract.return_value = {
                "title": "Test Video",
                "description": "Test Description",
                "uploader": "Test Uploader",
                "duration": 100,
                "view_count": 1000
            }
            
            mock_download.return_value = True
            mock_edit.return_value = True
            
            result = process_youtube_video(
                "https://www.youtube.com/watch?v=test",
                self.test_config
            )
            
            self.assertTrue(result)


class SecurityAudit:
    """Perform security audit of the implementation"""
    
    def __init__(self):
        self.findings = []
    
    def audit_file_permissions(self):
        """Check file permissions for sensitive files"""
        sensitive_files = ['youtube_tools_config.json', 'token.json', '.env']
        
        for file in sensitive_files:
            if os.path.exists(file):
                # On Windows, we can't easily check Unix permissions
                # but we can check if the file exists and is accessible
                try:
                    with open(file, 'r') as f:
                        # If we can read it, it's accessible
                        pass
                    print(f"✓ {file} exists and is accessible")
                except PermissionError:
                    print(f"⚠ {file} has restricted access (good for security)")
                except FileNotFoundError:
                    print(f"- {file} does not exist (may be OK)")
    
    def audit_api_key_storage(self):
        """Check how API keys are stored"""
        findings = []
        
        if os.path.exists('youtube_tools_config.json'):
            with open('youtube_tools_config.json', 'r') as f:
                try:
                    config = json.load(f)
                    if 'api_keys' in config:
                        if any(config['api_keys'].values()):
                            findings.append({
                                'severity': 'medium',
                                'issue': 'API keys found in configuration file',
                                'recommendation': 'Consider using environment variables or encrypted storage'
                            })
                        else:
                            findings.append({
                                'severity': 'info',
                                'issue': 'No API keys found in configuration file',
                                'recommendation': 'Good practice to keep keys out of config'
                            })
                except json.JSONDecodeError:
                    findings.append({
                        'severity': 'high',
                        'issue': 'Configuration file is not valid JSON',
                        'recommendation': 'Verify configuration file format'
                    })
        
        self.findings.extend(findings)
        return findings
    
    def audit_input_validation(self):
        """Check for input validation in the implementation"""
        findings = []
        
        # Read the implementation file to check for input validation
        with open('youtube_enhancement_tools.py', 'r') as f:
            content = f.read()
        
        # Check for basic input validation patterns
        if 'urllib.parse' in content and 'urlparse' in content:
            findings.append({
                'severity': 'info',
                'issue': 'URL parsing validation found',
                'recommendation': 'Good practice for URL validation'
            })
        else:
            findings.append({
                'severity': 'medium',
                'issue': 'Limited URL validation found',
                'recommendation': 'Add more comprehensive URL validation'
            })
        
        # Check for file path validation
        if 'os.path.join' in content and 'os.path.abspath' in content:
            findings.append({
                'severity': 'info',
                'issue': 'File path handling found',
                'recommendation': 'Good practice for path safety'
            })
        
        self.findings.extend(findings)
        return findings
    
    def run_complete_audit(self):
        """Run complete security audit"""
        print("Running Security Audit...")
        print("=" * 50)
        
        self.audit_file_permissions()
        print()
        
        api_key_findings = self.audit_api_key_storage()
        print("API Key Storage Audit:")
        for finding in api_key_findings:
            print(f"  {finding['severity'].upper()}: {finding['issue']}")
        print()
        
        input_validation_findings = self.audit_input_validation()
        print("Input Validation Audit:")
        for finding in input_validation_findings:
            print(f"  {finding['severity'].upper()}: {finding['issue']}")
        print()
        
        print("Security Audit Complete")
        print("=" * 50)
        
        return self.findings


class PerformanceTest:
    """Performance testing for the tools"""
    
    def __init__(self):
        self.results = {}
    
    def test_config_operations(self):
        """Test performance of config operations"""
        print("Testing configuration operations performance...")
        
        start_time = time.time()
        for i in range(100):
            save_config({"test": f"value_{i}"})
            load_config()
        end_time = time.time()
        
        elapsed = end_time - start_time
        self.results['config_operations'] = {
            'time': elapsed,
            'operations': 200,  # 100 saves + 100 loads
            'rate': 200 / elapsed if elapsed > 0 else float('inf')
        }
        
        print(f"  Completed 200 config operations in {elapsed:.4f}s ({self.results['config_operations']['rate']:.2f} ops/sec)")
    
    def run_all_performance_tests(self):
        """Run all performance tests"""
        print("Running Performance Tests...")
        print("=" * 50)
        
        self.test_config_operations()
        
        print("\nPerformance Tests Complete")
        print("=" * 50)
        
        return self.results


def run_comprehensive_tests():
    """Run all tests and audits"""
    print("Starting Comprehensive Test Suite for YouTube Enhancement Tools")
    print("=" * 70)
    
    # Run unit tests
    print("Running Unit Tests...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestYouTubeEnhancementTools)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nUnit Tests Result: {result.testsRun} tests run")
    if result.failures:
        print(f"Failures: {len(result.failures)}")
    if result.errors:
        print(f"Errors: {len(result.errors)}")
    
    # Run security audit
    security_audit = SecurityAudit()
    security_findings = security_audit.run_complete_audit()
    
    # Run performance tests
    perf_test = PerformanceTest()
    perf_results = perf_test.run_all_performance_tests()
    
    # Summary
    print("\nTest Suite Summary:")
    print("=" * 30)
    print(f"Unit Tests: {result.testsRun} run, {len(result.failures)} failed, {len(result.errors)} errors")
    print(f"Security Findings: {len(security_findings)} issues identified")
    print(f"Performance Tests: {len(perf_results)} metrics collected")
    
    print("\nRecommendations:")
    if len(result.failures) > 0 or len(result.errors) > 0:
        print("- Address failing unit tests before production use")
    if any(f['severity'] in ['high', 'critical'] for f in security_findings):
        print("- Address high severity security issues immediately")
    if len(security_findings) > 0:
        print("- Review and address security recommendations")
    
    print("\nOverall Assessment: Implementation is documented and structured,")
    print("but requires dependency installation and API key configuration to function fully.")


if __name__ == "__main__":
    run_comprehensive_tests()