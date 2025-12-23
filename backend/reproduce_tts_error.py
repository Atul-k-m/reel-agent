import asyncio
import os
import sys

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from services.generator_audio import generate_audio

async def test_audio_gen():
    text = "Hello world, this is a test of the emergency broadcast system."
    output_path = "debug_audio.mp3"
    
    print(f"Testing text: '{text}'")
    
    try:
        # Use the service function which has the gTTS fallback
        if os.path.exists(output_path): os.remove(output_path)
        
        await generate_audio(text, output_path)
                    
        print("Success!")
        if os.path.exists(output_path):
            print(f"File size: {os.path.getsize(output_path)}")
            
    except Exception as e:
        print(f"Caught Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_audio_gen())
