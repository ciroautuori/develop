/**
 * ToolAI Backoffice Page - REFACTORED
 * Gestione post ToolAI con Design System StudioCentOS (Shadcn + Tailwind)
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  RefreshCw,
  Trash2,
  Send,
  CheckCircle2,
  Clock,
  FileText,
  Loader2,
  X,
  Cpu,
  Image as ImageIcon,
  Mic,
  Code,
  Video,
  Boxes,
  Star,
  ExternalLink,
  Bot,
  ChevronRight,
  Eye,
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { SPACING } from '../../../shared/config/constants';
import { toast } from 'sonner';
import type {
  ToolAIPost,
  ToolAIStats,
  GeneratePostRequest,
} from '../../landing/types/toolai.types';
import {
  fetchAdminPosts,
  fetchStats,
  generatePost,
  publishPost,
  deletePost,
} from '../../../services/api/toolai';

// Status configuration
const STATUS_CONFIG: Record<string, { label: string; color: string; bgColor: string }> = {
  draft: { label: 'Bozza', color: 'text-muted-foreground', bgColor: 'bg-muted' },
  scheduled: { label: 'Programmato', color: 'text-primary', bgColor: 'bg-primary/10' },
  published: { label: 'Pubblicato', color: 'text-green-500', bgColor: 'bg-green-500/10' },
  archived: { label: 'Archiviato', color: 'text-muted-foreground', bgColor: 'bg-muted' },
};

// Category configuration
const CATEGORIES = [
  { id: 'llm', label: 'LLM', icon: Cpu, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { id: 'image', label: 'Immagini', icon: ImageIcon, color: 'text-pink-500', bg: 'bg-pink-500/10' },
  { id: 'audio', label: 'Audio', icon: Mic, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  { id: 'code', label: 'Codice', icon: Code, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  { id: 'video', label: 'Video', icon: Video, color: 'text-red-500', bg: 'bg-red-500/10' },
  { id: 'multimodal', label: 'Multimodale', icon: Boxes, color: 'text-blue-500', bg: 'bg-blue-500/10' },
];

export function ToolAIBackoffice() {
  const navigate = useNavigate();

  // State
  const [posts, setPosts] = useState<ToolAIPost[]>([]);
  const [stats, setStats] = useState<ToolAIStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedPost, setSelectedPost] = useState<ToolAIPost | null>(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  // Generate form state
  const [generateForm, setGenerateForm] = useState<GeneratePostRequest>({
    num_tools: 3,
    categories: ['llm', 'image', 'code', 'audio'],
    auto_publish: false,
    translate: true,
    generate_image: true,
  });

  // Helper: format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  // Fetch posts and stats
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const status = statusFilter === 'all' ? undefined : statusFilter;
      const [postsData, statsData] = await Promise.all([
        fetchAdminPosts(page, 10, status),
        fetchStats(),
      ]);
      setPosts(postsData.posts || []);
      setTotalPages(Math.ceil(postsData.total / postsData.per_page) || 1);
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Errore nel caricamento dei dati');
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle generate
  const handleGenerate = async () => {
    if ((generateForm.categories?.length || 0) === 0) {
      toast.error('Seleziona almeno una categoria');
      return;
    }
    setGenerating(true);
    try {
      await generatePost(generateForm);
      toast.success('Post generato con successo!');
      setShowGenerateModal(false);
      fetchData();
    } catch (error) {
      console.error('Error generating post:', error);
      toast.error('Errore nella generazione del post');
    } finally {
      setGenerating(false);
    }
  };

  // Handle publish
  const handlePublish = async (postId: number) => {
    try {
      await publishPost(postId);
      toast.success('Post pubblicato!');
      fetchData();
    } catch (error) {
      console.error('Error publishing post:', error);
      toast.error('Errore nella pubblicazione');
    }
  };

  // Handle delete
  const handleDelete = async (postId: number) => {
    if (!confirm('Sei sicuro di voler eliminare questo post?')) return;
    try {
      await deletePost(postId);
      toast.success('Post eliminato!');
      fetchData();
    } catch (error) {
      console.error('Error deleting post:', error);
      toast.error("Errore nell'eliminazione");
    }
  };

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Header with Tab Navigation - Pattern AIMarketing */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        {/* Title Row */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
            <Bot className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
              AI Marketing Hub
            </h1>
            <p className="text-sm text-muted-foreground">
              Genera contenuti e chatta con l'assistente AI
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-card border border-border rounded-2xl p-2 shadow-sm">
          <div className="flex gap-1 overflow-x-auto">
            <Button
              variant="ghost"
              onClick={() => navigate('/admin/ai-marketing')}
              className="flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl h-auto text-muted-foreground hover:text-foreground hover:bg-muted/50"
            >
              <Sparkles className="w-5 h-5" />
              <span className="text-xs font-medium whitespace-nowrap">Content</span>
            </Button>
            <Button
              variant="ghost"
              onClick={() => navigate('/admin/ai-marketing')}
              className="flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl h-auto text-muted-foreground hover:text-foreground hover:bg-muted/50"
            >
              <Eye className="w-5 h-5" />
              <span className="text-xs font-medium whitespace-nowrap">Lead Finder</span>
            </Button>
            <Button
              variant="ghost"
              onClick={() => navigate('/admin/ai-marketing')}
              className="flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl h-auto text-muted-foreground hover:text-foreground hover:bg-muted/50"
            >
              <Bot className="w-5 h-5" />
              <span className="text-xs font-medium whitespace-nowrap">AI Chat</span>
            </Button>
            <Button
              variant="ghost"
              onClick={() => navigate('/admin/ai-marketing')}
              className="flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl h-auto text-muted-foreground hover:text-foreground hover:bg-muted/50"
            >
              <Clock className="w-5 h-5" />
              <span className="text-xs font-medium whitespace-nowrap">Calendario</span>
            </Button>
            <Button
              variant="ghost"
              className="flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl h-auto bg-gradient-to-r from-primary to-primary/80 text-white shadow-lg hover:from-primary/90 hover:to-primary/70"
            >
              <Bot className="w-5 h-5" />
              <span className="text-xs font-medium whitespace-nowrap">ToolAI</span>
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Content - Grid 2 columns */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Left Panel - Stats + Genera */}
        <div className="space-y-6">
          {/* Stats Card */}
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-foreground mb-4">Statistiche</h3>
            {stats ? (
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: 'Post Totali', value: stats.total_posts },
                  { label: 'Pubblicati', value: stats.published_posts },
                  { label: 'Bozze', value: stats.draft_posts },
                  { label: 'Tool Scoperti', value: stats.total_tools_discovered },
                ].map((stat, i) => (
                  <div key={i} className="p-3 rounded-lg bg-muted/50">
                    <p className="text-xs text-muted-foreground">{stat.label}</p>
                    <p className="text-2xl font-bold text-primary">{stat.value}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-24">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            )}
          </div>

          {/* Generate Card */}
          <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-foreground mb-4">Genera Nuovo Post</h3>

            {/* Num Tools */}
            <div className="mb-4">
              <label className="block text-sm text-muted-foreground mb-2">
                Numero di Tool: <span className="text-primary font-bold">{generateForm.num_tools}</span>
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={generateForm.num_tools}
                onChange={e => setGenerateForm({ ...generateForm, num_tools: parseInt(e.target.value) })}
                className="w-full accent-primary"
              />
            </div>

            {/* Categories */}
            <div className="mb-4">
              <label className="block text-sm text-muted-foreground mb-2">Categorie</label>
              <div className="grid grid-cols-3 gap-2">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => {
                      const cats = generateForm.categories || [];
                      const newCats = cats.includes(cat.id)
                        ? cats.filter(c => c !== cat.id)
                        : [...cats, cat.id];
                      setGenerateForm({ ...generateForm, categories: newCats });
                    }}
                    className={cn(
                      'p-2 rounded-lg border transition-all flex flex-col items-center gap-1',
                      generateForm.categories?.includes(cat.id)
                        ? 'border-primary bg-primary/10'
                        : 'border-border hover:border-primary/50 bg-background'
                    )}
                  >
                    <cat.icon className={cn("w-4 h-4", cat.color)} />
                    <span className="text-xs text-foreground">{cat.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Options */}
            <div className="space-y-2 mb-4">
              {[
                { key: 'auto_publish', label: 'Pubblica automaticamente' },
                { key: 'translate', label: 'Traduci in EN/ES' },
                { key: 'generate_image', label: 'Genera immagine' },
              ].map(opt => (
                <label key={opt.key} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={generateForm[opt.key as keyof GeneratePostRequest] as boolean}
                    onChange={e => setGenerateForm({ ...generateForm, [opt.key]: e.target.checked })}
                    className="w-4 h-4 rounded accent-primary border-input bg-background"
                  />
                  <span className="text-sm text-foreground">{opt.label}</span>
                </label>
              ))}
            </div>

            {/* Generate Button */}
            <Button
              onClick={handleGenerate}
              disabled={generating || (generateForm.categories?.length || 0) === 0}
              className="w-full h-12 text-lg gap-2 bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {generating ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Generando...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  Genera Post AI
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Right Panel - Posts List */}
        <div className="space-y-4">
          {/* Filter + Actions */}
          <div className="bg-card border border-border rounded-xl p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-foreground">Post Recenti</h3>
              <Button variant="outline" size="sm" onClick={fetchData} disabled={loading}>
                <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
              </Button>
            </div>

            {/* Status Filter */}
            <div className="flex flex-wrap gap-2">
              {['all', 'draft', 'published', 'scheduled'].map(status => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={cn(
                    "px-3 py-1.5 text-xs rounded-full border transition-all",
                    statusFilter === status
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'border-input text-muted-foreground hover:border-primary hover:text-primary bg-background'
                  )}
                >
                  {status === 'all' ? 'Tutti' : STATUS_CONFIG[status]?.label || status}
                </button>
              ))}
            </div>
          </div>

          {/* Posts List */}
          <div className="bg-card border border-border rounded-xl p-4 shadow-sm">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : posts.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mb-2 opacity-50" />
                <p className="text-muted-foreground">Nessun post trovato</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                {posts.map(post => (
                  <div
                    key={post.id}
                    className="p-4 rounded-lg border border-border hover:border-primary/50 hover:bg-muted/50 transition-all cursor-pointer bg-card"
                    onClick={() => setSelectedPost(post)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-foreground truncate">{post.title_it}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDate(post.post_date)} • {post.tools.length} tool
                        </p>
                      </div>
                      <span className={cn(
                        'px-2 py-1 rounded-full text-xs shrink-0',
                        STATUS_CONFIG[post.status]?.bgColor || 'bg-muted',
                        STATUS_CONFIG[post.status]?.color || 'text-muted-foreground'
                      )}>
                        {STATUS_CONFIG[post.status]?.label || post.status}
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 mt-3">
                      {post.status === 'draft' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => { e.stopPropagation(); handlePublish(post.id); }}
                          className="gap-1 text-primary hover:text-primary hover:bg-primary/10 h-8"
                        >
                          <Send className="h-3 w-3" />
                          Pubblica
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => { e.stopPropagation(); handleDelete(post.id); }}
                        className="gap-1 text-destructive hover:text-destructive hover:bg-destructive/10 h-8"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                      <ChevronRight className="h-4 w-4 text-muted-foreground ml-auto" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Post Detail Modal */}
      <AnimatePresence>
        {selectedPost && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
            onClick={() => setSelectedPost(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="w-full max-w-2xl rounded-2xl p-6 max-h-[80vh] overflow-y-auto bg-card border border-border shadow-xl"
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs',
                    STATUS_CONFIG[selectedPost.status]?.bgColor,
                    STATUS_CONFIG[selectedPost.status]?.color
                  )}>
                    {STATUS_CONFIG[selectedPost.status]?.label || selectedPost.status}
                  </span>
                  <h2 className="text-xl font-bold text-foreground mt-2">{selectedPost.title_it}</h2>
                  <p className="text-sm text-muted-foreground">{formatDate(selectedPost.post_date)}</p>
                </div>
                <button onClick={() => setSelectedPost(null)} className="text-muted-foreground hover:text-foreground">
                  <X className="h-6 w-6" />
                </button>
              </div>

              <p className="text-foreground mb-4 leading-relaxed">{selectedPost.summary_it}</p>

              {/* Tools */}
              <div className="space-y-2 mb-4">
                <h4 className="text-sm font-medium text-muted-foreground">Tool ({selectedPost.tools.length})</h4>
                {selectedPost.tools.map(tool => (
                  <div key={tool.id} className="p-3 rounded-lg bg-muted/50 border border-border">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-foreground">{tool.name}</span>
                      {tool.source_url && (
                        <a href={tool.source_url} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary">
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{tool.description_it}</p>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-border">
                {selectedPost.status === 'draft' && (
                  <Button
                    onClick={() => { handlePublish(selectedPost.id); setSelectedPost(null); }}
                    className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Pubblica
                  </Button>
                )}
                <Button
                  variant="outline"
                  onClick={() => { handleDelete(selectedPost.id); setSelectedPost(null); }}
                  className="text-destructive hover:bg-destructive/10 border-destructive/20"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Elimina
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default ToolAIBackoffice;
