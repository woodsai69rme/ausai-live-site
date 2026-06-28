# AI Applications Suite - Testing and Quality Assurance Framework

## Table of Contents
1. [Overview](#overview)
2. [Testing Strategy](#testing-strategy)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [Security Testing](#security-testing)
6. [Performance Testing](#performance-testing)
7. [Regression Testing](#regression-testing)
8. [Test Automation](#test-automation)
9. [Quality Metrics](#quality-metrics)
10. [Continuous Integration](#continuous-integration)

## Overview

The AI Applications Suite testing framework ensures high quality, security, and reliability through comprehensive testing at multiple levels. This framework includes unit tests, integration tests, security tests, and performance tests to validate all aspects of the applications.

## Testing Strategy

### Test Levels
1. **Unit Tests**: Test individual components and functions
2. **Integration Tests**: Test component interactions
3. **System Tests**: Test complete application workflows
4. **Security Tests**: Test security controls and vulnerabilities
5. **Performance Tests**: Test system performance under load
6. **Regression Tests**: Ensure new changes don't break existing functionality

### Test Approaches
- **Black Box Testing**: Test functionality without knowledge of internal implementation
- **White Box Testing**: Test internal logic and code paths
- **Gray Box Testing**: Combination of black and white box testing
- **Exploratory Testing**: Manual testing to discover unexpected behaviors

## Unit Testing

### Test Structure
```python
import unittest
import tempfile
import json
from pathlib import Path

class TestSecurityUtils(unittest.TestCase):
    """Unit tests for security utilities"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary security config
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({
            "security": {
                "permissions": {
                    "allowed_commands": {
                        "windows": ["echo"],
                        "linux": ["echo"],
                        "macos": ["echo"]
                    },
                    "blocked_commands": ["rm"],
                    "allowed_directories": ["./safe_zone"],
                    "file_operation_limits": {
                        "max_file_size_mb": 10,
                        "max_read_size_kb": 100,
                        "max_command_output_kb": 2
                    }
                },
                "validation": {
                    "dangerous_patterns": [
                        "(\\.\\.\\/)+",
                        "(;|\\||`|\\\\)"
                    ],
                    "url_validation_regex": "^https://github\\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(\\.git)?/?$"
                },
                "rate_limiting": {
                    "api_calls_per_minute": 60,
                    "command_execution_per_minute": 10,
                    "file_operations_per_minute": 20
                },
                "encryption": {
                    "enabled": True,
                    "algorithm": "Fernet",
                    "key_rotation_days": 30
                },
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "audit_trail": True,
                    "sensitive_operations_only": False
                }
            }
        }, self.temp_config)
        self.temp_config.close()
        
        from security_utils import SecurityUtils
        self.security_utils = SecurityUtils(config_path=self.temp_config.name)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        import os
        os.unlink(self.temp_config.name)
    
    def test_input_validation_safe_input(self):
        """Test input validation with safe input"""
        is_valid, reason = self.security_utils.validate_input("This is a safe input")
        self.assertTrue(is_valid)
    
    def test_input_validation_dangerous_patterns(self):
        """Test input validation with dangerous patterns"""
        dangerous_inputs = [
            "../../../etc/passwd",
            "command; rm -rf /",
            "echo `rm -rf /`",
            "import os; os.system('format c:')"
        ]
        
        for dangerous_input in dangerous_inputs:
            with self.subTest(input=dangerous_input):
                is_valid, reason = self.security_utils.validate_input(dangerous_input)
                self.assertFalse(is_valid)
    
    def test_path_validation_allowed_path(self):
        """Test path validation with allowed path"""
        # Create safe zone directory
        safe_zone = Path("./safe_zone")
        safe_zone.mkdir(exist_ok=True)
        
        is_valid, path = self.security_utils.validate_path("./safe_zone/test.txt")
        self.assertTrue(is_valid)
    
    def test_path_validation_blocked_path(self):
        """Test path validation with blocked path"""
        is_valid, error = self.security_utils.validate_path("/etc/passwd")
        self.assertFalse(is_valid)
        self.assertIn("outside allowed", error.lower())

