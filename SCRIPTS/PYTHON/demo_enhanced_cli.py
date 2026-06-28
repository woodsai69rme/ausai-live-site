#!/usr/bin/env python3
"""
Demo script for Enhanced Charm Crush CLI
Shows off all the new features and capabilities
"""
import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

def demo_cli_features():
    """Demonstrate the enhanced CLI features"""
    print("Enhanced Charm Crush CLI Demo")
    print("=" * 50)
    
    print("\nAvailable Commands:")
    print("-" * 30)
    
    commands = [
        ("configure", "Setup API keys and preferences"),
        ("status", "Show system status and costs"),
        ("chat", "Interactive AI chat"),
        ("code", "Generate code from prompts"),
        ("github", "GitHub repository management"),
        ("cleanup", "Disk cleanup tools"),
        ("analyze", "File analysis and large file detection"),
        ("models", "List available AI models"),
        ("usage", "Usage statistics")
    ]
    
    for cmd, desc in commands:
        print(f"  {cmd:<12} - {desc}")
    
    print(f"\nKey Files:")
    print("-" * 30)
    
    files = [
        ("charm_crush_enhanced.py", "Main CLI with all features"),
        ("github_bulk_downloader.py", "Bulk GitHub repository downloader"),
        ("disk_cleanup_tool.py", "Intelligent disk cleanup"),
        ("repo_sync_organizer.py", "Repository sync & organizer"),
        ("setup_enhanced_cli.py", "Automatic setup script"),
        ("QUICK_START.md", "Quick start guide"),
        ("ENHANCED_CLI_README.md", "Complete documentation")
    ]
    
    for filename, desc in files:
        exists = "YES" if Path(filename).exists() else "NO"
        print(f"  {exists} {filename:<30} - {desc}")
    
    print(f"\nConfiguration:")
    print("-" * 30)
    
    config_dir = Path.home() / ".charm_crush_enhanced"
    config_files = [
        ("config.json", "Application settings"),
        ("keys.json", "Encrypted API keys"),
        ("encryption.key", "Encryption key")
    ]
    
    for filename, desc in config_files:
        filepath = config_dir / filename
        exists = "YES" if filepath.exists() else "NO"
        print(f"  {exists} {filename:<25} - {desc}")
    
    print(f"\nGitHub Repository Features:")
    print("-" * 30)
    
    github_features = [
        "Download all your repositories",
        "Download starred repositories", 
        "Download from organizations",
        "Sync existing repositories",
        "Find and remove duplicates",
        "Export repository inventory",
        "Check for updates",
        "Organize by owner/project"
    ]
    
    for feature in github_features:
        print(f"  - {feature}")
    
    print(f"\nDisk Cleanup Features:")
    print("-" * 30)
    
    cleanup_features = [
        "Safe C:\\ and X:\\ drive cleanup",
        "Windows-specific optimizations",
        "Large file detection (>50MB, >100MB, etc.)",
        "Temporary file removal",
        "Cache cleanup",
        "Log file removal",
        "Node modules cleanup",
        "Python cache cleanup",
        "Thumbnails cleanup",
        "Dry run mode for safety"
    ]
    
    for feature in cleanup_features:
        print(f"  - {feature}")
    
    print(f"\nAI Assistant Features:")
    print("-" * 30)
    
    ai_features = [
        "OpenRouter integration (100+ AI models)",
        "Smart rate limiting with backoff",
        "Cost tracking and budget management",
        "Privacy mode with encrypted storage",
        "Interactive chat",
        "Code generation",
        "Research and analysis",
        "Code review and analysis",
        "Project scaffolding",
        "Multiple AI providers"
    ]
    
    for feature in ai_features:
        print(f"  - {feature}")
    
    print(f"\nUsage Examples:")
    print("-" * 30)
    
    examples = [
        ("python charm_crush_enhanced.py configure", "Setup the CLI"),
        ("python charm_crush_enhanced.py status", "Check system status"),
        ("python charm_crush_enhanced.py github --action download", "Download repos"),
        ("python charm_crush_enhanced.py cleanup --dry-run", "Safe cleanup"),
        ("python github_bulk_downloader.py --all --output X:/githubrepo", "Bulk download"),
        ("python repo_sync_organizer.py --base-path X:/githubrepo --sync", "Sync repos"),
        ("python disk_cleanup_tool.py --live", "Clean disk"),
        ("python disk_cleanup_tool.py --large-files --threshold 100", "Find large files")
    ]
    
    for cmd, desc in examples:
        print(f"  {cmd}")
        print(f"    => {desc}")
        print()
    
    print(f"Demo Complete!")
    print("=" * 50)
    print("Run 'python charm_crush_enhanced.py configure' to get started!")

