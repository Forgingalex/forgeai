'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, BookOpen, Trash2, Edit2, X, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { apiGet, apiPost, apiRequest } from '@/lib/api'

interface Flashcard {
  id: number
  front: string
  back: string
  review_count: number
}

interface FlashcardSet {
  id: number
  name: string
  description?: string
  flashcards: Flashcard[]
}

export default function FlashcardsPage() {
  const [sets, setSets] = useState<FlashcardSet[]>([])
  const [selectedSet, setSelectedSet] = useState<FlashcardSet | null>(null)
  const [isCreatingSet, setIsCreatingSet] = useState(false)
  const [isAddingCard, setIsAddingCard] = useState(false)
  const [newSetName, setNewSetName] = useState('')
  const [newSetDesc, setNewSetDesc] = useState('')
  const [newCardFront, setNewCardFront] = useState('')
  const [newCardBack, setNewCardBack] = useState('')
  const [flippedCard, setFlippedCard] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadSets()
  }, [])

  const loadSets = async () => {
    try {
      const data = await apiGet<FlashcardSet[]>('/api/v1/flashcards/sets')
      setSets(data)
    } catch (error: any) {
      console.error('Failed to load sets:', error)
    }
  }

  const loadSet = async (setId: number) => {
    try {
      const data = await apiGet<FlashcardSet>(`/api/v1/flashcards/sets/${setId}`)
      setSelectedSet(data)
      setSets(prev => prev.map(s => s.id === setId ? data : s))
    } catch (error: any) {
      console.error('Failed to load set:', error)
    }
  }

  const createSet = async () => {
    if (!newSetName.trim()) return
    
    setIsLoading(true)
    try {
      const data = await apiPost<FlashcardSet>('/api/v1/flashcards/sets', {
        name: newSetName,
        description: newSetDesc || undefined,
      })
      setSets(prev => [...prev, data])
      setIsCreatingSet(false)
      setNewSetName('')
      setNewSetDesc('')
      setSelectedSet(data)
    } catch (error: any) {
      alert(error.message || 'Failed to create set')
    } finally {
      setIsLoading(false)
    }
  }

  const addCard = async () => {
    if (!selectedSet || !newCardFront.trim() || !newCardBack.trim()) return
    
    setIsLoading(true)
    try {
      const data = await apiPost<Flashcard>(`/api/v1/flashcards/sets/${selectedSet.id}/cards`, {
        front: newCardFront,
        back: newCardBack,
      })
      await loadSet(selectedSet.id)
      setIsAddingCard(false)
      setNewCardFront('')
      setNewCardBack('')
    } catch (error: any) {
      alert(error.message || 'Failed to add card')
    } finally {
      setIsLoading(false)
    }
  }

  const deleteSet = async (setId: number) => {
    if (!confirm('Delete this flashcard set?')) return
    
    try {
      await apiRequest(`/api/v1/flashcards/sets/${setId}`, { method: 'DELETE' })
      setSets(prev => prev.filter(s => s.id !== setId))
      if (selectedSet?.id === setId) {
        setSelectedSet(null)
      }
    } catch (error: any) {
      alert(error.message || 'Failed to delete set')
    }
  }

  const deleteCard = async (cardId: number) => {
    if (!confirm('Delete this flashcard?')) return
    
    try {
      await apiRequest(`/api/v1/flashcards/cards/${cardId}`, { method: 'DELETE' })
      if (selectedSet) {
        await loadSet(selectedSet.id)
      }
    } catch (error: any) {
      alert(error.message || 'Failed to delete card')
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">Flashcards</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Create and manage your study flashcards
            </p>
          </div>
          <Button onClick={() => setIsCreatingSet(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Set
          </Button>
        </div>

        {isCreatingSet && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Create New Set</h2>
              <div className="space-y-4">
                <Input
                  placeholder="Set name"
                  value={newSetName}
                  onChange={(e) => setNewSetName(e.target.value)}
                />
                <Input
                  placeholder="Description (optional)"
                  value={newSetDesc}
                  onChange={(e) => setNewSetDesc(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button onClick={createSet} disabled={isLoading}>
                    Create
                  </Button>
                  <Button variant="ghost" onClick={() => setIsCreatingSet(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1">
            <Card className="p-4">
              <h2 className="text-lg font-semibold mb-4">Your Sets</h2>
              <div className="space-y-2">
                {sets.map((set) => (
                  <div
                    key={set.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedSet?.id === set.id
                        ? 'bg-blue-100 dark:bg-blue-900'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                    onClick={() => loadSet(set.id)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium">{set.name}</h3>
                        <p className="text-sm text-gray-500">
                          {set.flashcards?.length || 0} cards
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteSet(set.id)
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
                {sets.length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">
                    No sets yet. Create one to get started!
                  </p>
                )}
              </div>
            </Card>
          </div>

          <div className="md:col-span-2">
            {selectedSet ? (
              <div>
                <div className="mb-4 flex justify-between items-center">
                  <div>
                    <h2 className="text-2xl font-bold">{selectedSet.name}</h2>
                    {selectedSet.description && (
                      <p className="text-gray-600 dark:text-gray-400">
                        {selectedSet.description}
                      </p>
                    )}
                  </div>
                  <Button onClick={() => setIsAddingCard(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Card
                  </Button>
                </div>

                {isAddingCard && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6"
                  >
                    <Card className="p-6">
                      <h3 className="text-lg font-semibold mb-4">Add New Card</h3>
                      <div className="space-y-4">
                        <Input
                          placeholder="Front (question)"
                          value={newCardFront}
                          onChange={(e) => setNewCardFront(e.target.value)}
                        />
                        <Input
                          placeholder="Back (answer)"
                          value={newCardBack}
                          onChange={(e) => setNewCardBack(e.target.value)}
                        />
                        <div className="flex gap-2">
                          <Button onClick={addCard} disabled={isLoading}>
                            Add
                          </Button>
                          <Button variant="ghost" onClick={() => setIsAddingCard(false)}>
                            Cancel
                          </Button>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedSet.flashcards?.map((card) => (
                    <motion.div
                      key={card.id}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="relative"
                    >
                      <Card
                        className="p-6 h-48 cursor-pointer hover:shadow-lg transition-shadow"
                        onClick={() => setFlippedCard(flippedCard === card.id ? null : card.id)}
                      >
                        <div className="h-full flex flex-col justify-between">
                          <div className="flex-1 flex items-center justify-center">
                            <p className="text-center text-lg">
                              {flippedCard === card.id ? card.back : card.front}
                            </p>
                          </div>
                          <div className="flex justify-between items-center mt-4 pt-4 border-t">
                            <span className="text-xs text-gray-500">
                              Reviewed {card.review_count} times
                            </span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation()
                                deleteCard(card.id)
                              }}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </Card>
                    </motion.div>
                  ))}
                  {(!selectedSet.flashcards || selectedSet.flashcards.length === 0) && (
                    <div className="col-span-2 text-center py-12 text-gray-500">
                      <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <p>No cards yet. Add your first card!</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <Card className="p-12 text-center">
                <BookOpen className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-500">Select a set to view flashcards</p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

