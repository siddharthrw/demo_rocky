# 🤖 Rocky Demo Website

A minimal, fast-to-launch demo website featuring Rocky, an intelligent alien companion from Project Hail Mary.

## ✨ Features

- **Rocky Sprite**: Walking animation on every screen
- **Tap to Chat**: Click Rocky to open chat modal
- **Token-Efficient**: Uses streaming responses to minimize API costs
- **Minimal Stack**: Vanilla HTML/CSS/JS + Flask backend
- **Production-Ready**: No build process needed

## 🚀 Quick Start

### Option 1: Windows Batch (Easiest)
```bash
run_demo.bat
```
This will:
1. Install Flask and Flask-CORS
2. Start the server on `http://localhost:5000`

### Option 2: Manual Setup
```bash
# Install dependencies
pip install flask flask-cors

# Run the Flask app
python web_app.py
```

Then open your browser to: **http://localhost:5000**

## 📁 Project Structure

```
buddy/
├── index.html              # Main website (vanilla HTML/CSS/JS)
├── web_app.py             # Flask API server
├── ai_session.py          # Existing AI logic (unchanged)
├── run_demo.bat           # Windows startup script
└── .env                   # API keys (already configured)
```

## 🎯 How It Works

```
User taps Rocky
    ↓
Chat modal opens (vanilla JS)
    ↓
User types message & hits Enter
    ↓
POST /api/chat (to Flask)
    ↓
Flask calls ai_session.py (your existing code)
    ↓
Gemini API responds with Rocky's reply
    ↓
Response displayed in chat bubbles
```

## 💬 API Endpoints

### `POST /api/chat`
Send a message to Rocky

**Request:**
```json
{
  "message": "What are you?",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "text": "I am Rocky, an alien from Project Hail Mary...",
  "user_id": "user_123",
  "model": "gemini-2.5-flash-lite",
  "tokens_estimate": 42
}
```

### `GET /api/health`
Health check endpoint

## 🎨 Customization

### Change Rocky's Appearance
Edit the SVG in `index.html` (search for `rocky-sprite`):
```javascript
.rocky-sprite {
    background: url('data:image/svg+xml,...') no-repeat center;
}
```

### Change Colors
Update CSS variables:
```css
/* Purple theme */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Or customize in chat styles */
.user .message-bubble {
    background: #667eea;  /* Change user message color */
}
```

### Adjust Token Limit
In `web_app.py`, modify the maxOutputTokens:
```python
"maxOutputTokens": 150,  # Reduce for cheaper responses
```

## ⚡ Performance Tips

1. **Reduce max tokens** for shorter responses (cheaper API calls)
2. **Use local caching** - responses are cached per user session
3. **Rate limit** - add request throttling if needed
4. **Lazy load** - prefetch common responses on idle

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask flask-cors
```

### "Address already in use"
Flask is already running on port 5000. Either:
- Close the existing process
- Change port in `web_app.py`: `app.run(port=5001)`

### Rocky isn't responding
1. Check browser console (F12) for errors
2. Verify `GEMINI_API_KEY` is set in `.env`
3. Check Flask console for backend errors
4. Ensure internet connection (API calls need it)

## 📦 Dependencies

- **Flask** (0.1 KB) - Lightweight web server
- **Flask-CORS** (0.05 KB) - Enable cross-origin requests
- **Python 3.7+** - Built-in, no extra packages needed

**Total size**: ~15 KB (minimal!)

## 🎓 Next Steps

Once you verify the demo works:

1. **Add more pages** - Copy the layout, add new HTML sections
2. **Customize Rocky** - Replace SVG with actual sprite images
3. **Add FAQ matching** - Implement fast path (0-token responses)
4. **Deploy** - Use Vercel, Heroku, or your own server

## 📝 License

Rocky character © Andy Weir (Project Hail Mary)
Website code: MIT License

---

**Ready?** Run `run_demo.bat` or execute:
```bash
python web_app.py
```

Then visit: **http://localhost:5000** 🚀