def demo_github_features():
    """Demonstrate GitHub functionality"""
    print("\nGitHub Repository Management Demo")
    print("=" * 50)
    
    print("\nDownload Commands:")
    print("-" * 30)
    
    download_examples = [
        ("Download all your repositories:", "python github_bulk_downloader.py --all --output X:/githubrepo"),
        ("Download starred repositories:", "python github_bulk_downloader.py --starred --output X:/githubrepo"),
        ("Download from organization:", "python github_bulk_downloader.py --org microsoft --output X:/githubrepo"),
        ("List repositories first:", "python github_bulk_downloader.py --user yourusername --list-only"),
        ("Search for specific repos:", "python github_bulk_downloader.py --search 'machine learning' --language python")
    ]
    
    for desc, cmd in download_examples:
        print(f"  {desc}")
        print(f"    {cmd}")
        print()
    
    print("Sync & Organization Commands:")
    print("-" * 30)
    
    sync_examples = [
        ("Check for updates:", "python repo_sync_organizer.py --base-path X:/githubrepo --check-updates --token YOUR_TOKEN"),
        ("Sync repositories:", "python repo_sync_organizer.py --base-path X:/githubrepo --sync --token YOUR_TOKEN"),
        ("Find duplicates:", "python repo_sync_organizer.py --base-path X:/githubrepo --find-duplicates"),
        ("Remove duplicates (dry run):", "python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates --dry-run"),
        ("Remove duplicates:", "python repo_sync_organizer.py --base-path X:/githubrepo --cleanup-duplicates"),
        ("Export inventory:", "python repo_sync_organizer.py --base-path X:/githubrepo --export inventory.json"),
        ("Scan and organize:", "python repo_sync_organizer.py --base-path X:/githubrepo --scan-only")
    ]
    
    for desc, cmd in sync_examples:
        print(f"  {desc}")
        print(f"    {cmd}")
        print()

def demo_cleanup_features():
    """Demonstrate disk cleanup functionality"""
    print("\nDisk Cleanup Demo")
    print("=" * 50)
    
    print("\nCleanup Commands:")
    print("-" * 30)
    
    cleanup_examples = [
        ("Dry run (see what would be deleted):", "python disk_cleanup_tool.py --dry-run"),
        ("Live cleanup:", "python disk_cleanup_tool.py --live"),
        ("Clean specific locations:", "python disk_cleanup_tool.py --live --locations temp cache"),
        ("Windows-specific cleanup:", "python disk_cleanup_tool.py --live --windows-specific"),
        ("Clean multiple drives:", "python disk_cleanup_tool.py --live --drives C: X:"),
        ("Custom time limits:", "python disk_cleanup_tool.py --live --max-age 7"),
        ("Custom size minimums:", "python disk_cleanup_tool.py --live --min-size 50")
    ]
    
    for desc, cmd in cleanup_examples:
        print(f"  {desc}")
        print(f"    {cmd}")
        print()
    
    print("Analysis Commands:")
    print("-" * 30)
    
    analysis_examples = [
        ("Find large files:", "python disk_cleanup_tool.py --large-files --threshold 100"),
        ("Analyze specific drive:", "python disk_cleanup_tool.py --large-files --threshold 50 --drives X:"),
        ("Get drive information:", "python disk_cleanup_tool.py --analyze --drives C: X:")
    ]
    
    for desc, cmd in analysis_examples:
        print(f"  {desc}")
        print(f"    {cmd}")
        print()

def demo_ai_features():
    """Demonstrate AI functionality"""
    print("\nAI Assistant Demo")
    print("=" * 50)
    
    print("\nChat Commands:")
    print("-" * 30)
    
    chat_examples = [
        ("Interactive chat:", "python charm_crush_enhanced.py chat 'Hello, how are you?'"),
        ("Code generation:", "python charm_crush_enhanced.py code 'Create a Python function to calculate fibonacci'"),
        ("Research topic:", "python charm_crush_enhanced.py research 'Latest AI trends in 2024'"),
        ("Show available models:", "python charm_crush_enhanced.py models"),
        ("Check costs:", "python charm_crush_enhanced.py usage")
    ]
    
    for desc, cmd in chat_examples:
        print(f"  {desc}")
        print(f"    {cmd}")
        print()
    
    print("Advanced Commands:")
    print("-" * 30)
    
    advanced_examples = [
        ("Code review:", "python charm_crush_enhanced.py review --file my_code.py"),
        ("Deep analysis:", "python charm_crush_enhanced.py analyze --file my_code.py"),
        ("Project scaffolding:", "python charm_crush_enhanced.py scaffold --type react --name my-app"),
        ("Git commit assistance:", "python charm_crush_enhanced.py git-commit --message 'Add new feature'"),
        ("Show detailed status:", "python charm_crush_enhanced.py status")
    ]
    
    for desc, cmd in advanced_examples:
        print(f"  {desc}")
        print(f"    {cmd}")
        print()

def main():
    """Main demo function"""
    print("Enhanced Charm Crush CLI - Complete Feature Demo")
    print("=" * 60)
    print("This demo showcases all the new features added to the original CLI")
    print()
    
    # Run all demos
    demo_cli_features()
    demo_github_features()
    demo_cleanup_features()
    demo_ai_features()
    
    print("\nReady to Use!")
    print("=" * 60)
    print("All files are ready and configured.")
    print("Run the following command to get started:")
    print()
    print("  python charm_crush_enhanced.py configure")
    print()
    print("Then explore the individual tools:")
    print("  python github_bulk_downloader.py --help")
    print("  python disk_cleanup_tool.py --help")
    print("  python repo_sync_organizer.py --help")
    print()
    print("Happy coding!")

if __name__ == "__main__":
    main()