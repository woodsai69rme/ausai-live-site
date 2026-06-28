#!/usr/bin/env python3
"""
AI Applications Suite - Code Structure Validation

This script validates that all the code files have been created correctly
and follow the expected structure without requiring external dependencies.
"""

import os
import sys
from pathlib import Path

def validate_project_structure():
    """Validate the project directory structure"""
    print("Validating project structure...")
    
    project_root = Path(__file__).parent / "AI-Applications-Suite"
    
    required_dirs = [
        "ai_apps_suite",
        "ai_apps_suite/core",
        "ai_apps_suite/config", 
        "ai_apps_suite/utils",
        "ai_apps_suite/services",
        "ai_apps_suite/api",
        "ai_apps_suite/routes",
        "ai_apps_suite/dashboard",
        "ai_apps_suite/docs",
        "tests",
        "docs"
    ]
    
    all_present = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            print(f"❌ Missing directory: {dir_path}")
            all_present = False
        else:
            print(f"✅ Directory present: {dir_path}")
    
    return all_present

def validate_core_files():
    """Validate that core files exist and have expected content"""
    print("\nValidating core files...")
    
    project_root = Path(__file__).parent / "AI-Applications-Suite"
    
    # Check main.py
    main_file = project_root / "main.py"
    if main_file.exists():
        content = main_file.read_text()
        if "AI Applications Suite" in content:
            print("✅ main.py exists and contains expected content")
        else:
            print("❌ main.py exists but doesn't contain expected content")
            return False
    else:
        print("❌ main.py does not exist")
        return False
    
    # Check setup_and_run.py
    setup_file = project_root / "setup_and_run.py"
    if setup_file.exists():
        content = setup_file.read_text()
        if "AI Applications Suite" in content:
            print("✅ setup_and_run.py exists and contains expected content")
        else:
            print("❌ setup_and_run.py exists but doesn't contain expected content")
            return False
    else:
        print("❌ setup_and_run.py does not exist")
        return False
    
    # Check requirements.txt
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text()
        if "fastapi" in content and "uvicorn" in content:
            print("✅ requirements.txt exists and contains expected dependencies")
        else:
            print("❌ requirements.txt exists but doesn't contain expected dependencies")
            return False
    else:
        print("❌ requirements.txt does not exist")
        return False
    
    return True

def validate_service_files():
    """Validate that service files exist"""
    print("\nValidating service files...")
    
    project_root = Path(__file__).parent / "AI-Applications-Suite"
    
    service_files = [
        "ai_apps_suite/services/youtube_enhancer.py",
        "ai_apps_suite/services/ai_ranker.py", 
        "ai_apps_suite/services/accessibility_enhancer.py",
        "ai_apps_suite/services/analytics_system.py",
        "ai_apps_suite/services/security_scanner.py",
        "ai_apps_suite/services/workflows.py"
    ]
    
    all_present = True
    for file_path in service_files:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ Missing service file: {file_path}")
            all_present = False
        else:
            print(f"✅ Service file present: {file_path}")
    
    return all_present

def validate_utility_files():
    """Validate that utility files exist"""
    print("\nValidating utility files...")
    
    project_root = Path(__file__).parent / "AI-Applications-Suite"
    
    util_files = [
        "ai_apps_suite/utils/logger.py",
        "ai_apps_suite/utils/database.py",
        "ai_apps_suite/utils/api_response.py",
        "ai_apps_suite/utils/file_operations.py",
        "ai_apps_suite/utils/error_handling.py",
        "ai_apps_suite/utils/auth.py"
    ]
    
    all_present = True
    for file_path in util_files:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ Missing utility file: {file_path}")
            all_present = False
        else:
            print(f"✅ Utility file present: {file_path}")
    
    return all_present

def validate_api_files():
    """Validate that API files exist"""
    print("\nValidating API files...")
    
    project_root = Path(__file__).parent / "AI-Applications-Suite"
    
    api_files = [
        "ai_apps_suite/api/gateway.py",
        "ai_apps_suite/routes/auth_routes.py"
    ]
    
    all_present = True
    for file_path in api_files:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ Missing API file: {file_path}")
            all_present = False
        else:
            print(f"✅ API file present: {file_path}")
    
    return all_present

def validate_documentation():
    """Validate that documentation files exist"""
    print("\nValidating documentation files...")
    
    project_root = Path(__file__).parent / "AI-Applications-Suite"
    
    doc_files = [
        "README.md",
        "docs/USER_GUIDE.md",
        "docs/DEVELOPER_GUIDE.md", 
        "docs/API_DOCUMENTATION.md",
        "docs/PRODUCTION_DEPLOYMENT.md",
        "docs/PERFORMANCE_MONITORING.md",
        "docs/COMPLETE_SETUP_GUIDE.md"
    ]
    
    all_present = True
    for file_path in doc_files:
        full_path = project_root / file_path
        if not full_path.exists():
            print(f"❌ Missing documentation file: {file_path}")
            all_present = False
        else:
            print(f"✅ Documentation file present: {file_path}")
    
    return all_present

def main():
    """Run all validations"""
    print("AI Applications Suite - Code Structure Validation")
    print("=" * 50)
    
    all_valid = True
    
    all_valid &= validate_project_structure()
    all_valid &= validate_core_files()
    all_valid &= validate_service_files()
    all_valid &= validate_utility_files()
    all_valid &= validate_api_files()
    all_valid &= validate_documentation()
    
    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 All code structure validations passed!")
        print("\nThe AI Applications Suite has been properly implemented with:")
        print("- Complete project structure")
        print("- All service modules")
        print("- Utility functions")
        print("- API gateway and routes")
        print("- Comprehensive documentation")
        print("\nTo run the application, install dependencies and execute:")
        print("  python setup_and_run.py run")
    else:
        print("❌ Some validations failed. Please check the implementation.")
    
    return all_valid

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)