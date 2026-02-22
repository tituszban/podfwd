import { ContentSection, SsmlChunk } from '@/types'
import { ChevronDown, ChevronRight, Loader2, Play, Pause, RotateCcw, SkipBack, SkipForward, Download } from 'lucide-react'
import { useState, useMemo, useRef, useEffect, useCallback } from 'react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui'
import { generateChunkAudio } from '@/lib/api'

export type ViewMode = 'ssml' | 'description'

interface SectionViewProps {
  sections: ContentSection[]
  ssmlChunks: SsmlChunk[]
  emailId: string
  viewMode: ViewMode
}

// Color palette for chunks
const CHUNK_COLORS = [
  'bg-blue-500',
  'bg-green-500',
  'bg-purple-500',
  'bg-orange-500',
  'bg-pink-500',
  'bg-cyan-500',
  'bg-yellow-500',
  'bg-red-500',
]

const CHUNK_BORDER_COLORS = [
  'border-blue-500',
  'border-green-500',
  'border-purple-500',
  'border-orange-500',
  'border-pink-500',
  'border-cyan-500',
  'border-yellow-500',
  'border-red-500',
]

// Speed options from 1x to 2.5x in 0.1 increments
const SPEED_OPTIONS = Array.from({ length: 16 }, (_, i) => (1 + i * 0.1).toFixed(1))

