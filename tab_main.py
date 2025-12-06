from a import gr

import time
import random

def tab_main():
    with gr.Blocks() as demo:
        with gr.Row():
            msg = gr.Textbox()
            clear = gr.Button("Clear")
