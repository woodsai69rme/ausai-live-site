#!/usr/bin/env python3
"""
Extract iconic rock and guitar drops from C:\\Users\\karma\\Music\\rock
into C:\\Users\\karma\\JARVIS\\audio_cache\\music_drops
"""

import os
import subprocess
from pathlib import Path

FFMPEG = Path(r"C:\Users\karma\ai-music-video-studio\ffmpeg.exe")
if not FFMPEG.exists():
    FFMPEG = Path(r"C:\Users\karma\ffmpeg.exe")

SRC_DIR = Path(r"C:\Users\karma\Music\rock")
OUT_DIR = Path(r"C:\Users\karma\JARVIS\audio_cache\music_drops")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Define precise timestamps for iconic drops (start, duration_seconds)
CLIPS = [
    {
        "file": "NA - AC⧸DC - Thunderstruck (Official Video).webm",
        "out": "acdc_thunderstruck.mp3",
        "start": "00:00:15",
        "duration": "8",
        "desc": "Thunderstruck fast picking intro"
    },
    {
        "file": "NA - AC⧸DC - Thunderstruck (Official Video).webm",
        "out": "acdc_thunder_drop.mp3",
        "start": "00:00:32",
        "duration": "7",
        "desc": "Thunderstruck chant drop"
    },
    {
        "file": "Metallica - Master of Puppets (Remastered).webm",
        "out": "takeover_master_puppets.mp3",
        "start": "00:00:01",
        "duration": "7",
        "desc": "Master of Puppets main crushing riff"
    },
    {
        "file": "NA - Guns N' Roses - Sweet Child O' Mine.webm",
        "out": "gnr_sweet_child_intro.mp3",
        "start": "00:00:00",
        "duration": "8",
        "desc": "Sweet Child O Mine Slash intro"
    },
    {
        "file": "Pink Floyd - Comfortably Numb.webm",
        "out": "pink_floyd_solo.mp3",
        "start": "00:04:31",
        "duration": "10",
        "desc": "Comfortably Numb iconic solo section"
    },
    {
        "file": "Metallica - Fade To Black (Remastered).webm",
        "out": "metallica_fade_riff.mp3",
        "start": "00:00:00",
        "duration": "8",
        "desc": "Fade To Black acoustic intro"
    },
    {
        "file": "Metallica - Nothing Else Matters (Remastered).webm",
        "out": "metallica_nem_clean.mp3",
        "start": "00:00:00",
        "duration": "8",
        "desc": "Nothing Else Matters fingerpicking intro"
    },
    {
        "file": "Metallica - The Unforgiven (Remastered).webm",
        "out": "metallica_unforgiven_horn.mp3",
        "start": "00:00:00",
        "duration": "8",
        "desc": "The Unforgiven western horn intro"
    },
    {
        "file": "NA - Led Zeppelin - Stairway To Heaven (Official Audio).webm",
        "out": "led_zeppelin_stairway_intro.mp3",
        "start": "00:00:00",
        "duration": "8",
        "desc": "Stairway to Heaven acoustic intro"
    }
]

print(f"[*] Extracting real music drops using: {FFMPEG}")
for clip in CLIPS:
    src_path = SRC_DIR / clip["file"]
    out_path = OUT_DIR / clip["out"]
    if not src_path.exists():
        print(f"[!] Warning: Missing source {src_path.name}")
        continue
    
    cmd = [
        str(FFMPEG),
        "-y",
        "-ss", clip["start"],
        "-i", str(src_path),
        "-t", clip["duration"],
        "-af", "afade=t=in:ss=0:d=0.5,afade=t=out:st=6:d=1.5",
        "-b:a", "192k",
        str(out_path)
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"[+] Extracted: {out_path.name} ({clip['desc']}) - {out_path.stat().st_size} bytes")
    except Exception as e:
        print(f"[-] Error extracting {clip['out']}: {e}")

print(f"[OK] Music drops populated in {OUT_DIR}")
