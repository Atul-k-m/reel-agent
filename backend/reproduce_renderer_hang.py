import asyncio
import os
import json
import subprocess

async def test_renderer():
    # Setup paths based on what we know exists
    base_dir = r"d:\reelagent"
    frontend_dir = os.path.join(base_dir, "frontend")
    
    # Use the folder found in list_dir
    job_dir = os.path.join(base_dir, "generated", "ice_age_20251222_195142")
    audio_path = os.path.join(job_dir, "full_audio.mp3")
    output_path = os.path.join(job_dir, "debug_render.mp4")
    
    print(f"Testing render in: {job_dir}")
    print(f"Audio exists: {os.path.exists(audio_path)}")
    
    # Mock data
    text = "Debugging the renderer hang issue."
    timestamps = [] # empty usually defaults to something or we can load if json exists
    
    json_path = audio_path + ".json"
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            timestamps = json.load(f)
            
    # Fix paths
    audio_path_clean = audio_path.replace("\\", "/")
    
    input_props = {
        "text": text,
        "audioSrc": audio_path_clean,
        "timestamps": timestamps
    }
    
    props_json = json.dumps(input_props)
    
    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    
    cmd = [
        npx_cmd, "--yes", "remotion", "render",
        "src/remotion/index.ts",
        "Swiss", # Fixed Template ID (was Typographic: Swiss)
        output_path,
        f"--props={props_json}",
        "--log=verbose"
    ]
    
    print(f"Command: {cmd}")
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=frontend_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("Process started...")
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        
        print("Process finished!")
        print(f"Return code: {process.returncode}")
        
        if process.returncode != 0:
            print("STDERR:")
            print(stderr.decode())
        else:
            print("Success!")
            print(f"Output size: {os.path.getsize(output_path)}")
            
    except asyncio.TimeoutError:
        print("TIMEOUT! Process killed.")
        process.kill()
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_renderer())
