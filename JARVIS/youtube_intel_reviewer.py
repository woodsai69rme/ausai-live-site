#!/usr/bin/env python3
"""
Mr. Wilson: YouTube Video & Public Playlist Intelligence Reviewer (v3.0).
Extracts video metadata, transcripts, and generates structured executive intelligence dossiers
for single videos or entire public playlists.
Supports OpenRouter and local Ollama failover, with voice summary narration.
"""

import os
import sys
import json
import re
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

JARVIS_DIR = Path(r"C:\Users\karma\JARVIS")
REVIEWS_DIR = JARVIS_DIR / "youtube_reviews"
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

OPENROUTER_API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "REDACTED_API_KEY"
)


def speak(text: str):
    clean = text.replace("'", "").replace('"', '').replace('`', '').strip()
    if not clean:
        return
    ps_cmd = (
        f"Add-Type -AssemblyName System.Speech; "
        f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$synth.Rate = 1; "
        f"$synth.Speak('{clean}')"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15
        )
    except Exception:
        pass


def extract_video_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"youtube\.com\/shorts\/([0-9A-Za-z_-]{11})"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def get_video_info(url: str) -> Dict[str, Any]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


def get_transcript(video_id: str) -> str:
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        entries = None
        for t in transcript_list:
            if t.language_code.startswith("en"):
                entries = t.fetch()
                break
        if entries is None:
            first = next(iter(transcript_list))
            entries = first.fetch()

        lines = []
        for e in entries:
            txt = getattr(e, "text", None) or (e.get("text") if isinstance(e, dict) else str(e))
            if txt:
                lines.append(txt)
        return " ".join(lines)
    except Exception as e:
        return f"[Transcript unavailable: {e}]"


def analyze_with_ai(title: str, channel: str, transcript: str, description: str) -> str:
    prompt = f"""
You are Mr. Wilson, Woods' sharp, loyal Australian female sovereign AI co-pilot.
Provide a high-impact, structured intelligence review of this YouTube content for Woods.

Title: {title}
Channel: {channel}
Description: {description[:500]}
Transcript Snippet: {transcript[:4000]}

Format your review in Markdown with:
1. 🎯 Executive Verdict (1-2 sentences: is this worth Woods' time?)
2. 🔑 Core Takeaways (3-5 punchy bullet points)
3. 🛠️ Actionable Tactics / Architecture (key implementations or tools mentioned)
4. ⚡ Co-Pilot Rationale (how this applies to Woods' empire & workflows)
"""

    # 1. Try OpenRouter
    import urllib.request
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "google/gemma-4-26b-a4b-it:free",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    # 2. Local Ollama fallback
    try:
        ollama_url = "http://localhost:11434/api/chat"
        body = {
            "model": "deepseek-r1:8b",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        req = urllib.request.Request(ollama_url, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data.get("message", {}).get("content", "").strip()
            return re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    except Exception:
        pass

    return f"**Title:** {title}\n**Channel:** {channel}\n\n**Overview:**\n{description[:300]}\n\n**Transcript Preview:**\n{transcript[:400]}..."


def review_url(url: str):
    print("=" * 70)
    print(" 🎬 MR. WILSON // YOUTUBE VIDEO & PLAYLIST INTELLIGENCE REVIEWER")
    print("=" * 70)
    print(f"Target URL: {url}")
    print("[*] Fetching metadata and transcript...")

    try:
        info = get_video_info(url)
    except Exception as e:
        print(f"[!] Error extracting info: {e}")
        return

    # Check if playlist
    if "entries" in info:
        entries = list(info.get("entries", []))
        playlist_title = info.get("title", "YouTube Playlist")
        print(f"\n[+] Detected Public Playlist: '{playlist_title}' ({len(entries)} videos)")
        speak(f"Analyzing YouTube playlist {playlist_title} with {len(entries)} videos, Woods.")

        out_lines = [f"# 📺 Playlist Intelligence Dossier: {playlist_title}\n\n"]
        for i, entry in enumerate(entries[:10], 1): # Review first 10 videos
            v_title = entry.get("title", "Untitled")
            v_url = entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
            print(f"  [{i}/{min(len(entries), 10)}] Reviewing: {v_title[:50]}...")
            vid = entry.get("id") or extract_video_id(v_url)
            transcript = get_transcript(vid) if vid else ""
            review = analyze_with_ai(v_title, entry.get("uploader", "Unknown"), transcript, entry.get("description", ""))

            out_lines.append(f"## {i}. {v_title}\n**Link:** {v_url}\n\n{review}\n\n---\n")

        report_file = REVIEWS_DIR / f"Playlist_Review_{re.sub(r'[^a-zA-Z0-9]', '_', playlist_title)[:40]}.md"
        report_file.write_text("\n".join(out_lines), encoding="utf-8")
        print(f"\n[OK] Full Playlist Dossier written to: {report_file}")
        speak(f"Playlist dossier ready, Woods. Review saved to vault.")
        os.startfile(str(report_file))

    else:
        # Single video
        title = info.get("title", "Untitled Video")
        channel = info.get("uploader", "Unknown Channel")
        vid = info.get("id") or extract_video_id(url)
        print(f"\n[+] Video: {title}")
        print(f"[+] Channel: {channel}")
        
        speak(f"Reviewing video: {title}, Woods.")
        transcript = get_transcript(vid) if vid else ""
        print(f"[+] Transcript retrieved: {len(transcript)} chars")

        review = analyze_with_ai(title, channel, transcript, info.get("description", ""))
        
        report_file = REVIEWS_DIR / f"Video_Review_{re.sub(r'[^a-zA-Z0-9]', '_', title)[:40]}.md"
        report_content = f"# 🎬 YouTube Intelligence Review: {title}\n**Channel:** {channel}\n**URL:** {url}\n\n{review}"
        report_file.write_text(report_content, encoding="utf-8")

        print("\n" + "=" * 70)
        print(review)
        print("=" * 70)
        print(f"\n[OK] Review saved to: {report_file}")
        
        # Speak the first verdict line
        first_line = [l for l in review.split("\n") if l.strip() and not l.startswith("#")][:1]
        if first_line:
            speak(f"Review complete, Woods. {first_line[0]}")
        
        os.startfile(str(report_file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Intel Reviewer")
    parser.add_argument("url", nargs="?", default="", help="YouTube video or playlist URL")
    args = parser.parse_args()

    target = args.url
    if not target:
        target = input("Enter YouTube URL (Video or Playlist): ").strip()
    if target:
        review_url(target)
    else:
        print("[!] No URL provided.")
