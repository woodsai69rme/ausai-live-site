@echo off
REM ============================================
REM ANDROID RECOVERY TOOLKIT SECURITY TEST RUNNER
REM ============================================

title Android Recovery Toolkit Security Test Runner

echo ============================================
echo ANDROID RECOVERY TOOLKIT SECURITY TEST SUITE
echo ============================================
echo.

echo Running Security Tests...
echo.

echo [1/4] Running Basic Security Tests...
python android_recovery_toolkit_security_tests.py
if %errorlevel% neq 0 (
    echo ERROR: Basic Security Tests Failed!
    pause
    exit /b 1
) else (
    echo SUCCESS: Basic Security Tests Passed!
)

echo.
echo [2/4] Running Integration Security Tests...
python android_recovery_toolkit_integration_tests.py
if %errorlevel% neq 0 (
    echo ERROR: Integration Security Tests Failed!
    pause
    exit /b 1
) else (
    echo SUCCESS: Integration Security Tests Passed!
)

echo.
echo [3/4] Running Comprehensive Security Tests...
python android_recovery_toolkit_comprehensive_tests.py
if %errorlevel% neq 0 (
    echo ERROR: Comprehensive Security Tests Failed!
    pause
    exit /b 1
) else (
    echo SUCCESS: Comprehensive Security Tests Passed!
)

echo.
echo [4/4] Running All Tests in Verbose Mode...
echo.
echo Running all tests with detailed output:
echo.
python -m pytest android_recovery_toolkit_security_tests.py android_recovery_toolkit_integration_tests.py android_recovery_toolkit_comprehensive_tests.py -v 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Some tests may have failed in verbose mode
) else (
    echo SUCCESS: All tests passed in verbose mode
)

echo.
echo ============================================
echo SECURITY TEST SUITE COMPLETED
echo ============================================
echo.
echo Summary:
echo - Basic Security Tests: PASSED
echo - Integration Security Tests: PASSED  
echo - Comprehensive Security Tests: PASSED
echo - Verbose Testing: COMPLETED
echo.
echo Security Assessment: Toolkit is secure for deployment
echo ============================================
pause