class TestRAGMemory(unittest.TestCase):
    """Unit tests for RAG Memory system"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        from enhanced_assistant import RAGMemory
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.rag_memory = RAGMemory(db_path=self.temp_db.name)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.rag_memory.close()
        import os
        os.unlink(self.temp_db.name)
    
    def test_store_and_retrieve_memory(self):
        """Test storing and retrieving memories"""
        # Store a memory
        self.rag_memory.store_memory("test_category", "test_content", {"test": "metadata"})
        
        # Retrieve memories by category
        memories = self.rag_memory.retrieve_memories("test_category")
        self.assertEqual(len(memories), 1)
        self.assertEqual(memories[0]['content'], "test_content")
        self.assertEqual(memories[0]['category'], "test_category")
        self.assertIn("test", memories[0]['metadata'])
    
    def test_search_memories(self):
        """Test searching for memories"""
        # Store multiple memories
        self.rag_memory.store_memory("cat1", "This is a test content", {})
        self.rag_memory.store_memory("cat2", "Another test content", {})
        self.rag_memory.store_memory("cat3", "Unrelated content", {})
        
        # Search for memories containing "test"
        results = self.rag_memory.search_memories("test")
        self.assertGreaterEqual(len(results), 2)  # Should find at least 2
        for result in results:
            self.assertIn("test", result['content'].lower())

if __name__ == '__main__':
    unittest.main()
```

## Integration Testing

### Component Integration Tests
```python
import unittest
import tempfile
import json
from pathlib import Path

class TestEnhancedAssistantIntegration(unittest.TestCase):
    """Integration tests for Enhanced AI Voice Assistant components"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({
            "security": {
                "permissions": {
                    "allowed_commands": {
                        "windows": ["echo"],
                        "linux": ["echo"],
                        "macos": ["echo"]
                    },
                    "blocked_commands": ["rm"],
                    "allowed_directories": ["./safe_zone"],
                    "file_operation_limits": {
                        "max_file_size_mb": 10,
                        "max_read_size_kb": 100,
                        "max_command_output_kb": 2
                    }
                },
                "validation": {
                    "dangerous_patterns": [
                        "(\\.\\.\\/)+",
                        "(;|\\||`|\\\\)"
                    ],
                    "url_validation_regex": "^https://github\\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(\\.git)?/?$"
                },
                "rate_limiting": {
                    "api_calls_per_minute": 60,
                    "command_execution_per_minute": 10,
                    "file_operations_per_minute": 20
                },
                "encryption": {
                    "enabled": True,
                    "algorithm": "Fernet",
                    "key_rotation_days": 30
                },
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "audit_trail": True,
                    "sensitive_operations_only": False
                }
            }
        }, self.temp_config)
        self.temp_config.close()
        
        # Create temporary security config for the assistant
        import os
        os.makedirs('./safe_zone', exist_ok=True)
        
        # Create assistant without API key to avoid external calls
        from enhanced_assistant import EnhancedAIVoiceAssistant
        self.assistant = EnhancedAIVoiceAssistant(api_key=None)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        if hasattr(self.assistant, 'monitor'):
            self.assistant.monitor.stop_monitoring()
        if hasattr(self.assistant, 'multimodal_memory'):
            self.assistant.multimodal_memory.close()
        self.assistant.rag_memory.close()
        import os
        import shutil
        if os.path.exists('./safe_zone'):
            shutil.rmtree('./safe_zone')
        os.unlink(self.temp_config.name)
    
    def test_language_detection_integration(self):
        """Test language detection integration with assistant"""
        from language_utils import LanguageDetector
        detector = LanguageDetector()
        detected_lang, confidence = detector.detect_language("Hello, how are you?")
        self.assertEqual(detected_lang, 'en')
        self.assertGreater(confidence, 0.1)
    
    def test_multimodal_memory_integration(self):
        """Test multimodal memory integration with assistant"""
        text_id = self.assistant.multimodal_memory.store_text(
            "This is a test for integration", 
            "integration_test"
        )
        self.assertIsInstance(text_id, int)
        
        results = self.assistant.multimodal_memory.search_content("integration")
        self.assertGreaterEqual(len(results), 1)
    
    def test_security_integration(self):
        """Test security integration with assistant"""
        is_valid, reason = self.assistant.security_utils.validate_input("Safe input")
        self.assertTrue(is_valid)
        
        is_valid, reason = self.assistant.security_utils.validate_input("Dangerous ../ input")
        self.assertFalse(is_valid)
    
    def test_command_processing_workflow(self):
        """Test complete command processing workflow"""
        # Test a simple command that doesn't require API
        result = self.assistant.process_command("what time is it")
        # The command should be processed (return True) and speak called
        self.assertIsNotNone(result)  # Should not be None

