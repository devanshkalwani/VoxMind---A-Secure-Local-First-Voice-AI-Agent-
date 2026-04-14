import os
import pathlib
import subprocess

# Define the restricted output directory
BASE_DIR = pathlib.Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"

# Ensure the output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _get_safe_path(filename: str) -> pathlib.Path:
    """Ensure the path strictly resolves inside the OUTPUT_DIR to prevent directory traversal."""
    # Strip any directory path passed in filename
    basename = os.path.basename(filename)
    return OUTPUT_DIR / basename

def create_file(filename: str, resource_type: str = "file", content: str = "") -> str:
    path = _get_safe_path(filename)
    if path.exists():
        return f"{resource_type.capitalize()} `{filename}` already exists in output folder."
    try:
        if resource_type == "folder":
            path.mkdir(parents=True, exist_ok=True)
            return f"Successfully created folder `{filename}` in the output folder."
        else:
            path.write_text(content)
            return f"Successfully created file `{filename}` in the output folder."
    except Exception as e:
        return f"Error creating {resource_type}: {e}"

def write_code(filename: str, code_content: str, append: bool = False) -> str:
    path = _get_safe_path(filename)
    try:
        mode = "a" if append and path.exists() else "w"
        with open(path, mode) as f:
            f.write("\n" + code_content if mode == "a" else code_content)
        action_word = "Appended" if mode == "a" else "Wrote"
        return f"Successfully {action_word.lower()} code to `{filename}` in the output folder."
    except Exception as e:
        return f"Error writing code: {e}"

def summarize_text(text: str) -> str:
    import ollama
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': 'You are a highly capable summarizer. Provide a concise, clear summary of the text provided.'},
            {'role': 'user', 'content': text}
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error summarizing text: {e}"

def chat(query: str) -> str:
    import ollama
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': 'You are VoxMind, a helpful AI assistant operating locally on this computer.'},
            {'role': 'user', 'content': query}
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error in chat: {e}"

def execute_system_command(command: str) -> str:
    """Execute raw system commands like 'open -a Visual Studio Code' safely."""
    try:
        # We only allow some safe commands like open
        if not command.startswith("open "):
            return "Command restricted for safety. Only 'open' commands are permitted."
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Successfully executed: {command}"
        else:
            return f"System executed with error: {result.stderr}"
    except Exception as e:
        return f"System exception during command execution: {str(e)}"
