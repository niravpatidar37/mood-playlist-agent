import type { Track } from '../types'

interface Props {
  tracks: Track[]
}

export default function TrackTable({ tracks }: Props) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-purple-400 uppercase tracking-wider border-b border-white/10">
            <th className="pb-2 pr-3 w-8">#</th>
            <th className="pb-2 pr-3">Title</th>
            <th className="pb-2 pr-3">Artist</th>
            <th className="pb-2 pr-3">Genre</th>
            <th className="pb-2 pr-3 text-right">BPM</th>
            <th className="pb-2">Links</th>
          </tr>
        </thead>
        <tbody>
          {tracks.map((t, i) => (
            <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition">
              <td className="py-2.5 pr-3 text-slate-500">{i + 1}</td>
              <td className="py-2.5 pr-3 font-semibold text-slate-200">{t.title}</td>
              <td className="py-2.5 pr-3 text-slate-400">{t.artist}</td>
              <td className="py-2.5 pr-3 text-amber-400 text-xs">{t.genre}</td>
              <td className="py-2.5 pr-3 text-right text-slate-500">{t.bpm ?? '—'}</td>
              <td className="py-2.5 flex gap-2">
                {t.spotify_search_url && (
                  <a
                    href={t.spotify_search_url}
                    target="_blank"
                    rel="noreferrer"
                    className="px-2 py-0.5 rounded text-xs font-semibold bg-green-500/15 text-green-400 border border-green-500/30 hover:bg-green-500/25 transition"
                  >
                    Spotify
                  </a>
                )}
                {t.youtube_search_url && (
                  <a
                    href={t.youtube_search_url}
                    target="_blank"
                    rel="noreferrer"
                    className="px-2 py-0.5 rounded text-xs font-semibold bg-red-500/15 text-red-400 border border-red-500/30 hover:bg-red-500/25 transition"
                  >
                    YouTube
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