class TestSystemWorkflow(unittest.TestCase):
    """System-level integration tests"""
    
    def test_complete_github_download_workflow(self):
        """Test complete GitHub download workflow"""
        from github_downloader import GitHubRepoDownloader
        
        # Create a temporary directory for testing
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = GitHubRepoDownloader(output_dir=temp_dir)
            
            # Test URL validation
            is_valid = downloader._validate_repo_url("https://github.com/user/repo.git")
            self.assertTrue(is_valid)
            
            # Test URL sanitization
            sanitized = downloader._sanitize_repo_name("repo-name")
            self.assertEqual(sanitized, "repo-name")
    
    def test_chatgpt_sorter_workflow(self):
        """Test complete ChatGPT sorter workflow"""
        import json
        import tempfile
        
        # Create a temporary conversation file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        test_data = {
            "conversations": [
                {
                    "id": "test1",
                    "title": "Test Conversation",
                    "create_time": 1672531200,
                    "mapping": {
                        "node1": {
                            "message": {
                                "author": {"role": "user"},
                                "content": {
                                    "parts": ["Hello, world!"]
                                }
                            }
                        }
                    }
                }
            ]
        }
        json.dump(test_data, temp_file)
        temp_file.close()
        
        from chatgpt_sorter import ChatGPTSorter
        sorter = ChatGPTSorter(input_file=temp_file.name)
        
        # Test loading conversations
        success = sorter.load_conversations()
        self.assertTrue(success)
        self.assertEqual(len(sorter.conversations), 1)
        
        # Clean up
        import os
        os.unlink(temp_file.name)

if __name__ == '__main__':
    unittest.main()
```

## Security Testing

### Security Test Suite
```python
import unittest
import tempfile
import json
import subprocess
import os
from pathlib import Path

