# God Mode: Ultimate AI Empire Dashboard

You have a comprehensive "Central Portal" dashboard set up. Here is how to use it and what I've configured for you.

## 🚀 Launching the Dashboard

1.  Run `START_GOD_MODE.bat` in your root directory.
2.  Select **Option 1** (Launch God Mode).
3.  The dashboard will open at `http://localhost:3142`.

## 🧠 Features & Tools

### 1. Central Portal (The Dashboard)
This dashboard integrates all your projects, agents, and tools.
-   **System Tools:** Manage your AI environment.
-   **Project Hub:** View and launch your coding projects.
-   **Neural Pipeline:** Monitor data flows.

### 2. ChatGPT Sorter (Two Options)
I have configured two ways to sort your ChatGPT exports:
-   **Sorter Pro Tab:** In the dashboard, go to the "Sorter Pro" tab. You can **upload your `conversations.json` file directly**, and it will organize your chats, extract code blocks, and separate prompts into folders on your Desktop (`Sorted_AI_Knowledge`).
-   **Advanced Python Sorter:** In the "System Tools" tab, the "ChatGPT Sorter" button is now linked to your advanced Python script (`chatgptproj/scripts/chatgpt_sorter_advanced.py`). *Note: This requires manual file path input currently.*

### 3. AI Voice Assistant
-   **God-Mode AI Tab:** This tab features a voice-activated AI assistant. Ensure your microphone is enabled. It uses the `useVoiceAssistant` hook connected to your browser's speech recognition.

### 4. Code & Projects
-   **Code Forge:** A built-in code editor and refactorer.
-   **Project Hub:** Scans your directory for projects (Node.js, Python) and lets you launch them.

### 5. Monetization & Influencer
-   **Influencer Studio:** Generate content for Instagram, X, etc.
-   **Music War Room:** Manage and distribute your music tracks.

## 🛠️ Configuration Updates
I have updated the system configuration (`route.ts`) to correctly point to your local scripts:
-   **YouTube Tools:** Linked to `projects/ACTIVE/youtube_enhancement_tools/youtube_enhancement_tools.py`
-   **ChatGPT Sorter:** Linked to `chatgptproj/scripts/chatgpt_sorter_advanced.py`

## ⚠️ Important Note
Your disk space is running low (`ENOSPC` error). Please clear some space (e.g., delete `07_CACHE_TEMP` or old downloads) to ensure the dashboard and tools run smoothly.
