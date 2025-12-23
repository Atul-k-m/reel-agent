from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
import sys
import asyncio
from datetime import datetime, timedelta
import shutil
import traceback

# Windows subprocess fix
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# ======================================================
# PRODUCTION LOGGING UTILITIES
# ======================================================
def get_system_info() -> dict:
    """Get system resource info for debugging production issues"""
    import platform
    info = {
        "cpu_count": os.cpu_count(),
        "platform": platform.system(),
        "python": sys.version.split()[0],
        "env": "PRODUCTION" if os.environ.get("PORT") else "LOCAL",
    }
    
    # Try to get memory info (requires psutil, graceful fallback)
    try:
        import psutil
        mem = psutil.virtual_memory()
        info["memory_available_mb"] = mem.available // (1024 * 1024)
        info["memory_total_mb"] = mem.total // (1024 * 1024)
        info["memory_percent"] = mem.percent
    except ImportError:
        info["memory"] = "psutil not installed"
    except Exception as e:
        info["memory"] = f"error: {e}"
    
    return info


def log_system_info(job_id: str):
    """Log system info to job logs for debugging"""
    info = get_system_info()
    JobDB.add_log(job_id, f"[SYS] Environment: {info['env']}")
    JobDB.add_log(job_id, f"[SYS] CPUs: {info['cpu_count']}, Platform: {info['platform']}")
    
    if "memory_available_mb" in info:
        JobDB.add_log(job_id, f"[SYS] Memory: {info['memory_available_mb']}MB free / {info['memory_total_mb']}MB total ({info['memory_percent']}% used)")
    else:
        JobDB.add_log(job_id, f"[SYS] Memory: {info.get('memory', 'unavailable')}")


async def cleanup_old_jobs():
    """Cronjob: Deletes generated folders older than 24 hours"""
    while True:
        try:
            print("Running cleanup cron...")
            now = datetime.now()
            cutoff = now - timedelta(hours=24)
            
            if os.path.exists(settings.GENERATED_DIR):
                for item in os.listdir(settings.GENERATED_DIR):
                    item_path = os.path.join(settings.GENERATED_DIR, item)
                    if os.path.isdir(item_path):
                        # check modification time
                        mtime = datetime.fromtimestamp(os.path.getmtime(item_path))
                        if mtime < cutoff:
                            print(f"[Cleanup] Deleting old job: {item}")
                            shutil.rmtree(item_path, ignore_errors=True)
        except Exception as e:
            print(f"[Cleanup] Error: {e}")
            
        await asyncio.sleep(3600) # Run every hour

from models import (
    JobCreate,
    JobDB,
    TaskStatus,
    Job,
    Scene,
    DurationMode,
)

from services.generator_script import generate_script
from services.generator_image import generate_image
from services.generator_audio import generate_audio
from services.video_editor import assemble_reel
from services.duration_utils import (
    calculate_scene_durations,
    get_scene_frames,
    estimate_duration_from_text,
)

from core.config import settings

FPS = 30

app = FastAPI(title="ReelAgent API", version="1.0.0")

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Static generated files
# -------------------------
os.makedirs(settings.GENERATED_DIR, exist_ok=True)
app.mount(
    "/generated",
    StaticFiles(directory=settings.GENERATED_DIR),
    name="generated",
)


