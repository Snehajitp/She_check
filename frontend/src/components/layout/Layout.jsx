import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Heart, Microscope, MessageCircle, Calendar, LogOut, Menu, X } from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { to: '/dashboard', icon: Heart,         label: 'Dashboard' },
  { to: '/cancer',    icon: Microscope,     label: 'Cancer Check' },
  { to: '/chatbot',   icon: MessageCircle,  label: 'Health Chat' },
  { to: '/period',    icon: Calendar,       label: 'Period Tracker' },
]

export default function Layout() {
  const { user, logoutUser } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  const handleLogout = () => { logoutUser(); navigate('/') }

  return (
    <div className="min-h-screen flex bg-rose-50">
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-plum flex flex-col transform transition-transform duration-300
        ${open ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:flex`}>
        {/* Logo */}
        <div className="px-6 py-8 border-b border-plum-light">
          <h1 className="font-display text-2xl text-white">She Check</h1>
          <p className="text-rose-200 text-sm mt-1">Hi, {user?.name} 👋</p>
        </div>
        {/* Nav */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink key={to} to={to} onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all duration-200
                ${isActive ? 'bg-white/20 text-white' : 'text-rose-200 hover:bg-white/10 hover:text-white'}`
              }>
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        {/* Logout */}
        <div className="px-4 py-6 border-t border-plum-light">
          <button onClick={handleLogout}
            className="flex items-center gap-3 px-4 py-3 rounded-2xl text-rose-200 hover:bg-white/10 hover:text-white text-sm font-medium w-full transition-all">
            <LogOut size={18} /> Sign out
          </button>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-30 bg-plum px-4 py-4 flex items-center justify-between">
        <h1 className="font-display text-xl text-white">She Check</h1>
        <button onClick={() => setOpen(!open)} className="text-white">
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
      {open && <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={() => setOpen(false)} />}

      {/* Main */}
      <main className="flex-1 lg:ml-0 pt-16 lg:pt-0 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
