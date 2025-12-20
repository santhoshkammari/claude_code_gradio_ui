// API communication module
class ClaudeAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    async sendMessage(message, option1, option2, onChunk) {
        const response = await fetch(`${this.baseURL}/claude`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                option1: option1,
                option2: option2
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

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
                        return;
                    }
                    if (onChunk) {
                        onChunk(data);
                    }
                }
            }
        }
    }
}

export default ClaudeAPI;
