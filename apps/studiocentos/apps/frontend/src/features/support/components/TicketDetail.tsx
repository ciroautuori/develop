import { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, AlertCircle, Clock, CheckCircle, ArrowUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card'
import { Badge } from '../../../shared/components/ui/badge'
import { Button } from '../../../shared/components/ui/button'
import { Input } from '../../../shared/components/ui/input'
import { Textarea } from '../../../shared/components/ui/textarea'
import { formatDistanceToNow } from 'date-fns'
import { it } from 'date-fns/locale'
import { toast } from 'sonner'

interface Message {
  id: number
  ticket_id: number
  sender_type: 'user' | 'ai' | 'agent' | 'system'
  sender_id?: number
  content: string
  content_type: string
  ai_provider?: string
  ai_model?: string
  ai_confidence?: number
  ai_tokens_used?: number
  is_internal: boolean
  created_at: string
  updated_at: string
  sender_name?: string
  sender_avatar?: string
}

interface TicketDetail {
  id: number
  user_id: number
  title: string
  description?: string
  status: 'open' | 'in_progress' | 'waiting_user' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  ai_handled: boolean
  ai_confidence: number
  escalated_at?: string
  assigned_agent_id?: number
  assigned_agent_name?: string
  category?: string
  tags?: string[]
  sentiment: string
  created_at: string
  updated_at: string
  resolved_at?: string
  closed_at?: string
  messages: Message[]
  message_count: number
  last_message_at?: string
}

interface TicketDetailProps {
  ticketId: number
  onClose?: () => void
}

export function TicketDetail({ ticketId, onClose }: TicketDetailProps) {
  const [ticket, setTicket] = useState<TicketDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [newMessage, setNewMessage] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchTicketDetail()
  }, [ticketId])

  useEffect(() => {
    scrollToBottom()
  }, [ticket?.messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const fetchTicketDetail = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/support/tickets/${ticketId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTicket(data)
      } else {
        toast.error('Errore nel caricamento del ticket')
      }
    } catch (error) {
      console.error('Error fetching ticket:', error)
      toast.error('Errore di connessione')
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!newMessage.trim() || sending || !ticket) return

    setSending(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/support/tickets/${ticketId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ticket_id: ticketId,
          content: newMessage,
          content_type: 'text',
          is_internal: false
        })
      })

      if (response.ok) {
        const newMsg = await response.json()
        setTicket(prev => prev ? {
          ...prev,
          messages: [...prev.messages, newMsg],
          message_count: prev.message_count + 1,
          last_message_at: newMsg.created_at
        } : null)
        setNewMessage('')
        toast.success('Messaggio inviato')
      } else {
        toast.error('Errore nell\'invio del messaggio')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Errore di connessione')
    } finally {
      setSending(false)
    }
  }

  const escalateTicket = async () => {
    if (!ticket) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/support/tickets/${ticketId}/escalate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          reason: 'Richiesta escalation manuale dall\'utente',
          priority: 'high'
        })
      })

      if (response.ok) {
        toast.success('Ticket escalato al supporto umano')
        fetchTicketDetail() // Ricarica i dettagli
      } else {
        toast.error('Errore nell\'escalation')
      }
    } catch (error) {
      console.error('Error escalating ticket:', error)
      toast.error('Errore di connessione')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return <AlertCircle className="h-4 w-4 text-gold" />
      case 'in_progress': return <Clock className="h-4 w-4 text-gold" />
      case 'resolved': return <CheckCircle className="h-4 w-4 text-gold" />
      case 'closed': return <CheckCircle className="h-4 w-4 text-gray-500" />
      default: return <AlertCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'open': return 'Aperto'
      case 'in_progress': return 'In corso'
      case 'waiting_user': return 'In attesa'
      case 'resolved': return 'Risolto'
      case 'closed': return 'Chiuso'
      default: return status
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-gray-500 text-white'
      case 'high': return 'bg-gold text-white'
      case 'medium': return 'bg-gold text-black'
      case 'low': return 'bg-gold text-white'
      default: return 'bg-gray-500 text-white'
    }
  }

  const getSenderIcon = (senderType: string) => {
    switch (senderType) {
      case 'ai': return <Bot className="h-4 w-4 text-gold" />
      case 'agent': return <User className="h-4 w-4 text-gold" />
      case 'system': return <AlertCircle className="h-4 w-4 text-gold" />
      default: return <User className="h-4 w-4 text-gray-500" />
    }
  }

  if (loading) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold"></div>
        </CardContent>
      </Card>
    )
  }

  if (!ticket) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-96">
          <div className="text-center text-gray-500">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Ticket non trovato</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="border-b">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg mb-2">{ticket.title}</CardTitle>
            <div className="flex items-center gap-3 text-sm text-gray-600">
              <span>Ticket #{ticket.id}</span>
              <div className="flex items-center gap-1">
                {getStatusIcon(ticket.status)}
                <span>{getStatusText(ticket.status)}</span>
              </div>
              <Badge className={`text-xs ${getPriorityColor(ticket.priority)}`}>
                {ticket.priority.toUpperCase()}
              </Badge>
              {ticket.ai_handled ? (
                <Badge variant="outline" className="text-xs">
                  <Bot className="h-3 w-3 mr-1" />
                  AI Assistant
                </Badge>
              ) : (
                <Badge variant="outline" className="text-xs">
                  <User className="h-3 w-3 mr-1" />
                  Operatore Umano
                </Badge>
              )}
            </div>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              ✕
            </Button>
          )}
        </div>

        {ticket.description && (
          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700">{ticket.description}</p>
          </div>
        )}

        <div className="flex items-center justify-between mt-3">
          <div className="text-xs text-gray-500">
            Creato {formatDistanceToNow(new Date(ticket.created_at), { addSuffix: true, locale: it })}
            {ticket.escalated_at && (
              <span className="ml-2">• Escalato {formatDistanceToNow(new Date(ticket.escalated_at), { addSuffix: true, locale: it })}</span>
            )}
          </div>

          {ticket.ai_handled && ticket.status === 'open' && (
            <Button
              variant="outline"
              size="sm"
              onClick={escalateTicket}
              className="text-xs"
            >
              <ArrowUp className="h-3 w-3 mr-1" />
              Escalate a operatore
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {ticket.messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender_type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] p-3 rounded-lg ${
                  message.sender_type === 'user'
                    ? 'bg-gold text-white'
                    : message.sender_type === 'system'
                    ? 'bg-gold/10 text-gold border border-gold'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="flex items-start gap-2">
                  {message.sender_type !== 'user' && (
                    <div className="flex-shrink-0 mt-0.5">
                      {getSenderIcon(message.sender_type)}
                    </div>
                  )}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium">
                        {message.sender_name ||
                         (message.sender_type === 'ai' ? 'Assistente AI' :
                          message.sender_type === 'system' ? 'Sistema' : 'Operatore')}
                      </span>
                      <span className="text-xs opacity-70">
                        {formatDistanceToNow(new Date(message.created_at), { addSuffix: true, locale: it })}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-line">{message.content}</p>

                    {message.ai_confidence !== undefined && (
                      <div className="flex items-center gap-2 mt-2">
                        <Badge
                          variant={message.ai_confidence > 80 ? "default" : message.ai_confidence > 60 ? "secondary" : "destructive"}
                          className="text-xs"
                        >
                          Confidenza: {message.ai_confidence}%
                        </Badge>
                        {message.ai_provider && (
                          <span className="text-xs opacity-60">
                            {message.ai_provider}
                            {message.ai_model && ` • ${message.ai_model}`}
                            {message.ai_tokens_used && ` • ${message.ai_tokens_used} tokens`}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        {ticket.status !== 'closed' && (
          <div className="p-4 border-t bg-white">
            <div className="flex gap-2">
              <Textarea
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Scrivi un messaggio..."
                className="flex-1 min-h-[60px] max-h-32 resize-none"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
                disabled={sending}
              />
              <Button
                onClick={sendMessage}
                disabled={sending || !newMessage.trim()}
                size="sm"
                className="self-end"
              >
                {sending ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Premi Invio per inviare, Shift+Invio per andare a capo
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
