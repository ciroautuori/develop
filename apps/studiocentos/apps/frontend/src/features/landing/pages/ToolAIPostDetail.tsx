/**
 * ToolAI Post Detail - Pagina singolo post SEO optimized
 * Con schema.org markup per Rich Snippets
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
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
  Share2,
  Twitter,
  Linkedin,
  Copy,
  Check,
  ChevronRight,
  ArrowRight,
} from 'lucide-react';
import { LanguageProvider, useLanguage } from '../i18n';
import { LandingHeader } from '../components/LandingHeader';
import { LandingFooter } from '../components/LandingFooter';
import { fetchPostBySlug, fetchPublicPosts } from '../../../services/api/toolai';
import type { ToolAIPost, AITool } from '../types/toolai.types';

// Category config
const CATEGORIES = [
  { id: 'llm', label: { it: 'LLM', en: 'LLM', es: 'LLM' }, icon: Cpu, color: '#1877F2' },
  { id: 'image', label: { it: 'Immagini', en: 'Images', es: 'Imágenes' }, icon: ImageIcon, color: '#E4405F' },
  { id: 'audio', label: { it: 'Audio', en: 'Audio', es: 'Audio' }, icon: Mic, color: '#1877F2' },
  { id: 'code', label: { it: 'Codice', en: 'Code', es: 'Código' }, icon: Code, color: '#0A66C2' },
  { id: 'video', label: { it: 'Video', en: 'Video', es: 'Video' }, icon: Video, color: '#1DA1F2' },
  { id: 'multimodal', label: { it: 'Multimodale', en: 'Multimodal', es: 'Multimodal' }, icon: Boxes, color: '#5E4B1C' },
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

  const shareUrl = `https://studiocentos.com/toolai/${slug}`;

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
      <div className="min-h-screen bg-[#0a0a0a] light:bg-white flex items-center justify-center">
        <div className="text-center">
          <Sparkles className="w-12 h-12 mx-auto text-gold animate-pulse mb-4" />
          <p className="text-gray-400">
            {language === 'it' ? 'Caricamento...' : language === 'es' ? 'Cargando...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] light:bg-white">
        <LandingHeader />
        <div className="pt-32 pb-16 px-4 text-center">
          <h1 className="text-2xl font-bold text-white light:text-gray-900 mb-4">
            {language === 'it' ? 'Post non trovato' : language === 'es' ? 'Publicación no encontrada' : 'Post not found'}
          </h1>
          <Link to="/toolai" className="text-gold hover:underline">
            {language === 'it' ? '← Torna alla lista' : language === 'es' ? '← Volver a la lista' : '← Back to list'}
          </Link>
        </div>
        <LandingFooter />
      </div>
    );
  }

  const title = getLocalizedField('title');
  const summary = getLocalizedField('summary');
  const content = getLocalizedField('content');
  const insights = getLocalizedField('insights');
  const takeaway = getLocalizedField('takeaway');

  return (
    <>
      <Helmet>
        <title>{title} | ToolAI - StudiocentOS</title>
        <meta name="description" content={summary} />
        <meta name="keywords" content={post.meta_keywords?.join(', ')} />
        <meta property="og:title" content={`${title} | ToolAI`} />
        <meta property="og:description" content={summary} />
        <meta property="og:type" content="article" />
        <meta property="og:url" content={shareUrl} />
        {post.image_url && <meta property="og:image" content={post.image_url} />}
        <meta property="article:published_time" content={post.post_date} />
        <meta property="article:section" content="AI Tools" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={summary} />
        <link rel="canonical" href={shareUrl} />
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": summary,
            "image": post.image_url,
            "datePublished": post.post_date,
            "dateModified": post.published_at || post.post_date,
            "author": {
              "@type": "Organization",
              "name": "StudiocentOS",
              "url": "https://studiocentos.com"
            },
            "publisher": {
              "@type": "Organization",
              "name": "StudiocentOS",
              "logo": {
                "@type": "ImageObject",
                "url": "https://studiocentos.com/logo.png"
              }
            },
            "mainEntityOfPage": {
              "@type": "WebPage",
              "@id": shareUrl
            },
            "about": (post.tools && Array.isArray(post.tools) ? post.tools : []).filter(tool => tool && tool.name).map(tool => ({
              "@type": "SoftwareApplication",
              "name": tool.name,
              "url": tool.source_url || undefined,
              "applicationCategory": tool.category || undefined,
              "aggregateRating": tool.stars ? {
                "@type": "AggregateRating",
                "ratingValue": tool.stars > 1000 ? 5 : tool.stars > 100 ? 4 : 3,
                "ratingCount": tool.stars
              } : undefined
            }))
          })}
        </script>
      </Helmet>

      <div className="min-h-screen bg-[#0a0a0a] light:bg-white text-white light:text-gray-900">
        <LandingHeader />

        {/* Breadcrumb */}
        <div className="pt-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            <nav className="flex items-center gap-2 text-sm text-gray-400 py-4">
              <Link to="/" className="hover:text-gold">Home</Link>
              <ChevronRight className="w-4 h-4" />
              <Link to="/toolai" className="hover:text-gold">ToolAI</Link>
              <ChevronRight className="w-4 h-4" />
              <span className="text-gold truncate max-w-[40vw] sm:max-w-[200px]">{title}</span>
            </nav>
          </div>
        </div>

        {/* Article Header */}
        <article className="px-4 sm:px-6 lg:px-8 pb-16">
          <div className="max-w-4xl mx-auto">
            <header className="mb-8 animate-fade-in">
              {/* Meta */}
              <div className="flex flex-wrap items-center gap-3 mb-6">
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-gold/20 text-gold">
                  <Calendar className="w-4 h-4" />
                  {formatDate(post.post_date)}
                </div>
                {post.ai_generated && (
                  <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-gold/20 text-gold text-sm">
                    <Sparkles className="w-4 h-4" />
                    AI Generated
                  </div>
                )}
              </div>

              {/* Title */}
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6">
                {title}
              </h1>

              {/* Summary */}
              <p className="text-xl text-gray-400 light:text-gray-600 leading-relaxed">
                {summary}
              </p>

              {/* Share */}
              <div className="flex items-center gap-3 mt-6 pt-6 border-t border-white/10 light:border-gray-200">
                <span className="text-sm text-gray-400">
                  {language === 'it' ? 'Condividi:' : language === 'es' ? 'Compartir:' : 'Share:'}
                </span>
                <button
                  onClick={() => handleShare('twitter')}
                  className="p-2 rounded-lg bg-white/5 light:bg-gray-100 hover:bg-white/10 light:hover:bg-gray-200 transition-colors"
                  title="Share on Twitter"
                >
                  <Twitter className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleShare('linkedin')}
                  className="p-2 rounded-lg bg-white/5 light:bg-gray-100 hover:bg-white/10 light:hover:bg-gray-200 transition-colors"
                  title="Share on LinkedIn"
                >
                  <Linkedin className="w-4 h-4" />
                </button>
                <button
                  onClick={handleCopyLink}
                  className="p-2 rounded-lg bg-white/5 light:bg-gray-100 hover:bg-white/10 light:hover:bg-gray-200 transition-colors"
                  title="Copy link"
                >
                  {copied ? <Check className="w-4 h-4 text-gold" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </header>

            {/* Featured Image */}
            {post.image_url && (
              <div className="rounded-2xl overflow-hidden mb-12 animate-fade-in">
                <img
                  src={post.image_url}
                  alt={title}
                  className="w-full h-auto object-cover"
                />
              </div>
            )}

            {/* Tools Section */}
            <section className="mb-12 animate-fade-in">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-gold" />
                {language === 'it' ? 'Tool Analizzati' : language === 'es' ? 'Herramientas Analizadas' : 'Analyzed Tools'}
                <span className="text-gray-400 font-normal">({post.tools.length})</span>
              </h2>

              <div className="space-y-4">
                {post.tools.map((tool, i) => {
                  const catConfig = CATEGORIES.find(c => c.id === tool.category);
                  const Icon = catConfig?.icon || Cpu;
                  const description = tool[`description_${language}` as keyof AITool] || tool.description_it;
                  const relevance = tool[`relevance_${language}` as keyof AITool] || tool.relevance_it;

                  return (
                    <div
                      key={tool.id}
                      className="p-6 rounded-xl bg-gradient-to-br from-white/10 to-white/5 light:from-white light:to-gray-50 border border-white/10 light:border-gray-200"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-4">
                          <div
                            className="p-3 rounded-xl flex-shrink-0"
                            style={{ backgroundColor: `${catConfig?.color || '#D4AF37'}20` }}
                          >
                            <Icon className="w-6 h-6" style={{ color: catConfig?.color || '#D4AF37' }} />
                          </div>
                          <div>
                            <h3 className="text-xl font-bold mb-1">{tool.name}</h3>
                            <p className="text-sm text-gray-400 mb-3">{tool.source}</p>
                            <p className="text-gray-300 light:text-gray-600 mb-4">
                              {String(description)}
                            </p>
                            {relevance && (
                              <div className="p-3 rounded-lg bg-gold/10 border border-gold/30">
                                <p className="text-sm text-gold">
                                  <strong>
                                    {language === 'it' ? 'Perché è rilevante:' : language === 'es' ? 'Por qué es relevante:' : 'Why it matters:'}
                                  </strong>{' '}
                                  {String(relevance)}
                                </p>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex flex-col items-end gap-2 flex-shrink-0">
                          {tool.stars && (
                            <div className="flex items-center gap-1 text-gold">
                              <Star className="w-4 h-4 fill-current" />
                              <span className="text-sm font-medium">{tool.stars.toLocaleString()}</span>
                            </div>
                          )}
                          {tool.downloads && (
                            <div className="flex items-center gap-1 text-gray-400">
                              <Download className="w-4 h-4" />
                              <span className="text-sm">{tool.downloads.toLocaleString()}</span>
                            </div>
                          )}
                          {tool.source_url && (
                            <a
                              href={tool.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 px-3 py-1 rounded-lg bg-white/5 light:bg-gray-100 hover:bg-white/10 light:hover:bg-gray-200 text-sm text-gold transition-colors"
                            >
                              <ExternalLink className="w-3 h-3" />
                              {language === 'it' ? 'Visita' : language === 'es' ? 'Visitar' : 'Visit'}
                            </a>
                          )}
                        </div>
                      </div>

                      {/* Tags */}
                      {tool.tags && tool.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-white/10 light:border-gray-100">
                          {tool.tags.map((tag, j) => (
                            <span
                              key={j}
                              className="px-2 py-1 rounded text-xs bg-white/5 light:bg-gray-100 text-gray-400"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Insights */}
            {insights && (
              <section
                className="mb-12"
              >
                <h2 className="text-2xl font-bold mb-4">
                  {language === 'it' ? '📊 Approfondimenti' : language === 'es' ? '📊 Análisis' : '📊 Insights'}
                </h2>
                <div className="prose prose-invert light:prose max-w-none">
                  <p className="text-gray-300 light:text-gray-600 whitespace-pre-line leading-relaxed">
                    {insights}
                  </p>
                </div>
              </section>
            )}

            {/* Takeaway */}
            {takeaway && (
              <section
                className="mb-12"
              >
                <div className="p-6 rounded-xl bg-gradient-to-r from-gold/20 to-gold/10 border border-gold/30">
                  <h2 className="text-xl font-bold mb-3 text-gold">
                    💡 {language === 'it' ? 'Conclusioni' : language === 'es' ? 'Conclusiones' : 'Key Takeaway'}
                  </h2>
                  <p className="text-gray-200 light:text-gray-700 leading-relaxed">
                    {takeaway}
                  </p>
                </div>
              </section>
            )}

            {/* Back Link */}
            <div className="flex justify-between items-center pt-8 border-t border-white/10 light:border-gray-200">
              <Link
                to="/toolai"
                className="flex items-center gap-2 text-gold hover:underline"
              >
                <ArrowLeft className="w-4 h-4" />
                {language === 'it' ? 'Tutti i post' : language === 'es' ? 'Todas las publicaciones' : 'All posts'}
              </Link>
            </div>
          </div>
        </article>

        {/* Related Posts */}
        {relatedPosts.length > 0 && (
          <section className="px-4 sm:px-6 lg:px-8 pb-16 bg-white/5 light:bg-gray-50">
            <div className="max-w-7xl mx-auto py-12">
              <h2 className="text-2xl font-bold mb-8 text-center">
                {language === 'it' ? 'Altri Post' : language === 'es' ? 'Otras Publicaciones' : 'More Posts'}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {relatedPosts.map((rPost) => {
                  const rTitle = rPost[`title_${language}` as keyof ToolAIPost] || rPost.title_it;
                  return (
                    <Link
                      key={rPost.id}
                      to={`/toolai/${rPost.slug}`}
                      className="p-6 rounded-xl bg-white/5 light:bg-white border border-white/10 light:border-gray-200 hover:border-gold/50 transition-all"
                    >
                      <div className="text-sm text-gold mb-2">
                        {formatDate(rPost.post_date)}
                      </div>
                      <h3 className="font-bold line-clamp-2 group-hover:text-gold">
                        {String(rTitle)}
                      </h3>
                    </Link>
                  );
                })}
              </div>
            </div>
          </section>
        )}

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
