import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Microscope, MessageCircle, Calendar, ArrowRight, Heart } from 'lucide-react'

const cards = [
  { to:'/cancer',  icon: Microscope,    color:'from-rose-400 to-rose-600',   title:'Cancer Detection',  desc:'Analyse clinical parameters or upload a mammogram image for AI-powered screening.' },
  { to:'/chatbot', icon: MessageCircle, color:'from-mauve-400 to-mauve-600', title:'Health Chatbot',    desc:'Ask questions about women\'s health and get personalised, empathetic guidance.' },
  { to:'/period',  icon: Calendar,      color:'from-sage-400 to-sage-600',   title:'Period Tracker',    desc:'Log your cycles and get your next period prediction with phase-specific advice.' },
]

export default function DashboardPage() {
  const { user } = useAuth()
  return (
    <div>
      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <Heart size={20} className="text-rose-400" fill="currentColor" />
          <span className="text-rose-400 font-medium text-sm">She Check</span>
        </div>
        <h1 className="font-display text-4xl text-plum">Good to see you, {user?.name}.</h1>
        <p className="text-gray-500 mt-2">Your personal women's health companion. What would you like to check today?</p>
      </div>

      {/* Feature cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {cards.map(({ to, icon: Icon, color, title, desc }) => (
          <Link key={to} to={to}
            className="card group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 flex flex-col">
            <div className={`inline-flex p-3 rounded-2xl bg-gradient-to-br ${color} text-white mb-4 w-fit`}>
              <Icon size={22} />
            </div>
            <h2 className="font-display text-xl text-plum mb-2">{title}</h2>
            <p className="text-gray-500 text-sm leading-relaxed flex-1">{desc}</p>
            <div className="flex items-center gap-1 text-rose-500 text-sm font-medium mt-4 group-hover:gap-2 transition-all">
              Open <ArrowRight size={14} />
            </div>
          </Link>
        ))}
      </div>

      {/* Disclaimer */}
      <div className="mt-10 bg-amber-50 border border-amber-200 rounded-2xl px-5 py-4 text-amber-800 text-sm">
        <strong>Medical disclaimer:</strong> She Check is an AI-assisted screening tool for informational purposes only.
        Always consult a qualified healthcare professional for diagnosis and treatment.
      </div>
    </div>
  )
}
