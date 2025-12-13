import { useState, useEffect } from 'react'
import './App.css'
import type { Session, Task, Message } from './types'

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [taskFilter, setTaskFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')

  useEffect(() => {
    const mockSession: Session = {
      id: '1',
      title: 'AI Research Project',
      created_at: Date.now(),
      updated_at: Date.now()
    }
    setSessions([mockSession])
    setCurrentSession(mockSession)

    const mockTasks: Task[] = [
      { id: '1', session_id: '1', title: 'Find top 5 RAG papers', content: 'Research and summarize latest RAG techniques', status: 'completed', priority: 'high', created_at: Date.now() - 86400000, updated_at: Date.now() },
      { id: '2', session_id: '1', title: 'Implement vector database', content: 'Set up ChromaDB for embeddings', status: 'in_progress', priority: 'high', created_at: Date.now() - 43200000, updated_at: Date.now() },
      { id: '3', session_id: '1', title: 'Design UI mockups', content: 'Create glassmorphic design system', status: 'pending', priority: 'medium', created_at: Date.now(), updated_at: Date.now() }
    ]
    setTasks(mockTasks)

    const mockMessages: Message[] = [
      { id: '1', session_id: '1', role: 'user', content: 'Help me find the best RAG papers', created_at: Date.now() - 86400000 },
      { id: '2', session_id: '1', role: 'assistant', content: 'I found 5 excellent RAG papers. Here are the top ones:\n1. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks\n2. Self-RAG: Learning to Retrieve, Generate, and Critique\n3. REPLUG: Retrieval-Augmented Black-Box Language Models', created_at: Date.now() - 86300000 }
    ]
    setMessages(mockMessages)
  }, [])

  const filteredTasks = tasks.filter(task => taskFilter === 'all' || task.status === taskFilter)

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !currentSession) return

    const newMessage: Message = {
      id: Date.now().toString(),
      session_id: currentSession.id,
      role: 'user',
      content: inputMessage,
      created_at: Date.now()
    }
    setMessages([...messages, newMessage])
    setInputMessage('')
  }

  return (
    <div className="app">
      <aside className="left-sidebar glass">
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">✦</div>
            <span>Scratchpad AI</span>
          </div>
        </div>

        <div className="sessions-section">
          <div className="section-title">Sessions</div>
          <div className="sessions-list">
            {sessions.map(session => (
              <div
                key={session.id}
                className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
                onClick={() => setCurrentSession(session)}
              >
                <div className="session-icon">💬</div>
                <div className="session-info">
                  <div className="session-title">{session.title}</div>
                  <div className="session-date">{new Date(session.updated_at).toLocaleDateString()}</div>
                </div>
              </div>
            ))}
          </div>
          <button className="new-session-btn glass-btn">+ New Session</button>
        </div>

        <div className="profile-section">
          <div className="profile-card glass">
            <div className="profile-avatar">U</div>
            <div className="profile-info">
              <div className="profile-name">User</div>
              <div className="profile-status">Active</div>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="main-header glass">
          <div className="header-title">Tasks</div>
          <div className="task-filters">
            <button className={`filter-btn ${taskFilter === 'all' ? 'active' : ''}`} onClick={() => setTaskFilter('all')}>All</button>
            <button className={`filter-btn ${taskFilter === 'pending' ? 'active' : ''}`} onClick={() => setTaskFilter('pending')}>Pending</button>
            <button className={`filter-btn ${taskFilter === 'in_progress' ? 'active' : ''}`} onClick={() => setTaskFilter('in_progress')}>In Progress</button>
            <button className={`filter-btn ${taskFilter === 'completed' ? 'active' : ''}`} onClick={() => setTaskFilter('completed')}>Completed</button>
          </div>
          <button className="new-task-btn">+ New Task</button>
        </header>

        <div className="tasks-grid">
          {filteredTasks.map(task => (
            <div key={task.id} className="task-card glass">
              <div className="task-header">
                <div className="task-priority" data-priority={task.priority}></div>
                <div className="task-title">{task.title}</div>
                <div className={`task-status status-${task.status}`}>
                  {task.status.replace('_', ' ')}
                </div>
              </div>
              {task.content && <div className="task-content">{task.content}</div>}
              <div className="task-footer">
                <div className="task-date">{new Date(task.created_at).toLocaleDateString()}</div>
                <div className="task-actions">
                  <button className="task-action-btn">✏️</button>
                  <button className="task-action-btn">🗑️</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      <aside className="right-sidebar glass">
        <div className="chat-header">
          <div className="chat-title">AI Assistant</div>
          <div className="chat-model">Sonnet 4.5</div>
        </div>

        <div className="messages-container">
          {messages.map(message => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content glass">
                <div className="message-text">{message.content}</div>
                <div className="message-time">
                  {new Date(message.created_at).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="chat-input-container">
          <div className="chat-input glass">
            <input
              type="text"
              placeholder="Ask AI anything..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <div className="input-actions">
              <button className="input-btn">📎</button>
              <button className="input-btn send" onClick={handleSendMessage}>➤</button>
            </div>
          </div>
        </div>
      </aside>
    </div>
  )
}

export default App
