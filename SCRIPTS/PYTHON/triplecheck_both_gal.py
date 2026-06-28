#!/usr/bin/env python3
"""
TRIPLE-CHECK BOTH .GAL FILES - COMPLETE VERIFICATION
No assumptions - check everything from scratch
"""

import zipfile
import os
import struct

print("\n" + "="*80)
print("  TRIPLE-CHECK - BOTH .GAL FILES")
print("  Starting fresh verification...")
print("="*80 + "\n")

gal_files = [
    r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260305_1358.gal",
    r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260306_0440.gal",
]

for idx, gal_path in enumerate(gal_files, 1):
    filename = os.path.basename(gal_path)
    
    print("="*80)
    print(f"  FILE {idx}: {filename}")
    print("="*80 + "\n")
    
    # Check 1: File exists
    print("1. File exists?")
    if os.path.exists(gal_path):
        print(f"   ✅ YES")
    else:
        print(f"   ❌ NO")
        continue
    
    # Check 2: File size
    print("\n2. File size?")
    size_bytes = os.path.getsize(gal_path)
    size_gb = size_bytes / (1024**3)
    print(f"   {size_gb:.2f} GB ({size_bytes:,} bytes)")
    
    # Check 3: Is it a ZIP file? (Manual header check)
    print("\n3. Is it a valid ZIP file?")
    
    try:
        with open(gal_path, 'rb') as f:
            # Read first 4 bytes (ZIP magic number should be PK\x03\x04)
            magic = f.read(4)
            f.seek(0)
            
            if magic == b'PK\x03\x04':
                print(f"   ✅ Has valid ZIP header (PK)")
                
                # Try to open as ZIP
                try:
                    with zipfile.ZipFile(gal_path, 'r') as z:
                        print(f"   ✅ Successfully opened as ZIP")
                        
                        # List all files
                        files = z.namelist()
                        print(f"\n4. Total files inside: {len(files)}")
                        
                        # Check each file
                        print(f"\n5. Checking CRC for each file:")
                        bad_files = []
                        good_files = []
                        
                        for info in z.infolist():
                            try:
                                # Try to read
                                data = z.read(info.filename)
                                
                                # Verify CRC
                                import zlib
                                actual_crc = zlib.crc32(data) & 0xffffffff
                                expected_crc = info.CRC
                                
                                if actual_crc == expected_crc:
                                    good_files.append(info.filename)
                                    sz = len(data) / 1024
                                    print(f"   ✅ {info.filename} ({sz:.1f} KB) - CRC OK")
                                else:
                                    bad_files.append((info.filename, f"CRC mismatch"))
                                    print(f"   ❌ {info.filename} - CRC MISMATCH")
                                    
                            except Exception as e:
                                bad_files.append((info.filename, str(e)))
                                print(f"   ❌ {info.filename} - ERROR: {e}")
                        
                        print(f"\n6. File types found:")
                        by_ext = {}
                        for f in files:
                            ext = os.path.splitext(f)[1] if '.' in os.path.basename(f) else '(no ext)'
                            by_ext[ext] = by_ext.get(ext, 0) + 1
                        for ext, cnt in sorted(by_ext.items(), key=lambda x: -x[1]):
                            print(f"   {ext}: {cnt}")
                        
                        print(f"\n7. Directory structure:")
                        top_dirs = set()
                        for f in files:
                            parts = f.replace('\\', '/').split('/')
                            if len(parts) > 1:
                                top_dirs.add(parts[0])
                        for d in sorted(top_dirs):
                            cnt = sum(1 for f in files if f.replace('\\', '/').startswith(d + '/'))
                            print(f"   {d}/ ({cnt} files)")
                        
                        print(f"\n8. Python scripts:")
                        py_files = [f for f in files if f.endswith('.py')]
                        for f in sorted(py_files):
                            print(f"   ✅ {f}")
                        
                        print(f"\n9. Config files:")
                        cfg_files = [f for f in files if f.endswith(('.json', '.yaml', '.ini'))]
                        for f in sorted(cfg_files):
                            print(f"   • {f}")
                        
                        print(f"\n10. Database files:")
                        db_files = [f for f in files if f.endswith(('.db', '.sqlite'))]
                        if db_files:
                            for f in sorted(db_files):
                                print(f"   💾 {f}")
                        else:
                            print(f"   None found")
                        
                        print(f"\n11. Total extracted size:")
                        total = sum(info.file_size for info in z.infolist())
                        total_gb = total / (1024**3)
                        print(f"   {total_gb:.2f} GB")
                        
                        # Summary
                        print(f"\n{'-'*80}")
                        print(f"  SUMMARY for {filename}")
                        print(f"{'-'*80}")
                        print(f"  ✅ Valid ZIP: YES")
                        print(f"  ✅ Total files: {len(files)}")
                        print(f"  ✅ Good files (CRC OK): {len(good_files)}")
                        if bad_files:
                            print(f"  ❌ Bad files (CRC errors): {len(bad_files)}")
                            for f, e in bad_files:
                                print(f"     - {f}: {e}")
                        else:
                            print(f"  ❌ Bad files: 0 - ALL FILES PERFECT!")
                        print(f"{'-'*80}")
                        
                except zipfile.BadZipFile as e:
                    print(f"   ❌ Failed to open: {e}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    
            elif magic == b'PK\x05\x06':
                print(f"   ⚠️  Empty ZIP archive (no files)")
            else:
                print(f"   ❌ NOT A ZIP FILE")
                print(f"      Header bytes: {magic.hex()} (expected: 504b0304)")
                print(f"      This file does not have ZIP magic number PK\\x03\\x04")
                
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
    
    print("\n")

print("="*80)
print("  VERIFICATION COMPLETE")
print("="*80)
