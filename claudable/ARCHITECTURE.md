# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          BROWSER                                │
├─────────────────────────────────────────────────────────────────┤
│  index.html                                                      │
│  ├── Loads: static/css/styles.css                              │
│  └── Loads: static/js/main.js (ES6 module)                     │
│                                                                  │
│  JavaScript Modules:                                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ main.js                                                   │  │
│  │   └── Initializes UIController                           │  │
│  │                                                           │  │
│  │ ui.js (UIController)                                      │  │
│  │   ├── Handles user interactions                          │  │
│  │   ├── Manages DOM elements                               │  │
│  │   ├── Updates display                                    │  │
│  │   └── Coordinates: State ↔ API                          │  │
│  │                                                           │  │
│  │ state.js (AppState)                                       │  │
│  │   ├── Stores: mode, model, files, isStreaming           │  │
│  │   ├── Observable pattern (listeners)                     │  │
│  │   └── Single source of truth                            │  │
│  │                                                           │  │
│  │ api.js (ClaudeAPI)                                        │  │
│  │   ├── sendMessage(message, option1, option2)            │  │
│  │   ├── Handles fetch() to /claude endpoint               │  │
│  │   ├── Parses SSE stream                                 │  │
│  │   └── Calls onChunk() callback                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SERVER (FastAPI)                          │
├─────────────────────────────────────────────────────────────────┤
│  api.py                                                          │
│                                                                  │
│  Routes:                                                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ GET /                                                   │    │
│  │   └── Returns index.html                               │    │
│  │                                                          │    │
│  │ GET /static/{path}                                      │    │
│  │   └── Serves CSS and JS files                          │    │
│  │                                                          │    │
│  │ GET /health                                             │    │
│  │   └── Returns {"status": "healthy"}                    │    │
│  │                                                          │    │
│  │ POST /claude                                            │    │
│  │   ├── Receives: {message, option1, option2}           │    │
│  │   ├── Generates streaming response                     │    │
│  │   └── Returns: Server-Sent Events (SSE)               │    │
│  │       Format: data: <word>\n\n                         │    │
│  │       End: data: [DONE]\n\n                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Future Integration Point:                                      │
│  └── Real LLM (Claude API / Qwen Agent)                        │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow

### User Submits Message

```
1. User types message and clicks submit
   │
   ├─→ ui.js: handleSubmit()
   │     │
   │     ├─→ state.js: set('isStreaming', true)
   │     │
   │     └─→ api.js: sendMessage(message, mode, model)
   │           │
   │           └─→ fetch('http://localhost:8000/claude', {
   │                   method: 'POST',
   │                   body: JSON.stringify({
   │                       message: "user message",
   │                       option1: "claudecode",
   │                       option2: "Claude Sonnet 4.5"
   │                   })
   │               })
   │
2. Server receives request
   │
   └─→ api.py: /claude endpoint
         │
         └─→ generate_stream() async generator
               │
               ├─→ Yields: "data: Hello\n\n"
               ├─→ Yields: "data: I\n\n"
               ├─→ Yields: "data: received\n\n"
               ├─→ ...
               └─→ Yields: "data: [DONE]\n\n"

3. Client receives stream
   │
   ├─→ api.js: Parses SSE chunks
   │     │
   │     └─→ For each chunk: onChunk(word)
   │           │
   │           └─→ ui.js: appendToResponse(word)
   │                 │
   │                 └─→ DOM: Update response-content element
   │
4. Stream completes
   │
   └─→ state.js: set('isStreaming', false)
```

## Module Responsibilities

### main.js
- **Single Purpose**: Bootstrap the application
- **Dependencies**: ui.js
- **Exports**: Nothing (entry point)

### ui.js
- **Purpose**: User Interface Controller
- **Dependencies**: state.js, api.js
- **Responsibilities**:
  - Bind DOM elements
  - Attach event listeners
  - Handle user interactions
  - Update display based on state
  - Coordinate between state and API

### state.js
- **Purpose**: Application State Management
- **Dependencies**: None
- **Responsibilities**:
  - Store application data
  - Notify listeners on changes
  - Provide get/set interface
  - Single source of truth

### api.js
- **Purpose**: Backend Communication
- **Dependencies**: None
- **Responsibilities**:
  - HTTP requests to /claude
  - Parse SSE streams
  - Error handling
  - Callback-based chunk delivery

## Data Models

### State Object
```javascript
{
  mode: 'claudecode' | 'qwen',
  model: string,  // 'Claude Sonnet 4.5', 'Claude Haiku 4.5'
  files: File[],
  isStreaming: boolean
}
```

### API Request
```javascript
{
  message: string,
  option1: string,  // mode
  option2: string   // model name
}
```

### API Response (SSE)
```
data: word1 \n\n
data: word2 \n\n
...
data: [DONE]\n\n
```

## Benefits of This Architecture

1. **Separation of Concerns**
   - UI logic separated from business logic
   - State management isolated
   - API communication abstracted

2. **Testability**
   - Each module can be tested independently
   - Mock dependencies easily
   - Clear interfaces

3. **Maintainability**
   - Changes to API don't affect UI
   - UI changes don't affect state
   - Single file for each concern

4. **Scalability**
   - Easy to add new features
   - Can replace modules without breaking others
   - Clear extension points

## Adding New Features

### Adding Chat History
1. Add `history: []` to state.js
2. In ui.js, push messages to history on submit
3. Create new history.js for display logic
4. Update index.html with history container

### Adding File Upload
1. Modify api.js to support FormData
2. Update /claude endpoint to accept files
3. Add file preview in ui.js
4. Process files in backend

### Adding Markdown Rendering
1. Install markdown library in static/js
2. In ui.js, parse response as markdown
3. Update CSS for markdown styles
4. Render in response-content element
