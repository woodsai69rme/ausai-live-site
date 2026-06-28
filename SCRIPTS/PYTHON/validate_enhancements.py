#!/usr/bin/env python3
"""
Validation Tests for AI Ecosystem Enhancements
Tests all enhancement modules to ensure they work correctly
"""
import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock

# Add the home directory to the path so we can import our modules
sys.path.insert(0, str(Path.home()))

class TestAI_Ecosystem_Enhancer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        from AI_ECOSYSTEM_ENHANCER import AI_Ecosystem_Enhancer
        self.enhancer = AI_Ecosystem_Enhancer()
        
        # Create a temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        original_enhancement_dir = self.enhancer.enhancement_dir
        self.enhancer.enhancement_dir = self.temp_dir / "AI_ECOSYSTEM_ENHANCEMENTS"
        self.enhancer.enhancement_dir.mkdir(parents=True)
        
        # Update config file path
        self.enhancer.config_file = self.enhancer.enhancement_dir / "enhancements_config.json"
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """Test loading enhancement configuration."""
        # Test default config creation
        self.enhancer.config_file.unlink()  # Remove existing config
        self.enhancer.load_config()
        
        self.assertTrue(self.enhancer.config_file.exists())
        self.assertIn("auto_learning_enabled", self.enhancer.config)
        self.assertIn("performance_monitoring", self.enhancer.config)
    
    def test_add_predictive_task_assignment(self):
        """Test adding predictive task assignment enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "ai_army"
        enhancement_dir.mkdir()
        
        self.enhancer.add_predictive_task_assignment(enhancement_dir)
        
        enhancement_file = enhancement_dir / "predictive_task_assignment.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("predict_best_agent_for_task", content)
        self.assertIn("smart_assign_task", content)
    
    def test_add_performance_analytics(self):
        """Test adding performance analytics enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "ai_army"
        enhancement_dir.mkdir()
        
        self.enhancer.add_performance_analytics(enhancement_dir)
        
        enhancement_file = enhancement_dir / "performance_analytics.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("generate_performance_report", content)
        self.assertIn("visualize_performance", content)
    
    def test_add_adaptive_learning(self):
        """Test adding adaptive learning enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "ai_army"
        enhancement_dir.mkdir()
        
        self.enhancer.add_adaptive_learning(enhancement_dir)
        
        enhancement_file = enhancement_dir / "adaptive_learning.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("AdaptiveLearningSystem", content)
        self.assertIn("record_task_outcome", content)
        self.assertIn("get_agent_improvement_suggestions", content)
    
    def test_add_contextual_awareness(self):
        """Test adding contextual awareness enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "voice_assistant"
        enhancement_dir.mkdir()
        
        self.enhancer.add_contextual_awareness(enhancement_dir)
        
        enhancement_file = enhancement_dir / "contextual_awareness.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("ContextManager", content)
        self.assertIn("EnhancedVoiceAssistant", content)
        self.assertIn("infer_topic", content)
    
    def test_add_emotion_recognition(self):
        """Test adding emotion recognition enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "voice_assistant"
        enhancement_dir.mkdir()
        
        self.enhancer.add_emotion_recognition(enhancement_dir)
        
        enhancement_file = enhancement_dir / "emotion_recognition.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("EmotionRecognizer", content)
        self.assertIn("analyze_emotion", content)
        self.assertIn("SentimentIntensityAnalyzer", content)
    
    def test_add_proactive_suggestions(self):
        """Test adding proactive suggestions enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "voice_assistant"
        enhancement_dir.mkdir()
        
        self.enhancer.add_proactive_suggestions(enhancement_dir)
        
        enhancement_file = enhancement_dir / "proactive_suggestions.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("ProactiveSuggester", content)
        self.assertIn("daily_tip", content)
        self.assertIn("midday_checkin", content)
    
    def test_add_intelligent_categorization(self):
        """Test adding intelligent categorization enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "organization_system"
        enhancement_dir.mkdir()
        
        self.enhancer.add_intelligent_categorization(enhancement_dir)
        
        enhancement_file = enhancement_dir / "intelligent_categorization.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("IntelligentCategorizer", content)
        self.assertIn("categorize_documents", content)
        self.assertIn("classify_new_document", content)
    
    def test_add_automated_deduplication(self):
        """Test adding automated deduplication enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "organization_system"
        enhancement_dir.mkdir()
        
        self.enhancer.add_automated_deduplication(enhancement_dir)
        
        enhancement_file = enhancement_dir / "automated_deduplication.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("AutomatedDeduplicator", content)
        self.assertIn("calculate_hash", content)
        self.assertIn("is_duplicate", content)
    
    def test_add_trend_analysis(self):
        """Test adding trend analysis enhancement."""
        enhancement_dir = self.enhancer.enhancement_dir / "organization_system"
        enhancement_dir.mkdir()
        
        self.enhancer.add_trend_analysis(enhancement_dir)
        
        enhancement_file = enhancement_dir / "trend_analysis.py"
        self.assertTrue(enhancement_file.exists())
        
        # Check that the file contains expected content
        with open(enhancement_file, 'r') as f:
            content = f.read()
        
        self.assertIn("TrendAnalyzer", content)
        self.assertIn("analyze_document_trends", content)
        self.assertIn("visualize_trends", content)


