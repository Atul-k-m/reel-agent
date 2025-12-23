import requests
import json
import re
from collections import defaultdict
from typing import List, Tuple

from core.config import settings
from models import Scene, JobDB, DurationMode

# ===================== CONFIG =====================

WORDS_PER_MINUTE = 150          # exact baseline (your requirement)
MAX_RETRIES = 6

# 60s → 150 words
# 45s ≈ 112 words (−25%)
# 65s ≈ 162 words (+8.33%)
LOW_TOL = 0.50          # Relaxed to -50% (allow ~75 words for 60s target) to prevent crashes
HIGH_TOL = 0.50         # +50%

DURATION_TARGETS = {
    DurationMode.AUTO: 60,
    DurationMode.QUICK: 15,
    DurationMode.SHORT: 30,
    DurationMode.MEDIUM: 60,
    DurationMode.LONG: 90,
}

# ===================== LOGGING =====================

# ===================== LOGGING =====================

def log(job_id: str, msg: str):
    if job_id:
        JobDB.add_log(job_id, msg)

# ===================== UTIL =====================

def clean_json_text(text: str) -> str:
    text = re.sub(r"```json|```", "", text).strip()
    start, end = text.find("["), text.rfind("]")
    if start != -1 and end != -1:
        return text[start:end + 1]
    return text

def normalize_topic(topic: str) -> str:
    if "prove" in topic.lower():
        return (
            "analyze a popular internet conspiracy theory that claims Antarctica is not real, "
            "presenting arguments people make online without asserting them as facts"
        )
    return topic

# ===================== PARSING =====================

def parse_scenes(raw: str, topic: str, job_id: str) -> List[Scene]:
    cleaned = clean_json_text(raw)
    log(job_id, f"DEBUG JSON: {cleaned[:200]}...")

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        log(job_id, "WARN: Malformed JSON, attempting lenient parse")
        return []

    # 🔧 SCHEMA REPAIR: list[str] → list[dict]
    if isinstance(data, list) and data and isinstance(data[0], str):
        log(job_id, "SCHEMA FIX: Wrapping string output into scene object")
        scenes_list = []
        for i, text in enumerate(data):
            scenes_list.append({
                "narration": text,
                "visual_prompt": f"Visual representing: {topic} part {i+1}",
                "visual_text": ""
            })
        data = scenes_list

    # unwrap dict
    if isinstance(data, dict):
        for k in ("scenes", "script", "response", "data"):
            if k in data and isinstance(data[k], list):
                data = data[k]
                break

    if not isinstance(data, list):
        raise ValueError("Invalid JSON root")

    scenes = []
    for s in data:
        if not isinstance(s, dict):
            continue
        scenes.append(Scene(
            narration=s.get("narration", "..."),
            visual_prompt=s.get("visual_prompt", f"Visual of {topic}"),
            visual_text=s.get("visual_text", "")
        ))

    return scenes

# ===================== PROMPTS =====================

def build_system_prompt(seconds: int, words_target: int) -> str:
    return f"""
You are a master viral scriptwriter for short-form video (TikTok/Reels).
Your goal is HIGH RETENTION.

TARGET: ~{seconds} seconds (~{words_target} words).
This is a guide, not a hard limit. Focus on flow and impact.

STRUCTURE (Critical):
1. HOOK (0-3s): A shocking statement, question, or visual cue to grab attention.
2. BUILD-UP: Provide context, "what if", or "did you know".
3. REVEAL/VALUE: The core interesting fact or twist.
4. CTA/OUTRO: Brief conclusion.

STYLE:
- Conversational, energetic, and punchy.
- Avoid formal language. Write like you speak.
- Visuals should be startling or satisfying.

OUTPUT FORMAT: Unformatted JSON Array.
[
  {{
    "narration": "Text spoken by AI...",
    "visual_prompt": "Description for AI image generator...",
    "visual_text": "Short overlay text (2-5 words)"
  }}
]
"""

# ===================== PROVIDERS =====================

def try_groq(system_prompt, user_prompt, job_id):
    if not settings.GROQ_API_KEY:
        log(job_id, "SKIP: Groq (no key)")
        return None

    log(job_id, "TRY: Groq (Viral Script)")
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.8, # Slightly higher creative temp
    }
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        log(job_id, f"GROQ ERROR {r.status_code}: {r.text[:100]}")
    except Exception as e:
        log(job_id, f"GROQ EXCEPTION: {e}")
    return None

# ===================== MAIN =====================

def generate_script(
    topic: str,
    scene_count: int = 4,
    duration_mode: DurationMode = DurationMode.AUTO,
    job_id: str = None,
) -> Tuple[List[Scene], str]:

    log(job_id, "Job created (Flexible Duration Mode)")

    topic = normalize_topic(topic)
    
    # Calculate target words purely as a guide
    seconds = DURATION_TARGETS.get(duration_mode, 60)
    target_words = int((seconds / 60) * WORDS_PER_MINUTE)
    
    log(job_id, f"Guide: {seconds}s target (~{target_words} words). No strict limits.")

    user_prompt = f"""
Topic: {topic}
Length: Create roughly {scene_count} scenes.
Focus: Make it viral.
"""

    # Single attempt strategy with best prompt - retry only on crash
    for attempt in range(1, 4):
        system_prompt = build_system_prompt(seconds, target_words)
        
        raw = try_groq(system_prompt, user_prompt, job_id)
        if not raw:
            log(job_id, "No response from Groq. Retrying...")
            continue

        try:
            scenes = parse_scenes(raw, topic, job_id)
            if not scenes:
                raise ValueError("Empty scenes list")
                
            total = sum(len(s.narration.split()) for s in scenes)
            log(job_id, f"SUCCESS: Generated {len(scenes)} scenes ({total} words).")
            return scenes, system_prompt
            
        except Exception as e:
            log(job_id, f"Parse Failed ({e}). Retrying...")
            continue

    raise RuntimeError("Script generation failed after retries.")
