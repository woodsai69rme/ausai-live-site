#!/usr/bin/env python3
"""
DOUBLE-CHECK CRC ERRORS - CAREFUL VERIFICATION
Check each file multiple times to be certain
"""

import zipfile
import os

gal_file = r"C:\Users\karma\SYSTEM_CORE\Empire_Clone_20260306_0440.gal"

print(f"\n{'='*80}")
print(f"  DOUBLE-CHECKING CRC ERRORS")
print(f"  File: {os.path.basename(gal_file)}")
print(f"{'='*80}\n")

try:
    with zipfile.ZipFile(gal_file, 'r') as z:
        files = z.namelist()
        
        print(f"Total files to check: {len(files)}\n")
        
        print("Checking EACH file carefully:\n")
        
        all_ok = []
        all_bad = []
        
        for i, info in enumerate(z.infolist(), 1):
            filename = info.filename
            
            # Try multiple methods to check integrity
            errors = []
            
            # Method 1: Try to read the file
            try:
                data = z.read(info.filename)
            except Exception as e:
                errors.append(f"Read error: {e}")
            
            # Method 2: Check CRC explicitly
            try:
                # Get the CRC from the file header
                expected_crc = info.CRC
                # Read and calculate actual CRC
                data = z.read(info.filename)
                import zlib
                actual_crc = zlib.crc32(data) & 0xffffffff
                
                if expected_crc != actual_crc:
                    errors.append(f"CRC mismatch: expected {expected_crc}, got {actual_crc}")
            except Exception as e:
                errors.append(f"CRC check error: {e}")
            
            # Report results
            if errors:
                all_bad.append((filename, errors))
                print(f"{i}. ❌ {filename}")
                for err in errors:
                    print(f"      {err}")
            else:
                all_ok.append(filename)
                print(f"{i}. ✅ {filename} - OK")
        
        print(f"\n{'='*80}")
        print(f"  RESULTS")
        print(f"{'='*80}")
        print(f"\n  ✅ Files with NO errors: {len(all_ok)}")
        for f in all_ok:
            print(f"     {f}")
        
        print(f"\n  ❌ Files with errors: {len(all_bad)}")
        for f, errs in all_bad:
            print(f"     {f}")
            for e in errs:
                print(f"        {e}")
        
        print(f"\n{'='*80}")
        if len(all_bad) == 0:
            print(f"  ✅ ALL FILES PASS CRC CHECK - NO CORRUPTION")
        else:
            print(f"  ⚠️  {len(all_bad)} FILE(S) HAVE CRC ERRORS")
        print(f"{'='*80}\n")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
