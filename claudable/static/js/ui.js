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
        this.subtitle = document.getElementById('subtitle');
    }
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
                this.updateSubtitle(value);
                this.modeMenu.classList.remove('active');
            });
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
            'code': 'Code',
            'scout': 'Scout',
            'citeria': 'Citeria'
        };
        return map[value] || value;
    }

    getSubtitle(value) {
        const subtitles = {
            'code': 'Intelligent coding assistant • Write better code • Debug faster',
            'scout': 'Explore your codebase • Discover insights • Navigate effortlessly',
            'citeria': 'Strategic code analysis • Quality standards • Smart evaluation'
        };
        return subtitles[value] || subtitles['code'];
    }

    updateSubtitle(value) {
        if (this.subtitle) {
            this.subtitle.textContent = this.getSubtitle(value);
        }
    }
    }

    getSubtitle(value) {
        const subtitles = {
            'code': 'Intelligent coding assistant • Write better code • Debug faster',
            'scout': 'Explore your codebase • Discover insights • Navigate effortlessly',
            'citeria': 'Strategic code analysis • Quality standards • Smart evaluation'
        };
        return subtitles[value] || subtitles['code'];
    }

    updateSubtitle(value) {
        if (this.subtitle) {
            this.subtitle.textContent = this.getSubtitle(value);
        }
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

        try {
            // Create a new chat session
            const response = await fetch('/api/chat/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    option1: mode,
                    option2: model
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Redirect to the chat page
            window.location.href = `/chat/${data.chat_uuid}`;
        } catch (error) {
            console.error('Error:', error);
            alert(`Error creating chat: ${error.message}`);
            this.state.set('isStreaming', false);
        }
    }
}

export default UIController;
