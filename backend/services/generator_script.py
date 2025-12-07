import requests
import json
import re
from core.config import settings
from models import Scene, JobDB

def generate_script(topic: str, scene_count: int = 4, job_id: str = None) -> tuple[list[Scene], str]:
    """
    Generates a script for the given topic using Ollama.
    Returns a list of Scene objects and the prompt used.
    """
    prompt = f"""
    You are an expert viral content creator.
    Create a {scene_count}-scene script about: "{topic}".
    
    Structure: Hook -> Twist -> Explanation -> Takeaway.
    
    Output a JSON LIST of objects.
    Example:
    [
        {{
            "narration": "Did you know...",
            "visual_prompt": "Galaxy image"
        }},
        {{
            "narration": "But actually...",
            "visual_prompt": "Microscope view"
        }}
    ]
    
    Output JSON ONLY. Format:
    [
        {{
            "narration": "Script line (max 15 words).",
            "visual_prompt": "Simple search query for a background image (e.g. 'black hole')"
        }},
        ...
    ]
    Ensure you generate exactly {scene_count} scenes.
    Do not add any markdown formatting or extra text.
    """
    
    try:
        if job_id:
             JobDB.add_log(job_id, f"Sending request to Ollama ({settings.OLLAMA_MODEL})...")

        response = requests.post(f"{settings.OLLAMA_HOST}/api/generate", json={
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json" 
        })
        
        if response.status_code == 200:
            data = response.json()
            raw_json = data.get("response", "[]")
            
            if job_id:
                JobDB.add_log(job_id, f"DEBUG: Raw LLM Output: {raw_json[:200]}...")
            
            # Clean up potential markdown formatting
            cleaned_json = re.sub(r"```json|```", "", raw_json).strip()
            
            try:
                scenes_data = json.loads(cleaned_json)
                
                # Handle case where LLM wraps list in an object (e.g. {"scenes": [...]})
                if isinstance(scenes_data, dict):
                    if "scenes" in scenes_data:
                        scenes_data = scenes_data["scenes"]
                    elif "script" in scenes_data:
                        scenes_data = scenes_data["script"]
                    elif "response" in scenes_data:
                        scenes_data = scenes_data["response"]
                    else:
                        # Fallback: assume values are the scenes (e.g. {"0": {...}, "scene1": [...]})
                        # Handle case where value is a list e.g. {"0": [{...}]}
                        vals = []
                        for v in scenes_data.values():
                            if isinstance(v, list) and len(v) > 0:
                                # Try to find a dict in the list
                                found_item = next((i for i in v if isinstance(i, dict)), None)
                                if found_item:
                                    vals.append(found_item)
                                else:
                                    vals.append(v[0]) # Fallback
                            else:
                                vals.append(v)
                        scenes_data = vals
                
                if not isinstance(scenes_data, list):
                     raise ValueError(f"Expected list of scenes, got {type(scenes_data)}")

                final_scenes = []
                for s in scenes_data:
                    if not isinstance(s, dict): continue
                    
                    # Resilience: Ensure required fields exist
                    if "narration" not in s:
                        s["narration"] = "..."
                    if "visual_prompt" not in s:
                        # Fallback visual prompt if missing
                        s["visual_prompt"] = f"Abstract background representing {topic}"
                    
                    final_scenes.append(Scene(**s))
                    
                return final_scenes, prompt
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                error_msg = f"JSON Parse Error: {e}"
                print(error_msg)
                if job_id:
                    JobDB.add_log(job_id, f"ERROR: {error_msg}")
                    JobDB.add_log(job_id, f"Bad Content: {cleaned_json}")
                return [], prompt
        else:
            error_msg = f"Ollama Error Status {response.status_code}: {response.text}"
            print(error_msg)
            if job_id:
                JobDB.add_log(job_id, error_msg)
            return [], prompt
            
    except Exception as e:
        error_msg = f"Script Generation Failed: {e}"
        print(error_msg)
        if job_id:
             JobDB.add_log(job_id, error_msg)
        return [], prompt
