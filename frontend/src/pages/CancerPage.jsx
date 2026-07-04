import { useState } from 'react'
import { predictParameters, predictImage } from '../services/api'
import { Upload, FlaskConical, AlertCircle, CheckCircle2 } from 'lucide-react'
import toast from 'react-hot-toast'

const PARAMS = [
  { key:'radius_mean',            label:'Radius Mean',              placeholder:'e.g. 13.5' },
  { key:'texture_mean',           label:'Texture Mean',             placeholder:'e.g. 18.2' },
  { key:'perimeter_mean',         label:'Perimeter Mean',           placeholder:'e.g. 87.0' },
  { key:'area_mean',              label:'Area Mean',                placeholder:'e.g. 560'  },
  { key:'smoothness_mean',        label:'Smoothness Mean',          placeholder:'e.g. 0.09' },
  { key:'compactness_mean',       label:'Compactness Mean',         placeholder:'e.g. 0.08' },
  { key:'concavity_mean',         label:'Concavity Mean',           placeholder:'e.g. 0.05' },
  { key:'concave_points_mean',    label:'Concave Points Mean',      placeholder:'e.g. 0.03' },
  { key:'symmetry_mean',          label:'Symmetry Mean',            placeholder:'e.g. 0.17' },
  { key:'fractal_dimension_mean', label:'Fractal Dimension Mean',   placeholder:'e.g. 0.06' },
]

function ResultCard({ result }) {
  const isMalignant = result.prediction === 'Malignant'
  return (
    <div className={`rounded-3xl p-6 border-2 ${isMalignant ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
      <div className="flex items-center gap-3 mb-3">
        {isMalignant
          ? <AlertCircle className="text-red-500" size={28} />
          : <CheckCircle2 className="text-green-500" size={28} />}
        <div>
          <span className={isMalignant ? 'badge-malignant' : 'badge-benign'}>{result.prediction}</span>
          <span className="text-gray-500 text-sm ml-2">{(result.confidence * 100).toFixed(1)}% confidence</span>
        </div>
      </div>
      <p className="text-gray-700 text-sm leading-relaxed mb-3">{result.message}</p>
      <p className="text-gray-400 text-xs italic">{result.disclaimer}</p>
    </div>
  )
}

export default function CancerPage() {
  const [tab, setTab] = useState('params')
  const [params, setParams] = useState({})
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleParams = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = Object.fromEntries(Object.entries(params).map(([k,v]) => [k, parseFloat(v)]))
      const { data } = await predictParameters(payload)
      setResult(data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Prediction failed')
    } finally { setLoading(false) }
  }

  const handleImage = async (e) => {
    e.preventDefault()
    if (!file) return toast.error('Please select an image')
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const { data } = await predictImage(fd)
      setResult(data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Image analysis failed')
    } finally { setLoading(false) }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="font-display text-4xl text-plum mb-2">Cancer Detection</h1>
        <p className="text-gray-500">AI-powered breast cancer screening. Enter clinical parameters or upload a mammogram image.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 bg-white rounded-2xl p-1 shadow-soft w-fit">
        {[{ id:'params', label:'Clinical Parameters', icon: FlaskConical },
          { id:'image',  label:'Mammogram Image',     icon: Upload }].map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => { setTab(id); setResult(null) }}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all
              ${tab === id ? 'bg-plum text-white shadow' : 'text-gray-500 hover:text-plum'}`}>
            <Icon size={15} /> {label}
          </button>
        ))}
      </div>

      {/* Parameters form */}
      {tab === 'params' && (
        <div className="card">
          <form onSubmit={handleParams}>
            <div className="grid grid-cols-2 gap-4 mb-6">
              {PARAMS.map(({ key, label, placeholder }) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
                  <input type="number" step="any" className="input text-sm" placeholder={placeholder}
                    value={params[key] || ''} onChange={e => setParams({...params, [key]: e.target.value})} required />
                </div>
              ))}
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Analysing…' : 'Analyse Parameters'}
            </button>
          </form>
        </div>
      )}

      {/* Image form */}
      {tab === 'image' && (
        <div className="card">
          <form onSubmit={handleImage}>
            <label className="block w-full border-2 border-dashed border-rose-200 rounded-2xl p-10 text-center cursor-pointer hover:border-rose-400 hover:bg-rose-50 transition-all">
              <Upload className="mx-auto text-rose-300 mb-3" size={36} />
              <p className="text-gray-600 font-medium">{file ? file.name : 'Click to upload mammogram image'}</p>
              <p className="text-gray-400 text-sm mt-1">JPEG or PNG, max 10 MB</p>
              <input type="file" accept="image/jpeg,image/png" className="hidden"
                onChange={e => { setFile(e.target.files[0]); setResult(null) }} />
            </label>
            <button type="submit" disabled={loading || !file} className="btn-primary w-full mt-4">
              {loading ? 'Analysing image…' : 'Analyse Mammogram'}
            </button>
          </form>
        </div>
      )}

      {/* Result */}
      {result && <div className="mt-6"><ResultCard result={result} /></div>}
    </div>
  )
}
