#!/usr/bin/env python3
"""
Simple test for GitHub Repository Manager
"""
import unittest
import tempfile
import shutil
from pathlib import Path
import json
from unittest.mock import Mock, patch, MagicMock

# Add the home directory to the path so we can import our modules
import sys
sys.path.insert(0, str(Path.home()))

class TestGitHubRepoManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        from GITHUB_REPO_MANAGER import GitHubRepoManager
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create a temporary config file
        self.config_file = self.temp_dir / "test_config.json"
        test_config = {
            "github_token": "fake_token",
            "base_directory": str(self.temp_dir / "repos"),
            "delay_between_downloads": 0,  # No delay for tests
            "max_retries": 1,
            "timeout": 10,
            "clone_depth": 1,
            "preserve_existing": False,
            "include_private": True,
            "include_public": True,
            "repo_filters": {
                "min_stars": 0,
                "languages": [],
                "exclude_forks": False
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        self.manager = GitHubRepoManager(str(self.config_file))
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """Test loading configuration."""
        self.assertEqual(self.manager.config["github_token"], "fake_token")
        self.assertEqual(self.manager.config["delay_between_downloads"], 0)
    
    def test_should_include_repo(self):
        """Test repository filtering logic."""
        # Test with no filters
        repo1 = {"fork": False, "stargazers_count": 10, "language": "Python"}
        self.assertTrue(self.manager._should_include_repo(repo1))
        
        # Test with exclude_forks filter
        self.manager.config["repo_filters"]["exclude_forks"] = True
        repo2 = {"fork": True, "stargazers_count": 10, "language": "Python"}
        self.assertFalse(self.manager._should_include_repo(repo2))
        
        # Test with min_stars filter
        self.manager.config["repo_filters"]["exclude_forks"] = False  # Reset
        self.manager.config["repo_filters"]["min_stars"] = 20
        self.assertFalse(self.manager._should_include_repo(repo1))  # Only has 10 stars
        
        # Test with language filter
        self.manager.config["repo_filters"]["min_stars"] = 0  # Reset
        self.manager.config["repo_filters"]["languages"] = ["Java"]
        self.assertFalse(self.manager._should_include_repo(repo1))  # Is Python, not Java
    
    @patch('subprocess.run')
    def test_clone_new_repo(self, mock_subprocess):
        """Test cloning a new repository."""
        # Mock successful git clone
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        repo_url = "https://github.com/testuser/testrepo.git"
        repo_path = self.temp_dir / "testrepo"
        
        result = self.manager._clone_new_repo(repo_url, repo_path)
        
        self.assertTrue(result)
        mock_subprocess.assert_called_once()
        # Check that the call includes the repo URL and path
        args, kwargs = mock_subprocess.call_args
        self.assertIn(str(repo_path), str(args))
        self.assertIn(repo_url, str(args))
    
    @patch('subprocess.run')
    def test_update_repo(self, mock_subprocess):
        """Test updating an existing repository."""
        # Mock successful git pull
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result
        
        repo_path = self.temp_dir / "existing_repo"
        repo_path.mkdir()  # Create directory to simulate existing repo
        
        result = self.manager._update_repo(repo_path)
        
        self.assertTrue(result)
        mock_subprocess.assert_called_once()
        # Check that the call is made in the repo directory
        args, kwargs = mock_subprocess.call_args
        self.assertIn("-C")
        self.assertIn(str(repo_path), str(args))
    
    def test_save_config(self):
        """Test saving configuration."""
        new_config = {
            "github_token": "new_token",
            "base_directory": "./new_base",
            "delay_between_downloads": 10,
            "max_retries": 3,
            "timeout": 30,
            "clone_depth": 1,
            "preserve_existing": True,
            "include_private": True,
            "include_public": True,
            "repo_filters": {
                "min_stars": 0,
                "languages": [],
                "exclude_forks": False
            }
        }
        
        self.manager.save_config(new_config)
        
        # Reload and check
        with open(self.config_file, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config["github_token"], "new_token")
        self.assertEqual(loaded_config["delay_between_downloads"], 10)


def run_tests():
    """Run all tests and return results."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nGitHub Manager Tests - Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result


if __name__ == '__main__':
    print("Running GitHub Repository Manager Tests...")
    print("="*50)
    result = run_tests()
    
    if result.wasSuccessful():
        print("\n✓ All tests passed! GitHub Manager is functioning correctly.")
    else:
        print("\n✗ Some tests failed. Please review the output above.")
    
    sys.exit(0 if result.wasSuccessful() else 1)