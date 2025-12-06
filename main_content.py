import gradio as gr
import state
from tab_main import tab_main

def create_main_content():
    with gr.Tab('Task'):
        tab_main()
    with gr.Tab('History'):
        tab_main()
