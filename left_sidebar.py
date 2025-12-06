from a import gr

def create_left_sidebar():
    with gr.Column():
        gr.Markdown("### Left Sidebar")
        gr.Button("Left Action 1")
        gr.Button("Left Action 2")
