import './RightSidebar.css'
import type { FileChange } from '../../types'

interface RightSidebarProps {
  selectedTask: any
  fileChanges: FileChange[]
  gitDiff: string
  activityLog: any[]
  onClose: () => void
  activityEndRef: React.RefObject<HTMLDivElement | null>
}

export default function RightSidebar({
  selectedTask,
  fileChanges,
  gitDiff,
  activityLog,
  onClose,
  activityEndRef
}: RightSidebarProps) {
  return (
    <aside className="right-sidebar glass">
      <div className="files-header">
        <div className="files-title">Activity & Files</div>
        <button className="close-sidebar-btn" onClick={onClose}>×</button>
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
  )
}
