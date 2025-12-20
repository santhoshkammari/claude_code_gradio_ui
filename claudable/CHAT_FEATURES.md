# Chat Interface Features

## Overview
The Claudable interface has been upgraded with a modern chat system similar to Claude/ChatGPT, featuring persistent chat sessions and a collapsible sidebar.

## Features

### 1. **Front Page (index.html)**
- Clean, minimal interface for starting new conversations
- Enter a message and press Enter or click submit
- Automatically creates a new chat session and redirects to `/chat/{uuid}`
- Keeps the original prompt buttons (Landing Page, Gaming Platform, etc.)

### 2. **Chat Page (/chat/{uuid})**
- Dedicated chat interface for each conversation
- Real-time message streaming
- Compact input box (reduced height from front page)
- Messages displayed in chat bubbles:
  - User messages: Dark background, right-aligned
  - Assistant messages: White background with border, left-aligned
- Typing indicator during streaming responses

### 3. **Sidebar**
- **Default State**: Closed (maximizes chat space)
- **Toggle Button**: Fixed position (top-left), follows sidebar when open
- **Features**:
  - "New Chat" button - returns to front page
  - List of all chat sessions sorted by most recent
  - Each item shows:
    - Chat title (auto-generated from first message)
    - Relative timestamp (Today, Yesterday, X days ago)
  - Active chat highlighted with orange accent
  - Click any chat to switch to it

### 4. **Database (SQLite3)**
- **Location**: `./chats.db` in project root
- **Tables**:
  - `chats`: id, uuid, title, created_at, updated_at
  - `messages`: id, chat_uuid, role (user/assistant), content, created_at
- **Features**:
  - Automatic title generation from first message (max 50 chars)
  - Indexed for performance (chat_uuid, updated_at)
  - Session persistence across server restarts

## API Endpoints

### Chat Session Management
- `POST /api/chat/create` - Create new chat with first message
- `GET /chat/{uuid}` - Serve chat page
- `GET /api/chats` - List all chat sessions
- `GET /api/chat/{uuid}/messages` - Get messages for a chat
- `POST /api/chat/{uuid}/message` - Send message to existing chat (streaming)
- `DELETE /api/chat/{uuid}` - Delete a chat session

### Original Endpoints (Still Active)
- `GET /` - Front page
- `POST /claude` - Original streaming endpoint
- `POST /sample` - Sample/demo endpoint
- `POST /web` - Web search endpoint

## File Structure

```
claudable/
├── api.py                      # FastAPI server with chat endpoints
├── database.py                 # SQLite database management
├── chats.db                    # SQLite database file (auto-created)
├── index.html                  # Front page
├── chat.html                   # Chat page
├── static/
│   ├── css/
│   │   ├── styles.css         # Front page styles
│   │   └── chat.css           # Chat page styles (NEW)
│   └── js/
│       ├── main.js            # Front page entry
│       ├── ui.js              # Front page UI controller (updated)
│       ├── api.js             # API communication
│       ├── state.js           # State management
│       └── chat.js            # Chat page controller (NEW)
```

## Usage

### Start the Server
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Access the Interface
- Front page: http://localhost:8000/
- Specific chat: http://localhost:8000/chat/{uuid}

### User Flow
1. User visits front page
2. Enters a message and presses Enter
3. System creates chat session with UUID
4. User is redirected to `/chat/{uuid}`
5. First message is already saved
6. Chat page loads with:
   - Message history
   - Streaming response from AI
   - Sidebar with all chats (closed by default)

## Design Principles

### Maintained from Original
- Orange accent color (#DE7356)
- Plus Jakarta Sans font for headers
- Rounded, modern aesthetic
- Smooth transitions and animations
- Clean, minimal design

### New Additions
- Chat bubble design for messages
- Collapsible sidebar with smooth animation
- Compact input for chat view
- Typing indicators
- Relative timestamps

## Technical Details

### Auto-Resize Textarea
The message input automatically grows as you type (up to 200px max height).

### Message Streaming
Uses Server-Sent Events (SSE) with the existing search_agent integration:
- Words streamed individually
- Real-time UI updates
- Automatic scrolling to latest message

### Session Persistence
All conversations are stored in SQLite with:
- Unique UUIDs for each chat
- Automatic timestamp tracking
- Efficient querying with indexes

## Future Enhancements (Optional)
- Edit chat titles
- Delete individual messages
- Search within chats
- Export chat history
- Keyboard shortcuts (e.g., Cmd+K for new chat)
- Dark mode toggle
