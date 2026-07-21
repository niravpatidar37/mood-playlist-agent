import { useState } from 'react'
import type { Track } from '../types'

interface Props {
  tracks: Track[]
  onSave: (loved: Track[], disliked: Track[]) => void
}

export default function FeedbackPanel({ tracks, onSave }: Props) {
  const [loved, setLoved] = useState<Set<number>>(new Set())
  const [disliked, setDisliked] = useState<Set<number>>(new Set())
  const [saved, setSaved] = useState(false)

  const toggle = (set: Set<number>, setFn: (s: Set<number>) => void, other: Set<number>, setOther: (s: Set<number>) => void, i: number) => {
    const next = new Set(set)
    if (next.has(i)) { next.delete(i) } else { next.add(i); other.delete(i); setOther(new Set(other)) }
    setFn(next)
  }

  const handleLoveAll = () => {
    setLoved(new Set(tracks.map((_, i) => i)))
    setDisliked(new Set())
  }

  const handleClear = () => { setLoved(new Set()); setDisliked(new Set()) }

  const handleSave = () => {
    onSave(
      tracks.filter((_, i) => loved.has(i)),
      tracks.filter((_, i) => disliked.has(i)),
    )
    setSaved(true)
  }

  if (saved) {
    return (
      <div className="rounded-xl border border-green-500/30 bg-green-500/10 px-4 py-3 text-green-400 text-sm font-medium">
        ✅ Feedback saved — your next playlist will reflect your taste.
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-purple-300">📊 Rate this playlist</p>
        <div className="flex gap-2">
          <button onClick={handleLoveAll} className="px-3 py-1 text-xs rounded-lg bg-pink-500/20 text-pink-300 border border-pink-500/30 hover:bg-pink-500/30 transition">
            ♥ Love all
          </button>
          <button onClick={handleClear} className="px-3 py-1 text-xs rounded-lg bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10 transition">
            Clear
          </button>
        </div>
      </div>

      <div className="space-y-1">
        {tracks.map((t, i) => (
          <div key={i} className="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-white/5 transition">
            <span className="text-sm text-slate-300">
              <span className="text-slate-500 mr-2">{i + 1}.</span>
              {t.title} <span className="text-slate-500">— {t.artist}</span>
            </span>
            <div className="flex gap-2 shrink-0">
              <button
                onClick={() => toggle(loved, setLoved, disliked, setDisliked, i)}
                className={`w-7 h-7 rounded-full text-sm border transition ${loved.has(i) ? 'bg-pink-500/30 border-pink-500/50 text-pink-300' : 'border-white/10 text-slate-600 hover:border-pink-500/50 hover:text-pink-400'}`}
              >♥</button>
              <button
                onClick={() => toggle(disliked, setDisliked, loved, setLoved, i)}
                className={`w-7 h-7 rounded-full text-sm border transition ${disliked.has(i) ? 'bg-red-500/20 border-red-500/40 text-red-400' : 'border-white/10 text-slate-600 hover:border-red-500/40 hover:text-red-400'}`}
              >✕</button>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={handleSave}
        disabled={loved.size === 0 && disliked.size === 0}
        className="w-full py-2 rounded-xl text-sm font-semibold bg-purple-600 hover:bg-purple-500 disabled:opacity-30 disabled:cursor-not-allowed transition"
      >
        💾 Save Feedback
      </button>
    </div>
  )
}
