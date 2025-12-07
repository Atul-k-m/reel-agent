from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import asyncio
from datetime import datetime

from models import JobCreate, JobDB, TaskStatus, Job
from services.generator_script import generate_script
from services.generator_image import generate_image
from services.generator_audio import generate_audio
from services.video_editor import assemble_reel
from core.config import settings

app = FastAPI(title="ReelAgent API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_job(job_id: str):
    """
    Background task to execute the pipeline.
    """
    job = JobDB.get(job_id)
    if not job:
        return

    # 1. SCRIPT
    JobDB.update(job_id, status=TaskStatus.SCRIPTING)
    JobDB.add_log(job_id, f"Input Topic: {job.topic}")
    
    JobDB.add_log(job_id, "Generating Script via Ollama...")
    scenes, used_prompt = generate_script(job.topic, job.scene_count, job_id)
    JobDB.add_log(job_id, f"Used Script Prompt: {used_prompt}")
    
    if not scenes:
        JobDB.update(job_id, status=TaskStatus.FAILED, error_msg="Script generation failed")
        JobDB.add_log(job_id, "ERROR: Script generation returned empty.")
        return
        
    JobDB.update(job_id, script=scenes)
    JobDB.add_log(job_id, f"Script generated with {len(scenes)} scenes.")

    # 2. VISUALS & AUDIO
    JobDB.update(job_id, status=TaskStatus.VISUALIZING)
    
    # Create a sanitized folder name from the topic
    import re
    sanitized_topic = re.sub(r'[^a-zA-Z0-9]', '_', job.topic.lower())[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{sanitized_topic}_{timestamp}"
    
    job_dir = os.path.join(settings.GENERATED_DIR, folder_name)
    os.makedirs(job_dir, exist_ok=True)
    
    # Process scenes sequentially
    updated_scenes = []
    for i, scene in enumerate(scenes):
        # Image
        try:
            img_path = os.path.join(job_dir, f"scene_{i}.png")
            # Apply Image Style
            styled_prompt = f"{scene.visual_prompt}, {job.image_style} style, high quality, 8k"
            JobDB.add_log(job_id, f"Scene {i+1}: Generating Image: '{styled_prompt}'")
            generate_image(styled_prompt, img_path)
            scene.image_path = img_path
        except Exception as e:
            JobDB.add_log(job_id, f"Image failed for scene {i+1}: {e}")
            print(f"Image failed: {e}")
        
        # Audio
        try:
            audio_path = os.path.join(job_dir, f"scene_{i}.mp3")
            JobDB.add_log(job_id, f"Scene {i+1}: Generating Audio: '{scene.narration}'")
            await generate_audio(scene.narration, audio_path)
            scene.audio_path = audio_path
        except Exception as e:
            JobDB.add_log(job_id, f"Audio failed for scene {i+1}: {e}")
            print(f"Audio failed: {e}")
            
        updated_scenes.append(scene)
    
    JobDB.update(job_id, script=updated_scenes)

    # 3. EDITING
    JobDB.update(job_id, status=TaskStatus.EDITING)
    JobDB.add_log(job_id, "Assembling video clips...")
    video_path = os.path.join(job_dir, "final.mp4")
    success = assemble_reel(updated_scenes, video_path, job_id)
    
    if success:
        JobDB.update(job_id, status=TaskStatus.FINISHED, video_path=video_path)
        JobDB.add_log(job_id, "Reel created successfully!")
    else:
        JobDB.update(job_id, status=TaskStatus.FAILED, error_msg="Video assembly failed")
        JobDB.add_log(job_id, "ERROR: Video assembly failed.")

@app.post("/jobs", response_model=Job)
async def create_job(job_req: JobCreate, background_tasks: BackgroundTasks):
    job = JobDB.create(job_req)
    background_tasks.add_task(process_job, job.id)
    return job

@app.get("/jobs", response_model=list[Job])
def get_jobs():
    return list(JobDB.jobs.values())

@app.get("/")
def health_check():
    return {"status": "running", "system": "ReelAgent"}

@app.on_event("startup")
async def startup_event():
    os.makedirs(settings.GENERATED_DIR, exist_ok=True)
    print("ReelAgent Startup: Ready.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
