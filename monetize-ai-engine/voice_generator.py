"""
Free Neural Voiceover Generator for AutoMonetize AI
Uses Edge-TTS for 100% free high-quality voiceover generation ($0 API cost).
"""

import os
import sys
import json
import asyncio
import edge_tts

AVAILABLE_VOICES = [
    {"id": "en-US-ChristopherNeural", "name": "Christopher (US Male - Deep & Energetic)", "gender": "Male"},
    {"id": "en-US-JennyNeural", "name": "Jenny (US Female - Natural & Clear)", "gender": "Female"},
    {"id": "en-US-GuyNeural", "name": "Guy (US Male - Professional & Trustworthy)", "gender": "Male"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (British Female - Elegant)", "gender": "Female"}
]

async def _synthesize_async(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_voiceover(text, voice="en-US-ChristopherNeural", output_filename="audio_narration.mp3"):
    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(out_dir, output_filename)
    
    if not text or len(text.strip()) == 0:
        text = "Welcome to AutoMonetize AI. Discover, build, and monetize profitable software applications on autopilot."

    asyncio.run(_synthesize_async(text, voice, output_path))
    
    return {
        "success": True,
        "audio_url": f"/{output_filename}",
        "voice_used": voice,
        "char_count": len(text)
    }

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "This is a test of the AutoMonetize AI neural voice engine."
    res = generate_voiceover(t)
    print(json.dumps(res, indent=2))
