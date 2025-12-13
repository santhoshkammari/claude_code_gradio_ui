import express from 'express'
import cors from 'cors'
import Database from 'better-sqlite3'
import { query } from '@anthropic-ai/claude-agent-sdk'
import { spawn } from 'child_process'

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
    model TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS activity_logs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    type TEXT NOT NULL,
    data TEXT NOT NULL,
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
  create: db.prepare('INSERT INTO tasks (id, session_id, title, content, status, priority, model, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'),
  updateStatus: db.prepare('UPDATE tasks SET status = ?, model = ?, updated_at = ? WHERE id = ?'),
  delete: db.prepare('DELETE FROM tasks WHERE id = ?')
}

const activityStmts = {
  getByTask: db.prepare('SELECT * FROM activity_logs WHERE task_id = ? ORDER BY created_at ASC'),
  create: db.prepare('INSERT INTO activity_logs (id, task_id, type, data, created_at) VALUES (?, ?, ?, ?, ?)'),
  deleteByTask: db.prepare('DELETE FROM activity_logs WHERE task_id = ?')
}

const taskStreams = new Map<string, Set<express.Response>>()
const runningTasks = new Map<string, boolean>()

function broadcastToTask(taskId: string, data: any) {
  const clients = taskStreams.get(taskId)
  if (clients) {
    const payload = `data: ${JSON.stringify(data)}\n\n`
    clients.forEach(client => {
      try {
        client.write(payload)
      } catch (e) {
        clients.delete(client)
      }
    })
  }

  const logId = `${Date.now()}-${Math.random()}`
  activityStmts.create.run(logId, taskId, data.type, JSON.stringify(data), Date.now())
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
  const { id, session_id, title, content, status, priority, model } = req.body
  const now = Date.now()
  taskStmts.create.run(id, session_id, title, content || null, status, priority || null, model || null, now, now)
  res.json({ id, session_id, title, content, status, priority, model, created_at: now, updated_at: now })
})

app.delete('/api/tasks/:id', (req, res) => {
  taskStmts.delete.run(req.params.id)
  activityStmts.deleteByTask.run(req.params.id)
  res.json({ success: true })
})

app.get('/api/tasks/:taskId/stream', (req, res) => {
  const { taskId } = req.params

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  })

  if (!taskStreams.has(taskId)) {
    taskStreams.set(taskId, new Set())
  }
  taskStreams.get(taskId)!.add(res)

  const existingLogs = activityStmts.getByTask.all(taskId)
  existingLogs.forEach((log: any) => {
    res.write(`data: ${log.data}\n\n`)
  })

  req.on('close', () => {
    const clients = taskStreams.get(taskId)
    if (clients) {
      clients.delete(res)
      if (clients.size === 0) {
        taskStreams.delete(taskId)
      }
    }
  })
})

app.post('/api/tasks/:taskId/execute', async (req, res) => {
  const { taskId } = req.params
  const { model } = req.body
  const task = taskStmts.getById.get(taskId)

  if (!task) {
    return res.status(404).json({ error: 'Task not found' })
  }

  if (runningTasks.get(taskId)) {
    return res.json({ message: 'Task already running' })
  }

  res.json({ message: 'Task execution started' })

  runningTasks.set(taskId, true)
  taskStmts.updateStatus.run('in_progress', model, Date.now(), taskId)
  broadcastToTask(taskId, { type: 'task_status', status: 'in_progress' })

  const executor = model === 'qwen' ? executeQwenTask : executeClaudeTask
  executor(taskId, task.title, task.content, model).catch(err => {
    console.error('Task execution error:', err)
    taskStmts.updateStatus.run('failed', model, Date.now(), taskId)
    broadcastToTask(taskId, { type: 'task_status', status: 'failed', error: err.message })
    runningTasks.delete(taskId)
  })
})

async function executeClaudeTask(taskId: string, title: string, description: string, model: string) {
  try {
    const stream = query({
      prompt: `Task: ${title}\n\nDescription: ${description}\n\nPlease work on this task and provide updates on your progress.`,
      options: {
        model: model || 'sonnet',
        systemPrompt: { type: 'preset', preset: 'claude_code' },
        tools: { type: 'preset', preset: 'claude_code' },
        permissionMode: 'bypassPermissions',
        allowDangerouslySkipPermissions: true,
        cwd: process.cwd()
      }
    })

    for await (const msg of stream) {
      if (msg.type === 'assistant') {
        for (const content of msg.message.content) {
          if (content.type === 'text') {
            broadcastToTask(taskId, {
              type: 'message',
              role: 'assistant',
              content: content.text
            })
          } else if (content.type === 'tool_use') {
            broadcastToTask(taskId, {
              type: 'tool_use',
              tool: content.name,
              input: content.input
            })
          }
        }
      } else if (msg.type === 'user') {
        for (const content of msg.message.content) {
          if (content.type === 'text') {
            broadcastToTask(taskId, {
              type: 'message',
              role: 'user',
              content: content.text
            })
          } else if (content.type === 'tool_result') {
            broadcastToTask(taskId, {
              type: 'tool_result',
              tool: content.tool_use_id,
              content: typeof content.content === 'string' ? content.content : JSON.stringify(content.content)
            })
          }
        }
      } else if (msg.type === 'result') {
        if (msg.subtype === 'success') {
          broadcastToTask(taskId, {
            type: 'message',
            role: 'assistant',
            content: `Task completed successfully!\n\nResult: ${msg.result}`
          })
          taskStmts.updateStatus.run('completed', model, Date.now(), taskId)
          broadcastToTask(taskId, { type: 'task_status', status: 'completed' })
        } else {
          broadcastToTask(taskId, {
            type: 'message',
            role: 'assistant',
            content: `Task failed: ${msg.subtype}`
          })
          taskStmts.updateStatus.run('failed', model, Date.now(), taskId)
          broadcastToTask(taskId, { type: 'task_status', status: 'failed' })
        }
      }
    }
  } catch (error: any) {
    broadcastToTask(taskId, {
      type: 'message',
      role: 'system',
      content: `Error: ${error.message}`
    })
    taskStmts.updateStatus.run('failed', model, Date.now(), taskId)
    broadcastToTask(taskId, { type: 'task_status', status: 'failed', error: error.message })
  } finally {
    runningTasks.delete(taskId)
  }
}

async function executeQwenTask(taskId: string, title: string, description: string, model: string) {
  return new Promise((resolve, reject) => {
    const prompt = `Task: ${title}\n\nDescription: ${description}\n\nPlease work on this task and provide updates on your progress.`

    const qwen = spawn('qwen', ['-y', '-p', prompt])

    qwen.stdout.on('data', (data) => {
      const text = data.toString()
      broadcastToTask(taskId, {
        type: 'message',
        role: 'assistant',
        content: text
      })
    })

    qwen.stderr.on('data', (data) => {
      broadcastToTask(taskId, {
        type: 'message',
        role: 'system',
        content: `Error: ${data.toString()}`
      })
    })

    qwen.on('close', (code) => {
      if (code === 0) {
        taskStmts.updateStatus.run('completed', model, Date.now(), taskId)
        broadcastToTask(taskId, { type: 'task_status', status: 'completed' })
        resolve(true)
      } else {
        taskStmts.updateStatus.run('failed', model, Date.now(), taskId)
        broadcastToTask(taskId, { type: 'task_status', status: 'failed' })
        reject(new Error(`Qwen exited with code ${code}`))
      }
      runningTasks.delete(taskId)
    })
  })
}

const PORT = 3001
app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`)
})
