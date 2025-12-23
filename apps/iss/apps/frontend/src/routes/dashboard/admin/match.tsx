
import { createFileRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/dashboard/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Sparkles, Target, ThumbsUp, AlertTriangle, ExternalLink } from 'lucide-react'

export const Route = createFileRoute('/dashboard/admin/match')({
    component: MatchPage,
})

interface MatchResult {
    id: number
    title: string
    ente: string
    match_score: number
    match_reasoning: string
    match_strengths: string[]
    match_weaknesses: string[]
    link: string
    scadenza_raw: string
}

function MatchPage() {
    const { data: matches, isLoading, refetch } = useQuery<MatchResult[]>({
        queryKey: ['best-matches'],
        queryFn: async () => {
            const response = await fetch('/api/v1/bandi/best-matches?limit=5')
            if (!response.ok) throw new Error('Errore analisi match')
            return response.json()
        },
        staleTime: 300000, // 5 minuti cache
        refetchOnWindowFocus: false,
    })

    return (
        <DashboardLayout
            title="Analisi Perfect Tender"
            description="L'IA analizza i bandi compatibili con il profilo di Innovazione Sociale Salernitana"
            userRole="admin"
            action={
                <Button onClick={() => refetch()} disabled={isLoading}>
                    <Sparkles className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                    {isLoading ? 'Analisi in corso...' : 'Rianalizza Compatibilità'}
                </Button>
            }
        >
            <div className="space-y-6">
                {/* Intro Card */}
                <Card className="bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-100">
                    <CardContent className="pt-6">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-white rounded-full shadow-sm">
                                <Target className="h-6 w-6 text-indigo-600" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-indigo-900">Profilo di Matching Attivo</h3>
                                <p className="text-sm text-indigo-700 mt-1">
                                    Analisi basata su: <strong>Inclusione Digitale, Terzo Settore, Disabilità, Giovani</strong>.
                                    <br />
                                    Target: Over 65, NEET. Area: Salerno/Campania.
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Results */}
                {isLoading && matches === undefined ? (
                    <div className="text-center py-12">
                        <Sparkles className="h-12 w-12 mx-auto text-indigo-300 animate-pulse mb-4" />
                        <h3 className="text-lg font-medium text-gray-900">L'IA sta leggendo i bandi per te...</h3>
                        <p className="text-gray-500">Confronto semantico in corso su {20} bandi recenti.</p>
                    </div>
                ) : (
                    <div className="grid gap-6">
                        {matches?.map((match) => (
                            <Card key={match.id} className="overflow-hidden border-l-4" style={{ borderLeftColor: getScoreColor(match.match_score) }}>
                                <CardHeader className="pb-2">
                                    <div className="flex justify-between items-start gap-4">
                                        <div>
                                            <CardTitle className="text-xl text-gray-900">
                                                {match.title}
                                            </CardTitle>
                                            <CardDescription className="flex items-center gap-2 mt-1">
                                                <span className="font-medium text-gray-700">{match.ente}</span> •
                                                <span className="text-gray-500">{match.scadenza_raw || 'Scadenza non rilevata'}</span>
                                            </CardDescription>
                                        </div>
                                        <div className="text-center shrink-0">
                                            <div className="text-2xl font-bold" style={{ color: getScoreColor(match.match_score) }}>
                                                {match.match_score}%
                                            </div>
                                            <span className="text-xs text-gray-500 uppercase font-bold tracking-wider">Compatibilità</span>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="mb-4">
                                        <Progress value={match.match_score} className="h-2" color={getScoreColor(match.match_score)} />
                                    </div>

                                    <div className="bg-gray-50 p-4 rounded-lg mb-4 text-gray-700 text-sm italic border border-gray-100">
                                        " {match.match_reasoning} "
                                    </div>

                                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <h4 className="flex items-center gap-2 text-sm font-semibold text-green-700 mb-2">
                                                <ThumbsUp className="h-4 w-4" /> Punti di Forza
                                            </h4>
                                            <ul className="space-y-1">
                                                {match.match_strengths?.map((s, i) => (
                                                    <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                                                        <span className="text-green-500 mt-1">•</span> {s}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                        <div>
                                            <h4 className="flex items-center gap-2 text-sm font-semibold text-amber-700 mb-2">
                                                <AlertTriangle className="h-4 w-4" /> Attenzione a
                                            </h4>
                                            <ul className="space-y-1">
                                                {match.match_weaknesses?.map((w, i) => (
                                                    <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                                                        <span className="text-amber-500 mt-1">•</span> {w}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>

                                    <div className="flex justify-end pt-2">
                                        <Button variant="outline" size="sm" onClick={() => window.open(match.link, '_blank')}>
                                            <ExternalLink className="h-4 w-4 mr-2" />
                                            Vai al Bando
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}

                        {matches?.length === 0 && (
                            <div className="text-center py-12 bg-gray-50 rounded-lg">
                                <Target className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                                <h3 className="text-lg font-medium">Nessun "Perfect Match" trovato</h3>
                                <p className="text-gray-500">Nessun bando recente supera la soglia del 60% di compatibilità.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </DashboardLayout>
    )
}

function getScoreColor(score: number): string {
    if (score >= 85) return '#16a34a' // Green-600
    if (score >= 70) return '#ea580c' // Orange-600
    return '#ca8a04' // Yellow-600
}
