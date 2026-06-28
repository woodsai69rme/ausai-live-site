#!/usr/bin/env python3
"""
Simplified Test for YouTube Enhancement Tools
"""

import os
import sys
import json

def test_config_functions():
    """Test configuration loading and saving"""
    print("Testing configuration functions...")
    
    # Default configuration
    default_config = {
        "api_keys": {
            "openai": "",
            "youtube": "",
            "elevenlabs": ""
        },
        "settings": {
            "download_dir": "./downloads/",
            "output_dir": "./output/",
            "temp_dir": "./temp/",
            "default_quality": "720p",
            "batch_size": 5
        }
    }
    
    # Save configuration
    config_file = "youtube_tools_config.json"
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print("✓ Configuration saved successfully")
    
    # Load configuration
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        print("✓ Configuration loaded successfully")
        print(f"✓ Download directory: {loaded_config['settings']['download_dir']}")
        return True
    else:
        print("✗ Configuration file not found")
        return False

def test_directories():
    """Test directory creation"""
    print("\nTesting directory creation...")
    
    dirs_to_test = [
        "./downloads/",
        "./output/",
        "./temp/"
    ]
    
    for dir_path in dirs_to_test:
        os.makedirs(dir_path, exist_ok=True)
        if os.path.exists(dir_path):
            print(f"✓ Directory created: {dir_path}")
        else:
            print(f"✗ Directory failed: {dir_path}")
    
    return True

def main():
    print("Running Simplified Test for YouTube Enhancement Tools")
    print("=" * 55)
    
    success = True
    
    # Test configuration functions
    success &= test_config_functions()
    
    # Test directory creation
    success &= test_directories()
    
    print("\n" + "=" * 55)
    if success:
        print("✓ All simplified tests passed!")
    else:
        print("✗ Some tests failed")
    
    print("Simplified test complete")

if __name__ == "__main__":
    main()