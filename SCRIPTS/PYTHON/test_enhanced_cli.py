#!/usr/bin/env python3
"""
Test script for Enhanced Charm Crush CLI
Validates all components are working correctly
"""
import subprocess
import sys
import os
from pathlib import Path
import json

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"CMD: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"PASS: {description}")
            if result.stdout:
                print(f"Output: {result.stdout[:200]}...")  # First 200 chars
            return True
        else:
            print(f"FAIL: {description}")
            print(f"Error: {result.stderr[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: {description}")
        return False
    except Exception as e:
        print(f"ERROR: {description} - {e}")
        return False

def test_imports():
    """Test Python imports"""
    print(f"\n{'='*60}")
    print("TEST: Python imports")
    print(f"{'='*60}")
    
    modules = [
        'aiohttp',
        'cryptography',
        'requests',
        'pathlib',
        'asyncio',
        'json'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"PASS: {module}")
        except ImportError:
            print(f"FAIL: {module} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def test_file_structure():
    """Test that all required files exist"""
    print(f"\n{'='*60}")
    print("TEST: File structure")
    print(f"{'='*60}")
    
    required_files = [
        'charm_crush_enhanced.py',
        'github_bulk_downloader.py',
        'disk_cleanup_tool.py',
        'repo_sync_organizer.py',
        'setup_enhanced_cli.py',
        'requirements_enhanced.txt',
        'QUICK_START.md'
    ]
    
    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"PASS: {file}")
        else:
            print(f"FAIL: {file} - MISSING")
            all_ok = False
    
    return all_ok

def test_config_files():
    """Test configuration setup"""
    print(f"\n{'='*60}")
    print("TEST: Configuration files")
    print(f"{'='*60}")
    
    config_dir = Path.home() / ".charm_crush_enhanced"
    
    if config_dir.exists():
        print(f"PASS: Config directory exists: {config_dir}")
        
        config_file = config_dir / "config.json"
        if config_file.exists():
            print(f"PASS: Config file exists")
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    print(f"  - Rate limit: {config.get('rate_limit_per_minute', 'N/A')}/min")
                    print(f"  - Budget: ${config.get('monthly_budget', 'N/A')}")
            except:
                print(f"  - Config file corrupted")
                return False
        else:
            print(f"FAIL: Config file missing")
            return False
        
        keys_file = config_dir / "keys.json"
        if keys_file.exists():
            print(f"PASS: Keys file exists")
        else:
            print(f"FAIL: Keys file missing")
            return False
        
        return True
    else:
        print(f"FAIL: Config directory missing: {config_dir}")
        print(f"  Run: python setup_enhanced_cli.py")
        return False

def test_help_commands():
    """Test that help works for all tools"""
    print(f"\n{'='*60}")
    print("TEST: Help commands")
    print(f"{'='*60}")
    
    commands = [
        "python charm_crush_enhanced.py --help",
        "python github_bulk_downloader.py --help",
        "python disk_cleanup_tool.py --help",
        "python repo_sync_organizer.py --help"
    ]
    
    all_ok = True
    for cmd in commands:
        if run_command(cmd, f"Help for {cmd.split()[1]}"):
            pass
        else:
            all_ok = False
    
    return all_ok

def test_basic_commands():
    """Test basic CLI commands"""
    print(f"\n{'='*60}")
    print("TEST: Basic CLI commands")
    print(f"{'='*60}")
    
    commands = [
        ("python charm_crush_enhanced.py status", "Status command"),
        ("python charm_crush_enhanced.py models", "Models command"),
        ("python repo_sync_organizer.py --scan-only", "Scan command"),
        ("python disk_cleanup_tool.py --dry-run", "Cleanup dry run"),
    ]
    
    all_ok = True
    for cmd, desc in commands:
        if run_command(cmd, desc):
            pass
        else:
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print("Enhanced Charm Crush CLI - Test Suite")
    print("=" * 80)
    
    tests = [
        ("Python Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Config Files", test_config_files),
        ("Help Commands", test_help_commands),
        ("Basic Commands", test_basic_commands),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{status:<10} {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Results: {sum(results.values())}/{len(results)} tests passed")
    print("=" * 80)
    
    if all(results.values()):
        print("\nALL TESTS PASSED!")
        print("\nYou're ready to use the Enhanced Charm Crush CLI!")
        print("\nQuick start:")
        print("1. python charm_crush_enhanced.py configure")
        print("2. python github_bulk_downloader.py --all --output X:/githubrepo")
        print("3. python disk_cleanup_tool.py --dry-run")
        return 0
    else:
        print("\nSOME TESTS FAILED")
        print("\nPlease check the output above and fix any issues.")
        print("\nCommon solutions:")
        print("- Run: python setup_enhanced_cli.py")
        print("- Install missing modules: pip install -r requirements_enhanced.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())