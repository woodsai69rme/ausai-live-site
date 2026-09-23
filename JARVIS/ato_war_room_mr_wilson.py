#!/usr/bin/env python3
"""
Mr. Wilson: ATO War Room (Forensic Mode v3.0).
Interactive forensic intelligence terminal for Woods' tax defense.
Cross-examines deposits, searches taxpayer evidence, and launches spreadsheets on command.
"""

import os
import sys
import csv
import subprocess
from pathlib import Path

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WOODATO_DIR = Path(r"C:\WOODATO")
X_WOODATO_DIR = Path(r"X:\WOODATO")
REASON_EXCEL = WOODATO_DIR / "ATO_REASON_FOR_DECISION_APPENDIX_1_AS_IS.xlsx"
REASON_CSV = WOODATO_DIR / "ATO_REASON_FOR_DECISION_APPENDIX_1_AS_IS.csv"
PORTAL_HTML = WOODATO_DIR / "ATO_WAR_ROOM_MASTER_PORTAL.html"


def print_banner():
    print("=" * 70)
    print(" ⚖️  MR. WILSON: ATO WAR ROOM // FORENSIC DEFENSE SUITE (v3.0)")
    print("=" * 70)
    c_status = "[MOUNTED]" if WOODATO_DIR.exists() else "[UNMOUNTED]"
    x_status = "[MOUNTED]" if X_WOODATO_DIR.exists() else "[OFFLINE]"
    print(f"  • C:\\WOODATO: {c_status}")
    print(f"  • X:\\WOODATO: {x_status}")
    print("  • Net Assessment Liability: $0.00 (Fully sheltered under TR 97/11)")
    print("=" * 70)
    print("Commands:")
    print("  'search <name/keyword>' - Search all 882 disputed deposits")
    print("  'open' / 'sheet'        - Launch Reason for Decision Excel spreadsheet")
    print("  'portal' / 'dash'       - Open interactive War Room HTML Portal")
    print("  'summary'               - Print Executive Defense Briefing")
    print("  'exit'                  - Exit War Room")
    print("-" * 70)


def search_deposits(query: str):
    q = query.lower()
    if not REASON_CSV.exists():
        print(f"[!] Reason for Decision CSV not found at {REASON_CSV}")
        return

    matches = []
    try:
        with open(REASON_CSV, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                row_str = " ".join(row).lower()
                if q in row_str:
                    matches.append(row)
    except Exception as e:
        print(f"[!] CSV Read Error: {e}")
        return

    print(f"\n[+] Found {len(matches)} matching deposit records for '{query}':")
    for i, m in enumerate(matches[:15], 1):
        clean_preview = " | ".join([col.strip() for col in m if col.strip()][:5])
        print(f"  [{i}] {clean_preview}")
    if len(matches) > 15:
        print(f"  ... and {len(matches) - 15} more rows.")
    print()


def open_master_sheet():
    target = REASON_EXCEL if REASON_EXCEL.exists() else REASON_CSV
    if target.exists():
        print(f"[+] Launching {target.name} in default application...")
        os.startfile(str(target))
    else:
        print(f"[!] Master spreadsheet not found at {target}")


def open_portal():
    if PORTAL_HTML.exists():
        print(f"[+] Opening War Room Portal in browser...")
        os.startfile(str(PORTAL_HTML))
    else:
        print(f"[!] Portal HTML not found at {PORTAL_HTML}")


def print_summary():
    print("""
========================================================================
 🛡️ MR. WILSON ATO EXECUTIVE SUMMARY & DEFENSE STRATEGY
========================================================================
 • Primary Assessment: $505,192.29 AUD default assessment (Disputed).
 • Gross Revenue: $1,712.76 USD ($2,610.25 AUD) from genuine business activity.
 • Instant Asset Write-Off (IAWO): -$6,221.50 AUD hardware + workstation write-off.
 • Net Tax Due: $0.00 AUD (100% Tax Sheltered).
 • Non-Income Deposits: Private asset sales (vehicles, equipment) and non-assessable
   personal loans & transfers with accompanying Statutory Declarations.
 • Statutory Declarations Ready:
   - Stat Dec: Steven Malcolm Woods (Asset Sales)
   - Stat Dec: Lincoln Cowin (Equipment / Machinery)
   - Stat Dec: Michael Hubert (Hino Truck / Asset Sale)
   - Stat Dec: Jake Dwan (Non-assessable Loan/Deposit)
========================================================================
""")


def main():
    print_banner()
    while True:
        try:
            cmd = input("⚖️ [War Room]: ").strip()
            if not cmd:
                continue
            lower = cmd.lower()
            if lower in ["exit", "quit", "q"]:
                print("\n[Mr. Wilson]: Disengaging ATO War Room. All records secured.")
                break
            elif lower.startswith("search ") or lower.startswith("find "):
                term = cmd.split(" ", 1)[1].strip()
                search_deposits(term)
            elif lower in ["open", "sheet", "excel", "spreadsheet"]:
                open_master_sheet()
            elif lower in ["portal", "dash", "dashboard"]:
                open_portal()
            elif lower in ["summary", "brief", "status"]:
                print_summary()
            else:
                # Default to searching deposits
                search_deposits(cmd)
        except KeyboardInterrupt:
            print("\n[Mr. Wilson]: War Room closed.")
            break
        except Exception as e:
            print(f"[!] Error: {e}")


if __name__ == "__main__":
    main()
