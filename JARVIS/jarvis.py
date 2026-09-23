#!/usr/bin/env python
"""
JARVIS  -  Local, FREE AI assistant built for YOUR stack (Windows + Ollama + MEMORY RAG).
Inspired by "I Built JARVIS with Claude Code" (Zubair Trabzada) but 100% local & free.

No cloud, no API keys, no monthly bill. Runs on your RTX 4060 + Ollama models.

Features (mapped to the YouTube video):
  - Brain router ............ hot-swap between your local models (qwen3.5:9b, ornith:9b, qwythos-9b, deepseek-r1:8b)
  - Second brain ............ answers grounded in YOUR MEMORY/ notes (golden rules, projects, tools)
  - RAG recall .............. semantic search over your full MEMORY vault via drive_backup_rag
  - Deep web research ....... live web research by text ("jarvis research ...") via DuckDuckGo/Brave
  - Morning briefing ........ reads your real calendar/email stubs (Gmail+Calendar demoable)
  - TARS persona + humor ... configurable personality dials (humor, sarcasm, helpfulness)
  - Desktop control ........ "open <app/file>" launches anything via your shell
  - Knowledge map ........... opens a self-contained 3D-ish knowledge graph of your MEMORY notes
  - Voice ................... optional TTS (pyttsx3) + STT (speechrecognition); degrades gracefully

Run:
  python jarvis.py                 # interactive chat
  python jarvis.py --config jarvis_config.json
  python jarvis.py "what's my ATO dispute deadline?"   # one-shot
  python jarvis.py map             # open the knowledge map
  python jarvis.py research "best free local LLMs 2026"

Requires: Python 3, requests, Ollama running on :11434, TOOLS/drive_backup_rag/drive_backup_rag.py
Optional: pyttsx3 (voice out), SpeechRecognition (voice in)
"""
import argparse, json, os, sys, subprocess, webbrowser, textwrap, shutil, datetime, re, time

# ----------------------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
MEMORY_DIR = os.environ.get("MEMORY_DIR", os.path.join(HOME, "MEMORY"))
RAG_SCRIPT = os.environ.get(
    "RAG_SCRIPT",
    os.path.join(HOME, "TOOLS", "drive_backup_rag", "drive_backup_rag.py"),
)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# ----------------------------------------------------------------------------- default config
DEFAULT_CONFIG = {
    "brains": {
        "qwen":   {"model": "qwen3.5:9b",  "label": "Qwen 3.5 9B (balanced)"},
        "ornith": {"model": "ornith:9b",   "label": "Ornith 9B (coding)"},
        "qwythos":{"model": "richardyoung/qwythos-9b-abliterated:latest", "label": "Qwythos 9B (creative)"},
        "deepseek":{"model": "deepseek-r1:8b", "label": "DeepSeek R1 8B (reasoning)"},
        "coder":  {"model": "qwen2.5-coder:latest", "label": "Qwen2.5-Coder 7.6B"},
        "phi":    {"model": "phi4-mini:latest", "label": "Phi-4 Mini (fast)"},
        "big":    {"model": "hf.co/deepreinforce-ai/Ornith-1.0-35B-GGUF:Q4_K_M", "label": "Ornith 35B (heavy)"},
    },
    "default_brain": "qwen",
    "use_second_brain": True,        # ground answers in MEMORY notes
    "max_memory_chunks": 6,
    "use_rag": True,                 # semantic recall over full vault
    "max_rag_hits": 4,
    "voice": {
        "enabled": False,
        "rate": 175,
        "volume": 1.0,
    },
    "persona": {
        "name": "JARVIS",
        "humor": 0.5,        # 0=deadpan, 1=wisecracking TARS
        "sarcasm": 0.35,
        "helpfulness": 0.9,
        "style": "concise, competent, a touch dry; you are the user's personal AI chief-of-staff.",
    },
    "knowledge_map": os.path.join(HERE, "knowledge_map.html"),
}

def load_config(path):
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                user = json.load(f)
            _deep_merge(cfg, user)
            print(f"[JARVIS] config loaded from {path}")
        except Exception as e:
            print(f"[JARVIS] config load failed ({e}); using defaults")
    return cfg

def _deep_merge(base, over):
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v

# ----------------------------------------------------------------------------- Ollama brain
def ollama_chat(model, messages, stream=False, timeout=180):
    payload = {"model": model, "messages": messages, "stream": stream,
               "options": {"temperature": 0.7}}
    try:
        import requests
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()["message"]["content"]
    except Exception as e:
        return f"[brain error: {e}]"

