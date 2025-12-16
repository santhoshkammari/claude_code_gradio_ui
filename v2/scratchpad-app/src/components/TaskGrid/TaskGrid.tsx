import './TaskGrid.css'
import type { Task } from '../../types'

interface TaskGridProps {
  tasks: Task[]
  selectedTask: Task | null
  taskFilter: 'all' | 'pending' | 'in_progress' | 'completed'
  onTaskClick: (task: Task) => void
  onDeleteTask: (id: string) => void
  onStartTask: (taskId: string, model: string) => void
  onUpdateTaskModel: (taskId: string, model: string) => void
  onNewTask: () => void
  onFilterChange: (filter: 'all' | 'pending' | 'in_progress' | 'completed') => void
  API_URL: string
}

const truncateText = (text: string, maxLength: number = 120) => {
  if (!text) return '';
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
};

export default function TaskGrid({
  tasks,
  selectedTask,
  taskFilter,
  onTaskClick,
  onDeleteTask,
  onStartTask,
  onUpdateTaskModel,
  onNewTask,
  onFilterChange,
  API_URL
}: TaskGridProps) {
  const filteredTasks = tasks.filter(task => taskFilter === 'all' || task.status === taskFilter)

  return (
    <>
      <header className="main-header glass">
        <div className="header-title">Tasks</div>
        <div className="task-filters">
          <button className={`filter-btn ${taskFilter === 'all' ? 'active' : ''}`} onClick={() => onFilterChange('all')}>All</button>
          <button className={`filter-btn ${taskFilter === 'pending' ? 'active' : ''}`} onClick={() => onFilterChange('pending')}>Pending</button>
          <button className={`filter-btn ${taskFilter === 'in_progress' ? 'active' : ''}`} onClick={() => onFilterChange('in_progress')}>Running</button>
          <button className={`filter-btn ${taskFilter === 'completed' ? 'active' : ''}`} onClick={() => onFilterChange('completed')}>Completed</button>
        </div>
        <button className="new-task-btn" onClick={onNewTask}>+ New Task</button>
      </header>

      <div className="tasks-grid">
        {filteredTasks.map(task => (
          <div
            key={task.id}
            className={`task-card glass ${selectedTask?.id === task.id ? 'selected' : ''}`}
            onClick={() => onTaskClick(task)}
          >
            <div className="task-header">
              <div className="task-priority" data-priority={task.priority}></div>
              <div className="task-title">{task.title}</div>
              <div className={`task-status-badge status-${task.status}`}>
                {task.status === 'in_progress' ? '⚡' : task.status === 'completed' ? '✓' : task.status === 'failed' ? '✗' : '○'}
              </div>
            </div>
            {task.content && <div className="task-content">{truncateText(task.content)}</div>}
            {task.folder_path && <div className="task-folder">📁 {task.folder_path}</div>}
            {task.model && (
              <div className="task-model-badge">
                <span className="model-label">Agent:</span>
                <span className="model-name">{task.model}</span>
              </div>
            )}
            <div className="task-footer">
              <div className="task-date">{new Date(task.created_at).toLocaleDateString()}</div>
              <div className="task-footer-actions">
                <button className="task-delete-btn" onClick={(e) => { e.stopPropagation(); onDeleteTask(task.id) }}>Delete</button>
                {task.status === 'pending' && (
                  <div className="unified-start-btn-wrapper">
                    <button
                      className="unified-start-btn"
                      onClick={(e) => { e.stopPropagation(); onStartTask(task.id, task.model || 'sonnet'); }}
                    >
                      <span className="start-text">Start</span>
                      <span className="start-divider"></span>
                      <select
                        className="start-dropdown-trigger"
                        onClick={(e) => e.stopPropagation()}
                        onChange={async (e) => {
                          e.stopPropagation();
                          if(e.target.value) {
                            try {
                              await fetch(`${API_URL}/tasks/${task.id}`, {
                                method: 'PUT',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ model: e.target.value })
                              });
                              onUpdateTaskModel(task.id, e.target.value);
                            } catch (err) {
                              console.error('Failed to update task model:', err);
                            }
                            onStartTask(task.id, e.target.value);
                          }
                        }}
                      >
                        <option value="">▼</option>
                        <option value="sonnet">Sonnet</option>
                        <option value="haiku">Haiku</option>
                        <option value="qwen">Qwen</option>
                      </select>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  )
}
