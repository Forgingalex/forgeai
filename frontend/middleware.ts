import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value || 
                request.headers.get('authorization')?.replace('Bearer ', '')
  
  // Protect routes that require authentication
  const protectedRoutes = ['/chat', '/upload', '/memory']
  const isProtectedRoute = protectedRoutes.some(route => 
    request.nextUrl.pathname.startsWith(route)
  )
  
  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/chat/:path*', '/upload/:path*', '/memory/:path*']
}