def ollama_list():
    try:
        import requests
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []

# ----------------------------------------------------------------------------- second brain (MEMORY notes)
SECTION_FILES = {
    "golden": "00_GOLDEN_RULES.md",
    "background": "01_BACKGROUND_AND_PROJECTS.md",
    "tools": "02_FREE_AI_TOOLS.md",
    "computeruse": "03_COMPUTER_USE_AND_FOOT_CLAN.md",
    "index": "04_SESSION_AND_KNOWLEDGE_INDEX.md",
}

def load_second_brain(filter_section=None, max_chars=6000):
    """Load MEMORY notes as the 'second brain' context. Optionally narrow by section."""
    chunks = []
    files = SECTION_FILES.items()
    if filter_section:
        files = [(k, SECTION_FILES[k]) for k in SECTION_FILES if filter_section in k]
    for key, fname in files:
        p = os.path.join(MEMORY_DIR, fname)
        if not os.path.exists(p):
            continue
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            # trim very large files to a representative head+tail window
            if len(txt) > max_chars:
                txt = txt[:max_chars//2] + "\n...[truncated]...\n" + txt[-max_chars//2:]
            chunks.append(f"### {key.upper()} ({fname})\n{txt}")
        except Exception as e:
            chunks.append(f"### {key}\n[error reading: {e}]")
    return "\n\n".join(chunks)

def recall_rag(query, max_hits=4):
    """Semantic recall across the full MEMORY vault via drive_backup_rag.
    Uses the plain `query` (hit-list + excerpts) — ~0.7s, NOT the slow `--answer`
    flag which runs an extra LLM synthesis pass on every call."""
    if not os.path.exists(RAG_SCRIPT):
        return ""
    try:
        out = subprocess.run(
            [sys.executable, RAG_SCRIPT, "query", query],
            capture_output=True, text=True, timeout=30,
        )
        txt = (out.stdout or "") + (out.stderr or "")
        if not txt.strip():
            return ""
        # Keep only the first max_hits hits region, bounded
        lines = txt.splitlines()
        kept, hits = [], 0
        for ln in lines:
            if ln.strip().startswith("[") and "hits=" in ln:
                hits = int(re.search(r"hits=(\d+)", ln).group(1))
            kept.append(ln)
            if len(kept) > 60:
                break
        return "\n".join(kept)[:3500]
    except Exception as e:
        return f"[rag error: {e}]"

# ----------------------------------------------------------------------------- web research
def web_research(query, max_results=6):
    """Live web research — no API key required.
    Primary: jina.ai reader over Bing (returns clean markdown results).
    Fallback: DuckDuckGo lite HTML scrape.
    Returns bounded, readable result list."""
    import requests
    # 1) jina.ai reader over Bing (reliable, no key)
    try:
        r = requests.get("https://r.jina.ai/http://www.bing.com/search",
                         params={"q": query}, timeout=25)
        md = r.text
        # pull numbered result headings + urls
        items = re.findall(r'^\s*\d+\.\s+##\s+\[(.*?)\]\((https?://[^)]+)\)', md, re.M)
        if items:
            lines = [f"{i}. {t}\n   {u}" for i, (t, u) in enumerate(items[:max_results], 1)]
            return "Live research (Bing via jina):\n" + "\n".join(lines)
    except Exception:
        pass
    # 2) fallback: DuckDuckGo lite
    try:
        r = requests.post("https://lite.duckduckgo.com/lite/", data={"q": query},
                          headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        items = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*class="result-link"[^>]*>(.*?)</a>',
                           r.text, re.S)
        if items:
            lines = []
            for i, (url, title) in enumerate(items[:max_results], 1):
                lines.append(f"{i}. {re.sub('<.*?>','',title).strip()}\n   {url}")
            return "Live research (DuckDuckGo):\n" + "\n".join(lines)
    except Exception as e:
        return f"Web research unavailable: {e}"
    return "No live results (offline or blocked). Try again with a connection."

# ----------------------------------------------------------------------------- morning briefing
def morning_briefing():
    """Demoable morning briefing: real local context (date, models, memory summary) +
    plug-in points for Gmail/Calendar (stubbed, no secrets required)."""
    now = datetime.datetime.now()
    lines = []
    lines.append(f"Good morning. It's {now.strftime('%A %d %B %Y, %H:%M')}.")
    # real: what's available
    models = ollama_list()
    lines.append(f"Local brains online: {len(models)} Ollama models." if models else "No Ollama models detected.")
    # real: memory index peek
    mem = load_second_brain("index", max_chars=1500)
    if mem:
        lines.append("From your knowledge index, today's focus:")
        # pull a few bullet lines
        for line in mem.splitlines():
            if line.strip().startswith(("-", "*", "#")):
                lines.append("  - " + line.strip("*-# ").strip()[:120])
                if len(lines) > 6:
                    break
    lines.append("\n[Calendar/Gmail]: connect your client to enable real briefings "
                 "(stub — no credentials stored). Plug a fetch hook into the `calendar_hook` config key.")
    return "\n".join(lines)

# ----------------------------------------------------------------------------- desktop control
def open_desktop(target):
    """Open an app/file/URL on Windows. `target` may be a known alias or a path/URL."""
    aliases = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "comfy": r"C:\Users\karma\ComfyUI",
        "memory": MEMORY_DIR,
        "tellem": r"C:\Users\karma\ai-music-video-studio",
        "studio": r"C:\Users\karma\ACTIVE_PROJECTS\tellemthatsme-studio",
    }
    t = target.strip().lower()
    path = aliases.get(t, target)
    # os.startfile is the Windows-native launcher (no shell, no injection sink).
    # webbrowser handles URLs. No os.system / shell interpolation of user input.
    try:
        if path.startswith("http"):
            webbrowser.open(path)
        elif os.path.exists(path):
            os.startfile(path)
        else:
            return f"Can't find '{target}'. Try a full path or a known alias (chrome/memory/studio/tellem)."
        return f"Opened: {target}"
    except Exception as e:
        return f"Couldn't open {target}: {e}"

