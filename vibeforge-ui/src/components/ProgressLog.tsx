import type { ProgressEvent } from '../types'

interface Props {
  events: ProgressEvent[]
}

const NODE_ICON: Record<string, string> = {
  analyse_mood:      '🔍',
  curate_playlist:   '🎵',
  critique_playlist: '🎯',
  increment_attempts:'🔄',
  finalise:          '✨',
  done:              '✅',
  error:             '❌',
}

function eventLabel(evt: ProgressEvent): string {
  const d = evt.data
  switch (evt.node) {
    case 'analyse_mood':
      return d?.emotion
        ? `Mood Analyst — ${d.emotion}, ${d.energy} energy, BPM ${d.bpm_range}${d.occasion ? ` · occasion: ${d.occasion}` : ''}`
        : 'Mood Analyst — reading your vibe…'
    case 'curate_playlist':
      return d?.attempt && d.attempt > 0
        ? `Music Curator — refining playlist (attempt ${d.attempt + 1}/3)…`
        : 'Music Curator — building your 10-track playlist…'
    case 'critique_playlist':
      return d?.score !== undefined
        ? `Critic — ${d.score}/10 ${d.score >= 7 ? '✅ accepted' : '⚠️ needs refinement'}`
        : 'Critic — evaluating quality…'
    case 'finalise':
      return 'Finalising — enriching track links…'
    case 'done':
      return 'Playlist ready!'
    case 'error':
      return `Error — ${(evt as any).message ?? 'something went wrong'}`
    default:
      return evt.node
  }
}

export default function ProgressLog({ events }: Props) {
  if (events.length === 0) return null

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 space-y-2">
      <p className="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2">
        Pipeline progress
      </p>
      {events.map((evt, i) => (
        <div key={i} className="flex items-start gap-2 text-sm">
          <span className="mt-0.5 shrink-0">{NODE_ICON[evt.node] ?? '•'}</span>
          <span className={evt.node === 'error' ? 'text-red-400' : 'text-slate-300'}>
            {eventLabel(evt)}
          </span>
        </div>
      ))}
    </div>
  )
}
