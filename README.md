# ReelAgent: Autonomous AI Reel Generator

ReelAgent is a completely free, open-source, and self-hosted system that architects, scripts, visualizes, narrates, edits, and posts Instagram Reels automatically.

## 🏗 Architecture

The system follows a modular microservice-like architecture (monolith code, modular logic) utilizing local AI models.

```mermaid
graph TD
    User[Dashboard Frontend] -->|New Topic| API[FastAPI Backend]
    API -->|Bg Task| Pipeline[Content Pipeline]
    
    subgraph "AI Core (Local)"
        Pipeline -->|Script| Ollama[Ollama (Llama 3)]
        Pipeline -->|Voice| TTS[Edge-TTS (Azure Filter)]
        Pipeline -->|Visuals| SD[Stable Diffusion (Diffusers)]
    end
    
    subgraph "Assembly"
        Pipeline -->|Editing| MoviePy[MoviePy Engine]
        MoviePy -->|Result| Storage[./generated]
    end
```

## 🛠 Tech Stack

- **Frontend**: React, Vite, Vanilla CSS (Premium Glassmorphism).
- **Backend**: Python 3.10+, FastAPI, SQLite (In-Memory/File).
- **AI Models**:
    - **LLM**: [Ollama](https://ollama.com/) (running `llama3` or `mistral`).
    - **Image**: [Stable Diffusion v1.5](https://huggingface.co/runwayml/stable-diffusion-v1-5) (via `diffusers`).
    - **Voice**: `edge-tts` (Microsoft Edge Online TTS - Free, no token required).
- **Video**: `moviepy` (programmatic editing).

## 📂 Project Structure

```
D:/reelagent/
├── backend/
│   ├── core/           # Config & Settings
│   ├── services/       # AI Modules
│   │   ├── generator_script.py
│   │   ├── generator_image.py
│   │   ├── generator_audio.py
│   │   └── video_editor.py
│   ├── main.py         # API Entry Point
│   ├── models.py       # Data Schemas
│   └── requirements.txt
├── frontend/
│   ├── src/            # React Code
│   ├── package.json
│   └── vite.config.js
├── generated/          # Output Videos
└── data/               # Persistent Storage
```

## 🚀 Setup Instructions

### 1. Prerequisites
- **Python 3.10+** installed.
- **Node.js 18+** installed.
- **Ollama** installed and running (`ollama serve`). 
    - Pull the model: `ollama pull llama3`

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
# If using GPU for images, ensure CUDA is installed and install torch linked to CUDA.
python main.py
```
*Backend will run on http://localhost:8000*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend will run on http://localhost:5173*

### 4. Running the Pipeline
1. Open the dashboard at `http://localhost:5173`.
2. Enter a topic (e.g., "Future of Space Hotels").
3. Click **GENERATE REEL**.
4. Watch the progress in the "Active Pipelines" list.
5. The final result will be saved in `D:/reelagent/generated/{job_id}/final.mp4`.

## 🤖 Automation (Cron)
To run this autonomously every day:
1. Create a simple script `daily_run.py` that POSTs to `http://localhost:8000/jobs` with a trending topic.
2. Schedule it via Windows Task Scheduler or Cron:
   `0 9 * * * python D:/reelagent/cron/daily_run.py`

## 📊 Analytics & Posting
- **Posting**: The architecture includes the `instagram_publisher` abstract. To enable real posting, register for a Meta Developer account and add your Access Token in `.env`.
- **Analytics**: Can be added by polling the Media Insights endpoint of the Instagram Graph API.

## ⚠️ Hardware Note
- **Image Generation**: Uses CPU by default in the provided mock/stub to ensure it runs everywhere. Uncomment lines in `backend/services/generator_image.py` to enable GPU acceleration with `diffusers`.
