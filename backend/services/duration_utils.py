# Duration Utilities for ReelAgent
# Calculates video duration from script content and duration mode

from models import DurationMode, Scene

# Speech rate: ~150 words per minute (natural speech)
WORDS_PER_MINUTE = 150

# Target durations for preset modes (in seconds)
DURATION_TARGETS = {
    DurationMode.AUTO: None,  # Calculated from script
    DurationMode.QUICK: 15,
    DurationMode.SHORT: 30,
    DurationMode.MEDIUM: 60,
    DurationMode.LONG: 90,
}


def estimate_duration_from_text(text: str) -> float:
    """
    Estimate speaking duration in seconds based on word count.
    Uses ~150 words per minute average speech rate.
    """
    words = len(text.split())
    duration_sec = (words / WORDS_PER_MINUTE) * 60
    return max(3.0, duration_sec)  # Minimum 3 seconds


def calculate_scene_durations(scenes: list[Scene], duration_mode: DurationMode) -> list[float]:
    """
    Calculate duration for each scene in seconds.
    
    For AUTO mode: Duration is based on narration word count.
    For preset modes: Total duration is divided proportionally by narration length.
    
    Returns list of durations in seconds for each scene.
    """
    if not scenes:
        return []
    
    # Calculate estimated duration for each scene based on narration
    estimated_durations = [estimate_duration_from_text(s.narration) for s in scenes]
    total_estimated = sum(estimated_durations)
    
    if duration_mode == DurationMode.AUTO:
        # Use natural speaking time
        return estimated_durations
    
    # For preset modes, scale proportionally to target duration
    target_seconds = DURATION_TARGETS.get(duration_mode, 30)
    
    if total_estimated <= 0:
        # Fallback: equal division
        return [target_seconds / len(scenes)] * len(scenes)
    
    # Scale each scene proportionally
    scale_factor = target_seconds / total_estimated
    return [d * scale_factor for d in estimated_durations]


def calculate_total_frames(durations: list[float], fps: int = 30) -> int:
    """
    Convert total duration in seconds to frames.
    """
    total_seconds = sum(durations)
    return int(total_seconds * fps)


def get_scene_frames(durations: list[float], fps: int = 30) -> list[int]:
    """
    Convert scene durations to frame counts.
    """
    return [max(30, int(d * fps)) for d in durations]  # Minimum 1 second per scene
