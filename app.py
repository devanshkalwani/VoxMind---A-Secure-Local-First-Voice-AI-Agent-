import streamlit as st
import os
import time

from audio_utils import transcribe_audio
from llm_router import classify_intent
import tools

# --- UI Config & Custom CSS ---
st.set_page_config(page_title="VoxMind Enterprise", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
    /* Premium Classy Dark Theme */
    .stApp {
        background-color: #0b0f19;
        background-image: radial-gradient(circle at 50% -20%, #172554 0%, #080b12 80%);
        color: #f1f5f9;
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    /* Fix original top white bar and spacing alignment */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
        font-weight: 500;
        letter-spacing: -0.01em;
    }
    p, span, div {
        color: #cbd5e1;
    }
    .voxmind-title {
        font-size: 3.5rem !important;
        background: -webkit-linear-gradient(45deg, #4f46e5, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        letter-spacing: -0.04em !important;
    }
    
    /* Fix Sidebar Light-Theme Bug */
    [data-testid="stSidebar"] {
        background-color: #080b12 !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #f8fafc !important;
    }

    /* Input Fields & File Uploader - Making them Classy */
    [data-testid="stFileUploaderDropzone"] {
        background-color: rgba(30, 41, 59, 0.4) !important;
        border: 1px dashed rgba(56, 189, 248, 0.4) !important;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px dashed rgba(56, 189, 248, 0.8) !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.1);
    }
    .stTextInput>div>div>input {
        background-color: rgba(15, 23, 42, 0.7) !important;
        color: white !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    .stTextInput>div>div>input:focus {
        border: 1px solid rgba(56, 189, 248, 0.8) !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.2) !important;
    }
    
    /* Professional Buttons */
    .stButton>button {
        border-radius: 6px;
        background: linear-gradient(135deg, #1d4ed8 0%, #0f172a 100%);
        color: white !important;
        border: 1px solid rgba(56, 189, 248, 0.4);
        transition: all 0.2s ease;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.85rem;
        padding: 0.5rem 1rem;
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e293b 100%);
        border: 1px solid rgba(56, 189, 248, 0.8);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.3);
        transform: translateY(-1px);
    }
    
    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Memory & State Initialization
if "history" not in st.session_state:
    st.session_state.history = []
if "processed_audio_hash" not in st.session_state:
    st.session_state.processed_audio_hash = None
if "current_commands" not in st.session_state:
    st.session_state.current_commands = []
if "current_transcript" not in st.session_state:
    st.session_state.current_transcript = ""

# Sidebar has been removed based on user request.

# --- MAIN DASHBOARD ---
st.markdown("<h1 class='voxmind-title'>VoxMind</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.2rem; color: #94a3b8; margin-top: -10px; margin-bottom: 30px;'>Enterprise Voice-Controlled Restricted AI</p>", unsafe_allow_html=True)

st.markdown("""
<div class='glass-card'>
    Given the constraint of pure-local execution, inject your instructions via the audio module below or manually type them. The backend will parse the intent securely. <br>
</div>
""", unsafe_allow_html=True)

if "text_override" not in st.session_state:
    st.session_state.text_override = ""

def clear_dashboard():
    st.session_state.text_override = ""
    st.session_state.current_commands = []
    st.session_state.current_transcript = ""

col_btn, _ = st.columns([1, 4])
with col_btn:
    st.button("🔄 CLEAR / NEW TASK", on_click=clear_dashboard)

# Text Input Fallback option heavily styled via CSS
text_input = st.text_input("Manual Text Override", placeholder="Type your command here clearly...", key="text_override")

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    recorded_audio = st.audio_input("Initialize Microphone")
    
with col2:
    uploaded_audio = st.file_uploader("Upload Acoustic Signature (.wav)", type=["wav", "mp3"])

# Execution priority: Manual Text -> Recorded Audio -> Uploaded Audio
audio_to_process = recorded_audio if recorded_audio else uploaded_audio
manual_text = text_input.strip()

# --- PIPELINE EXECUTION ---
if manual_text or audio_to_process:
    
    input_hash = hash(manual_text) if manual_text else hash(audio_to_process.getvalue())
    
    if st.session_state.processed_audio_hash != input_hash:
        st.session_state.processed_audio_hash = input_hash
        st.session_state.current_commands = []
        st.session_state.current_transcript = ""
        
        st.toast("Input received. Initializing pipeline...", icon="⚡")
        
        if manual_text:
            st.session_state.current_transcript = manual_text
        else:
            audio_bytes = audio_to_process.getvalue()
            temp_path = f"temp_{input_hash}.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_bytes)
                
            with st.spinner("Module 1: STT Engine processing (Whisper base.en)..."):
                st.session_state.current_transcript = transcribe_audio(temp_path)
            
            try:
                os.remove(temp_path)
            except Exception:
                pass
            
        if st.session_state.current_transcript and not st.session_state.current_transcript.startswith("Error"):
            with st.spinner("Module 2: Intent Classification (Llama-3 LLM Core)..."):
                intent_data = classify_intent(st.session_state.current_transcript)
                commands = intent_data.get("commands", [])
                
                if not commands and "intent" in intent_data:
                    commands = [intent_data]
                    
                st.session_state.current_commands = commands

    # --- Render Results ---
    if st.session_state.current_transcript:
        st.success(f"**Identified Transcript:** \"{st.session_state.current_transcript}\"")
        
    if st.session_state.current_commands:
        st.divider()
        st.subheader(f"Execution Graph: {len(st.session_state.current_commands)} Actions")
        
        for idx, cmd in enumerate(st.session_state.current_commands):
            intent = cmd.get("intent", "chat")
            
            with st.container():
                st.markdown(f"#### ❖ Action Request: `{intent.upper()}`")
                
                task_id = f"{input_hash}_{idx}"
                if task_id in [h.get("id") for h in st.session_state.history]:
                    st.info("✔ Task completed and logged.")
                    st.markdown("---")
                    continue

                if intent == "create_file":
                    filename = cmd.get("filename", f"untitled_{idx}.txt")
                    resource_type = cmd.get("resource_type", "file")
                    st.warning(f"**Action Required:** Grant system permission to create physical {resource_type} `{filename}`.")
                    if st.button(f"AUTHORIZE {resource_type.upper()} CREATION", key=f"btn_{task_id}"):
                        with st.spinner(f"Allocating `{filename}`..."):
                            result = tools.create_file(filename, resource_type=resource_type)
                        action_str = f"Create {resource_type} '{filename}'"
                        st.session_state.history.append({"id": task_id, "transcript": st.session_state.current_transcript, "intent": intent, "action": action_str, "result": result})
                        st.rerun()
                        
                elif intent == "write_code":
                    filename = cmd.get("filename", f"script_{idx}.py")
                    code_content = cmd.get("code_content", "# No code payload")
                    append = cmd.get("append", False)
                    action_word = "Append to" if append else "Write"
                    
                    st.warning(f"**Action Required:** System generated script payload to {action_word.lower()} `{filename}`.")
                    with st.expander("Review Compiled Payload", expanded=True):
                        st.code(code_content, language="python")
                    
                    if st.button("AUTHORIZE PAYLOAD DEPLOYMENT", key=f"btn_{task_id}"):
                        with st.spinner("Deploying script locally..."):
                            result = tools.write_code(filename, code_content, append=append)
                        st.session_state.history.append({"id": task_id, "transcript": st.session_state.current_transcript, "intent": intent, "action": f"{action_word} '{filename}'", "result": result})
                        st.rerun()
                        
                elif intent == "summarize":
                    text_to_summarize = cmd.get("text", "")
                    if st.button("INITIATE SUMMARIZATION", key=f"btn_{task_id}"):
                        with st.spinner("Analyzing text computationally..."):
                            result = tools.summarize_text(text_to_summarize)
                        st.session_state.history.append({"id": task_id, "transcript": st.session_state.current_transcript, "intent": intent, "action": "Summarize text", "result": result})
                        st.rerun()

                elif intent == "run_command":
                    command = cmd.get("command", "")
                    st.warning(f"**Action Required:** Grant system permission to execute command: `{command}`")
                    if st.button("AUTHORIZE SYSTEM COMMAND", key=f"btn_{task_id}"):
                        with st.spinner("Executing command..."):
                            result = tools.execute_system_command(command)
                        st.session_state.history.append({"id": task_id, "transcript": st.session_state.current_transcript, "intent": intent, "action": f"Execute '{command}'", "result": result})
                        st.rerun()
                        
                elif intent == "chat":
                    query = cmd.get("query", st.session_state.current_transcript)
                    if st.button("QUERY LANGUAGE MODEL", key=f"btn_{task_id}"):
                        with st.spinner("Generating synthesized response..."):
                            result = tools.chat(query)
                        st.session_state.history.append({"id": task_id, "transcript": st.session_state.current_transcript, "intent": intent, "action": "General Chat", "result": result})
                        st.rerun()
                
                st.markdown("---")

# --- ARCHITECTURE FOOTER (3 Boxes) ---
st.markdown("<br><br><h3 style='text-align: center; margin-bottom: 30px; letter-spacing: 0.1em; text-transform: uppercase; font-size: 1.1rem; color: #94a3b8;'>System Architecture & Protocols</h3>", unsafe_allow_html=True)

col_arch1, col_arch2, col_arch3 = st.columns(3)

with col_arch1:
    st.markdown("""
    <div class='glass-card' style='padding: 24px; min-height: 200px;'>
        <h4 style='color: #38bdf8 !important; font-size: 0.95rem; text-transform: uppercase; margin-top: 0;'>1. Native Execution</h4>
        <p style='font-size: 0.9rem; color: #94a3b8;'>VoxMind is a hardened, fully-local execution agent. By leveraging <strong>Faster-Whisper</strong> natively compiled on edge hardware, acoustic signatures never leave your physical machine.</p>
    </div>
    """, unsafe_allow_html=True)

with col_arch2:
    st.markdown("""
    <div class='glass-card' style='padding: 24px; min-height: 200px;'>
        <h4 style='color: #38bdf8 !important; font-size: 0.95rem; text-transform: uppercase; margin-top: 0;'>2. Deterministic AI Engine</h4>
        <p style='font-size: 0.9rem; color: #94a3b8;'>The logic core utilizes <strong>Llama-3</strong> via Ollama. It bypasses open-ended chat APIs by enforcing strict JSON constraints, allowing it to interface directly with python file systems.</p>
    </div>
    """, unsafe_allow_html=True)

with col_arch3:
    st.markdown("""
    <div class='glass-card' style='padding: 24px; min-height: 200px;'>
        <h4 style='color: #38bdf8 !important; font-size: 0.95rem; text-transform: uppercase; margin-top: 0;'>3. Secure Jailed Sandbox</h4>
        <p style='font-size: 0.9rem; color: #94a3b8;'>All dynamically generated payloads and physical scripts are securely jailed inside a restricted <code>/output</code> deployment folder. This completely minimizes directory-traversal vulnerabilities.</p>
    </div>
    """, unsafe_allow_html=True)

# --- ACTUAL WEBSITE FOOTER ---
st.markdown("""
<div style="text-align: center; padding-top: 20px; padding-bottom: 40px; color: #475569; font-size: 0.85rem; border-top: 1px solid rgba(255,255,255,0.05);">
    &copy; 2026 <strong>VoxMind Software</strong>. Built for secure offline intelligence environments.<br>
    <span style="font-size: 0.75rem;">Developed for Local Device </span>
</div>
""", unsafe_allow_html=True)

# --- EXECUTION HISTORY (At the bottom) ---
st.markdown("<br><h2 style='text-align: center; color: white;'>Execution History Logs</h2><br>", unsafe_allow_html=True)

if not st.session_state.history:
    st.info("No payloads executed. Speak or type a command above to begin.")
else:
    for idx, item in enumerate(reversed(st.session_state.history)):
        st.markdown(f"#### Activity Sequence: {len(st.session_state.history) - idx}")
        with st.container(border=True):
            st.markdown(f"**Transcription:** `{item.get('transcript', '')}`")
            st.markdown(f"**Detected Intent:** `{item.get('intent', '').upper()}`")
            if 'action' in item:
                st.markdown(f"**Action Taken:** {item['action']}")
            st.success(f"**Final Result:** {item.get('result', '')}")
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Purge Execution Logs", key="purge_memory_bottom"):
        st.session_state.history = []
        st.rerun()

