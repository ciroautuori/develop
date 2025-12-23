import * as React from "react"
import { useState, useRef, useEffect } from "react"
import { MessageCircle, X, Send, Loader2 } from "lucide-react"
import { Button } from "./button"
import { cn } from "../../lib/utils"

interface Message {
  id: string
  content: string
  isUser: boolean
  timestamp: Date
}

interface ChatWidgetProps {
  className?: string
}

export function ChatWidget({ className }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      content: "Ciao! Sono l'assistente AI di StudioCentOS. Come posso aiutarti?",
      isUser: false,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      // Chiamata AI reale via Nginx proxy
      const response = await fetch('/ai/api/v1/demo/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputValue,
          provider: 'demo'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.answer || "Mi dispiace, non riesco a rispondere al momento. Riprova più tardi.",
        isUser: false,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error("Errore invio messaggio:", error)

      // Fallback message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Mi dispiace, sto avendo difficoltà tecniche. Per assistenza immediata contatta info@studiocentos.it o chiama il nostro ufficio di Salerno.",
        isUser: false,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className={cn("fixed z-50", className)}>
      {/* Chat Button - Mobile First - Floating Gold Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        size="icon"
        className={cn(
          "fixed bottom-6 right-6 h-16 w-16 rounded-full shadow-lg transition-all duration-300",
          "bg-gold hover:bg-gold/90 text-white",
          "sm:bottom-8 sm:right-8 sm:h-14 sm:w-14",
          isOpen && "rotate-180"
        )}
      >
        {isOpen ? (
          <X className="h-8 w-8 sm:h-6 sm:w-6" />
        ) : (
          <MessageCircle className="h-8 w-8 sm:h-6 sm:w-6" />
        )}
      </Button>

      {/* Chat Window - PURE TAILWIND - Identical everywhere */}
      {isOpen && (
        <div className={cn(
          "fixed bottom-24 right-6 w-[calc(100vw-48px)] max-w-[400px]",
          "sm:bottom-28 sm:right-8 sm:w-96",
          "flex flex-col rounded-2xl overflow-hidden",
          "bg-card/95 backdrop-blur-xl border border-border shadow-2xl",
          "h-[70vh] max-h-[500px]"
        )}>
          {/* Header - Gold accent */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center h-10 w-10 rounded-full bg-gold/10">
                <MessageCircle className="h-5 w-5 text-gold" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground text-sm">StudioCentOS AI</h3>
                <p className="text-xs text-muted-foreground">Assistente virtuale</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 rounded-full hover:bg-muted transition-colors"
              aria-label="Chiudi chat"
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-background/50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex",
                  message.isUser ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                    message.isUser
                      ? "bg-gold text-white rounded-br-sm"
                      : "bg-muted text-foreground rounded-bl-sm"
                  )}
                >
                  {message.content}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-3">
                  <Loader2 className="h-5 w-5 animate-spin text-gold" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-3 border-t border-border bg-card">
            <div className="flex gap-2">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Scrivi un messaggio..."
                className={cn(
                  "flex-1 resize-none rounded-xl px-4 py-3 text-sm",
                  "bg-muted border-0 text-foreground placeholder:text-muted-foreground",
                  "focus:outline-none focus:ring-2 focus:ring-gold/50",
                  "disabled:opacity-50"
                )}
                rows={1}
                disabled={isLoading}
              />
              <Button
                onClick={sendMessage}
                size="icon"
                disabled={!inputValue.trim() || isLoading}
                className="h-12 w-12 rounded-xl shrink-0"
              >
                <Send className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
