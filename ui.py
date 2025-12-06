from a import gr

from left_sidebar import create_left_sidebar
from right_sidebar import create_right_sidebar
from tab_main import tab_main

with gr.Blocks() as demo:
    with gr.Sidebar(position="left",width='15%'):
        create_left_sidebar()

    with gr.Column():
        with gr.Tab('Task'):
            tab_main()
        with gr.Tab('History'):
            tab_main()

    with gr.Sidebar(position="right", width="28%"):
        create_right_sidebar()

demo.launch()
