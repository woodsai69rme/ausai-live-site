#!/usr/bin/env python3
"""
Test runner for YouTube Enhancement Tools
Executes comprehensive test suite with coverage reporting
"""

import unittest
import sys
import os
import subprocess
from pathlib import Path

def run_existing_tests():
    """Run the existing test suite"""
    print("Running existing tests...")
    try:
        # Discover and run existing tests
        loader = unittest.TestLoader()
        start_dir = 'tests'
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        print(f"\nExisting tests - Ran: {result.testsRun}, Failures: {len(result.failures)}, Errors: {len(result.errors)}")
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running existing tests: {e}")
        return False

def run_improved_tests():
    """Run the improved test suite"""
    print("\nRunning improved tests...")
    try:
        # Import and run the improved test suite
        from improved_youtube_enhancement_tests import (
            TestSecurity,
            TestEdgeCases,
            TestErrorHandling,
            TestPerformance,
            TestIntegration,
            TestAPIKeyManagement,
            TestCopyrightCompliance,
            TestBatchProcessing,
            TestProgressTracking
        )
        
        # Create test suites
        loader = unittest.TestLoader()
        
        security_suite = loader.loadTestsFromTestCase(TestSecurity)
        edge_case_suite = loader.loadTestsFromTestCase(TestEdgeCases)
        error_handling_suite = loader.loadTestsFromTestCase(TestErrorHandling)
        performance_suite = loader.loadTestsFromTestCase(TestPerformance)
        integration_suite = loader.loadTestsFromTestCase(TestIntegration)
        api_suite = loader.loadTestsFromTestCase(TestAPIKeyManagement)
        copyright_suite = loader.loadTestsFromTestCase(TestCopyrightCompliance)
        batch_suite = loader.loadTestsFromTestCase(TestBatchProcessing)
        progress_suite = loader.loadTestsFromTestCase(TestProgressTracking)
        
        # Combine all suites
        comprehensive_suite = unittest.TestSuite([
            security_suite,
            edge_case_suite,
            error_handling_suite,
            performance_suite,
            integration_suite,
            api_suite,
            copyright_suite,
            batch_suite,
            progress_suite
        ])
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(comprehensive_suite)
        
        print(f"\nImproved tests - Ran: {result.testsRun}, Failures: {len(result.failures)}, Errors: {len(result.errors)}")
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running improved tests: {e}")
        return False

def run_coverage_analysis():
    """Run coverage analysis if coverage is installed"""
    try:
        import coverage
        print("\nRunning coverage analysis...")
        
        # Initialize coverage
        cov = coverage.Coverage(source=['youtube_enhancement_tools'])
        cov.start()
        
        # Run tests to collect coverage data
        run_improved_tests()
        
        cov.stop()
        cov.save()
        
        # Report coverage
        print("\nCoverage Summary:")
        cov.report(show_missing=True)
        
        # Generate HTML report
        cov.html_report(directory='htmlcov')
        print("HTML coverage report generated in 'htmlcov' directory")
        
    except ImportError:
        print("\nCoverage module not found. Install with: pip install coverage")
    except Exception as e:
        print(f"Error during coverage analysis: {e}")

def main():
    """Main test runner function"""
    print("="*60)
    print("YouTube Enhancement Tools - Comprehensive Test Suite")
    print("="*60)
    
    # Change to the script's directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Run existing tests
    existing_success = run_existing_tests()
    
    # Run improved tests
    improved_success = run_improved_tests()
    
    # Run coverage analysis
    run_coverage_analysis()
    
    # Summary
    print("\n" + "="*60)
    print("TEST RUNNER SUMMARY")
    print("="*60)
    print(f"Existing tests passed: {'✓' if existing_success else '✗'}")
    print(f"Improved tests passed: {'✓' if improved_success else '✗'}")
    
    if existing_success and improved_success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())