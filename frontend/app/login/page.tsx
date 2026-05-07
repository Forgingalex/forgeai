'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Eye, EyeOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiPost } from '@/lib/api'
import { useAuth } from '@/lib/contexts/AuthContext'

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false)
  const router = useRouter()
  const { checkAuth } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (isSubmitting) return
    setError('')
    setIsSubmitting(true)

    if (!isLogin && password !== confirmPassword) {
      setError('Passkeys do not match')
      setIsSubmitting(false)
      return
    }

    try {
      if (!isLogin) {
        await apiPost('/api/v1/auth/register', {
          username,
          email,
          password,
          full_name: fullName,
        })
      }
      
      const body = new URLSearchParams({ username, password })
      
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body,
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error(isLogin ? 'Login failed' : 'Registration successful, but auto-login failed')
      }

      await checkAuth()
      router.push('/chat')
    } catch (err: any) {
      setError(err.message || 'An error occurred')
      setIsSubmitting(false)
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
            filter: 'blur(80px) brightness(0.2)',
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
            
            <motion.div layout className="relative">
              <Input
                type={showPassword ? "text" : "password"}
                placeholder="Passkey"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-black/50 border-white/10 text-white placeholder:text-gray-500 focus-visible:ring-[#ecad29] pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors hover:text-[#ecad29]"
                style={{ color: showPassword ? '#ecad29' : '#6b7280' }}
              >
                {showPassword ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              </button>
            </motion.div>
            
            <AnimatePresence mode="popLayout">
              {!isLogin && (
                <motion.div
                  initial={{ opacity: 0, x: -20, height: 0 }}
                  animate={{ opacity: 1, x: 0, height: 'auto' }}
                  exit={{ opacity: 0, x: -20, height: 0 }}
                  transition={{ duration: 0.3 }}
                  className="relative overflow-hidden"
                >
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Confirm Passkey"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required={!isLogin}
                    className="bg-black/50 border-white/10 text-white placeholder:text-gray-500 focus-visible:ring-[#ecad29]"
                  />
                </motion.div>
              )}
            </AnimatePresence>
            
            <motion.div layout className="flex justify-end pt-1">
              {isLogin && (
                <button
                  type="button"
                  onClick={() => setIsForgotModalOpen(true)}
                  className="text-xs text-gray-500 hover:text-[#ecad29] transition-colors"
                >
                  Forgot Passkey?
                </button>
              )}
            </motion.div>

            <motion.div layout className="pt-2">
              <Button 
                type="submit"
                disabled={isSubmitting}
                className="w-full text-black hover:bg-[#d99d25] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ backgroundColor: '#ecad29' }}
              >
                {isSubmitting ? 'Authenticating...' : (isLogin ? 'Open Workspace' : 'Initialize Session')}
              </Button>
            </motion.div>
          </form>

          <motion.div layout className="mt-6 text-center">
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin)
                setError('')
                setConfirmPassword('')
              }}
              className="text-sm text-gray-400 hover:text-[#ecad29] transition-colors"
            >
              {isLogin ? "No clearance? Initialize here" : 'Already authorized? Access Vault'}
            </button>
          </motion.div>
        </motion.div>
      </div>

      <AnimatePresence>
        {isForgotModalOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-sm rounded-2xl border border-white/10 p-6 shadow-2xl"
              style={{ backgroundColor: 'rgba(22, 22, 24, 0.9)' }}
            >
              <h2 className="text-xl font-bold text-white mb-2">Access Recovery</h2>
              <p className="text-sm text-gray-300 mb-6">
                Password recovery is restricted. Please contact the System Administrator to reset your forged identity.
              </p>
              <Button
                onClick={() => setIsForgotModalOpen(false)}
                className="w-full text-black hover:bg-[#d99d25] transition-colors"
                style={{ backgroundColor: '#ecad29' }}
              >
                Acknowledge
              </Button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
