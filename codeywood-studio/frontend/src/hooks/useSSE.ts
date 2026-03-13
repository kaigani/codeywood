import { useState, useCallback } from 'react'
import type { SSEEvent } from '../types'

export function useSSE() {
  const [lines, setLines] = useState<string[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [exitCode, setExitCode] = useState<number | null>(null)

  const start = useCallback(async (response: Response) => {
    setLines([])
    setIsRunning(true)
    setExitCode(null)

    const reader = response.body?.getReader()
    if (!reader) return

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n')
        buffer = parts.pop() || ''

        for (const line of parts) {
          if (!line.startsWith('data: ')) continue
          try {
            const event: SSEEvent = JSON.parse(line.slice(6))
            if (event.type === 'output') {
              setLines(prev => [...prev, event.text])
            } else if (event.type === 'done') {
              setExitCode(event.exit_code)
            } else if (event.type === 'error') {
              setLines(prev => [...prev, `ERROR: ${event.text}\n`])
            }
          } catch {}
        }
      }
    } finally {
      setIsRunning(false)
    }
  }, [])

  const clear = useCallback(() => {
    setLines([])
    setExitCode(null)
  }, [])

  return { lines, isRunning, exitCode, start, clear }
}
