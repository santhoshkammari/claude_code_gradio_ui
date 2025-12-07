from a import gr

from left_sidebar import create_left_sidebar
from right_sidebar import create_right_sidebar
from tab_main import tab_main

with gr.Blocks() as demo:
    with gr.Sidebar(position="left", width=250):
        create_left_sidebar()

    tab_main()

    with gr.Sidebar(position="right", width=350):
        create_right_sidebar()

demo.launch()
