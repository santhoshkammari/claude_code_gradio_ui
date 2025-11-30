import gradio as gr
import state

def create_right_sidebar():
    with gr.Column():
        gr.Markdown("### Right Sidebar")
        gr.Button("Right Action 1")
        gr.Button("Right Action 2")
