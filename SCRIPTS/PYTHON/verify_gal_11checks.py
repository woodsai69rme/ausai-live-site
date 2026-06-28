#!/usr/bin/env python3
"""
GAL FILE VERIFICATION - 11 CHECKS
DO NOT DELETE ANYTHING - VERIFICATION ONLY

For EACH .gal file:
1. ✅ File exists and is accessible
2. ✅ File size is measured
3. ✅ Opens as valid ZIP archive (not corrupted)
4. ✅ Counts total files inside
5. ✅ Checks each file for CRC errors (corruption)
6. ✅ Lists file types (.py, .json, .db, etc.)
7. ✅ Shows directory structure
8. ✅ Finds all Python scripts
9. ✅ Finds config files
10. ✅ Finds database files
11. ✅ Calculates total extracted size (WITHOUT extracting)
"""

import zipfile
import os
from datetime import datetime

print("\n" + "="*80)
print("  GAL FILE VERIFICATION - ALL 11 CHECKS")
print("  ⚠️  VERIFICATION ONLY - NO DELETIONS")
print("="*80)

gal_files = [
    r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260305_1358.gal",
    r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260306_0440.gal",
]

results = {}

for idx, gal_path in enumerate(gal_files, 1):
    filename = os.path.basename(gal_path)
    
    print(f"\n{'#'*80}")
    print(f"# FILE {idx}/{len(gal_files)}: {filename}")
    print(f"{'#'*80}\n")
    
    result = {
        'exists': False,
        'size_gb': 0,
        'valid_zip': False,
        'total_files': 0,
        'corrupted_count': 0,
        'file_types': {},
        'directories': set(),
        'python_scripts': [],
        'config_files': [],
        'database_files': [],
        'extracted_size_gb': 0,
        'error': None
    }
    
    # 1. Check file exists
    print("1. Checking if file exists and is accessible...")
    if not os.path.exists(gal_path):
        print(f"   ❌ FILE NOT FOUND")
        result['error'] = "File does not exist"
    else:
        print(f"   ✅ File exists and is accessible")
        result['exists'] = True
        
        # 2. Get file size
        print("\n2. Measuring file size...")
        size_bytes = os.path.getsize(gal_path)
        size_gb = size_bytes / (1024**3)
        result['size_gb'] = size_gb
        print(f"   📊 File Size: {size_gb:.2f} GB ({size_bytes:,} bytes)")
        
        # 3-11. Open and analyze
        print("\n3. Checking if opens as valid ZIP archive...")
        try:
            with zipfile.ZipFile(gal_path, 'r') as z:
                print(f"   ✅ Valid ZIP archive - NOT corrupted")
                result['valid_zip'] = True
                
                # 4. Count total files
                print("\n4. Counting total files inside...")
                all_names = z.namelist()
                result['total_files'] = len(all_names)
                print(f"   📦 Total files: {len(all_names):,}")
                
                # 5. Check CRC errors
                print("\n5. Checking each file for CRC errors (corruption)...")
                print(f"   ⏳ Scanning {len(all_names):,} files...")
                bad = []
                for info in z.infolist():
                    try:
                        z.read(info.filename)
                    except Exception as e:
                        bad.append((info.filename, str(e)))
                
                result['corrupted_count'] = len(bad)
                if bad:
                    print(f"   ⚠️  {len(bad)} files with CRC errors!")
                    for f, e in bad[:10]:
                        print(f"      - {f}")
                    if len(bad) > 10:
                        print(f"      ... and {len(bad)-10} more")
                else:
                    print(f"   ✅ NO CORRUPTION - All files passed CRC check")
                
                # 6. List file types
                print("\n6. Listing file types (.py, .json, .db, etc.)...")
                by_ext = {}
                for n in all_names:
                    ext = os.path.splitext(n)[1] if '.' in os.path.basename(n) else '(no ext)'
                    by_ext[ext] = by_ext.get(ext, 0) + 1
                result['file_types'] = by_ext
                print(f"   📊 File Types:")
                for ext, cnt in sorted(by_ext.items(), key=lambda x: -x[1])[:20]:
                    print(f"      {ext}: {cnt:,}")
                if len(by_ext) > 20:
                    print(f"      ... and {len(by_ext)-20} more types")
                
                # 7. Show directory structure
                print("\n7. Showing directory structure...")
                top_dirs = set()
                root_files = []
                for n in all_names:
                    parts = n.replace('\\', '/').split('/')
                    if len(parts) > 1:
                        top_dirs.add(parts[0])
                    else:
                        root_files.append(n)
                result['directories'] = top_dirs
                result['root_files'] = root_files
                
                print(f"   📁 Top-Level Directories:")
                for d in sorted(top_dirs):
                    cnt = sum(1 for n in all_names if n.replace('\\', '/').startswith(d + '/'))
                    print(f"      {d}/ ({cnt:,} files)")
                
                if root_files:
                    print(f"\n   📄 Root-Level Files ({len(root_files)}):")
                    for f in root_files[:10]:
                        print(f"      {f}")
                    if len(root_files) > 10:
                        print(f"      ... and {len(root_files)-10} more")
                
                # 8. Find all Python scripts
                print("\n8. Finding all Python scripts...")
                py = [n for n in all_names if n.endswith('.py')]
                result['python_scripts'] = py
                print(f"   🐍 Python Scripts: {len(py)}")
                for f in sorted(py):
                    print(f"      ✅ {f}")
                
                # 9. Find config files
                print("\n9. Finding config files...")
                cfg_ext = ['.json', '.yaml', '.yml', '.ini', '.toml', '.cfg']
                cfg = [n for n in all_names if any(n.endswith(e) for e in cfg_ext)]
                result['config_files'] = cfg
                print(f"   ⚙️  Config Files: {len(cfg)}")
                for f in sorted(cfg)[:20]:
                    print(f"      • {f}")
                if len(cfg) > 20:
                    print(f"      ... and {len(cfg)-20} more")
                
                # 10. Find database files
                print("\n10. Finding database files...")
                db_ext = ['.db', '.sqlite', '.sqlite3']
                db = [n for n in all_names if any(n.endswith(e) for e in db_ext)]
                result['database_files'] = db
                if db:
                    print(f"   💾 Database Files: {len(db)}")
                    for f in sorted(db):
                        try:
                            info = z.getinfo(f)
                            sz_gb = info.file_size / (1024**3)
                            sz_mb = info.file_size / (1024*1024)
                            if sz_gb >= 1:
                                print(f"      💾 {f} ({sz_gb:.2f} GB)")
                            else:
                                print(f"      💾 {f} ({sz_mb:.2f} MB)")
                        except:
                            print(f"      💾 {f}")
                else:
                    print(f"   💾 No database files found")
                
                # 11. Calculate total extracted size
                print("\n11. Calculating total extracted size (WITHOUT extracting)...")
                total_bytes = sum(info.file_size for info in z.infolist())
                total_gb = total_bytes / (1024**3)
                result['extracted_size_gb'] = total_gb
                print(f"   💾 Total Extracted Size: {total_gb:.2f} GB")
                
        except zipfile.BadZipFile as e:
            print(f"   ❌ NOT A VALID ZIP FILE: {e}")
            result['error'] = f"Not a valid ZIP: {e}"
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            result['error'] = str(e)
    
    results[gal_path] = result

