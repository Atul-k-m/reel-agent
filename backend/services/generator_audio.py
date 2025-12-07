import edge_tts
import asyncio
import os
from core.config import settings

async def generate_audio(text: str, output_path: str, voice: str = "en-US-ChristopherNeural") -> str:
    """
    Generates TTS audio file using edge-tts.
    """
    subs = edge_tts.Communicate(text, voice)
    await subs.save(output_path)
    return output_path
