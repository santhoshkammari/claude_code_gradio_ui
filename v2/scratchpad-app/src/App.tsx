import { useState, useEffect, useRef } from 'react'
import './App.css'
import './components/shared/common.css'
import LeftSidebar from './components/LeftSidebar/LeftSidebar'
import RightSidebar from './components/RightSidebar/RightSidebar'
import TaskGrid from './components/TaskGrid/TaskGrid'
import ChatView from './components/ChatView/ChatView'
import MainChatView from './components/MainChatView/MainChatView'
import NewTaskModal from './components/Modals/NewTaskModal'
import NewSessionModal from './components/Modals/NewSessionModal'
import type { Session, Task } from './types'

const API_URL = 'http://localhost:3001/api'

function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [showChat, setShowChat] = useState(false)
  const [activityLog, setActivityLog] = useState<any[]>([])
  const [chatMessages, setChatMessages] = useState<any[]>([])
  const [gitDiff, setGitDiff] = useState<string>('')
  const [taskFilter, setTaskFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')
  const [showTaskModal, setShowTaskModal] = useState(false)
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const [newTaskFolder, setNewTaskFolder] = useState('')
  const [showNewSessionModal, setShowNewSessionModal] = useState(false)
  const [newSessionFolder, setNewSessionFolder] = useState('')
  const [newSessionFolderSuggestions, setNewSessionFolderSuggestions] = useState<string[]>([])
  const [chatInput, setChatInput] = useState('')
  const [selectedModel, setSelectedModel] = useState('sonnet')
  const [showSidebar, setShowSidebar] = useState(false)
  const [collapsedSessions, setCollapsedSessions] = useState<Record<string, boolean>>({})
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
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

  const scientistNames = [
    'Einstein', 'Feynman', 'Curie', 'Turing', 'Tesla', 'Newton',
    'Bohr', 'Hawking', 'Ramanujan', 'Darwin', 'Pasteur', 'Copernicus',
    'Galileo', 'Maxwell', 'Planck', 'Heisenberg', 'Dirac', 'Oppenheimer',
    'Schrödinger', 'Hubble', 'Watson', 'Crick', 'Mendel', 'Lavoisier',
    'Faraday', 'Rutherford', 'Chadwick', 'Bose', 'Euler', 'Lagrange'
  ]

  const getRandomScientistName = () => {
    return scientistNames[Math.floor(Math.random() * scientistNames.length)]
  }

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
      setGitDiff(data.diff || '')
    } catch (err) {
      console.error('Failed to fetch file changes:', err)
    }
  }

  const parseStreamJsonMessage = (data: any) => {
    try {
      if (data.type && (data.type === 'system' || data.type === 'assistant' || data.type === 'result')) {
        switch (data.type) {
          case 'system':
            if (data.subtype === 'init') {
              return { type: 'system_init', role: 'system', content: 'Qwen initialized' };
            }
            break;
          case 'assistant':
            if (data.message?.content) {
              const textContent = data.message.content
                .filter((item: any) => item?.type === 'text')
                .map((item: any) => item?.text)
                .filter(Boolean)
                .join(' ');

              if (textContent) {
                return { type: 'message', role: 'assistant', content: textContent };
              }

              const toolContent = data.message.content
                .filter((item: any) => item?.type === 'tool_use')
                .map((item: any) => `Using tool: ${item?.name || 'unknown'} with input: ${JSON.stringify(item?.input || {})}`)
                .join(' ');

              if (toolContent) {
                return { type: 'message', role: 'assistant', content: toolContent };
              }
            }
            break;
          case 'result':
            const resultContent = data.result || `Task completed with ${data.num_turns || 0} turns`;
            return { type: 'message', role: 'assistant', content: resultContent };
        }
      }
    } catch (parseError) {
      console.error('Error parsing stream-json message:', parseError);
      console.error('Problematic data:', data);
    }
    return data;
  };

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
      try {
        const raw_data = JSON.parse(event.data);
        const data = parseStreamJsonMessage(raw_data);
        setActivityLog(prev => [...prev, data])

        if (data.type === 'message' && data.role !== 'system') {
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
      } catch (error) {
        console.error('Error parsing stream data:', error);
        console.error('Raw event data:', event.data);
      }
    }

    eventSource.onerror = () => {
      eventSource.close()
      eventSourceRef.current = null
    }
  }

  const createSession = async (folderPath?: string) => {
    const id = Date.now().toString()
    const title = getRandomScientistName()
    const res = await fetch(`${API_URL}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, title, folder_path: folderPath || undefined })
    })
    const newSession = await res.json()
    setSessions([newSession, ...sessions])
    setCurrentSession(newSession)
  }

  const handleCreateSession = async () => {
    await createSession(newSessionFolder)
    setShowNewSessionModal(false)
    setNewSessionFolder('')
    setNewSessionFolderSuggestions([])
  }

  const searchSessionFolders = async (query: string) => {
    if (!query || query.length < 2) {
      setNewSessionFolderSuggestions([])
      return
    }
    try {
      const res = await fetch(`${API_URL}/folders/search?q=${encodeURIComponent(query)}`)
      const data = await res.json()
      setNewSessionFolderSuggestions(data)
    } catch (err) {
      console.error('Session folder search error:', err)
    }
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
    if (!newTaskDescription.trim()) return

    let session = currentSession
    if (!session) {
      const id = Date.now().toString()
      const title = getRandomScientistName()
      const res = await fetch(`${API_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, title })
      })
      const newSession = await res.json()
      setSessions([newSession])
      setCurrentSession(newSession)
      session = newSession
    }

    if (!session) return;

    const id = Date.now().toString()
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id,
        session_id: session.id,
        title: newTaskDescription.substring(0, 30) + (newTaskDescription.length > 30 ? '...' : ''),
        content: newTaskDescription,
        status: 'pending',
        priority: 'medium',
        folder_path: newTaskFolder || null
      })
    })
    const newTask = await res.json()
    setTasks([newTask, ...tasks])
    setShowTaskModal(false)
    setNewTaskDescription('')
    setNewTaskFolder('')
  }

  const handleBackToTasks = () => {
    setShowChat(false)
    setSelectedTask(null)
    setShowSidebar(false)
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

  const sendMessage = async () => {
    if (!chatInput.trim() || !selectedTask) return

    if (chatInput.toLowerCase().trim() === 'hi') {
      const userMessage = { role: 'user', content: chatInput }
      setChatMessages(prev => [...prev, userMessage])

      setTimeout(() => {
        const aiResponse = { role: 'assistant', content: 'sayi back' }
        setChatMessages(prev => [...prev, aiResponse])
      }, 300)

      setChatInput('')
      return
    }

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

  const handleMainChatSubmit = async (message: string, config: any) => {
    let session = currentSession
    if (!session) {
      const id = Date.now().toString()
      const title = getRandomScientistName()
      const res = await fetch(`${API_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, title })
      })
      const newSession = await res.json()
      setSessions([newSession])
      setCurrentSession(newSession)
      session = newSession
    }

    if (!session) return

    const id = Date.now().toString()
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id,
        session_id: session.id,
        title: message.substring(0, 30) + (message.length > 30 ? '...' : ''),
        content: message,
        status: 'pending',
        priority: 'medium',
        model: config.model,
        agent: config.agent,
        tools: config.tools
      })
    })
    const newTask = await res.json()
    setTasks([newTask, ...tasks])
    setSelectedTask(newTask)
    setShowChat(true)
    setShowSidebar(true)

    try {
      await fetch(`${API_URL}/tasks/${newTask.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: config.model })
      })
    } catch (err) {
      console.error('Failed to start task:', err)
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
      setGitDiff('')
    }
  }

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  return (
    <div className={`app ${showSidebar ? 'sidebar-visible' : 'sidebar-hidden'}`}>
      <LeftSidebar
        sessions={sessions}
        currentSession={currentSession}
        tasks={tasks}
        selectedTask={selectedTask}
        collapsedSessions={collapsedSessions}
        onSessionClick={setCurrentSession}
        onTaskClick={(task) => {
          setSelectedTask(task);
          setShowChat(true);
          setShowSidebar(true);
        }}
        onDeleteSession={deleteSession}
        onDeleteTask={deleteTask}
        onNewSession={createSession}
        onToggleSession={(id) => {
          setCollapsedSessions(prev => ({
            ...prev,
            [id]: !prev[id]
          }));
        }}
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={toggleSidebar}
      />

      <main className="main-content">
        {!showChat ? (
          <div className="main-with-overlay">
            <TaskGrid
              tasks={tasks}
              selectedTask={selectedTask}
              taskFilter={taskFilter}
              onTaskClick={(task) => {
                setSelectedTask(task);
                setShowChat(true);
                setShowSidebar(true);
              }}
              onDeleteTask={deleteTask}
              onStartTask={async (taskId: string, model: string) => {
                try {
                  await fetch(`${API_URL}/tasks/${taskId}/execute`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model })
                  })
                } catch (err) {
                  console.error('Failed to start task:', err)
                }
              }}
              onUpdateTaskModel={(taskId: string, model: string) => {
                setTasks(prev => prev.map(t =>
                  t.id === taskId ? { ...t, model: model } : t
                ));
              }}
              onNewTask={() => setShowTaskModal(true)}
              onFilterChange={setTaskFilter}
              API_URL={API_URL}
            />
            <MainChatView onSubmitMessage={handleMainChatSubmit} />
          </div>
        ) : (
          <ChatView
            selectedTask={selectedTask}
            chatMessages={chatMessages}
            chatInput={chatInput}
            selectedModel={selectedModel}
            onBackToTasks={handleBackToTasks}
            onChatInputChange={setChatInput}
            onSendMessage={sendMessage}
            onModelChange={setSelectedModel}
            onStartTask={startTask}
            chatEndRef={chatEndRef}
          />
        )}
      </main>

      <RightSidebar
        gitDiff={gitDiff}
        onClose={handleBackToTasks}
      />

      <NewTaskModal
        isOpen={showTaskModal}
        taskDescription={newTaskDescription}
        onDescriptionChange={setNewTaskDescription}
        onClose={() => setShowTaskModal(false)}
        onCreate={handleCreateTask}
      />

      <NewSessionModal
        isOpen={showNewSessionModal}
        folderPath={newSessionFolder}
        suggestions={newSessionFolderSuggestions}
        onFolderPathChange={(value) => {
          setNewSessionFolder(value)
          searchSessionFolders(value)
        }}
        onClose={() => {
          setShowNewSessionModal(false)
          setNewSessionFolder('')
          setNewSessionFolderSuggestions([])
        }}
        onCreate={handleCreateSession}
      />
    </div>
  )
}

export default App
