import { useState } from 'react'
import { logPeriod } from '../services/api'
import { Plus, Trash2, Calendar, Droplets, Zap } from 'lucide-react'
import toast from 'react-hot-toast'

const SYMPTOMS = ['Cramps', 'Headache', 'Bloating', 'Fatigue', 'Mood swings', 'Back pain', 'Heavy bleeding', 'Light bleeding', 'Normal bleeding', 'Nausea']

const PHASE_COLORS = {
  Menstrual:  'bg-rose-100 text-rose-700 border-rose-200',
  Follicular: 'bg-amber-100 text-amber-700 border-amber-200',
  Ovulatory:  'bg-mauve-100 text-mauve-700 border-mauve-200',
  Luteal:     'bg-sage-100 text-sage-600 border-sage-200',
}

function CycleEntry({ entry, index, onChange, onRemove }) {
  const toggle = (symptom) => {
    const syms = entry.symptoms.includes(symptom)
      ? entry.symptoms.filter(s => s !== symptom)
      : [...entry.symptoms, symptom]
    onChange(index, { ...entry, symptoms: syms })
  }
  return (
    <div className="card border border-rose-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-plum">Cycle {index + 1}</h3>
        {index > 0 && <button onClick={() => onRemove(index)} className="text-gray-400 hover:text-red-400 transition-colors"><Trash2 size={16} /></button>}
      </div>
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Start date</label>
          <input type="date" className="input text-sm" value={entry.start_date}
            onChange={e => onChange(index, {...entry, start_date: e.target.value})} required />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">End date</label>
          <input type="date" className="input text-sm" value={entry.end_date}
            onChange={e => onChange(index, {...entry, end_date: e.target.value})} />
        </div>
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-2">Symptoms</label>
        <div className="flex flex-wrap gap-2">
          {SYMPTOMS.map(s => (
            <button type="button" key={s} onClick={() => toggle(s)}
              className={`text-xs px-3 py-1 rounded-full border transition-all
                ${entry.symptoms.includes(s) ? 'bg-plum text-white border-plum' : 'bg-white text-gray-500 border-gray-200 hover:border-plum'}`}>
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function ResultCard({ result }) {
  const phaseClass = PHASE_COLORS[result.current_phase] || 'bg-gray-100 text-gray-700 border-gray-200'
  return (
    <div className="space-y-4">
      {/* Next period + phase */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card border border-rose-200 text-center">
          <Droplets className="mx-auto text-rose-400 mb-2" size={24} />
          <p className="text-xs text-gray-500 mb-1">Next period predicted</p>
          <p className="font-display text-2xl text-plum">{result.predicted_next_date}</p>
          <p className="text-xs text-gray-400 mt-1">Avg cycle: {result.avg_cycle_length} days</p>
        </div>
        <div className="card border text-center">
          <Zap className="mx-auto text-mauve-400 mb-2" size={24} />
          <p className="text-xs text-gray-500 mb-1">Current phase</p>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border ${phaseClass}`}>
            {result.current_phase}
          </span>
          <p className="text-xs text-gray-400 mt-2 leading-snug">{result.phase_description}</p>
        </div>
      </div>

      {/* Ovulation */}
      <div className="card border border-mauve-100">
        <div className="flex items-center gap-2 mb-2">
          <Calendar size={16} className="text-mauve-500" />
          <span className="text-sm font-medium text-plum">Ovulation window</span>
        </div>
        <p className="text-gray-600 text-sm">{result.ovulation_window.start} → {result.ovulation_window.end}</p>
      </div>

      {/* Advisories */}
      <div className="card border border-sage-100">
        <h3 className="font-medium text-plum mb-3 text-sm">Phase advisories</h3>
        <ul className="space-y-2">
          {result.advisories.map((a, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
              <span className="text-sage-500 mt-0.5">✓</span> {a}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default function PeriodPage() {
  const [entries, setEntries] = useState([{ start_date:'', end_date:'', symptoms:[] }])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const updateEntry = (i, val) => setEntries(entries.map((e, idx) => idx === i ? val : e))
  const removeEntry = (i) => setEntries(entries.filter((_, idx) => idx !== i))
  const addEntry    = () => setEntries([...entries, { start_date:'', end_date:'', symptoms:[] }])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (entries.length < 1) return toast.error('Add at least one cycle')
    setLoading(true)
    try {
      const { data } = await logPeriod({ cycle_entries: entries })
      setResult(data)
      toast.success('Cycle analysed!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to analyse cycle')
    } finally { setLoading(false) }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="font-display text-4xl text-plum mb-2">Period Tracker</h1>
        <p className="text-gray-500">Log your recent cycles to predict your next period and get personalised health advice.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {entries.map((entry, i) => (
          <CycleEntry key={i} entry={entry} index={i} onChange={updateEntry} onRemove={removeEntry} />
        ))}

        <button type="button" onClick={addEntry}
          className="flex items-center gap-2 text-rose-500 text-sm font-medium hover:text-rose-600 transition-colors">
          <Plus size={16} /> Add another cycle
        </button>

        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? 'Predicting…' : 'Predict my next period'}
        </button>
      </form>

      {result && <div className="mt-8"><ResultCard result={result} /></div>}
    </div>
  )
}
