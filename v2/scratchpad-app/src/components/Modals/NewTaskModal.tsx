import './Modal.css'

interface NewTaskModalProps {
  isOpen: boolean
  taskDescription: string
  onDescriptionChange: (value: string) => void
  onClose: () => void
  onCreate: () => void
}

export default function NewTaskModal({
  isOpen,
  taskDescription,
  onDescriptionChange,
  onClose,
  onCreate
}: NewTaskModalProps) {
  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal glass" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Task</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>Task Description</label>
            <textarea
              placeholder="Describe what you want the AI to do..."
              value={taskDescription}
              onChange={(e) => onDescriptionChange(e.target.value)}
              className="form-textarea"
              rows={6}
            />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={onCreate}>Create Task</button>
        </div>
      </div>
    </div>
  )
}
