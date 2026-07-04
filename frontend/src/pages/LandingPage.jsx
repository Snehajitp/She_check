import { Link } from 'react-router-dom'
import { Heart, Microscope, MessageCircle, Calendar, ArrowRight } from 'lucide-react'

const features = [
  { icon: Microscope,    color: 'bg-rose-100 text-rose-600',   title: 'Cancer Detection',    desc: 'AI-powered breast cancer screening via clinical parameters or mammogram image analysis.' },
  { icon: MessageCircle, color: 'bg-mauve-100 text-mauve-600', title: 'Health Chatbot',       desc: 'Ask anything about women\'s health — get empathetic, evidence-based answers 24/7.' },
  { icon: Calendar,      color: 'bg-sage-100 text-sage-600',   title: 'Period Tracker',       desc: 'Log your cycles, predict your next period, and get personalised phase advisories.' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 via-white to-mauve-50">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-5 max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <Heart className="text-rose-500" size={24} fill="currentColor" />
          <span className="font-display text-2xl text-plum">She Check</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-plum font-medium hover:text-plum-light transition-colors">Sign in</Link>
          <Link to="/register" className="btn-primary text-sm py-2 px-5">Get started</Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 bg-rose-100 text-rose-700 px-4 py-2 rounded-full text-sm font-medium mb-8">
          <Heart size={14} fill="currentColor" /> Women's health, powered by AI
        </div>
        <h1 className="font-display text-6xl text-plum leading-tight mb-6">
          Your health.<br />
          <span className="italic text-rose-500">Your power.</span>
        </h1>
        <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          She Check brings together cancer screening, a personal health assistant,
          and cycle tracking — all in one compassionate platform built for women.
        </p>
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Link to="/register" className="btn-primary flex items-center gap-2 text-base py-4 px-8">
            Start for free <ArrowRight size={18} />
          </Link>
          <Link to="/login" className="btn-secondary text-base py-4 px-8">Sign in</Link>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 pb-24">
        <div className="grid md:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, color, title, desc }) => (
            <div key={title} className="card hover:shadow-lg transition-shadow duration-300">
              <div className={`inline-flex p-3 rounded-2xl ${color} mb-4`}>
                <Icon size={22} />
              </div>
              <h3 className="font-display text-xl text-plum mb-2">{title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-8 text-gray-400 text-sm border-t border-rose-100">
        She Check is a screening aid only — always consult a healthcare professional for medical advice.
      </footer>
    </div>
  )
}
