import type { Playlist, Mode, ProgressEvent } from '../types'

const BASE = 'http://localhost:8000'

export async function fetchModels(): Promise<string[]> {
  const res = await fetch(`${BASE}/models`)
  if (!res.ok) throw new Error('Failed to fetch models')
  return res.json()
}

export async function generatePlaylist(params: {
  mood: string
  context: string
  seed: string
  model: string
  mode: Exclude<Mode, 'agentic'>
  spotify_enrich: boolean
}): Promise<Playlist> {
  const res = await fetch(`${BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'Generation failed')
  }
  return res.json()
}

export function streamPlaylist(params: {
  mood: string
  context: string
  seed: string
  model: string
  spotify_enrich: boolean
  onEvent: (evt: ProgressEvent) => void
  onPlaylist: (pl: Playlist) => void
  onError: (msg: string) => void
}): () => void {
  const qs = new URLSearchParams({
    mood: params.mood,
    context: params.context,
    seed: params.seed,
    model: params.model,
    spotify_enrich: String(params.spotify_enrich),
  })
  const es = new EventSource(`${BASE}/stream?${qs}`)

  es.onmessage = (e) => {
    const evt: ProgressEvent = JSON.parse(e.data)
    params.onEvent(evt)
    if (evt.node === 'finalise' && evt.data?.tracks) {
      params.onPlaylist(evt.data as unknown as Playlist)
    }
    if (evt.node === 'done' || evt.node === 'error') {
      if (evt.node === 'error') params.onError((evt as any).message ?? 'Unknown error')
      es.close()
    }
  }

  es.onerror = () => {
    params.onError('Connection to server lost')
    es.close()
  }

  // return a cleanup function so callers can cancel early
  return () => es.close()
}
