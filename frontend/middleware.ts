import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(_request: NextRequest) {
  // Auth protection is handled client-side by AuthGuard.
  // The access_token cookie is scoped to the API domain (hf.space),
  // so it is invisible to the Vercel edge. Any server-side cookie
  // check here would cause an infinite redirect loop.
  return NextResponse.next()
}

export const config = {
  matcher: ['/chat/:path*', '/upload/:path*', '/memory/:path*']
}
