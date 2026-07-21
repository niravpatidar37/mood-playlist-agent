import { useEffect, useState } from 'react'
import type { Playlist, Mode, ProgressEvent } from './types'
import { fetchModels, generatePlaylist, streamPlaylist } from './api/vibeforge'
import MoodForm from './components/MoodForm'
import PlaylistCard from './components/PlaylistCard'
import ProgressLog from './components/ProgressLog'
import FeedbackPanel from './components/FeedbackPanel'
import './index.css'

export default function App() {
  const [models, setModels] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [playlist, setPlaylist] = useState<Playlist | null>(null)
  const [events, setEvents] = useState<ProgressEvent[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchModels().then(setModels).catch(() => setModels(['llama-3.3-70b-versatile']))
  }, [])

  const handleSubmit = async (params: {
    mood: string; context: string; seed: string
    model: string; mode: Mode; spotify_enrich: boolean
  }) => {
    setLoading(true)
    setPlaylist(null)
    setEvents([])
    setError(null)

    if (params.mode === 'agentic') {
      streamPlaylist({
        ...params,
        onEvent: (evt) => setEvents(prev => [...prev, evt]),
        onPlaylist: (pl) => { setPlaylist(pl); setLoading(false) },
        onError: (msg) => { setError(msg); setLoading(false) },
      })
    } else {
      try {
        const pl = await generatePlaylist(params as any)
        setPlaylist(pl)
      } catch (e: any) {
        setError(e.message ?? 'Something went wrong')
      } finally {
        setLoading(false)
      }
    }
  }

  const handleFeedback = async (loved: any[], disliked: any[]) => {
    await fetch('http://localhost:8000/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ loved, disliked }),
    }).catch(() => {})
  }

  return (
    <div className="min-h-screen bg-[#0f0f1a]">
      <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">

        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-purple-400 via-pink-400 to-amber-400 bg-clip-text text-transparent">
            ⚡ VibeForge
          </h1>
          <p className="text-slate-500 mt-1 text-sm">Your mood. Forged into sound.</p>
        </div>

        {/* Form */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
          <MoodForm models={models} loading={loading} onSubmit={handleSubmit} />
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-400 text-sm">
            ❌ {error}
          </div>
        )}

        {/* Agentic progress */}
        {events.length > 0 && <ProgressLog events={events} />}

        {/* Playlist result */}
        {playlist && (
          <>
            <PlaylistCard playlist={playlist} />
            <FeedbackPanel tracks={playlist.tracks} onSave={handleFeedback} />
          </>
        )}
      </div>
    </div>
  )
}
