from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
from models import Scene, JobDB
import os

def create_video_clip(scene: Scene, output_dir: str, index: int, job_id: str = None) -> str:
    """
    Creates a single video clip for a scene: Image + Audio + Ken Burns (Zoom) effect.
    """
    try:
        if job_id: JobDB.add_log(job_id, f"   - Assembly Scene {index}: Loading audio {scene.audio_path}...")
        audio = AudioFileClip(scene.audio_path)
        duration = audio.duration + 0.5 # Add padding
        
        if job_id: JobDB.add_log(job_id, f"   - Assembly Scene {index}: Loading image {scene.image_path}...")
        # Load Image
        img_clip = ImageClip(scene.image_path).set_duration(duration)
        
        # Simple Zoom Effect (Resize) - DISABLED due to Memory Usage (int64 allocation errors)
        # img_clip = img_clip.resize(lambda t: 1 + 0.05 * t) 
        
        # Set Audio
        video_clip = img_clip.set_audio(audio)
        
        return video_clip
    except Exception as e:
        msg = f"Error creating clip {index}: {e}"
        print(msg)
        if job_id: JobDB.add_log(job_id, f"ERROR: {msg}")
        return None

def assemble_reel(scenes: list[Scene], output_path: str, job_id: str = None):
    """
    Concatenates all scene clips into a final video.
    """
    clips = []
    try:
        if job_id: JobDB.add_log(job_id, f"Starting assembly of {len(scenes)} scenes...")
        
        for i, scene in enumerate(scenes):
            if scene.image_path and scene.audio_path:
                clip = create_video_clip(scene, os.path.dirname(output_path), i, job_id)
                if clip:
                    clips.append(clip)
            else:
                if job_id: JobDB.add_log(job_id, f"Skipping scene {i} due to missing assets.")
        
        if not clips:
            if job_id: JobDB.add_log(job_id, "ERROR: No valid clips created.")
            return False

        if job_id: JobDB.add_log(job_id, "Concatenating clips...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        if job_id: JobDB.add_log(job_id, f"Writing video file to {output_path}...")
        # Optimize write for low memory usage: threads=1, reduced FPS if needed (kept 24 for now)
        # Added temp_audiofile to fix Windows "Broken pipe" / permission errors with FFMPEG
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            threads=1,            # Lower memory usage
            preset="ultrafast",   # Faster encoding
            temp_audiofile="temp-audio.m4a", 
            remove_temp=True
        )
        
        return True
    except Exception as e:
        msg = f"Assembly Failed: {e}"
        print(msg)
        if job_id: JobDB.add_log(job_id, f"ERROR: {msg}")
        return False
