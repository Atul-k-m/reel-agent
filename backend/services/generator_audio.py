import asyncio
import os
import wave
from gtts import gTTS


async def generate_audio(
    text: str,
    output_path: str,
    voice: str = "en-US-ChristopherNeural"
) -> tuple[str, float]:
    """
    Generates TTS audio file.

    Returns:
        (audio_path, duration_in_seconds)

    Priority:
        1. Piper TTS (local, high quality)
        2. gTTS (fallback)
    """

    # ----------------------------
    # 1. Try Piper TTS
    # ----------------------------
    try:
        model_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "piper_models",
                "en_US-lessac-medium.onnx"
            )
        )

        if os.path.exists(model_path):
            print(f"Generating audio with Piper TTS ({os.path.basename(model_path)})")
            from piper import PiperVoice

            def run_piper():
                voice_model = PiperVoice.load(model_path)

                with wave.open(output_path, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)  # 16-bit PCM
                    wav_file.setframerate(voice_model.config.sample_rate)

                    for chunk in voice_model.synthesize(text):
                        wav_file.writeframes(chunk.audio_int16_bytes)

            await asyncio.to_thread(run_piper)

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                with wave.open(output_path, "rb") as wf:
                    duration_sec = wf.getnframes() / wf.getframerate()

                print(f"Piper audio saved: {output_path} ({duration_sec:.2f}s)")
                create_dummy_json(text, output_path, duration_sec)
                return output_path, duration_sec

        else:
            print("Piper model not found, skipping.")

    except Exception as e:
        print("Piper TTS failed:", e)
        if os.path.exists(output_path):
            os.remove(output_path)

    # ----------------------------
    # 2. Fallback: gTTS
    # ----------------------------
    print("Falling back to gTTS...")

    def run_gtts():
        tts = gTTS(text=text, lang="en")
        tts.save(output_path)

    await asyncio.to_thread(run_gtts)

    if not os.path.exists(output_path):
        raise RuntimeError("gTTS failed to generate audio")

    # gTTS duration estimation (rough but acceptable)
    estimated_duration = max(len(text.split()) / 2.5, 5.0)

    print(f"gTTS audio saved: {output_path} (~{estimated_duration:.2f}s)")
    create_dummy_json(text, output_path, estimated_duration)

    return output_path, estimated_duration


def create_dummy_json(text: str, output_path: str, duration_sec: float):
    import json

    word_boundaries = [{
        "text": text,
        "start": 0,
        "duration": int(duration_sec * 1000)
    }]

    with open(output_path + ".json", "w", encoding="utf-8") as f:
        json.dump(word_boundaries, f, indent=2)