# ======================================================
# BACKGROUND PIPELINE
# ======================================================
async def process_job(job_id: str):
    """Main job processing pipeline with comprehensive error handling"""
    job = JobDB.get(job_id)
    if not job:
        return

    # Log system info at job start (critical for debugging production)
    try:
        log_system_info(job_id)
    except Exception as e:
        JobDB.add_log(job_id, f"[SYS] Error getting system info: {e}")

    # ==================================================
    # 1. SCRIPT
    # ==================================================
    JobDB.update(job_id, status=TaskStatus.SCRIPTING)
    JobDB.add_log(job_id, f"Input Topic: {job.topic}")

    try:
        scenes, used_prompt = await asyncio.to_thread(
            generate_script,
            job.topic,
            job.scene_count,
            job.duration_mode,  # duration_mode comes before job_id now
            job_id,
        )
    except Exception as e:
        JobDB.update(job_id, status=TaskStatus.FAILED, error_msg=str(e))
        JobDB.add_log(job_id, f"ERROR: Script generation crashed: {e}")
        return

    if not scenes:
        JobDB.update(job_id, status=TaskStatus.FAILED, error_msg="Script empty")
        return

    JobDB.update(job_id, script=scenes)
    JobDB.add_log(job_id, f"Generated {len(scenes)} scenes")

    # ==================================================
    # 2. CREATE JOB FOLDER
    # ==================================================
    import re

    sanitized = re.sub(r"[^a-zA-Z0-9]", "_", job.topic.lower())[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_dir = os.path.join(settings.GENERATED_DIR, f"{sanitized}_{timestamp}")
    os.makedirs(job_dir, exist_ok=True)

    # ==================================================
    # TYPOGRAPHIC / REMOTION FLOW
    # ==================================================
    if job.image_style.startswith("Typographic"):
        JobDB.update(job_id, status=TaskStatus.VISUALIZING)
        JobDB.add_log(job_id, f"Typographic mode: {job.image_style}")
        JobDB.add_log(job_id, f"Duration mode: {job.duration_mode.value}")

        # ------------------------------------------------
        # Combine narration
        # ------------------------------------------------
        full_script = " ".join(scene.narration for scene in scenes)

        # ------------------------------------------------
        # Generate AUDIO (RETURNS DURATION)
        # ------------------------------------------------
        audio_path = os.path.join(job_dir, "full_audio.mp3")

        try:
            audio_path, audio_duration = await generate_audio(
                full_script,
                audio_path,
            )
        except Exception as e:
            JobDB.update(job_id, status=TaskStatus.FAILED, error_msg=str(e))
            return

        JobDB.add_log(
            job_id,
            f"Audio generated: {audio_duration:.2f}s",
        )

        # ------------------------------------------------
        # Calculate per-scene durations (SCRIPT FIRST)
        # ------------------------------------------------
        JobDB.update(job_id, status=TaskStatus.EDITING)
        JobDB.add_log(job_id, "Calculating scene durations...")

        # ------------------------------------------------
        # Calculate per-scene durations
        # ------------------------------------------------
        # First estimate durations based on narration word count
        estimated_durations = [estimate_duration_from_text(s.narration) for s in scenes]
        total_estimated = sum(estimated_durations)
        if total_estimated > 0:
            # Scale estimated durations to match actual audio length EXACTLY
            scale_factor = audio_duration / total_estimated
            scene_durations = [d * scale_factor for d in estimated_durations]
        else:
            # Fallback if estimates fail
            scene_durations = [audio_duration / len(scenes)] * len(scenes)

        # Convert to frame counts, ensuring total matches audio
        scene_frames = get_scene_frames(scene_durations, fps=FPS)
        total_frames = int(audio_duration * FPS)
        
        # Adjust last scene to fix rounding errors
        current_frames = sum(scene_frames)
        diff = total_frames - current_frames
        if scene_frames:
            scene_frames[-1] += diff

        total_seconds = total_frames / FPS
        JobDB.add_log(job_id, f"Final video duration (synced to audio): {total_seconds:.2f}s ({total_frames} frames)")
        
        # Log per-scene durations
        for i, frames in enumerate(scene_frames):
             JobDB.add_log(job_id, f"Scene {i+1}: {frames} frames")

        # ------------------------------------------------
        # Prepare scenes payload for Remotion
        # ------------------------------------------------
        scenes_payload = []
        for i, scene in enumerate(scenes):
            data = scene.dict()
            data["duration_frames"] = scene_frames[i]
            scenes_payload.append(data)

        # ------------------------------------------------
        # Render with Remotion
        # ------------------------------------------------
        from services.remotion_renderer import RemotionRenderer

        template_id = job.image_style.split(":")[-1].strip()
        output_video = os.path.join(job_dir, "final_typographic.mp4")

        JobDB.add_log(job_id, f"Starting Remotion render (template: {template_id})...")
        
        renderer = RemotionRenderer(frontend_dir="../frontend")

        try:
            result = await renderer.render_video(
                template_id=template_id,
                output_path=output_video,
                audio_path=audio_path,
                text=full_script,
                duration_in_frames=total_frames,
                scenes=scenes_payload,
            )
        except Exception as e:
            error_msg = f"Remotion render crashed: {type(e).__name__}: {str(e)}"
            JobDB.add_log(job_id, f"ERROR: {error_msg}")
            JobDB.add_log(job_id, f"TRACEBACK: {traceback.format_exc()[-500:]}")
            JobDB.update(job_id, status=TaskStatus.FAILED, error_msg=error_msg)
            return

        # Handle the new error return format
        if result is None:
            error_msg = "Remotion returned None (unknown failure)"
            JobDB.add_log(job_id, f"ERROR: {error_msg}")
            JobDB.update(job_id, status=TaskStatus.FAILED, error_msg=error_msg)
            return
            
        if isinstance(result, dict) and "error" in result:
            error_msg = result["error"]
            # Truncate for storage but log full
            JobDB.add_log(job_id, f"ERROR: Remotion failed: {error_msg[:500]}")
            JobDB.update(
                job_id,
                status=TaskStatus.FAILED,
                error_msg=error_msg[:200],  # Truncate for DB
            )
            return

        # Success!
        JobDB.update(
            job_id,
            status=TaskStatus.FINISHED,
            video_path=result,
        )
        JobDB.add_log(job_id, "✓ Typographic video ready")
        return

    # ==================================================
    # STANDARD IMAGE + VIDEO FLOW
    # ==================================================
    JobDB.update(job_id, status=TaskStatus.VISUALIZING)

    semaphore = asyncio.Semaphore(1)

    async def process_scene(i: int, scene: Scene):
        async def gen_img():
            img_path = os.path.join(job_dir, f"scene_{i}.png")
            prompt = f"{scene.visual_prompt}, {job.image_style}, high quality"
            async with semaphore:
                await asyncio.to_thread(generate_image, prompt, img_path)
            scene.image_path = img_path

        async def gen_audio_scene():
            audio_path = os.path.join(job_dir, f"scene_{i}.mp3")
            audio_path, _ = await generate_audio(scene.narration, audio_path)
            scene.audio_path = audio_path

        await asyncio.gather(gen_img(), gen_audio_scene())
        return scene

    updated_scenes = await asyncio.gather(
        *(process_scene(i, s) for i, s in enumerate(scenes))
    )

    JobDB.update(job_id, script=updated_scenes)

    # ------------------------------------------------
    # Assemble final video
    # ------------------------------------------------
    JobDB.update(job_id, status=TaskStatus.EDITING)
    output_video = os.path.join(job_dir, "final.mp4")

    success = await asyncio.to_thread(
        assemble_reel,
        updated_scenes,
        output_video,
        job_id,
    )

    if success:
        JobDB.update(
            job_id,
            status=TaskStatus.FINISHED,
            video_path=output_video,
        )
        JobDB.add_log(job_id, "Reel created successfully")
    else:
        JobDB.update(
            job_id,
            status=TaskStatus.FAILED,
            error_msg="Video assembly failed",
        )


# ======================================================
# API ROUTES
# ======================================================
@app.post("/jobs", response_model=Job)
async def create_job(job_req: JobCreate, background_tasks: BackgroundTasks):
    job = JobDB.create(job_req)
    background_tasks.add_task(process_job, job.id)
    return job


@app.get("/jobs", response_model=list[Job])
def get_jobs():
    return list(JobDB.jobs.values())


@app.get("/api/health")
def health_check():
    return {"status": "running", "system": "ReelAgent"}


# ======================================================
# SERVE FRONTEND (Production)
# ======================================================
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))
assets_path = os.path.join(frontend_dist, "assets")

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Only serve index.html if not an API/Generated call
    if full_path.startswith("api") or full_path.startswith("generated"):
        return {"error": "Not found"}
    
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "running", "system": "ReelAgent (Frontend not found)"}


@app.on_event("startup")
async def startup_event():
    os.makedirs(settings.GENERATED_DIR, exist_ok=True)
    print("ReelAgent Startup: Ready")
    asyncio.create_task(cleanup_old_jobs())


# ======================================================
# ENTRYPOINT
# ======================================================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
