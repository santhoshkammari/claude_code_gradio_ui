import gradio as gr
import json

def handle_submit(message, model, mode, images):
    """Handle form submission"""
    return f"Message: {message}\nModel: {model}\nMode: {mode}\nImages: {len(images) if images else 0}"

def handle_prompt_click(prompt_text):
    """Handle clicking on a prompt button"""
    return prompt_text

css = """
    body, .gradio-container {
        background-color: rgb(249, 250, 251) !important;
    }

    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 20px;
    }

    .claudable-heading {
        font-size: 72px;
        font-weight: 800;
        color: rgb(222, 115, 86);
        text-align: center;
        margin-bottom: 16px;
        font-family: system-ui, -apple-system, sans-serif;
    }

    .claudable-subtitle {
        font-size: 14px;
        color: rgb(107, 114, 128);
        text-align: center;
        margin-bottom: 60px;
        font-family: system-ui, -apple-system, sans-serif;
    }

    .input-container {
        background: white;
        border-radius: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 24px;
        margin-bottom: 24px;
    }

    .textarea-wrapper {
        margin-bottom: 16px;
    }

    .custom-textarea {
        width: 100%;
        min-height: 120px;
        border: none;
        outline: none;
        resize: none;
        font-size: 16px;
        font-family: system-ui, -apple-system, sans-serif;
        color: rgb(17, 24, 39);
        background: transparent;
        padding: 0;
    }

    .custom-textarea::placeholder {
        color: rgb(156, 163, 175);
    }

    .controls-row {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }

    .icon-button {
        background: transparent;
        border: 1px solid rgba(229, 231, 235, 0.5);
        border-radius: 9999px;
        padding: 8px 12px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        color: rgb(55, 65, 81);
        transition: all 0.2s;
        font-family: system-ui, -apple-system, sans-serif;
    }

    .icon-button:hover {
        background: rgb(249, 250, 251);
        border-color: rgb(209, 213, 219);
    }

    .dropdown-button {
        background: transparent;
        border: 1px solid rgba(229, 231, 235, 0.5);
        border-radius: 9999px;
        padding: 8px 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: rgb(55, 65, 81);
        transition: all 0.2s;
        font-family: system-ui, -apple-system, sans-serif;
        position: relative;
    }

    .dropdown-button:hover {
        background: rgb(249, 250, 251);
        border-color: rgb(209, 213, 219);
    }

    .submit-button {
        background: rgb(107, 114, 128);
        border: none;
        border-radius: 9999px;
        padding: 10px 16px;
        cursor: pointer;
        margin-left: auto;
        transition: all 0.2s;
    }

    .submit-button:hover:not(:disabled) {
        background: rgb(75, 85, 99);
    }

    .submit-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .submit-icon {
        width: 20px;
        height: 20px;
        fill: white;
    }

    .prompts-row {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
    }

    .prompt-button {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(229, 231, 235, 0.5);
        border-radius: 12px;
        padding: 12px 20px;
        cursor: pointer;
        font-size: 14px;
        color: rgb(55, 65, 81);
        transition: all 0.2s;
        font-family: system-ui, -apple-system, sans-serif;
    }

    .prompt-button:hover {
        background: white;
        border-color: rgb(209, 213, 219);
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .hidden {
        display: none !important;
    }

    #file-input {
        display: none;
    }

    .claude-icon {
        width: 16px;
        height: 16px;
    }

    .dropdown-icon {
        width: 12px;
        height: 12px;
    }
"""

