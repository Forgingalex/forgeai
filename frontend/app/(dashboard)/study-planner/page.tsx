'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, Calendar, CheckCircle2, Clock, Trash2, BookOpen } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { apiGet, apiPost, apiRequest } from '@/lib/api'

interface StudySession {
  id: number
  topic: string
  scheduled_date: string
  duration_minutes: number
  completed: boolean
  notes?: string
}

interface StudyPlan {
  id: number
  title: string
  description?: string
  topics: string[]
  start_date: string
  end_date: string
  hours_per_day: number
  status: string
  sessions: StudySession[]
}

export default function StudyPlannerPage() {
  const [plans, setPlans] = useState<StudyPlan[]>([])
  const [selectedPlan, setSelectedPlan] = useState<StudyPlan | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const [newPlanTitle, setNewPlanTitle] = useState('')
  const [newPlanDesc, setNewPlanDesc] = useState('')
  const [newPlanTopics, setNewPlanTopics] = useState('')
  const [newPlanStartDate, setNewPlanStartDate] = useState('')
  const [newPlanEndDate, setNewPlanEndDate] = useState('')
  const [newPlanHours, setNewPlanHours] = useState(2)

  useEffect(() => {
    loadPlans()
  }, [])

  const loadPlans = async () => {
    try {
      const data = await apiGet<StudyPlan[]>('/api/v1/study-planner/')
      setPlans(data)
    } catch (error: any) {
      console.error('Failed to load plans:', error)
    }
  }

  const loadPlan = async (planId: number) => {
    try {
      const data = await apiGet<StudyPlan>(`/api/v1/study-planner/${planId}`)
      setSelectedPlan(data)
      setPlans(prev => prev.map(p => p.id === planId ? data : p))
    } catch (error: any) {
      console.error('Failed to load plan:', error)
    }
  }

  const createPlan = async () => {
    if (!newPlanTitle.trim() || !newPlanStartDate || !newPlanEndDate) return
    
    setIsLoading(true)
    try {
      const topics = newPlanTopics.split(',').map(t => t.trim()).filter(t => t)
      const data = await apiPost<StudyPlan>('/api/v1/study-planner/', {
        title: newPlanTitle,
        description: newPlanDesc || undefined,
        topics: topics,
        start_date: newPlanStartDate,
        end_date: newPlanEndDate,
        hours_per_day: newPlanHours,
      })
      setPlans(prev => [data, ...prev])
      setIsCreating(false)
      setNewPlanTitle('')
      setNewPlanDesc('')
      setNewPlanTopics('')
      setNewPlanStartDate('')
      setNewPlanEndDate('')
      setNewPlanHours(2)
      await loadPlan(data.id)
    } catch (error: any) {
      alert(error.message || 'Failed to create plan')
    } finally {
      setIsLoading(false)
    }
  }

  const completeSession = async (sessionId: number) => {
    if (!selectedPlan) return
    
    try {
      await apiPost(`/api/v1/study-planner/${selectedPlan.id}/sessions/${sessionId}/complete`, {})
      await loadPlan(selectedPlan.id)
    } catch (error: any) {
      alert(error.message || 'Failed to complete session')
    }
  }

  const deletePlan = async (planId: number) => {
    if (!confirm('Delete this study plan?')) return
    
    try {
      await apiRequest(`/api/v1/study-planner/${planId}`, { method: 'DELETE' })
      setPlans(prev => prev.filter(p => p.id !== planId))
      if (selectedPlan?.id === planId) {
        setSelectedPlan(null)
      }
    } catch (error: any) {
      alert(error.message || 'Failed to delete plan')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const getCompletionRate = (plan: StudyPlan) => {
    if (!plan.sessions || plan.sessions.length === 0) return 0
    const completed = plan.sessions.filter(s => s.completed).length
    return Math.round((completed / plan.sessions.length) * 100)
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">Study Planner</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Create personalized study schedules
            </p>
          </div>
          <Button onClick={() => setIsCreating(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Plan
          </Button>
        </div>

        {isCreating && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Create Study Plan</h2>
              <div className="space-y-4">
                <Input
                  placeholder="Plan title"
                  value={newPlanTitle}
                  onChange={(e) => setNewPlanTitle(e.target.value)}
                />
                <Input
                  placeholder="Description (optional)"
                  value={newPlanDesc}
                  onChange={(e) => setNewPlanDesc(e.target.value)}
                />
                <Input
                  placeholder="Topics (comma-separated)"
                  value={newPlanTopics}
                  onChange={(e) => setNewPlanTopics(e.target.value)}
                />
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-600 dark:text-gray-400 mb-1 block">
                      Start Date
                    </label>
                    <Input
                      type="date"
                      value={newPlanStartDate}
                      onChange={(e) => setNewPlanStartDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-600 dark:text-gray-400 mb-1 block">
                      End Date
                    </label>
                    <Input
                      type="date"
                      value={newPlanEndDate}
                      onChange={(e) => setNewPlanEndDate(e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400 mb-1 block">
                    Hours per day: {newPlanHours}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="8"
                    value={newPlanHours}
                    onChange={(e) => setNewPlanHours(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div className="flex gap-2">
                  <Button onClick={createPlan} disabled={isLoading}>
                    Create Plan
                  </Button>
                  <Button variant="ghost" onClick={() => setIsCreating(false)}>
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
              <h2 className="text-lg font-semibold mb-4">Your Plans</h2>
              <div className="space-y-2">
                {plans.map((plan) => {
                  const completionRate = getCompletionRate(plan)
                  return (
                    <div
                      key={plan.id}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedPlan?.id === plan.id
                          ? 'bg-blue-100 dark:bg-blue-900'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                      onClick={() => loadPlan(plan.id)}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium">{plan.title}</h3>
                          <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
                            <Calendar className="w-3 h-3" />
                            <span>{completionRate}% complete</span>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            deletePlan(plan.id)
                          }}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  )
                })}
                {plans.length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">
                    No plans yet. Create one to get started!
                  </p>
                )}
              </div>
            </Card>
          </div>

          <div className="md:col-span-2">
            {selectedPlan ? (
              <div>
                <div className="mb-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h2 className="text-2xl font-bold">{selectedPlan.title}</h2>
                      {selectedPlan.description && (
                        <p className="text-gray-600 dark:text-gray-400 mt-1">
                          {selectedPlan.description}
                        </p>
                      )}
                      <div className="mt-2 flex gap-4 text-sm text-gray-500">
                        <span>{formatDate(selectedPlan.start_date)} - {formatDate(selectedPlan.end_date)}</span>
                        <span>{selectedPlan.hours_per_day} hrs/day</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">
                        {getCompletionRate(selectedPlan)}%
                      </div>
                      <div className="text-xs text-gray-500">Complete</div>
                    </div>
                  </div>
                  
                  {selectedPlan.topics && selectedPlan.topics.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {selectedPlan.topics.map((topic, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded text-sm"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="space-y-3">
                  {selectedPlan.sessions?.map((session) => (
                    <motion.div
                      key={session.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <Card className={`p-4 ${session.completed ? 'opacity-75' : ''}`}>
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              {session.completed ? (
                                <CheckCircle2 className="w-5 h-5 text-green-600" />
                              ) : (
                                <Clock className="w-5 h-5 text-gray-400" />
                              )}
                              <div>
                                <h3 className="font-semibold">{session.topic}</h3>
                                <div className="text-sm text-gray-500 mt-1">
                                  {formatDate(session.scheduled_date)} • {session.duration_minutes} minutes
                                </div>
                                {session.notes && (
                                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                                    {session.notes}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                          {!session.completed && (
                            <Button
                              size="sm"
                              onClick={() => completeSession(session.id)}
                            >
                              Mark Complete
                            </Button>
                          )}
                        </div>
                      </Card>
                    </motion.div>
                  ))}
                  {(!selectedPlan.sessions || selectedPlan.sessions.length === 0) && (
                    <Card className="p-12 text-center">
                      <BookOpen className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                      <p className="text-gray-500">No sessions scheduled yet</p>
                    </Card>
                  )}
                </div>
              </div>
            ) : (
              <Card className="p-12 text-center">
                <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-500">Select a plan to view schedule</p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

