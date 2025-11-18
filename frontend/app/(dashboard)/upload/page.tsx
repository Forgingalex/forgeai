'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileText, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { apiUpload } from '@/lib/api'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [summary, setSummary] = useState('')

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('process_now', 'true')
      formData.append('simple_summary', 'false')

      const result = await apiUpload('/api/v1/files/upload', formData)
      setSummary(result.summary || '')
      setIsUploading(false)
    } catch (error: any) {
      alert(error.message)
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Upload & Summarize</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Upload PDFs or text files to extract insights and build your knowledge base.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Upload File</h2>
            
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center mb-4">
              <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer text-blue-600 hover:underline"
              >
                {file ? file.name : 'Click to select or drag and drop'}
              </label>
            </div>

            {file && (
              <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-md flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <span className="text-sm text-green-700 dark:text-green-400">
                  {file.name} selected
                </span>
              </div>
            )}

            <Button
              onClick={handleUpload}
              disabled={!file || isUploading}
              className="w-full"
            >
              {isUploading ? 'Uploading...' : 'Upload & Process'}
            </Button>
          </Card>

          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Summary</h2>
            {summary ? (
              <div className="prose dark:prose-invert max-w-none">
                <p className="whitespace-pre-wrap text-sm">{summary}</p>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Upload a file to see its summary here</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}

