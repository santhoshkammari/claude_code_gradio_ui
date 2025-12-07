from a import gr

from left_sidebar import create_left_sidebar
from right_sidebar import create_right_sidebar
from tab_main import tab_main

custom_css = """
.gradio-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}
.main {
    padding: 0 !important;
    gap: 0 !important;
}
.contain {
    padding: 0 !important;
}
.wrap {
    padding: 0 !important;
}
.sidebar-parent {
    padding: 0 !important;
}
body {
    margin: 0 !important;
    padding: 0 !important;
}
"""

with gr.Blocks() as demo:
    with gr.Sidebar(position="left", width=250):
        create_left_sidebar()

    tab_main()

    with gr.Sidebar(position="right", width=350):
        create_right_sidebar()

demo.launch(css=custom_css)
