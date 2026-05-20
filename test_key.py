import urllib.request
import urllib.error
import json

key = "AIzaSyAQ4DJLCNS2jIy634wYwWD0uU5e9ny4r3Q"
print(f"Testing key: {key[:10]}...")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={key}"
payload = json.dumps({
    "contents": [{"role": "user", "parts": [{"text": "say hi in one word"}]}],
    "generationConfig": {"maxOutputTokens": 10}
}).encode()

try:
    req = urllib.request.Request(url, data=payload,
          headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"SUCCESS — Gemini says: {reply}")
except urllib.error.HTTPError as e:
    print(f"FAILED — HTTP {e.code}: {e.read().decode()[:300]}")
except Exception as e:
    print(f"FAILED — {e}")