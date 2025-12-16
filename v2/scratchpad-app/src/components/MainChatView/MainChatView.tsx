import { useState, useRef, useEffect } from 'react'
import './MainChatView.css'

interface Tool {
  id: string
  name: string
  category: string
}

interface Agent {
  id: string
  name: string
  tools: string[]
}

interface MainChatViewProps {
  onSubmitMessage: (message: string, config: ChatConfig) => void
}

interface ChatConfig {
  model: string
  agent: string
  tools: string[]
  files?: File[]
}

const AVAILABLE_TOOLS: Tool[] = [
  { id: 'Task', name: 'Task', category: 'Agent' },
  { id: 'TaskOutput', name: 'TaskOutput', category: 'Agent' },
  { id: 'Skill', name: 'Skill', category: 'Agent' },
  { id: 'EnterPlanMode', name: 'EnterPlanMode', category: 'Agent' },
  { id: 'ExitPlanMode', name: 'ExitPlanMode', category: 'Agent' },
  { id: 'AskUserQuestion', name: 'AskUserQuestion', category: 'Agent' },
  { id: 'SlashCommand', name: 'SlashCommand', category: 'Agent' },
  { id: 'Bash', name: 'Bash', category: 'Command' },
  { id: 'BashOutput', name: 'BashOutput', category: 'Command' },
  { id: 'KillBash', name: 'KillBash', category: 'Command' },
  { id: 'Read', name: 'Read', category: 'FileSystem' },
  { id: 'Write', name: 'Write', category: 'FileSystem' },
  { id: 'Edit', name: 'Edit', category: 'FileSystem' },
  { id: 'Glob', name: 'Glob', category: 'FileSystem' },
  { id: 'Grep', name: 'Grep', category: 'FileSystem' },
  { id: 'NotebookEdit', name: 'NotebookEdit', category: 'Notebook' },
  { id: 'WebFetch', name: 'WebFetch', category: 'Web' },
  { id: 'WebSearch', name: 'WebSearch', category: 'Web' },
  { id: 'TodoWrite', name: 'TodoWrite', category: 'Todo' },
  { id: 'ListMcpResources', name: 'ListMcpResources', category: 'MCP' },
  { id: 'ReadMcpResource', name: 'ReadMcpResource', category: 'MCP' },
]

const PREDEFINED_AGENTS: Agent[] = [
  { id: 'general', name: 'General', tools: AVAILABLE_TOOLS.map(t => t.id) },
  { id: 'coder', name: 'Coder', tools: ['Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash', 'TodoWrite'] },
  { id: 'researcher', name: 'Researcher', tools: ['WebFetch', 'WebSearch', 'Read', 'Grep', 'Glob', 'TodoWrite'] },
  { id: 'planner', name: 'Planner', tools: ['Task', 'TaskOutput', 'EnterPlanMode', 'ExitPlanMode', 'TodoWrite', 'AskUserQuestion', 'Read', 'Glob', 'Grep'] },
  { id: 'executor', name: 'Executor', tools: ['Bash', 'BashOutput', 'KillBash', 'Read', 'Write', 'Edit', 'TodoWrite'] },
  { id: 'analyst', name: 'Analyst', tools: ['NotebookEdit', 'Read', 'Write', 'Bash', 'Glob', 'Grep', 'TodoWrite'] }
]

