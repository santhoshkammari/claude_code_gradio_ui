# Quick Start Guide

## Starting the Application

```bash
# Make sure you're in the claudable directory
cd claudable

# Run the FastAPI server
python api.py
```

The server will start on http://localhost:8000

## Testing the Setup

1. Open your browser to http://localhost:8000
2. Type a message in the text area
3. Select mode (Claude Code or Qwen)
4. Select model (Claude Sonnet 4.5 or Claude Haiku 4.5)
5. Click the submit button (arrow icon)
6. Watch the streaming response appear below!

## What Happens

When you submit a message:
1. `ui.js` captures your input
2. `api.js` sends POST request to `/claude` endpoint
3. `api.py` streams back a dummy response word by word
4. `ui.js` displays each word as it arrives
5. Response appears in the response container with smooth animation

## Current Behavior (Dummy Response)

The endpoint currently returns a test message like:
```
Hello! I received your message: "your message here"

You selected:
- Mode: claudecode
- Model: Claude Sonnet 4.5

This is a dummy streaming response...
```

## File Flow

```
User Input → ui.js → api.js → /claude endpoint → api.py → stream response → api.js → ui.js → Display
```

## Troubleshooting

### Port Already in Use
If port 8000 is busy:
```python
# Edit api.py, change the port in the last line:
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

### Static Files Not Loading
Make sure you're accessing via the FastAPI server (http://localhost:8000), not opening index.html directly in the browser.

### JavaScript Errors
Check browser console (F12) for errors. ES6 modules require a server to work.

## Next: Adding Real LLM

See README.md for instructions on integrating actual Claude or Qwen APIs.
