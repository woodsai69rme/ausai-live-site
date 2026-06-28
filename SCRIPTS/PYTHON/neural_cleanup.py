import os
import hashlib
import shutil
from pathlib import Path

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def neural_cleanup():
    root_dir = Path("C:/Users/karma")
    target_dir = root_dir / "Knowledge_Base"
    duplicates_dir = target_dir / "Duplicates_Archive"
    
    if not target_dir.exists(): target_dir.mkdir()
    if not duplicates_dir.exists(): duplicates_dir.mkdir()

    seen_hashes = {}
    file_types = ['.pdf', '.md', '.json', '.html', '.txt']

    print(f"--- Starting Neural Cleanup in {root_dir} ---")

    for file_path in root_dir.rglob('*'):
        if file_path.suffix.lower() in file_types and "Knowledge_Base" not in str(file_path):
            try:
                f_hash = get_file_hash(file_path)
                
                if f_hash in seen_hashes:
                    print(f"[DUP] Moving duplicate: {file_path.name}")
                    shutil.move(str(file_path), str(duplicates_dir / file_path.name))
                else:
                    seen_hashes[f_hash] = file_path
                    # Logical sort (Simplified: move to Knowledge_Base by extension)
                    type_dir = target_dir / file_path.suffix[1:].upper()
                    if not type_dir.exists(): type_dir.mkdir()
                    
                    print(f"[SORT] Organizing: {file_path.name}")
                    shutil.copy(str(file_path), str(type_dir / file_path.name))
            except Exception as e:
                print(f"[ERR] Skipping {file_path.name}: {e}")

    print("--- Cleanup Complete. High-Value Knowledge Consolidated ---")

if __name__ == "__main__":
    neural_cleanup()
