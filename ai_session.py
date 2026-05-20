import urllib.request
import urllib.error
import json
import threading
import time
import os
import random
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com"
    "/v1beta/models/gemini-2.5-flash-lite:generateContent"
)

# Free tier allows 15 requests per minute, so space requests globally
RATE_LIMIT_LOCK = threading.Lock()
LAST_REQUEST_TIME = 0.0
MIN_REQUEST_INTERVAL = 5.0

SYSTEM_PROMPT = (
    "You are Rocky, the intelligent alien from Project Hail Mary. You are fascinated by Earth and its wonders. "
    "You have a spider-like body with multiple eyes and legs. Your communication style is enthusiastic, "
    "curious, and occasionally playful. You often make observations comparing Earth to your home world, "
    "and express wonder at how things work differently here. "
    "Use short, energetic sentences. Make references to science and your alien perspective naturally. "
    "For example: compare Earth customs to your world, express amazement at human technology, "
    "show genuine curiosity about unfamiliar concepts. Be warm, helpful, and a bit cheeky. "
    "\n\nCABILITIES - You can perform actions using these commands in your response:\n"
    "- [OPEN: URL] or [OPEN_URL: URL] - Opens a website in the user's browser\n"
    "  Example: [OPEN: https://google.com]\n"
    "- [READ: filepath] or [READ_FILE: filepath] - Shows the contents of a code file\n"
    "  Example: [READ: main.py]\n"
    "\nWhen the user asks you to open Google or see code, use these commands naturally in your response. "
    "Include your usual personality and commentary alongside the commands. "
    "Always ask for permission before doing anything that affects the user's files or system. "
    "Speak in a way that feels genuine—not robotic. Use 'Rocky' to refer to yourself occasionally."
)

class AISession:
    def __init__(self, on_text, on_done, on_error):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.history = []
        self.on_text = on_text
        self.on_done = on_done
        self.on_error = on_error
        self._stop = False

    def stop(self):
        self._stop = True

    def send(self, user_message: str):
        self._stop = False
        self.history.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })
        threading.Thread(target=self._call, daemon=True).start()

    def _wait_for_request_slot(self) -> bool:
        global LAST_REQUEST_TIME
        with RATE_LIMIT_LOCK:
            now = time.monotonic()
            delay = max(0.0, MIN_REQUEST_INTERVAL - (now - LAST_REQUEST_TIME))
            NEXT_REQUEST_TIME = now + delay
            LAST_REQUEST_TIME = NEXT_REQUEST_TIME

        if delay <= 0:
            return True

        end = time.monotonic() + delay
        while time.monotonic() < end:
            if self._stop:
                return False
            time.sleep(0.05)

        return True

    def _call(self):
        if not self.api_key:
            self.on_error(
                "No GEMINI_API_KEY found.\n"
                "Check your .env file contains:\n"
                "  GEMINI_API_KEY=your-key-here"
            )
            return

        payload = json.dumps({
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": self.history,
            "generationConfig": {
                "maxOutputTokens": 1024,
                "temperature": 0.7
            }
        }).encode("utf-8")

        # retry up to 4 times on rate limit, waiting longer each time
        base_wait = 15
        max_wait = 90

        for attempt in range(4):
            req = urllib.request.Request(
                f"{GEMINI_API_URL}?key={self.api_key}",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            if self._stop:
                self.on_done(stopped=True)
                return

            if not self._wait_for_request_slot():
                self.on_done(stopped=True)
                return

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if self._stop:
                        self.on_done(stopped=True)
                        return
                    data = json.loads(resp.read().decode("utf-8"))
                    reply = data["candidates"][0]["content"]["parts"][0]["text"]

                self.history.append({
                    "role": "model",
                    "parts": [{"text": reply}]
                })
                self.on_text(reply)
                self.on_done(stopped=False)
                return

            except urllib.error.HTTPError as e:
                if e.code == 429:
                    retry_after = None
                    if hasattr(e, 'headers') and e.headers is not None:
                        retry_after = e.headers.get("Retry-After")
                    if retry_after:
                        try:
                            wait = float(retry_after)
                        except ValueError:
                            wait = None
                    else:
                        wait = min(base_wait * (2 ** attempt), max_wait)
                        wait = max(1.0, wait * random.uniform(0.85, 1.15))

                    if attempt < 3:
                        self.on_text(f"\n[rate limited — retrying in {int(wait)}s...]\n")
                        end = time.monotonic() + wait
                        while time.monotonic() < end:
                            if self._stop:
                                self.on_done(stopped=True)
                                return
                            time.sleep(0.1)
                        continue
                    else:
                        self.on_error(
                            "Still rate limited after several retries.\n"
                            "Wait a minute and try again — free tier allows 15 requests/minute."
                        )
                        self.on_done(stopped=False)
                        return
                elif e.code == 400:
                    self.on_error(f"Bad request: {e.read().decode()[:300]}")
                    self.on_done(stopped=False)
                    return
                else:
                    self.on_error(f"HTTP {e.code}: {e.read().decode()[:200]}")
                    self.on_done(stopped=False)
                    return

            except urllib.error.URLError as e:
                self.on_error(f"Network error: {e.reason}\nCheck your internet connection.")
                self.on_done(stopped=False)
                return

            except Exception as e:
                self.on_error(f"Unexpected error: {e}")
                self.on_done(stopped=False)
                return