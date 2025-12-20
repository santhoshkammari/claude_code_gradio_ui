// State management module
class AppState {
    constructor() {
        this.data = {
            mode: 'claudecode',
            model: 'Claude Sonnet 4.5',
            files: [],
            isStreaming: false
        };
        this.listeners = [];
    }

    get(key) {
        return this.data[key];
    }

    set(key, value) {
        this.data[key] = value;
        this.notify(key, value);
    }

    subscribe(callback) {
        this.listeners.push(callback);
    }

    notify(key, value) {
        this.listeners.forEach(callback => callback(key, value));
    }

    reset() {
        this.data.files = [];
        this.data.isStreaming = false;
        this.notify('files', []);
        this.notify('isStreaming', false);
    }
}

export default AppState;
