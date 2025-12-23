/**
 * ToolAI Hub - "Ferrari Edition" v2 (Restored & Refined) 🏎️
 * Modern Premium Experience: Glassmorphism, Particles, Bento Grid.
 * Color Strategy: Gold/Black branding (No Purple in UI/Text), but Colored Categories kept.
 * Typography: Standardized (No massive fonts).
 */

import { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  ArrowRight,
  Cpu,
  Image as ImageIcon,
  Mic,
  Code,
  Video,
  Boxes,
  Github,
  Globe,
  TrendingUp,
  Flame,
  Search,
  Loader2
} from 'lucide-react';
import { useLanguage, LanguageProvider } from '../i18n';
import { LandingHeader } from '../components/LandingHeader';
import { LandingFooter } from '../components/LandingFooter';
import { fetchPublicPosts } from '../../../services/api/toolai';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import type { ToolAIPost, AITool } from '../types/toolai.types';

// --- CONFIGURATION & HELPERS ---

const CATEGORIES = [
  { id: 'all', label: { it: 'Tutti', en: 'All', es: 'Todos' }, icon: Sparkles, color: 'text-primary', bg: 'bg-primary/10' },
  { id: 'llm', label: { it: 'LLM', en: 'LLM', es: 'LLM' }, icon: Cpu, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { id: 'image', label: { it: 'Vision', en: 'Vision', es: 'Visión' }, icon: ImageIcon, color: 'text-pink-500', bg: 'bg-pink-500/10' },
  { id: 'code', label: { it: 'Dev', en: 'Dev', es: 'Dev' }, icon: Code, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  { id: 'audio', label: { it: 'Audio', en: 'Audio', es: 'Audio' }, icon: Mic, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  { id: 'video', label: { it: 'Video', en: 'Video', es: 'Video' }, icon: Video, color: 'text-red-500', bg: 'bg-red-500/10' },
];

// --- COMPONENTS ---

// 1. Trending Ticker Component
function TrendingTicker({ tools }: { tools: AITool[] }) {
  if (!tools.length) return null;

  return (
    <div className="w-full bg-background/50 border-y border-border backdrop-blur-sm overflow-hidden py-2">
      <motion.div
        className="flex gap-8 whitespace-nowrap"
        animate={{ x: [0, -1000] }}
        transition={{ repeat: Infinity, duration: 40, ease: "linear" }}
      >
        {[...tools, ...tools, ...tools].map((tool, i) => ( // Triple copy for seamless loop
          <div key={`${tool.id}-${i}`} className="flex items-center gap-2 text-sm text-muted-foreground group cursor-default">
            <Flame className="w-3.5 h-3.5 text-primary" /> {/* Changed from orange to primary/gold to align with brand */}
            <span className="font-medium text-foreground group-hover:text-primary transition-colors">
              {tool.name}
            </span>
            <span className="text-xs opacity-50 flex items-center gap-1">
              {tool.trending_score ? `Score: ${tool.trending_score}` : ''}
              {tool.stars ? `• ⭐ ${tool.stars}` : ''}
            </span>
          </div>
        ))}
      </motion.div>
    </div>
  );
}

// 2. Bento Card Component
function BentoCard({ post, index, language }: { post: ToolAIPost; index: number; language: string }) {
  const isFeatured = index === 0; // First item is BIG
  const title = post[`title_${language}` as keyof ToolAIPost] || post.title_it;
  const summary = post[`summary_${language}` as keyof ToolAIPost] || post.summary_it;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={cn(
        "group relative rounded-3xl bg-card border border-border p-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-primary/10 hover:-translate-y-1",
        isFeatured ? "col-span-1 md:col-span-2 lg:col-span-2 row-span-2" : "col-span-1"
      )}
    >
      {/* Background Gradient Animation - GOLD focused */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <Link to={`/toolai/${post.slug}`} className="relative h-full flex flex-col z-10">
        {/* Header Badges */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider border border-primary/20">
              {new Date(post.post_date).toLocaleDateString()}
            </span>
            {isFeatured && (
              <span className="px-2 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center gap-1 animate-pulse">
                <Flame className="w-3 h-3" /> HOT
              </span>
            )}
          </div>

          {/* Tool Pile - Colored Icons Preserved */}
          <div className="flex -space-x-2">
            {post.tools.slice(0, 3).map((tool, i) => {
              const cat = CATEGORIES.find(c => c.id === tool.category) || CATEGORIES[0];
              const Icon = cat.icon;
              return (
                <div key={i} className={cn("w-8 h-8 rounded-full border-2 border-card flex items-center justify-center", cat.bg)}>
                  <Icon className={cn("w-4 h-4", cat.color)} />
                </div>
              )
            })}
            {post.tools.length > 3 && (
              <div className="w-8 h-8 rounded-full border-2 border-card bg-muted flex items-center justify-center text-xs font-bold text-muted-foreground">
                +{post.tools.length - 3}
              </div>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-grow">
          {/* FONT FIX: Standardized Sizes */}
          <h3 className={cn("font-bold text-foreground mb-3 leading-tight group-hover:text-primary transition-colors", isFeatured ? "text-2xl" : "text-xl")}>
            {String(title)}
          </h3>
          <p className={cn("text-muted-foreground leading-relaxed line-clamp-3", isFeatured ? "text-lg" : "text-sm")}>
            {String(summary)}
          </p>
        </div>

        {/* Tools Mini-List (Only for Featured or Large Cards) */}
        {isFeatured && (
          <div className="mt-6 space-y-2">
            {post.tools.slice(0, 3).map((tool, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-muted/30 border border-border/50 group-hover:border-primary/20 transition-colors">
                <div className="flex items-center gap-3">
                  {tool.source === 'github' ? <Github className="w-4 h-4" /> : <Boxes className="w-4 h-4" />}
                  <span className="font-medium">{tool.name}</span>
                </div>
                {tool.trending_score && (
                  <div className="flex items-center gap-1 text-xs font-mono text-muted-foreground">
                    <TrendingUp className="w-3 h-3 text-green-500" />
                    {tool.trending_score}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Footer Action */}
        <div className="mt-6 pt-4 border-t border-border flex items-center justify-between text-sm">
          <span className="font-medium text-primary flex items-center gap-2 group-hover:gap-3 transition-all">
            {language === 'it' ? 'Esplora' : 'Explore'} <ArrowRight className="w-4 h-4" />
          </span>
          <span className="text-muted-foreground/60 text-xs">ID: #{post.id}</span>
        </div>
      </Link>
    </motion.div>
  );
}


// --- MAIN PAGE COMPONENT ---

function ToolAIHubContent() {
  const { language, t } = useLanguage();
  const navigate = useNavigate();

  // State
  const [posts, setPosts] = useState<ToolAIPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  // Fetch Data
  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const result = await fetchPublicPosts(page, 20, language); // Fetch MORE posts for bento
        setPosts(result.posts || []);
      } catch (e) { console.error(e); }
      setLoading(false);
    }
    load();
  }, [page, language]);

  // Derived State (Filtering)
  const filteredPosts = useMemo(() => {
    return posts.filter(p => {
      // 1. Category Filter
      if (categoryFilter !== 'all') {
        if (!p.tools.some(t => t.category === categoryFilter)) return false;
      }
      // 2. Search Filter
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const textMatch = String(p[`title_${language}` as keyof ToolAIPost] || '').toLowerCase().includes(q)
          || String(p[`summary_${language}` as keyof ToolAIPost] || '').toLowerCase().includes(q);
        const toolMatch = p.tools.some(t => t.name.toLowerCase().includes(q));
        return textMatch || toolMatch;
      }
      return true;
    });
  }, [posts, categoryFilter, searchQuery, language]);

  // Extract all tools for Ticker
  const allTools = useMemo(() => posts.flatMap(p => p.tools).slice(0, 15), [posts]);


  return (
    <>
      <Helmet>
        <title>ToolAI Elite Hub | StudioCentOS</title>
      </Helmet>

      <div className="min-h-screen bg-background text-foreground antialiased selection:bg-primary/30">
        <LandingHeader />

        {/* HERO SECTION - Premium & Modern (Restored) */}
        <section className="relative pt-32 pb-16 overflow-hidden">
          {/* Animated Background Elements - RESTORED PURPLE BLOBS */}
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[120px] " />
          </div>

          <div className="max-w-7xl mx-auto px-4 sm:px-6 relative z-10 text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary border border-primary/20 mb-8 font-medium backdrop-blur-md"
            >
              <Sparkles className="w-4 h-4" />
              <span className="tracking-wide text-xs uppercase">
                {language === 'it' ? 'Il Motore di Ricerca per l\'AI' : 'The Search Engine for AI'}
              </span>
            </motion.div>

            {/* FONT FIX: text-5xl (Restored H1 Layout but Standard Size) */}
            <motion.h1
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8 }}
              className="text-4xl md:text-5xl font-black tracking-tighter mb-8"
            >
              {/* REMOVED PURPLE GRADIENT -> NOW PURE GOLD OR STANDARD */}
              TOOL<span className="text-primary">AI</span> HUB
            </motion.h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto mb-12 leading-relaxed"
            >
              {language === 'it'
                ? 'Ogni giorno scandagliamo GitHub, HuggingFace e ArXiv. Tu ricevi solo il meglio.'
                : 'Every day we scan GitHub, HuggingFace and ArXiv. You get only the best.'}
            </motion.p>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="max-w-2xl mx-auto relative group z-20"
            >
              {/* GRADIENT RESTORED: Primary to Purple-600 for Modernity */}
              <div className="absolute -inset-1 bg-gradient-to-r from-primary to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-60 transition duration-500" />
              <div className="relative flex items-center bg-card/80 backdrop-blur-xl border border-border rounded-2xl p-2 shadow-2xl">
                <Search className="w-6 h-6 text-muted-foreground ml-4" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={language === 'it' ? 'Cerca "LLM", "Video Generation", "GPT-4o"...' : 'Search "LLM", "Video Generation"...'}
                  className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-lg placeholder-muted-foreground/70"
                />
                {searchQuery && (
                  <Button variant="ghost" size="icon" onClick={() => setSearchQuery('')} className="mr-2">X</Button>
                )}
              </div>
            </motion.div>

            {/* Categories - COLORED PILLS RESTORED (Modernity) */}
            <div className="mt-12 flex flex-wrap justify-center gap-3">
              {CATEGORIES.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => setCategoryFilter(cat.id)}
                  className={cn(
                    "px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 flex items-center gap-2 border",
                    categoryFilter === cat.id
                      ? "bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/20 scale-105"
                      // HERE IS THE MAGIC: Restored custom colors for inactive/hover states 
                      : `bg-card border-border text-muted-foreground hover:border-current hover:bg-muted ${cat.color.replace('text-', 'hover:text-')}`
                  )}
                >
                  <cat.icon className={cn("w-4 h-4", categoryFilter === cat.id ? "text-primary-foreground" : cat.color)} />
                  {cat.label[language as 'it' | 'en' | 'es']}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* TRENDING TICKER */}
        <div className="mb-16">
          <TrendingTicker tools={allTools} />
        </div>

        {/* CONTENT GRID - BENTO STYLE */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-32">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
              <p className="text-muted-foreground animate-pulse">Scanning the AI Multiverse...</p>
            </div>
          ) : filteredPosts.length === 0 ? (
            <div className="text-center py-20">
              <div className="inline-block p-6 rounded-full bg-muted mb-4">
                <Search className="w-8 h-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-bold mb-2">No Signal Detected</h3>
              <p className="text-muted-foreground">Try adjusting your sensors (or search query).</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-[minmax(300px,auto)]">
              {filteredPosts.map((post, i) => (
                <BentoCard key={post.id} post={post} index={i} language={language} />
              ))}
            </div>
          )}
        </section>

        <LandingFooter />
      </div>
    </>
  );
}

export function ToolAIHub() {
  return (
    <LanguageProvider>
      <ToolAIHubContent />
    </LanguageProvider>
  );
}

export default ToolAIHub;
