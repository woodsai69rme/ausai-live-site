#!/usr/bin/env python3
"""One-off verifier: schtasks /create + /query + /delete on the corrected sleep_task.xml."""
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

XML = r"C:\Users\karma\SLEEP_TRIPLE\sleep_task.xml"
TASK = r"SLEEP_TRIPLE\Nightly_Test"

create = subprocess.run(["schtasks", "/create", "/tn", TASK,
                         "/xml", XML, "/f"], capture_output=True, text=True)
print("--- schtasks /create ---")
print(f"rc={create.returncode}")
print(f"stdout={create.stdout.strip()!r}")
print(f"stderr={create.stderr.strip()!r}")

if create.returncode != 0:
    raise SystemExit("register failed")

q = subprocess.run(["schtasks", "/query", "/tn", TASK, "/fo", "LIST", "/v"],
                   capture_output=True, text=True)
print("--- schtasks /query ---")
print(f"rc={q.returncode}")
print(q.stdout.strip()[:800])

d = subprocess.run(["schtasks", "/delete", "/tn", TASK, "/f"],
                   capture_output=True, text=True)
print("--- schtasks /delete ---")
print(f"rc={d.returncode}")
print(f"stdout={d.stdout.strip()!r}")
print(f"stderr={d.stderr.strip()!r}")

# Also: confirm XML is well-formed
tree = ET.parse(XML)
root = tree.getroot()
ns = "{http://schemas.microsoft.com/windows/2004/02/mit/task}"
trigger = next(root.iter(ns + "CalendarTrigger"))
action = next(root.iter(ns + "Exec"))
print("--- XML parse ---")
print(f"version={root.get('version')}")
print(f"start_boundary={trigger.find(ns + 'StartBoundary').text}")
print(f"command={action.find(ns + 'Command').text}")
print(f"arguments={action.find(ns + 'Arguments').text}")
print("XML_OK")
