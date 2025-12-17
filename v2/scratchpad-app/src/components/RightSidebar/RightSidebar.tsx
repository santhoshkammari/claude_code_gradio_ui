import { useState, useEffect, useRef } from 'react'
import './RightSidebar.css'

interface FileDiff {
  path: string
  additions: number
  deletions: number
  diff: string
}

interface RightSidebarProps {
  gitDiff: string
  onClose: () => void
}

export default function RightSidebar({
  gitDiff,
  onClose
}: RightSidebarProps) {
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set())
  const [parsedFiles, setParsedFiles] = useState<FileDiff[]>([])
  const hasInitialized = useRef(false)

  const parseGitDiff = (diff: string): FileDiff[] => {
    const files: FileDiff[] = []
    const diffBlocks = diff.split('diff --git')

    for (let i = 1; i < diffBlocks.length; i++) {
      const block = diffBlocks[i]
      const lines = block.split('\n')

      // Extract filename from "a/path b/path"
      const fileMatch = lines[0].match(/a\/(.*?) b\/(.*)$/)
      if (!fileMatch) continue

      const filename = fileMatch[2]

      // Count additions and deletions
      let additions = 0
      let deletions = 0
      let diffContent = ''

      for (const line of lines) {
        if (line.startsWith('+') && !line.startsWith('+++')) additions++
        if (line.startsWith('-') && !line.startsWith('---')) deletions++
        diffContent += line + '\n'
      }

      files.push({
        path: filename,
        additions,
        deletions,
        diff: diffContent.trim()
      })
    }

    return files
  }

  useEffect(() => {
    if (gitDiff) {
      const files = parseGitDiff(gitDiff)
      setParsedFiles(files)

      // Only expand the first file on initial load or when gitDiff changes significantly
      if (!hasInitialized.current && files.length > 0) {
        setExpandedFiles(prev => {
          hasInitialized.current = true;
          return new Set([...prev, files[0].path]);
        });
      }
    } else {
      setParsedFiles([])
      setExpandedFiles(() => {
        hasInitialized.current = false;
        return new Set();
      })
    }
  }, [gitDiff])

  const toggleFileExpand = (path: string) => {
    setExpandedFiles(prev => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }

  return (
    <aside className="right-sidebar">
      <div className="sidebar-header">
        <h3>Git Changes</h3>
        <button className="close-button" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="files-diff-section">
        {parsedFiles.length === 0 ? (
          <div className="empty-state">No changes detected</div>
        ) : (
          parsedFiles.map((file) => {
            const isExpanded = expandedFiles.has(file.path)

            return (
              <div key={file.path} className="file-diff-item">
                <div
                  className="file-diff-header"
                  onClick={() => toggleFileExpand(file.path)}
                >
                  <span className="expand-icon">
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <span className="file-path">{file.path}</span>
                  <div className="file-stats">
                    <span className="additions">+{file.additions}</span>
                    <span className="deletions">-{file.deletions}</span>
                  </div>
                </div>

                {isExpanded && (
                  <pre className="file-diff-content">
                    <code>{file.diff}</code>
                  </pre>
                )}
              </div>
            )
          })
        )}
      </div>
    </aside>
  )
}
