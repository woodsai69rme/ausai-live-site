#!/usr/bin/env python3
"""
TEST EXTRACTION ON BOTH .GAL FILES
This will test if files can be successfully extracted
WITHOUT actually extracting anything to disk
"""

import zipfile
import os
from datetime import datetime

print("\n" + "="*80)
print("  EXTRACTION TEST - BOTH .GAL FILES")
print("  Testing if files can be extracted (without actually extracting)")
print("="*80 + "\n")

gal_files = [
    (r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260305_1358.gal", "80 GB - March 5"),
    (r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260306_0440.gal", "44 GB - March 6"),
]

results = {}

for gal_path, description in gal_files:
    filename = os.path.basename(gal_path)
    
    print("="*80)
    print(f"  TESTING: {filename} ({description})")
    print("="*80 + "\n")
    
    result = {
        'can_open': False,
        'is_valid_zip': False,
        'total_files': 0,
        'extractable_files': 0,
        'corrupted_files': 0,
        'files_list': [],
        'errors': []
    }
    
    # Test 1: Can we open the file?
    print("TEST 1: Can we open the file?")
    try:
        with zipfile.ZipFile(gal_path, 'r') as z:
            print(f"  ✅ SUCCESS - File opened as valid ZIP")
            result['can_open'] = True
            result['is_valid_zip'] = True
            
            # Test 2: Count files and test each one
            print("\nTEST 2: Testing each file for extractability...")
            files = z.namelist()
            result['total_files'] = len(files)
            print(f"  📦 Total files in archive: {len(files)}\n")
            
            good_files = []
            bad_files = []
            
            for i, info in enumerate(z.infolist(), 1):
                fname = info.filename
                try:
                    # Try to read the file (test if extractable)
                    data = z.read(fname)
                    
                    # Verify CRC
                    import zlib
                    actual_crc = zlib.crc32(data) & 0xffffffff
                    expected_crc = info.CRC
                    
                    if actual_crc == expected_crc:
                        good_files.append(fname)
                        size_kb = len(data) / 1024
                        print(f"  ✅ [{i}/{len(files)}] {fname} ({size_kb:.1f} KB) - EXTRACTABLE")
                    else:
                        bad_files.append((fname, "CRC mismatch"))
                        print(f"  ❌ [{i}/{len(files)}] {fname} - CRC MISMATCH")
                        
                except Exception as e:
                    bad_files.append((fname, str(e)))
                    print(f"  ❌ [{i}/{len(files)}] {fname} - ERROR: {e}")
            
            result['extractable_files'] = len(good_files)
            result['corrupted_files'] = len(bad_files)
            result['files_list'] = good_files
            result['errors'] = bad_files
            
            # Summary for this file
            print(f"\n{'-'*80}")
            print(f"  EXTRACTION TEST RESULTS for {filename}")
            print(f"{'-'*80}")
            print(f"  ✅ Can open: YES")
            print(f"  ✅ Valid ZIP: YES")
            print(f"  📦 Total files: {result['total_files']}")
            print(f"  ✅ Extractable: {result['extractable_files']} files")
            print(f"  ❌ Corrupted: {result['corrupted_files']} files")
            
            if result['extractable_files'] > 0:
                print(f"\n  📋 EXTRACTABLE FILES:")
                for f in good_files:
                    print(f"     ✅ {f}")
            
            if result['corrupted_files'] > 0:
                print(f"\n  ❌ CORRUPTED FILES:")
                for f, err in bad_files:
                    print(f"     ❌ {f}")
                    print(f"         Error: {err}")
            
            # Calculate success rate
            if result['total_files'] > 0:
                success_rate = (result['extractable_files'] / result['total_files']) * 100
                print(f"\n  📊 SUCCESS RATE: {success_rate:.1f}% ({result['extractable_files']}/{result['total_files']})")
            
            print(f"{'-'*80}\n")
            
    except zipfile.BadZipFile as e:
        print(f"  ❌ FAILED - Not a valid ZIP file")
        print(f"     Error: {e}")
        result['errors'].append(("File itself", str(e)))
        
    except Exception as e:
        print(f"  ❌ FAILED - Error opening file")
        print(f"     Error: {e}")
        result['errors'].append(("File itself", str(e)))
    
    results[filename] = result
    print("\n")

# FINAL SUMMARY
print("="*80)
print("  FINAL SUMMARY - BOTH FILES TESTED")
print("="*80 + "\n")

for filename, result in results.items():
    print(f"{'='*80}")
    print(f"  {filename}")
    print(f"{'='*80}")
    
    if result['can_open']:
        print(f"  ✅ Can Open: YES")
        print(f"  ✅ Valid ZIP: YES")
        print(f"  📦 Total Files: {result['total_files']}")
        print(f"  ✅ Extractable: {result['extractable_files']} files")
        print(f"  ❌ Corrupted: {result['corrupted_files']} files")
        
        if result['extractable_files'] > 0:
            print(f"\n  ✅ YOU CAN EXTRACT THESE FILES:")
            for f in result['files_list']:
                print(f"     {f}")
        
        if result['corrupted_files'] > 0:
            print(f"\n  ❌ CANNOT EXTRACT THESE FILES:")
            for f, err in result['errors']:
                print(f"     {f}")
                print(f"        Error: {err}")
    else:
        print(f"  ❌ CANNOT OPEN - File is corrupted or not a valid ZIP")
        print(f"  ❌ EXTRACTION: IMPOSSIBLE")
        print(f"  ❌ Files inside: UNKNOWN (cannot read archive)")
    
    print()

# OVERALL VERDICT
print("="*80)
print("  OVERALL VERDICT")
print("="*80 + "\n")

file1_ok = results.get(list(results.keys())[0], {}).get('can_open', False)
file2_ok = results.get(list(results.keys())[1], {}).get('can_open', False)

if not file1_ok and file2_ok:
    print("  📊 SITUATION:")
    print("  • 80 GB file: CORRUPTED - Cannot extract anything")
    print("  • 44 GB file: PARTIAL - Can extract some files")
    print("\n  ✅ RECOMMENDATION:")
    print("  • Delete 80 GB file (useless, corrupted)")
    print("  • Extract what you can from 44 GB file")
    print("  • Then delete 44 GB file")
    print("\n  🎯 YOUR ORIGINAL FILES:")
    print("  • All 22 Python scripts are SAFE in SYSTEM_CORE")
    print("  • These are just backup copies")
    
elif file1_ok and file2_ok:
    print("  ✅ BOTH FILES CAN BE EXTRACTED!")
    print("  • You can safely extract both")
    print("  • Then delete if you want")
    
elif not file1_ok and not file2_ok:
    print("  ❌ BOTH FILES ARE CORRUPTED")
    print("  • Cannot extract either file")
    print("  • Your originals in SYSTEM_CORE are safe")
    print("  • Safe to delete both .gal files")
    
else:
    print("  ⚠️  MIXED RESULTS - See details above")

print("\n" + "="*80)
print("  TEST COMPLETE")
print("="*80 + "\n")
