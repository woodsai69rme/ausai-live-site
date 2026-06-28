import os
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple


class DuplicateDetector:
    """
    A comprehensive duplicate detection and removal system that identifies
    duplicate files based on content hashes and provides options for handling them.
    """
    
    def __init__(self, scan_paths: List[str], hash_db_path: str = "duplicate_hashes.json"):
        self.scan_paths = [Path(p) for p in scan_paths]
        self.hash_db_path = Path(hash_db_path)
        self.hashes_db = self.load_hashes_db()
        self.duplicate_groups = {}
    
    def load_hashes_db(self) -> Dict[str, List[str]]:
        """Load the hash database from file if it exists."""
        if self.hash_db_path.exists():
            try:
                with open(self.hash_db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading hash database: {e}. Starting fresh.")
                return {}
        return {}
    
    def save_hashes_db(self):
        """Save the hash database to file."""
        try:
            with open(self.hash_db_path, 'w') as f:
                json.dump(self.hashes_db, f, indent=2)
        except Exception as e:
            print(f"Error saving hash database: {e}")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate the SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def scan_for_duplicates(self) -> Dict[str, List[str]]:
        """Scan specified paths for duplicate files."""
        print("Scanning for duplicates...")
        
        # Dictionary to store file hashes and their paths
        hash_to_paths = {}
        
        for scan_path in self.scan_paths:
            if not scan_path.exists():
                print(f"Warning: Scan path {scan_path} does not exist.")
                continue
            
            # Walk through all files in the directory and subdirectories
            for file_path in scan_path.rglob('*'):
                if file_path.is_file():
                    # Skip the hash database file itself
                    if file_path.samefile(self.hash_db_path):
                        continue
                    
                    file_hash = self.calculate_file_hash(file_path)
                    
                    if file_hash:
                        if file_hash in hash_to_paths:
                            hash_to_paths[file_hash].append(str(file_path))
                        else:
                            hash_to_paths[file_hash] = [str(file_path)]
        
        # Find groups of duplicates (hashes with more than one file path)
        self.duplicate_groups = {
            hash_val: paths 
            for hash_val, paths in hash_to_paths.items() 
            if len(paths) > 1
        }
        
        # Update the hashes database with newly found files
        for file_hash, paths in hash_to_paths.items():
            if file_hash not in self.hashes_db:
                self.hashes_db[file_hash] = paths
            else:
                # Merge paths if hash already exists
                existing_paths = set(self.hashes_db[file_hash])
                new_paths = set(paths)
                all_paths = list(existing_paths.union(new_paths))
                self.hashes_db[file_hash] = all_paths
        
        self.save_hashes_db()
        
        print(f"Found {len(self.duplicate_groups)} groups of duplicate files.")
        return self.duplicate_groups
    
    def get_duplicate_report(self) -> str:
        """Generate a human-readable report of duplicate files."""
        if not self.duplicate_groups:
            return "No duplicates found."
        
        report_lines = [f"Duplicate Detection Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
        report_lines.append("="*60)
        
        total_duplicates = 0
        total_size_saved = 0
        
        for file_hash, paths in self.duplicate_groups.items():
            report_lines.append(f"\nDuplicate Group (Hash: {file_hash[:16]}...):")
            group_size = 0
            
            for i, path_str in enumerate(paths):
                path = Path(path_str)
                size = path.stat().st_size
                group_size += size
                total_size_saved += size if i > 0 else 0  # Count all but the first file toward savings
                total_duplicates += 1 if i > 0 else 0  # Count all but the first file as duplicates
                
                report_lines.append(f"  {i+1}. {path_str} ({size} bytes)")
            
            report_lines.append(f"  Group Total Size: {group_size} bytes")
        
        report_lines.append(f"\nSummary:")
        report_lines.append(f"- Total duplicate files: {total_duplicates}")
        report_lines.append(f"- Potential space savings: {total_size_saved} bytes ({self.format_bytes(total_size_saved)})")
        report_lines.append(f"- Unique duplicate groups: {len(self.duplicate_groups)}")
        
        return "\n".join(report_lines)
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def remove_duplicates(self, keep_strategy: str = "original") -> List[str]:
        """
        Remove duplicate files based on the specified strategy.
        
        Args:
            keep_strategy: How to choose which file to keep
                          "original" - keep the first occurrence found historically
                          "newest" - keep the newest file by modification time
                          "oldest" - keep the oldest file by modification time
                          "largest" - keep the largest file by size
                          "smallest" - keep the smallest file by size
                          
        Returns:
            List of removed file paths
        """
        removed_files = []
        
        for file_hash, paths in self.duplicate_groups.items():
            if len(paths) <= 1:
                continue  # No duplicates in this group
            
            # Convert to Path objects with stats
            path_info = []
            for path_str in paths:
                path_obj = Path(path_str)
                if path_obj.exists():
                    stat = path_obj.stat()
                    path_info.append({
                        'path': path_obj,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime
                    })
            
            if not path_info:
                continue  # All files in this group were already deleted
            
            # Determine which file to keep based on strategy
            if keep_strategy == "original":
                # Keep the first one from the historical record
                paths_from_db = self.hashes_db.get(file_hash, [])
                if paths_from_db:
                    keep_path = Path(paths_from_db[0])
                    files_to_remove = [info for info in path_info if info['path'] != keep_path]
                else:
                    # Fallback to keeping the first in current list
                    keep_path = path_info[0]['path']
                    files_to_remove = path_info[1:]
                    
            elif keep_strategy == "newest":
                keep_info = max(path_info, key=lambda x: x['mtime'])
                files_to_remove = [info for info in path_info if info['path'] != keep_info['path']]
                
            elif keep_strategy == "oldest":
                keep_info = min(path_info, key=lambda x: x['mtime'])
                files_to_remove = [info for info in path_info if info['path'] != keep_info['path']]
                
            elif keep_strategy == "largest":
                keep_info = max(path_info, key=lambda x: x['size'])
                files_to_remove = [info for info in path_info if info['path'] != keep_info['path']]
                
            elif keep_strategy == "smallest":
                keep_info = min(path_info, key=lambda x: x['size'])
                files_to_remove = [info for info in path_info if info['path'] != keep_info['path']]
                
            else:
                print(f"Unknown keep strategy: {keep_strategy}")
                continue
            
            # Remove the selected files
            for info in files_to_remove:
                try:
                    info['path'].unlink()
                    removed_files.append(str(info['path']))
                    print(f"Removed: {info['path']}")
                    
                    # Update the hashes database
                    if file_hash in self.hashes_db:
                        if str(info['path']) in self.hashes_db[file_hash]:
                            self.hashes_db[file_hash].remove(str(info['path']))
                            # Clean up empty hash entries
                            if not self.hashes_db[file_hash]:
                                del self.hashes_db[file_hash]
                                
                except Exception as e:
                    print(f"Error removing {info['path']}: {e}")
        
        # Save updated database
        self.save_hashes_db()
        
        print(f"\nRemoved {len(removed_files)} duplicate files.")
        return removed_files
    
    def move_duplicates_to_folder(self, destination_folder: str) -> List[str]:
        """Move all but one duplicate in each group to a destination folder."""
        destination = Path(destination_folder)
        destination.mkdir(parents=True, exist_ok=True)
        
        moved_files = []
        
        for file_hash, paths in self.duplicate_groups.items():
            if len(paths) <= 1:
                continue  # No duplicates in this group
            
            # Keep the first file, move the rest
            files_to_move = paths[1:]  # All except the first
            
            for path_str in files_to_move:
                source_path = Path(path_str)
                if source_path.exists():
                    try:
                        dest_path = destination / source_path.name
                        # Handle naming conflicts in destination
                        counter = 1
                        original_dest = dest_path
                        while dest_path.exists():
                            stem = original_dest.stem
                            suffix = original_dest.suffix
                            dest_path = destination / f"{stem}_duplicate_{counter}{suffix}"
                            counter += 1
                        
                        source_path.rename(dest_path)
                        moved_files.append(str(dest_path))
                        print(f"Moved duplicate: {source_path} -> {dest_path}")
                        
                        # Update the hashes database
                        if file_hash in self.hashes_db:
                            if path_str in self.hashes_db[file_hash]:
                                self.hashes_db[file_hash].remove(path_str)
                                # Add new path
                                self.hashes_db[file_hash].append(str(dest_path))
                        
                    except Exception as e:
                        print(f"Error moving {source_path}: {e}")
        
        # Clean up empty hash entries
        self.hashes_db = {k: v for k, v in self.hashes_db.items() if v}
        
        # Save updated database
        self.save_hashes_db()
        
        print(f"\nMoved {len(moved_files)} duplicate files to {destination}.")
        return moved_files


def main():
    """Main function to demonstrate the duplicate detection system."""
    print("Duplicate Detector and Remover")
    print("==============================")
    
    # Get directories to scan from user
    scan_dirs_input = input("Enter directories to scan for duplicates (comma-separated): ").strip()
    if not scan_dirs_input:
        scan_dirs = [".", "./projects", "./documents", "./ai-tools", "./chatgpt-exports"]
    else:
        scan_dirs = [d.strip() for d in scan_dirs_input.split(',')]
    
    # Initialize detector
    detector = DuplicateDetector(scan_dirs)
    
    # Scan for duplicates
    duplicates = detector.scan_for_duplicates()
    
    # Generate and display report
    report = detector.get_duplicate_report()
    print("\n" + report)
    
    # Ask user what to do with duplicates
    if duplicates:
        print("\nWhat would you like to do with duplicates?")
        print("1. Move to duplicates folder")
        print("2. Remove all but keep one (by original order)")
        print("3. Remove all but keep newest")
        print("4. Remove all but keep oldest")
        print("5. Remove all but keep largest")
        print("6. Remove all but keep smallest")
        print("7. Do nothing (just report)")
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            dest_folder = input("Enter destination folder for duplicates: ").strip()
            if not dest_folder:
                dest_folder = "./duplicates_moved"
            detector.move_duplicates_to_folder(dest_folder)
        elif choice == "2":
            detector.remove_duplicates("original")
        elif choice == "3":
            detector.remove_duplicates("newest")
        elif choice == "4":
            detector.remove_duplicates("oldest")
        elif choice == "5":
            detector.remove_duplicates("largest")
        elif choice == "6":
            detector.remove_duplicates("smallest")
        elif choice == "7":
            print("No files were modified.")
        else:
            print("Invalid choice. No action taken.")
    else:
        print("No duplicates found to process.")


if __name__ == "__main__":
    main()