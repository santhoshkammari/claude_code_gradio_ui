export interface Session {
  id: string
  title: string
  created_at: number
  updated_at: number
}

export interface Task {
  id: string
  session_id: string
  title: string
  content?: string
  status: 'pending' | 'in_progress' | 'completed'
  priority?: 'low' | 'medium' | 'high'
  created_at: number
  updated_at: number
}

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: number
}
