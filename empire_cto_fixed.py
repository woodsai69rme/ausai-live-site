#!/usr/bin/env python3
"""Wrapper to run empire_cto --money-day (byte-compiled module fix)"""
import sys
import os
import importlib.util

CORE = os.path.join(os.path.dirname(__file__), 'CUAI', 'core')

def load_pyc(name, pyc_filename):
    pyc_path = os.path.join(CORE, '__pycache__', pyc_filename)
    spec = importlib.util.spec_from_file_location(name, pyc_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules[name] = mod
    return mod

# Load dependencies first
for mod_name, pyc in [('vision_fleet', 'vision_fleet.cpython-311.pyc')]:
    try:
        load_pyc(mod_name, pyc)
        print(f"[OK] Loaded {mod_name} from {pyc}")
    except Exception as e:
        print(f"[FAIL] {mod_name}: {e}")
        sys.exit(1)

# Set argument and run empire_cto
sys.argv = ['empire_cto', '--money-day']

empire_pyc = os.path.join(CORE, '__pycache__', 'empire_cto.cpython-311.pyc')
spec = importlib.util.spec_from_file_location('empire_cto', empire_pyc)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    print("[DONE] empire_cto --money-day completed")
except SystemExit as e:
    print(f"[EXIT] empire_cto exited with code: {e.code}")
    sys.exit(e.code if isinstance(e.code, int) else 1)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)