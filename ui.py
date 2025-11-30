import gradio as gr
from left_sidebar import create_left_sidebar
from main_content import create_main_content
from right_sidebar import create_right_sidebar

with gr.Blocks() as demo:
    with gr.Sidebar(position="left"):
        create_left_sidebar()

    create_main_content()

    with gr.Sidebar(position="right", width=450):
        create_right_sidebar()

demo.launch()
