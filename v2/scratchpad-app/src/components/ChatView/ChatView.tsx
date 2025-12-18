import './ChatView.css'
import type { Task } from '../../types'

interface ChatViewProps {
  selectedTask: Task | null
  chatMessages: any[]
  chatInput: string
  selectedModel: string
  onBackToTasks: () => void
  onChatInputChange: (value: string) => void
  onSendMessage: () => void
  onModelChange: (model: string) => void
  onStartTask: (model: string) => void
  chatEndRef: React.RefObject<HTMLDivElement | null>
}

export default function ChatView({
  selectedTask,
  chatMessages,
  chatInput,
  selectedModel,
  onBackToTasks,
  onChatInputChange,
  onSendMessage,
  onModelChange,
  onStartTask,
  chatEndRef
}: ChatViewProps) {
  return (
    <>
      <div className="chat-header glass">
        <div className="chat-header-left">
          <button className="back-btn" onClick={onBackToTasks}>←</button>
          <div className="chat-header-info">
            <div className="chat-header-title">{selectedTask?.title}</div>
            <div className="chat-header-status">
              <span className={`status-indicator status-${selectedTask?.status}`}></span>
              {selectedTask?.status}
            </div>
          </div>
        </div>
        {selectedTask?.folder_path && (
          <div className="chat-header-folder">📁 {selectedTask.folder_path}</div>
        )}
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {chatMessages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <div className="message-avatar">{msg.role === 'assistant' ? '🤖' : '👤'}</div>
              <div className="message-bubble">
                <div className="message-content">{msg.content}</div>
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className="minimal-chat-overlay-task">
          <div className="chat-input-floating">
            <textarea
              className="minimal-textarea"
              placeholder="Message..."
              value={chatInput}
              onChange={(e) => onChatInputChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  onSendMessage()
                }
              }}
              rows={1}
            />

            <div className="input-controls-inline">
              <div className="config-pill-compact" onClick={() => {}}>
                <span className="pill-icon">🤖</span>
                <span className="pill-text">{selectedModel === 'sonnet' ? 'Sonnet 4.5' : selectedModel === 'haiku' ? 'Haiku 4.5' : 'Qwen'}</span>
              </div>

              <div className="config-pill-compact" onClick={() => {}}>
                <span className="pill-icon">⚡</span>
                <span className="pill-text">General</span>
              </div>

              <div className="config-pill-compact" onClick={() => {}}>
                <span className="pill-icon">🛠️</span>
                <span className="pill-text">21 tools</span>
              </div>

              <button
                className="icon-btn icon-btn-compact"
                title="Attach file"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                </svg>
              </button>

              <button
                className="send-btn-minimal"
                onClick={onSendMessage}
                disabled={!chatInput.trim()}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