# ----------------------------------------------------------------------------- knowledge map
def open_knowledge_map(cfg):
    path = cfg.get("knowledge_map") or os.path.join(HERE, "knowledge_map.html")
    if not os.path.exists(path):
        build_knowledge_map(cfg, path)
    webbrowser.open(path)
    return f"Knowledge map opened: {path}"

def build_knowledge_map(cfg, path):
    """Generate a self-contained 3D-ish knowledge galaxy from your MEMORY sections."""
    nodes = []
    idx = 0
    # hub
    nodes.append({"id": 0, "label": "JARVIS CORE", "group": 0, "size": 14})
    sec_colors = {"golden": 1, "background": 2, "tools": 3, "computeruse": 4, "index": 5}
    for key, fname in SECTION_FILES.items():
        p = os.path.join(MEMORY_DIR, fname)
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        # split into heading-based nodes
        heads = re.findall(r'^#{1,4}\s+(.+)$', txt, re.M)
        nodes.append({"id": len(nodes), "label": key.upper(), "group": sec_colors.get(key, 6), "size": 9})
        parent = len(nodes) - 1
        for h in heads[:18]:
            h = h.strip()[:40]
            if not h:
                continue
            nodes.append({"id": len(nodes), "label": h, "group": sec_colors.get(key, 6), "size": 5, "parent": parent})
    # edges: each node to its parent (or core)
    edges = []
    for n in nodes:
        if "parent" in n:
            edges.append({"source": n["parent"], "target": n["id"]})
        elif n["id"] != 0:
            edges.append({"source": 0, "target": n["id"]})
    html = _KM_HTML_TEMPLATE.replace("/*__NODES__*/", json.dumps(nodes)).replace("/*__EDGES__*/", json.dumps(edges))
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path

