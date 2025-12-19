import gradio as gr
def update(name):
    return f"Welcome to Gradio, {name}!"

with gr.Blocks() as demo:
    inp = gr.Textbox(
        value=None,
        type="text",
        lines=2,
        max_lines=None,
        placeholder=None,
        label=None,
        info=None,
        every=None,
        inputs=None,
        show_label=False,
        container=False,
        scale=None,
        min_width=160,
        interactive=None,
        visible=True,
        elem_id=None,
        autofocus=False,
        autoscroll=True,
        elem_classes=None,
        render=True,
        key=None,
        preserved_by_key="value",
        text_align=None,
        rtl=False,
        buttons=None,
        max_length=None,
        submit_btn=False,
        stop_btn=False,
        html_attributes=None
        )



demo.launch(server_port=7862)
