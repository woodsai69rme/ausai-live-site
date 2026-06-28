# ✅ Enhancements Applied - 2026-05-08

## Completed Upgrades

| Component | Before | After |
|-----------|--------|-------|
| **OpenClaw** | 2026.4.27 | **2026.5.6** ✅ |
| **file-transfer plugin** | Not installed | **Enabled** ✅ |
| **Stale plugins** | 4 errors | **Removed** ✅ |
| **Config** | Invalid | **Validated** ✅ |
| **Daemon** | Running old | **Restarted** ✅ |

## New Capabilities

### `/steer` Command
Redirect active agent sessions without restart:
```
/steer Focus on the database schema instead
```

### `/side` Command
Ask questions mid-session:
```
/side What's the time complexity of this algorithm?
```

### file-transfer Plugin
Binary file operations on paired nodes:
- `file_fetch` - Pull files from paired node
- `dir_list` - List remote directory contents
- `dir_fetch` - Fetch entire directories
- `file_write` - Write files to paired node

## Quick Test Commands

```powershell
# Verify installation
openclaw --version                              # 2026.5.6
openclaw plugins list | findstr file-transfer   # enabled
openclaw config validate                        # Config valid

# Run enhanced agent
openclaw agents add test
openclaw agent --agent test
# Then try: /steer Write tests first
```

## All Free Options Still Work

- `ollama run qwen2.5-coder:latest` (coding)
- `python start.py` (Tadpole music)
- `python main.py` (ComfyUI video)
- `cd hermes-agent; uv run python run_agent.py` (self-improving)