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
    <nav className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/chat" className="flex items-center gap-2 px-4">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
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
                        ? "border-blue-500 text-gray-900 dark:text-gray-100"
                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
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
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}

