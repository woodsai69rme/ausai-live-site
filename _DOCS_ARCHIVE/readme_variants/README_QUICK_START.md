# Archon Project - Quick Start Guide

## 🚀 One-Command Startup

Double-click any of these batch files to get started:

---

## 📦 Available Options

### **Option 0: `start-all.bat`** - The Everything Button ⭐
**What it does:**
- ✅ Checks and installs all dependencies
- ✅ Starts Frontend server (http://localhost:5173/)
- ✅ Starts Backend server (http://localhost:8181/)
- ✅ Opens documentation
- ✅ Creates log files

**Time:** 2-5 minutes  
**Best for:** First-time setup or when you want everything running

**Usage:**
```bash
Double-click: start-all.bat
```

---

### **Option 1: `option-1-quick-start.bat`** - Start Coding Now 🎯
**What it does:**
- ✅ Starts Frontend immediately
- ✅ Starts Backend immediately
- ✅ Opens browser automatically
- ✅ Opens VS Code (if installed)

**Time:** 30 seconds  
**Best for:** Daily development work

**Prerequisites:**
- Dependencies already installed (run `start-all.bat` first if not)

**Usage:**
```bash
Double-click: option-1-quick-start.bat
```

**Then:**
- Open http://localhost:5173/ to see the app
- Edit files in `archon-ui-main/src/` (auto-reload)
- Edit files in `python/src/` (auto-reload)

---

### **Option 2: `option-2-full-setup.bat`** - Complete Setup 🔧
**What it does:**
- ✅ Fixes all security vulnerabilities
- ✅ Updates all dependencies to latest versions
- ✅ Runs full test suite
- ✅ Builds production version
- ✅ Builds documentation
- ✅ Runs integration tests
- ✅ Creates coverage reports

**Time:** 30-60 minutes  
**Best for:** Preparing for production or after long breaks

**Usage:**
```bash
Double-click: option-2-full-setup.bat
Type Y to confirm
```

**Creates:**
- Backup branch: `backup-before-full-setup-[date]`
- Logs in: `logs/full-setup/`
- Production build in: `archon-ui-main/dist/`

---

### **Option 3: `option-3-cleanup.bat`** - Organize Project 🧹
**What it does:**
- ✅ Archives legacy code (original_archon/)
- ✅ Consolidates .env files
- ✅ Cleans temporary/cache files
- ✅ Optimizes git repository
- ✅ Generates cleanup report

**Time:** 2-5 minutes  
**Best for:** When project feels cluttered

**Safety:**
- 💾 Creates backup branch
- 📦 Moves files (doesn't delete)
- 🔄 100% reversible

**Usage:**
```bash
Double-click: option-3-cleanup.bat
Type "yes" to confirm
```

**Archives:**
- original_archon/ → ARCHIVE/original_archon-[date]/
- Old .env files → ENV_BACKUP/

---

## 🌐 Service URLs

Once servers are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173/ | React web application |
| **Backend API** | http://localhost:8181/ | FastAPI server |
| **API Docs** | http://localhost:8181/docs | Swagger documentation |
| **Health Check** | http://localhost:8181/health | Server status |
| **MCP Server** | http://localhost:8051/ | MCP protocol server |

---

## 🛠️ Manual Commands

If you prefer command line:

### Frontend (archon-ui-main/)
```bash
cd archon-ui-main

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Fix security issues
npm audit fix
```

### Backend (python/)
```bash
cd python

# Install dependencies
python -m venv .venv
.venv\Scripts\pip install -e .

# Start server
.venv\Scripts\python -m uvicorn src.server.main:app --reload --port 8181

# Run tests
.venv\Scripts\python -m pytest

# Run with coverage
.venv\Scripts\python -m pytest --cov=src
```

### Documentation (docs/)
```bash
cd docs

# Install dependencies
npm install

# Start development server
npm run start

# Build
npm run build
```

---

## 📁 Project Structure

```
C:\Users\karma\
├── archon-ui-main/          # React Frontend (Port 5173)
│   ├── src/                 # Source code
│   ├── test/                # Test files
│   └── package.json         # Dependencies
│
├── python/                   # Python Backend (Port 8181)
│   ├── src/
│   │   ├── server/          # FastAPI app
│   │   ├── agents/          # AI agents
│   │   └── mcp/             # MCP server
│   ├── tests/               # Test files
│   └── pyproject.toml       # Dependencies
│
├── docs/                     # Documentation (Docusaurus)
│   ├── docs/                # MDX files
│   └── package.json
│
├── original_archon/          # Legacy code (safe to archive)
├── migration/                # Database scripts
│
├── START_HERE.bat           # ⭐ Start here!
├── option-1-quick-start.bat # Quick dev mode
├── option-2-full-setup.bat  # Complete setup
├── option-3-cleanup.bat     # Organize project
└── start-all.bat            # Everything
```

---

## 🔧 Troubleshooting

### Frontend won't start
```bash
cd archon-ui-main
rm -rf node_modules
npm install
npm run dev
```

### Backend won't start
```bash
cd python
rm -rf .venv
python -m venv .venv
.venv\Scripts\pip install -e .
.venv\Scripts\python -m uvicorn src.server.main:app --reload
```

### Port already in use
- Frontend: Change port in `archon-ui-main/vite.config.ts`
- Backend: Change `--port 8181` to another number

### Tests failing
```bash
# Frontend
cd archon-ui-main
npm test -- --run

# Backend
cd python
.venv\Scripts\python -m pytest -v
```

---

## 📊 Current Status

✅ **Frontend**: React + Vite + TypeScript (Builds successfully)  
✅ **Tests**: 37/37 passing (100%)  
⚠️ **Security**: 6 moderate vulnerabilities (fixable)  
✅ **Backend**: FastAPI + PydanticAI (Operational)  
⚠️ **Dependencies**: Need Python 3.12+ and Node.js  

---

## 📞 Need Help?

1. **Check logs**: `logs/` directory has detailed logs
2. **Review status**: Open `PROJECT_STATUS_REPORT.md`
3. **See cleanup plan**: Open `DEVELOPMENT_ENVIRONMENT_IMPROVEMENT_PLAN_REVISED.md`
4. **Restore backup**: `git checkout backup-[date]`

---

## 🎯 Recommended Workflow

### Daily Development
1. Double-click `option-1-quick-start.bat`
2. Wait 30 seconds
3. Browser opens automatically
4. Start coding!

### After Break (1+ weeks)
1. Double-click `option-2-full-setup.bat`
2. Wait 30-60 minutes
3. Everything updated and tested
4. Ready to deploy

### When Project Grows
1. Double-click `option-3-cleanup.bat`
2. Archive old code
3. Organize files
4. Continue developing

---

## ⚡ Quick Reference

| Task | Command/File |
|------|--------------|
| Start everything | `start-all.bat` |
| Quick dev mode | `option-1-quick-start.bat` |
| Full setup | `option-2-full-setup.bat` |
| Cleanup | `option-3-cleanup.bat` |
| View app | http://localhost:5173/ |
| API docs | http://localhost:8181/docs |
| Run tests | `npm test` (frontend), `pytest` (backend) |
| Build | `npm run build` |
| Fix security | `npm audit fix` |

---

## 🎉 You're Ready!

Choose your path:
- 🚀 **Start coding**: Run `option-1-quick-start.bat`
- 🔧 **Full setup**: Run `option-2-full-setup.bat`
- 🧹 **Organize**: Run `option-3-cleanup.bat`

Happy coding! 💻

---

*Generated: February 17, 2026*  
*Version: 2.0*  
*Status: All systems operational*
