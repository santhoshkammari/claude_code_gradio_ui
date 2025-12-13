import { useState, useEffect, useRef } from 'react'
import './App.css'
import type { Session, Task, FileChange } from './types'

const API_URL = 'http://localhost:3001/api'

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [showChat, setShowChat] = useState(false)
  const [activityLog, setActivityLog] = useState<any[]>([])
  const [chatMessages, setChatMessages] = useState<any[]>([])
  const [fileChanges, setFileChanges] = useState<FileChange[]>([])
  const [gitDiff, setGitDiff] = useState<string>('')
  const [taskFilter, setTaskFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const [newTaskFolder, setNewTaskFolder] = useState('')
  const [folderSuggestions, setFolderSuggestions] = useState<string[]>([])
  const [chatInput, setChatInput] = useState('')
  const [selectedModel, setSelectedModel] = useState('sonnet')
  const activityEndRef = useRef<HTMLDivElement>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const prevActivityLengthRef = useRef(0)

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
      fetchFileChanges(selectedTask.id)
    }
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [selectedTask])

  useEffect(() => {
    if (activityLog.length > prevActivityLengthRef.current && activityLog.length > 0 && showChat) {
      activityEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
    prevActivityLengthRef.current = activityLog.length
  }, [activityLog, showChat])

  useEffect(() => {
    if (chatMessages.length > 0 && showChat) {
      setTimeout(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }, 100)
    }
  }, [chatMessages, showChat])

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

  const fetchFileChanges = async (taskId: string) => {
    try {
      const res = await fetch(`${API_URL}/tasks/${taskId}/files`)
      const data = await res.json()
      setFileChanges(data.files || [])
      setGitDiff(data.diff || '')
    } catch (err) {
      console.error('Failed to fetch file changes:', err)
    }
  }

  const searchFolders = async (query: string) => {
    if (!query || query.length < 2) {
      setFolderSuggestions([])
      return
    }
    try {
      const res = await fetch(`${API_URL}/folders/search?q=${encodeURIComponent(query)}`)
      const data = await res.json()
      setFolderSuggestions(data)
    } catch (err) {
      console.error('Folder search error:', err)
    }
  }

  const connectToTaskStream = (taskId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    setActivityLog([])
    setChatMessages([])
    prevActivityLengthRef.current = 0

    const eventSource = new EventSource(`${API_URL}/tasks/${taskId}/stream`)
    eventSourceRef.current = eventSource

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setActivityLog(prev => [...prev, data])

      if (data.type === 'message') {
        setChatMessages(prev => [...prev, data])
      }

      if (data.type === 'task_status') {
        setTasks(prev => prev.map(t =>
          t.id === taskId ? { ...t, status: data.status } : t
        ))
        if (data.status === 'completed' || data.status === 'failed') {
          eventSource.close()
          eventSourceRef.current = null
          fetchFileChanges(taskId)
        }
      }
    }

    eventSource.onerror = () => {
      eventSource.close()
      eventSourceRef.current = null
    }
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
    if (!newTaskTitle.trim() || !newTaskDescription.trim()) return

    let session = currentSession
    if (!session) {
      const id = Date.now().toString()
      const title = 'Default Session'
      const res = await fetch(`${API_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, title })
      })
      session = await res.json()
      setSessions([session])
      setCurrentSession(session)
    }

    const id = Date.now().toString()
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id,
        session_id: session.id,
        title: newTaskTitle,
        content: newTaskDescription,
        status: 'pending',
        priority: 'medium',
        folder_path: newTaskFolder || null
      })
    })
    const newTask = await res.json()
    setTasks([newTask, ...tasks])
    setShowTaskModal(false)
    setNewTaskTitle('')
    setNewTaskDescription('')
    setNewTaskFolder('')
  }

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task)
    setShowChat(true)
  }

  const handleBackToTasks = () => {
    setShowChat(false)
    setSelectedTask(null)
  }

  const startTask = async (model: string) => {
    if (!selectedTask) return
    try {
      await fetch(`${API_URL}/tasks/${selectedTask.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model })
      })
    } catch (err) {
      console.error('Failed to start task:', err)
    }
  }

  const startTaskFromCard = async (taskId: string, model: string) => {
    try {
      await fetch(`${API_URL}/tasks/${taskId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model })
      })
    } catch (err) {
      console.error('Failed to start task:', err)
    }
  }

  const sendMessage = async () => {
    if (!chatInput.trim() || !selectedTask) return

    const message = { role: 'user', content: chatInput }
    setChatMessages(prev => [...prev, message])
    setChatInput('')

    try {
      await fetch(`${API_URL}/tasks/${selectedTask.id}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: chatInput })
      })
    } catch (err) {
      console.error('Failed to send message:', err)
    }
  }

  const deleteTask = async (id: string) => {
    await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' })
    const updated = tasks.filter(t => t.id !== id)
    setTasks(updated)
    if (selectedTask?.id === id) {
      setSelectedTask(null)
      setShowChat(false)
      setChatMessages([])
      setActivityLog([])
      setFileChanges([])
      setGitDiff('')
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
        {!showChat ? (
          <>
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
                  onClick={() => handleTaskClick(task)}
                >
                  <div className="task-header">
                    <div className="task-priority" data-priority={task.priority}></div>
                    <div className="task-title">{task.title}</div>
                    <div className={`task-status-badge status-${task.status}`}>
                      {task.status === 'in_progress' ? '⚡' : task.status === 'completed' ? '✓' : task.status === 'failed' ? '✗' : '○'}
                    </div>
                  </div>
                  {task.content && <div className="task-content">{task.content}</div>}
                  {task.folder_path && <div className="task-folder">📁 {task.folder_path}</div>}
                  {task.model && <div className="task-model-badge">Agent: {task.model}</div>}
                  <div className="task-footer">
                    <div className="task-date">{new Date(task.created_at).toLocaleDateString()}</div>
                    <div className="task-footer-actions">
                      {task.status === 'pending' && (
                        <div className="start-btn-group">
                          <button className="start-btn" onClick={(e) => { e.stopPropagation(); startTaskFromCard(task.id, 'sonnet'); }}>
                            ▶ Start
                          </button>
                          <select className="model-select" onClick={(e) => e.stopPropagation()} onChange={(e) => { e.stopPropagation(); startTaskFromCard(task.id, e.target.value); }}>
                            <option value="">▼</option>
                            <option value="sonnet">Sonnet</option>
                            <option value="haiku">Haiku</option>
                            <option value="qwen">Qwen</option>
                          </select>
                        </div>
                      )}
                      <button className="task-action-btn" onClick={(e) => { e.stopPropagation(); deleteTask(task.id) }}>🗑️</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            <div className="chat-header glass">
              <div className="chat-header-left">
                <button className="back-btn" onClick={handleBackToTasks}>←</button>
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

              <div className="chat-input-container glass">
                <select
                  className="model-selector"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                >
                  <option value="sonnet">Sonnet 4.5</option>
                  <option value="haiku">Haiku</option>
                  <option value="qwen">Qwen</option>
                </select>
                <input
                  type="text"
                  className="chat-input"
                  placeholder="Message the AI agent..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                />
                <button className="send-btn" onClick={() => sendMessage()}>Send</button>
                {selectedTask?.status === 'pending' && (
                  <button className="start-task-btn" onClick={() => startTask(selectedModel)}>
                    ▶ Start Task
                  </button>
                )}
              </div>
            </div>
          </>
        )}
      </main>

      <aside className="right-sidebar glass">
        <div className="files-header">
          <div className="files-title">Activity & Files</div>
        </div>

        <div className="files-container">
          {selectedTask ? (
            <>
              <div className="files-section">
                <div className="section-header">
                  <span className="section-icon">📁</span>
                  <span className="section-title">Files Changed</span>
                  <span className="section-count">{fileChanges.length}</span>
                </div>
                <div className="files-list">
                  {fileChanges.map((file, idx) => (
                    <div key={idx} className="file-item">
                      <span className={`file-type-icon ${file.type}`}>
                        {file.type === 'added' ? '+' : file.type === 'modified' ? 'M' : '-'}
                      </span>
                      <span className="file-path">{file.path}</span>
                      {(file.additions || file.deletions) && (
                        <span className="file-changes">
                          {file.additions ? <span className="additions">+{file.additions}</span> : null}
                          {file.deletions ? <span className="deletions">-{file.deletions}</span> : null}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {gitDiff && (
                <div className="diff-section">
                  <div className="section-header">
                    <span className="section-icon">🔀</span>
                    <span className="section-title">Git Diff</span>
                  </div>
                  <pre className="diff-content">{gitDiff}</pre>
                </div>
              )}

              <div className="activity-section">
                <div className="section-header">
                  <span className="section-icon">⚡</span>
                  <span className="section-title">Tool Activity</span>
                </div>
                <div className="activity-list">
                  {activityLog.filter(log => log.type === 'tool_use' || log.type === 'tool_result').map((log, idx) => (
                    <div key={idx} className="activity-item-compact">
                      {log.type === 'tool_use' && (
                        <div className="tool-use-compact">
                          <span className="tool-icon">🔧</span>
                          <span className="tool-name">{log.tool}</span>
                        </div>
                      )}
                      {log.type === 'tool_result' && (
                        <div className="tool-result-compact">
                          <span className="result-icon">✓</span>
                          <span className="result-text">Completed</span>
                        </div>
                      )}
                    </div>
                  ))}
                  <div ref={activityEndRef} />
                </div>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <div className="empty-text">Select a task to see file changes and activity</div>
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
                <label>Folder Path (optional)</label>
                <input
                  type="text"
                  placeholder="Start typing to search folders..."
                  value={newTaskFolder}
                  onChange={(e) => {
                    setNewTaskFolder(e.target.value)
                    searchFolders(e.target.value)
                  }}
                  className="form-input"
                />
                {folderSuggestions.length > 0 && (
                  <div className="folder-suggestions">
                    {folderSuggestions.map((folder, idx) => (
                      <div
                        key={idx}
                        className="folder-suggestion-item"
                        onClick={() => {
                          setNewTaskFolder(folder)
                          setFolderSuggestions([])
                        }}
                      >
                        📁 {folder}
                      </div>
                    ))}
                  </div>
                )}
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
              <button className="btn-primary" onClick={handleCreateTask}>Create Task</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
