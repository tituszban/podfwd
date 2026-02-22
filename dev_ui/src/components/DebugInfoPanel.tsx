import { ParseResult } from '@/types'
import { AlertCircle, Info } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger } from './ui'

type ViewMode = 'ssml' | 'description'

interface DebugInfoPanelProps {
  parseResult: ParseResult
  viewMode: ViewMode
  onViewModeChange: (mode: ViewMode) => void
}

export function DebugInfoPanel({ parseResult, viewMode, onViewModeChange }: DebugInfoPanelProps) {
  return (
    <div className="bg-zinc-900/50 border-b border-border p-4">
      <div className="flex items-start gap-4 flex-wrap">
        {/* Status - only show if error */}
        {!parseResult.success && (
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 text-red-500">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm font-medium">Error</span>
            </div>
          </div>
        )}

        {/* Email Info */}
        <InfoItem label="Sender" value={parseResult.emailInfo.sender} />
        <InfoItem label="Recipient" value={parseResult.emailInfo.recipient} />
        <InfoItem label="Date" value={parseResult.emailInfo.date} />

        {/* Parser Info - show full parser chain */}
        <InfoItem label="Parser" value={parseResult.parserName} />
        
        {/* Voice Info - only once, with reason as tooltip */}
        <InfoItem 
          label="Voice" 
          value={parseResult.voice}
          tooltip={parseResult.voiceReason}
        />

        {/* Stats */}
        <InfoItem 
          label="Sections" 
          value={String(parseResult.sections.length)} 
        />
        <InfoItem 
          label="Audio Chunks" 
          value={String(parseResult.ssmlChunks.length)} 
        />

        {/* View Mode Toggle */}
        <div className="ml-auto">
          <Tabs value={viewMode} onValueChange={(v) => onViewModeChange(v as ViewMode)}>
            <TabsList className="h-7">
              <TabsTrigger value="ssml" className="text-xs px-3 h-5">SSML</TabsTrigger>
              <TabsTrigger value="description" className="text-xs px-3 h-5">Description</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </div>

      {/* Error Display */}
      {!parseResult.success && parseResult.error && (
        <div className="mt-4 p-4 bg-red-950/50 border border-red-900 rounded-md">
          <div className="font-medium text-red-400 mb-2">Error</div>
          <div className="text-sm text-red-300">{parseResult.error}</div>
          {parseResult.errorTraceback && (
            <details className="mt-2">
              <summary className="text-xs text-red-400 cursor-pointer">
                Show traceback
              </summary>
              <pre className="mt-2 text-xs text-red-300/70 overflow-x-auto whitespace-pre-wrap">
                {parseResult.errorTraceback}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  )
}

interface InfoItemProps {
  label: string
  value: string
  tooltip?: string
}

function InfoItem({ label, value, tooltip }: InfoItemProps) {
  return (
    <div className="flex items-center gap-1.5" title={tooltip}>
      <span className="text-xs text-muted-foreground">{label}:</span>
      <span className="text-sm font-medium">
        {value || '—'}
      </span>
      {tooltip && (
        <Info className="h-3 w-3 text-muted-foreground" />
      )}
    </div>
  )
}
