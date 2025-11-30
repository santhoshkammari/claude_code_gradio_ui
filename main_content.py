import gradio as gr
import state

def create_main_content():
    with gr.Column():
        gr.Markdown("### Main Content")
        gr.Textbox(label="Input", placeholder="Enter something...")
        gr.Button("Submit")
