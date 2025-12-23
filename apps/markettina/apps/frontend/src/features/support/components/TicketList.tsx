import { useState, useEffect } from 'react'
import { Clock, MessageSquare, AlertCircle, CheckCircle, User, Bot } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card'
import { Badge } from '../../../shared/components/ui/badge'
import { Button } from '../../../shared/components/ui/button'
import { formatDistanceToNow } from 'date-fns'
import { it } from 'date-fns/locale'

interface TicketSummary {
  id: number
  title: string
  status: 'open' | 'in_progress' | 'waiting_user' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  ai_handled: boolean
  message_count: number
  created_at: string
  last_message_at?: string
}

interface TicketListProps {
  onTicketSelect?: (ticketId: number) => void
  selectedTicketId?: number
}

export function TicketList({ onTicketSelect, selectedTicketId }: TicketListProps) {
  const [tickets, setTickets] = useState<TicketSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'open' | 'resolved'>('all')

  useEffect(() => {
    fetchTickets()
  }, [filter])

  const fetchTickets = async () => {
    try {
      const token = localStorage.getItem('token')
      const url = filter === 'all'
        ? '/api/v1/support/tickets'
        : `/api/v1/support/tickets?status=${filter}`

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTickets(data)
      }
    } catch (error) {
      console.error('Error fetching tickets:', error)
    } finally {
      setLoading(false)
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

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'Urgente'
      case 'high': return 'Alta'
      case 'medium': return 'Media'
      case 'low': return 'Bassa'
      default: return priority
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>I tuoi ticket</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>I tuoi ticket</CardTitle>
          <div className="flex gap-2">
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('all')}
            >
              Tutti
            </Button>
            <Button
              variant={filter === 'open' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('open')}
            >
              Aperti
            </Button>
            <Button
              variant={filter === 'resolved' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter('resolved')}
            >
              Risolti
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {tickets.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Nessun ticket trovato</p>
            <p className="text-sm">Inizia una chat per creare il tuo primo ticket!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {tickets.map((ticket) => (
              <div
                key={ticket.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                  selectedTicketId === ticket.id
                    ? 'border-gold bg-gold/10'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => onTicketSelect?.(ticket.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h4 className="font-medium text-sm mb-1 line-clamp-2">
                      {ticket.title}
                    </h4>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span>#{ticket.id}</span>
                      <span>•</span>
                      <span>
                        {formatDistanceToNow(new Date(ticket.created_at), {
                          addSuffix: true,
                          locale: it
                        })}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {ticket.ai_handled ? (
                      <Bot className="h-4 w-4 text-gold" aria-label="Gestito da AI" />
                    ) : (
                      <User className="h-4 w-4 text-gold" aria-label="Gestito da operatore" />
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(ticket.status)}
                    <span className="text-sm">{getStatusText(ticket.status)}</span>
                    <Badge className={`text-xs ${getPriorityColor(ticket.priority)}`}>
                      {getPriorityText(ticket.priority)}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <MessageSquare className="h-3 w-3" />
                    <span>{ticket.message_count}</span>
                    {ticket.last_message_at && (
                      <>
                        <span>•</span>
                        <span>
                          {formatDistanceToNow(new Date(ticket.last_message_at), {
                            addSuffix: true,
                            locale: it
                          })}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
