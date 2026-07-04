import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Heart } from 'lucide-react'
import { register } from '../services/api'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const [form, setForm] = useState({ name:'', email:'', password:'', date_of_birth:'' })
  const [loading, setLoading] = useState(false)
  const { loginUser } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await register(form)
      loginUser(data)
      navigate('/dashboard')
      toast.success(`Welcome to She Check, ${data.name}!`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 to-mauve-50 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 text-plum">
            <Heart size={28} fill="currentColor" className="text-rose-500" />
            <span className="font-display text-3xl">She Check</span>
          </Link>
          <p className="text-gray-500 mt-2">Create your account</p>
        </div>
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { label:'Full name',      key:'name',          type:'text',     placeholder:'Sneha' },
              { label:'Email',          key:'email',         type:'email',    placeholder:'you@example.com' },
              { label:'Password',       key:'password',      type:'password', placeholder:'••••••••' },
              { label:'Date of birth',  key:'date_of_birth', type:'date',     placeholder:'' },
            ].map(({ label, key, type, placeholder }) => (
              <div key={key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input type={type} className="input" placeholder={placeholder}
                  value={form[key]} onChange={e => setForm({...form, [key]: e.target.value})}
                  required={key !== 'date_of_birth'} />
              </div>
            ))}
            <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>
          <p className="text-center text-sm text-gray-500 mt-4">
            Already have an account? <Link to="/login" className="text-rose-500 font-medium hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
