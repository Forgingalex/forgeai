'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, BookOpen, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { apiPost } from '@/lib/api'

interface RAGResponse {
  answer: string
  sources: string[]
}

export default function MemoryPage() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState<string[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [error, setError] = useState('')
  const [topK, setTopK] = useState(3)

  const handleSearch = async () => {
    if (!question.trim()) return

    setIsSearching(true)
    setError('')
    setAnswer('')
    setSources([])

    try {
      const response = await apiPost<RAGResponse>('/api/v1/rag/query', {
        question: question.trim(),
        top_k: topK,
      })
      
      setAnswer(response.answer)
      setSources(response.sources || [])
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to query knowledge base'
      setError(errorMessage)
      console.error('RAG query error:', error)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Ask Your Notes</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Query your uploaded materials using RAG (Retrieval-Augmented Generation).
          </p>
        </div>

        <Card className="p-6 mb-6">
          <div className="space-y-4">
            <Input
              placeholder="Ask a question based on your uploaded materials..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />

            <div className="flex items-center gap-4">
              <label className="text-sm text-gray-600 dark:text-gray-400">
                Context chunks: {topK}
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="flex-1"
              />
            </div>

            <Button
              onClick={handleSearch}
              disabled={isSearching || !question.trim()}
              className="w-full"
            >
              <Search className="w-4 h-4 mr-2" />
              {isSearching ? 'Searching...' : 'Search Notes'}
            </Button>
          </div>
        </Card>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="p-4 border-red-200 bg-red-50 dark:bg-red-900/20">
              <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                <AlertCircle className="w-5 h-5" />
                <p>{error}</p>
              </div>
            </Card>
          </motion.div>
        )}

        {isSearching && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <Card className="p-6">
              <div className="flex items-center gap-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <p className="text-gray-600 dark:text-gray-400">Searching your knowledge base...</p>
              </div>
            </Card>
          </motion.div>
        )}

        {answer && !isSearching && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <BookOpen className="w-5 h-5 text-blue-600" />
                <h2 className="text-xl font-semibold">Answer from your notes</h2>
              </div>
              <div className="prose dark:prose-invert max-w-none mb-4">
                <p className="whitespace-pre-wrap">{answer}</p>
              </div>
              {sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-300">Sources:</p>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 dark:text-gray-400">
                    {sources.map((source, idx) => (
                      <li key={idx}>{source}</li>
                    ))}
                  </ul>
                </div>
              )}
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  )
}

