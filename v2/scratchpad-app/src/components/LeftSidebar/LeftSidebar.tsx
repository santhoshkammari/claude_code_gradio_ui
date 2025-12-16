import './LeftSidebar.css'
import '../shared/ThemeToggle.css'
import type { Session, Task } from '../../types'
import ThemeToggle from '../shared/ThemeToggle'
import { useState } from 'react'

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
  onNewSession: () => void
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
  onNewSession,
  onToggleSession
}: LeftSidebarProps) {
  const [openMenuTaskId, setOpenMenuTaskId] = useState<string | null>(null);

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
                >
                  <div className="session-header">
                    <div className="session-icon">🔬</div>
                    <div className="session-info">
                      <div className="session-title">{session.title}</div>
                      <div className="session-date">{new Date(session.updated_at).toLocaleDateString()}</div>
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
        <button className="new-session-btn" onClick={onNewSession}>+ New Session</button>
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
