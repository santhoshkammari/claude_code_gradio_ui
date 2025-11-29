# Claude Code Gradio UI - Project Task List

## Project Goal
Convert the ClaudeCodeUI (React/Vite-based web application) into a pure Gradio Python application.

## Source Repository
- Original: https://github.com/siteboon/claudecodeui.git
- Reference: Gradio library at https://github.com/gradio-app/gradio.git

## Target Application
- Name: `claude_code_gradio_ui`
- Command: `python claude_code_gradio_ui.py` should launch the application
- Framework: Pure Gradio (Python-based)
- No React, Node.js, or JavaScript dependencies

## Original Application Overview

### Architecture
The original ClaudeCodeUI is a full-stack application with:
- **Frontend**: React 18 + Vite, Tailwind CSS, CodeMirror editor
- **Backend**: Express.js server with WebSocket support
- **CLI Integration**: Integrates with Claude Code CLI and Cursor CLI
- **Database**: SQLite for credentials and session management

### Key Features to Replicate
1. **Project Management**
   - Browse Claude Code projects from `~/.claude/projects/`
   - Project selection and navigation
   - Session management (create, view, delete sessions)

2. **Chat Interface**
   - Real-time communication with Claude Code CLI
   - WebSocket-based streaming responses
   - Message history with timestamps
   - Support for code blocks and file references

3. **File Explorer & Editor**
   - Interactive file tree browser
   - Syntax highlighting for code files
   - File operations (create, read, update, delete)

4. **Session Management**
   - Resume previous conversations
   - Session persistence (JSONL format)
   - Session organization by project

5. **Settings & Configuration**
   - API credentials management
   - Tool settings configuration
   - Theme support (dark/light mode)

6. **CLI Integration**
   - Process spawning for Claude Code CLI
   - Support for both Claude Code and Cursor CLI
   - Terminal emulation with xterm.js

### Technical Stack (Original)
```json
{
  "frontend": {
    "framework": "React 18",
    "build": "Vite",
    "styling": "Tailwind CSS",
    "editor": "CodeMirror",
    "markdown": "react-markdown",
    "router": "react-router-dom"
  },
  "backend": {
    "runtime": "Node.js",
    "server": "Express",
    "websocket": "ws",
    "database": "better-sqlite3",
    "cli": "@anthropic-ai/claude-agent-sdk"
  }
}
```

## Gradio Conversion Strategy

### Phase 1: Research & Planning
- [x] Clone and explore original repository
- [x] Understand architecture and data flow
- [ ] Map React components to Gradio components
- [ ] Identify Gradio equivalents for key features
- [ ] Plan Python module structure

### Phase 2: Core Infrastructure
- [ ] Set up Python project structure
- [ ] Create database models (SQLite)
- [ ] Implement Claude Code CLI integration (Python subprocess)
- [ ] Build project discovery and session parsing logic
- [ ] Create configuration management system

### Phase 3: Gradio UI Implementation
- [ ] Main layout with tabs (Chat, Files, Settings, etc.)
- [ ] Project/Session selector (Gradio Dropdown/Radio)
- [ ] Chat interface with streaming (Gradio Chatbot)
- [ ] File browser (Gradio File Explorer or custom component)
- [ ] Code editor with syntax highlighting (Gradio Code component)
- [ ] Settings panel (Gradio Form components)

### Phase 4: Advanced Features
- [ ] WebSocket/streaming for real-time updates
- [ ] Terminal emulator integration
- [ ] Git operations support
- [ ] TaskMaster AI integration (optional)
- [ ] Multi-session support

### Phase 5: Testing & Polish
- [ ] Test all core features
- [ ] Handle edge cases and errors
- [ ] Add loading states and user feedback
- [ ] Documentation and README
- [ ] Package for distribution

## Gradio Component Mapping

| Original (React) | Gradio Equivalent | Notes |
|-----------------|-------------------|-------|
| Sidebar navigation | `gr.Tabs` or `gr.Column` | For project/session selection |
| Chat interface | `gr.Chatbot` | With streaming support |
| Code editor | `gr.Code` | With syntax highlighting |
| File tree | `gr.FileExplorer` | Or custom HTML component |
| Settings form | `gr.Form` + inputs | Checkboxes, textboxes, etc. |
| WebSocket updates | `gr.Timer` + events | For polling/updates |
| Terminal | `gr.HTML` + custom JS | May need custom component |

## Python Module Structure
```
claude_code_gradio_ui/
├── claude_code_gradio_ui.py       # Main entry point
├── TASK.md                         # This file
├── README.md                       # User documentation
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore file
├── core/
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── database.py                 # SQLite database models
│   ├── claude_cli.py               # Claude Code CLI integration
│   └── session_parser.py           # JSONL session parsing
├── ui/
│   ├── __init__.py
│   ├── app.py                      # Main Gradio app
│   ├── chat.py                     # Chat interface
│   ├── files.py                    # File explorer
│   ├── settings.py                 # Settings panel
│   └── components.py               # Reusable UI components
└── utils/
    ├── __init__.py
    ├── file_operations.py          # File system utilities
    └── helpers.py                  # General helpers
```

## Key Technical Considerations

### 1. Real-time Communication
- Original: WebSocket for bidirectional communication
- Gradio: Use `gr.Timer` for polling or implement custom WebSocket handler
- Challenge: Gradio's event system is different from WebSocket

### 2. Session State Management
- Original: React state + localStorage
- Gradio: `gr.State` components + Python session management
- Challenge: Maintaining state across interactions

### 3. CLI Process Management
- Original: Node.js `spawn` with stdio pipes
- Gradio: Python `subprocess.Popen` with proper stream handling
- Challenge: Real-time output streaming

### 4. File System Operations
- Original: Express routes + Node.js fs module
- Gradio: Python `pathlib` + `os` module
- Challenge: Security (sandboxing file access)

### 5. Code Editor
- Original: CodeMirror (full-featured editor)
- Gradio: `gr.Code` (simpler, read-mostly)
- Challenge: Limited editing capabilities in Gradio

## Development Approach

As an Applied AI Research Engineer, this project will focus on:
1. **Rapid Prototyping**: Get core features working quickly
2. **Iterative Development**: Build, test, refine in cycles
3. **Data-Centric Thinking**: Focus on data flow and state management
4. **Python Best Practices**: Clean, maintainable, well-documented code
5. **User-Centric Design**: Prioritize usability and clarity

## Success Criteria
- [ ] Can launch app with `python claude_code_gradio_ui.py`
- [ ] Can browse and select Claude Code projects
- [ ] Can view and create chat sessions
- [ ] Can send messages and receive responses from Claude
- [ ] Can browse project files
- [ ] Can configure settings and credentials
- [ ] Code is clean, documented, and maintainable

## Current Status
- Phase 1: In Progress (Exploration and Planning)
- Next Steps: Complete component mapping and begin Phase 2

## Notes
- Keep it simple initially - focus on core chat functionality first
- Add advanced features incrementally
- Use pure Gradio components where possible
- Only create custom components if absolutely necessary
- Document all design decisions and trade-offs
