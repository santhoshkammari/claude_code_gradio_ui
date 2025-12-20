# Claudable - Modular Web Interface

A clean, modular web interface for Claude and Qwen AI agents with streaming responses.

## Project Structure

```
claudable/
├── index.html              # Main HTML page (clean, minimal)
├── api.py                  # FastAPI backend with /claude endpoint
├── server.py              # Simple HTTP server (legacy)
├── static/
│   ├── css/
│   │   └── styles.css     # All CSS styles
│   └── js/
│       ├── main.js        # Entry point
│       ├── api.js         # API communication layer
│       ├── state.js       # State management
│       └── ui.js          # UI controller and event handlers
└── src/                   # Python source modules
```

## Features

- **Modular Architecture**: Separate files for HTML, CSS, and JavaScript modules
- **Streaming Responses**: Token-by-token streaming via Server-Sent Events (SSE)
- **Clean Separation**: Business logic separated from presentation
- **Easy to Extend**: Add new features without bloating single files

## Running the Application

### Option 1: Using FastAPI (Recommended)

FastAPI serves both the API endpoints and static files:

```bash
cd claudable
python api.py
```

Then open http://localhost:8000 in your browser.

### Option 2: Using Simple HTTP Server

For development/testing without the backend:

```bash
cd claudable
python server.py
```

Then open http://localhost:7860 in your browser.

## API Endpoints

### POST /claude

Streams AI responses token by token.

**Request Body:**
```json
{
  "message": "Your prompt here",
  "option1": "claudecode",  // or "qwen"
  "option2": "Claude Sonnet 4.5"  // model name
}
```

**Response:**
- Content-Type: `text/event-stream`
- Format: Server-Sent Events (SSE)
- Each chunk: `data: <word>\n\n`
- End marker: `data: [DONE]\n\n`

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "Claude API is running"
}
```

## JavaScript Modules

### api.js
Handles all HTTP communication with the backend.
- `ClaudeAPI` class for making streaming requests
- Parses SSE responses
- Error handling

### state.js
Manages application state.
- `AppState` class with getter/setter
- Observable pattern for state changes
- Tracks: mode, model, files, streaming status

### ui.js
Controls all UI interactions.
- `UIController` class
- Event listeners for buttons, dropdowns, forms
- DOM manipulation
- Connects state and API modules

### main.js
Application entry point.
- Initializes UIController when DOM is ready
- Keeps initialization logic separate

## Styling

All CSS is in `static/css/styles.css`:
- Modern, clean design
- Smooth animations
- Responsive layout
- Custom scrollbars for response area

## Current Status

- ✅ Modular JavaScript structure
- ✅ Streaming endpoint with dummy data
- ✅ Separate CSS file
- ✅ Clean HTML structure
- ✅ Response display with streaming
- 🔄 Real LLM integration (coming soon)

## Adding Real LLM Integration

To replace the dummy streaming response with actual Claude/Qwen:

1. Edit `api.py` at the `/claude` endpoint
2. Replace the `generate_stream()` function
3. Integrate with Claude API or Qwen agent
4. Keep the same SSE streaming format

Example:
```python
async def generate_stream():
    # Your LLM integration here
    async for token in llm_stream(request.message):
        yield f"data: {token}\n\n"
    yield "data: [DONE]\n\n"
```

## Benefits of This Structure

1. **Maintainability**: Each file has a single responsibility
2. **Scalability**: Easy to add new features (e.g., chat history, file uploads)
3. **Debugging**: Isolated modules make bugs easier to track
4. **Performance**: Browser caches static files separately
5. **Team Work**: Multiple developers can work on different files

## Next Steps

- Integrate real Claude API
- Integrate Qwen agent
- Add file upload handling
- Add chat history
- Add error handling UI
- Add loading states
- Add response markdown rendering
