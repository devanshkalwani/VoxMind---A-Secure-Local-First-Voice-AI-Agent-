import json
import ollama  # type: ignore

# We explicitly define the client to ensure it uses 127.0.0.1 instead of 'localhost'
# for maximum stability on Mac networks.
client = ollama.Client(host='http://127.0.0.1:11434')

SYSTEM_PROMPT = """You are a highly intelligent command router for a local AI agent named VoxMind.
Analyze the user's transcript and extract ALL intents into a sequence of commands.

CRITICAL RULES:
1. COMPOUND COMMANDS: If the user asks for multiple things (e.g., "Create a file AND write code AND summarize it"), you MUST generate an array with multiple command objects in the correct order.
2. CODE PRIORITIZATION: If the user mentions creating a file AND implies there should be code/logic in it (e.g., "Create a calculator in calc.py"), do NOT use 'create_file'. Use 'write_code' with the full code payload.
3. QUALITY CODE: When 'write_code' is used, you must generate high-quality, professional, and working code for the 'code_content' field.
4. JSON ONLY: Output RAW JSON ONLY. No markdown, no explanations.

Supported intents:
- 'create_file': Only for empty files or folders. ('filename', 'resource_type')
- 'write_code': For any request involving logic/scripts. ('filename', 'code_content', 'append')
- 'summarize': ('text')
- 'run_command': ('command' - e.g. "open -a 'Visual Studio Code'")
- 'chat': ('query')

JSON EXAMPLES:
User: "Create a folder scripts, write a python hello world in scripts/hi.py, then open it."
{
  "commands": [
    {"intent": "create_file", "filename": "scripts", "resource_type": "folder"},
    {"intent": "write_code", "filename": "scripts/hi.py", "code_content": "print('Hello World')", "append": false},
    {"intent": "run_command", "command": "open scripts/hi.py"}
  ]
}
"""

def classify_intent(user_text: str) -> dict:
    # We use a retry loop to handle intermittent local LLM service drops
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = client.chat(model='llama3', messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_text}
            ], format='json', options={'temperature': 0.1})
            
            result_json = response['message']['content']
            return json.loads(result_json)
        except Exception as e:
            if attempt < max_retries:
                print(f"[RETRY] Ollama classification failed (Attempt {attempt + 1}/{max_retries + 1}): {e}")
                continue
            else:
                print(f"[ERROR] Max retries reached for intent classification: {e}")
                return {"commands": [{"intent": "chat", "query": user_text}]} # Final fallback
