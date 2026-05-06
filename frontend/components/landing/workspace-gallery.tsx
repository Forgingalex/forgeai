'use client'

import { useQuery } from '@tanstack/react-query'
import gsap from 'gsap'
import { ArrowLeft, ArrowRight, Bookmark, Sparkles } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect, useMemo, useRef, useState } from 'react'

import { apiGet } from '@/lib/api'
import { cn } from '@/lib/utils'

interface Workspace {
  id: number
  name: string
  description?: string | null
  created_at: string
}

const fallbackWorkspaces: Workspace[] = [
  {
    id: 0,
    name: 'Research Vault',
    description: 'Indexed papers, SIWES notes, and local references ready for retrieval.',
    created_at: new Date().toISOString(),
  },
  {
    id: 0,
    name: 'Exam Forge',
    description: 'Flashcards, mock exams, and summaries shaped into active recall sessions.',
    created_at: new Date().toISOString(),
  },
  {
    id: 0,
    name: 'Project Memory',
    description: 'Architecture decisions, code notes, and implementation trails for portfolio work.',
    created_at: new Date().toISOString(),
  },
]

function titleParts(name: string) {
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return [parts[0], 'WORKSPACE']
  return [parts.slice(0, -1).join(' '), parts[parts.length - 1]]
}