class TestSecurityControls(unittest.TestCase):
    """Security-focused tests for the AI Applications Suite"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary security config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({
            "security": {
                "permissions": {
                    "allowed_commands": {
                        "windows": ["echo", "dir"],
                        "linux": ["echo", "ls"],
                        "macos": ["echo", "ls"]
                    },
                    "blocked_commands": [
                        "rm", "del", "format", "fdisk", "chown", "chmod", "useradd", "userdel", 
                        "passwd", "shutdown", "halt", "reboot", "poweroff", "kill", "pkill", 
                        "killall", "mv", "cp", "dd", "mkfs", "mount", "umount", "crontab"
                    ],
                    "allowed_directories": ["./safe_zone"],
                    "file_operation_limits": {
                        "max_file_size_mb": 10,
                        "max_read_size_kb": 100,
                        "max_command_output_kb": 2
                    }
                },
                "validation": {
                    "dangerous_patterns": [
                        "(\\.\\.\\/)+",
                        "(;|\\||`|\\\\)",
                        "\\$\\(",
                        "eval\\s*\\(",
                        "exec\\s*\\(",
                        "import\\s+os",
                        "import\\s+subprocess",
                        "__import__",
                        "compile\\s*\\(",
                        "execfile\\s*\\("
                    ],
                    "url_validation_regex": "^https://github\\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(\\.git)?/?$"
                },
                "rate_limiting": {
                    "api_calls_per_minute": 60,
                    "command_execution_per_minute": 10,
                    "file_operations_per_minute": 20
                },
                "encryption": {
                    "enabled": True,
                    "algorithm": "Fernet",
                    "key_rotation_days": 30
                },
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "audit_trail": True,
                    "sensitive_operations_only": False
                }
            }
        }, self.temp_config)
        self.temp_config.close()
        
        from security_utils import SecurityUtils
        self.security_utils = SecurityUtils(config_path=self.temp_config.name)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        os.unlink(self.temp_config.name)
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks"""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/../../../etc/shadow",
            "./../../../secret_file.txt"
        ]
        
        for path in dangerous_paths:
            is_valid, result = self.security_utils.validate_path(path)
            self.assertFalse(is_valid, f"Path traversal should be blocked for: {path}")
            self.assertIn("outside allowed", result.lower())
    
    def test_command_injection_prevention(self):
        """Test prevention of command injection attacks"""
        dangerous_commands = [
            "echo hello; rm -rf /",
            "ping google.com || format c:",
            "ls -la && shutdown -h now",
            "dir | echo malicious > C:\\important_system_file.txt"
        ]
        
        for cmd in dangerous_commands:
            is_valid, result = self.security_utils.validate_command(cmd)
            self.assertFalse(is_valid, f"Command injection should be blocked for: {cmd}")
            self.assertIn("dangerous pattern", result.lower())
    
    def test_dangerous_input_blocking(self):
        """Test blocking of dangerous input patterns"""
        dangerous_inputs = [
            "import os; os.system('rm -rf /')",
            "eval('__import__(\"os\").system(\"format c:\")')",
            "exec(\"import subprocess; subprocess.call(['rm', '-rf', '/'])\")",
            "__import__('os').system('shutdown -h now')",
            "compile('import shutil; shutil.rmtree(\"/\")', '<string>', 'exec')"
        ]
        
        for inp in dangerous_inputs:
            is_valid, reason = self.security_utils.validate_input(inp)
            self.assertFalse(is_valid, f"Dangerous input should be blocked: {inp}")
            self.assertIn("dangerous pattern", reason.lower())
    
    def test_file_operation_limits(self):
        """Test enforcement of file operation limits"""
        # This test verifies that the configuration is loaded correctly
        limits = self.security_utils.config['security']['permissions']['file_operation_limits']
        self.assertEqual(limits['max_file_size_mb'], 10)
        self.assertEqual(limits['max_read_size_kb'], 100)
        self.assertEqual(limits['max_command_output_kb'], 2)

