import { Outlet } from 'react-router-dom'
import { EmailSidebar } from './EmailSidebar'

export function Layout() {
  return (
    <div className="flex h-screen bg-background">
      <EmailSidebar />
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}
