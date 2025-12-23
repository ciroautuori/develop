import { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, AlertCircle, X, Minimize2, MessageSquare, Loader2 } from 'lucide-react'
import { Button } from '../../../shared/components/ui/button'
import { Input } from '../../../shared/components/ui/input'
// Card components removed - using native divs for better scroll control
import { Badge } from '../../../shared/components/ui/badge'
import { toast } from 'sonner'
import { useLanguage } from '../../landing/i18n'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai' | 'agent' | 'system'
  timestamp: Date
  isRead?: boolean
  confidence?: number
  metadata?: {
    provider?: string
    model?: string
    tokens_used?: number
  }
}

interface ChatResponse {
  answer: string
  confidence: number
  provider: string
  processing_time: number
}

export function ChatWidget() {
  const { t } = useLanguage()
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [ticketId, setTicketId] = useState<number | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'online' | 'offline' | 'connecting'>('online')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
    // Mark messages as read when chat is open
    if (isOpen && !isMinimized) {
      setMessages(prev => prev.map(msg => ({ ...msg, isRead: true })))
    }
  }, [messages, isOpen, isMinimized])

  useEffect(() => {
    // Messaggio di benvenuto
    if (isOpen && messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        content: t.chat.welcome,
        sender: 'ai',
        timestamp: new Date()
      }
      setMessages([welcomeMessage])
    }
  }, [isOpen, messages.length, t.chat.welcome])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setConnectionStatus('connecting')

    try {
      // Use demo endpoint via Nginx proxy
      const endpoint = '/ai/api/v1/demo/ask'
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          question: inputMessage,
          provider: 'demo'
        })
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Sessione scaduta. Effettua nuovamente il login.')
        }
        throw new Error(`Errore server: ${response.status}`)
      }

      const data: ChatResponse = await response.json()
      setConnectionStatus('online')

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.answer,
        sender: 'ai',
        timestamp: new Date(),
        confidence: data.confidence
      }

      setMessages(prev => [...prev, aiMessage])

      // Track chatbot response received
      // trackBusinessEvents.chatbotInteraction('message_sent')

    } catch (error) {
      console.error('Errore chat:', error)
      setConnectionStatus('offline')

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `❌ ${error instanceof Error ? error.message : 'Errore di connessione. Riprova tra poco.'}`,
        sender: 'system',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])

      toast.error('Errore durante l\'invio del messaggio')
    } finally {
      setIsLoading(false)
    }
  }

  const escalateToHuman = async (currentTicketId?: number, reason?: string) => {
    if (!currentTicketId && !ticketId) return

    try {
      const token = localStorage.getItem('token')

      // If no token, show contact message instead
      if (!token) {
        const contactMessage: Message = {
          id: Date.now().toString(),
          content: `${t.chat.contactUs}\n\n${t.chat.contactForm}`,
          sender: 'system',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, contactMessage])
        toast.info(t.chat.contactUs)
        return
      }

      const response = await fetch(`/support/tickets/${currentTicketId || ticketId}/escalate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          reason: reason || 'Richiesta escalation manuale dall\'utente',
          priority: 'high'
        })
      })

      if (response.ok) {
        const escalationMessage: Message = {
          id: Date.now().toString(),
          content: t.chat.transferred,
          sender: 'system',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, escalationMessage])
        toast.success(t.chat.transferred)
      } else {
        throw new Error('Errore durante l\'escalation')
      }
    } catch (error) {
      console.error('Errore escalation:', error)
      toast.error('Errore durante il trasferimento')
    }
  }

  const clearChat = () => {
    setMessages([])
    setTicketId(null)
    setIsOpen(false)
    setTimeout(() => setIsOpen(true), 100)
  }

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'online': return 'bg-gold'
      case 'connecting': return 'bg-gold'
      case 'offline': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'online': return t.chat.online
      case 'connecting': return t.chat.connecting
      case 'offline': return t.chat.offline
      default: return t.chat.offline
    }
  }

  return (
    <>
      {/* Chat Button - Mobile Responsive */}
      {!isOpen && (
        <button
          onClick={() => {
            setIsOpen(true);
          }}
          className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 w-14 h-14 sm:w-16 sm:h-16 z-[9999] group transition-all duration-300 hover:scale-110"
          aria-label={t.chat.openChat}
        >
          {/* Outer glow ring */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-gold to-gold/60 opacity-20 blur-lg group-hover:opacity-40 transition-opacity" />

          {/* Main button */}
          <div className="relative w-full h-full rounded-full bg-background border-2 border-gold flex items-center justify-center shadow-2xl group-hover:border-gold/80 transition-all">
            {/* Icon - Headset per customer support */}
            <svg
              viewBox="0 0 24 24"
              className="w-7 h-7 text-gold group-hover:text-gold/80 transition-colors"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M3 11c0-3.771 0-5.657 1.172-6.828C5.343 3 7.229 3 11 3h2c3.771 0 5.657 0 6.828 1.172C21 5.343 21 7.229 21 11v1c0 3.771 0 5.657-1.172 6.828C18.657 20 16.771 20 13 20h-2c-3.771 0-5.657 0-6.828-1.172C3 17.657 3 15.771 3 12v-1z" />
              <path d="M8 14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2h1a2 2 0 0 1 2 2v1zM16 14a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-1a2 2 0 0 0-2-2h-1a2 2 0 0 0-2 2v1z" />
            </svg>

            {/* Pulse animation */}
            <div className="absolute inset-0 rounded-full border-2 border-gold animate-ping opacity-20" />
          </div>

          {/* Message badge - Only show unread count */}
          {(() => {
            const unreadCount = messages.filter(m => !m.isRead && m.sender !== 'user').length
            return unreadCount > 0 && (
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-gold text-white text-xs font-bold rounded-full flex items-center justify-center shadow-lg border-2 border-background">
                {unreadCount}
              </div>
            )
          })()}
        </button>
      )}

      {/* Chat Window - Full screen on mobile, optimized for 375px and below */}
      {isOpen && (
        <div className={`fixed z-[9999] transition-all duration-300 shadow-2xl flex flex-col bg-card border border-border ${isMinimized
          ? 'bottom-4 right-4 sm:bottom-6 sm:right-6 w-72 sm:w-80 h-16 rounded-xl'
          : 'inset-0 sm:inset-auto sm:bottom-6 sm:right-6 sm:w-[min(400px,calc(100vw-3rem))] h-[100dvh] sm:h-[600px] sm:max-h-[calc(100dvh-3rem)] sm:rounded-xl'
          }`}>
          {/* Header - fixed height */}
          <div className="flex-shrink-0 p-4 bg-background border-b border-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-lg">
                <svg viewBox="0 0 24 24" className="h-5 w-5 text-gold" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M8 14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2h1a2 2 0 0 1 2 2v1zM16 14a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-1a2 2 0 0 0-2-2h-1a2 2 0 0 0-2 2v1z" />
                </svg>
                <span className="text-gold font-medium">{t.chat.title}</span>
                <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
              </div>
              <div className="flex items-center gap-1">
                <Badge variant="secondary" className="text-xs bg-gold/20 text-gold border border-gold/40">
                  {getStatusText()}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="text-gold hover:bg-secondary h-8 w-8 p-0"
                >
                  <Minimize2 className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="text-gold hover:bg-secondary h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages Area - scrollable */}
              <div className="flex-1 min-h-0 overflow-y-auto overscroll-contain p-4 space-y-4 bg-background [-webkit-overflow-scrolling:touch]">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[90%] sm:max-w-[85%] p-3 sm:p-4 rounded-xl shadow-sm transition-all hover:shadow-md ${message.sender === 'user'
                        ? 'bg-gold text-white'
                        : message.sender === 'system'
                          ? 'bg-warning/10 text-warning-foreground border border-warning/20'
                          : 'bg-muted text-foreground'
                        }`}
                    >
                      <div className="flex items-start gap-2">
                        {message.sender !== 'user' && (
                          <div className="flex-shrink-0 mt-0.5">
                            {message.sender === 'ai' ? (
                              <div className="h-10 w-10 rounded-full bg-gold/10 flex items-center justify-center">
                                <svg viewBox="0 0 24 24" className="h-4 w-4 text-gold" fill="none" stroke="currentColor" strokeWidth="2">
                                  <path d="M8 14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2h1a2 2 0 0 1 2 2v1zM16 14a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-1a2 2 0 0 0-2-2h-1a2 2 0 0 0-2 2v1z" />
                                </svg>
                              </div>
                            ) : message.sender === 'system' ? (
                              <AlertCircle className="h-4 w-4 text-warning" />
                            ) : (
                              <User className="h-4 w-4 text-gold" />
                            )}
                          </div>
                        )}
                        <div className="flex-1">
                          <div className="text-sm leading-relaxed">
                            <div
                              className="text-foreground"
                              dangerouslySetInnerHTML={{
                                __html: message.content
                                  .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gold">$1</strong>')
                                  .replace(/^\* /gm, '<span class="text-gold">•</span> ')
                                  .replace(/^- /gm, '<span class="text-gold">•</span> ')
                                  .replace(/\n/g, '<br />')
                              }}
                            />
                          </div>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs opacity-70">
                              {message.timestamp.toLocaleTimeString('it-IT', {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </span>
                            {message.confidence !== undefined && (
                              <div className="flex items-center gap-2">
                                <Badge
                                  variant={message.confidence > 0.8 ? "default" : message.confidence > 0.6 ? "secondary" : "destructive"}
                                  className="text-xs"
                                >
                                  {Math.round(message.confidence * 100)}%
                                </Badge>
                                {message.confidence < 0.6 && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => escalateToHuman(ticketId, "Bassa confidenza rilevata")}
                                    className="text-xs h-6 px-2"
                                  >
                                    <AlertCircle className="h-3 w-3 mr-1" />
                                    Operatore
                                  </Button>
                                )}
                              </div>
                            )}
                          </div>
                          {message.metadata && (
                            <div className="text-xs opacity-60 mt-1">
                              {message.metadata.provider && `${message.metadata.provider}`}
                              {message.metadata.model && ` • ${message.metadata.model}`}
                              {message.metadata.tokens_used && ` • ${message.metadata.tokens_used} tokens`}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-muted text-foreground p-4 rounded-xl max-w-[85%]">
                      <div className="flex items-center gap-2">
                        <div className="h-10 w-10 rounded-full bg-gold/10 flex items-center justify-center">
                          <svg viewBox="0 0 24 24" className="h-4 w-4 text-gold" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M8 14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1a2 2 0 0 1 2-2h1a2 2 0 0 1 2 2v1zM16 14a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-1a2 2 0 0 0-2-2h-1a2 2 0 0 0-2 2v1z" />
                          </svg>
                        </div>
                        <Loader2 className="h-4 w-4 animate-spin text-gold" />
                        <span className="text-sm text-muted-foreground">{t.chat.thinking}</span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area - fixed at bottom */}
              <div className="flex-shrink-0 p-4 border-t border-border bg-background">
                {ticketId && (
                  <div className="flex items-center justify-between mb-2 text-xs text-gray-500">
                    <span>{t.chat.ticket} #{ticketId}</span>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => escalateToHuman(ticketId)}
                        className="text-xs h-6 px-2"
                      >
                        {t.chat.humanOperator}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={clearChat}
                        className="text-xs h-6 px-2"
                      >
                        {t.chat.newChat}
                      </Button>
                    </div>
                  </div>
                )}
                <div className="flex gap-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={t.chat.placeholder}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                    disabled={isLoading || connectionStatus === 'offline'}
                    className="w-full px-3 py-2 sm:px-4 sm:py-3 bg-background border border-input rounded-lg text-sm sm:text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-gold focus:border-transparent flex-1"
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={isLoading || !inputMessage.trim() || connectionStatus === 'offline'}
                    size="sm"
                    className="px-3 sm:px-4 py-2 sm:py-3 min-w-[44px] sm:min-w-[48px] text-lg font-medium text-white bg-gold rounded-lg hover:bg-gold/90 focus:outline-none focus:ring-2 focus:ring-gold focus:ring-offset-2 transition-colors"
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 sm:h-5 sm:w-5 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4 sm:h-5 sm:w-5" />
                    )}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  {t.chat.poweredBy}
                </p>
              </div>
            </>
          )}
        </div>
      )}
    </>
  )
}
