import { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Clock, Bot, Users, MessageSquare, Zap, Target } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/card'
import { Badge } from '../../../shared/components/ui/badge'
import { Progress } from '../../../shared/components/ui/progress'

interface SupportMetrics {
  total_tickets: number
  open_tickets: number
  resolved_tickets: number
  ai_handled_percentage: number
  avg_response_time: number
  avg_resolution_time: number
  customer_satisfaction: number
}

interface AIProviderStats {
  provider: string
  requests: number
  success_rate: number
  avg_confidence: number
  avg_response_time: number
  total_tokens: number
  estimated_cost: number
}

interface AnalyticsData {
  metrics: SupportMetrics
  ai_providers: AIProviderStats[]
  ticket_trends: {
    daily_created: number[]
    daily_resolved: number[]
    labels: string[]
  }
  category_distribution: Record<string, number>
  sentiment_analysis: Record<string, number>
}

export function SupportAnalytics() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState(7)

  useEffect(() => {
    fetchAnalytics()
  }, [timeRange])

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/support/analytics?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <Card key={i}>
            <CardContent className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!analytics) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center text-gray-500">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Impossibile caricare le statistiche</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const { metrics, ai_providers, category_distribution, sentiment_analysis } = analytics

  return (
    <div className="space-y-6">
      {/* Time Range Selector */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Statistiche Supporto</h2>
        <div className="flex gap-2">
          {[7, 30, 90].map((days) => (
            <button
              key={days}
              onClick={() => setTimeRange(days)}
              className={`px-3 py-1 text-sm rounded-md ${
                timeRange === days
                  ? 'bg-gold text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {days} giorni
            </button>
          ))}
        </div>
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ticket Totali</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.total_tickets}</div>
            <p className="text-xs text-muted-foreground">
              {metrics.open_tickets} aperti, {metrics.resolved_tickets} risolti
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risolti da AI</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(metrics.ai_handled_percentage)}%</div>
            <Progress value={metrics.ai_handled_percentage} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tempo Risposta</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.avg_response_time}s</div>
            <p className="text-xs text-muted-foreground">
              Media risposta AI
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Soddisfazione</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.customer_satisfaction.toFixed(1)}/5</div>
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <span
                  key={i}
                  className={`text-sm ${
                    i < Math.floor(metrics.customer_satisfaction) ? 'text-gold' : 'text-gray-300'
                  }`}
                >
                  ★
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Providers Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Performance Provider AI</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {ai_providers.map((provider) => (
              <div key={provider.provider} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="capitalize">
                      {provider.provider}
                    </Badge>
                    <span className="text-sm text-gray-600">
                      {provider.requests} richieste
                    </span>
                  </div>
                  <div className="text-sm font-medium">
                    {Math.round(provider.success_rate * 100)}% successo
                  </div>
                </div>
                <Progress value={provider.success_rate * 100} className="h-2" />
                <div className="grid grid-cols-3 gap-4 text-xs text-gray-500">
                  <div>
                    Confidenza: {Math.round(provider.avg_confidence * 100)}%
                  </div>
                  <div>
                    Tempo: {provider.avg_response_time.toFixed(1)}s
                  </div>
                  <div>
                    Costo: ${provider.estimated_cost.toFixed(3)}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Distribuzione per Categoria</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(category_distribution).map(([category, count]) => {
              const total = Object.values(category_distribution).reduce((a, b) => a + b, 0)
              const percentage = (count / total) * 100

              return (
                <div key={category} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="capitalize">{category}</span>
                    <span className="font-medium">{count} ({percentage.toFixed(1)}%)</span>
                  </div>
                  <Progress value={percentage} className="h-2" />
                </div>
              )
            })}
          </CardContent>
        </Card>
      </div>

      {/* Sentiment Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Analisi Sentiment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(sentiment_analysis).map(([sentiment, count]) => {
              const total = Object.values(sentiment_analysis).reduce((a, b) => a + b, 0)
              const percentage = (count / total) * 100

              const getColor = (sentiment: string) => {
                switch (sentiment) {
                  case 'positive': return 'bg-gold'
                  case 'negative': return 'bg-gray-500'
                  default: return 'bg-gray-500'
                }
              }

              const getEmoji = (sentiment: string) => {
                switch (sentiment) {
                  case 'positive': return '😊'
                  case 'negative': return '😞'
                  default: return '😐'
                }
              }

              return (
                <div key={sentiment} className="flex items-center gap-3">
                  <span className="text-lg">{getEmoji(sentiment)}</span>
                  <div className="flex-1">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="capitalize">{sentiment}</span>
                      <span className="font-medium">{percentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getColor(sentiment)}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Metriche Tempo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-gold" />
                <span className="text-sm">Tempo Medio Risposta</span>
              </div>
              <span className="font-medium">{metrics.avg_response_time}s</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-gold" />
                <span className="text-sm">Tempo Medio Risoluzione</span>
              </div>
              <span className="font-medium">{Math.round(metrics.avg_resolution_time)}min</span>
            </div>
            <div className="pt-2 border-t">
              <div className="text-xs text-gray-500 space-y-1">
                <p>• Risposta AI: ~2 secondi</p>
                <p>• Escalation umana: ~5 minuti</p>
                <p>• Risoluzione completa: ~2 ore</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Efficienza Sistema</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-gold mb-2">
                {Math.round(metrics.ai_handled_percentage)}%
              </div>
              <p className="text-sm text-gray-600">Ticket risolti automaticamente</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Efficienza AI</span>
                <span className="font-medium">Ottima</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Costi operativi</span>
                <span className="font-medium text-gold">-78%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Soddisfazione utenti</span>
                <span className="font-medium text-gold">+45%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
