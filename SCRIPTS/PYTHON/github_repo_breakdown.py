#!/usr/bin/env python3
"""
GITHUB REPOSITORY BREAKDOWN
Shows exactly what goes in each of the 6 repositories
"""

import os

# Define the 6 repositories and their files
REPOSITORIES = {
    "autonomous-agents": {
        "description": "Multi-agent AI coordination system",
        "files": [
            "AI_ARMY_MANAGER.py",
            "AUTONOMOUS_SALESMAN.py",
            "JANITOR_AGENT.py",
            "SYNTHETIC_BRAIN_TRAINER.py",
        ],
        "target_audience": "AI developers, automation engineers",
    },
    "defi-crypto-trading": {
        "description": "DeFi yield monitoring and crypto trading",
        "files": [
            "DEFI_YIELD_MONITOR.py",
            "PROFIT_TRACKER.py",
            "NOMAD_BRIDGE_TELEGRAM.py",
        ],
        "target_audience": "Crypto traders, DeFi developers",
    },
    "ai-voice-hologram": {
        "description": "Voice AI and holographic avatar integration",
        "files": [
            "AI_VOICE_ASSISTANT.py",
            "HOLOGRAPHIC_AVATAR_BRIDGE.py",
            "OMNI_VISION_CONSCIOUSNESS.py",
        ],
        "target_audience": "Voice AI devs, AR/VR creators",
    },
    "dev-automation-tools": {
        "description": "Developer productivity and automation suite",
        "files": [
            "GITHUB_REPO_MANAGER.py",
            "AUTO_ENGINEER_LOOP.py",
            "PROJECT_INCEPTION.py",
            "master_organization_system.py",
            "automated_documentation.py",
            "maintenance_scheduler.py",
        ],
        "target_audience": "Software developers, DevOps engineers",
    },
    "security-iot-shield": {
        "description": "Security auditing, backups, and IoT integration",
        "files": [
            "RED_TEAM_DEFENDER.py",
            "IRON_VAULT_BACKUP.py",
            "security_config.py",
            "REALITY_BRIDGE_IOT.py",
        ],
        "target_audience": "Security researchers, sysadmins",
    },
    "dao-governance": {
        "description": "DAO governance toolkit",
        "files": [
            "DIGITAL_DAO_GOVERNANCE.py",
        ],
        "target_audience": "Blockchain developers, Web3 enthusiasts",
    },
}

def show_breakdown():
    """Display the repository breakdown"""
    
    print("\n" + "="*70)
    print("  GITHUB REPOSITORY BREAKDOWN")
    print("  SYSTEM_CORE → 6 Focused Repositories")
    print("="*70)
    
    total_scripts = 0
    
    for repo_name, info in REPOSITORIES.items():
        print(f"\n{'='*70}")
        print(f"  REPOSITORY: {repo_name}")
        print(f"{'='*70}")
        print(f"📝 Description: {info['description']}")
        print(f"👥 Target: {info['target_audience']}")
        print(f"\n📦 FILES ({len(info['files'])} scripts):")
        
        for i, filename in enumerate(info['files'], 1):
            print(f"   {i}. {filename}")
            total_scripts += 1
        
        print(f"\n📁 Repository Structure:")
        print(f"   github.com/karma-ai-systems/{repo_name}/")
        print(f"   ├── {info['files'][0]}")
        if len(info['files']) > 1:
            for f in info['files'][1:3]:
                print(f"   ├── {f}")
            if len(info['files']) > 3:
                print(f"   ├── ... ({len(info['files']) - 2} more)")
        print(f"   ├── README.md")
        print(f"   ├── requirements.txt")
        print(f"   ├── .gitignore")
        print(f"   └── LICENSE")
    
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total Repositories: {len(REPOSITORIES)}")
    print(f"  Total Python Scripts: {total_scripts}")
    print(f"  Average Scripts per Repo: {total_scripts / len(REPOSITORIES):.1f}")
    print(f"\n  Organization: github.com/karma-ai-systems/")
    for repo_name in REPOSITORIES.keys():
        print(f"    • {repo_name}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    show_breakdown()
