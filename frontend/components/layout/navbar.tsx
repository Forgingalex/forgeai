'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Sparkles, MessageSquare, Upload, Brain, LogOut, BookOpen, FileText, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function Navbar() {
  const pathname = usePathname()

  const handleLogout = () => {
    localStorage.removeItem('token')
    // Clear cookie as well
    document.cookie = 'token=; path=/; max-age=0; SameSite=Lax'
    window.location.href = '/login'
  }

  const navItems = [
    { href: '/chat', label: 'Chat', icon: MessageSquare },
    { href: '/upload', label: 'Upload', icon: Upload },
    { href: '/memory', label: 'Memory', icon: Brain },
    { href: '/flashcards', label: 'Flashcards', icon: BookOpen },
    { href: '/exams', label: 'Exams', icon: FileText },
    { href: '/study-planner', label: 'Planner', icon: Calendar },
  ]

  return (
    <nav className="border-b border-white/10 bg-[#030711]/80 text-white backdrop-blur-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/chat" className="flex items-center gap-2 px-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-200/30 bg-cyan-200/10">
                <Sparkles className="w-5 h-5 text-cyan-100" />
              </div>
              <span className="bg-gradient-to-r from-cyan-100 to-amber-100 bg-clip-text text-xl font-bold text-transparent">
                ForgeAI
              </span>
            </Link>
            
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors",
                      isActive
                        ? "border-cyan-200 text-cyan-100"
                        : "border-transparent text-slate-400 hover:border-white/30 hover:text-slate-100"
                    )}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </Link>
                )
              })}
            </div>
          </div>
          
          <div className="flex items-center">
            <Button variant="ghost" size="sm" onClick={handleLogout} className="text-slate-300 hover:text-white">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}
