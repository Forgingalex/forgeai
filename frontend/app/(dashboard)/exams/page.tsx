'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Plus, FileText, CheckCircle2, XCircle, Clock, Trophy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { apiGet, apiPost } from '@/lib/api'

interface ExamQuestion {
  id: number
  question_number: number
  question: string
  user_answer?: string
  is_correct?: boolean
  feedback?: string
}

interface ExamSession {
  id: number
  title: string
  topic?: string
  total_questions: number
  score?: number
  status: string
  questions: ExamQuestion[]
}

export default function ExamsPage() {
  const [exams, setExams] = useState<ExamSession[]>([])
  const [selectedExam, setSelectedExam] = useState<ExamSession | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const [newExamTitle, setNewExamTitle] = useState('')
  const [newExamTopic, setNewExamTopic] = useState('')
  const [newExamQuestions, setNewExamQuestions] = useState(10)

  useEffect(() => {
    loadExams()
  }, [])

  const loadExams = async () => {
    try {
      const data = await apiGet<ExamSession[]>('/api/v1/exams/')
      setExams(data)
    } catch (error: any) {
      console.error('Failed to load exams:', error)
    }
  }

  const loadExam = async (examId: number) => {
    try {
      const data = await apiGet<ExamSession>(`/api/v1/exams/${examId}`)
      setSelectedExam(data)
      setCurrentQuestionIndex(0)
      const initialAnswers: Record<number, string> = {}
      data.questions.forEach(q => {
        if (q.user_answer) {
          initialAnswers[q.id] = q.user_answer
        }
      })
      setAnswers(initialAnswers)
    } catch (error: any) {
      console.error('Failed to load exam:', error)
    }
  }

  const createExam = async () => {
    if (!newExamTitle.trim()) return
    
    setIsLoading(true)
    try {
      const data = await apiPost<ExamSession>('/api/v1/exams/', {
        title: newExamTitle,
        topic: newExamTopic || undefined,
        total_questions: newExamQuestions,
      })
      setExams(prev => [data, ...prev])
      setIsCreating(false)
      setNewExamTitle('')
      setNewExamTopic('')
      setNewExamQuestions(10)
      await loadExam(data.id)
    } catch (error: any) {
      alert(error.message || 'Failed to create exam')
    } finally {
      setIsLoading(false)
    }
  }

  const submitAnswer = async (questionId: number, answer: string) => {
    if (!selectedExam) return
    
    setIsSubmitting(true)
    try {
      await apiPost(`/api/v1/exams/${selectedExam.id}/submit-answer`, {
        question_id: questionId,
        answer: answer,
      })
      await loadExam(selectedExam.id)
    } catch (error: any) {
      alert(error.message || 'Failed to submit answer')
    } finally {
      setIsSubmitting(false)
    }
  }

  const completeExam = async () => {
    if (!selectedExam) return
    
    setIsLoading(true)
    try {
      await apiPost(`/api/v1/exams/${selectedExam.id}/complete`, {})
      await loadExam(selectedExam.id)
    } catch (error: any) {
      alert(error.message || 'Failed to complete exam')
    } finally {
      setIsLoading(false)
    }
  }

  const currentQuestion = selectedExam?.questions[currentQuestionIndex]

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">Exam Mode</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Test your knowledge with AI-generated exams
            </p>
          </div>
          <Button onClick={() => setIsCreating(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Exam
          </Button>
        </div>

        {isCreating && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Create New Exam</h2>
              <div className="space-y-4">
                <Input
                  placeholder="Exam title"
                  value={newExamTitle}
                  onChange={(e) => setNewExamTitle(e.target.value)}
                />
                <Input
                  placeholder="Topic (optional)"
                  value={newExamTopic}
                  onChange={(e) => setNewExamTopic(e.target.value)}
                />
                <div>
                  <label className="text-sm text-gray-600 dark:text-gray-400">
                    Number of questions: {newExamQuestions}
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="20"
                    value={newExamQuestions}
                    onChange={(e) => setNewExamQuestions(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
                <div className="flex gap-2">
                  <Button onClick={createExam} disabled={isLoading}>
                    Create Exam
                  </Button>
                  <Button variant="ghost" onClick={() => setIsCreating(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <Card className="p-4">
              <h2 className="text-lg font-semibold mb-4">Your Exams</h2>
              <div className="space-y-2">
                {exams.map((exam) => (
                  <div
                    key={exam.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedExam?.id === exam.id
                        ? 'bg-blue-100 dark:bg-blue-900'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                    onClick={() => loadExam(exam.id)}
                  >
                    <h3 className="font-medium">{exam.title}</h3>
                    <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                      {exam.status === 'completed' && exam.score !== null ? (
                        <>
                          <Trophy className="w-4 h-4" />
                          <span>{exam.score.toFixed(0)}%</span>
                        </>
                      ) : (
                        <>
                          <Clock className="w-4 h-4" />
                          <span>{exam.status}</span>
                        </>
                      )}
                    </div>
                  </div>
                ))}
                {exams.length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">
                    No exams yet. Create one to get started!
                  </p>
                )}
              </div>
            </Card>
          </div>

          <div className="md:col-span-3">
            {selectedExam ? (
              <div>
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h2 className="text-2xl font-bold">{selectedExam.title}</h2>
                      {selectedExam.topic && (
                        <p className="text-gray-600 dark:text-gray-400">
                          Topic: {selectedExam.topic}
                        </p>
                      )}
                    </div>
                    {selectedExam.status === 'completed' && selectedExam.score !== null && (
                      <div className="text-right">
                        <div className="text-3xl font-bold text-blue-600">
                          {selectedExam.score.toFixed(0)}%
                        </div>
                        <div className="text-sm text-gray-500">
                          {selectedExam.questions.filter(q => q.is_correct).length} / {selectedExam.total_questions} correct
                        </div>
                      </div>
                    )}
                  </div>

                  {selectedExam.status === 'in_progress' && (
                    <div className="mb-4">
                      <div className="flex gap-2 mb-2">
                        {selectedExam.questions.map((q, idx) => (
                          <button
                            key={q.id}
                            onClick={() => setCurrentQuestionIndex(idx)}
                            className={`w-10 h-10 rounded ${
                              idx === currentQuestionIndex
                                ? 'bg-blue-600 text-white'
                                : answers[q.id]
                                ? 'bg-green-500 text-white'
                                : 'bg-gray-200 dark:bg-gray-700'
                            }`}
                          >
                            {idx + 1}
                          </button>
                        ))}
                      </div>
                      <Button onClick={completeExam} disabled={isLoading} className="w-full">
                        Complete Exam
                      </Button>
                    </div>
                  )}
                </div>

                {currentQuestion && (
                  <Card className="p-6">
                    <div className="mb-4">
                      <span className="text-sm text-gray-500">
                        Question {currentQuestion.question_number} of {selectedExam.total_questions}
                      </span>
                    </div>
                    
                    <h3 className="text-xl font-semibold mb-4">{currentQuestion.question}</h3>
                    
                    {selectedExam.status === 'in_progress' ? (
                      <div className="space-y-4">
                        <textarea
                          className="w-full p-3 border rounded-lg dark:bg-gray-800 dark:border-gray-700"
                          rows={4}
                          placeholder="Type your answer here..."
                          value={answers[currentQuestion.id] || ''}
                          onChange={(e) => setAnswers(prev => ({ ...prev, [currentQuestion.id]: e.target.value }))}
                        />
                        <Button
                          onClick={() => submitAnswer(currentQuestion.id, answers[currentQuestion.id] || '')}
                          disabled={isSubmitting || !answers[currentQuestion.id]}
                          className="w-full"
                        >
                          Submit Answer
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                            Your Answer:
                          </label>
                          <p className="mt-1 p-3 bg-gray-50 dark:bg-gray-800 rounded">
                            {currentQuestion.user_answer || 'No answer provided'}
                          </p>
                        </div>
                        
                        {currentQuestion.is_correct !== undefined && (
                          <div className={`p-4 rounded-lg flex items-center gap-2 ${
                            currentQuestion.is_correct
                              ? 'bg-green-50 dark:bg-green-900/20'
                              : 'bg-red-50 dark:bg-red-900/20'
                          }`}>
                            {currentQuestion.is_correct ? (
                              <CheckCircle2 className="w-5 h-5 text-green-600" />
                            ) : (
                              <XCircle className="w-5 h-5 text-red-600" />
                            )}
                            <span className={currentQuestion.is_correct ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'}>
                              {currentQuestion.is_correct ? 'Correct' : 'Incorrect'}
                            </span>
                          </div>
                        )}
                        
                        {currentQuestion.feedback && (
                          <div>
                            <label className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                              Feedback:
                            </label>
                            <p className="mt-1 p-3 bg-blue-50 dark:bg-blue-900/20 rounded">
                              {currentQuestion.feedback}
                            </p>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="flex justify-between mt-6">
                      <Button
                        variant="outline"
                        onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
                        disabled={currentQuestionIndex === 0}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setCurrentQuestionIndex(Math.min(selectedExam.questions.length - 1, currentQuestionIndex + 1))}
                        disabled={currentQuestionIndex === selectedExam.questions.length - 1}
                      >
                        Next
                      </Button>
                    </div>
                  </Card>
                )}
              </div>
            ) : (
              <Card className="p-12 text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-500">Select an exam to get started</p>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