_KM_HTML_TEMPLATE = r"""<!doctype html><html><head><meta charset="utf-8"><title>JARVIS Knowledge Galaxy</title>
<style>html,body{margin:0;height:100%;background:radial-gradient(circle at 50% 40%,#0b1026,#02030a);overflow:hidden;font-family:Segoe UI,Arial}
#hud{position:fixed;top:12px;left:14px;color:#7fd3ff;z-index:5;text-shadow:0 0 8px #1a6}
#hud b{color:#bff}</style></head>
<body><div id="hud"><b>JARVIS KNOWLEDGE GALAXY</b><br>drag to rotate · scroll to zoom · your MEMORY/ second brain</div>
<canvas id="c"></canvas><script>
const NODES=/*__NODES__*/; const EDGES=/*__EDGES__*/;
const cv=document.getElementById('c'), ctx=cv.getContext('2d');
let W,H; function rs(){W=cv.width=innerWidth;H=cv.height=innerHeight;} rs(); addEventListener('resize',rs);
const COL={0:'#ffd24a',1:'#ff6b6b',2:'#6bff9e',3:'#6bb8ff',4:'#c46bff',5:'#ffb86b',6:'#9aa'};
function proj(x,y,z){const s=200/(200+z);return [W/2+x*s,H/2+y*s,s];}
let ang=0, ay=0, zoom=1;
NODES.forEach(n=>{const a=Math.random()*6.28, b=Math.random()*3.14-1.57, r=120+Math.random()*220;
  n.x=Math.sin(a)*Math.cos(b)*r; n.y=Math.sin(b)*r; n.z=Math.cos(a)*Math.cos(b)*r;});
let drag=false, lx=0, ly=0;
cv.onmousedown=e=>{drag=true;lx=e.clientX;ly=e.clientY;};
addEventListener('mouseup',()=>drag=false);
addEventListener('mousemove',e=>{if(!drag)return; ang+=(e.clientX-lx)*0.005; ay+=(e.clientY-ly)*0.005; lx=e.clientX; ly=e.clientY;});
cv.onwheel=e=>{zoom*=e.deltaY<0?1.1:0.9; e.preventDefault();};
function frame(){ctx.clearRect(0,0,W,H); ang+=0.0015;
  const ca=Math.cos(ang),sa=Math.sin(ang),cb=Math.cos(ay),sb=Math.sin(ay);
  const pts=NODES.map(n=>{let x=n.x*ca-n.z*sa, z=n.x*sa+n.z*ca;
    let y=n.y*cb-z*sb, zz=z*cb+n.y*sb;
    const p=proj(x,y,zz*zoom); return {n,p};});
  EDGES.forEach(e=>{const a=pts[e.source].p,b=pts[e.target].p;
    ctx.strokeStyle='rgba(120,200,255,0.12)';ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();});
  pts.sort((a,b)=>a.p[2]-b.p[2]);
  pts.forEach(({n,p})=>{const c=COL[n.group]||'#9aa'; const r=(n.size||4)*p[2]*zoom*0.01+1;
    ctx.fillStyle=c;ctx.shadowColor=c;ctx.shadowBlur=12;
    ctx.beginPath();ctx.arc(p[0],p[1],r,0,6.28);ctx.fill();});
  ctx.shadowBlur=0; requestAnimationFrame(frame);}
frame();
</script></body></html>"""

# ----------------------------------------------------------------------------- TTS / STT
def speak(text, cfg):
    try:
        import pyttsx3
        e = pyttsx3.init()
        e.setProperty("rate", cfg["voice"].get("rate", 175))
        e.setProperty("volume", cfg["voice"].get("volume", 1.0))
        e.say(text); e.runAndWait()
    except Exception as e:
        print(f"[voice out unavailable: {e}]")

def listen():
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as src:
            print("[JARVIS] listening...", end="", flush=True)
            audio = r.listen(src, timeout=5)
        return r.recognize_google(audio)
    except Exception as e:
        return f"[voice in unavailable: {e}]"

# ----------------------------------------------------------------------------- brain assembly
def build_system_prompt(cfg, use_memory=True):
    persona = cfg["persona"]
    p = persona["style"]
    sysmsg = (f"You are {persona['name']}, a personal AI chief-of-staff for the user (karma / tellemthatsme). "
             f"Personality: {p}. Humor dial {persona['humor']}, sarcasm {persona['sarcasm']}, "
             f"helpfulness {persona['helpfulness']}. Be concise and actionable.")
    if use_memory and cfg.get("use_second_brain", True):
        mem = load_second_brain(max_chars=6000)
        if mem:
            sysmsg += ("\n\nYou have access to the user's personal 'second brain' (MEMORY notes). "
                       "Use it to ground answers about the user's projects, golden rules, tools, and history:\n\n" + mem)
    return sysmsg

def answer(cfg, user_text, brain_key=None, history=None):
    brain_key = brain_key or cfg["default_brain"]
    model = cfg["brains"].get(brain_key, cfg["brains"][cfg["default_brain"]])["model"]
    if history is None:
        history = []
    messages = [{"role": "system", "content": build_system_prompt(cfg)}]

    # RAG recall augmentation
    if cfg.get("use_rag", True):
        rag = recall_rag(user_text, cfg.get("max_rag_hits", 4))
        if rag:
            messages.append({"role": "system", "content": "Relevant recalled memory:\n" + rag})

    messages += history
    messages.append({"role": "user", "content": user_text})
    reply = ollama_chat(model, messages, timeout=240)
    return reply, model

