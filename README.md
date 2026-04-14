<div align="center">
  <img src="https://img.icons8.com/color/96/000000/microphone.png" alt="logo" width="80"/>
  <h1>VoxMind 🎙️</h1>
  <p><strong>A Highly Secure, Fully-Local Voice AI Agent</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
  [![Local Framework](https://img.shields.io/badge/Local-Ollama%20%7C%20Llama--3-orange)](https://ollama.ai)
  [![Transcription](https://img.shields.io/badge/STT-Faster--Whisper-green)](https://github.com/SYSTRAN/faster-whisper)
</div>

---

In the era of cloud-first computing, streaming acoustic data directly limits privacy. **VoxMind** is a truly offline, deeply sandboxed Python AI agent designed to execute advanced desktop operations dynamically using Voice.

## 🚀 Key Features

* **Strictly Local Audio Muxing**: Transcribes your voice locally using `faster-whisper (base.en)` utilizing native INT8 hardware acceleration.
* **Deterministic Intent System**: Intercepts speech using Meta's `Llama-3` (via Ollama) mapped through a JSON structural constraint.
* **Jailed Execution Sandbox**: All dynamically generated files, python payloads, and code appends are strictly routed into the `output/` folder, destroying any OS directory traversal risk.
* **Native Desktop Triggers**: Can spawn subprocess operations natively (e.g., `"open -a 'Visual Studio Code'"`).
* **Zero-Trust Human Authorization**: While the agent dynamically scopes the payload, it will **never** execute physical writes without human authorization via the Streamlit backend.

---

## 🛠️ Quick Start

Ensure you have a modern macOS system natively equipped with Homebrew.

### 1. Audio System Setup
You must supply your system with raw C-binding drivers so `faster-whisper` can consume binary audio safely.
```bash
brew install ffmpeg
```

### 2. Prepare the AI Nodes
Install [Ollama](https://ollama.com/) locally. Pull the inference engine into your local weight cache:
```bash
ollama run llama3
```

### 3. Spin Up VoxMind
```bash
# Clone the repository
git clone https://github.com/your-username/VoxMind.git
cd VoxMind

# Spin up a localized virtual environment & inject dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Boot the Dashboard
streamlit run app.py
```

---

## 🧠 System Execution Lifecycle
Instead of abstract operations, VoxMind visibly renders the structural breakdown of its actions logically inside the UI sequence tree:
1. **TRANSCRIPTION**: Raw acoustic mapping
2. **INTENT DETECTION**: LLM Structural Routing classification
3. **ACTION PROPOSAL**: `create_file()`, `write_code()`, or `run_command()`
4. **SECURE RESULT**: Human Authorization validation & Python process outcome

*(Developed for Apple Silicon M-Series. Highly compatible across Intel Linux/Windows with minor audio driver abstraction.)*
