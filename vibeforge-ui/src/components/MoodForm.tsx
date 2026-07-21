import { useState } from 'react'
import type { Mode } from '../types'

interface Props {
  models: string[]
  loading: boolean
  onSubmit: (params: {
    mood: string
    context: string
    seed: string
    model: string
    mode: Mode
    spotify_enrich: boolean
  }) => void
}

const MODES: { value: Mode; label: string; desc: string }[] = [
  { value: 'fast',    label: 'Fast',    desc: 'Single agent, ~5s' },
  { value: 'deep',    label: 'Deep',    desc: 'Mood Analyst → Curator, ~10s' },
  { value: 'agentic', label: 'Agentic', desc: 'LangGraph + Critic loop, ~20s' },
]

export default function MoodForm({ models, loading, onSubmit }: Props) {
  const [mood, setMood] = useState('')
  const [context, setContext] = useState('')
  const [seed, setSeed] = useState('')
  const [model, setModel] = useState(models[0] ?? '')
  const [mode, setMode] = useState<Mode>('fast')
  const [spotify, setSpotify] = useState(true)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!mood.trim()) return
    onSubmit({ mood, context, seed, model, mode, spotify_enrich: spotify })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Mood input */}
      <div>
        <label className="block text-sm font-medium text-purple-300 mb-1">
          How are you feeling?
        </label>
        <textarea
          value={mood}
          onChange={e => setMood(e.target.value)}
          rows={3}
          placeholder="e.g. birthday celebration, high energy party vibes…"
          className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-3 text-sm text-slate-200 placeholder-slate-500 resize-none focus:outline-none focus:border-purple-500 transition"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Seed track */}
        <div>
          <label className="block text-sm font-medium text-purple-300 mb-1">
            🎯 Seed track <span className="text-slate-500 font-normal">(optional)</span>
          </label>
          <input
            value={seed}
            onChange={e => setSeed(e.target.value)}
            placeholder="e.g. Blinding Lights by The Weeknd"
            className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 transition"
          />
        </div>

        {/* Extra context */}
        <div>
          <label className="block text-sm font-medium text-purple-300 mb-1">
            Extra context <span className="text-slate-500 font-normal">(optional)</span>
          </label>
          <input
            value={context}
            onChange={e => setContext(e.target.value)}
            placeholder="e.g. rainy evening, studying"
            className="w-full rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 transition"
          />
        </div>
      </div>

      {/* Mode selector */}
      <div>
        <label className="block text-sm font-medium text-purple-300 mb-2">Generation mode</label>
        <div className="grid grid-cols-3 gap-2">
          {MODES.map(m => (
            <button
              key={m.value}
              type="button"
              onClick={() => setMode(m.value)}
              className={`rounded-xl border px-3 py-2 text-left transition ${
                mode === m.value
                  ? 'border-purple-500 bg-purple-500/20 text-purple-200'
                  : 'border-white/10 bg-white/5 text-slate-400 hover:border-purple-500/50'
              }`}
            >
              <div className="text-sm font-semibold">{m.label}</div>
              <div className="text-xs mt-0.5 opacity-70">{m.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-6">
        {/* Model selector */}
        <div className="flex-1">
          <label className="block text-sm font-medium text-purple-300 mb-1">LLM model</label>
          <select
            value={model}
            onChange={e => setModel(e.target.value)}
            className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-purple-500"
          >
            {models.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>

        {/* Spotify toggle */}
        <label className="flex items-center gap-2 cursor-pointer mt-5">
          <input
            type="checkbox"
            checked={spotify}
            onChange={e => setSpotify(e.target.checked)}
            className="w-4 h-4 accent-purple-500"
          />
          <span className="text-sm text-slate-400">Spotify links</span>
        </label>
      </div>

      <button
        type="submit"
        disabled={!mood.trim() || loading}
        className="w-full rounded-xl py-3 font-semibold text-white bg-purple-600 hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed transition"
      >
        {loading ? 'Forging your playlist…' : '✨ Generate Playlist'}
      </button>
    </form>
  )
}
