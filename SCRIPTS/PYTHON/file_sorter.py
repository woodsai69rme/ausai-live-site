import os
import shutil
import mimetypes
from pathlib import Path
import hashlib
from typing import Dict, List, Tuple

class FileSorter:
    """
    A comprehensive file sorting system that categorizes files by type and content,
    with duplicate detection and removal capabilities.
    """
    
    def __init__(self, source_dir: str, destination_dir: str):
        self.source_dir = Path(source_dir)
        self.destination_dir = Path(destination_dir)
        self.file_types = {
            'code': ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.json', '.yaml', '.yml', '.xml', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rb', '.php', '.sql', '.sh', '.bat', '.cmd', '.ps1'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.odp', '.ods', '.md', '.tex', '.csv'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.raw'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
            'data': ['.json', '.csv', '.xml', '.yaml', '.yml', '.db', '.sqlite', '.sql']
        }
        
        # Create destination directories if they don't exist
        for category in self.file_types.keys():
            (self.destination_dir / category).mkdir(parents=True, exist_ok=True)
    
    def get_file_category(self, file_path: Path) -> str:
        """
        Determine the category of a file based on its extension.
        """
        extension = file_path.suffix.lower()
        
        for category, extensions in self.file_types.items():
            if extension in extensions:
                return category
        
        # If extension is not recognized, try to determine type by content
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if mime_type.startswith('text/'):
                return 'documents'
            elif mime_type.startswith('image/'):
                return 'images'
            elif mime_type.startswith('video/'):
                return 'videos'
            elif mime_type.startswith('audio/'):
                return 'audio'
        
        # Default to 'documents' if type cannot be determined
        return 'documents'
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate the MD5 hash of a file for duplicate detection.
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def sort_files(self, move_files: bool = False) -> Dict[str, List[str]]:
        """
        Sort files from source directory to categorized destination directories.
        
        Args:
            move_files: If True, move files; if False, copy files
            
        Returns:
            Dictionary with category names as keys and lists of processed files as values
        """
        results = {category: [] for category in self.file_types.keys()}
        
        if not self.source_dir.exists():
            print(f"Source directory {self.source_dir} does not exist!")
            return results
        
        processed_files = {}  # To track duplicates
        duplicate_files = []
        
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file():
                category = self.get_file_category(file_path)
                destination_category_dir = self.destination_dir / category
                
                # Calculate file hash for duplicate detection
                file_hash = self.calculate_file_hash(file_path)
                
                if file_hash:
                    if file_hash in processed_files:
                        # This is a duplicate
                        duplicate_files.append(str(file_path))
                        print(f"Duplicate found: {file_path} (duplicate of {processed_files[file_hash]})")
                    else:
                        # New file, process it
                        processed_files[file_hash] = str(file_path)
                        
                        # Create destination path
                        destination_path = destination_category_dir / file_path.name
                        
                        # Handle naming conflicts in destination
                        counter = 1
                        original_destination = destination_path
                        while destination_path.exists():
                            stem = original_destination.stem
                            suffix = original_destination.suffix
                            destination_path = destination_category_dir / f"{stem}_{counter}{suffix}"
                            counter += 1
                        
                        # Copy or move the file
                        try:
                            if move_files:
                                shutil.move(str(file_path), str(destination_path))
                                print(f"Moved: {file_path} -> {destination_path}")
                            else:
                                shutil.copy2(str(file_path), str(destination_path))
                                print(f"Copied: {file_path} -> {destination_path}")
                            
                            results[category].append(str(file_path))
                        except Exception as e:
                            print(f"Error processing {file_path}: {e}")
                else:
                    print(f"Could not process file: {file_path}")
        
        # Handle duplicates
        if duplicate_files:
            duplicates_dir = self.destination_dir / 'duplicates'
            duplicates_dir.mkdir(exist_ok=True)
            
            for dup_file in duplicate_files:
                try:
                    if move_files:
                        shutil.move(dup_file, str(duplicates_dir / Path(dup_file).name))
                        print(f"Moved duplicate: {dup_file} -> {duplicates_dir}")
                    else:
                        shutil.copy2(dup_file, str(duplicates_dir / Path(dup_file).name))
                        print(f"Copied duplicate: {dup_file} -> {duplicates_dir}")
                except Exception as e:
                    print(f"Error processing duplicate {dup_file}: {e}")
        
        return results
    
    def sort_by_content_keywords(self, source_dir: str = None, keyword_mapping: Dict[str, List[str]] = None):
        """
        Sort files based on content keywords.
        
        Args:
            source_dir: Directory to scan (defaults to self.source_dir)
            keyword_mapping: Dictionary mapping category names to lists of keywords
        """
        if source_dir is None:
            source_dir = self.source_dir
        else:
            source_dir = Path(source_dir)
        
        if keyword_mapping is None:
            # Default keyword mapping for common project types
            keyword_mapping = {
                'ai_ml': ['ai', 'machine learning', 'neural', 'tensorflow', 'pytorch', 'model', 'algorithm', 'data science'],
                'web_dev': ['html', 'css', 'javascript', 'react', 'vue', 'angular', 'node', 'express', 'api', 'frontend', 'backend'],
                'mobile_dev': ['ios', 'android', 'flutter', 'react native', 'mobile', 'app', 'swift', 'kotlin'],
                'database': ['sql', 'database', 'mysql', 'postgresql', 'mongodb', 'redis', 'query', 'schema'],
                'security': ['security', 'encryption', 'authentication', 'authorization', 'firewall', 'ssl', 'tls', 'vulnerability'],
                'devops': ['docker', 'kubernetes', 'ci/cd', 'jenkins', 'aws', 'azure', 'gcp', 'cloud', 'deployment', 'terraform'],
                'testing': ['test', 'unittest', 'pytest', 'junit', 'mock', 'assert', 'coverage', 'tdd', 'bdd']
            }
        
        for file_path in source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.txt', '.md']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                    
                    # Check for keywords in content
                    matched_categories = []
                    for category, keywords in keyword_mapping.items():
                        if any(keyword in content for keyword in keywords):
                            matched_categories.append(category)
                    
                    # If matches found, create symlinks or copies in corresponding directories
                    if matched_categories:
                        for category in matched_categories:
                            category_dir = self.destination_dir / 'content_based' / category
                            category_dir.mkdir(parents=True, exist_ok=True)
                            
                            destination_path = category_dir / file_path.name
                            counter = 1
                            original_destination = destination_path
                            while destination_path.exists():
                                stem = original_destination.stem
                                suffix = original_destination.suffix
                                destination_path = category_dir / f"{stem}_{counter}{suffix}"
                                counter += 1
                            
                            shutil.copy2(str(file_path), str(destination_path))
                            print(f"Content-sorted ({category}): {file_path} -> {destination_path}")
                
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")


def main():
    """
    Main function to demonstrate the file sorting capabilities.
    """
    # Example usage
    source_directory = input("Enter source directory path to sort: ").strip()
    if not source_directory:
        source_directory = "."
    
    destination_directory = input("Enter destination directory path for sorted files: ").strip()
    if not destination_directory:
        destination_directory = "./sorted_files"
    
    sorter = FileSorter(source_directory, destination_directory)
    
    print("Starting file sorting process...")
    results = sorter.sort_files(move_files=False)  # Set to True to move instead of copy
    
    print("\nSorting completed. Summary:")
    for category, files in results.items():
        print(f"{category}: {len(files)} files processed")
    
    print("\nPerforming content-based sorting...")
    sorter.sort_by_content_keywords()
    
    print("\nAll sorting operations completed!")


if __name__ == "__main__":
    main()