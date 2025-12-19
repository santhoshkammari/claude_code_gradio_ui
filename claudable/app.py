import gradio as gr
def update(name):
    return f"Welcome to Gradio, {name}!"

css="""
    .transparent-md {
        background-color: white !important; 
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    .block {
  border: none !important;
  box-shadow: none !important;
  background: white !important;
}
    """

demo = gr.Blocks(
         fill_height = False,
        fill_width = False,
) 
with demo:
    gr.Markdown("Claudable",height=250)
    gr.Markdown("Connect CLI Agent • Build what you want • Deploy instantly")

    with gr.Row():
        with gr.Group():
            inp = gr.Textbox(
                value=None,
                type="text",
                lines=5,
                max_lines=6,
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
            with gr.Group():
                with gr.Row(equal_height=True):
                    gr.Markdown(elem_classes="transparent-md")
                    gr.Markdown(elem_classes="transparent-md")
                    gr.Markdown(elem_classes="transparent-md")
                    gr.Markdown(elem_classes="transparent-md")
                    gr.Markdown(elem_classes="transparent-md")
                    gr.Markdown(elem_classes="transparent-md")
                    gr.Dropdown(choices=["Sonnet", "Haiku"], interactive=True,show_label=False,container=False,min_width=80)
                    gr.Button("Send")

demo.launch(server_port=7862,css=css)   
