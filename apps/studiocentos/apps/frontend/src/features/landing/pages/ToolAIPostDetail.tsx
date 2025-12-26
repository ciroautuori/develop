import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Calendar,
  Sparkles,
  ExternalLink,
  Star,
  Download,
  Cpu,
  Image as ImageIcon,
  Mic,
  Code,
  Video,
  Boxes,
  Twitter,
  Linkedin,
  Copy,
  Check,
  ChevronRight,
  TrendingUp,
  Github,
  Globe,
  Flame,
  Loader2,
  ArrowRight
} from 'lucide-react';
import { LanguageProvider, useLanguage } from '../i18n';
import { LandingHeader } from '../components/LandingHeader';
import { LandingFooter } from '../components/LandingFooter';
import { fetchPostBySlug, fetchPublicPosts } from '../../../services/api/toolai';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import type { ToolAIPost, AITool } from '../types/toolai.types';

// Category config (Synced with Hub)
const CATEGORIES = [
  { id: 'all', label: { it: 'Tutti', en: 'All', es: 'Todos' }, icon: Sparkles, color: 'text-primary', bg: 'bg-primary/10' },
  { id: 'llm', label: { it: 'LLM', en: 'LLM', es: 'LLM' }, icon: Cpu, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { id: 'image', label: { it: 'Vision', en: 'Vision', es: 'Visión' }, icon: ImageIcon, color: 'text-pink-500', bg: 'bg-pink-500/10' },
  { id: 'code', label: { it: 'Dev', en: 'Dev', es: 'Dev' }, icon: Code, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  { id: 'audio', label: { it: 'Audio', en: 'Audio', es: 'Audio' }, icon: Mic, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  { id: 'video', label: { it: 'Video', en: 'Video', es: 'Video' }, icon: Video, color: 'text-red-500', bg: 'bg-red-500/10' },
];

function ToolAIPostDetailContent() {
  const { slug } = useParams<{ slug: string }>();
  const { language, t } = useLanguage();
  const navigate = useNavigate();

  const [post, setPost] = useState<ToolAIPost | null>(null);
  const [relatedPosts, setRelatedPosts] = useState<ToolAIPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const loadPost = async () => {
      if (!slug) return;
      setLoading(true);
      setError(null);

      try {
        const data = await fetchPostBySlug(slug, language);
        setPost(data);

        // Load related posts
        const related = await fetchPublicPosts(1, 4, language);
        setRelatedPosts((related.posts || []).filter(p => p && p.id !== data.id).slice(0, 3));
      } catch (err) {
        console.error('Error loading post:', err);
        setError('Post not found');
        setPost(null);
        setRelatedPosts([]);
      }
      setLoading(false);
    };

    loadPost();
  }, [slug, language]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(language === 'it' ? 'it-IT' : language === 'es' ? 'es-ES' : 'en-US', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  const getLocalizedField = (field: string) => {
    if (!post) return '';
    const key = `${field}_${language}` as keyof ToolAIPost;
    return (post[key] || post[`${field}_it` as keyof ToolAIPost] || '') as string;
  };

  const shareUrl = `https://studiocentos.it/toolai/${slug}`;

  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleShare = (platform: 'twitter' | 'linkedin') => {
    const title = getLocalizedField('title');
    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(shareUrl)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`,
    };
    window.open(urls[platform], '_blank', 'width=600,height=400');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
        <p className="text-muted-foreground animate-pulse">
          {language === 'it' ? 'Scansione Multiverso AI...' : 'Scanning AI Multiverse...'}
        </p>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-background text-foreground antialiased selection:bg-primary/30">
        <LandingHeader />
        <div className="pt-32 pb-16 px-4 text-center max-w-7xl mx-auto">
          <div className="inline-block p-6 rounded-full bg-muted mb-4">
            <Boxes className="w-12 h-12 text-muted-foreground" />
          </div>
          <h1 className="text-3xl font-bold mb-4">
            {language === 'it' ? 'Post non trovato' : 'Post not found'}
          </h1>
          <p className="text-muted-foreground mb-8">
            {language === 'it' ? 'Il segnale è andato perduto nello spazio-tempo.' : 'The signal was lost in spacetime.'}
          </p>
          <Button asChild className="rounded-full">
            <Link to="/toolai">
              {language === 'it' ? 'Torna all\'Hub' : 'Back to Hub'}
            </Link>
          </Button>
        </div>
        <LandingFooter />
      </div>
    );
  }

  const title = getLocalizedField('title');
  const summary = getLocalizedField('summary');
  const insights = getLocalizedField('insights');
  const takeaway = getLocalizedField('takeaway');

  // CLEANUP TITLE: Se il titolo inizia con una data lunga, cerchiamo di renderlo più leggibile
  const cleanTitle = title.split(':').length > 1 ? title.split(':').slice(1).join(':').trim() : title;
  const dateHeader = title.split(':').length > 1 ? title.split(':')[0].trim() : formatDate(post.post_date);

  return (
    <>
      <Helmet>
        <title>{title} | ToolAI - StudioCentOS</title>
        <meta name="description" content={summary} />
        <link rel="canonical" href={shareUrl} />
      </Helmet>

      <div className="min-h-screen bg-background text-foreground antialiased selection:bg-primary/30 relative overflow-hidden">
        <LandingHeader />

        {/* Animated Background Blobs - Synced with Hub */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[120px] animate-pulse" />
          <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-[120px]" />
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 pt-32 pb-24">
          {/* Breadcrumb - Premium Minimalist */}
          <nav className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-muted-foreground mb-12 animate-fade-in">
            <Link to="/" className="hover:text-primary transition-colors">Home</Link>
            <ChevronRight className="w-3 h-3" />
            <Link to="/toolai" className="hover:text-primary transition-colors">ToolAI Hub</Link>
            <ChevronRight className="w-3 h-3" />
            <span className="text-primary truncate max-w-[150px]">{cleanTitle}</span>
          </nav>

          {/* Article Header */}
          <header className="mb-16">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-wrap items-center gap-3 mb-6"
            >
              <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/20 text-xs font-bold uppercase tracking-wider">
                <Calendar className="w-3 h-3" />
                {dateHeader}
              </div>
              {post.ai_generated && (
                <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-purple-500/10 text-purple-500 text-xs font-bold border border-purple-500/20">
                  <Sparkles className="w-3 h-3" />
                  AI CURATED
                </div>
              )}
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight mb-8 leading-[1.1]"
            >
              {cleanTitle}
            </motion.h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-xl sm:text-2xl text-muted-foreground leading-relaxed mb-10"
            >
              {summary}
            </motion.p>

            {/* Share & Actions */}
            <div className="flex flex-wrap items-center gap-4 pt-8 border-t border-border/50">
              <span className="text-sm font-bold uppercase tracking-widest text-muted-foreground/60 mr-2">
                {language === 'it' ? 'Condividi' : 'Share'}
              </span>
              <Button variant="outline" size="icon" onClick={() => handleShare('twitter')} className="rounded-xl hover:text-primary hover:border-primary">
                <Twitter className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={() => handleShare('linkedin')} className="rounded-xl hover:text-primary hover:border-primary">
                <Linkedin className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={handleCopyLink} className="rounded-xl hover:text-primary hover:border-primary">
                {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
              </Button>
            </div>
          </header>

          {/* Featured Image - Premium Container */}
          {post.image_url && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="relative rounded-[2rem] overflow-hidden mb-20 shadow-2xl shadow-primary/5 group"
            >
              <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent opacity-40 z-10" />
              <img
                src={post.image_url}
                alt={title}
                className="w-full h-auto object-cover transition-transform duration-700 group-hover:scale-105"
              />
            </motion.div>
          )}

          {/* Tools Grid - Premium Bento Capsules */}
          <section className="space-y-12 mb-24">
            <h2 className="text-3xl font-black tracking-tighter flex items-center gap-3 mb-10">
              <Sparkles className="w-8 h-8 text-primary" />
              {language === 'it' ? 'Tool Analizzati' : 'Analysed Tools'}
              <span className="text-muted-foreground font-light ml-2">({post.tools.length})</span>
            </h2>

            <div className="grid gap-8">
              {post.tools.map((tool, i) => {
                const cat = CATEGORIES.find(c => c.id === tool.category) || CATEGORIES[0];
                const Icon = cat.icon;
                const description = tool[`description_${language}` as keyof AITool] || tool.description_it;
                const relevance = tool[`relevance_${language}` as keyof AITool] || tool.relevance_it;

                return (
                  <motion.div
                    key={tool.id}
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="group relative rounded-3xl bg-card/40 backdrop-blur-xl border border-border p-8 hover:border-primary/30 transition-all duration-500 hover:shadow-2xl hover:shadow-primary/5"
                  >
                    <div className="flex flex-col md:flex-row gap-8 items-start">
                      {/* Left: Icon & Category */}
                      <div className="flex-shrink-0">
                        <div className={cn("w-16 h-16 rounded-2xl flex items-center justify-center border transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3", cat.bg, "border-current/10")}>
                          <Icon className={cn("w-8 h-8", cat.color)} />
                        </div>
                      </div>

                      {/* Center: Info */}
                      <div className="flex-grow space-y-4">
                        <div className="flex flex-wrap items-center justify-between gap-4">
                          <div>
                            <h3 className="text-2xl font-bold group-hover:text-primary transition-colors">{tool.name}</h3>
                            <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-widest text-muted-foreground mt-1">
                              {tool.source === 'github' ? <Github className="w-3 h-3" /> : <Globe className="w-3 h-3" />}
                              {tool.source}
                            </div>
                          </div>

                          <div className="flex items-center gap-4">
                            {tool.stars && (
                              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-muted/50 border border-border text-sm font-medium">
                                <Star className="w-4 h-4 text-primary fill-primary" />
                                {tool.stars.toLocaleString()}
                              </div>
                            )}
                            {tool.trending_score && (
                              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-green-500/10 border border-green-500/20 text-green-500 text-sm font-bold">
                                <TrendingUp className="w-4 h-4" />
                                {tool.trending_score}
                              </div>
                            )}
                          </div>
                        </div>

                        <p className="text-lg text-muted-foreground leading-relaxed">
                          {String(description)}
                        </p>

                        {relevance && (
                          <div className="relative p-6 rounded-2xl bg-primary/5 border border-primary/10 overflow-hidden">
                            <div className="absolute top-0 left-0 w-1 h-full bg-primary" />
                            <p className="text-sm font-medium">
                              <span className="text-primary font-black uppercase tracking-widest text-[10px] block mb-2">
                                {language === 'it' ? 'Core Innovation' : 'Why it matters'}
                              </span>
                              {String(relevance)}
                            </p>
                          </div>
                        )}

                        {/* Tags */}
                        {tool.tags && tool.tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 pt-4">
                            {tool.tags.map((tag, j) => (
                              <span key={j} className="px-2.5 py-1 rounded-lg bg-muted text-[10px] font-bold uppercase tracking-tighter text-muted-foreground hover:bg-primary/10 hover:text-primary transition-colors cursor-default">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Right: Action */}
                      {tool.source_url && (
                        <div className="w-full md:w-auto flex-shrink-0 pt-4 md:pt-0">
                          <Button asChild size="lg" className="w-full md:w-auto rounded-xl gap-3 shadow-lg shadow-primary/20">
                            <a href={tool.source_url} target="_blank" rel="noopener noreferrer">
                              {language === 'it' ? 'Esplora' : 'Visit Site'} <ExternalLink className="w-4 h-4" />
                            </a>
                          </Button>
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </section>

          {/* Insights Section - Premium Design */}
          {insights && (
            <section className="mb-20 animate-fade-in">
              <div className="group p-10 rounded-[2.5rem] bg-gradient-to-br from-card/80 to-background border border-border relative overflow-hidden">
                {/* Visual Accent */}
                <div className="absolute top-0 right-0 p-8 opacity-10">
                  <TrendingUp className="w-32 h-32 text-primary" />
                </div>

                <h2 className="text-3xl font-black tracking-tighter mb-6 flex items-center gap-3">
                  <Cpu className="w-8 h-8 text-primary" />
                  {language === 'it' ? 'Analisi Strategica' : 'Strategic Insights'}
                </h2>
                <div className="prose prose-invert max-w-none">
                  <p className="text-lg text-muted-foreground whitespace-pre-line leading-relaxed">
                    {insights}
                  </p>
                </div>
              </div>
            </section>
          )}

          {/* Takeaway - Premium "Ferrari" Box */}
          {takeaway && (
            <section className="mb-24">
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="relative p-1 bg-gradient-to-r from-primary via-purple-500 to-primary rounded-[3rem] overflow-hidden"
              >
                <div className="bg-background rounded-[2.9rem] p-10 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-10 opacity-5">
                    <Sparkles className="w-40 h-40 text-primary" />
                  </div>
                  <h2 className="text-2xl font-black tracking-widest uppercase mb-4 text-primary">
                    {language === 'it' ? 'Verdetto Finale' : 'Final Verdict'}
                  </h2>
                  <p className="text-xl font-medium text-foreground leading-relaxed italic">
                    "{takeaway}"
                  </p>
                </div>
              </motion.div>
            </section>
          )}

          {/* Back to Hub - High-End Call to Action */}
          <div className="text-center pt-16 border-t border-border">
            <Button asChild variant="ghost" size="lg" className="group rounded-full gap-3 hover:bg-primary/10 hover:text-primary transition-all">
              <Link to="/toolai">
                <ArrowLeft className="w-5 h-5 transition-transform group-hover:-translate-x-2" />
                {language === 'it' ? 'Torna alla Hub' : 'Back to the Hub'}
              </Link>
            </Button>
          </div>
        </div>

        {/* Related Posts Section - Refined Grid */}
        <AnimatePresence>
          {relatedPosts.length > 0 && (
            <section className="bg-muted/30 border-t border-border py-24">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h2 className="text-3xl font-black tracking-tighter mb-12 text-center">
                  {language === 'it' ? 'Espandi la tua Visione' : 'Expand your Vision'}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                  {relatedPosts.map((rPost, idx) => {
                    const rTitle = rPost[`title_${language}` as keyof ToolAIPost] || rPost.title_it;
                    // Prova a ripulire il titolo anche qui
                    const cleanRTitle = rTitle.split(':').length > 1 ? rTitle.split(':').slice(1).join(':').trim() : rTitle;

                    return (
                      <motion.div
                        key={rPost.id}
                        initial={{ opacity: 0, scale: 0.9 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.1 }}
                      >
                        <Link
                          to={`/toolai/${rPost.slug}`}
                          className="group block p-8 rounded-3xl bg-card border border-border hover:border-primary/50 transition-all duration-300 h-full flex flex-col hover:-translate-y-2 hover:shadow-xl hover:shadow-primary/5"
                        >
                          <div className="text-xs font-bold uppercase tracking-widest text-primary mb-4 flex items-center gap-2">
                            <Calendar className="w-3 h-3" />
                            {new Date(rPost.post_date).toLocaleDateString()}
                          </div>
                          <h3 className="text-xl font-bold group-hover:text-primary transition-colors line-clamp-2 flex-grow mb-6">
                            {cleanRTitle}
                          </h3>
                          <div className="flex items-center gap-2 text-primary font-bold text-sm">
                            LEGGI <ArrowRight className="w-4 h-4" />
                          </div>
                        </Link>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </section>
          )}
        </AnimatePresence>

        <LandingFooter />
      </div>
    </>
  );
}

// Wrapper component with LanguageProvider
export function ToolAIPostDetail() {
  return (
    <LanguageProvider>
      <ToolAIPostDetailContent />
    </LanguageProvider>
  );
}

export default ToolAIPostDetail;
