import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui'
import { DebugInfoPanel, SectionView, type ViewMode } from '@/components'
import { parseEmail, refreshParse } from '@/lib/api'
import { ParseResult } from '@/types'
import { cn } from '@/lib/utils'

export function EmailView() {
  const { emailId } = useParams()
  const [parseResult, setParseResult] = useState<ParseResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('ssml')

  useEffect(() => {
    if (emailId) {
      loadParseResult(emailId)
    } else {
      setParseResult(null)
    }
  }, [emailId])

  async function loadParseResult(id: string) {
    try {
      setLoading(true)
      const result = await parseEmail(id)
      setParseResult(result)
    } catch (error) {
      console.error('Failed to parse email:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleRefresh() {
    if (!emailId) return
    try {
      setRefreshing(true)
      const result = await refreshParse(emailId)
      setParseResult(result)
    } catch (error) {
      console.error('Failed to refresh parse:', error)
    } finally {
      setRefreshing(false)
    }
  }

  if (!emailId) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <div className="text-lg font-medium mb-2">No email selected</div>
          <div className="text-sm">Select an email from the sidebar to view its parsed content</div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  if (!parseResult) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <div className="text-lg font-medium mb-2">Failed to load email</div>
          <Button variant="outline" onClick={() => loadParseResult(emailId)}>
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header with Debug Info */}
      <div className="flex-shrink-0">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="font-semibold truncate">{parseResult.emailInfo.subject}</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", refreshing && "animate-spin")} />
            Refresh Parse
          </Button>
        </div>
        <DebugInfoPanel 
          parseResult={parseResult} 
          viewMode={viewMode}
          onViewModeChange={setViewMode}
        />
      </div>

      {/* Main Content - Side by Side View */}
      <div className="flex-1 overflow-hidden">
        <SectionView 
          sections={parseResult.sections}
          ssmlChunks={parseResult.ssmlChunks}
          emailId={emailId}
          viewMode={viewMode}
        />
      </div>
    </div>
  )
}
