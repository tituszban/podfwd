import { useState } from 'react'
import { Loader2, Volume2 } from 'lucide-react'
import { Button } from './ui'
import { SsmlChunk } from '@/types'
import { generateChunkAudio } from '@/lib/api'

interface AudioPlayerProps {
  emailId: string
  chunk: SsmlChunk
  voice: string
}

export function AudioPlayer({ emailId, chunk }: AudioPlayerProps) {
  const [loading, setLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [cached, setCached] = useState(false)

  async function handleGenerate() {
    try {
      setLoading(true)
      setError(null)
      const result = await generateChunkAudio(emailId, chunk.index)
      
      if (result.success && result.audioUrl) {
        setAudioUrl(result.audioUrl)
        setCached(result.cached)
      } else {
        setError(result.error || 'Failed to generate audio')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate audio')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center gap-2 p-2 bg-zinc-900 rounded-md">
      <div className="flex-1 min-w-0">
        <div className="text-xs text-muted-foreground">
          Chunk {chunk.index + 1} • Sections: {chunk.sectionIndices.join(', ')}
          {cached && <span className="ml-2 text-green-500">(cached)</span>}
        </div>
      </div>

      {!audioUrl ? (
        <Button
          variant="outline"
          size="sm"
          onClick={handleGenerate}
          disabled={loading}
          className="flex-shrink-0"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              <Volume2 className="h-4 w-4 mr-1" />
              Generate
            </>
          )}
        </Button>
      ) : (
        <audio controls className="h-8">
          <source src={audioUrl} />
          Your browser does not support the audio element.
        </audio>
      )}

      {error && (
        <div className="text-xs text-red-400">{error}</div>
      )}
    </div>
  )
}

interface ChunkAudioListProps {
  emailId: string
  chunks: SsmlChunk[]
  voice: string
}

export function ChunkAudioList({ emailId, chunks, voice }: ChunkAudioListProps) {
  if (chunks.length === 0) {
    return (
      <div className="text-sm text-muted-foreground p-4">
        No SSML chunks available
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {chunks.map((chunk) => (
        <AudioPlayer
          key={chunk.index}
          emailId={emailId}
          chunk={chunk}
          voice={voice}
        />
      ))}
    </div>
  )
}
