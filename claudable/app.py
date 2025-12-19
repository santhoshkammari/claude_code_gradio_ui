import gradio as gr
import json

def handle_submit(message, model, mode, images):
    """Handle form submission"""
    return f"Message: {message}\nModel: {model}\nMode: {mode}\nImages: {len(images) if images else 0}"

def handle_prompt_click(prompt_text):
    """Handle clicking on a prompt button"""
    return prompt_text

css = """
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    body, .gradio-container {
        background-color: rgb(249, 250, 251) !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", Inter, system-ui, Arial, sans-serif !important;
    }

    .main-container {
        max-width: 896px;
        margin: 0 auto;
        padding: 80px 20px 40px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .header-section {
        text-align: center;
        margin-bottom: 48px;
    }

    .claudable-heading {
        font-size: 72px;
        font-weight: 800;
        color: rgb(222, 115, 86);
        text-align: center;
        margin: 0 0 16px 0;
        font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
        letter-spacing: -4.32px;
        line-height: 72px;
        transition: color 1s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .claudable-subtitle {
        font-size: 14px;
        color: rgb(107, 114, 128);
        text-align: center;
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", Inter, system-ui, Arial, sans-serif;
        line-height: 20px;
    }

    .input-container {
        width: 100%;
        max-width: 896px;
        background: rgb(255, 255, 255);
        border-radius: 28px;
        border: 1px solid rgb(229, 231, 235);
        box-shadow: rgba(0, 0, 0, 0.1) 0px 20px 25px -5px, rgba(0, 0, 0, 0.1) 0px 8px 10px -6px;
        padding: 16px;
        margin-bottom: 24px;
        transition: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .input-container:hover {
        box-shadow: rgba(0, 0, 0, 0.12) 0px 24px 30px -5px, rgba(0, 0, 0, 0.12) 0px 10px 12px -6px;
    }

    .textarea-wrapper {
        width: 100%;
    }

    .custom-textarea {
        width: 100%;
        min-height: 120px;
        border: none !important;
        outline: none !important;
        resize: none;
        font-size: 16px;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", Inter, system-ui, Arial, sans-serif;
        color: rgb(17, 24, 39);
        background: transparent !important;
        padding: 8px;
        border-radius: 0;
        line-height: 24px;
        box-shadow: none !important;
    }

    .custom-textarea:focus {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    .custom-textarea::placeholder {
        color: rgb(156, 163, 175);
    }

    .controls-row {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }

    .icon-button {
        background: transparent;
        border: 1px solid rgba(229, 231, 235, 0.5);
        border-radius: 9999px;
        padding: 10px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        font-size: 14px;
        color: rgb(156, 163, 175);
        transition: color 0.1s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.1s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.1s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", Inter, system-ui, Arial, sans-serif;
        box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 2px 0px;
        min-width: 36px;
        min-height: 36px;
    }

    .icon-button:hover {
        background: rgb(249, 250, 251);
        border-color: rgb(209, 213, 219);
        color: rgb(55, 65, 81);
    }

    .dropdown-button {
        background: transparent;
        border: 1px solid rgba(229, 231, 235, 0.5);
        border-radius: 9999px;
        padding: 8px 12px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        font-weight: 500;
        color: rgb(55, 65, 81);
        transition: color 0.1s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.1s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.1s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", Inter, system-ui, Arial, sans-serif;
        position: relative;
        box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 2px 0px;
        line-height: 20px;
    }

    .dropdown-button:hover {
        background: rgb(249, 250, 251);
        border-color: rgb(209, 213, 219);
    }

    .dropdown-button:active {
        transform: scale(0.98);
    }

    .submit-button {
        background: rgb(17, 24, 39);
        border: none;
        border-radius: 9999px;
        width: 40px;
        height: 40px;
        cursor: pointer;
        margin-left: auto;
        transition: opacity 0.15s cubic-bezier(0, 0, 0.2, 1), background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1), transform 0.1s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .submit-button:hover:not(:disabled) {
        background: rgb(31, 41, 55);
        transform: scale(1.05);
    }

    .submit-button:active:not(:disabled) {
        transform: scale(0.95);
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
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 32px;
        width: 100%;
        max-width: 896px;
    }

    .prompt-button {
        background: rgba(255, 255, 255, 0);
        border: 1px solid rgba(222, 115, 86, 0.1);
        border-radius: 9999px;
        padding: 8px 16px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: rgb(107, 114, 128);
        transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", "Segoe UI", Inter, system-ui, Arial, sans-serif;
        line-height: 20px;
    }

    .prompt-button:hover {
        background: rgb(249, 250, 251);
        border-color: rgba(222, 115, 86, 0.15);
        color: rgb(55, 65, 81);
        transform: translateY(-1px);
    }

    .prompt-button:active {
        transform: translateY(0px);
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
        flex-shrink: 0;
    }

    .dropdown-icon {
        width: 12px;
        height: 12px;
        flex-shrink: 0;
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .dropdown-button:hover .dropdown-icon {
        transform: translateY(1px);
    }

    /* Footer styling */
    .footer-section {
        margin-top: 40px;
        text-align: center;
        display: flex;
        gap: 16px;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        color: rgb(156, 163, 175);
    }

    .footer-link {
        color: rgb(107, 114, 128);
        text-decoration: none;
        transition: color 0.2s;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .footer-link:hover {
        color: rgb(222, 115, 86);
    }

    /* Image upload preview */
    .upload-preview {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 8px;
    }

    .upload-preview-item {
        width: 60px;
        height: 60px;
        border-radius: 8px;
        background: rgb(249, 250, 251);
        border: 1px solid rgb(229, 231, 235);
        position: relative;
        overflow: hidden;
    }

    .upload-preview-item img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .remove-preview {
        position: absolute;
        top: -4px;
        right: -4px;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: rgb(17, 24, 39);
        color: white;
        border: none;
        cursor: pointer;
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
    }

    .remove-preview:hover {
        background: rgb(222, 115, 86);
    }

    /* Dropdown menu styling */
    .dropdown-menu {
        position: absolute;
        top: calc(100% + 8px);
        left: 0;
        background: white;
        border: 1px solid rgb(229, 231, 235);
        border-radius: 12px;
        box-shadow: rgba(0, 0, 0, 0.1) 0px 10px 25px -5px, rgba(0, 0, 0, 0.05) 0px 8px 10px -6px;
        padding: 6px;
        min-width: 180px;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transform: translateY(-10px);
        transition: opacity 0.15s cubic-bezier(0.4, 0, 0.2, 1), transform 0.15s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.15s;
    }

    .dropdown-menu.active {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
    }

    .dropdown-item {
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        color: rgb(55, 65, 81);
        transition: background 0.1s;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .dropdown-item:hover {
        background: rgb(249, 250, 251);
    }

    .dropdown-item.selected {
        background: rgb(249, 250, 251);
        color: rgb(222, 115, 86);
        font-weight: 500;
    }

    .dropdown-button {
        position: relative;
    }
"""