class TestEnhancedAIArmy(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        from AI_ECOSYSTEM_ENHANCER import AI_Ecosystem_Enhancer
        self.enhancer = AI_Ecosystem_Enhancer()
        
        # Create a temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        original_enhancement_dir = self.enhancer.enhancement_dir
        self.enhancer.enhancement_dir = self.temp_dir / "AI_ECOSYSTEM_ENHANCEMENTS"
        self.enhancer.enhancement_dir.mkdir(parents=True)
        
        # Create the enhancement
        enhancement_dir = self.enhancer.enhancement_dir / "ai_army"
        enhancement_dir.mkdir()
        self.enhancer.add_predictive_task_assignment(enhancement_dir)
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)
    
    def test_predict_best_agent_for_task(self):
        """Test the predictive task assignment function."""
        # Import the function from the generated file
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "predictive_task_assignment", 
            self.enhancer.enhancement_dir / "ai_army" / "predictive_task_assignment.py"
        )
        pt_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pt_module)
        
        # Test with a research task
        best_agent = pt_module.predict_best_agent_for_task("Research the latest AI trends", [])
        self.assertIn(best_agent, ["researcher", "analyst"])  # Should pick researcher or analyst
        
        # Test with a writing task
        best_agent = pt_module.predict_best_agent_for_task("Write a blog post about AI", [])
        self.assertEqual(best_agent, "writer")
        
        # Test with a coding task
        best_agent = pt_module.predict_best_agent_for_task("Debug this Python code", [])
        self.assertEqual(best_agent, "code_assistant")


class TestEnhancedVoiceAssistant(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        from AI_ECOSYSTEM_ENHANCER import AI_Ecosystem_Enhancer
        self.enhancer = AI_Ecosystem_Enhancer()
        
        # Create a temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        original_enhancement_dir = self.enhancer.enhancement_dir
        self.enhancer.enhancement_dir = self.temp_dir / "AI_ECOSYSTEM_ENHANCEMENTS"
        self.enhancer.enhancement_dir.mkdir(parents=True)
        
        # Create the enhancement
        enhancement_dir = self.enhancer.enhancement_dir / "voice_assistant"
        enhancement_dir.mkdir()
        self.enhancer.add_contextual_awareness(enhancement_dir)
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)
    
    def test_context_manager(self):
        """Test the context manager functionality."""
        # Import the class from the generated file
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "contextual_awareness", 
            self.enhancer.enhancement_dir / "voice_assistant" / "contextual_awareness.py"
        )
        ca_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ca_module)
        
        # Test context manager
        ctx_manager = ca_module.ContextManager()
        
        # Test updating and getting context
        ctx_manager.update_context("test_key", "test_value")
        value = ctx_manager.get_context("test_key")
        self.assertEqual(value, "test_value")
        
        # Test adding to history
        ctx_manager.add_to_history("user", "Hello assistant")
        history = ctx_manager.get_recent_context()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["message"], "Hello assistant")
        
        # Test topic inference
        ctx_manager.add_to_history("assistant", "The weather is sunny today")
        topic = ctx_manager.infer_topic()
        self.assertIn(topic, ["weather", "general"])


