// UI interaction module
import AppState from './state.js';
import ClaudeAPI from './api.js';

class UIController {
    constructor() {
        this.state = new AppState();
        this.api = new ClaudeAPI();
        this.init();
    }

    init() {
        this.bindElements();
        this.attachEventListeners();
        this.setupStateSubscriptions();
    }

    bindElements() {
        this.messageInput = document.getElementById('message-input');
        this.submitBtn = document.getElementById('submit-btn');
        this.uploadBtn = document.getElementById('upload-btn');
        this.fileInput = document.getElementById('file-input');
        this.modeBtn = document.getElementById('mode-btn');
        this.modeMenu = document.getElementById('mode-menu');
        this.modeSelected = document.getElementById('mode-selected');
        this.modelBtn = document.getElementById('model-btn');
        this.modelMenu = document.getElementById('model-menu');
        this.modelSelected = document.getElementById('model-selected');
        this.responseContainer = document.getElementById('response-container');
        this.responseContent = document.getElementById('response-content');
    }

    attachEventListeners() {
        // Upload button
        this.uploadBtn.addEventListener('click', () => {
            this.fileInput.click();
        });

        // File input
        this.fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.state.set('files', files);
            console.log('Files selected:', files.map(f => f.name));
        });

        // Mode dropdown
        this.modeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown(this.modeMenu);
        });

        // Model dropdown
        this.modelBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown(this.modelMenu);
        });

        // Mode dropdown items
        document.querySelectorAll('#mode-menu .dropdown-item').forEach(item => {
            item.addEventListener('click', () => {
                const value = item.getAttribute('data-value');
                this.state.set('mode', value);
                this.modeSelected.textContent = this.getDisplayName(value);
                this.modeMenu.classList.remove('active');
            });
        });

        // Model dropdown items
        document.querySelectorAll('#model-menu .dropdown-item').forEach(item => {
            item.addEventListener('click', () => {
                const value = item.getAttribute('data-value');
                this.state.set('model', value);
                this.modelSelected.textContent = value;
                this.modelMenu.classList.remove('active');
            });
        });

        // Prompt buttons
        document.querySelectorAll('.prompt-button').forEach(btn => {
            btn.addEventListener('click', () => {
                const prompt = btn.getAttribute('data-prompt');
                this.messageInput.value = `Create a ${prompt}`;
                this.messageInput.focus();
                this.updateSubmitButton();
            });
        });

        // Textarea
        this.messageInput.addEventListener('input', () => this.updateSubmitButton());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (!this.submitBtn.disabled) {
                    this.handleSubmit();
                }
            }
        });

        // Submit button
        this.submitBtn.addEventListener('click', () => this.handleSubmit());

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('active'));
            }
        });
    }

    setupStateSubscriptions() {
        this.state.subscribe((key, value) => {
            if (key === 'isStreaming') {
                this.submitBtn.disabled = value || this.messageInput.value.trim().length === 0;
            }
        });
    }

    toggleDropdown(menu) {
        const isActive = menu.classList.contains('active');
        document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('active'));
        if (!isActive) {
            menu.classList.add('active');
        }
    }

    getDisplayName(value) {
        const map = {
            'claudecode': 'Claude Code',
            'qwen': 'Qwen'
        };
        return map[value] || value;
    }

    updateSubmitButton() {
        this.submitBtn.disabled = this.messageInput.value.trim().length === 0 || this.state.get('isStreaming');
    }

    async handleSubmit() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        const mode = this.state.get('mode');
        const model = this.state.get('model');

        this.state.set('isStreaming', true);
        this.showResponse();
        this.clearResponseContent();

        try {
            await this.api.sendMessage(message, mode, model, (chunk) => {
                this.appendToResponse(chunk);
            });
        } catch (error) {
            this.appendToResponse(`\n\nError: ${error.message}`);
            console.error('Error:', error);
        } finally {
            this.state.set('isStreaming', false);
        }

        // Clear form
        this.messageInput.value = '';
        this.fileInput.value = '';
        this.state.set('files', []);
        this.updateSubmitButton();
    }

    showResponse() {
        this.responseContainer.classList.add('visible');
    }

    clearResponseContent() {
        this.responseContent.textContent = '';
    }

    appendToResponse(text) {
        this.responseContent.textContent += text;
        this.responseContainer.scrollTop = this.responseContainer.scrollHeight;
    }
}

export default UIController;
