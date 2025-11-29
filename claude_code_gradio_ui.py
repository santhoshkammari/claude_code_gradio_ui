#!/usr/bin/env python3
"""
Claude Code Gradio UI - Main Entry Point

A pure Python/Gradio-based user interface for Claude Code CLI.

Usage:
    python claude_code_gradio_ui.py
"""

import gradio as gr
from pathlib import Path


def create_app():
    """
    Create and configure the main Gradio application.

    Returns:
        gr.Blocks: The configured Gradio application
    """

    with gr.Blocks(
        title="Claude Code UI",
        theme=gr.themes.Soft(),
    ) as app:

        # Header
        gr.Markdown(
            """
            # Claude Code Gradio UI

            A Python-based interface for Claude Code CLI
            """
        )

        # Main content area with tabs
        with gr.Tabs() as tabs:

            # Chat Tab
            with gr.Tab("Chat"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="Claude Code Chat",
                            height=500,
                        )
                        with gr.Row():
                            msg = gr.Textbox(
                                label="Message",
                                placeholder="Type your message here...",
                                scale=4,
                            )
                            send_btn = gr.Button("Send", scale=1, variant="primary")

                    with gr.Column(scale=1):
                        gr.Markdown("### Project Selection")
                        project_dropdown = gr.Dropdown(
                            label="Select Project",
                            choices=["No projects found"],
                            interactive=True,
                        )
                        session_dropdown = gr.Dropdown(
                            label="Select Session",
                            choices=["No sessions"],
                            interactive=True,
                        )
                        new_session_btn = gr.Button("New Session", variant="secondary")

            # Files Tab
            with gr.Tab("Files"):
                gr.Markdown("### File Explorer")
                gr.Markdown("File explorer functionality coming soon...")

            # Settings Tab
            with gr.Tab("Settings"):
                gr.Markdown("### Settings")
                with gr.Accordion("API Configuration", open=True):
                    api_key = gr.Textbox(
                        label="Anthropic API Key",
                        type="password",
                        placeholder="sk-ant-...",
                    )
                    save_settings_btn = gr.Button("Save Settings", variant="primary")

        # Footer
        gr.Markdown(
            """
            ---
            Built with [Gradio](https://gradio.app) |
            Based on [ClaudeCodeUI](https://github.com/siteboon/claudecodeui) |
            Powered by [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
            """
        )

        # Event handlers (placeholder functions for now)
        def respond(message, chat_history):
            """Handle chat message submission."""
            # TODO: Implement actual Claude Code integration
            bot_message = f"Echo: {message}"
            chat_history.append((message, bot_message))
            return "", chat_history

        # Connect events
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        send_btn.click(respond, [msg, chatbot], [msg, chatbot])

    return app


def main():
    """Main entry point for the application."""
    print("Starting Claude Code Gradio UI...")
    print("=" * 50)

    # Create and launch the app
    app = create_app()

    # Launch with configuration
    app.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True for public sharing
        show_error=True,
    )


if __name__ == "__main__":
    main()
