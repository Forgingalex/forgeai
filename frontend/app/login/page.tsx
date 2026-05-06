'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiPost } from '@/lib/api'
import { useAuth } from '@/lib/contexts/AuthContext'

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()
  const { checkAuth } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      if (!isLogin) {
        await apiPost('/api/v1/auth/register', {
          username,
          email,
          password,
          full_name: fullName,
        })
      }
      
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/login`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error(isLogin ? 'Login failed' : 'Registration successful, but auto-login failed')
      }

      await checkAuth()
      router.push('/chat')
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    }
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#0a0a0b]">
      {/* Background with Parallax Scale & Deep Blur */}
      <motion.div 
        className="absolute inset-0 z-0"
        initial={{ scale: 1.1 }}
        animate={{ scale: 1 }}
        transition={{ duration: 10, ease: "easeOut" }}
      >
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ 
            backgroundImage: 'url(/forgeai_frontend.jpg)',
            filter: 'blur(60px) brightness(0.25)',
            transform: 'scale(1.2)'
          }}
        />
      </motion.div>

      <div className="relative z-10 w-full max-w-md p-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="backdrop-blur-xl rounded-2xl border border-white/10 p-8 shadow-2xl"
          style={{ backgroundColor: 'rgba(22, 22, 24, 0.7)' }}
        >
          <div className="flex flex-col items-center gap-3 mb-8">
            <motion.div 
              whileHover={{ rotate: 180 }}
              transition={{ duration: 0.5 }}
              className="w-12 h-12 rounded-xl flex items-center justify-center border border-[#ecad29]/30"
              style={{ backgroundColor: 'rgba(236, 173, 41, 0.1)' }}
            >
              <Sparkles className="w-6 h-6" style={{ color: '#ecad29' }} />
            </motion.div>
            <h1 className="text-3xl font-bold tracking-tight text-white">
              ForgeAI
            </h1>
            <p className="text-sm text-gray-400">
              {isLogin ? 'Enter the Research Vault' : 'Initialize your clearance'}
            </p>
          </div>

          <AnimatePresence mode="wait">
            {error && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-6 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-sm text-red-200 text-center"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="space-y-4">
            <AnimatePresence mode="popLayout">
              {!isLogin && (
                <motion.div
                  initial={{ opacity: 0, x: -20, height: 0 }}
                  animate={{ opacity: 1, x: 0, height: 'auto' }}
                  exit={{ opacity: 0, x: -20, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4 overflow-hidden"
                >
                  <Input
                    type="text"
                    placeholder="Full Name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required={!isLogin}
                    className="bg-black/50 border-white/10 text-white placeholder:text-gray-500 focus-visible:ring-[#ecad29]"
                  />
                  <Input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required={!isLogin}
                    className="bg-black/50 border-white/10 text-white placeholder:text-gray-500 focus-visible:ring-[#ecad29]"
                  />
                </motion.div>
              )}
            </AnimatePresence>
            
            <motion.div layout>
              <Input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="bg-black/50 border-white/10 text-white placeholder:text-gray-500 focus-visible:ring-[#ecad29]"
              />
            </motion.div>
            
            <motion.div layout>
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-black/50 border-white/10 text-white placeholder:text-gray-500 focus-visible:ring-[#ecad29]"
              />
            </motion.div>
            
            <motion.div layout className="pt-2">
              <Button 
                type="submit" 
                className="w-full text-black hover:bg-[#d99d25] transition-colors"
                style={{ backgroundColor: '#ecad29' }}
              >
                {isLogin ? 'Access Vault' : 'Request Access'}
              </Button>
            </motion.div>
          </form>

          <motion.div layout className="mt-6 text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-sm text-gray-400 hover:text-[#ecad29] transition-colors"
            >
              {isLogin ? "No clearance? Initialize here" : 'Already authorized? Access Vault'}
            </button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}
