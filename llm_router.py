import json
import ollama  # type: ignore

SYSTEM_PROMPT = """You are a highly intelligent command router that controls a local AI agent.
Analyze the user's spoken transcript and extract all the intents they wish to execute. The user might ask for multiple things in one sentence (Compound Commands).

Supported intents:
1. 'create_file': The user explicitly asks to create an entirely new file or folder. Needs 'filename' and 'resource_type' ("file" or "folder").
2. 'write_code': The user asks to write code, generate a script, or program something into a file. Needs 'filename', 'code_content', and 'append' (boolean).
3. 'summarize': The user asks you to summarize text. Needs 'text'.
4. 'run_command': The user asks to open an application or run a safe system command (e.g. open VS Code). Needs 'command' (e.g., "open -a 'Visual Studio Code'").
5. 'chat': The user asks a general question. Needs 'query'.

You must return a strictly formatted JSON object containing an array of 'commands'.
DO NOT wrap the response in markdown blocks. Output RAW JSON ONLY.

JSON SCHEMA EXAMPLES:

User: "Create a python file called hello.py."
{"commands": [{"intent": "create_file", "filename": "hello.py", "resource_type": "file"}]}

User: "Create a folder called scripts."
{"commands": [{"intent": "create_file", "filename": "scripts", "resource_type": "folder"}]}

User: "Write a python script that reverses a string and save it to test.py, and then summarize the importance of python."
{"commands": [
    {"intent": "write_code", "filename": "test.py", "code_content": "def reverse_string(s):\n    return s[::-1]\n\nprint(reverse_string('hello'))", "append": false},
    {"intent": "summarize", "text": "the importance of python"}
]}

User: "Open VS Code."
{"commands": [{"intent": "run_command", "command": "open -a 'Visual Studio Code'"}]}

User: "Hello there, how are you?"
{"commands": [{"intent": "chat", "query": "Hello there, how are you?"}]}
"""

def classify_intent(user_text: str) -> dict:
    try:
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_text}
        ], format='json', options={'temperature': 0.1})
        
        result_json = response['message']['content']
        return json.loads(result_json)
    except Exception as e:
        print(f"Error classifying intent: {e}")
        return {"commands": [{"intent": "chat", "query": user_text}]} # Strict fallback
