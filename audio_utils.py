import os
from faster_whisper import WhisperModel
import subprocess

# Model definition (we use base.en for perfectly balanced speed/accuracy on local Macs)
MODEL_SIZE = "base.en"

# Lazy-load to prevent blocking app startup immediately
_model = None

def get_model():
    global _model
    if _model is None:
        try:
            # For Apple Silicon, computing natively using float32 is safe, or int8 for CPU fallback
            _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        except Exception as e:
            print(f"Failed to load whisper model: {e}")
    return _model

def transcribe_audio(audio_path: str) -> str:
    """Takes a file path and returns transcribed string."""
    model = get_model()
    if not model:
        return "Error: Could not load Whisper Model."
    
    try:
        # Run standard inference
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        text = " ".join([segment.text for segment in segments]).strip()
        return text
    except Exception as e:
        return f"System Error during transcription: {str(e)}"
