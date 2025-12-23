import { useState } from 'react'
import { MessageSquare, Bot, Users, BarChart3 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card'
import { Button } from '../../../shared/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../shared/components/ui/tabs'
import { ChatWidget } from '../components/ChatWidget'
import { TicketList } from '../components/TicketList'
import { TicketDetail } from '../components/TicketDetail'
import { SupportAnalytics } from '../components/SupportAnalytics'

export function SupportDashboard() {
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState('chat')

  const handleTicketSelect = (ticketId: number) => {
    setSelectedTicketId(ticketId)
    setActiveTab('tickets')
  }

  const handleCloseTicketDetail = () => {
    setSelectedTicketId(null)
  }

  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Centro Assistenza</h1>
        <p className="text-gray-600">
          Ottieni supporto immediato dal nostro assistente AI o consulta i tuoi ticket esistenti
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <Bot className="h-4 w-4" />
            Chat AI
          </TabsTrigger>
          <TabsTrigger value="tickets" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            I miei Ticket
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Statistiche
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chat Area */}
            <div className="lg:col-span-2">
              <Card className="h-[600px]">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-gold" />
                    Assistente AI
                  </CardTitle>
                  <p className="text-sm text-gray-600">
                    Chatta con il nostro assistente AI per ottenere supporto immediato
                  </p>
                </CardHeader>
                <CardContent className="h-[500px] p-0">
                  <div className="h-full bg-gray-50 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <Bot className="h-16 w-16 mx-auto mb-4 opacity-50" />
                      <p className="text-lg font-medium mb-2">Assistente AI Pronto</p>
                      <p className="text-sm mb-4">
                        Usa il widget chat in basso a destra per iniziare una conversazione
                      </p>
                      <Button
                        onClick={() => {
                          // Trigger chat widget opening
                          const event = new CustomEvent('openChatWidget')
                          window.dispatchEvent(event)
                        }}
                        className="flex items-center gap-2"
                      >
                        <MessageSquare className="h-4 w-4" />
                        Inizia Chat
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Azioni Rapide</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => setActiveTab('tickets')}
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Visualizza tutti i ticket
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => {
                      const event = new CustomEvent('openChatWidget')
                      window.dispatchEvent(event)
                    }}
                  >
                    <Bot className="h-4 w-4 mr-2" />
                    Nuova chat AI
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => setActiveTab('analytics')}
                  >
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Visualizza statistiche
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Suggerimenti</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm space-y-2">
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-gold rounded-full mt-2 flex-shrink-0" />
                      <p>Descrivi il problema in modo dettagliato per ottenere risposte più precise</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-gold rounded-full mt-2 flex-shrink-0" />
                      <p>L'AI può aiutarti con problemi comuni, login, configurazioni e troubleshooting</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-gold rounded-full mt-2 flex-shrink-0" />
                      <p>Per problemi complessi, il ticket verrà automaticamente escalato a un operatore</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="tickets" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Ticket List */}
            <div>
              <TicketList
                onTicketSelect={handleTicketSelect}
                selectedTicketId={selectedTicketId || undefined}
              />
            </div>

            {/* Ticket Detail */}
            <div>
              {selectedTicketId ? (
                <TicketDetail
                  ticketId={selectedTicketId}
                  onClose={handleCloseTicketDetail}
                />
              ) : (
                <Card className="h-full">
                  <CardContent className="flex items-center justify-center h-96">
                    <div className="text-center text-gray-500">
                      <MessageSquare className="h-16 w-16 mx-auto mb-4 opacity-50" />
                      <p className="text-lg font-medium mb-2">Seleziona un Ticket</p>
                      <p className="text-sm">
                        Clicca su un ticket dalla lista per visualizzarne i dettagli e la conversazione
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <SupportAnalytics />
        </TabsContent>
      </Tabs>

      {/* Chat Widget - Always Available */}
      <ChatWidget />
    </div>
  )
}
