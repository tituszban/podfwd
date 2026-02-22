import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Mail, Star, RefreshCw, FileText } from 'lucide-react'
import { Button, ScrollArea, Separator } from './ui'
import { fetchEmails, refreshEmails } from '@/lib/api'
import { EmailInfo } from '@/types'
import { cn } from '@/lib/utils'

export function EmailSidebar() {
  const [gmailEmails, setGmailEmails] = useState<EmailInfo[]>([])
  const [emlEmails, setEmlEmails] = useState<EmailInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const navigate = useNavigate()
  const { emailId } = useParams()

  useEffect(() => {
    loadEmails()
  }, [])

  async function loadEmails() {
    try {
      setLoading(true)
      const data = await fetchEmails()
      setGmailEmails(data.gmail)
      setEmlEmails(data.eml)
    } catch (error) {
      console.error('Failed to load emails:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleRefresh() {
    try {
      setRefreshing(true)
      const data = await refreshEmails()
      setGmailEmails(data.gmail)
      setEmlEmails(data.eml)
    } catch (error) {
      console.error('Failed to refresh emails:', error)
    } finally {
      setRefreshing(false)
    }
  }

  function handleEmailClick(email: EmailInfo) {
    navigate(`/email/${email.id}`)
  }

  return (
    <aside className="w-80 border-r border-border flex flex-col">
      <div className="p-4 border-b border-border flex items-center justify-between">
        <h1 className="font-semibold text-lg">PODFWD Dev</h1>
        <Button
          variant="ghost"
          size="icon"
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <RefreshCw className={cn("h-4 w-4", refreshing && "animate-spin")} />
        </Button>
      </div>

      <ScrollArea className="flex-1">
        {loading ? (
          <div className="p-4 text-center text-muted-foreground">Loading...</div>
        ) : (
          <div className="p-2">
            {/* Gmail Emails Section */}
            <div className="mb-4">
              <div className="flex items-center gap-2 px-2 py-1 text-sm font-medium text-muted-foreground">
                <Mail className="h-4 w-4" />
                Gmail ({gmailEmails.length})
              </div>
              <div className="space-y-1">
                {gmailEmails.map((email) => (
                  <EmailItem
                    key={email.id}
                    email={email}
                    isSelected={emailId === email.id}
                    onClick={() => handleEmailClick(email)}
                  />
                ))}
                {gmailEmails.length === 0 && (
                  <div className="px-2 py-4 text-sm text-muted-foreground text-center">
                    No Gmail emails found
                  </div>
                )}
              </div>
            </div>

            <Separator className="my-4" />

            {/* EML Files Section */}
            <div>
              <div className="flex items-center gap-2 px-2 py-1 text-sm font-medium text-muted-foreground">
                <FileText className="h-4 w-4" />
                .eml Files ({emlEmails.length})
              </div>
              <div className="space-y-1">
                {emlEmails.map((email) => (
                  <EmailItem
                    key={email.id}
                    email={email}
                    isSelected={emailId === email.id}
                    onClick={() => handleEmailClick(email)}
                  />
                ))}
                {emlEmails.length === 0 && (
                  <div className="px-2 py-4 text-sm text-muted-foreground text-center">
                    No .eml files in sources/
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </ScrollArea>
    </aside>
  )
}

interface EmailItemProps {
  email: EmailInfo
  isSelected: boolean
  onClick: () => void
}

const TYPE_BADGES: Record<string, { label: string; className: string }> = {
  inbox: { label: 'Inbox', className: 'bg-blue-500/30 text-blue-300 border border-blue-500/50' },
  debug: { label: 'Debug', className: 'bg-yellow-500/30 text-yellow-300 border border-yellow-500/50' },
  testcase: { label: 'Test', className: 'bg-purple-500/30 text-purple-300 border border-purple-500/50' },
  eml: { label: 'File', className: 'bg-gray-500/30 text-gray-300 border border-gray-500/50' },
}

function EmailItem({ email, isSelected, onClick }: EmailItemProps) {
  const badge = TYPE_BADGES[email.emailType] || TYPE_BADGES.eml

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left px-3 py-2 rounded-md transition-colors",
        "hover:bg-accent hover:text-accent-foreground",
        isSelected && "bg-accent text-accent-foreground"
      )}
    >
      <div className="flex items-start gap-2">
        {email.isStarred && (
          <Star className="h-4 w-4 text-yellow-500 fill-yellow-500 flex-shrink-0 mt-0.5" />
        )}
        <div className="flex-1 min-w-0">
          <div className="font-medium text-sm truncate">{email.subject}</div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className={cn(
              "text-[10px] px-1.5 py-0.5 rounded font-medium",
              badge.className
            )}>
              {badge.label}
            </span>
            <span className="text-xs text-muted-foreground truncate">{email.sender}</span>
          </div>
          <div className="text-xs text-muted-foreground">{email.date}</div>
        </div>
      </div>
    </button>
  )
}
