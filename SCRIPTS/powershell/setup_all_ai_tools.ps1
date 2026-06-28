# === COMPLETE SETUP FOR FREE LOCAL AI CODING & VIBE CODING ===
# Run these commands in PowerShell as Administrator (if needed)

echo "=== STEP 1: VERIFY SYSTEM ==="
node --version
npm --version
python --version
git --version
ollama --version

echo ""
echo "=== STEP 2: INSTALL OPENCLAW ==="
# Method A: Git clone (recommended for control)
git clone https://github.com/openclaw/openclaw.git
cd openclaw
npm install
npm run build
npx openclaw onboard --install-daemon

echo ""
echo "=== STEP 3: INSTALL HERMES AGENT ==="
# Method: Installer script (requires uv)
powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
.\setup-hermes.sh
cd ..

echo ""
echo "=== STEP 4: PULL LOCAL MODELS ==="
ollama pull llama3.2:3b
ollama pull qwen2.5-coder:7b
ollama pull hermes3:8b
ollama pull dolphin:7b
ollama pull qwen3:8b

echo ""
echo "=== STEP 5: INSTALL SKILLS CLI ==="
npm install -g @lobehub/market-cli
# Or use npx directly: npx @lobehub/market-cli skills search "react"

echo ""
echo "=== STEP 6: INSTALL SKILLS ==="
# Search for skills
npx skills find "react"
npx skills find "deployment"
npx skills find "testing"

# Install top skills
npx skills add vercel-labs/agent-skills
npx skills add microsoft/azure-skills
npx skills add firecrawl/firecrawl-cli
npx skills add supabase/supabase

echo ""
echo "=== STEP 7: SETUP N8N ==="
# Requires Docker Desktop installed
docker pull n8nio/n8n
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n

echo ""
echo "=== STEP 8: INSTALL LOCAL MUSIC ==="
git clone https://github.com/proximasan/tadpole-studio.git
cd tadpole-studio
python start.py

echo ""
echo "=== STEP 9: OPENROUTER CONFIG ==="
echo "Create .env file with:"
echo "OPENROUTER_API_KEY=sk-or-v1-..."
echo "OPENROUTER_DEFAULT_MODEL=openrouter/free"
echo ""
echo "Then test:"
echo "curl https://openrouter.ai/api/v1/chat/completions -H \"Authorization: Bearer \$OPENROUTER_API_KEY\" -H \"Content-Type: application/json\" -d '{\"model\":\"openrouter/free\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}'"

echo ""
echo "=== STEP 10: UPDATE SYSTEM PATH ==="
echo "Add these to PATH if not present:"
echo "C:\Users\karma\AppData\Local\pnpm"
echo "C:\Users\karma\.local\bin (for Hermes)"
echo "%APPDATA%\Python\Python313\Scripts (for pip installs)"

echo ""
echo "=== ALL DONE! ==="
echo "Next: Run 'openclaw onboard' or 'hermes' to start!"