export default function MainChatView({ onSubmitMessage }: MainChatViewProps) {
  const [message, setMessage] = useState('')
  const [selectedModel, setSelectedModel] = useState('haiku')
  const [selectedAgent, setSelectedAgent] = useState('general')
  const [selectedTools, setSelectedTools] = useState<string[]>(PREDEFINED_AGENTS[0].tools)
  const [showModelDropdown, setShowModelDropdown] = useState(false)
  const [showAgentDropdown, setShowAgentDropdown] = useState(false)
  const [showToolsDropdown, setShowToolsDropdown] = useState(false)
  const [attachedFiles, setAttachedFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const modelDropdownRef = useRef<HTMLDivElement>(null)
  const agentDropdownRef = useRef<HTMLDivElement>(null)
  const toolsDropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modelDropdownRef.current && !modelDropdownRef.current.contains(event.target as Node)) {
        setShowModelDropdown(false)
      }
      if (agentDropdownRef.current && !agentDropdownRef.current.contains(event.target as Node)) {
        setShowAgentDropdown(false)
      }
      if (toolsDropdownRef.current && !toolsDropdownRef.current.contains(event.target as Node)) {
        setShowToolsDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleAgentChange = (agentId: string) => {
    setSelectedAgent(agentId)
    const agent = PREDEFINED_AGENTS.find(a => a.id === agentId)
    if (agent) {
      setSelectedTools(agent.tools)
    }
    setShowAgentDropdown(false)
  }

  const handleToolToggle = (toolId: string) => {
    setSelectedTools(prev =>
      prev.includes(toolId)
        ? prev.filter(t => t !== toolId)
        : [...prev, toolId]
    )
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAttachedFiles(prev => [...prev, ...Array.from(e.target.files!)])
    }
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items
    if (items) {
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile()
          if (file) {
            setAttachedFiles(prev => [...prev, file])
          }
        }
      }
    }
  }

  const handleRemoveFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = () => {
    if (!message.trim() && attachedFiles.length === 0) return

    onSubmitMessage(message, {
      model: selectedModel,
      agent: selectedAgent,
      tools: selectedTools,
      files: attachedFiles.length > 0 ? attachedFiles : undefined
    })

    setMessage('')
    setAttachedFiles([])
  }

  const getToolsByCategory = (category: string) => {
    return AVAILABLE_TOOLS.filter(t => t.category === category)
  }

  const categories = ['Agent', 'Command', 'FileSystem', 'Notebook', 'Web', 'Todo', 'MCP']
  const currentAgent = PREDEFINED_AGENTS.find(a => a.id === selectedAgent)
  const modelDisplayName = selectedModel === 'sonnet' ? 'Sonnet 4.5' : selectedModel === 'haiku' ? 'Haiku 4.5' : 'Qwen'

  return (
    <div className="minimal-chat-overlay">
      <div className="chat-input-floating">
        <div className="input-top-bar">
          <div className="config-pills">
            <div className="pill-wrapper" ref={modelDropdownRef}>
              <button
                className="config-pill"
                onClick={() => setShowModelDropdown(!showModelDropdown)}
              >
                <span className="pill-icon">🤖</span>
                <span className="pill-text">{modelDisplayName}</span>
                <span className="pill-arrow">▼</span>
              </button>
              {showModelDropdown && (
                <div className="minimal-dropdown">
                  <div
                    className={`dropdown-item ${selectedModel === 'haiku' ? 'active' : ''}`}
                    onClick={() => { setSelectedModel('haiku'); setShowModelDropdown(false) }}
                  >
                    Haiku 4.5
                  </div>
                  <div
                    className={`dropdown-item ${selectedModel === 'sonnet' ? 'active' : ''}`}
                    onClick={() => { setSelectedModel('sonnet'); setShowModelDropdown(false) }}
                  >
                    Sonnet 4.5
                  </div>
                  <div
                    className={`dropdown-item ${selectedModel === 'qwen' ? 'active' : ''}`}
                    onClick={() => { setSelectedModel('qwen'); setShowModelDropdown(false) }}
                  >
                    Qwen
                  </div>
                </div>
              )}
            </div>

            <div className="pill-wrapper" ref={agentDropdownRef}>
              <button
                className="config-pill"
                onClick={() => setShowAgentDropdown(!showAgentDropdown)}
              >
                <span className="pill-icon">⚡</span>
                <span className="pill-text">{currentAgent?.name}</span>
                <span className="pill-arrow">▼</span>
              </button>
              {showAgentDropdown && (
                <div className="minimal-dropdown">
                  {PREDEFINED_AGENTS.map(agent => (
                    <div
                      key={agent.id}
                      className={`dropdown-item ${selectedAgent === agent.id ? 'active' : ''}`}
                      onClick={() => handleAgentChange(agent.id)}
                    >
                      {agent.name}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="pill-wrapper" ref={toolsDropdownRef}>
              <button
                className="config-pill"
                onClick={() => setShowToolsDropdown(!showToolsDropdown)}
              >
                <span className="pill-icon">🛠️</span>
                <span className="pill-text">{selectedTools.length} tools</span>
                <span className="pill-arrow">▼</span>
              </button>
              {showToolsDropdown && (
                <div className="minimal-dropdown tools-dropdown">
                  {categories.map(category => (
                    <div key={category} className="tool-category">
                      <div className="category-name">{category}</div>
                      {getToolsByCategory(category).map(tool => (
                        <label key={tool.id} className="tool-checkbox">
                          <input
                            type="checkbox"
                            checked={selectedTools.includes(tool.id)}
                            onChange={() => handleToolToggle(tool.id)}
                          />
                          <span>{tool.name}</span>
                        </label>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {attachedFiles.length > 0 && (
            <div className="attached-files-mini">
              {attachedFiles.map((file, idx) => (
                <div key={idx} className="file-mini">
                  <span>{file.type.startsWith('image/') ? '🖼️' : '📎'}</span>
                  <button onClick={() => handleRemoveFile(idx)}>×</button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="input-main-area">
          <textarea
            ref={textareaRef}
            className="minimal-textarea"
            placeholder="What would you like to build?"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onPaste={handlePaste}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit()
              }
            }}
            rows={1}
          />

          <div className="input-actions-mini">
            <button
              className="icon-btn"
              onClick={() => fileInputRef.current?.click()}
              title="Attach file"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
              </svg>
            </button>

            <button
              className="send-btn-minimal"
              onClick={handleSubmit}
              disabled={!message.trim() && attachedFiles.length === 0}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,.pdf,.txt,.md,.json,.csv"
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />
      </div>
    </div>
  )
}
