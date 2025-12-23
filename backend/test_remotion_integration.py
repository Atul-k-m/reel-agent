import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from services.generator_audio import generate_audio
from services.remotion_renderer import RemotionRenderer

async def test_full_pipeline():
    print("--- 1. Generating Audio & Timestamps ---")
    text = "Welcome to the future of typographic video generation."
    voice = "en-US-ChristopherNeural"
    audio_path = os.path.abspath("integration_test_audio.mp3")
    
    try:
        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(audio_path + ".json"): os.remove(audio_path + ".json")
        
        await generate_audio(text, audio_path, voice)
        print(f"[OK] Audio generated at {audio_path}")
    except Exception as e:
        print(f"[FAIL] Audio generation failed: {e}")
        return

    print("\n--- 2. Rendering Videos (All Templates) ---")
    # Point to frontend directory relative to here (backend/)
    renderer = RemotionRenderer(frontend_dir="../frontend")
    
    templates = ["Bauhaus", "Swiss", "Neon", "Kinetic"]
    
    for tmpl in templates:
        output_name = f"integration_test_{tmpl.lower()}.mp4"
        output_path = os.path.abspath(output_name)
        
        if os.path.exists(output_path): os.remove(output_path)
        
        print(f"\nRendering {tmpl}...")
        result = await renderer.render_video(
            template_id=tmpl,
            output_path=output_path,
            audio_path=audio_path,
            text=text
        )
        
        if result and os.path.exists(result):
            print(f"[OK] {tmpl} Rendered: {result} (Size: {os.path.getsize(result)} bytes)")
        else:
            print(f"[FAIL] {tmpl} Rendering failed.")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
