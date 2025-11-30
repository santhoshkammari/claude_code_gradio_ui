import gradio as gr

with gr.Blocks() as demo:
    with gr.Sidebar(position="left"):
        gr.Button()
    with gr.Sidebar(position="right",width=450):
        gr.Button()

demo.launch()
