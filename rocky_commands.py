import re
import subprocess
import webbrowser
import os
import platform

def extract_and_execute_commands(response_text: str) -> str:
    """
    Parse Rocky's response for special commands and execute them.
    Returns the cleaned response text with commands removed.
    
    Supported command formats:
    - [OPEN: https://google.com] or [OPEN_URL: https://google.com]
    - [READ: path/to/file.py] or [READ_FILE: path/to/file.py]
    """
    
    # Find all command patterns
    url_pattern = r'\[(?:OPEN|OPEN_URL):\s*([^\]]+)\]'
    file_pattern = r'\[(?:READ|READ_FILE):\s*([^\]]+)\]'
    
    # Execute URL opens
    for match in re.finditer(url_pattern, response_text):
        url = match.group(1).strip()
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening URL {url}: {e}")
    
    # Execute file reads
    for match in re.finditer(file_pattern, response_text):
        filepath = match.group(1).strip()
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()
                    print(f"--- Contents of {filepath} ---\n{content}\n---")
            else:
                print(f"File not found: {filepath}")
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
    
    # Remove command syntax from display text
    clean_text = re.sub(url_pattern, '', response_text)
    clean_text = re.sub(file_pattern, '', clean_text)
    
    return clean_text
