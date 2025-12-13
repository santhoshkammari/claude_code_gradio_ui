import Database from 'better-sqlite3'

const db = new Database('scratchpad.db')

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
    FOREIGN KEY (session_id) REFERENCES sessions(id)
  );

  CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
  );
`)

export const sessionQueries = {
  getAll: db.prepare('SELECT * FROM sessions ORDER BY updated_at DESC'),
  getById: db.prepare('SELECT * FROM sessions WHERE id = ?'),
  create: db.prepare('INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)'),
  update: db.prepare('UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?'),
  delete: db.prepare('DELETE FROM sessions WHERE id = ?')
}

export const taskQueries = {
  getBySession: db.prepare('SELECT * FROM tasks WHERE session_id = ? ORDER BY created_at DESC'),
  getById: db.prepare('SELECT * FROM tasks WHERE id = ?'),
  create: db.prepare('INSERT INTO tasks (id, session_id, title, content, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'),
  update: db.prepare('UPDATE tasks SET title = ?, content = ?, status = ?, priority = ?, updated_at = ? WHERE id = ?'),
  delete: db.prepare('DELETE FROM tasks WHERE id = ?')
}

export const messageQueries = {
  getBySession: db.prepare('SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC'),
  create: db.prepare('INSERT INTO messages (id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)'),
  delete: db.prepare('DELETE FROM messages WHERE session_id = ?')
}

export default db
