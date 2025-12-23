# ReelAgent: Autonomous AI Reel Generator

ReelAgent is a completely free, open-source, and self-hosted system that architects, scripts, visualizes, narrates, edits, and posts Instagram Reels automatically.

## 🏗 Architecture

The system follows a modular microservice-like architecture (monolith code, modular logic).

```mermaid
graph TD
    User[Dashboard Frontend] -->|New Topic| API[FastAPI Backend]
    API -->|Bg Task| Pipeline[Content Pipeline]
    
    subgraph "AI Core (Local/Hybrid)"
        Pipeline -->|Script| Ollama[Ollama (Llama 3)]
        Pipeline -->|Voice| TTS[Edge-TTS / Piper]
        Pipeline -->|Visuals| IMG[Pollinations / Stable Diffusion]
    end
    
    subgraph "Assembly"
        Pipeline -->|Editing| Remotion[Remotion (React Video)]
        Remotion -->|Render| Chromium[Chromium Headless]
        Chromium -->|Result| Storage[./generated]
    end
```

## 🛠 Tech Stack

- **Frontend**: React, Vite, Vanilla CSS (Premium Glassmorphism).
- **Video Engine**: [Remotion](https://www.remotion.dev/) (React-based Video).
- **Backend**: Python 3.10+, FastAPI.
- **AI Models**:
    - **LLM**: Ollama (Llama 3) or Groq.
    - **Image**: Pollinations AI / Stable Diffusion / HuggingFace.
    - **Voice**: Piper (Local) or Edge-TTS.

## 📂 Project Structure

```
D:/reelagent/
├── backend/
│   ├── core/           # Config & Settings
│   ├── services/       # AI Modules
│   │   ├── generator_script.py (LLM)
│   │   ├── generator_image.py (Flux/SD)
│   │   ├── generator_audio.py (TTS)
│   │   └── remotion_renderer.py (Video)
│   ├── main.py         # API Entry Point
│   └── Dockerfile      # Production Build
├── frontend/
│   ├── src/            # React Code
│   │   └── remotion/   # Video Templates (Bauhaus, Neon, etc.)
│   └── package.json
└── generated/          # Output Videos
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.10+ installed.
- Node.js 18+ installed.
- (Optional) Ollama running for local LLM.

### 2. Quick Start (Local)

**Backend**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
*Server starts at http://localhost:8000*

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
*Dashboard at http://localhost:5173*

### 3. Deployment (Render / Docker)
ReelAgent includes a `Dockerfile` for single-container deployment.
1. Push to GitHub.
2. Deploy as a **Web Service** on [Render](https://render.com).
3. The app will build both frontend and backend and serve the UI at the root URL.

## 🤖 Features
- **Cron Cleanup**: Automatically deletes generated videos older than 24 hours.
- **8+ Styles**: Bauhaus, Neon, Glitch, Minimal, and more.
- **One-Click Download**: Download rendered videos directly from the dashboard.
