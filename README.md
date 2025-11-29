# Claude Code Gradio UI

A pure Python/Gradio-based user interface for Claude Code CLI.

## Overview

This project is a Gradio-based conversion of the original ClaudeCodeUI (React/Node.js), providing a clean Python interface for interacting with Claude Code and managing your AI-assisted development sessions.

## Features

- Browse and manage Claude Code projects
- Interactive chat interface with Claude
- Session management (create, view, delete)
- File explorer and editor
- Settings and configuration management
- Real-time updates and streaming responses

## Installation

### Prerequisites

- Python 3.8 or higher
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and configured

### Setup

1. Clone the repository:
```bash
git clone https://github.com/santhoshkammari/claude_code_gradio_ui.git
cd claude_code_gradio_ui
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using uv (recommended for faster installation):
```bash
uv pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python claude_code_gradio_ui.py
```

The Gradio interface will open in your default browser (typically at `http://localhost:7860`).

## Project Structure

```
claude_code_gradio_ui/
├── claude_code_gradio_ui.py       # Main entry point
├── TASK.md                         # Development roadmap
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── core/                           # Core functionality
│   ├── config.py                   # Configuration management
│   ├── database.py                 # Database models
│   ├── claude_cli.py               # CLI integration
│   └── session_parser.py           # Session parsing
├── ui/                             # Gradio UI components
│   ├── app.py                      # Main app
│   ├── chat.py                     # Chat interface
│   ├── files.py                    # File explorer
│   └── settings.py                 # Settings panel
└── utils/                          # Utilities
    ├── file_operations.py          # File operations
    └── helpers.py                  # Helper functions
```

## Development Status

This project is currently in early development. See [TASK.md](TASK.md) for the detailed development roadmap and current progress.

### Current Phase: Planning & Initial Development
- [x] Project structure setup
- [x] Initial planning and architecture design
- [ ] Core infrastructure implementation
- [ ] Gradio UI implementation
- [ ] Testing and refinement

## Original Project

This is a Python/Gradio conversion of [ClaudeCodeUI](https://github.com/siteboon/claudecodeui) by siteboon.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

Santhosh Kammari (santhoshkammari1999@gmail.com)

## Acknowledgments

- Original ClaudeCodeUI project by siteboon
- Anthropic's Claude Code CLI
- Gradio framework by Hugging Face
