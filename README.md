# VoxMind

VoxMind is a completely local, voice-controlled AI agent. It takes spoken commands and translates them into system actions, like creating files, writing code, or running basic shell commands. Everything runs offline on edge hardware to avoid the privacy issues commonly associated with cloud AI providers.

## How the system works

The agent is built on a straightforward, step-by-step pipeline:

1. **Transcription**: Audio is captured from the microphone and interpreted locally using Faster-Whisper.
2. **Intent Parsing**: A local Meta Llama 3 instance reads the transcript. Instead of generating conversational text, it is prompted to output a strict JSON array that maps to predefined system functions.
3. **Execution**: The system pauses to ask for human permission before applying any changes to the host machine.

## Setup Instructions

To run this project, make sure you have Python installed. You will also need Ollama to run the text models natively.

First, install `ffmpeg`. The Whisper transcription model relies on this to handle audio buffers correctly.
```bash
brew install ffmpeg
```

Next, pull the Llama 3 model weights via Ollama.
```bash
ollama run llama3
```

Clone the repository and install the standard dependencies.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Finally, boot up the dashboard.
```bash
streamlit run app.py
```

## Security and Constraints

A major challenge when building agents is ensuring they don't accidentally wipe or alter important system data. To prevent directory traversal attacks, any file creation or code generation is strictly confined to the `output/` directory within the repository.

Additionally, VoxMind uses a human-in-the-loop architecture. Even if the LLM correctly parses a spoken command to open an application or modify a script, the backend will not execute the subprocess until you manually click the authorization button on the user interface.
