import type { Playlist } from '../types'
import TrackTable from './TrackTable'

interface Props {
  playlist: Playlist
}

const ENERGY_STYLE = {
  low:    'bg-green-500/15 text-green-400 border-green-500/30',
  medium: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  high:   'bg-red-500/15   text-red-400   border-red-500/30',
}

const ENERGY_LABEL = { low: '⬇ LOW', medium: '⚡ MEDIUM', high: '🔥 HIGH' }

export default function PlaylistCard({ playlist: pl }: Props) {
  return (
    <div className="rounded-2xl border border-purple-500/30 bg-gradient-to-br from-slate-900 to-slate-800 p-6 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">{pl.name}</h2>
          <p className="text-slate-400 text-sm mt-1 italic">{pl.mood_summary}</p>
        </div>
        <span className={`shrink-0 px-3 py-1 rounded-full text-xs font-bold border ${ENERGY_STYLE[pl.energy_level]}`}>
          {ENERGY_LABEL[pl.energy_level]}
        </span>
      </div>

      {/* Vibe tags */}
      <div className="flex flex-wrap gap-2">
        {pl.vibe_tags.map(tag => (
          <span key={tag} className="px-3 py-0.5 rounded-full text-xs bg-purple-500/15 text-purple-300 border border-purple-500/25">
            #{tag}
          </span>
        ))}
      </div>

      {/* Genres */}
      <p className="text-xs text-slate-500">
        Genres: {pl.genres.join(' · ')}
      </p>

      {/* Track table */}
      <TrackTable tracks={pl.tracks} />
    </div>
  )
}
