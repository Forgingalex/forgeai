'use client'

import { useMutation } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'framer-motion'
import { Code2, Database, Sparkles } from 'lucide-react'
import { useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useMemo, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import { PromptInputBox, PromptMode } from '@/components/chat/prompt-input-box'
import { apiPost } from '@/lib/api'
import { cn } from '@/lib/utils'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  created_at: string
}

interface ChatSession {
  id: number
  workspace_id?: number | null
  created_at: string
  updated_at: string | null
}

function getSocketUrl(sessionId: number, token: string) {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
  return `${wsUrl}/api/v1/chat/ws/${sessionId}?token=${encodeURIComponent(token)}`
}

function ChatClient() {
  const searchParams = useSearchParams()
  const workspaceId = searchParams.get('workspace')
  const numericWorkspaceId = workspaceId ? Number(workspaceId) : undefined
  const [messages, setMessages] = useState<Message[]>([])
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [mode, setMode] = useState<PromptMode>('chat')
  const [canvasValue, setCanvasValue] = useState('# ForgeAI Canvas\n\n')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const assistantIdRef = useRef<number | null>(null)

  const createSession = useMutation({
    mutationFn: (payload: { workspace_id?: number }) =>
      apiPost<ChatSession>('/api/v1/chat/sessions', payload),
    onSuccess: (session) => setSessionId(session.id),
    onError: (error) => {
      setMessages([
        {
          id: Date.now(),
          role: 'assistant',
          content: `Failed to connect: ${error instanceof Error ? error.message : 'Unknown error'}`,
          created_at: new Date().toISOString(),
        },
      ])
    },
  })

  useEffect(() => {
    createSession.mutate({ workspace_id: numericWorkspaceId })
    return () => wsRef.current?.close()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [numericWorkspaceId])

  useEffect(() => {
    if (!sessionId) return undefined

    let cancelled = false
    const connect = async () => {
      try {
        const res = await fetch('/api/v1/auth/ws-token', { credentials: 'include' })
        if (!res.ok) return
        const { token } = await res.json()
        if (cancelled) return

        const socket = new WebSocket(getSocketUrl(sessionId, token))
        wsRef.current = socket

        socket.onmessage = (event) => {
          const data = JSON.parse(event.data)
          if (data.type === 'chunk') {
            setMessages((current) => {
              const assistantId = assistantIdRef.current
              const last = current[current.length - 1]
              if (assistantId && last?.id === assistantId && last.role === 'assistant') {
                return [...current.slice(0, -1), { ...last, content: last.content + data.content }]
              }
              const newId = Date.now()
              assistantIdRef.current = newId
              return [
                ...current,
                { id: newId, role: 'assistant', content: data.content, created_at: new Date().toISOString() },
              ]
            })
          }

          if (data.type === 'complete') {
            setIsLoading(false)
            const sources = Array.isArray(data.sources) ? data.sources : []
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantIdRef.current ? { ...message, sources } : message
              )
            )
            assistantIdRef.current = null
          }

          if (data.type === 'error') {
            setIsLoading(false)
            assistantIdRef.current = null
            setMessages((current) => [
              ...current,
              {
                id: Date.now(),
                role: 'assistant',
                content: `Error: ${data.message}`,
                created_at: new Date().toISOString(),
              },
            ])
          }
        }

        socket.onerror = () => {
          setIsLoading(false)
          setMessages((current) => [
            ...current,
            {
              id: Date.now(),
              role: 'assistant',
              content: 'Connection error. Please retry after the API server is ready.',
              created_at: new Date().toISOString(),
            },
          ])
        }
      } catch (err) {
        console.error('WebSocket connection failed:', err)
      }
    }

    connect()

    return () => {
      cancelled = true
      wsRef.current?.close()
    }
  }, [sessionId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const status = useMemo(() => {
    if (mode === 'search') return { icon: Database, label: 'Search mode', tone: 'text-cyan-200' }
    if (mode === 'think') return { icon: Sparkles, label: 'Think mode', tone: 'text-violet-200' }
    if (mode === 'canvas') return { icon: Code2, label: 'Canvas mode', tone: 'text-amber-200' }
    return { icon: Sparkles, label: 'Chat mode', tone: 'text-slate-200' }
  }, [mode])

  const handleSend = (message: string, _files: File[], selectedMode: PromptMode) => {
    const socket = wsRef.current
    if (!message.trim() || isLoading || !socket || socket.readyState !== WebSocket.OPEN) return

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    }
    const assistantMessage: Message = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    }

    assistantIdRef.current = assistantMessage.id
    setMessages((current) => [...current, userMessage, assistantMessage])
    setIsLoading(true)
    socket.send(JSON.stringify({ message, mode: selectedMode, top_k: 5 }))

    if (selectedMode === 'canvas') {
      setCanvasValue((current) => `${current}\n## Prompt\n\n${message}\n`)
    }
  }

  const StatusIcon = status.icon

  return (
    <div className="forge-surface flex h-[calc(100vh-4rem)] overflow-hidden text-white">
      <div className="absolute inset-0 bg-[url('/forgeai_frontend.jpg')] bg-[length:520px_auto] bg-fixed bg-center opacity-70" />
      <div className="absolute inset-0 bg-[#030711]/80" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(30,174,219,0.18),transparent_28%),radial-gradient(circle_at_82%_10%,rgba(236,173,41,0.16),transparent_26%)]" />

      <div className="relative z-10 flex w-full">
        <section className={cn('flex min-w-0 flex-1 flex-col', mode === 'canvas' && 'lg:w-1/2 lg:flex-none')}>
          <header className="border-b border-white/10 bg-[#06101d]/40 px-6 py-4 backdrop-blur-2xl">
            <div className="mx-auto flex max-w-5xl items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-cyan-100/70">ForgeAI Cognitive Platform</p>
                <h1 className="mt-1 text-xl font-semibold text-white">Local-first research cockpit</h1>
              </div>
              <div className={cn('flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.08] px-3 py-1.5 text-sm backdrop-blur-xl', status.tone)}>
                <StatusIcon className="h-4 w-4" />
                {status.label}
              </div>
            </div>
          </header>

          <main className="min-h-0 flex-1 overflow-y-auto px-4 py-6">
            <div className="mx-auto flex max-w-5xl flex-col gap-4">
              {messages.length === 0 && (
                <div className="flex min-h-[48vh] items-center justify-center">
                  <div className="max-w-2xl rounded-2xl border border-white/10 bg-white/[0.08] p-8 text-center shadow-2xl backdrop-blur-2xl">
                    <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-2xl border border-cyan-200/30 bg-cyan-200/10">
                      <Sparkles className="h-6 w-6 text-cyan-100" />
                    </div>
                    <h2 className="text-2xl font-semibold">Ask, retrieve, reason, or draft beside canvas.</h2>
                    <p className="mt-3 text-sm leading-6 text-slate-300">
                      Search uses local ChromaDB knowledge. Think routes to Gemini Pro with Ollama fallback. Canvas opens a working markdown surface.
                    </p>
                  </div>
                </div>
              )}

              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn('flex', message.role === 'user' ? 'justify-end' : 'justify-start')}
                >
                  <article
                    className={cn(
                      'max-w-3xl rounded-2xl border p-4 text-sm leading-6 shadow-2xl backdrop-blur-2xl',
                      message.role === 'user'
                        ? 'border-cyan-200/30 bg-cyan-300/15 text-cyan-50'
                        : 'border-white/10 bg-[#09111f]/70 text-slate-100'
                    )}
                  >
                    {message.role === 'assistant' ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content || ' '}</ReactMarkdown>
                    ) : (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 border-t border-white/10 pt-3 text-xs text-cyan-100/80">
                        Sources: {message.sources.join(', ')}
                      </div>
                    )}
                  </article>
                </motion.div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </main>

          <footer className="border-t border-white/10 bg-[#030711]/50 p-4 backdrop-blur-2xl">
            <div className="mx-auto max-w-4xl">
              <PromptInputBox
                isLoading={isLoading}
                onModeChange={setMode}
                onSend={handleSend}
                placeholder="Query the system with retrieval-augmented context..."
              />
            </div>
          </footer>
        </section>

        <AnimatePresence>
          {mode === 'canvas' && (
            <motion.aside
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 40 }}
              className="relative hidden min-w-0 flex-1 border-l border-white/10 bg-[#050b15]/70 backdrop-blur-2xl lg:flex lg:flex-col"
            >
              <header className="flex h-[73px] items-center justify-between border-b border-white/10 px-5">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-amber-100/70">Canvas</p>
                  <h2 className="text-lg font-semibold text-white">Markdown workspace</h2>
                </div>
                <Code2 className="h-5 w-5 text-amber-100" />
              </header>
              <textarea
                value={canvasValue}
                onChange={(event) => setCanvasValue(event.target.value)}
                className="min-h-0 flex-1 resize-none bg-transparent p-5 font-mono text-sm leading-6 text-slate-100 outline-none placeholder:text-slate-500"
              />
            </motion.aside>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="min-h-[calc(100vh-4rem)] bg-[#030711]" />}>
      <ChatClient />
    </Suspense>
  )
}
