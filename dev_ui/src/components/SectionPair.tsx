import { ContentSection } from '@/types'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui'

interface SectionPairProps {
  section: ContentSection
  showDescription?: boolean
}

export function SectionPair({ section, showDescription = false }: SectionPairProps) {
  const [debugOpen, setDebugOpen] = useState(false)

  return (
    <div className="border border-border rounded-lg overflow-hidden mb-4">
      {/* Debug Header */}
      <Collapsible open={debugOpen} onOpenChange={setDebugOpen}>
        <CollapsibleTrigger className="flex items-center gap-2 w-full p-2 bg-zinc-900/50 hover:bg-zinc-900 text-left text-sm">
          {debugOpen ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
          <span className="font-mono text-xs text-muted-foreground">
            [{section.index}] {section.contentType}
          </span>
          {section.isRemoved && (
            <span className="ml-auto px-2 py-0.5 bg-zinc-700 text-zinc-300 rounded text-xs">
              Removed
            </span>
          )}
        </CollapsibleTrigger>
        <CollapsibleContent>
          <div className="p-2 bg-zinc-900/30 text-xs font-mono space-y-1">
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

      {/* Content Grid */}
      <div className="grid grid-cols-2 divide-x divide-border">
        {/* Original HTML */}
        <div className="p-4">
          <div className="text-xs text-muted-foreground mb-2 font-medium">Original HTML</div>
          <div 
            className="email-content p-4 text-sm"
            dangerouslySetInnerHTML={{ __html: section.originalHtml }}
          />
        </div>

        {/* SSML / Description */}
        <div className="p-4">
          {section.isRemoved ? (
            <div className="removed-section h-full flex items-center justify-center">
              <div className="text-center">
                <div className="font-medium">Content Removed</div>
                {section.removalReason && (
                  <div className="text-xs mt-1">{section.removalReason}</div>
                )}
              </div>
            </div>
          ) : showDescription ? (
            <>
              <div className="text-xs text-muted-foreground mb-2 font-medium">Description HTML</div>
              <div 
                className="email-content p-4 text-sm"
                dangerouslySetInnerHTML={{ __html: section.descriptionHtml }}
              />
            </>
          ) : (
            <>
              <div className="text-xs text-muted-foreground mb-2 font-medium">SSML Tags</div>
              <div className="ssml-content">
                {section.ssmlTags.length > 0 ? (
                  section.ssmlTags.map((tag, i) => (
                    <pre key={i} className="text-green-400 mb-2">{formatXml(tag)}</pre>
                  ))
                ) : (
                  <span className="text-muted-foreground">No SSML generated</span>
                )}
              </div>
            </>
          )}
        </div>
      </div>
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

interface SectionListProps {
  sections: ContentSection[]
  showDescription?: boolean
}

export function SectionList({ sections, showDescription = false }: SectionListProps) {
  if (sections.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        No sections parsed
      </div>
    )
  }

  return (
    <div className="p-4">
      {sections.map((section) => (
        <SectionPair 
          key={section.index} 
          section={section}
          showDescription={showDescription}
        />
      ))}
    </div>
  )
}
