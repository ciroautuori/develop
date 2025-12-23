/**
 * CalendarManager Component
 * Editorial calendar with scheduled posts management
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  CalendarDays,
  Plus,
  LayoutGrid,
  List,
  Loader2,
  Eye,
  Edit2,
  Trash2,
  Send,
  X,
  Facebook,
  Instagram,
  Linkedin,
  Twitter,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Sparkles,
} from 'lucide-react';
import { Button } from '../../../../../shared/components/ui/button';
import { cn } from '../../../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { useScheduledPosts } from '../../../hooks/marketing/useScheduledPosts';
import { CalendarSkeleton } from '../../../../../shared/components/skeletons';
import { BatchContentModal } from './BatchContentModal';
import type { BatchContentItem } from '../../../types/batch-content.types';

import { SOCIAL_PLATFORMS } from '../constants/platforms';

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  draft: { label: 'Bozza', color: 'bg-gray-500', icon: Edit2 },
  scheduled: { label: 'Programmato', color: 'bg-gold', icon: Clock },
  publishing: { label: 'Pubblicando...', color: 'bg-gold', icon: Loader2 },
  published: { label: 'Pubblicato', color: 'bg-gold', icon: CheckCircle2 },
  failed: { label: 'Fallito', color: 'bg-gray-500', icon: XCircle },
  cancelled: { label: 'Annullato', color: 'bg-gray-500', icon: X },
};

export default function CalendarManager() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const { posts, loading, fetchPosts, createPost, updatePost, deletePost, publishNow, cancelPost } =
    useScheduledPosts(true); // Auto-fetch on mount

  const [view, setView] = useState<'list' | 'month'>('list');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [newPostForm, setNewPostForm] = useState({
    content: '',
    platforms: ['facebook', 'instagram'],
    scheduled_at: '',
  });

  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';

  const handleCreatePost = async () => {
    if (!newPostForm.content.trim()) {
      toast.error('Inserisci il contenuto del post');
      return;
    }
    if (!newPostForm.scheduled_at) {
      toast.error('Seleziona data e ora di pubblicazione');
      return;
    }

    await createPost({
      content: newPostForm.content,
      platforms: newPostForm.platforms,
      scheduled_at: newPostForm.scheduled_at,
    });

    setShowCreateModal(false);
    setNewPostForm({ content: '', platforms: ['facebook', 'instagram'], scheduled_at: '' });
  };

  const handleDeletePost = async (id: number) => {
    if (confirm('Sei sicuro di voler eliminare questo post?')) {
      await deletePost(id);
    }
  };

  const handlePublishNow = async (id: number) => {
    if (confirm('Pubblicare questo post immediatamente?')) {
      await publishNow(id);
    }
  };

  const handleCancelPost = async (id: number) => {
    if (confirm('Annullare la programmazione di questo post?')) {
      await cancelPost(id);
    }
  };

  const togglePlatform = (platformId: string) => {
    setNewPostForm((prev) => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter((p) => p !== platformId)
        : [...prev.platforms, platformId],
    }));
  };

  const handleBatchSuccess = async (items: BatchContentItem[]) => {
    toast.success(`${items.length} contenuti generati! Aggiungi al calendario manualmente.`);
    // Note: In production, could auto-create posts from batch items
    await fetchPosts();
  };

  // Stats calculation
  const stats = {
    scheduled: posts.filter((p) => p.status === 'scheduled').length,
    published: posts.filter((p) => p.status === 'published').length,
    failed: posts.filter((p) => p.status === 'failed').length,
    total: posts.length,
  };

  return (
    <div className="space-y-6" role="region" aria-label="Gestione calendario editoriale">
      {/* Header with Stats */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className={`${cardBg} rounded-2xl p-6`}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className={`text-2xl font-bold ${textPrimary}`}>Calendario Editoriale</h2>
            <p className={textSecondary}>Gestisci i tuoi post programmati</p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setView(view === 'list' ? 'month' : 'list')}
              aria-label={view === 'list' ? 'Cambia a vista calendario mensile' : 'Cambia a vista lista'}
            >
              {view === 'list' ? <LayoutGrid className="w-4 h-4" aria-hidden="true" /> : <List className="w-4 h-4" aria-hidden="true" />}
            </Button>
            <Button
              onClick={() => setShowBatchModal(true)}
              aria-label="Genera campagna batch"
              className="bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold"
            >
              <Sparkles className="w-4 h-4 mr-2" aria-hidden="true" />
              Genera Campagna
            </Button>
            <Button
              onClick={() => setShowCreateModal(true)}
              aria-label="Crea nuovo post programmato"
              className="bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold"
            >
              <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
              Nuovo Post
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div
          className="grid grid-cols-2 sm:grid-cols-4 gap-4"
          role="group"
          aria-label="Statistiche calendario"
        >
          <div className={`p-4 rounded-xl ${isDark ? 'bg-white/5' : 'bg-gray-50'}`} aria-label={`${stats.scheduled} post programmati`}>
            <div className={`text-3xl font-bold ${textPrimary}`}>{stats.scheduled}</div>
            <div className={`text-sm ${textSecondary}`}>Programmati</div>
          </div>
          <div className={`p-4 rounded-xl ${isDark ? 'bg-white/5' : 'bg-gray-50'}`} aria-label={`${stats.published} post pubblicati`}>
            <div className="text-3xl font-bold text-gold">{stats.published}</div>
            <div className={`text-sm ${textSecondary}`}>Pubblicati</div>
          </div>
          <div className={`p-4 rounded-xl ${isDark ? 'bg-white/5' : 'bg-gray-50'}`} aria-label={`${stats.failed} post falliti`}>
            <div className="text-3xl font-bold text-gray-400">{stats.failed}</div>
            <div className={`text-sm ${textSecondary}`}>Falliti</div>
          </div>
          <div className={`p-4 rounded-xl ${isDark ? 'bg-white/5' : 'bg-gray-50'}`} aria-label={`${stats.total} post totali`}>
            <div className={`text-3xl font-bold ${textPrimary}`}>{stats.total}</div>
            <div className={`text-sm ${textSecondary}`}>Totale</div>
          </div>
        </div>
      </motion.div>

      {/* Posts List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`${cardBg} rounded-2xl divide-y ${isDark ? 'divide-white/10' : 'divide-gray-100'}`}
        role="list"
        aria-label="Lista post programmati"
      >
        {loading ? (
          <CalendarSkeleton />
        ) : posts.length === 0 ? (
          <div className="p-12 text-center">
            <CalendarDays className={`w-16 h-16 mx-auto mb-4 ${textSecondary} opacity-50`} aria-hidden="true" />
            <h4 className={`text-lg font-medium ${textPrimary} mb-2`}>Nessun post programmato</h4>
            <p className={textSecondary}>Crea il tuo primo post programmato</p>
            <Button
              onClick={() => setShowCreateModal(true)}
              aria-label="Crea il tuo primo post programmato"
              className="mt-4 bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold"
            >
              <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
              Crea Post
            </Button>
          </div>
        ) : (
          posts.map((post) => {
            const statusConfig = STATUS_CONFIG[post.status] || STATUS_CONFIG.draft;
            const StatusIcon = statusConfig.icon;

            return (
              <div
                key={post.id}
                role="listitem"
                aria-label={`Post per ${post.platforms.join(', ')}, programmato per ${new Date(post.scheduled_at).toLocaleString('it-IT')}, stato ${statusConfig.label}`}
                tabIndex={0}
                className={`p-4 flex items-start gap-4 transition-colors focus:outline-none focus:ring-2 focus:ring-gold ${
                  isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50'
                }`}
              >
                {/* Status Indicator */}
                <div className={cn('w-3 h-3 rounded-full mt-2', statusConfig.color)} />

                {/* Date & Time */}
                <div className="w-32 flex-shrink-0">
                  <div className={`font-semibold ${textPrimary}`}>
                    {new Date(post.scheduled_at).toLocaleDateString('it-IT', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                    })}
                  </div>
                  <div className={`text-sm ${textSecondary}`}>
                    {new Date(post.scheduled_at).toLocaleTimeString('it-IT', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </div>

                {/* Platforms */}
                <div className="flex gap-2 flex-shrink-0">
                  {post.platforms.map((platformId) => {
                    const platform = SOCIAL_PLATFORMS.find((p) => p.id === platformId);
                    if (!platform) return null;
                    const Icon = platform.icon;
                    return (
                      <div
                        key={platformId}
                        className="w-8 h-8 rounded-lg flex items-center justify-center bg-white/10"
                        style={{ backgroundColor: `${platform.color}20` }}
                        aria-label={platform.label}
                      >
                        <Icon className="w-4 h-4" style={{ color: platform.color }} aria-hidden="true" />
                      </div>
                    );
                  })}
                </div>

                {/* Content Preview */}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm line-clamp-2 ${textPrimary}`}>{post.content}</p>
                  {post.hashtags && post.hashtags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {post.hashtags.slice(0, 3).map((tag, idx) => (
                        <span
                          key={idx}
                          className={`text-xs px-2 py-0.5 rounded ${
                            isDark ? 'bg-gold/20 text-gold/80' : 'bg-gold/10 text-gold'
                          }`}
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Status Badge */}
                <div className="flex-shrink-0">
                  <span
                    className={cn(
                      'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium',
                      statusConfig.color,
                      'text-white'
                    )}
                  >
                    <StatusIcon className="w-3 h-3" aria-hidden="true" />
                    {statusConfig.label}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex gap-1 flex-shrink-0" role="group" aria-label="Azioni post">
                  {post.status === 'scheduled' && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePublishNow(post.id)}
                        aria-label="Pubblica subito"
                      >
                        <Send className="w-4 h-4" aria-hidden="true" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCancelPost(post.id)}
                        aria-label="Annulla programmazione"
                      >
                        <X className="w-4 h-4" aria-hidden="true" />
                      </Button>
                    </>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedPost(post)}
                    aria-label="Visualizza dettagli post"
                  >
                    <Eye className="w-4 h-4" aria-hidden="true" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDeletePost(post.id)}
                    className="text-gray-400 hover:bg-gray-500/10"
                    aria-label="Elimina post"
                  >
                    <Trash2 className="w-4 h-4" aria-hidden="true" />
                  </Button>
                </div>
              </div>
            );
          })
        )}
      </motion.div>

      {/* Create Post Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="presentation">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`${cardBg} rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto`}
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-modal-title"
            aria-describedby="create-modal-description"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 id="create-modal-title" className={`text-xl font-bold ${textPrimary}`}>Nuovo Post Programmato</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                aria-label="Chiudi finestra di creazione post"
                className={`p-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gold ${
                  isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100'
                }`}
              >
                <X className="w-5 h-5" aria-hidden="true" />
              </button>
            </div>
            <p id="create-modal-description" className="sr-only">Crea un nuovo post programmato per i tuoi canali social</p>

            <div className="space-y-4">
              {/* Content */}
              <div>
                <label htmlFor="post-content" className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                  Contenuto Post
                </label>
                <textarea
                  id="post-content"
                  value={newPostForm.content}
                  onChange={(e) => setNewPostForm({ ...newPostForm, content: e.target.value })}
                  placeholder="Scrivi il contenuto del tuo post..."
                  aria-describedby="content-hint"
                  aria-invalid={!newPostForm.content.trim()}
                  aria-required="true"
                  className={`w-full px-4 py-3 rounded-xl border ${inputBg} min-h-[150px] resize-none focus:ring-2 focus:ring-gold`}
                />
                <span id="content-hint" className="sr-only">Il contenuto del post è obbligatorio</span>
                {!newPostForm.content.trim() && (
                  <span role="alert" className="text-xs text-gray-400 mt-1 block">
                    Campo obbligatorio
                  </span>
                )}
              </div>

              {/* Platforms */}
              <fieldset>
                <legend className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                  Piattaforme
                </legend>
                <div
                  className="grid grid-cols-2 sm:grid-cols-4 gap-3"
                  role="group"
                  aria-label="Seleziona piattaforme social"
                >
                  {SOCIAL_PLATFORMS.filter(p => ['facebook', 'instagram', 'linkedin', 'twitter'].includes(p.id)).map((platform) => {
                    const Icon = platform.icon;
                    const isSelected = newPostForm.platforms.includes(platform.id);
                    return (
                      <button
                        key={platform.id}
                        onClick={() => togglePlatform(platform.id)}
                        role="checkbox"
                        aria-checked={isSelected}
                        aria-label={`Pubblica su ${platform.label}`}
                        className={`p-4 rounded-xl border-2 transition-all focus:outline-none focus:ring-2 focus:ring-gold ${
                          isSelected
                            ? 'border-gold bg-gold/10'
                            : isDark
                            ? 'border-white/10 hover:border-white/20 bg-white/5'
                            : 'border-gray-200 hover:border-gray-300 bg-gray-50'
                        }`}
                      >
                        <Icon
                          className="w-6 h-6 mx-auto mb-1"
                          style={{ color: isSelected ? platform.color : undefined }}
                          aria-hidden="true"
                        />
                        <div className={`text-xs font-medium ${textPrimary}`}>
                          {platform.label}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </fieldset>

              {/* Scheduled Date/Time */}
              <div>
                <label htmlFor="scheduled-datetime" className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                  Data e Ora di Pubblicazione
                </label>
                <input
                  id="scheduled-datetime"
                  type="datetime-local"
                  value={newPostForm.scheduled_at}
                  onChange={(e) =>
                    setNewPostForm({ ...newPostForm, scheduled_at: e.target.value })
                  }
                  aria-required="true"
                  aria-invalid={!newPostForm.scheduled_at}
                  className={`w-full px-4 py-3 rounded-xl border ${inputBg} focus:ring-2 focus:ring-gold`}
                />
                {!newPostForm.scheduled_at && (
                  <span role="alert" className="text-xs text-gray-400 mt-1 block">
                    Campo obbligatorio
                  </span>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1"
                  aria-label="Annulla creazione post"
                >
                  Annulla
                </Button>
                <Button
                  onClick={handleCreatePost}
                  disabled={!newPostForm.content || !newPostForm.scheduled_at}
                  className="flex-1 bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold"
                  aria-label="Crea post programmato"
                >
                  <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
                  Crea Post
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Post Detail Modal */}
      {selectedPost && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="presentation">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`${cardBg} rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto`}
            role="dialog"
            aria-modal="true"
            aria-labelledby="detail-modal-title"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 id="detail-modal-title" className={`text-xl font-bold ${textPrimary}`}>Dettagli Post</h3>
              <button
                onClick={() => setSelectedPost(null)}
                aria-label="Chiudi finestra dettagli post"
                className={`p-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gold ${
                  isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100'
                }`}
              >
                <X className="w-6 h-6" aria-hidden="true" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                  Contenuto
                </label>
                <div className={`p-4 rounded-xl ${inputBg} whitespace-pre-wrap`}>
                  {selectedPost.content}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                    Stato
                  </label>
                  <div className={`text-sm ${textPrimary}`}>
                    {STATUS_CONFIG[selectedPost.status]?.label}
                  </div>
                </div>
                <div>
                  <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                    Data Programmata
                  </label>
                  <div className={`text-sm ${textPrimary}`}>
                    {new Date(selectedPost.scheduled_at).toLocaleString('it-IT')}
                  </div>
                </div>
              </div>

              {selectedPost.published_at && (
                <div>
                  <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                    Data Pubblicazione
                  </label>
                  <div className={`text-sm ${textPrimary}`}>
                    {new Date(selectedPost.published_at).toLocaleString('it-IT')}
                  </div>
                </div>
              )}

              {selectedPost.error_message && (
                <div>
                  <label className={`block text-sm font-medium mb-2 text-gray-400`}>
                    Messaggio di Errore
                  </label>
                  <div className="p-4 rounded-xl bg-gray-500/10 text-gray-400 text-sm">
                    {selectedPost.error_message}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}

      {/* Batch Content Modal */}
      <BatchContentModal
        isOpen={showBatchModal}
        onClose={() => setShowBatchModal(false)}
        onSuccess={handleBatchSuccess}
      />
    </div>
  );
}
