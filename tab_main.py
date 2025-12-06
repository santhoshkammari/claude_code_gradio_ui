import gradio as gr

def tab_main():
    with gr.Column():
        gr.Textbox(label="Input", placeholder="Enter something...")
        gr.Button("Submit")

