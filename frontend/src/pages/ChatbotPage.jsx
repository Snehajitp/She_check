import { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../services/api'
import { Send, Bot, User } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ChatbotPage() {
  const [messages, setMessages] = useState([{
    role: 'model',
    content: "Hi! I'm your She Check health assistant 💗 I'm here to answer your questions about women's health — from menstrual health to hormones, fertility, and more. What's on your mind today?"
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim()) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    try {
      const { data } = await sendMessage({ message: userMsg, session_id: sessionId })
      setSessionId(data.session_id)
      setMessages(prev => [...prev, { role: 'model', content: data.reply }])
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to get response')
      setMessages(prev => [...prev, { role: 'model', content: 'Sorry, I encountered an error. Please try again.' }])
    } finally { setLoading(false) }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-6">
        <h1 className="font-display text-4xl text-plum mb-2">Health Chat</h1>
        <p className="text-gray-500">Ask anything about women's health — I'm here to help.</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
              ${msg.role === 'user' ? 'bg-plum text-white' : 'bg-rose-100 text-rose-500'}`}>
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className={`max-w-[75%] px-4 py-3 rounded-3xl text-sm leading-relaxed
              ${msg.role === 'user'
                ? 'bg-plum text-white rounded-tr-sm'
                : 'bg-white text-gray-700 shadow-soft rounded-tl-sm'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-rose-100 text-rose-500 flex items-center justify-center flex-shrink-0">
              <Bot size={14} />
            </div>
            <div className="bg-white shadow-soft rounded-3xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1 items-center h-4">
                {[0,1,2].map(i => (
                  <div key={i} className="w-2 h-2 bg-rose-300 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="flex gap-3 bg-white rounded-2xl shadow-soft p-2">
        <input type="text" className="flex-1 px-4 py-2 text-sm bg-transparent outline-none placeholder:text-gray-400"
          placeholder="Ask about your health…" value={input}
          onChange={e => setInput(e.target.value)} disabled={loading} />
        <button type="submit" disabled={loading || !input.trim()}
          className="bg-plum text-white p-3 rounded-xl hover:bg-plum-light transition-colors disabled:opacity-40">
          <Send size={16} />
        </button>
      </form>

      <p className="text-center text-xs text-gray-400 mt-2">
        For informational purposes only. Always consult a healthcare professional.
      </p>
    </div>
  )
}