export function SectionView({ sections, ssmlChunks, emailId, viewMode }: SectionViewProps) {
  const [expandedDebug, setExpandedDebug] = useState<Set<number>>(new Set())
  const [loadingChunk, setLoadingChunk] = useState<number | null>(null)
  const [audioUrls, setAudioUrls] = useState<Record<number, string>>({})
  const [audioErrors, setAudioErrors] = useState<Record<number, string>>({})
  
  // Audio player state
  const [activeChunk, setActiveChunk] = useState<number | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackSpeed, setPlaybackSpeed] = useState(() => {
    // Load saved speed from localStorage
    if (typeof window !== 'undefined') {
      return localStorage.getItem('audioPlaybackSpeed') || '1.0'
    }
    return '1.0'
  })
  const audioRef = useRef<HTMLAudioElement>(null)

  // Create a map from section index to chunk index
  const sectionToChunk = useMemo(() => {
    const map: Record<number, number> = {}
    ssmlChunks.forEach((chunk) => {
      chunk.sectionIndices.forEach((sectionIndex) => {
        map[sectionIndex] = chunk.index
      })
    })
    return map
  }, [ssmlChunks])

  const getChunkForSection = (sectionIndex: number) => sectionToChunk[sectionIndex]
  const getChunkColor = (chunkIndex: number) => CHUNK_COLORS[chunkIndex % CHUNK_COLORS.length]

  const toggleDebug = (index: number) => {
    setExpandedDebug(prev => {
      const next = new Set(prev)
      if (next.has(index)) {
        next.delete(index)
      } else {
        next.add(index)
      }
      return next
    })
  }

  const handleGenerateAudio = async (chunkIndex: number) => {
    setLoadingChunk(chunkIndex)
    setAudioErrors(prev => ({ ...prev, [chunkIndex]: '' }))

    try {
      const result = await generateChunkAudio(emailId, chunkIndex)
      if (result.success && result.audioUrl) {
        setAudioUrls(prev => ({ ...prev, [chunkIndex]: result.audioUrl! }))
      } else {
        setAudioErrors(prev => ({ ...prev, [chunkIndex]: result.error || 'Failed to generate' }))
      }
    } catch (err) {
      setAudioErrors(prev => ({ ...prev, [chunkIndex]: err instanceof Error ? err.message : 'Failed' }))
    } finally {
      setLoadingChunk(null)
    }
  }

  // Audio player controls
  const playChunk = useCallback((chunkIndex: number) => {
    const url = audioUrls[chunkIndex]
    if (!url) {
      handleGenerateAudio(chunkIndex)
      return
    }
    
    // If clicking the same chunk that's playing, toggle pause
    if (activeChunk === chunkIndex && isPlaying) {
      audioRef.current?.pause()
      return
    }
    
    setActiveChunk(chunkIndex)
    if (audioRef.current) {
      audioRef.current.src = url
      audioRef.current.playbackRate = parseFloat(playbackSpeed)
      audioRef.current.play()
    }
  }, [audioUrls, playbackSpeed, activeChunk, isPlaying]) // eslint-disable-line react-hooks/exhaustive-deps

  const togglePlayPause = useCallback(() => {
    if (!audioRef.current) return
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
  }, [isPlaying])

  const restart = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0
      audioRef.current.play()
    }
  }, [])

  const skipBackward = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.max(0, audioRef.current.currentTime - 10)
    }
  }, [])

  const skipForward = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.min(duration, audioRef.current.currentTime + 10)
    }
  }, [duration])

  const changeSpeed = useCallback((speed: string) => {
    setPlaybackSpeed(speed)
    localStorage.setItem('audioPlaybackSpeed', speed)
    if (audioRef.current) {
      audioRef.current.playbackRate = parseFloat(speed)
    }
  }, [])

  // Audio event handlers
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime)
    const handleDurationChange = () => setDuration(audio.duration || 0)
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => {
      setIsPlaying(false)
    }

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('durationchange', handleDurationChange)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('durationchange', handleDurationChange)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [])

  const formatTime = (time: number) => {
    if (!isFinite(time)) return '0:00'
    const mins = Math.floor(time / 60)
    const secs = Math.floor(time % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (sections.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        No sections parsed
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Main content area */}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse">
          <tbody>
            {/* Group sections by chunk for proper sticky behavior */}
            {(() => {
              // Build groups of consecutive sections by chunk
              // Sections without a chunk assignment get merged into the previous chunk's group
              const groups: { chunkIndex: number | undefined; sections: ContentSection[] }[] = []
              let currentGroup: { chunkIndex: number | undefined; sections: ContentSection[] } | null = null

              sections.forEach((section) => {
                const chunkIndex = getChunkForSection(section.index)
                
                // If this section has no chunk, try to merge with current group
                if (chunkIndex === undefined && currentGroup && currentGroup.chunkIndex !== undefined) {
                  // Keep it in the current chunk group
                  currentGroup.sections.push(section)
                } else if (!currentGroup || currentGroup.chunkIndex !== chunkIndex) {
                  // Start a new group
                  if (currentGroup) groups.push(currentGroup)
                  currentGroup = { chunkIndex, sections: [section] }
                } else {
                  currentGroup.sections.push(section)
                }
              })
              if (currentGroup) groups.push(currentGroup)

              return groups.map((group, groupIdx) => {
                const chunkIndex = group.chunkIndex
                const chunkColor = chunkIndex !== undefined ? getChunkColor(chunkIndex) : ''
                // For sections with no chunk, use a neutral gray bar
                const chunkBorderClass = chunkIndex !== undefined 
                  ? CHUNK_BORDER_COLORS[chunkIndex % CHUNK_BORDER_COLORS.length].replace('border-', 'bg-')
                  : 'bg-zinc-700'
                const hasAudio = chunkIndex !== undefined && !!audioUrls[chunkIndex]
                const isLoading = chunkIndex !== undefined && loadingChunk === chunkIndex
                const isActiveChunk = activeChunk === chunkIndex
                const hasError = chunkIndex !== undefined && !!audioErrors[chunkIndex]

                return (
                  <tr key={groupIdx} className="align-top">
                    {/* This cell contains all sections in this chunk group */}
                    <td colSpan={2} className="p-0">
                      <div className="flex">
                        {/* Content area */}
                        <div className="flex-1">
                          <table className="w-full border-collapse">
                            <tbody>
                              {group.sections.map((section) => {
                                const isExpanded = expandedDebug.has(section.index)
                                const hasOriginalContent = section.originalHtml && section.originalHtml.trim().length > 0
                                const hasOutputContent = !section.isRemoved && (
                                  (viewMode === 'ssml' && section.ssmlTags.length > 0) ||
                                  (viewMode === 'description' && section.descriptionHtml && section.descriptionHtml.trim().length > 0)
                                )
                                const isMinimalRow = !hasOriginalContent && !hasOutputContent && !section.isRemoved

                                return (
                                  <tr
                                    key={section.index}
                                    className={`align-top ${isActiveChunk && isPlaying ? 'bg-blue-500/5' : ''}`}
                                  >
                                    {/* Left side - Original HTML */}
                                    <td className={`w-1/2 border-b border-border ${isMinimalRow ? 'p-1' : 'p-3'}`}>
                                      {hasOriginalContent && (
                                        <div
                                          className="email-content text-sm"
                                          dangerouslySetInnerHTML={{ __html: section.originalHtml }}
                                        />
                                      )}
                                    </td>

                                    {/* Right side - SSML/Description */}
                                    <td className={`w-1/2 border-b border-border ${isMinimalRow ? 'p-1' : 'p-3'}`}>
                                      {/* Debug Header */}
                                      <Collapsible open={isExpanded} onOpenChange={() => toggleDebug(section.index)}>
                                        <CollapsibleTrigger className={`flex items-center gap-2 w-full text-left text-xs hover:bg-zinc-900/50 rounded px-1 ${isMinimalRow ? 'py-0.5' : 'py-1'}`}>
                                          {isExpanded ? (
                                            <ChevronDown className="h-3 w-3 flex-shrink-0" />
                                          ) : (
                                            <ChevronRight className="h-3 w-3 flex-shrink-0" />
                                          )}
                                          <span className={`font-mono truncate ${isMinimalRow ? 'text-zinc-600' : 'text-muted-foreground'}`}>
                                            [{section.index}] {section.contentType}
                                          </span>
                                          {section.isRemoved && (
                                            <span className="ml-auto px-1.5 py-0.5 bg-zinc-700 text-zinc-300 rounded text-xs flex-shrink-0">
                                              Removed
                                            </span>
                                          )}
                                        </CollapsibleTrigger>
                                        <CollapsibleContent>
                                          <div className="p-2 bg-zinc-900/30 text-xs font-mono space-y-1 rounded mt-1 mb-2">
                                            <div><span className="text-muted-foreground">Content Type:</span> {section.descriptionContentType}</div>
                                            {section.removalReason && (
                                              <div><span className="text-muted-foreground">Removal Reason:</span> {section.removalReason}</div>
                                            )}
                                            {Object.entries(section.debugInfo).map(([key, value]) => (
                                              <div key={key}>
                                                <span className="text-muted-foreground">{key}:</span> {String(value)}
                                              </div>
                                            ))}
                                          </div>
                                        </CollapsibleContent>
                                      </Collapsible>

                                      {/* SSML or Description content */}
                                      {(hasOutputContent || section.isRemoved) && (
                                        <div className="mt-1">
                                          {section.isRemoved ? (
                                            <div className="removed-section py-2 px-3 text-center">
                                              <div className="text-sm">Content Removed</div>
                                              {section.removalReason && (
                                                <div className="text-xs mt-0.5">{section.removalReason}</div>
                                              )}
                                            </div>
                                          ) : viewMode === 'description' ? (
                                            <div
                                              className="email-content text-sm"
                                              dangerouslySetInnerHTML={{ __html: section.descriptionHtml }}
                                            />
                                          ) : (
                                            <div className="ssml-content text-xs">
                                              {section.ssmlTags.map((tag, i) => (
                                                <pre key={i} className="text-green-400 whitespace-pre-wrap">{formatXml(tag)}</pre>
                                              ))}
                                            </div>
                                          )}
                                        </div>
                                      )}
                                    </td>
                                  </tr>
                                )
                              })}
                            </tbody>
                          </table>
                        </div>

                        {/* Right edge colored bar with sticky play button and vertical progress */}
                        <div className={`w-10 flex-shrink-0 ${chunkBorderClass} relative`}>
                          {/* Vertical progress indicator - fills from top as audio plays */}
                          {isActiveChunk && hasAudio && duration > 0 && (
                            <div 
                              className="absolute top-0 left-0 right-0 bg-white/30 pointer-events-none transition-all duration-100"
                              style={{ height: `${(currentTime / duration) * 100}%` }}
                            />
                          )}
                          {chunkIndex !== undefined && (
                            <div className="sticky top-0 flex flex-col items-center gap-1 py-2 z-10">
                              <span className={`text-[10px] font-bold text-white px-1.5 py-0.5 rounded ${chunkColor}`}>
                                {chunkIndex + 1}
                              </span>
                              <button
                                onClick={() => playChunk(chunkIndex)}
                                disabled={isLoading}
                                className={`w-7 h-7 rounded flex items-center justify-center transition-colors ${
                                  hasError
                                    ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                                    : isActiveChunk && isPlaying
                                      ? 'bg-white/20 text-white'
                                      : hasAudio
                                        ? 'bg-white/10 text-white hover:bg-white/20'
                                        : 'bg-black/20 text-white/70 hover:bg-black/30'
                                }`}
                                title={hasError ? audioErrors[chunkIndex] : (hasAudio ? (isActiveChunk && isPlaying ? 'Pause' : 'Play') : 'Generate audio')}
                              >
                                {isLoading ? (
                                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                ) : hasAudio ? (
                                  isActiveChunk && isPlaying ? (
                                    <Pause className="h-3.5 w-3.5" />
                                  ) : (
                                    <Play className="h-3.5 w-3.5" />
                                  )
                                ) : (
                                  <Download className="h-3.5 w-3.5" />
                                )}
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                )
              })
            })()}
          </tbody>
        </table>
      </div>

      {/* Audio Player Bar */}
      {activeChunk !== null && audioUrls[activeChunk] && (
        <div className="flex-shrink-0 border-t border-border bg-zinc-900 p-3">
          <div className="flex items-center gap-4">
            {/* Chunk indicator */}
            <div className={`px-2 py-1 rounded text-xs font-bold text-white ${getChunkColor(activeChunk)}`}>
              Chunk {activeChunk + 1}
            </div>

            {/* Playback controls */}
            <div className="flex items-center gap-1">
              <button
                onClick={restart}
                className="w-8 h-8 rounded hover:bg-zinc-800 flex items-center justify-center text-zinc-400 hover:text-white transition-colors"
                title="Restart"
              >
                <RotateCcw className="h-4 w-4" />
              </button>
              <button
                onClick={skipBackward}
                className="w-8 h-8 rounded hover:bg-zinc-800 flex items-center justify-center text-zinc-400 hover:text-white transition-colors"
                title="Skip back 10s"
              >
                <SkipBack className="h-4 w-4" />
              </button>
              <button
                onClick={togglePlayPause}
                className="w-10 h-10 rounded-full bg-blue-500 hover:bg-blue-600 flex items-center justify-center text-white transition-colors"
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 ml-0.5" />}
              </button>
              <button
                onClick={skipForward}
                className="w-8 h-8 rounded hover:bg-zinc-800 flex items-center justify-center text-zinc-400 hover:text-white transition-colors"
                title="Skip forward 10s"
              >
                <SkipForward className="h-4 w-4" />
              </button>
            </div>

            {/* Progress bar */}
            <div className="flex-1 flex items-center gap-2">
              <span className="text-xs text-muted-foreground w-10 text-right">{formatTime(currentTime)}</span>
              <div
                className="flex-1 h-3 bg-zinc-700 rounded-full cursor-pointer relative group"
                onMouseDown={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  
                  const audio = audioRef.current
                  if (!audio || !audio.duration || !isFinite(audio.duration)) {
                    return
                  }
                  
                  // Capture rect at mousedown for dragging
                  const rect = e.currentTarget.getBoundingClientRect()
                  
                  // Seek immediately on click
                  const initialPercent = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
                  audio.currentTime = initialPercent * audio.duration
                  
                  const handleMouseMove = (moveEvent: MouseEvent) => {
                    const percent = Math.max(0, Math.min(1, (moveEvent.clientX - rect.left) / rect.width))
                    if (audio && audio.duration && isFinite(audio.duration)) {
                      audio.currentTime = percent * audio.duration
                    }
                  }
                  const handleMouseUp = () => {
                    document.removeEventListener('mousemove', handleMouseMove)
                    document.removeEventListener('mouseup', handleMouseUp)
                  }
                  document.addEventListener('mousemove', handleMouseMove)
                  document.addEventListener('mouseup', handleMouseUp)
                }}
              >
                <div
                  className="absolute inset-y-0 left-0 bg-blue-500 rounded-full pointer-events-none"
                  style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                />
                <div
                  className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow pointer-events-none"
                  style={{ left: `calc(${duration ? (currentTime / duration) * 100 : 0}% - 8px)` }}
                />
              </div>
              <span className="text-xs text-muted-foreground w-10">{formatTime(duration)}</span>
            </div>

            {/* Speed selector */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Speed:</span>
              <select
                value={playbackSpeed}
                onChange={(e) => changeSpeed(e.target.value)}
                className="bg-zinc-800 border border-zinc-700 rounded px-2 py-1 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {SPEED_OPTIONS.map((speed) => (
                  <option key={speed} value={speed}>
                    {speed}x
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Hidden audio element */}
      <audio ref={audioRef} className="hidden" />
    </div>
  )
}

function formatXml(xml: string): string {
  // Simple XML formatting
  let formatted = ''
  let indent = 0
  const parts = xml.replace(/></g, '>\n<').split('\n')

  for (const part of parts) {
    if (part.match(/^<\//)) {
      indent = Math.max(0, indent - 1)
    }
    formatted += '  '.repeat(indent) + part + '\n'
    if (part.match(/^<[^/].*[^/]>$/) && !part.match(/^<.*\/>/)) {
      indent++
    }
  }

  return formatted.trim()
}
