#!/usr/bin/env python3
"""
GAL FILE VERIFICATION TOOL
Checks if .gal files are valid, not corrupted, and lists contents
"""

import zipfile
import os
from datetime import datetime

def verify_gal_file(gal_path):
    """Verify a .gal file is valid and show contents"""
    print(f"\n{'='*70}")
    print(f"VERIFYING: {os.path.basename(gal_path)}")
    print(f"{'='*70}")
    
    # Check file exists
    if not os.path.exists(gal_path):
        print(f"❌ FILE NOT FOUND: {gal_path}")
        return None
    
    # Get file size
    size_bytes = os.path.getsize(gal_path)
    size_gb = size_bytes / (1024**3)
    print(f"\n📊 FILE SIZE: {size_gb:.2f} GB ({size_bytes:,} bytes)")
    
    # Try to open as ZIP
    try:
        with zipfile.ZipFile(gal_path, 'r') as zipf:
            print(f"✅ Valid ZIP archive - NOT CORRUPTED")
            
            # Get file count
            file_count = len(zipf.namelist())
            print(f"📦 TOTAL FILES: {file_count:,}")
            
            # Check for corruption (bad CRC)
            print(f"\n🔍 Checking for corruption...")
            bad_files = []
            for info in zipf.infolist():
                try:
                    zipf.read(info.filename)
                except Exception as e:
                    bad_files.append((info.filename, str(e)))
            
            if bad_files:
                print(f"⚠️  WARNING: {len(bad_files)} corrupted files!")
                for fn, err in bad_files[:5]:
                    print(f"   - {fn}: {err}")
                return None
            else:
                print(f"✅ NO CORRUPTION DETECTED")
            
            # Get all file names
            all_names = zipf.namelist()
            
            # Count by extension
            by_ext = {}
            for name in all_names:
                ext = os.path.splitext(name)[1] or '(no ext)'
                by_ext[ext] = by_ext.get(ext, 0) + 1
            
            print(f"\n📊 FILE TYPES:")
            for ext, count in sorted(by_ext.items(), key=lambda x: -x[1])[:15]:
                print(f"   {ext}: {count:,}")
            
            # Get top directories
            top_dirs = set()
            root_files = []
            for name in all_names:
                parts = name.replace('\\', '/').split('/')
                if len(parts) > 1:
                    top_dirs.add(parts[0])
                else:
                    root_files.append(name)
            
            print(f"\n📁 TOP-LEVEL DIRECTORIES:")
            for d in sorted(top_dirs):
                # Count files in this directory
                count = sum(1 for n in all_names if n.replace('\\', '/').startswith(d + '/'))
                print(f"   {d}/ ({count:,} files)")
            
            if root_files:
                print(f"\n📄 ROOT FILES:")
                for f in root_files[:10]:
                    print(f"   {f}")
                if len(root_files) > 10:
                    print(f"   ... and {len(root_files) - 10} more")
            
            # Find Python scripts
            py_files = [n for n in all_names if n.endswith('.py')]
            print(f"\n🐍 PYTHON SCRIPTS ({len(py_files)} found):")
            for py in sorted(py_files):
                print(f"   ✅ {py}")
            
            # Find config files
            config_files = [n for n in all_names if n.endswith(('.json', '.yaml', '.ini', '.yml'))]
            print(f"\n⚙️  CONFIG FILES ({len(config_files)} found):")
            for cfg in sorted(config_files)[:15]:
                print(f"   • {cfg}")
            if len(config_files) > 15:
                print(f"   ... and {len(config_files) - 15} more")
            
            # Find database files
            db_files = [n for n in all_names if n.endswith(('.db', '.sqlite', '.sqlite3'))]
            if db_files:
                print(f"\n💾 DATABASE FILES ({len(db_files)} found):")
                for db in sorted(db_files):
                    # Get size
                    try:
                        info = zipf.getinfo(db)
                        size_mb = info.file_size / (1024*1024)
                        print(f"   💾 {db} ({size_mb:.1f} MB)")
                    except:
                        print(f"   💾 {db}")
            
            # Calculate total extracted size
            total_size = sum(info.file_size for info in zipf.infolist())
            total_gb = total_size / (1024**3)
            total_mb = total_size / (1024*1024)
            
            print(f"\n💾 DISK SPACE NEEDED FOR EXTRACTION:")
            if total_gb >= 1:
                print(f"   {total_gb:.2f} GB ({total_size:,} bytes)")
            else:
                print(f"   {total_mb:.2f} MB ({total_size:,} bytes)")
            
            print(f"\n{'='*70}")
            print(f"✅ VERIFICATION PASSED")
            print(f"{'='*70}\n")
            
            return {
                'valid': True,
                'file_count': file_count,
                'size_gb': size_gb,
                'extracted_size_gb': total_gb,
                'python_files': len(py_files),
                'config_files': len(config_files),
                'db_files': len(db_files),
            }
            
    except zipfile.BadZipFile as e:
        print(f"❌ CORRUPTED ZIP FILE: {e}")
        return {'valid': False, 'error': str(e)}
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'valid': False, 'error': str(e)}

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  GAL FILE VERIFICATION TOOL")
    print("  Checking both backup files for corruption")
    print("="*70)
    
    gal_files = [
        r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260305_1358.gal",
        r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260306_0440.gal",
    ]
    
    results = {}
    for gal_file in gal_files:
        results[gal_file] = verify_gal_file(gal_file)
    
    print("\n" + "="*70)
    print("  FINAL SUMMARY")
    print("="*70)
    
    for gal_file, result in results.items():
        filename = os.path.basename(gal_file)
        if result and result.get('valid'):
            print(f"\n✅ {filename}")
            print(f"   Status: VALID (no corruption)")
            print(f"   Size: {result['size_gb']:.2f} GB")
            print(f"   Files: {result['file_count']:,}")
            print(f"   Extracted size: {result['extracted_size_gb']:.2f} GB")
            print(f"   Python scripts: {result['python_files']}")
            print(f"   Config files: {result['config_files']}")
            print(f"   Database files: {result['db_files']}")
        else:
            print(f"\n❌ {filename}")
            print(f"   Status: CORRUPTED or ERROR")
            if result:
                print(f"   Error: {result.get('error', 'Unknown')}")
    
    # Final recommendation
    print("\n" + "="*70)
    all_valid = all(r and r.get('valid') for r in results.values())
    if all_valid:
        print("  ✅ BOTH FILES ARE VALID - SAFE TO DELETE OLDER ONE")
    else:
        print("  ⚠️  SOME FILES HAVE ISSUES - REVIEW BEFORE DELETING")
    print("="*70 + "\n")
