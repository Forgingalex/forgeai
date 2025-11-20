'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Send, Sparkles, Mic, MicOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { apiGet, apiPost } from '@/lib/api'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
  created_at: string
}

interface ChatSession {
  id: number
  created_at: string
  updated_at: string | null
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [isListening, setIsListening] = useState(false)
  const [isVoiceSupported, setIsVoiceSupported] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    const initSession = async () => {
      try {
        const session = await apiPost<ChatSession>('/api/v1/chat/sessions', {})
        
        // Validate session ID is a number
        if (typeof session.id !== 'number' || isNaN(session.id)) {
          throw new Error(`Invalid session ID: ${session.id}`)
        }
        
        setSessionId(session.id)
        
        const token = localStorage.getItem('token')
        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
        const ws = new WebSocket(`${wsUrl}/api/v1/chat/ws/${session.id}?token=${encodeURIComponent(token || '')}`)
        
        ws.onopen = () => {
          // Send token in first message for additional auth
          if (token) {
            ws.send(JSON.stringify({ token }))
          }
        }
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'chunk') {
              setMessages(prev => {
                const last = prev[prev.length - 1]
                if (last && last.role === 'assistant') {
                  return [...prev.slice(0, -1), { ...last, content: last.content + data.content }]
                }
                return [...prev, { id: Date.now(), role: 'assistant' as const, content: data.content, created_at: new Date().toISOString() }]
              })
            } else if (data.type === 'complete') {
              setIsLoading(false)
            } else if (data.type === 'error') {
              setMessages(prev => [...prev, {
                id: Date.now(),
                role: 'assistant',
                content: `Error: ${data.message}`,
                created_at: new Date().toISOString(),
              }])
              setIsLoading(false)
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
            setIsLoading(false)
          }
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          setMessages(prev => [...prev, {
            id: Date.now(),
            role: 'assistant',
            content: 'Connection error. Please try again.',
            created_at: new Date().toISOString(),
          }])
          setIsLoading(false)
        }
        
        ws.onclose = () => {
          console.log('WebSocket closed')
        }
        
        wsRef.current = ws
      } catch (error: any) {
        console.error('Failed to initialize session:', error)
        setMessages([{
          id: Date.now(),
          role: 'assistant',
          content: `Failed to connect: ${error.message || 'Unknown error'}`,
          created_at: new Date().toISOString(),
        }])
      }
    }
    
    initSession()
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    // Check for speech recognition support
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      if (SpeechRecognition) {
        setIsVoiceSupported(true)
        const recognition = new SpeechRecognition()
        recognition.continuous = false
        recognition.interimResults = false
        recognition.lang = 'en-US'
        
        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript
          setInput(transcript)
          setIsListening(false)
        }
        
        recognition.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error)
          setIsListening(false)
          if (event.error === 'no-speech') {
            alert('No speech detected. Please try again.')
          }
        }
        
        recognition.onend = () => {
          setIsListening(false)
        }
        
        recognitionRef.current = recognition
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  const toggleVoiceInput = () => {
    if (!isVoiceSupported) {
      alert('Voice input is not supported in your browser. Please use Chrome or Edge.')
      return
    }
    
    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
    } else {
      try {
        recognitionRef.current?.start()
        setIsListening(true)
      } catch (error) {
        console.error('Failed to start recognition:', error)
        setIsListening(false)
      }
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading || !wsRef.current) return

    if (wsRef.current.readyState !== WebSocket.OPEN) {
      alert('Connection not ready. Please wait...')
      return
    }

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: input,
      created_at: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    const messageToSend = input
    setInput('')
    setIsLoading(true)

    setMessages(prev => [...prev, {
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    }])

    try {
      wsRef.current.send(JSON.stringify({
        message: messageToSend,
        use_rag: false,
        top_k: 3,
      }))
    } catch (error: any) {
      console.error('Failed to send message:', error)
      setIsLoading(false)
      setMessages(prev => [...prev, {
        id: Date.now() + 2,
        role: 'assistant',
        content: `Failed to send message: ${error.message || 'Unknown error'}`,
        created_at: new Date().toISOString(),
      }])
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="flex-1 flex flex-col max-w-5xl mx-auto w-full">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-2">Welcome to ForgeAI</h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Ask me anything. Think faster, learn smarter.
                </p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <Card
                className={`max-w-2xl p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white dark:bg-gray-800'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-xs text-gray-500">Sources: {message.sources.join(', ')}</p>
                  </div>
                )}
              </Card>
            </motion.div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <Card className="bg-white dark:bg-gray-800 p-4">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </Card>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4">
          <div className="flex gap-2 max-w-4xl mx-auto">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything... Think faster, learn smarter."
              className="flex-1"
            />
            {isVoiceSupported && (
              <Button
                onClick={toggleVoiceInput}
                variant={isListening ? "destructive" : "outline"}
                disabled={isLoading}
                title={isListening ? "Stop recording" : "Start voice input"}
              >
                {isListening ? (
                  <MicOff className="w-4 h-4" />
                ) : (
                  <Mic className="w-4 h-4" />
                )}
              </Button>
            )}
            <Button onClick={handleSend} disabled={isLoading}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
          {isListening && (
            <div className="max-w-4xl mx-auto mt-2">
              <div className="flex items-center gap-2 text-sm text-red-600">
                <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse" />
                <span>Listening...</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

