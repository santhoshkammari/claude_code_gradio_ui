import { useState, useEffect } from 'react'
import './App.css'
import type { Session, Task, Message } from './types'

const API_URL = 'http://localhost:3001/api'

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [taskFilter, setTaskFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')
  const [isLoadingAI, setIsLoadingAI] = useState(false)

  useEffect(() => {
    fetchSessions()
  }, [])

  useEffect(() => {
    if (currentSession) {
      fetchTasks(currentSession.id)
    }
  }, [currentSession])

  useEffect(() => {
    if (selectedTask) {
      fetchMessages(selectedTask.id)
    }
  }, [selectedTask])

  const fetchSessions = async () => {
    const res = await fetch(`${API_URL}/sessions`)
    const data = await res.json()
    setSessions(data)
    if (data.length > 0 && !currentSession) {
      setCurrentSession(data[0])
    }
  }

  const fetchTasks = async (sessionId: string) => {
    const res = await fetch(`${API_URL}/sessions/${sessionId}/tasks`)
    const data = await res.json()
    setTasks(data)
  }

  const fetchMessages = async (taskId: string) => {
    const res = await fetch(`${API_URL}/tasks/${taskId}/messages`)
    const data = await res.json()
    setMessages(data)
  }

  const createSession = async () => {
    const id = Date.now().toString()
    const title = `Session ${sessions.length + 1}`
    const res = await fetch(`${API_URL}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, title })
    })
    const newSession = await res.json()
    setSessions([newSession, ...sessions])
    setCurrentSession(newSession)
  }

  const deleteSession = async (id: string) => {
    await fetch(`${API_URL}/sessions/${id}`, { method: 'DELETE' })
    const updated = sessions.filter(s => s.id !== id)
    setSessions(updated)
    if (currentSession?.id === id) {
      setCurrentSession(updated[0] || null)
    }
  }

  const createTask = async () => {
    if (!currentSession) return

    const id = Date.now().toString()
    const title = `Task ${tasks.length + 1}`
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id,
        session_id: currentSession.id,
        title,
        content: '',
        status: 'pending',
        priority: 'medium'
      })
    })
    const newTask = await res.json()
    setTasks([newTask, ...tasks])
  }

  const deleteTask = async (id: string) => {
    await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' })
    const updated = tasks.filter(t => t.id !== id)
    setTasks(updated)
    if (selectedTask?.id === id) {
      setSelectedTask(null)
      setMessages([])
    }
  }

  const updateTaskStatus = async (id: string, status: Task['status']) => {
    const task = tasks.find(t => t.id === id)
    if (!task) return

    await fetch(`${API_URL}/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...task,
        status,
        updated_at: Date.now()
      })
    })

    setTasks(tasks.map(t => t.id === id ? { ...t, status } : t))
    if (selectedTask?.id === id) {
      setSelectedTask({ ...selectedTask, status })
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedTask) return

    setIsLoadingAI(true)
    setInputMessage('')

    const userMsg: Message = {
      id: `${Date.now()}-user`,
      task_id: selectedTask.id,
      role: 'user',
      content: inputMessage,
      created_at: Date.now()
    }
    setMessages([...messages, userMsg])

    try {
      const response = await fetch(`${API_URL}/tasks/${selectedTask.id}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage })
      })

      const reader = response.body?.getReader()
      if (!reader) return

      let aiResponse = ''
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'chunk') {
              aiResponse += data.content
            } else if (data.type === 'done') {
              const assistantMsg: Message = {
                id: `${Date.now()}-assistant`,
                task_id: selectedTask.id,
                role: 'assistant',
                content: data.content,
                created_at: Date.now()
              }
              setMessages(prev => [...prev, assistantMsg])
            }
          }
        }
      }
    } catch (error) {
      console.error('AI error:', error)
    } finally {
      setIsLoadingAI(false)
    }
  }

  const filteredTasks = tasks.filter(task => taskFilter === 'all' || task.status === taskFilter)

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
              >
                <div onClick={() => setCurrentSession(session)}>
                  <div className="session-icon">💬</div>
                  <div className="session-info">
                    <div className="session-title">{session.title}</div>
                    <div className="session-date">{new Date(session.updated_at).toLocaleDateString()}</div>
                  </div>
                </div>
                <button className="delete-btn-small" onClick={() => deleteSession(session.id)}>×</button>
              </div>
            ))}
          </div>
          <button className="new-session-btn glass-btn" onClick={createSession}>+ New Session</button>
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
          <button className="new-task-btn" onClick={createTask}>+ New Task</button>
        </header>

        <div className="tasks-grid">
          {filteredTasks.map(task => (
            <div
              key={task.id}
              className={`task-card glass ${selectedTask?.id === task.id ? 'selected' : ''}`}
              onClick={() => setSelectedTask(task)}
            >
              <div className="task-header">
                <div className="task-priority" data-priority={task.priority}></div>
                <div className="task-title">{task.title}</div>
                <select
                  className={`task-status-select status-${task.status}`}
                  value={task.status}
                  onChange={(e) => {
                    e.stopPropagation()
                    updateTaskStatus(task.id, e.target.value as Task['status'])
                  }}
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              {task.content && <div className="task-content">{task.content}</div>}
              <div className="task-footer">
                <div className="task-date">{new Date(task.created_at).toLocaleDateString()}</div>
                <button className="task-action-btn" onClick={(e) => { e.stopPropagation(); deleteTask(task.id) }}>🗑️</button>
              </div>
            </div>
          ))}
        </div>
      </main>

      <aside className="right-sidebar glass">
        <div className="chat-header">
          <div className="chat-title">{selectedTask ? selectedTask.title : 'Select a task'}</div>
          <div className="chat-model">Sonnet 4.5</div>
        </div>

        <div className="messages-container">
          {selectedTask ? (
            messages.map(message => (
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
            ))
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <div className="empty-text">Select a task to start chatting with AI</div>
            </div>
          )}
          {isLoadingAI && (
            <div className="loading-indicator">
              <div className="loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
        </div>

        {selectedTask && (
          <div className="chat-input-container">
            <div className="chat-input glass">
              <input
                type="text"
                placeholder="Ask AI about this task..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isLoadingAI && handleSendMessage()}
                disabled={isLoadingAI}
              />
              <div className="input-actions">
                <button className="input-btn">📎</button>
                <button
                  className="input-btn send"
                  onClick={handleSendMessage}
                  disabled={isLoadingAI}
                >
                  ➤
                </button>
              </div>
            </div>
          </div>
        )}
      </aside>
    </div>
  )
}

export default App