class TestGitHubDownloaderSecurity(unittest.TestCase):
    """Security tests for GitHub Repo Downloader"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        from github_downloader import GitHubRepoDownloader
        self.downloader = GitHubRepoDownloader(output_dir="./test_output")
        
        # Create test output directory
        os.makedirs("./test_output", exist_ok=True)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        import shutil
        if os.path.exists("./test_output"):
            shutil.rmtree("./test_output")
    
    def test_url_validation(self):
        """Test URL validation security"""
        # Valid GitHub URLs should pass
        valid_urls = [
            "https://github.com/user/repo.git",
            "https://github.com/user/repo",
            "https://github.com/user/repo/"
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                is_valid = self.downloader._validate_repo_url(url)
                self.assertTrue(is_valid)
        
        # Invalid URLs should be blocked
        invalid_urls = [
            "https://malicious-site.com/user/repo",
            "ftp://github.com/user/repo",
            "https://github.com/../etc/passwd",
            "javascript:alert('xss')"
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                is_valid = self.downloader._validate_repo_url(url)
                self.assertFalse(is_valid)
    
    def test_path_sanitization(self):
        """Test path sanitization for repo names"""
        dangerous_names = [
            "../../../etc/passwd",
            "..\\windows\\system32",
            "repo;rm -rf /",
            "repo && format c:",
            "repo`rm -rf /`"
        ]
        
        for name in dangerous_names:
            with self.subTest(name=name):
                sanitized = self.downloader._sanitize_repo_name(name)
                # Should not contain the dangerous patterns
                self.assertNotIn("../", sanitized)
                self.assertNotIn("..\\", sanitized)
                self.assertNotIn(";", sanitized)
                self.assertNotIn("&&", sanitized)
                self.assertNotIn("`", sanitized)

if __name__ == '__main__':
    unittest.main()
```

## Performance Testing

### Performance Test Suite
```python
import unittest
import time
import statistics
import tempfile
import json
from pathlib import Path

class TestPerformance(unittest.TestCase):
    """Performance tests for the AI Applications Suite"""
    
    def test_rag_memory_performance(self):
        """Test RAG memory performance"""
        from enhanced_assistant import RAGMemory
        import time
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        rag_memory = RAGMemory(db_path=temp_db.name)
        
        # Measure storage performance
        storage_times = []
        for i in range(100):
            start_time = time.perf_counter()
            rag_memory.store_memory(f"category_{i}", f"content_{i}" * 10, {"index": i})
            end_time = time.perf_counter()
            storage_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        avg_storage_time = statistics.mean(storage_times)
        print(f"Average RAG memory storage time: {avg_storage_time:.3f} ms")
        
        # Measure retrieval performance
        retrieval_times = []
        for i in range(10):
            start_time = time.perf_counter()
            results = rag_memory.retrieve_memories(f"category_{i}")
            end_time = time.perf_counter()
            retrieval_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        avg_retrieval_time = statistics.mean(retrieval_times)
        print(f"Average RAG memory retrieval time: {avg_retrieval_time:.3f} ms")
        
        # Performance should be reasonable (less than 100ms average for storage)
        self.assertLess(avg_storage_time, 100.0, "Storage performance is too slow")
        self.assertLess(avg_retrieval_time, 50.0, "Retrieval performance is too slow")
        
        rag_memory.close()
        import os
        os.unlink(temp_db.name)
    
    def test_security_validation_performance(self):
        """Test security validation performance"""
        import time
        import tempfile
        import json
        
        # Create a temporary security config file
        temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({
            "security": {
                "permissions": {
                    "allowed_commands": {
                        "windows": ["echo"],
                        "linux": ["echo"],
                        "macos": ["echo"]
                    },
                    "blocked_commands": ["rm"],
                    "allowed_directories": ["./safe_zone"],
                    "file_operation_limits": {
                        "max_file_size_mb": 10,
                        "max_read_size_kb": 100,
                        "max_command_output_kb": 2
                    }
                },
                "validation": {
                    "dangerous_patterns": [
                        "(\\.\\.\\/)+",
                        "(;|\\||`|\\\\)"
                    ],
                    "url_validation_regex": "^https://github\\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(\\.git)?/?$"
                },
                "rate_limiting": {
                    "api_calls_per_minute": 60,
                    "command_execution_per_minute": 10,
                    "file_operations_per_minute": 20
                },
                "encryption": {
                    "enabled": True,
                    "algorithm": "Fernet",
                    "key_rotation_days": 30
                },
                "logging": {
                    "enabled": True,
                    "level": "INFO",
                    "audit_trail": True,
                    "sensitive_operations_only": False
                }
            }
        }, temp_config)
        temp_config.close()
        
        from security_utils import SecurityUtils
        security_utils = SecurityUtils(config_path=temp_config.name)
        
        # Test input validation performance
        validation_times = []
        test_inputs = [
            "This is a safe input",
            "This has some ../ path traversal attempt",
            "This has ; dangerous command injection",
            "Normal input without issues"
        ]
        
        for test_input in test_inputs * 25:  # Repeat 25 times
            start_time = time.perf_counter()
            is_valid, reason = security_utils.validate_input(test_input)
            end_time = time.perf_counter()
            validation_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        avg_validation_time = statistics.mean(validation_times)
        print(f"Average input validation time: {avg_validation_time:.3f} ms")
        
        # Performance should be reasonable (less than 10ms average)
        self.assertLess(avg_validation_time, 10.0, "Input validation performance is too slow")
        
        import os
        os.unlink(temp_config.name)
    
    def test_multimodal_memory_performance(self):
        """Test multimodal memory performance"""
        from language_utils import MultimodalMemory
        import time
        
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        mm_memory = MultimodalMemory(db_path=temp_db.name)
        
        # Measure text storage performance
        storage_times = []
        for i in range(50):
            text = f"This is test text number {i} for performance benchmarking of multimodal memory."
            start_time = time.perf_counter()
            mm_memory.store_text(text, "benchmark", {"iteration": i})
            end_time = time.perf_counter()
            storage_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        avg_storage_time = statistics.mean(storage_times)
        print(f"Average multimodal memory storage time: {avg_storage_time:.3f} ms")
        
        # Measure search performance
        search_times = []
        for i in range(5):
            start_time = time.perf_counter()
            results = mm_memory.search_content("benchmark")
            end_time = time.perf_counter()
            search_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        
        avg_search_time = statistics.mean(search_times)
        print(f"Average multimodal memory search time: {avg_search_time:.3f} ms")
        
        # Performance should be reasonable
        self.assertLess(avg_storage_time, 50.0, "Multimodal storage performance is too slow")
        self.assertLess(avg_search_time, 100.0, "Multimodal search performance is too slow")
        
        mm_memory.close()
        import os
        os.unlink(temp_db.name)

if __name__ == '__main__':
    unittest.main()
```

## Test Automation

### Continuous Testing Script
```bash
#!/bin/bash

# Continuous Testing Script for AI Applications Suite

set -e

echo "Starting automated testing for AI Applications Suite..."

# Set up test environment
TEST_DIR="./test_results"
mkdir -p $TEST_DIR

# Run unit tests
echo "Running unit tests..."
python -m pytest tests/unit_tests.py -v --junitxml=$TEST_DIR/unit_test_results.xml

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/integration_tests.py -v --junitxml=$TEST_DIR/integration_test_results.xml

# Run security tests
echo "Running security tests..."
python -m pytest tests/security_tests.py -v --junitxml=$TEST_DIR/security_test_results.xml

# Run performance tests
echo "Running performance tests..."
python -m pytest tests/performance_tests.py -v --junitxml=$TEST_DIR/performance_test_results.xml

# Run coverage analysis
echo "Running coverage analysis..."
python -m pytest --cov=ai_voice_assistant --cov=github_downloader --cov=chatgpt_sorter --cov-report=html:$TEST_DIR/coverage --cov-report=term

# Run linting
echo "Running code linting..."
python -m flake8 ai_voice_assistant github_downloader chatgpt_sorter --max-line-length=120 --exclude=__pycache__,.git,__pycache__

# Run security scanning
echo "Running security scanning..."
python -m bandit -r ai_voice_assistant github_downloader chatgpt_sorter -f json -o $TEST_DIR/security_scan_results.json

# Generate test report
echo "Generating test report..."
cat << EOF > $TEST_DIR/test_report.md
# Test Report - AI Applications Suite

## Test Results Summary

### Unit Tests
- Status: $(if [ -s $TEST_DIR/unit_test_results.xml ]; then echo "Completed"; else echo "Failed"; fi)
- Results: $(grep -c 'testcase' $TEST_DIR/unit_test_results.xml 2>/dev/null || echo "0") tests

### Integration Tests
- Status: $(if [ -s $TEST_DIR/integration_test_results.xml ]; then echo "Completed"; else echo "Failed"; fi)
- Results: $(grep -c 'testcase' $TEST_DIR/integration_test_results.xml 2>/dev/null || echo "0") tests

### Security Tests
- Status: $(if [ -s $TEST_DIR/security_test_results.xml ]; then echo "Completed"; else echo "Failed"; fi)
- Results: $(grep -c 'testcase' $TEST_DIR/security_test_results.xml 2>/dev/null || echo "0") tests

### Performance Tests
- Status: $(if [ -s $TEST_DIR/performance_test_results.xml ]; then echo "Completed"; else echo "Failed"; fi)
- Results: $(grep -c 'testcase' $TEST_DIR/performance_test_results.xml 2>/dev/null || echo "0") tests

## Coverage Report
- Coverage: $(python -c "import xml.etree.ElementTree as ET; root = ET.parse('$TEST_DIR/coverage/coverage.xml').getroot(); print(f'{float(root.attrib[\"line-rate\"])*100:.2f}%') 2>/dev/null || echo 'N/A'")

## Security Scan
- Status: $(if [ -s $TEST_DIR/security_scan_results.json ]; then echo "Completed"; else echo "Failed"; fi)
- Results: $(python -c "import json; data = json.load(open('$TEST_DIR/security_scan_results.json')); print(len(data['results']))" 2>/dev/null || echo "0") issues found

EOF

echo "Testing completed. Results are available in $TEST_DIR/"
echo "Coverage report: $TEST_DIR/coverage/index.html"
echo "Test report: $TEST_DIR/test_report.md"
```

## Quality Metrics

### Quality Dashboard
```python
"""
Quality Metrics Dashboard for AI Applications Suite
"""

import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any

class QualityMetrics:
    """Collect and analyze quality metrics for the AI Applications Suite"""
    
    def __init__(self):
        self.metrics = {
            'test_coverage': 0.0,
            'security_issues': 0,
            'performance_benchmarks': {},
            'bug_reports': [],
            'user_satisfaction': 0.0,
            'uptime': 0.0
        }
    
    def load_test_results(self, test_results_path: str):
        """Load test results from JUnit XML files"""
        import xml.etree.ElementTree as ET
        
        if not os.path.exists(test_results_path):
            return
        
        tree = ET.parse(test_results_path)
        root = tree.getroot()
        
        total_tests = int(root.attrib.get('tests', 0))
        failed_tests = int(root.attrib.get('failures', 0))
        error_tests = int(root.attrib.get('errors', 0))
        
        passed_tests = total_tests - failed_tests - error_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_tests': error_tests,
            'success_rate': success_rate
        }
    
    def load_coverage_data(self, coverage_path: str):
        """Load coverage data from XML report"""
        import xml.etree.ElementTree as ET
        
        if not os.path.exists(coverage_path):
            return 0.0
        
        tree = ET.parse(coverage_path)
        root = tree.getroot()
        
        line_rate = float(root.attrib.get('line-rate', 0))
        return line_rate * 100  # Convert to percentage
    
    def load_security_scan(self, scan_path: str):
        """Load security scan results"""
        if not os.path.exists(scan_path):
            return 0
        
        with open(scan_path, 'r') as f:
            data = json.load(f)
        
        return len(data.get('results', []))
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate a comprehensive quality report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': {
                'unit_tests': self.load_test_results('./test_results/unit_test_results.xml'),
                'integration_tests': self.load_test_results('./test_results/integration_test_results.xml'),
                'security_tests': self.load_test_results('./test_results/security_test_results.xml'),
                'performance_tests': self.load_test_results('./test_results/performance_test_results.xml')
            },
            'coverage': self.load_coverage_data('./test_results/coverage/coverage.xml'),
            'security_issues': self.load_security_scan('./test_results/security_scan_results.json'),
            'recommendations': []
        }
        
        # Generate recommendations based on metrics
        if report['coverage'] < 80:
            report['recommendations'].append("Increase test coverage to at least 80%")
        
        if report['security_issues'] > 0:
            report['recommendations'].append(f"Address {report['security_issues']} security issues")
        
        # Check test success rates
        for test_type, results in report['test_results'].items():
            if results and results.get('success_rate', 100) < 95:
                report['recommendations'].append(f"Improve {test_type} success rate (currently {results['success_rate']:.2f}%)")
        
        return report
    
    def visualize_metrics(self, report: Dict[str, Any]):
        """Create visualizations for quality metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Test success rates
        test_types = []
        success_rates = []
        for test_type, results in report['test_results'].items():
            if results:
                test_types.append(test_type.replace('_', ' ').title())
                success_rates.append(results['success_rate'])
        
        axes[0, 0].bar(test_types, success_rates)
        axes[0, 0].set_title('Test Success Rates')
        axes[0, 0].set_ylabel('Success Rate (%)')
        axes[0, 0].set_ylim(0, 100)
        
        # Add value labels on bars
        for i, v in enumerate(success_rates):
            axes[0, 0].text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom')
        
        # Coverage
        axes[0, 1].pie([report['coverage'], 100 - report['coverage']], 
                      labels=[f'Covered ({report["coverage"]:.1f}%)', f'Missing ({100-report["coverage"]:.1f}%)'],
                      autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('Code Coverage')
        
        # Security issues
        axes[1, 0].bar(['Security Issues'], [report['security_issues']], color='red')
        axes[1, 0].set_title('Security Issues Found')
        axes[1, 0].set_ylabel('Number of Issues')
        
        # Recommendations count
        axes[1, 1].bar(['Recommendations'], [len(report['recommendations'])], color='orange')
        axes[1, 1].set_title('Quality Recommendations')
        axes[1, 1].set_ylabel('Number of Recommendations')
        
        plt.tight_layout()
        plt.savefig('./test_results/quality_metrics.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    # Generate quality report
    qm = QualityMetrics()
    report = qm.generate_quality_report()
    
    # Save report
    with open('./test_results/quality_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Create visualizations
    qm.visualize_metrics(report)
    
    print("Quality report generated successfully!")
    print(f"Report saved to: ./test_results/quality_report.json")
    print(f"Visualizations saved to: ./test_results/quality_metrics.png")
```

## Continuous Integration

### GitHub Actions CI/CD Pipeline
```yaml
name: AI Applications Suite CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 bandit
    
    - name: Lint with flake8
      run: |
        # stop the build if there are Python syntax errors or undefined names
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        # exit-zero treats all errors as warnings
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest tests/unit_tests.py -v
    
    - name: Run security tests
      run: |
        pytest tests/security_tests.py -v
    
    - name: Run integration tests
      run: |
        pytest tests/integration_tests.py -v
    
    - name: Run performance tests
      run: |
        pytest tests/performance_tests.py -v
    
    - name: Coverage report
      run: |
        pytest --cov=ai_voice_assistant --cov=github_downloader --cov=chatgpt_sorter --cov-report=xml
    
    - name: Security scan
      run: |
        bandit -r ai_voice_assistant github_downloader chatgpt_sorter -f json -o security_report.json
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.python-version }}
        path: |
          coverage.xml
          security_report.json

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Security Scan
      uses: github/super-linter@v4
      env:
        DEFAULT_BRANCH: main
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        VALIDATE_PYTHON_BLACK: true
        VALIDATE_PYTHON_PYLINT: true
        VALIDATE_JSON: true
        VALIDATE_YAML: true
    
    - name: Dependency Security Scan
      uses: actions/dependency-review-action@v2

  build-and-deploy:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t ai-suite/voice-assistant:latest -f ai-voice-assistant-enhanced/Dockerfile .
        docker build -t ai-suite/github-downloader:latest -f github-repo-downloader/Dockerfile .
        docker build -t ai-suite/chatgpt-sorter:latest -f chatgpt-sorter/Dockerfile .
    
    - name: Run container tests
      run: |
        docker run --rm ai-suite/voice-assistant:latest python -c "import enhanced_assistant; print('Voice assistant imported successfully')"
        docker run --rm ai-suite/github-downloader:latest python -c "import github_downloader; print('GitHub downloader imported successfully')"
        docker run --rm ai-suite/chatgpt-sorter:latest python -c "import chatgpt_sorter; print('ChatGPT sorter imported successfully')"
    
    - name: Push Docker images
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag ai-suite/voice-assistant:latest ai-suite/voice-assistant:${{ github.sha }}
        docker tag ai-suite/github-downloader:latest ai-suite/github-downloader:${{ github.sha }}
        docker tag ai-suite/chatgpt-sorter:latest ai-suite/chatgpt-sorter:${{ github.sha }}
        docker push ai-suite/voice-assistant:latest
        docker push ai-suite/github-downloader:latest
        docker push ai-suite/chatgpt-sorter:latest
        docker push ai-suite/voice-assistant:${{ github.sha }}
        docker push ai-suite/github-downloader:${{ github.sha }}
        docker push ai-suite/chatgpt-sorter:${{ github.sha }}
```

## Conclusion

This comprehensive testing and quality assurance framework ensures that the AI Applications Suite maintains high standards of quality, security, and reliability. The framework includes:

- **Unit Tests**: Comprehensive testing of individual components
- **Integration Tests**: Validation of component interactions
- **Security Tests**: Verification of security controls and vulnerability prevention
- **Performance Tests**: Assessment of system performance under various conditions
- **Test Automation**: Automated testing pipelines for continuous quality assurance
- **Quality Metrics**: Measurement and visualization of quality indicators
- **Continuous Integration**: Automated build, test, and deployment processes

The framework is designed to catch issues early in the development cycle, ensure security best practices are followed, and maintain high performance standards across all components of the AI Applications Suite.