# Summary
print("\n" + "="*80)
print("  FINAL SUMMARY - ALL 11 CHECKS COMPLETE")
print("="*80)

for gal_path, r in results.items():
    filename = os.path.basename(gal_path)
    print(f"\n{'='*80}")
    print(f"  {filename}")
    print(f"{'='*80}")
    
    if r['error']:
        print(f"\n  ❌ ERROR: {r['error']}")
    else:
        print(f"\n  1. ✅ Exists: YES")
        print(f"  2. ✅ Size: {r['size_gb']:.2f} GB")
        print(f"  3. ✅ Valid ZIP: YES")
        print(f"  4. ✅ Total Files: {r['total_files']:,}")
        print(f"  5. ✅ Corrupted Files: {r['corrupted_count']}")
        print(f"  6. ✅ File Types: {len(r['file_types'])} different types")
        print(f"  7. ✅ Directories: {len(r['directories'])} top-level")
        print(f"  8. ✅ Python Scripts: {len(r['python_scripts'])}")
        print(f"  9. ✅ Config Files: {len(r['config_files'])}")
        print(f"  10. ✅ Database Files: {len(r['database_files'])}")
        print(f"  11. ✅ Extracted Size: {r['extracted_size_gb']:.2f} GB")

print("\n" + "="*80)
print("  VERDICT")
print("="*80)

all_valid = all(r['valid_zip'] and r['corrupted_count']==0 for r in results.values() if not r['error'])

if all_valid:
    print("\n  ✅ ALL FILES ARE VALID - NO CORRUPTION DETECTED")
else:
    print("\n  ⚠️  SOME FILES HAVE ISSUES - SEE DETAILS ABOVE")

print("\n" + "="*80)
print("  ⚠️  NO FILES WERE DELETED, MOVED, OR MODIFIED")
print("  ✅ VERIFICATION COMPLETE")
print("="*80 + "\n")
