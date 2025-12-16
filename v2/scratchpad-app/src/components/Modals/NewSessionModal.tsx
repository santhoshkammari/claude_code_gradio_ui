import './Modal.css'

interface NewSessionModalProps {
  isOpen: boolean
  folderPath: string
  suggestions: string[]
  onFolderPathChange: (value: string) => void
  onClose: () => void
  onCreate: () => void
}

export default function NewSessionModal({
  isOpen,
  folderPath,
  suggestions,
  onFolderPathChange,
  onClose,
  onCreate
}: NewSessionModalProps) {
  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal glass" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Session</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>Folder Path (optional)</label>
            <input
              type="text"
              placeholder="Start typing to search folders..."
              value={folderPath}
              onChange={(e) => onFolderPathChange(e.target.value)}
              className="form-input"
            />
            {suggestions.length > 0 && (
              <div className="folder-suggestions">
                {suggestions.map((folder, idx) => (
                  <div
                    key={idx}
                    className="folder-suggestion-item"
                    onClick={() => {
                      onFolderPathChange(folder)
                    }}
                  >
                    📁 {folder}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={onCreate}>Create Session</button>
        </div>
      </div>
    </div>
  )
}
