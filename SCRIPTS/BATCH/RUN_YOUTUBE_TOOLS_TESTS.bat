@echo off
REM YouTube Enhancement Tools - Test Runner
REM This script runs the comprehensive test suite for YouTube Enhancement Tools

echo.
echo ================================================
echo YouTube Enhancement Tools - Test Suite Runner
echo ================================================
echo.

REM Change to the current directory
cd /d "%~dp0"

echo Starting YouTube Enhancement Tools test suite...
echo.

REM Run the improved tests directly
echo Running improved YouTube Enhancement Tools tests...
python -c "
import unittest
import sys
import os
sys.path.insert(0, os.getcwd())

try:
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

    print(f'\nImproved tests - Ran: {result.testsRun}, Failures: {len(result.failures)}, Errors: {len(result.errors)}')
    
    if result.wasSuccessful():
        print('\nImproved tests completed successfully!')
        sys.exit(0)
    else:
        print('\nImproved tests encountered errors!')
        sys.exit(1)
        
except ImportError as e:
    print(f'Import error: {e}')
    print('Make sure improved_youtube_enhancement_tests.py exists in the current directory.')
    sys.exit(1)
except Exception as e:
    print(f'Error running improved tests: {e}')
    sys.exit(1)
"

REM Check if the improved tests executed successfully
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Improved YouTube Enhancement Tools tests completed successfully!
    echo.
) else (
    echo.
    echo Improved YouTube Enhancement Tools tests encountered errors!
    echo.
)

REM Run the corrected tests
echo Running corrected YouTube Enhancement Tools tests...
python -c "
import unittest
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from corrected_youtube_enhancement_tests import (
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

    print(f'\nCorrected tests - Ran: {result.testsRun}, Failures: {len(result.failures)}, Errors: {len(result.errors)}')
    
    if result.wasSuccessful():
        print('\nCorrected tests completed successfully!')
        sys.exit(0)
    else:
        print('\nCorrected tests encountered errors!')
        sys.exit(1)
        
except ImportError as e:
    print(f'Import error: {e}')
    print('Make sure corrected_youtube_enhancement_tests.py exists in the current directory.')
    sys.exit(1)
except Exception as e:
    print(f'Error running corrected tests: {e}')
    sys.exit(1)
"

REM Check if the corrected tests executed successfully
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Corrected YouTube Enhancement Tools tests completed successfully!
    echo.
) else (
    echo.
    echo Corrected YouTube Enhancement Tools tests encountered errors!
    echo.
)

REM Display test results summary
echo.
echo ================================================
echo YouTube Enhancement Tools Test Execution Summary
echo ================================================
echo 1. Improved tests: executed inline
echo 2. Corrected tests: executed inline
echo.
echo Check the output above for detailed results.
echo.

pause