html_content = """
<div class="main-container">
    <h1 class="claudable-heading">Claudable</h1>
    <p class="claudable-subtitle">Connect CLI Agent • Build what you want • Deploy instantly</p>

    <div class="input-container">
        <div class="textarea-wrapper">
            <textarea
                id="message-input"
                class="custom-textarea"
                placeholder="Ask Claudable to create a blog about..."
                oninput="updateSubmitButton()"
            ></textarea>
        </div>

        <div class="controls-row">
            <button class="icon-button" onclick="triggerFileUpload()" id="upload-btn">
                <svg class="claude-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21 15 16 10 5 21"></polyline>
                </svg>
            </button>
            <input type="file" id="file-input" multiple accept="image/*" onchange="handleFileUpload(event)" />

            <button class="dropdown-button" id="mode-dropdown" onclick="toggleDropdown('mode')">
                <svg class="claude-icon" fill="rgb(222, 115, 86)" viewBox="0 0 24 24">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                </svg>
                <span id="mode-text">Claude Code</span>
                <svg class="dropdown-icon" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>

            <button class="dropdown-button" id="model-dropdown" onclick="toggleDropdown('model')">
                <span id="model-text">Claude Sonnet 4.5</span>
                <svg class="dropdown-icon" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
            </button>

            <button class="submit-button" id="submit-btn" disabled onclick="handleSubmit()">
                <svg class="submit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="19" x2="12" y2="5"></line>
                    <polyline points="5 12 12 5 19 12"></polyline>
                </svg>
            </button>
        </div>
    </div>

    <div class="prompts-row">
        <button class="prompt-button" onclick="fillPrompt('Landing Page')">Landing Page</button>
        <button class="prompt-button" onclick="fillPrompt('Gaming Platform')">Gaming Platform</button>
        <button class="prompt-button" onclick="fillPrompt('Onboarding Portal')">Onboarding Portal</button>
        <button class="prompt-button" onclick="fillPrompt('Networking App')">Networking App</button>
        <button class="prompt-button" onclick="fillPrompt('Room Visualizer')">Room Visualizer</button>
    </div>
</div>

<script>
    let selectedFiles = [];
    let currentMode = 'Claude Code';
    let currentModel = 'Claude Sonnet 4.5';

    function triggerFileUpload() {
        document.getElementById('file-input').click();
    }

    function handleFileUpload(event) {
        selectedFiles = Array.from(event.target.files);
        console.log('Files selected:', selectedFiles.length);
        // You can add visual feedback here for uploaded files
    }

    function updateSubmitButton() {
        const textarea = document.getElementById('message-input');
        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = !textarea.value.trim();
    }

    function toggleDropdown(type) {
        // Basic dropdown toggle - in a real implementation,
        // you'd show a dropdown menu here
        if (type === 'mode') {
            const modes = ['Claude Code', 'Claude Dev', 'Custom Mode'];
            const currentIndex = modes.indexOf(currentMode);
            currentMode = modes[(currentIndex + 1) % modes.length];
            document.getElementById('mode-text').textContent = currentMode;
        } else if (type === 'model') {
            const models = ['Claude Sonnet 4.5', 'Claude Opus 4', 'Claude Haiku'];
            const currentIndex = models.indexOf(currentModel);
            currentModel = models[(currentIndex + 1) % models.length];
            document.getElementById('model-text').textContent = currentModel;
        }
    }

    function fillPrompt(promptText) {
        const textarea = document.getElementById('message-input');
        textarea.value = `Create a ${promptText}`;
        updateSubmitButton();
        textarea.focus();
    }

    function handleSubmit() {
        const message = document.getElementById('message-input').value;
        if (!message.trim()) return;

        // This would typically send data to backend
        console.log('Submitting:', {
            message: message,
            mode: currentMode,
            model: currentModel,
            files: selectedFiles.length
        });

        // You can trigger a Gradio event here
        // For now, just clear the textarea
        document.getElementById('message-input').value = '';
        updateSubmitButton();
    }

    // Allow Enter to submit (Shift+Enter for new line)
    document.addEventListener('DOMContentLoaded', function() {
        const textarea = document.getElementById('message-input');
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!document.getElementById('submit-btn').disabled) {
                    handleSubmit();
                }
            }
        });
    });
</script>
"""

demo = gr.Blocks(css=css, fill_height=True, fill_width=True)

with demo:
    # Hidden components to handle backend logic
    with gr.Row(visible=False):
        message_state = gr.Textbox(elem_id="message-state")
        model_state = gr.Textbox(value="Claude Sonnet 4.5", elem_id="model-state")
        mode_state = gr.Textbox(value="Claude Code", elem_id="mode-state")
        images_state = gr.File(file_count="multiple", type="filepath", elem_id="images-state")
        output_state = gr.Textbox(elem_id="output-state")

    # Main HTML UI
    gr.HTML(html_content)

    # You can wire up backend handlers here if needed
    # For example:
    # submit_btn.click(
    #     fn=handle_submit,
    #     inputs=[message_state, model_state, mode_state, images_state],
    #     outputs=[output_state]
    # )

if __name__ == "__main__":
    demo.launch(server_port=7862)
