import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../../../../../shared/components/ui/dialog';
import { Button } from '../../../../../shared/components/ui/button';
import { Loader2, Search, TrendingUp, FileText, CheckCircle2, Target } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '../../../../../shared/lib/utils';

// Interfaces matching backend
interface Keyword {
    keyword: string;
    search_volume: number;
    difficulty: string;
    intent: string;
}

interface ContentPlanItem {
    target_keyword: string;
    suggested_title: string;
    content_type: string;
    potential_traffic: number;
}

interface SEOStrategyResponse {
    keywords: Keyword[];
    content_plan: ContentPlanItem[];
    competitor_insights: string[];
}

interface SEOStrategyModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function SEOStrategyModal({ isOpen, onClose }: SEOStrategyModalProps) {
    const [isGenerating, setIsGenerating] = useState(false);
    const [result, setResult] = useState<SEOStrategyResponse | null>(null);

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            const token = localStorage.getItem('admin_token');
            const res = await fetch('/api/v1/marketing/seo/strategy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    seed_topics: ["Web Agency AI", "Sviluppo Web Enterprise", "Consulenza SEO"],
                    website_url: "https://studiocentos.com"
                })
            });

            if (!res.ok) throw new Error("Errore generazione strategia");

            const data = await res.json();
            setResult(data);
            toast.success("Strategia SEO Generata con Successo!");

        } catch (error) {
            console.error(error);
            toast.error("Errore durante la generazione della strategia");
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !isGenerating && onClose()}>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto border-gold/20">
                <DialogHeader className="border-b border-gold/10 pb-4">
                    <DialogTitle className="flex items-center gap-2 text-2xl text-gold">
                        <Search className="w-6 h-6 text-gold" />
                        Strategia SEO & Content Plan
                    </DialogTitle>
                    <DialogDescription>
                        Analisi automatica delle keyword e piano editoriale per dominare la nicchia.
                    </DialogDescription>
                </DialogHeader>

                {!result ? (
                    <div className="py-12 text-center space-y-6">
                        <div className="w-20 h-20 mx-auto rounded-full bg-gold/10 flex items-center justify-center animate-pulse">
                            <TrendingUp className="w-10 h-10 text-gold" />
                        </div>
                        <div className="max-w-md mx-auto">
                            <h3 className="text-lg font-medium mb-2">Genera il tuo Piano d'Attacco</h3>
                            <p className="text-muted-foreground mb-6">
                                L'Agente SEO analizzerà i volumi di ricerca, la competizione e genererà un piano contenuti per posizionare StudioCentOS.
                            </p>
                            <Button
                                onClick={handleGenerate}
                                size="lg"
                                className="w-full bg-gradient-to-r from-gold to-yellow-600 hover:from-yellow-600 hover:to-gold text-white border-0 shadow-lg shadow-gold/20 transition-all duration-300"
                                disabled={isGenerating}
                            >
                                {isGenerating ? (
                                    <>
                                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                        Analisi in corso... (richiede ~30s)
                                    </>
                                ) : (
                                    <>
                                        <Target className="w-5 h-5 mr-2" />
                                        Genera Strategia Ora
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-8 animate-in fade-in duration-500">
                        {/* Keywords Section */}
                        <section>
                            <h3 className="text-lg font-semibold flex items-center gap-2 mb-4 text-gold">
                                <Target className="w-5 h-5 text-gold" />
                                Keyword Opportunità (Top 10)
                            </h3>
                            <div className="bg-card border border-gold/20 rounded-xl overflow-hidden shadow-sm">
                                <table className="w-full text-sm">
                                    <thead className="bg-gold/5">
                                        <tr>
                                            <th className="px-4 py-3 text-left font-medium text-gold">Keyword</th>
                                            <th className="px-4 py-3 text-left font-medium text-gold">Volume</th>
                                            <th className="px-4 py-3 text-left font-medium text-gold">Difficoltà</th>
                                            <th className="px-4 py-3 text-left font-medium text-gold">Intento</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {result.keywords.slice(0, 10).map((kw, idx) => (
                                            <tr key={idx} className="border-t border-gold/10 hover:bg-gold/5 transition-colors">
                                                <td className="px-4 py-3 font-medium">{kw.keyword}</td>
                                                <td className="px-4 py-3 text-muted-foreground">{kw.search_volume}</td>
                                                <td className="px-4 py-3">
                                                    <span className={cn(
                                                        "px-2 py-1 rounded-full text-xs font-medium border",
                                                        kw.difficulty === 'hard' ? "bg-red-500/10 text-red-500 border-red-500/20" :
                                                            kw.difficulty === 'medium' ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20" :
                                                                "bg-green-500/10 text-green-500 border-green-500/20"
                                                    )}>
                                                        {kw.difficulty}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3 text-muted-foreground capitalize">{kw.intent}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>

                        {/* Content Plan Section */}
                        <section>
                            <h3 className="text-lg font-semibold flex items-center gap-2 mb-4 text-gold">
                                <FileText className="w-5 h-5 text-gold" />
                                Piano Editoriale Suggerito
                            </h3>
                            <div className="grid gap-3">
                                {result.content_plan.map((item, idx) => (
                                    <div key={idx} className="p-4 rounded-xl border border-gold/10 bg-card hover:border-gold/50 hover:bg-gold/5 transition-all duration-300 group">
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="text-xs font-bold text-gold uppercase tracking-wider bg-gold/10 px-2 py-0.5 rounded-full">
                                                {item.content_type}
                                            </span>
                                            <span className="text-xs text-muted-foreground flex items-center gap-1 group-hover:text-gold transition-colors">
                                                <TrendingUp className="w-3 h-3" />
                                                Potenziale: {item.potential_traffic} visite/mese
                                            </span>
                                        </div>
                                        <h4 className="font-semibold text-lg mb-1">{item.suggested_title}</h4>
                                        <p className="text-sm text-muted-foreground">Target: <span className="font-medium text-foreground">{item.target_keyword}</span></p>
                                    </div>
                                ))}
                            </div>
                        </section>

                        <div className="flex justify-end pt-4">
                            <Button onClick={() => setResult(null)} variant="outline" className="border-gold/20 hover:border-gold hover:text-gold hover:bg-gold/5">
                                Nuova Analisi
                            </Button>
                        </div>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    );
}
