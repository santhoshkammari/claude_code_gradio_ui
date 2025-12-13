import gradio as gr

css = """
.chatbot-container {
    height: 70vh;
    overflow-y: auto;
}

.input-row {
    position: sticky;
    bottom: 0;
    background: white;
    padding: 20px 0;
    border-top: 1px solid #e5e5e5;
}

.input-wrapper {
    position: relative;
    max-width: 800px;
    margin: 0 auto;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

.chat-input {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.chat-input textarea {
    border-radius: 24px !important;
    border: 1px solid #d1d5db !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    resize: none !important;
    box-shadow: 0 0 10px rgba(0,0,0,0.05) !important;
    overflow-y: hidden !important;
    scrollbar-width: none !important;
}

.chat-input textarea::-webkit-scrollbar {
    display: none !important;
}

.chat-input textarea:focus {
    border-color: #10a37f !important;
    box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1) !important;
    outline: none !important;
}

.send-btn {
    position: absolute !important;
    right: 8px !important;
    bottom: 8px !important;
    min-width: 36px !important;
    height: 36px !important;
    border-radius: 8px !important;
    background: #10a37f !important;
    border: none !important;
    padding: 0 !important;
}

.send-btn:hover {
    background: #0d8c6d !important;
}

.send-btn:disabled {
    background: #d1d5db !important;
    cursor: not-allowed !important;
}
"""

def chat_response(message, history):
    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": f"Echo: {message}"})
    return history, ""

with gr.Blocks(title="ChatGPT Clone") as demo:
    gr.Markdown("# ChatGPT-like Interface")

    chatbot = gr.Chatbot(
        [],
        elem_classes="chatbot-container",
        height=500
    )

    with gr.Row(elem_classes="input-row"):
        with gr.Column(scale=1, elem_classes="input-wrapper"):
            msg = gr.Textbox(
                placeholder="Message ChatGPT...",
                show_label=False,
                container=False,
                elem_classes="chat-input",
                lines=1,
                max_lines=5,
                autofocus=True
            )

    msg.submit(chat_response, [msg, chatbot], [chatbot, msg])

if __name__ == "__main__":
    demo.launch(css=css)