export function WorkspaceGallery() {
  const router = useRouter()
  const rootRef = useRef<HTMLDivElement>(null)
  const [active, setActive] = useState(0)

  const { data } = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => apiGet<Workspace[]>('/api/v1/workspaces/'),
    retry: false,
  })

  const workspaces = useMemo(() => {
    const real = data && data.length > 0 ? data : fallbackWorkspaces
    return real.slice(0, 6)
  }, [data])

  useEffect(() => {
    const root = rootRef.current
    if (!root) return

    const cards = root.querySelectorAll('.forge-gallery-card')
    const details = root.querySelector('.forge-gallery-details')
    const pagination = root.querySelector('.forge-gallery-pagination')
    const cover = root.querySelector('.forge-gallery-cover')

    gsap.set(cards, {
      opacity: 0,
      scale: 0.88,
      x: 120,
    })
    gsap.set(cards[active], {
      opacity: 1,
      scale: 1,
      x: 0,
      zIndex: 20,
    })
    gsap.to(cards, {
      opacity: (index) => (index === active ? 1 : 0.72),
      scale: (index) => (index === active ? 1 : 0.82),
      x: (index) => (index - active) * 168,
      y: (index) => (index === active ? 0 : 88),
      zIndex: (index) => (index === active ? 30 : 10 - Math.abs(index - active)),
      duration: 0.8,
      ease: 'sine.inOut',
      stagger: 0.04,
    })
    gsap.fromTo(details, { opacity: 0, x: -36 }, { opacity: 1, x: 0, duration: 0.55, ease: 'sine.out' })
    gsap.fromTo(pagination, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 0.55, ease: 'sine.out' })
    gsap.to(cover, { x: '110%', duration: 0.75, ease: 'sine.inOut' })
  }, [active, workspaces])

  const workspace = workspaces[active]
  const [titleOne, titleTwo] = titleParts(workspace.name)

  const move = (direction: 1 | -1) => {
    setActive((current) => (current + direction + workspaces.length) % workspaces.length)
  }

  const openWorkspace = () => {
    if (workspace.id > 0) router.push(`/chat?workspace=${workspace.id}`)
    else router.push('/chat')
  }

  return (
    <section ref={rootRef} className="relative min-h-screen overflow-hidden text-white">
      <div className="absolute inset-0 bg-[url('/forgeai_frontend.jpg')] bg-[length:560px_auto] bg-fixed bg-center opacity-80" />
      <div className="absolute inset-0 bg-[#020711]/80" />
      <div className="absolute left-0 right-0 top-0 z-30 h-1 bg-gradient-to-r from-cyan-200 via-amber-200 to-cyan-200" />

      <div className="forge-gallery-details absolute left-8 top-[24vh] z-20 max-w-[560px] md:left-14">
        <div className="mb-5 flex items-center gap-3 text-sm text-cyan-100/80">
          <span className="h-1 w-8 rounded-full bg-cyan-100" />
          Knowledge Workspace
        </div>
        <div className="overflow-hidden">
          <h1 className="font-['Arial_Narrow',Inter,sans-serif] text-6xl font-semibold uppercase leading-[0.95] tracking-normal md:text-8xl">
            {titleOne}
          </h1>
        </div>
        <div className="overflow-hidden">
          <h2 className="font-['Arial_Narrow',Inter,sans-serif] text-6xl font-semibold uppercase leading-[0.95] tracking-normal text-cyan-100 md:text-8xl">
            {titleTwo}
          </h2>
        </div>
        <p className="mt-6 max-w-xl text-base leading-7 text-slate-200/90">
          {workspace.description || 'A focused local knowledge set for retrieval, reasoning, and study workflows.'}
        </p>
        <div className="mt-8 flex items-center gap-4">
          <button
            className="grid h-10 w-10 place-items-center rounded-full border border-amber-200/30 bg-amber-200/20 text-amber-100 backdrop-blur-xl transition hover:bg-amber-200/30"
            aria-label="Pin workspace"
          >
            <Bookmark className="h-5 w-5 fill-current" />
          </button>
          <button
            onClick={openWorkspace}
            className="h-10 rounded-full border border-white/50 px-6 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:border-cyan-200 hover:text-cyan-100"
          >
            Open workspace
          </button>
        </div>
      </div>

      <div className="absolute bottom-[20vh] right-[9vw] z-10 h-[320px] w-[720px]">
        {workspaces.map((item, index) => {
          const [first, second] = titleParts(item.name)
          return (
            <button
              type="button"
              key={`${item.name}-${index}`}
              onClick={() => setActive(index)}
              className={cn(
                'forge-gallery-card absolute left-0 top-0 h-[300px] w-[210px] overflow-hidden rounded-[10px] border border-white/10 bg-[#07101d]/65 text-left shadow-[8px_12px_42px_rgba(0,0,0,0.58)] backdrop-blur-xl',
                active === index && 'ring-1 ring-cyan-200/50'
              )}
            >
              <div className="absolute inset-0 bg-[url('/forgeai_frontend.jpg')] bg-[length:360px_auto] bg-center opacity-80" />
              <div className="absolute inset-0 bg-gradient-to-b from-black/10 via-[#06101d]/40 to-black/80" />
              <div className="absolute bottom-5 left-4 right-4">
                <span className="mb-3 block h-1 w-8 rounded-full bg-white/80" />
                <p className="text-xs font-medium text-cyan-100/80">Workspace {index + 1}</p>
                <p className="mt-1 text-xl font-semibold uppercase leading-5">
                  {first}
                  <br />
                  <span className="text-amber-100">{second}</span>
                </p>
              </div>
            </button>
          )
        })}
      </div>

      <div className="forge-gallery-pagination absolute bottom-[10vh] right-[9vw] z-20 flex items-center gap-5">
        <button
          className="grid h-12 w-12 place-items-center rounded-full border border-white/30 text-white/80 transition hover:border-cyan-100 hover:text-cyan-100"
          onClick={() => move(-1)}
          aria-label="Previous workspace"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <button
          className="grid h-12 w-12 place-items-center rounded-full border border-white/30 text-white/80 transition hover:border-cyan-100 hover:text-cyan-100"
          onClick={() => move(1)}
          aria-label="Next workspace"
        >
          <ArrowRight className="h-5 w-5" />
        </button>
        <div className="h-px w-[260px] bg-white/20">
          <div
            className="h-px bg-amber-200 transition-all duration-500"
            style={{ width: `${((active + 1) / workspaces.length) * 100}%` }}
          />
        </div>
        <div className="grid h-12 w-12 place-items-center text-2xl font-bold">
          {String(active + 1).padStart(2, '0')}
        </div>
      </div>

      <div className="absolute left-8 top-8 z-20 flex items-center gap-3 md:left-14">
        <div className="grid h-10 w-10 place-items-center rounded-xl border border-cyan-200/30 bg-cyan-200/10 backdrop-blur-xl">
          <Sparkles className="h-5 w-5 text-cyan-100" />
        </div>
        <span className="text-xl font-semibold">ForgeAI</span>
      </div>
      <div className="forge-gallery-cover absolute inset-0 z-40 bg-white" />
    </section>
  )
}

