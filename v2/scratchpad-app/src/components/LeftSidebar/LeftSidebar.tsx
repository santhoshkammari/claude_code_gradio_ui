import './LeftSidebar.css'
import '../shared/ThemeToggle.css'
import type { Session, Task } from '../../types'
import ThemeToggle from '../shared/ThemeToggle'
import { useState, useRef, useEffect } from 'react'

const API_URL = 'http://localhost:3001/api'

interface LeftSidebarProps {
  sessions: Session[]
  currentSession: Session | null
  tasks: Task[]
  selectedTask: Task | null
  collapsedSessions: Record<string, boolean>
  onSessionClick: (session: Session) => void
  onTaskClick: (task: Task) => void
  onDeleteSession: (id: string) => void
  onDeleteTask: (id: string) => void
  onNewSession: (folderPath?: string) => void
  onToggleSession: (id: string) => void
}

export default function LeftSidebar({
  sessions,
  currentSession,
  tasks,
  selectedTask,
  collapsedSessions,
  onSessionClick,
  onTaskClick,
  onDeleteSession,
  onDeleteTask,
  onNewSession,
  onToggleSession
}: LeftSidebarProps) {
  const [openMenuTaskId, setOpenMenuTaskId] = useState<string | null>(null);
  const [showNewSessionInput, setShowNewSessionInput] = useState(false);
  const [newSessionPath, setNewSessionPath] = useState('');
  const [folderSuggestions, setFolderSuggestions] = useState<string[]>([]);
  const [hoveredSessionId, setHoveredSessionId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const newSessionBtnRef = useRef<HTMLButtonElement>(null);

  const handleMenuToggle = (taskId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setOpenMenuTaskId(openMenuTaskId === taskId ? null : taskId);
  };

  const handleMarkAsDone = (task: Task, e: React.MouseEvent) => {
    e.stopPropagation();
    // Update the task to mark as completed
    fetch(`${API_URL}/tasks/${task.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...task, status: 'completed' })
    }).then(() => {
      // Update local state or trigger a refresh
    }).catch(err => {
      console.error('Failed to update task:', err);
    });
    setOpenMenuTaskId(null);
  };

  const handleDelete = (taskId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    onDeleteTask(taskId);
    setOpenMenuTaskId(null);
  };

  useEffect(() => {
    if (showNewSessionInput && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showNewSessionInput]);

  const searchFolders = async (query: string) => {
    if (!query || query.length < 2) {
      setFolderSuggestions([]);
      return;
    }
    try {
      const res = await fetch(`${API_URL}/folders/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      // Filter out dot folders
      const filtered = data.filter((path: string) => !path.split('/').some((part: string) => part.startsWith('.')));
      setFolderSuggestions(filtered);
    } catch (err) {
      console.error('Folder search error:', err);
    }
  };

  const handleNewSessionInputChange = (value: string) => {
    setNewSessionPath(value);
    searchFolders(value);
  };

  const handleCreateSession = (path?: string) => {
    onNewSession(path || newSessionPath || undefined);
    setShowNewSessionInput(false);
    setNewSessionPath('');
    setFolderSuggestions([]);
  };

  const handleNewSessionKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (folderSuggestions.length > 0) {
        handleCreateSession(folderSuggestions[0]);
      } else {
        handleCreateSession();
      }
    } else if (e.key === 'Escape') {
      setShowNewSessionInput(false);
      setNewSessionPath('');
      setFolderSuggestions([]);
    }
  };

  return (
    <aside className="left-sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <div className="logo-icon">🤖</div>
          <span>Scratchpad AI</span>
        </div>
        <ThemeToggle />
      </div>

      <div className="sessions-section">
        <div className="section-title">Sessions</div>
        <div className="sessions-list">
          {sessions.map(session => {
            const sessionTasks = tasks.filter(task => task.session_id === session.id);
            const isCollapsed = collapsedSessions[session.id] || false;

            return (
              <div key={session.id} className="session-with-tasks">
                <div
                  className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
                  onClick={() => onSessionClick(session)}
                  onMouseEnter={() => setHoveredSessionId(session.id)}
                  onMouseLeave={() => setHoveredSessionId(null)}
                  title={session.folder_path || ''}
                >
                  <div className="session-header">
                    <div className="session-icon">🔬</div>
                    <div className="session-info">
                      <div className="session-title">{session.title}</div>
                      <div className="session-date">{new Date(session.updated_at).toLocaleDateString()}</div>
                      {session.folder_path && hoveredSessionId === session.id && (
                        <div className="session-folder-tooltip">📁 {session.folder_path}</div>
                      )}
                    </div>
                    <div className="session-toggle" onClick={(e) => {
                      e.stopPropagation();
                      onToggleSession(session.id);
                    }}>
                      {isCollapsed ? '▶' : '▼'}
                    </div>
                  </div>
                  <button className="delete-btn-small" onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id)
                  }}>×</button>
                </div>

                {!isCollapsed && sessionTasks.length > 0 && (
                  <div className="session-tasks-list">
                    {sessionTasks.map(task => (
                      <div
                        key={task.id}
                        className={`task-item ${selectedTask?.id === task.id ? 'active' : ''}`}
                        onClick={() => onTaskClick(task)}
                      >
                        <div className="task-icon">⚙️</div>
                        <div className="task-info">
                          <div className="task-title">{task.title}</div>
                          <div
                            className="task-menu-icon"
                            onClick={(e) => handleMenuToggle(task.id, e)}
                          >
                            ⋯
                          </div>
                        </div>

                        {openMenuTaskId === task.id && (
                          <div className="task-dropdown-menu">
                            <button className="dropdown-item" onClick={(e) => { e.stopPropagation(); setOpenMenuTaskId(null); /* Add share functionality */ }}>
                              Share
                            </button>
                            <button className="dropdown-item" onClick={(e) => handleMarkAsDone(task, e)}>
                              Mark as done
                            </button>
                            <button className="dropdown-item" onClick={(e) => handleDelete(task.id, e)}>
                              Delete
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        <div
          className="new-session-container"
          onMouseEnter={() => setShowNewSessionInput(true)}
          onMouseLeave={() => {
            if (!newSessionPath && folderSuggestions.length === 0) {
              setShowNewSessionInput(false);
            }
          }}
        >
          {showNewSessionInput && (
            <div className="new-session-input-wrapper">
              {folderSuggestions.length > 0 && (
                <div className="folder-suggestions">
                  {folderSuggestions.slice(0, 5).map((path, idx) => (
                    <div
                      key={idx}
                      className="folder-suggestion-item"
                      onClick={() => handleCreateSession(path)}
                    >
                      📁 {path}
                    </div>
                  ))}
                </div>
              )}
              <input
                ref={inputRef}
                type="text"
                className="new-session-input"
                placeholder="Enter folder path..."
                value={newSessionPath}
                onChange={(e) => handleNewSessionInputChange(e.target.value)}
                onKeyDown={handleNewSessionKeyDown}
                onBlur={() => {
                  setTimeout(() => {
                    setShowNewSessionInput(false);
                    setNewSessionPath('');
                    setFolderSuggestions([]);
                  }, 200);
                }}
              />
            </div>
          )}

          <button
            ref={newSessionBtnRef}
            className="new-session-btn"
          >
            + New Session
          </button>
        </div>
      </div>

      <div className="profile-section">
        <div className="profile-card glass">
          <div className="profile-avatar">👤</div>
          <div className="profile-info">
            <div className="profile-name">User</div>
            <div className="profile-status">Active</div>
          </div>
        </div>
      </div>
    </aside>
  )
}
