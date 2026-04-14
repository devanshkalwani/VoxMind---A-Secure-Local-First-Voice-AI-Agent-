# VoxMind

VoxMind is a completely local, voice-controlled AI agent. It takes spoken commands and translates them into system actions, like creating files, writing code, or running basic shell commands. Everything runs offline on edge hardware to avoid the privacy issues commonly associated with cloud AI providers.

## How the system works

The agent is built on a straightforward, step-by-step pipeline:

1. **Transcription**: Audio is captured from the microphone and interpreted locally using Faster-Whisper.
2. **Intent Parsing**: A local Meta Llama 3 instance reads the transcript. Instead of generating conversational text, it is prompted to output a strict JSON array that maps to predefined system functions.
3. **Execution**: The system pauses to ask for human permission before applying any changes to the host machine.

## 🚀 Comprehensive Local Setup Guide

Follow these steps to open and run the project smoothly on any desktop device (Mac, Windows, or Linux) without encountering issues.

### 1. Opening the Project with GitHub

You have a few ways to download the project to your local machine:

**Option A: Using Git Command Line (Recommended)**
Open your terminal or command prompt and run:
```bash
git clone https://github.com/devanshkalwani/VoxMind---A-Secure-Local-First-Voice-AI-Agent-.git
cd VoxMind---A-Secure-Local-First-Voice-AI-Agent-
```

**Option B: Using GitHub Desktop**
1. Download and install [GitHub Desktop](https://desktop.github.com/).
2. Click `File` > `Clone repository...`
3. Go to the `URL` tab, paste the repository link, and choose a local path.
4. Click `Clone`.

**Option C: Download ZIP**
If you don't use Git, you can click the green **Code** button at the top of the repository and select **Download ZIP**. Extract the folder and open it in your code editor.

### 2. Install System Dependencies

You must install **Python 3.8+** and **FFmpeg** (required by the Whisper transcription model to process audio).

**For macOS:**
Install `ffmpeg` using Homebrew:
```bash
brew install ffmpeg
```

**For Windows:**
Install `ffmpeg` using [Winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/) or [Chocolatey](https://chocolatey.org/):
```powershell
# Using Winget (built-in for Windows 10/11)
winget install ffmpeg

# Or using Chocolatey
choco install ffmpeg
```
*(Ensure `ffmpeg` is added to your system's PATH variable)*

**For Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Setup the AI Models (Ollama)

VoxMind relies on [Ollama](https://ollama.com/) to run text generation securely offline.
1. Download and install Ollama for your operating system from the official website.
2. Open your terminal/command prompt and pull the Llama 3 model weights:
```bash
ollama run llama3
```
*Note: Make sure Ollama is running in the background.*

### 4. Setup the Python Environment

It is highly recommended to use a virtual environment to avoid dependency conflicts.

**On macOS and Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Run the Application

Finally, once everything is installed and your virtual environment is activated, boot up the dashboard:

```bash
streamlit run app.py
```

The VoxMind interface will open automatically in your default web browser, usually at `http://localhost:8501`.
## Security and Constraints

A major challenge when building agents is ensuring they don't accidentally wipe or alter important system data. To prevent directory traversal attacks, any file creation or code generation is strictly confined to the `output/` directory within the repository.

Additionally, VoxMind uses a human-in-the-loop architecture. Even if the LLM correctly parses a spoken command to open an application or modify a script, the backend will not execute the subprocess until you manually click the authorization button on the user interface.
