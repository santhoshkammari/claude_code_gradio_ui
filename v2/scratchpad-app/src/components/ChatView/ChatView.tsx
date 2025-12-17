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

        <div className="chat-input-wrapper">
          <div className="input-field-wrapper">
            <textarea
              className="message-input-field"
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
            <div className="input-controls-bottom">
              <div className="model-selector-wrapper">
                <button className="model-selector-btn" onClick={() => {}}>
                  <span className="model-avatar">AI</span>
                  <span className="model-text">{selectedModel === 'sonnet' ? 'Sonnet 4.5' : selectedModel === 'haiku' ? 'Haiku' : 'Qwen'}</span>
                  <span className="model-arrow">▼</span>
                </button>
                <select
                  className="hidden-model-select"
                  value={selectedModel}
                  onChange={(e) => onModelChange(e.target.value)}
                >
                  <option value="sonnet">Sonnet 4.5</option>
                  <option value="haiku">Haiku</option>
                  <option value="qwen">Qwen</option>
                </select>
              </div>

              <div className="action-buttons-row">
                <div className="reason-badge-display">
                  <span className="reason-text">REASON</span>
                  <span className="reason-number">2</span>
                </div>
                <button className="action-icon-btn export-btn" title="Export" onClick={() => {}}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                </button>
                <button className="action-icon-btn send-btn-icon" onClick={() => onSendMessage()} title="Send">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {selectedTask?.status === 'pending' && (
            <button className="start-task-btn" onClick={() => onStartTask(selectedModel)}>
              ▶ Start Task
            </button>
          )}
        </div>
      </div>
    </>
  )
}
