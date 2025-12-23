/**
 * ToolAI Section - Landing Page
 * Shows latest AI tools and trends
 * Design System Compliant (Shadcn + Tailwind)
 */

import { motion } from 'framer-motion';
import {
  Sparkles,
  ArrowRight,
  Cpu,
  Image as ImageIcon,
  Mic,
  Code,
  Video,
  Boxes,
  Star,
  TrendingUp,
  Loader2,
  Calendar
} from 'lucide-react';
import { useLanguage } from '../i18n';
import { useLatestToolAI } from '../hooks/useToolAI';
import { Button } from '../../../shared/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../../shared/components/ui/card';
import { Badge } from '../../../shared/components/ui/badge';
import { Link } from 'react-router-dom';
import { cn } from '../../../shared/lib/utils';
import { BuyMeCoffeeButton } from '../../../shared/components/ui/BuyMeCoffeeButton';
import type { AITool } from '../types/toolai.types';

const CATEGORY_ICONS: Record<string, any> = {
  llm: Cpu,
  image: ImageIcon,
  audio: Mic,
  code: Code,
  video: Video,
  multimodal: Boxes,
};

export function ToolAISection() {
  const { t, language } = useLanguage();
  const { post, loading } = useLatestToolAI(language);

  // Fallback / Loading Skeleton Logic
  const topTool: AITool | undefined = post?.tools?.[0];
  // Ensure Icon is a valid component (fallback to Sparkles)
  const Icon = (topTool?.category && CATEGORY_ICONS[topTool.category]) || Sparkles;

  return (
    <section id="toolai" className="py-12 md:py-24 bg-background relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-12 lg:gap-20 items-center">

          {/* LEFT: Text & Value Proposition */}
          <div className="space-y-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Badge variant="outline" className="border-primary/30 text-primary bg-primary/5 px-3 py-1 text-sm font-medium rounded-full">
                  <Sparkles className="w-3.5 h-3.5 mr-2 animate-pulse" />
                  {t.toolai.titleHighlight || "AI Daily"}
                </Badge>
              </div>

              <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-foreground leading-tight">
                {t.toolai.title} <br />
                <span className="text-primary">{t.toolai.subtitle ? "Intelligence" : t.toolai.titleHighlight}</span>
              </h2>
            </div>

            <p className="text-base md:text-lg text-muted-foreground leading-relaxed max-w-xl">
              {t.toolai.subtitle}
            </p>

            <div className="flex flex-wrap gap-4">
              <Button asChild size="lg" className="rounded-full px-6 md:px-8 text-sm md:text-base font-semibold shadow-lg shadow-primary/10 w-full sm:w-auto">
                <Link to="/toolai">
                  {t.toolai.viewAll}
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Link>
              </Button>
              <BuyMeCoffeeButton />
            </div>
          </div>

          {/* RIGHT: Functional "Daily Tool" Card */}
          <div className="relative">
            {/* Decorative blob behind */}
            <div className="absolute -inset-4 bg-gradient-to-tr from-primary/20 to-transparent rounded-[2rem] blur-3xl opacity-50 -z-10" />

            {loading ? (
              <Card className="h-[400px] flex items-center justify-center border-border/60 shadow-xl">
                <div className="flex flex-col items-center gap-3 text-muted-foreground">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  <p className="text-sm font-medium">{t.loading.text}</p>
                </div>
              </Card>
            ) : topTool ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                <Card className="border-border shadow-2xl relative overflow-hidden group hover:border-primary/30 transition-all duration-300">
                  <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-primary to-primary/60" />

                  <CardHeader className="space-y-4 pb-4">
                    <div className="flex justify-between items-start">
                      <Badge variant="secondary" className="bg-primary/10 text-primary-foreground text-primary hover:bg-primary/20 font-semibold uppercase tracking-wider text-xs">
                        TODAY'S TOP PICK
                      </Badge>
                      <span className="text-xs font-mono text-muted-foreground flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date().toLocaleDateString()}
                      </span>
                    </div>

                    <div className="flex items-start gap-4">
                      <div className={cn("p-3 rounded-xl bg-muted text-foreground ring-1 ring-border group-hover:ring-primary/50 transition-all")}>
                        <Icon className="w-8 h-8" />
                      </div>
                      <div>
                        <CardTitle className="text-2xl font-bold leading-none mb-2 group-hover:text-primary transition-colors">
                          {topTool.name}
                        </CardTitle>
                        <CardDescription className="font-medium text-sm flex items-center gap-2">
                          {topTool.category?.toUpperCase()}
                          {topTool.source && (
                            <>
                              <span>•</span>
                              <span className="opacity-75">{topTool.source}</span>
                            </>
                          )}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-6">
                    <p className="text-muted-foreground text-sm leading-relaxed line-clamp-3">
                      {topTool.description_it || topTool.description_en || "Nessuna descrizione disponibile."}
                    </p>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 gap-4 py-4 border-y border-border/50 bg-muted/20 -mx-6 px-6">
                      <div>
                        <div className="text-xs text-muted-foreground uppercase font-bold tracking-wider mb-1">Trending Score</div>
                        <div className="flex items-center gap-2 text-primary font-bold text-lg">
                          <TrendingUp className="w-4 h-4" />
                          {topTool.trending_score || "N/A"}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-muted-foreground uppercase font-bold tracking-wider mb-1">GitHub Stars</div>
                        <div className="flex items-center gap-2 text-foreground font-bold text-lg">
                          <Star className="w-4 h-4 text-orange-400 fill-orange-400" />
                          {topTool.stars ? (topTool.stars / 1000).toFixed(1) + 'k' : "N/A"}
                        </div>
                      </div>
                    </div>
                  </CardContent>

                  <CardFooter className="pt-2">
                    <Button asChild className="w-full font-bold shadow-md" size="lg">
                      <Link to={`/toolai/${post?.slug}`}>
                        {t.toolai.readMore || "View Full Analysis"}
                        <ArrowRight className="ml-2 w-4 h-4" />
                      </Link>
                    </Button>
                  </CardFooter>
                </Card>
              </motion.div>
            ) : (
              <Card className="h-[300px] flex items-center justify-center border-dashed">
                <div className="text-center p-6">
                  <p className="text-muted-foreground font-medium">{t.toolai.noPostsTitle}</p>
                  <p className="text-sm text-muted-foreground/60 mt-2">{t.toolai.noPostsSubtitle}</p>
                </div>
              </Card>
            )}
          </div>

        </div>
      </div>
    </section>
  );
}
