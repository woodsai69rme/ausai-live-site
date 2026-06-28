#!/usr/bin/env python3
"""
Advanced Disk Cleanup Tool for Windows
Specialized cleanup for C:/ and X:/ drives with safety features
"""
import os
import sys
import asyncio
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
import ctypes
import subprocess
import win32api
import win32con
import win32security
import re
from typing import List, Dict, Tuple, Optional
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WindowsCleanupManager:
    """Advanced Windows disk cleanup with system integration"""
    
    def __init__(self):
        self.dry_run = True
        self.max_file_age_days = 30
        self.safe_mode = True
        
        # Dangerous system paths (never delete)
        self.system_paths = {
            r"C:\\Windows\\System32",
            r"C:\\Windows\\SysWOW64", 
            r"C:\\Windows\\WinSxS",
            r"C:\\Program Files",
            r"C:\\Program Files (x86)",
            r"C:\\ProgramData",
            r"C:\\Users\\All Users",
            r"C:\\Recovery",
            r"C:\\System Volume Information"
        }
        
        # Safe cleanup locations
        self.cleanup_locations = {
            "temp": [
                Path("C:/Windows/Temp"),
                Path("C:/Users") / os.getenv("USERNAME") / "AppData/Local/Temp",
                Path("C:/Temp"),
                Path("C:/tmp")
            ],
            "cache": [
                Path("C:/Users") / os.getenv("USERNAME") / "AppData/Local/Temp",
                Path("C:/Users") / os.getenv("USERNAME") / "AppData/Local/Microsoft/Windows/INetCache",
            ],
            "logs": [
                Path("C:/Windows/Logs"),
                Path("C:/Users") / os.getenv("USERNAME") / "AppData/Local/Temp",
            ],
            "updates": [
                Path("C:/Windows/SoftwareDistribution/Download"),
                Path("C:/Windows/WinSxS/Temp"),
            ]
        }
        
        # File patterns to clean
        self.clean_patterns = {
            '*.tmp', '*.temp', '*.log', '*.cache', '*.dmp', '*.err', '*.old',
            '*.bak', '*.swp', '*.swo', '*.swn', '*.~', '*.crdownload', '*.part',
            '*.lock', '*.pid', '*.sock', '*.socket', '*.db-shm', '*.db-wal',
            '*.thumb', '*.tmp*', 'Thumbs.db', 'desktop.ini'
        }
        
        # Large file threshold
        self.large_file_threshold_mb = 100
        
        # Statistics
        self.stats = {
            'scanned_dirs': 0,
            'files_found': 0,
            'files_deleted': 0,
            'space_freed_mb': 0,
            'errors': [],
            'warnings': []
        }
    
    def is_admin(self) -> bool:
        """Check if running as administrator"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def is_system_file(self, file_path: Path) -> bool:
        """Check if file is a critical system file"""
        path_str = str(file_path).lower()
        for system_path in self.system_paths:
            if path_str.startswith(system_path.lower()):
                return True
        return False
    
    def is_file_in_use(self, file_path: Path) -> bool:
        """Check if file is currently in use"""
        try:
            # Try to open in exclusive mode
            with open(file_path, 'a') as f:
                pass
            return False
        except (PermissionError, OSError):
            return True
    
    def get_file_age_days(self, file_path: Path) -> int:
        """Get file age in days"""
        try:
            modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - modified_time
            return age.days
        except:
            return 9999
    
    def is_safe_to_delete(self, file_path: Path) -> Tuple[bool, str]:
        """Determine if file is safe to delete"""
        if not file_path.exists():
            return False, "File does not exist"
        
        if file_path.is_dir():
            # Check if directory is empty
            try:
                if not any(file_path.iterdir()):
                    return True, "Empty directory"
                return False, "Directory not empty"
            except:
                return False, "Cannot read directory"
        
        # System file check
        if self.is_system_file(file_path):
            return False, "System file"
        
        # File in use check
        if self.is_file_in_use(file_path):
            return False, "File in use"
        
        # Age check for temporary files
        file_age = self.get_file_age_days(file_path)
        temp_patterns = ['temp', 'tmp', 'cache', 'log', 'dmp', 'bak']
        is_temp_file = any(pattern in file_path.name.lower() for pattern in temp_patterns)
        
        if is_temp_file and file_age > self.max_file_age_days:
            return True, f"Old temp file ({file_age} days)"
        
        # Extension-based safety
        safe_extensions = {'.tmp', '.temp', '.log', '.cache', '.dmp', '.err', '.old', '.bak', '.swp', '.swo', '.swn', '~', '.crdownload', '.part', '.lock', '.pid', '.sock', '.socket', '.db-shm', '.db-wal'}
        if file_path.suffix.lower() in safe_extensions:
            return True, "Safe extension"
        
        # Name pattern check
        name = file_path.name.lower()
        safe_patterns = ['temp', 'tmp', 'cache', 'log', 'dmp', 'bak', '~', 'backup']
        if any(pattern in name for pattern in safe_patterns):
            return True, "Name pattern match"
        
        return False, "Unknown/sensitive file"
    
    def get_directory_size(self, directory: Path) -> Tuple[int, int]:
        """Get directory size and file count"""
        total_size = 0
        file_count = 0
        
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                        file_count += 1
                    except:
                        pass
        except:
            pass
        
        return total_size, file_count
    
    def get_drive_info(self, drive: str) -> Dict:
        """Get drive information"""
        try:
            if not drive.endswith(':\\'):
                drive = drive + ':\\'
            
            total = shutil.disk_usage(drive).total
            used = shutil.disk_usage(drive).used
            free = shutil.disk_usage(drive).free
            
            return {
                'drive': drive,
                'total_gb': round(total / (1024**3), 2),
                'used_gb': round(used / (1024**3), 2),
                'free_gb': round(free / (1024**3), 2),
                'usage_percent': round((used / total) * 100, 1)
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def scan_cleanup_locations(self, location_type: str = None) -> List[Dict]:
        """Scan cleanup locations for candidates"""
        candidates = []
        
        locations_to_scan = []
        if location_type and location_type in self.cleanup_locations:
            locations_to_scan = self.cleanup_locations[location_type]
        else:
            # Scan all locations
            for loc_list in self.cleanup_locations.values():
                locations_to_scan.extend(loc_list)
        
        for location in locations_to_scan:
            if not location.exists():
                continue
            
            logger.info(f"Scanning {location}...")
            self.stats['scanned_dirs'] += 1
            
            try:
                # Scan files
                for pattern in self.clean_patterns:
                    for file_path in location.rglob(pattern):
                        if file_path.is_file():
                            is_safe, reason = self.is_safe_to_delete(file_path)
                            if is_safe:
                                file_info = {
                                    'path': str(file_path),
                                    'size_mb': file_path.stat().st_size / (1024 * 1024),
                                    'age_days': self.get_file_age_days(file_path),
                                    'reason': reason,
                                    'type': 'file'
                                }
                                candidates.append(file_info)
                                self.stats['files_found'] += 1
                
                # Scan empty directories
                for dir_path in location.rglob('*'):
                    if dir_path.is_dir():
                        try:
                            if not any(dir_path.iterdir()):
                                candidates.append({
                                    'path': str(dir_path),
                                    'size_mb': 0,
                                    'age_days': 0,
                                    'reason': 'Empty directory',
                                    'type': 'dir'
                                })
                        except:
                            pass
            
            except Exception as e:
                logger.error(f"Error scanning {location}: {e}")
                self.stats['warnings'].append(f"Scan error {location}: {e}")
        
        return candidates
    
    def find_large_files(self, drives: List[str] = None, threshold_mb: int = 100) -> List[Dict]:
        """Find large files on specified drives"""
        if drives is None:
            drives = ['C:', 'X:']
        
        large_files = []
        
        for drive in drives:
            drive_path = Path(drive + '/')
            if not drive_path.exists():
                continue
            
            logger.info(f"Scanning {drive} for large files...")
            
            try:
                for file_path in drive_path.rglob('*'):
                    if file_path.is_file():
                        try:
                            size = file_path.stat().st_size
                            size_mb = size / (1024 * 1024)
                            if size_mb > threshold_mb:
                                # Skip if system file
                                if self.is_system_file(file_path):
                                    continue
                                
                                large_files.append({
                                    'path': str(file_path),
                                    'size_mb': round(size_mb, 2),
                                    'age_days': self.get_file_age_days(file_path),
                                    'type': 'large_file'
                                })
                        except:
                            pass
            except Exception as e:
                logger.error(f"Error scanning {drive}: {e}")
                self.stats['warnings'].append(f"Large file scan error {drive}: {e}")
        
        return sorted(large_files, key=lambda x: x['size_mb'], reverse=True)
    
    async def perform_cleanup(self, dry_run: bool = True, location_types: List[str] = None) -> Dict:
        """Perform cleanup operation"""
        self.dry_run = dry_run
        
        if dry_run:
            logger.info("DRY RUN MODE - No files will be deleted")
        
        if not self.is_admin() and not dry_run:
            logger.warning("Not running as administrator. Some files may not be accessible.")
            if not input("Continue anyway? (y/N): ").lower() == 'y':
                return {'cancelled': True}
        
        # Scan for candidates
        candidates = await self.scan_cleanup_locations()
        
        if not candidates:
            logger.info("No cleanup candidates found")
            return self.stats
        
        logger.info(f"Found {len(candidates)} cleanup candidates")
        
        # Process candidates
        for candidate in candidates:
            try:
                path = Path(candidate['path'])
                
                if dry_run:
                    self.stats['files_deleted'] += 1
                    self.stats['space_freed_mb'] += candidate['size_mb']
                    logger.info(f"[DRY RUN] Would delete: {candidate['path']} ({candidate['size_mb']:.1f} MB)")
                else:
                    if candidate['type'] == 'dir':
                        path.rmdir()
                        logger.info(f"Removed empty directory: {candidate['path']}")
                    else:
                        path.unlink()
                        logger.info(f"Deleted file: {candidate['path']} ({candidate['size_mb']:.1f} MB)")
                    
                    self.stats['files_deleted'] += 1
                    self.stats['space_freed_mb'] += candidate['size_mb']
            
            except Exception as e:
                error_msg = f"Failed to delete {candidate['path']}: {e}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
        
        self.stats['space_freed_mb'] = round(self.stats['space_freed_mb'], 2)
        return self.stats
    
    async def windows_specific_cleanup(self, dry_run: bool = True) -> Dict:
        """Perform Windows-specific cleanup operations"""
        if dry_run:
            logger.info("DRY RUN - Windows-specific cleanup")
        
        results = {
            'operations': [],
            'space_freed_mb': 0,
            'errors': []
        }
        
        # Windows Update cache cleanup
        win_update_cache = Path("C:/Windows/SoftwareDistribution/Download")
        if win_update_cache.exists():
            logger.info("Cleaning Windows Update cache...")
            if not dry_run:
                try:
                    # Stop Windows Update service first (if possible)
                    subprocess.run(['net', 'stop', 'wuauserv'], capture_output=True)
                    
                    # Clear cache
                    for item in win_update_cache.iterdir():
                        if item.is_file():
                            size = item.stat().st_size / (1024 * 1024)
                            item.unlink()
                            results['space_freed_mb'] += size
                            results['operations'].append(f"Deleted Windows Update cache: {item.name}")
                        elif item.is_dir():
                            shutil.rmtree(item)
                            results['operations'].append(f"Removed Windows Update cache folder: {item.name}")
                    
                    # Restart service
                    subprocess.run(['net', 'start', 'wuauserv'], capture_output=True)
                except Exception as e:
                    results['errors'].append(f"Windows Update cache cleanup failed: {e}")
            else:
                results['operations'].append("[DRY RUN] Would clean Windows Update cache")
        
        # Temp files in user profile
        user_temp = Path("C:/Users") / os.getenv("USERNAME") / "AppData/Local/Temp"
        if user_temp.exists():
            logger.info("Cleaning user temp folder...")
            if not dry_run:
                try:
                    for item in user_temp.iterdir():
                        if item.is_file():
                            try:
                                size = item.stat().st_size / (1024 * 1024)
                                item.unlink()
                                results['space_freed_mb'] += size
                                results['operations'].append(f"Deleted temp file: {item.name}")
                            except:
                                pass
                except Exception as e:
                    results['errors'].append(f"User temp cleanup failed: {e}")
            else:
                results['operations'].append("[DRY RUN] Would clean user temp folder")
        
        results['space_freed_mb'] = round(results['space_freed_mb'], 2)
        return results
    
    def generate_cleanup_report(self, stats: Dict, detailed: bool = False) -> str:
        """Generate formatted cleanup report"""
        report = []
        report.append("=" * 60)
        report.append("DISK CLEANUP REPORT")
        report.append("=" * 60)
        
        if stats.get('cancelled'):
            report.append("Cleanup cancelled by user")
            return "\n".join(report)
        
        report.append(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        report.append(f"Scanned directories: {stats.get('scanned_dirs', 0)}")
        report.append(f"Files found: {stats.get('files_found', 0)}")
        report.append(f"Files deleted: {stats.get('files_deleted', 0)}")
        report.append(f"Space freed: {stats.get('space_freed_mb', 0):.1f} MB")
        
        if stats.get('warnings'):
            report.append(f"\nWarnings ({len(stats['warnings'])}):")
            for warning in stats['warnings'][:5]:  # Show first 5
                report.append(f"  - {warning}")
        
        if stats.get('errors'):
            report.append(f"\nErrors ({len(stats['errors'])}):")
            for error in stats['errors'][:5]:  # Show first 5
                report.append(f"  - {error}")
        
        report.append("=" * 60)
        return "\n".join(report)

# CLI interface
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Windows Disk Cleanup Tool")
    parser.add_argument('--dry-run', action='store_true', help='Simulate cleanup without deleting')
    parser.add_argument('--live', action='store_true', help='Perform actual cleanup (requires confirmation)')
    parser.add_argument('--locations', nargs='+', choices=['temp', 'cache', 'logs', 'updates'], help='Specific locations to clean')
    parser.add_argument('--large-files', action='store_true', help='Find large files')
    parser.add_argument('--threshold', type=int, default=100, help='Large file threshold in MB')
    parser.add_argument('--drives', nargs='+', default=['C:', 'X:'], help='Drives to scan')
    parser.add_argument('--windows-specific', action='store_true', help='Run Windows-specific cleanup')
    parser.add_argument('--admin-check', action='store_true', help='Check admin privileges only')
    
    args = parser.parse_args()
    
    manager = WindowsCleanupManager()
    
    if args.admin_check:
        if manager.is_admin():
            print("✓ Running as administrator")
        else:
            print("✗ Not running as administrator")
            sys.exit(1)
        return
    
    print("Advanced Windows Disk Cleanup Tool")
    print("=" * 50)
    
    # Show drive info
    for drive in args.drives:
        info = manager.get_drive_info(drive)
        if 'error' not in info:
            print(f"Drive {info['drive']}: {info['used_gb']}/{info['total_gb']} GB used ({info['usage_percent']}%)")
    
    if args.large_files:
        print(f"\nFinding large files (> {args.threshold} MB)...")
        large_files = manager.find_large_files(args.drives, args.threshold)
        if large_files:
            print(f"Found {len(large_files)} large files:")
            for i, file_info in enumerate(large_files[:10], 1):
                print(f"{i:2d}. {file_info['size_mb']:6.1f} MB | {file_info['path']}")
            if len(large_files) > 10:
                print(f"... and {len(large_files) - 10} more")
        else:
            print("No large files found")
        return
    
    if args.windows_specific:
        print("\nRunning Windows-specific cleanup...")
        result = await manager.windows_specific_cleanup(dry_run=not args.live)
        print(f"Space freed: {result['space_freed_mb']} MB")
        print(f"Operations: {len(result['operations'])}")
        if result['errors']:
            print(f"Errors: {len(result['errors'])}")
        return
    
    # Main cleanup
    if not args.live and not args.dry_run:
        print("\nNo mode specified. Use --dry-run or --live")
        return
    
    if args.live:
        print("\n⚠️  WARNING: This will permanently delete files!")
        confirm = input("Are you sure? Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("Cancelled")
            return
    
    # Perform cleanup
    dry_run = not args.live
    stats = await manager.perform_cleanup(dry_run=dry_run, location_types=args.locations)
    
    # Generate report
    report = manager.generate_cleanup_report(stats)
    print("\n" + report)

if __name__ == "__main__":
    asyncio.run(main())