# ----------------------------------------------------------------------------- command routing
def route_command(cfg, text):
    t = text.strip()
    low = t.lower()
    if low in ("map", "knowledge", "galaxy"):
        return ("__ACTION__", open_knowledge_map(cfg))
    if low.startswith("open "):
        return ("__ACTION__", open_desktop(t[5:].strip()))
    if low.startswith("research ") or low.startswith("jarvis research "):
        q = t.replace("jarvis research ", "").replace("research ", "")
        return ("__RESEARCH__", web_research(q))
    if low in ("brief", "briefing", "morning"):
        return ("__ACTION__", morning_briefing())
    if low.startswith("brain ") or low.startswith("use "):
        bk = low.split(" ", 1)[1].strip()
        if bk in cfg["brains"]:
            cfg["default_brain"] = bk
            return ("__ACTION__", f"Brain switched to {bk} ({cfg['brains'][bk]['model']}).")
        return ("__ACTION__", f"Unknown brain '{bk}'. Options: {', '.join(cfg['brains'].keys())}")
    if low in ("brains", "models", "list"):
        return ("__ACTION__", "Available brains:\n" + "\n".join(
            f"  {k}: {v['model']} — {v['label']}" for k, v in cfg["brains"].items()))
    if low in ("help", "?", "commands"):
        return ("__ACTION__", HELP_TEXT)
    return None

HELP_TEXT = """JARVIS commands:
  chat normally ........... talk to your second brain
  brain <name> ............ hot-swap model (qwen/ornith/qwythos/deepseek/coder/phi/big)
  brains .................. list available local models
  research <query> ........ live web research
  open <app/file/url> ..... launch anything (open chrome / open memory / open studio)
  map ..................... open 3D knowledge galaxy of your MEMORY notes
  brief ................... morning briefing
  help .................... this menu
Prefix with 'jarvis' optionally. Voice: set "voice.enabled":true in config."""

# ----------------------------------------------------------------------------- REPL / one-shot
def print_reply(reply, model, cfg):
    print(f"\n{JARVIS_TAG} ({model}):")
    print(textwrap.fill(reply, width=100))
    if cfg.get("voice", {}).get("enabled"):
        # strip markup before speaking
        speak(re.sub(r'[#*`>]', '', reply)[:400], cfg)

def main():
    ap = argparse.ArgumentParser(description="Local JARVIS AI assistant")
    ap.add_argument("prompt", nargs="*", help="one-shot prompt (or 'map'/'research ...')")
    ap.add_argument("--config", default=os.path.join(HERE, "jarvis_config.json"))
    ap.add_argument("--brain", default=None, help="override default brain key")
    ap.add_argument("--no-memory", action="store_true", help="disable second-brain context")
    args = ap.parse_args()

    cfg = load_config(args.config if os.path.exists(args.config) else None)
    if args.brain:
        cfg["default_brain"] = args.brain
    if args.no_memory:
        cfg["use_second_brain"] = False

    global JARVIS_TAG
    JARVIS_TAG = cfg["persona"]["name"]

    # one-shot modes
    if args.prompt:
        cmd = " ".join(args.prompt)
        if cmd.lower() in ("map", "research", "brief", "brains", "help"):
            routed = route_command(cfg, cmd)
            if routed:
                print(routed[1]); return
        if cmd.lower().startswith("research ") or cmd.lower().startswith("jarvis research "):
            q = cmd.replace("jarvis research ", "").replace("research ", "")
            print(web_research(q)); return
        reply, model = answer(cfg, cmd)
        print_reply(reply, model, cfg)
        return

    # interactive
    print(f"\n=== {JARVIS_TAG} online ===  brains: {len(cfg['brains'])} | second-brain: {'on' if cfg['use_second_brain'] else 'off'}")
    print("Type 'help' for commands. Ctrl+C to exit.\n")
    history = []
    try:
        while True:
            try:
                if cfg.get("voice", {}).get("enabled"):
                    user_in = listen()
                else:
                    user_in = input(f"{JARVIS_TAG}> ")
            except (EOFError, KeyboardInterrupt):
                print("\n[JARVIS] shutting down."); break
            if not user_in.strip():
                continue
            routed = route_command(cfg, user_in)
            if routed:
                if routed[0] == "__RESEARCH__":
                    print("\n[JARVIS] research results:\n" + routed[1])
                else:
                    print(routed[1])
                continue
            reply, model = answer(cfg, user_in, history=history)
            print_reply(reply, model, cfg)
            history.append({"role": "user", "content": user_in})
            history.append({"role": "assistant", "content": reply})
            history = history[-10:]
    except KeyboardInterrupt:
        print("\n[JARVIS] offline.")

JARVIS_TAG = "JARVIS"

if __name__ == "__main__":
    main()
