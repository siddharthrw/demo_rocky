import urllib.request
import json
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get("GEMINI_API_KEY", "")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read())

print("Available models:\n")
for m in data["models"]:
    name = m["name"]
    methods = m.get("supportedGenerationMethods", [])
    if "generateContent" in methods:
        print(f"  {name}")
        