class TestEnhancedOrganizationSystem(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        from AI_ECOSYSTEM_ENHANCER import AI_Ecosystem_Enhancer
        self.enhancer = AI_Ecosystem_Enhancer()
        
        # Create a temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        original_enhancement_dir = self.enhancer.enhancement_dir
        self.enhancer.enhancement_dir = self.temp_dir / "AI_ECOSYSTEM_ENHANCEMENTS"
        self.enhancer.enhancement_dir.mkdir(parents=True)
        
        # Create the enhancement
        enhancement_dir = self.enhancer.enhancement_dir / "organization_system"
        enhancement_dir.mkdir()
        self.enhancer.add_automated_deduplication(enhancement_dir)
    
    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)
    
    def test_automated_deduplicator(self):
        """Test the automated deduplicator functionality."""
        # Import the class from the generated file
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "automated_deduplication", 
            self.enhancer.enhancement_dir / "organization_system" / "automated_deduplication.py"
        )
        ad_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ad_module)
        
        # Test deduplicator
        deduplicator = ad_module.AutomatedDeduplicator()
        
        # Test exact duplicate detection
        is_dup, status = deduplicator.is_duplicate("This is a test string")
        self.assertFalse(is_dup)
        self.assertEqual(status, "unique")
        
        is_dup, status = deduplicator.is_duplicate("This is a test string")
        self.assertTrue(is_dup)
        self.assertEqual(status, "unique")  # Still unique but flagged as duplicate of previous


def run_enhancement_tests():
    """Run all enhancement validation tests and return results."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAI_Ecosystem_Enhancer))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedAIArmy))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedVoiceAssistant))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedOrganizationSystem))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\nEnhancement Tests - Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result


def run_original_tests():
    """Run the original ecosystem tests to ensure enhancements didn't break anything."""
    # Import and run the original test suite
    import test_ai_ecosystem
    return test_ai_ecosystem.run_tests()


def main():
    print("Running Validation Tests for AI Ecosystem Enhancements...")
    print("="*70)
    
    print("\n1. Testing Enhancement Modules...")
    enhancement_result = run_enhancement_tests()
    
    print("\n2. Testing Original Ecosystem (to ensure no regression)...")
    original_result = run_original_tests()
    
    print("\n" + "="*70)
    print("VALIDATION SUMMARY:")
    
    enhancement_success = enhancement_result.wasSuccessful()
    original_success = original_result.wasSuccessful()
    
    if enhancement_success and original_success:
        print("✓ ALL TESTS PASSED!")
        print("  - Enhancement modules are working correctly")
        print("  - Original ecosystem functionality preserved")
    elif enhancement_success and not original_success:
        print("⚠ ENHANCEMENT TESTS PASSED BUT ORIGINAL ECOSYSTEM HAS ISSUES")
        print("  - Enhancement modules are working correctly")
        print("  - Original ecosystem may have been affected")
    elif not enhancement_success and original_success:
        print("⚠ ORIGINAL ECOSYSTEM OK BUT ENHANCEMENTS HAVE ISSUES")
        print("  - Enhancement modules need attention")
        print("  - Original ecosystem functionality preserved")
    else:
        print("✗ BOTH ENHANCEMENTS AND ORIGINAL ECOSYSTEM HAVE ISSUES")
        print("  - Both need attention before deployment")
    
    print("="*70)
    
    return enhancement_success and original_success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)