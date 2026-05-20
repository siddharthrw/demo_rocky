"""
Flask app for Rocky multi-page website
"""
from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv
from ai_session import AISession
import threading
import time

load_dotenv()

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITE_PATH = os.path.join(BASE_DIR, "website.html")
SPRITES_DIR = os.path.join(BASE_DIR, "sprites")

app = Flask(__name__, static_folder=SPRITES_DIR, static_url_path='/sprites')
CORS(app)

# Store active sessions per user
sessions = {}


class WebAISession:
    """Wrapper around AISession for web use"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.response_text = ""
        self.is_done = False
        
    def on_text(self, text):
        self.response_text += text
        
    def on_done(self):
        self.is_done = True
        
    def on_error(self, error):
        self.response_text = f"Error: {error}"
        self.is_done = True
        
    def send_message(self, message):
        """Send message and wait for response"""
        self.response_text = ""
        self.is_done = False
        
        # Create AI session
        ai = AISession(self.on_text, self.on_done, self.on_error)
        ai.send_message(message)
        
        # Wait for response (with timeout)
        timeout = 30
        start = time.time()
        while not self.is_done and (time.time() - start) < timeout:
            time.sleep(0.1)
            
        return self.response_text


@app.route("/")
def index():
    """Serve the main website"""
    return send_file(WEBSITE_PATH)


@app.route("/api/chat", methods=["POST"])
def chat():
    """API endpoint for Rocky chat"""
    try:
        data = request.json
        user_message = data.get("message", "").strip()
        user_id = data.get("user_id", "default")
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
        
        # Get or create session for this user
        if user_id not in sessions:
            sessions[user_id] = WebAISession(user_id)
        
        web_session = sessions[user_id]
        response = web_session.send_message(user_message)
        
        return jsonify({
            "text": response,
            "user_id": user_id,
            "model": "gemini-2.5-flash-lite",
            "tokens_estimate": len(response.split()) * 1.3
        })
        
    except Exception as e:
        print(f"Error in chat API: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Health check"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🚀 ROCKY MULTI-PAGE WEBSITE")
    print("="*50)
    print("\n📍 Running on http://localhost:5000")
    print("🤖 Rocky is walking and ready to chat!")
    print("📄 Pages: Home, About, Contact")
    print("🎨 Sprites: Loaded from sprites/ folder")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)
