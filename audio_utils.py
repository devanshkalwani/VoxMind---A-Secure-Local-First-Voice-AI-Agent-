from faster_whisper import WhisperModel  # type: ignore
import os
import subprocess
import tempfile
import pathlib

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
    """Takes a file path, ensuring it's a standard WAV, and returns transcribed string."""
    model = get_model()
    if not model:
        return "Error: Could not load Whisper Model."
    
    # Pre-conversion: Use native FFmpeg to ensure the file is a standard 16kHz WAV
    # This bypasses pydub and audioop dependencies which are unstable on Python 3.14
    temp_wav_path = None
    try:
        # Create a unique temporary path for the converted file
        fd, temp_wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        # Run FFmpeg to convert to 16kHz mono WAV (standard for Whisper)
        # -y: overwrite, -i: input, -ar: sample rate, -ac: channels
        cmd = [
            "ffmpeg", "-y", "-i", audio_path, 
            "-ar", "16000", "-ac", "1", 
            temp_wav_path
        ]
        
        # We suppress output to keep logs clean
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Run standard inference on the converted file
        segments, info = model.transcribe(temp_wav_path, beam_size=5)
        
        text = " ".join([segment.text for segment in segments]).strip()
        
        return text if text else "Error: No speech detected in audio."
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg conversion failed: {e}")
        return "Error: Could not process audio format. Ensure FFmpeg is installed."
    except Exception as e:
        print(f"[ERROR] Audio processing failed: {e}")
        return f"System Error during transcription: {str(e)}"
    finally:
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except:
                pass
