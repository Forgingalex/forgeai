import { Navbar } from '@/components/layout/navbar'
import AuthGuard from '@/components/AuthGuard'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#030711] text-white">
        <Navbar />
        <main>{children}</main>
      </div>
    </AuthGuard>
  )
}
