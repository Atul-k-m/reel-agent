
import asyncio
import os
import sys

sys.path.append(os.getcwd())

from services.generator_audio import generate_audio
from services.generator_image import generate_image

async def test_audio():
    print("\n--- Testing Audio Service ---")
    try:
        output = "test_audio.mp3"
        if os.path.exists(output):
            os.remove(output)
            
        await generate_audio("Testing audio generation with fallback.", output)
        
        if os.path.exists(output) and os.path.getsize(output) > 0:
            json_file = output + ".json"
            if os.path.exists(json_file):
                print(f"[OK] Audio SUCCESS: {output} (Size: {os.path.getsize(output)} bytes)")
                print(f"[OK] Timestamps SUCCESS: {json_file}")
            else:
                 print(f"[PARTIAL] Audio created but missing timestamps JSON.")
        else:
            print("[FAIL] Audio FAILED: File not created or empty")
    except Exception as e:
        print(f"[FAIL] Audio Service failed: {e}")

def test_image():
    print("\n--- Testing Image Service (All Providers) ---")
    output = "test_image.jpg"
    if os.path.exists(output):
        os.remove(output)
        
    try:
        # This uses the main function with fallbacks
        result = generate_image("A futuristic city, cinematic lighting, high detail", output)
        
        if result and os.path.exists(result):
             print(f"[OK] Image SUCCESS: {result}")
        else:
             print("[FAIL] Image FAILED: All providers failed")
    except Exception as e:
        print(f"[ERROR] Image Service crashed: {e}")

if __name__ == "__main__":
    asyncio.run(test_audio())
    test_image()
