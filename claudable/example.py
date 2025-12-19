import gradio as gr

def process_text(text):
    """Simple function to demonstrate the textbox functionality"""
    if not text.strip():
        return "Please enter some text first!"
    return f"Processed: {text[:100]}..." if len(text) > 100 else f"Processed: {text}"

def main():
    with gr.Blocks(
        title="Modern Gradio Textbox Examples",
        theme=gr.themes.Soft(),
        css="""
        /* Modern textbox styling */
        .modern-textbox {
            border: 2px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            font-size: 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
            background-color: white !important;
        }
        
        .modern-textbox:focus-within {
            border-color: #6366f1 !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
        }
        
        /* Rounded textbox styling */
        .rounded-textbox {
            border: 2px solid #cbd5e1 !important;
            border-radius: 24px !important;
            padding: 14px 20px !important;
            font-size: 16px !important;
            background-color: #f8fafc !important;
        }
        
        .rounded-textbox:focus-within {
            border-color: #8b5cf6 !important;
            box-shadow: 0 4px 16px rgba(139, 92, 246, 0.2) !important;
        }
        
        /* Minimal textbox styling */
        .minimal-textbox {
            border: 1px solid transparent !important;
            border-bottom: 2px solid #cbd5e1 !important;
            border-radius: 0 !important;
            padding: 10px 0 !important;
            background: transparent !important;
        }
        
        .minimal-textbox:focus-within {
            border-bottom-color: #3b82f6 !important;
            background: transparent !important;
        }
        
        /* Gradient textbox styling */
        .gradient-textbox {
            border: none !important;
            border-radius: 16px !important;
            padding: 16px !important;
            font-size: 16px !important;
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        }
        
        .gradient-textbox:focus-within {
            background: linear-gradient(135deg, #e0f7fa, #b3e5fc) !important;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1) !important;
        }
        
        /* Output box styling */
        .output-box {
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 16px !important;
            background-color: #f8fafc !important;
            min-height: 100px !important;
            font-family: ui-sans-serif, system-ui, sans-serif !important;
            white-space: pre-wrap !important;
        }
        
        /* Custom button styling */
        .custom-button {
            border-radius: 12px !important;
            padding: 8px 20px !important;
            font-weight: 600 !important;
            transition: all 0.2s !important;
        }
        
        /* Title styling */
        h1 {
            text-align: center;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 2rem !important;
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
        }
        
        .section-title {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            margin: 1.5rem 0 1rem 0 !important;
            color: #1e293b !important;
        }
        """
    ) as demo:
        gr.Markdown("# 🚀 Modern Gradio Textbox Examples")
        
        with gr.Tab("🎨 Themed Examples"):
            gr.Markdown("### Different Gradio Themes Applied")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Default Theme")
                    with gr.Blocks(theme=gr.themes.Default()) as default_theme:
                        textbox1 = gr.Textbox(
                            label="Default Theme Input",
                            placeholder="Type here with default theme...",
                            elem_classes=["modern-textbox"]
                        )
                
                with gr.Column():
                    gr.Markdown("#### Soft Theme")
                    textbox2 = gr.Textbox(
                        label="Soft Theme Input",
                        placeholder="Type here with soft theme...",
                        elem_classes=["rounded-textbox"]
                    )
            
            default_theme.render()
        
        with gr.Tab("✏️ Custom Styled Textboxes"):
            gr.Markdown("### Various Custom Styling Approaches")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Modern Rounded Style")
                    textbox3 = gr.Textbox(
                        label="Modern Rounded Textbox",
                        placeholder="Type with rounded corners...",
                        elem_classes=["rounded-textbox"],
                        container=False
                    )
                    
                    gr.Markdown("#### Minimal Underline Style")
                    textbox4 = gr.Textbox(
                        label="Minimal Textbox",
                        placeholder="Minimal underline style...",
                        elem_classes=["minimal-textbox"],
                        container=False
                    )
                
                with gr.Column():
                    gr.Markdown("#### Gradient Background Style")
                    textbox5 = gr.Textbox(
                        label="Gradient Textbox",
                        placeholder="Text with gradient background...",
                        elem_classes=["gradient-textbox"]
                    )
                    
                    gr.Markdown("#### With Buttons")
                    textbox6 = gr.Textbox(
                        label="Text with Copy Button",
                        placeholder="Try the copy button!",
                        buttons=["copy"],
                        elem_classes=["modern-textbox"]
                    )
        
        with gr.Tab("📝 Advanced Features"):
            gr.Markdown("### Advanced Textbox Functionality")
            
            with gr.Row():
                with gr.Column():
                    input_text = gr.Textbox(
                        label="Input Text",
                        placeholder="Enter text to process...",
                        lines=4,
                        max_lines=10,
                        elem_classes=["gradient-textbox"],
                        html_attributes={"spellcheck": "false"}
                    )
                    
                    process_btn = gr.Button(
                        "Process Text", 
                        variant="primary", 
                        elem_classes=["custom-button"]
                    )
                
                with gr.Column():
                    output_text = gr.Textbox(
                        label="Processed Output",
                        interactive=False,
                        elem_classes=["output-box"]
                    )
            
            process_btn.click(
                fn=process_text,
                inputs=input_text,
                outputs=output_text
            )
        
        with gr.Tab("📱 Multi-line Textbox"):
            gr.Markdown("### Multi-line Textbox with Modern Styling")
            
            multiline = gr.Textbox(
                label="Multi-line Textbox",
                placeholder="Enter multiple lines of text here...",
                lines=6,
                max_lines=15,
                elem_classes=["gradient-textbox"],
                container=True
            )
    
    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch(share=True, server_port=7862, show_error=True)