import { useState, useEffect } from 'react'

export async function searchFolders(query: string, basePath: string = process.cwd()): Promise<string[]> {
  if (!query || query.length < 2) return []

  const response = await fetch(`http://localhost:3001/api/folders/search?q=${encodeURIComponent(query)}&base=${encodeURIComponent(basePath)}`)
  const folders = await response.json()
  return folders
}

export function useFolderSearch(initialPath: string = '') {
  const [query, setQuery] = useState(initialPath)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!query || query.length < 2) {
      setSuggestions([])
      return
    }

    const timer = setTimeout(async () => {
      setLoading(true)
      try {
        const results = await searchFolders(query)
        setSuggestions(results)
      } catch (err) {
        console.error('Folder search error:', err)
      } finally {
        setLoading(false)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [query])

  return { query, setQuery, suggestions, loading }
}
