// Chat page controller
class ChatController {
    constructor() {
        this.chatUuid = this.extractChatUuid();
        this.mode = 'code';
        this.model = 'sonnet';
        this.isStreaming = false;
        this.configureMarked();
        this.init();
    }

    configureMarked() {
        // Configure marked.js for GitHub-flavored markdown
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                gfm: true,
                breaks: true,
                headerIds: true,
                mangle: false,
                sanitize: false,
                smartLists: true,
                smartypants: false,
                xhtml: false,
                highlight: function(code, lang) {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {
                            console.error('Highlight error:', err);
                        }
                    }
                    return hljs.highlightAuto(code).value;
                }
            });
        }
    }

    extractChatUuid() {
        const path = window.location.pathname;
        const match = path.match(/\/chat\/([a-f0-9-]+)/);
        return match ? match[1] : null;
    }

    init() {
        this.bindElements();
        this.attachEventListeners();
        this.loadChatMessages();
        this.loadChatList();
        this.setupAutoResize();
    }

    bindElements() {
        // Sidebar
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.sidebarChats = document.getElementById('sidebar-chats');
        this.newChatBtn = document.getElementById('new-chat-btn');

        // Messages
        this.messagesContainer = document.getElementById('messages-container');

        // Input
        this.messageInput = document.getElementById('message-input');
        this.submitBtn = document.getElementById('submit-btn');
        this.uploadBtn = document.getElementById('upload-btn');
        this.fileInput = document.getElementById('file-input');

        // Dropdowns
        this.modeBtn = document.getElementById('mode-btn');
        this.modeMenu = document.getElementById('mode-menu');
        this.modeSelected = document.getElementById('mode-selected');
        this.modelBtn = document.getElementById('model-btn');
        this.modelMenu = document.getElementById('model-menu');
        this.modelSelected = document.getElementById('model-selected');
    }

    attachEventListeners() {
        // Sidebar toggle
        this.sidebarToggle.addEventListener('click', () => {
            this.sidebar.classList.toggle('open');
        });

        // New chat button
        this.newChatBtn.addEventListener('click', () => {
            window.location.href = '/';
        });

        // Upload button
        this.uploadBtn.addEventListener('click', () => {
            this.fileInput.click();
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
                this.mode = value;
                this.modeSelected.textContent = this.getDisplayName(value);
                this.modeMenu.classList.remove('active');
            });
        });

        // Model dropdown items
        document.querySelectorAll('#model-menu .dropdown-item').forEach(item => {
            item.addEventListener('click', () => {
                const value = item.getAttribute('data-value');
                this.model = value;
                this.modelSelected.textContent = value;
                this.modelMenu.classList.remove('active');
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

    setupAutoResize() {
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 200) + 'px';
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

    updateSubmitButton() {
        this.submitBtn.disabled = this.messageInput.value.trim().length === 0 || this.isStreaming;
    }

    async loadChatMessages() {
        try {
            const response = await fetch(`/api/chat/${this.chatUuid}/messages`);
            if (!response.ok) {
                throw new Error('Failed to load messages');
            }

            const data = await response.json();
            this.renderMessages(data.messages);

            // Check if the last message is from user and has no corresponding assistant response yet
            // This happens when a new chat is created and redirected here
            if (data.messages.length > 0) {
                const lastMessage = data.messages[data.messages.length - 1];

                // Only trigger initial response if:
                // 1. Last message is from user
                // 2. No assistant message exists in the entire chat
                // 3. This is likely a new chat (only one message exists, which is the user's)
                const hasResponse = data.messages.some(msg => msg.role === 'assistant');
                const isNewChat = data.messages.length === 1 && lastMessage.role === 'user';

                if (isNewChat && !hasResponse) {
                    console.log('New chat detected - triggering initial response...');
                    // Automatically trigger the response for the first message
                    this.processInitialMessage(lastMessage.content);
                }
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            this.addMessage('assistant', 'Error loading chat history. Please try again.');
        }
    }

    async processInitialMessage(message) {
        // Add typing indicator
        this.addTypingIndicator();
        this.isStreaming = true;
        this.updateSubmitButton();

        try {
            const response = await fetch(`/api/chat/${this.chatUuid}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    option1: this.mode,
                    option2: this.model
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Remove typing indicator
            this.removeTypingIndicator();

            // Create assistant message container
            const assistantContent = this.addMessage('assistant', '', true);

            // Stream the response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            break;
                        }
                        if (data !== '') {
                            // Unescape newlines from SSE format
                            const unescapedData = data.replace(/\\n/g, '\n');
                            // Data already contains the full accumulated buffer from API
                            // Just render it as markdown
                            try {
                                const html = marked.parse(unescapedData);
                                assistantContent.innerHTML = html;
                                assistantContent.querySelectorAll('pre code').forEach((block) => {
                                    hljs.highlightElement(block);
                                });
                            } catch (err) {
                                // If parsing fails, show as plain text
                                assistantContent.textContent = unescapedData;
                            }
                            this.scrollToBottom();
                        }
                    }
                }
            }

        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('assistant', `Error: ${error.message}`);
            console.error('Error:', error);
        } finally {
            this.isStreaming = false;
            this.updateSubmitButton();
        }
    }

    async loadChatList() {
        try {
            const response = await fetch('/api/chats');
            if (!response.ok) {
                throw new Error('Failed to load chats');
            }

            const data = await response.json();
            this.renderChatList(data.chats);
        } catch (error) {
            console.error('Error loading chats:', error);
        }
    }

    renderChatList(chats) {
        this.sidebarChats.innerHTML = '';

        chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = 'chat-item';
            if (chat.uuid === this.chatUuid) {
                chatItem.classList.add('active');
            }

            const title = document.createElement('div');
            title.className = 'chat-item-title';
            title.textContent = chat.title || 'New Chat';

            const date = document.createElement('div');
            date.className = 'chat-item-date';
            date.textContent = this.formatDate(chat.updated_at);

            chatItem.appendChild(title);
            chatItem.appendChild(date);

            chatItem.addEventListener('click', () => {
                window.location.href = `/chat/${chat.uuid}`;
            });

            this.sidebarChats.appendChild(chatItem);
        });
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            return 'Today';
        } else if (days === 1) {
            return 'Yesterday';
        } else if (days < 7) {
            return `${days} days ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    renderMessages(messages) {
        this.messagesContainer.innerHTML = '';
        messages.forEach(msg => {
            this.addMessage(msg.role, msg.content, false);
        });
        this.scrollToBottom();
    }

    addMessage(role, content, shouldScroll = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content markdown-body';

        // For assistant messages, render as markdown
        if (role === 'assistant' && content) {
            try {
                contentDiv.innerHTML = marked.parse(content);
                // Apply syntax highlighting to code blocks
                contentDiv.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            } catch (err) {
                console.error('Markdown parse error:', err);
                const p = document.createElement('p');
                p.textContent = content;
                contentDiv.appendChild(p);
            }
        } else {
            // For user messages, use plain text
            const p = document.createElement('p');
            p.textContent = content;
            contentDiv.appendChild(p);
        }

        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);

        if (shouldScroll) {
            this.scrollToBottom();
        }

        return contentDiv;
    }

    addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message message-assistant';
        messageDiv.id = 'typing-indicator';

        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';

        messageDiv.appendChild(indicator);
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    async handleSubmit() {
        const message = this.messageInput.value.trim();
        if (!message || this.isStreaming) return;

        // Add user message to UI
        this.addMessage('user', message);

        // Clear input
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        this.updateSubmitButton();

        // Set streaming state
        this.isStreaming = true;
        this.updateSubmitButton();

        // Add typing indicator
        this.addTypingIndicator();

        try {
            const response = await fetch(`/api/chat/${this.chatUuid}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    option1: this.mode,
                    option2: this.model
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Remove typing indicator
            this.removeTypingIndicator();

            // Create assistant message container
            const assistantContent = this.addMessage('assistant', '', true);

            // Stream the response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            break;
                        }
                        if (data !== '') {
                            // Unescape newlines from SSE format
                            const unescapedData = data.replace(/\\n/g, '\n');
                            // Data already contains the full accumulated buffer from API
                            // Just render it as markdown
                            try {
                                const html = marked.parse(unescapedData);
                                assistantContent.innerHTML = html;
                                assistantContent.querySelectorAll('pre code').forEach((block) => {
                                    hljs.highlightElement(block);
                                });
                            } catch (err) {
                                // If parsing fails, show as plain text
                                assistantContent.textContent = unescapedData;
                            }
                            this.scrollToBottom();
                        }
                    }
                }
            }

        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('assistant', `Error: ${error.message}`);
            console.error('Error:', error);
        } finally {
            this.isStreaming = false;
            this.updateSubmitButton();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatController();
});
