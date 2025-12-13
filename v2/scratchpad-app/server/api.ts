import express from 'express'
import cors from 'cors'
import Database from 'better-sqlite3'
import { query } from '@anthropic-ai/claude-agent-sdk'

const app = express()
const db = new Database('scratchpad.db')

app.use(cors())
app.use(express.json())

db.exec(`
  CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
  );

  CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    status TEXT NOT NULL,
    priority TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
  );
`)

const sessionStmts = {
  getAll: db.prepare('SELECT * FROM sessions ORDER BY updated_at DESC'),
  getById: db.prepare('SELECT * FROM sessions WHERE id = ?'),
  create: db.prepare('INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)'),
  update: db.prepare('UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?'),
  delete: db.prepare('DELETE FROM sessions WHERE id = ?')
}

const taskStmts = {
  getBySession: db.prepare('SELECT * FROM tasks WHERE session_id = ? ORDER BY created_at DESC'),
  getById: db.prepare('SELECT * FROM tasks WHERE id = ?'),
  create: db.prepare('INSERT INTO tasks (id, session_id, title, content, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'),
  update: db.prepare('UPDATE tasks SET title = ?, content = ?, status = ?, priority = ?, updated_at = ? WHERE id = ?'),
  delete: db.prepare('DELETE FROM tasks WHERE id = ?')
}

const messageStmts = {
  getByTask: db.prepare('SELECT * FROM messages WHERE task_id = ? ORDER BY created_at ASC'),
  create: db.prepare('INSERT INTO messages (id, task_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)'),
  deleteByTask: db.prepare('DELETE FROM messages WHERE task_id = ?')
}

app.get('/api/sessions', (req, res) => {
  const sessions = sessionStmts.getAll.all()
  res.json(sessions)
})

app.post('/api/sessions', (req, res) => {
  const { id, title } = req.body
  const now = Date.now()
  sessionStmts.create.run(id, title, now, now)
  res.json({ id, title, created_at: now, updated_at: now })
})

app.delete('/api/sessions/:id', (req, res) => {
  sessionStmts.delete.run(req.params.id)
  res.json({ success: true })
})

app.get('/api/sessions/:id/tasks', (req, res) => {
  const tasks = taskStmts.getBySession.all(req.params.id)
  res.json(tasks)
})

app.post('/api/tasks', (req, res) => {
  const { id, session_id, title, content, status, priority } = req.body
  const now = Date.now()
  taskStmts.create.run(id, session_id, title, content || null, status, priority || null, now, now)
  res.json({ id, session_id, title, content, status, priority, created_at: now, updated_at: now })
})

app.put('/api/tasks/:id', (req, res) => {
  const { title, content, status, priority } = req.body
  const now = Date.now()
  taskStmts.update.run(title, content, status, priority, now, req.params.id)
  res.json({ success: true })
})

app.delete('/api/tasks/:id', (req, res) => {
  taskStmts.delete.run(req.params.id)
  res.json({ success: true })
})

app.get('/api/tasks/:id/messages', (req, res) => {
  const messages = messageStmts.getByTask.all(req.params.id)
  res.json(messages)
})

app.post('/api/tasks/:taskId/chat', async (req, res) => {
  const { message } = req.body
  const { taskId } = req.params

  const task = taskStmts.getById.get(taskId)
  if (!task) {
    return res.status(404).json({ error: 'Task not found' })
  }

  const userMsgId = `${Date.now()}-user`
  messageStmts.create.run(userMsgId, taskId, 'user', message, Date.now())

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  })

  const previousMessages = messageStmts.getByTask.all(taskId)
  const context = previousMessages.map(m => `${m.role}: ${m.content}`).join('\n')

  const fullPrompt = `Task: ${task.title}
${task.content ? `Description: ${task.content}` : ''}

Previous conversation:
${context}

User: ${message}`

  try {
    const stream = query({
      prompt: fullPrompt,
      options: {
        model: 'sonnet',
        systemPrompt: { type: 'preset', preset: 'claude_code' },
        tools: { type: 'preset', preset: 'claude_code' },
        permissionMode: 'bypassPermissions',
        allowDangerouslySkipPermissions: true
      }
    })

    let fullResponse = ''

    for await (const msg of stream) {
      if (msg.type === 'assistant') {
        const textContent = msg.message.content.find((c: any) => c.type === 'text')
        if (textContent) {
          fullResponse += textContent.text
          res.write(`data: ${JSON.stringify({ type: 'chunk', content: textContent.text })}\n\n`)
        }
      } else if (msg.type === 'result') {
        if (msg.subtype === 'success') {
          fullResponse = msg.result
        }
      }
    }

    const assistantMsgId = `${Date.now()}-assistant`
    messageStmts.create.run(assistantMsgId, taskId, 'assistant', fullResponse, Date.now())

    res.write(`data: ${JSON.stringify({ type: 'done', content: fullResponse })}\n\n`)
    res.end()
  } catch (error: any) {
    res.write(`data: ${JSON.stringify({ type: 'error', error: error.message })}\n\n`)
    res.end()
  }
})

const PORT = 3001
app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`)
})