html_content = """
<div class="main-container">
    <div class="header-section">
        <h1 class="claudable-heading">Claudable</h1>
        <p class="claudable-subtitle">Connect CLI Agent • Build what you want • Deploy instantly</p>
    </div>

    <div class="input-container">
        <div class="textarea-wrapper">
            <textarea
                id="message-input"
                class="custom-textarea"
                placeholder="Ask Claudable to create a blog about..."
                oninput="updateSubmitButton()"
            ></textarea>
        </div>

        <div id="upload-preview" class="upload-preview"></div>

        <div class="controls-row">
            <button class="icon-button" onclick="triggerFileUpload()" id="upload-btn" title="Upload images">
                <svg class="claude-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21 15 16 10 5 21"></polyline>
                </svg>
            </button>
            <input type="file" id="file-input" multiple accept="image/*" onchange="handleFileUpload(event)" />

            <div style="position: relative;">
                <button class="dropdown-button" id="mode-dropdown" onclick="toggleDropdown('mode')" title="Select mode">
                    <svg class="claude-icon" fill="rgb(222, 115, 86)" viewBox="0 0 24 24">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                    </svg>
                    <span id="mode-text">Claude Code</span>
                    <svg class="dropdown-icon" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
                <div class="dropdown-menu" id="mode-menu">
                    <div class="dropdown-item selected" onclick="selectMode('Claude Code')">
                        <svg class="claude-icon" fill="rgb(222, 115, 86)" viewBox="0 0 24 24">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                        </svg>
                        Claude Code
                    </div>
                    <div class="dropdown-item" onclick="selectMode('Qwen')">
                        <svg class="claude-icon" fill="rgb(147, 51, 234)" viewBox="0 0 24 24">
                            <path d="M13 2L3 14h8l-1 8 10-12h-8l1-8z"></path>
                        </svg>
                        Qwen
                    </div>
                </div>
            </div>

            <div style="position: relative;">
                <button class="dropdown-button" id="model-dropdown" onclick="toggleDropdown('model')" title="Select model">
                    <span id="model-text">Claude Sonnet 4.5</span>
                    <svg class="dropdown-icon" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
                <div class="dropdown-menu" id="model-menu">
                    <div class="dropdown-item selected" onclick="selectModel('Claude Sonnet 4.5')">Claude Sonnet 4.5</div>
                    <div class="dropdown-item" onclick="selectModel('Claude Haiku 4.5')">Claude Haiku 4.5</div>
                </div>
            </div>

            <button class="submit-button" id="submit-btn" disabled onclick="handleSubmit()" title="Send message">
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

    <div class="footer-section">
        <a href="#" class="footer-link" onclick="return false;">
            <span>Use via API</span>
            <span>🔌</span>
        </a>
        <span>•</span>
        <a href="#" class="footer-link" onclick="return false;">
            <span>Built with Gradio</span>
            <span>🎨</span>
        </a>
        <span>•</span>
        <a href="#" class="footer-link" onclick="return false;">
            <span>Settings</span>
            <span>⚙️</span>
        </a>
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
        displayImagePreviews();
    }

    function displayImagePreviews() {
        const previewContainer = document.getElementById('upload-preview');
        previewContainer.innerHTML = '';

        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const previewItem = document.createElement('div');
                previewItem.className = 'upload-preview-item';
                previewItem.innerHTML = `
                    <img src="${e.target.result}" alt="Preview ${index + 1}" />
                    <button class="remove-preview" onclick="removeFile(${index})" title="Remove">×</button>
                `;
                previewContainer.appendChild(previewItem);
            };
            reader.readAsDataURL(file);
        });

        if (selectedFiles.length === 0) {
            previewContainer.style.display = 'none';
        } else {
            previewContainer.style.display = 'flex';
        }
    }

    function removeFile(index) {
        selectedFiles.splice(index, 1);
        displayImagePreviews();
    }

    function updateSubmitButton() {
        const textarea = document.getElementById('message-input');
        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = !textarea.value.trim();
    }

    function toggleDropdown(type) {
        const modeMenu = document.getElementById('mode-menu');
        const modelMenu = document.getElementById('model-menu');

        if (type === 'mode') {
            modeMenu.classList.toggle('active');
            modelMenu.classList.remove('active');
        } else if (type === 'model') {
            modelMenu.classList.toggle('active');
            modeMenu.classList.remove('active');
        }
    }

    function selectMode(mode) {
        currentMode = mode;
        document.getElementById('mode-text').textContent = mode;
        document.getElementById('mode-menu').classList.remove('active');

        // Update selected state
        const items = document.querySelectorAll('#mode-menu .dropdown-item');
        items.forEach(item => {
            if (item.textContent.trim() === mode) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    function selectModel(model) {
        currentModel = model;
        document.getElementById('model-text').textContent = model;
        document.getElementById('model-menu').classList.remove('active');

        // Update selected state
        const items = document.querySelectorAll('#model-menu .dropdown-item');
        items.forEach(item => {
            if (item.textContent.trim() === model) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-button') && !e.target.closest('.dropdown-menu')) {
            document.getElementById('mode-menu').classList.remove('active');
            document.getElementById('model-menu').classList.remove('active');
        }
    });

    function fillPrompt(promptText) {
        const textarea = document.getElementById('message-input');
        textarea.value = `Create a ${promptText}`;
        updateSubmitButton();
        textarea.focus();
    }

    function handleSubmit() {
        const message = document.getElementById('message-input').value;
        if (!message.trim()) return;

        console.log('Submitting:', {
            message: message,
            mode: currentMode,
            model: currentModel,
            files: selectedFiles.length
        });

        // Clear the form
        document.getElementById('message-input').value = '';
        selectedFiles = [];
        displayImagePreviews();
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

demo = gr.Blocks(css=css, fill_height=True, fill_width=True, title="Claudable")

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
