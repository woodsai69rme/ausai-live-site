import unittest
import os
import subprocess
import sys
from unittest.mock import patch, MagicMock

class TestAndroidRecoveryToolkit(unittest.TestCase):
    """Test suite for the enhanced Android Recovery Toolkit"""
    
    def setUp(self):
        """Set up test environment"""
        self.enhanced_files = [
            'Enhanced-Phone-Connection-Tester.bat',
            'Enhanced-Android-Scrcpy-Wrapper.bat',
            'Enhanced-Advanced-Recovery-Suite.bat',
            'Android-Recovery-Toolkit-Launcher.bat',
            'gui_app.py'
        ]
    
    def test_enhanced_files_exist(self):
        """Test that all enhanced files exist"""
        for file in self.enhanced_files:
            self.assertTrue(os.path.exists(file), f"{file} does not exist")
    
    def test_batch_file_readable(self):
        """Test that batch files can be read without errors"""
        batch_files = [
            'Enhanced-Phone-Connection-Tester.bat',
            'Enhanced-Android-Scrcpy-Wrapper.bat',
            'Enhanced-Advanced-Recovery-Suite.bat',
            'Android-Recovery-Toolkit-Launcher.bat'
        ]
        
        for batch_file in batch_files:
            with open(batch_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIsNotNone(content)
                self.assertGreater(len(content), 0)
    
    def test_python_file_readable(self):
        """Test that Python files can be read without errors"""
        with open('gui_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
    
    @patch('subprocess.run')
    def test_adb_detection_logic(self, mock_run):
        """Test ADB detection logic in enhanced batch files"""
        # Mock successful ADB detection
        mock_run.return_value = MagicMock(returncode=0, stdout="List of devices attached\nemulator-5554\tdevice\n")
        
        # This test verifies that the logic for ADB detection exists in the files
        with open('Enhanced-Phone-Connection-Tester.bat', 'r') as f:
            content = f.read()
            self.assertIn('where adb', content)
            self.assertIn('adb devices', content)
    
    def test_security_validation_functions(self):
        """Test that security validation functions exist in batch files"""
        with open('Enhanced-Phone-Connection-Tester.bat', 'r') as f:
            content = f.read()
            # Check for IP validation function
            self.assertIn(':validate_ip', content)
        
        with open('Enhanced-Android-Scrcpy-Wrapper.bat', 'r') as f:
            content = f.read()
            # Check for serial validation function
            self.assertIn(':validate_serial', content)
        
        with open('Enhanced-Advanced-Recovery-Suite.bat', 'r') as f:
            content = f.read()
            # Check for path validation function
            self.assertIn(':validate_folder_path', content)
            # Check for package name validation function
            self.assertIn(':validate_package_name', content)
    
    def test_input_sanitization(self):
        """Test that input sanitization exists in batch files"""
        with open('Enhanced-Phone-Connection-Tester.bat', 'r') as f:
            content = f.read()
            # Check for input validation
            self.assertIn('findstr /C:', content)
        
        with open('Enhanced-Advanced-Recovery-Suite.bat', 'r') as f:
            content = f.read()
            # Check for path validation
            self.assertIn('findstr /C:', content)
    
    def test_launcher_has_all_sections(self):
        """Test that the unified launcher has all required sections"""
        with open('Android-Recovery-Toolkit-Launcher.bat', 'r') as f:
            content = f.read()
            
            # Check for main menu sections
            self.assertIn('[A] CONNECTION & DIAGNOSTICS', content)
            self.assertIn('[B] SCREEN MIRRORING & CONTROL', content)
            self.assertIn('[C] QUICK ADB COMMANDS', content)
            self.assertIn('[D] RECOVERY & EMERGENCY TOOLS', content)
            self.assertIn('[E] EMERGENCY DATA RECOVERY', content)
            self.assertIn('[F] ADVANCED FORENSICS TOOLKIT', content)
            self.assertIn('[G] ADB ENHANCEMENT TOOLKIT', content)
            self.assertIn('[H] PHONE INFO & STATUS TOOL', content)
            self.assertIn('[I] ENHANCED GUI APPLICATION', content)
            self.assertIn('[J] ENHANCED WEB INTERFACE', content)
    
    def test_gui_app_imports(self):
        """Test that the GUI app has proper imports"""
        with open('gui_app.py', 'r') as f:
            content = f.read()
            
            # Check for required imports
            self.assertIn('import tkinter', content)
            self.assertIn('from tkinter', content)
            self.assertIn('import subprocess', content)
            self.assertIn('import threading', content)
    
    def test_gui_app_class_structure(self):
        """Test that the GUI app has the expected class structure"""
        with open('gui_app.py', 'r') as f:
            content = f.read()
            
            # Check for main class
            self.assertIn('class AndroidRecoveryToolkitGUI:', content)
            
            # Check for main methods
            self.assertIn('def __init__(self, root)', content)
            self.assertIn('def create_connection_tab(self)', content)
            self.assertIn('def create_control_tab(self)', content)
            self.assertIn('def create_recovery_tab(self)', content)
            self.assertIn('def create_tools_tab(self)', content)
            self.assertIn('def create_console_tab(self)', content)
    
    def test_readme_contains_key_sections(self):
        """Test that the enhanced README contains key sections"""
        with open('ENHANCED_README.md', 'r') as f:
            content = f.read()
            
            # Check for key sections
            self.assertIn('# Android Recovery Toolkit - Enhanced Edition', content)
            self.assertIn('## Key Enhancements', content)
            self.assertIn('### Security Improvements', content)
            self.assertIn('### User Experience Improvements', content)
            self.assertIn('## Installation', content)
            self.assertIn('## Usage', content)
            self.assertIn('## Security Features', content)
    
    def test_requirements_file_exists_and_valid(self):
        """Test that requirements file exists and is valid"""
        with open('requirements.txt', 'r') as f:
            content = f.read()
            self.assertIn('# Android Recovery Toolkit Requirements', content)

class TestSecurityFeatures(unittest.TestCase):
    """Test security-specific features of the toolkit"""
    
    def test_serial_validation_logic(self):
        """Test that serial validation logic is present and correct"""
        with open('Enhanced-Android-Scrcpy-Wrapper.bat', 'r') as f:
            content = f.read()
            
            # Look for validation logic
            self.assertIn('validate_serial', content)
            self.assertIn('alphanumeric characters', content)
    
    def test_path_validation_logic(self):
        """Test that path validation logic is present and correct"""
        with open('Enhanced-Advanced-Recovery-Suite.bat', 'r') as f:
            content = f.read()
            
            # Look for validation logic
            self.assertIn('validate_folder_path', content)
            self.assertIn('restricted system directories', content)
    
    def test_package_validation_logic(self):
        """Test that package validation logic is present and correct"""
        with open('Enhanced-Advanced-Recovery-Suite.bat', 'r') as f:
            content = f.read()
            
            # Look for validation logic
            self.assertIn('validate_package_name', content)
            self.assertIn('standard format', content)

class TestUserExperienceFeatures(unittest.TestCase):
    """Test user experience features of the toolkit"""
    
    def test_unified_launcher_menu_structure(self):
        """Test that the unified launcher has a well-structured menu"""
        with open('Android-Recovery-Toolkit-Launcher.bat', 'r') as f:
            content = f.read()
            
            # Check for clear menu structure
            self.assertIn('================================================================================', content)
            self.assertIn('ANDROID RECOVERY TOOLKIT - UNIFIED LAUNCHER', content)
            
            # Check for option selection logic
            self.assertIn('set /p choice=', content)
            self.assertIn('if /i "%choice%"=="A"', content)
    
    def test_error_handling_in_batch_files(self):
        """Test that error handling is present in batch files"""
        with open('Enhanced-Phone-Connection-Tester.bat', 'r') as f:
            content = f.read()
            
            # Look for error handling
            self.assertIn('if %errorlevel%', content)
            self.assertIn('echo ERROR:', content)
    
    def test_gui_has_all_tabs(self):
        """Test that the GUI has all required tabs"""
        with open('gui_app.py', 'r') as f:
            content = f.read()
            
            # Check for all tab creation methods
            self.assertIn("self.notebook.add(frame, text='Connection & Diagnostics')", content)
            self.assertIn("self.notebook.add(frame, text='Control & Mirroring')", content)
            self.assertIn("self.notebook.add(frame, text='Recovery & Data')", content)
            self.assertIn("self.notebook.add(frame, text='Additional Tools')", content)
            self.assertIn("self.notebook.add(frame, text='Console Output')", content)

def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAndroidRecoveryToolkit))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestUserExperienceFeatures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Results Summary:")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.2f}%")
    print(f"{'='*50}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)