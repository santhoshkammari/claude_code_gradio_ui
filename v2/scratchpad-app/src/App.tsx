import { useState, useEffect, useRef } from 'react'
import './App.css'
import type { Session, Task, Message } from './types'

const API_URL = 'http://localhost:3001/api'

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [activityLog, setActivityLog] = useState<any[]>([])
  const [taskFilter, setTaskFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const activityEndRef = useRef<HTMLDivElement>(null)

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
      connectToTaskStream(selectedTask.id)
    }
  }, [selectedTask])

  useEffect(() => {
    activityEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activityLog])

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

  const connectToTaskStream = (taskId: string) => {
    setActivityLog([])
    const eventSource = new EventSource(`${API_URL}/tasks/${taskId}/stream`)

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setActivityLog(prev => [...prev, data])

      if (data.type === 'task_status') {
        setTasks(prev => prev.map(t =>
          t.id === taskId ? { ...t, status: data.status } : t
        ))
        if (data.status === 'completed' || data.status === 'failed') {
          eventSource.close()
        }
      }
    }

    eventSource.onerror = () => {
      eventSource.close()
    }

    return () => eventSource.close()
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

  const handleCreateTask = async () => {
    if (!currentSession || !newTaskTitle.trim() || !newTaskDescription.trim()) return

    const id = Date.now().toString()
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id,
        session_id: currentSession.id,
        title: newTaskTitle,
        content: newTaskDescription,
        status: 'pending',
        priority: 'medium'
      })
    })
    const newTask = await res.json()
    setTasks([newTask, ...tasks])
    setShowTaskModal(false)
    setNewTaskTitle('')
    setNewTaskDescription('')

    await fetch(`${API_URL}/tasks/${id}/execute`, { method: 'POST' })
    fetchTasks(currentSession.id)
  }

  const deleteTask = async (id: string) => {
    await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' })
    const updated = tasks.filter(t => t.id !== id)
    setTasks(updated)
    if (selectedTask?.id === id) {
      setSelectedTask(null)
      setActivityLog([])
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
            <button className={`filter-btn ${taskFilter === 'in_progress' ? 'active' : ''}`} onClick={() => setTaskFilter('in_progress')}>Running</button>
            <button className={`filter-btn ${taskFilter === 'completed' ? 'active' : ''}`} onClick={() => setTaskFilter('completed')}>Completed</button>
          </div>
          <button className="new-task-btn" onClick={() => setShowTaskModal(true)}>+ New Task</button>
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
                <div className={`task-status-badge status-${task.status}`}>
                  {task.status === 'in_progress' ? '⚡' : task.status === 'completed' ? '✓' : task.status === 'failed' ? '✗' : '○'}
                </div>
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
          <div className="chat-model">{selectedTask ? `Status: ${selectedTask.status}` : 'AI Agent'}</div>
        </div>

        <div className="activity-container">
          {selectedTask ? (
            <>
              {activityLog.map((log, idx) => (
                <div key={idx} className="activity-item">
                  {log.type === 'tool_use' && (
                    <div className="tool-activity">
                      <div className="tool-header">
                        <span className="tool-icon">🔧</span>
                        <span className="tool-name">{log.tool}</span>
                      </div>
                      <div className="tool-input">{JSON.stringify(log.input, null, 2)}</div>
                    </div>
                  )}
                  {log.type === 'tool_result' && (
                    <div className="tool-result">
                      <div className="result-header">
                        <span className="result-icon">✓</span>
                        <span>Result</span>
                      </div>
                      <div className="result-content">{log.content}</div>
                    </div>
                  )}
                  {log.type === 'message' && (
                    <div className={`agent-message ${log.role}`}>
                      <div className="message-role">{log.role === 'assistant' ? '🤖 AI' : '👤 User'}</div>
                      <div className="message-text">{log.content}</div>
                    </div>
                  )}
                  {log.type === 'task_status' && (
                    <div className="status-update">
                      <span className="status-icon">📊</span>
                      <span>Task {log.status}</span>
                    </div>
                  )}
                </div>
              ))}
              <div ref={activityEndRef} />
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <div className="empty-text">Select a task to see AI agent activity</div>
            </div>
          )}
        </div>
      </aside>

      {showTaskModal && (
        <div className="modal-overlay" onClick={() => setShowTaskModal(false)}>
          <div className="modal glass" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Task</h2>
              <button className="modal-close" onClick={() => setShowTaskModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Task Title</label>
                <input
                  type="text"
                  placeholder="e.g., Build authentication system"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>Task Description</label>
                <textarea
                  placeholder="Describe what you want the AI to do..."
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  className="form-textarea"
                  rows={6}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowTaskModal(false)}>Cancel</button>
              <button className="btn-primary" onClick={handleCreateTask}>Create & Start Task</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
