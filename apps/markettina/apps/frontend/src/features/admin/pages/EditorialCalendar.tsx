/**
 * Editorial Calendar - Calendario Editoriale Social Media
 * UI completa per gestione post programmati multi-piattaforma
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Plus,
  Send,
  Clock,
  Edit2,
  Trash2,
  Eye,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Facebook,
  Instagram,
  Linkedin,
  Twitter,
  Image,
  Video,
  FileText,
  Loader2,
  Filter,
  LayoutGrid,
  List,
  Sparkles,
  X,
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';

// Types
interface ScheduledPost {
  id: number;
  content: string;
  title?: string;
  hashtags: string[];
  mentions: string[];
  media_urls: string[];
  media_type: string;
  platforms: string[];
  scheduled_at: string;
  published_at?: string;
  status: 'draft' | 'scheduled' | 'publishing' | 'published' | 'failed' | 'cancelled';
  platform_results: Record<string, any>;
  error_message?: string;
  retry_count: number;
  ai_generated: boolean;
  metrics: Record<string, any>;
  created_at: string;
}

interface CalendarDay {
  date: Date;
  posts: ScheduledPost[];
  isCurrentMonth: boolean;
  isToday: boolean;
}

const PLATFORMS = [
  { id: 'facebook', label: 'Facebook', icon: Facebook, color: '#1877F2' },
  { id: 'instagram', label: 'Instagram', icon: Instagram, color: '#E4405F' },
  { id: 'linkedin', label: 'LinkedIn', icon: Linkedin, color: '#0A66C2' },
  { id: 'twitter', label: 'Twitter/X', icon: Twitter, color: '#1DA1F2' },
];

const STATUS_CONFIG = {
  draft: { label: 'Bozza', color: 'bg-gray-500', icon: FileText },
  scheduled: { label: 'Programmato', color: 'bg-gold', icon: Clock },
  publishing: { label: 'Pubblicando...', color: 'bg-gold', icon: Loader2 },
  published: { label: 'Pubblicato', color: 'bg-gold', icon: CheckCircle2 },
  failed: { label: 'Fallito', color: 'bg-gray-500', icon: XCircle },
  cancelled: { label: 'Annullato', color: 'bg-gray-400', icon: AlertCircle },
};

export function EditorialCalendar() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // State
  const [view, setView] = useState<'month' | 'week' | 'list'>('month');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPost, setSelectedPost] = useState<ScheduledPost | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filterPlatform, setFilterPlatform] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  // Create form state
  const [newPost, setNewPost] = useState({
    content: '',
    title: '',
    platforms: ['facebook', 'instagram'],
    scheduled_at: '',
    media_urls: [] as string[],
    hashtags: [] as string[],
    ai_generated: false,
  });

  // Theme classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white placeholder-gray-400'
    : 'bg-gray-50 border-gray-200 text-gray-900 placeholder-gray-400';
  const selectBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-white border-gray-300 text-gray-900';

  // Fetch posts
  const fetchPosts = useCallback(async () => {
    setLoading(true);
    try {
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth() + 1;

      const response = await fetch(
        `/api/v1/marketing/calendar/view/month?year=${year}&month=${month}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPosts(data.posts || []);
      } else {
        // API error - clear posts
        setPosts([]);
      }
    } catch (error) {
      console.error('Error fetching posts:', error);
      setPosts([]);
    }
    setLoading(false);
  }, [currentDate]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  // Generate calendar days
  const generateCalendarDays = (): CalendarDay[] => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const today = new Date();

    const days: CalendarDay[] = [];

    // Days from previous month
    const startDayOfWeek = firstDay.getDay() || 7; // 1=Monday
    for (let i = startDayOfWeek - 1; i > 0; i--) {
      const date = new Date(year, month, 1 - i);
      days.push({
        date,
        posts: posts.filter(p => isSameDay(new Date(p.scheduled_at), date)),
        isCurrentMonth: false,
        isToday: isSameDay(date, today),
      });
    }

    // Days of current month
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const date = new Date(year, month, i);
      days.push({
        date,
        posts: posts.filter(p => isSameDay(new Date(p.scheduled_at), date)),
        isCurrentMonth: true,
        isToday: isSameDay(date, today),
      });
    }

    // Days from next month
    const remainingDays = 42 - days.length;
    for (let i = 1; i <= remainingDays; i++) {
      const date = new Date(year, month + 1, i);
      days.push({
        date,
        posts: posts.filter(p => isSameDay(new Date(p.scheduled_at), date)),
        isCurrentMonth: false,
        isToday: isSameDay(date, today),
      });
    }

    return days;
  };

  const isSameDay = (d1: Date, d2: Date) =>
    d1.getDate() === d2.getDate() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getFullYear() === d2.getFullYear();

  // Navigation
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Actions
  const handleCreatePost = async () => {
    try {
      const response = await fetch('/api/v1/marketing/calendar/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
        body: JSON.stringify({
          ...newPost,
          scheduled_at: new Date(newPost.scheduled_at).toISOString(),
        }),
      });

      if (response.ok) {
        toast.success('Post programmato con successo!');
        setShowCreateModal(false);
        setNewPost({
          content: '',
          title: '',
          platforms: ['facebook', 'instagram'],
          scheduled_at: '',
          media_urls: [],
          hashtags: [],
          ai_generated: false,
        });
        fetchPosts();
      } else {
        toast.error('Errore nella creazione del post');
      }
    } catch (error) {
      toast.error('Errore di connessione');
    }
  };

  const handlePublishNow = async (postId: number) => {
    try {
      const response = await fetch(`/api/v1/marketing/calendar/posts/${postId}/publish-now`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
      });

      if (response.ok) {
        toast.success('Post pubblicato!');
        fetchPosts();
      } else {
        toast.error('Errore nella pubblicazione');
      }
    } catch (error) {
      toast.error('Errore di connessione');
    }
  };

  const handleDeletePost = async (postId: number) => {
    if (!confirm('Sei sicuro di voler eliminare questo post?')) return;

    try {
      const response = await fetch(`/api/v1/marketing/calendar/posts/${postId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`,
        },
      });

      if (response.ok) {
        toast.success('Post eliminato');
        fetchPosts();
      } else {
        toast.error('Errore nella cancellazione');
      }
    } catch (error) {
      toast.error('Errore di connessione');
    }
  };

  // Filter posts
  const filteredPosts = posts.filter(post => {
    if (filterPlatform && !post.platforms.includes(filterPlatform)) return false;
    if (filterStatus && post.status !== filterStatus) return false;
    return true;
  });

  const calendarDays = generateCalendarDays();
  const monthNames = [
    'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
    'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'
  ];
  const dayNames = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'];

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Header - Pattern AIMarketing */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
              <Calendar className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
                Calendario Editoriale
              </h1>
              <p className="text-sm text-muted-foreground">
                Programma e gestisci i tuoi post social media
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 self-start sm:self-center w-full sm:w-auto">
            {/* View Toggle */}
            <div className={cn('flex rounded-lg p-1 flex-1 sm:flex-none', isDark ? 'bg-white/5' : 'bg-gray-100')}>
              <button
                onClick={() => setView('month')}
                className={cn(
                  'flex-1 sm:flex-none px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2',
                  view === 'month'
                    ? isDark ? 'bg-gold-500 text-black' : 'bg-gold text-white'
                    : textSecondary
                )}
              >
                <LayoutGrid className="w-4 h-4" />
                <span className="sm:hidden">Mese</span>
              </button>
              <button
                onClick={() => setView('list')}
                className={cn(
                  'flex-1 sm:flex-none px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2',
                  view === 'list'
                    ? isDark ? 'bg-gold-500 text-black' : 'bg-gold text-white'
                    : textSecondary
                )}
              >
                <List className="w-4 h-4" />
                <span className="sm:hidden">Lista</span>
              </button>
            </div>

            <Button
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-gold-500 to-gold-600 text-black font-semibold shadow-md flex-1 sm:flex-none"
            >
              <Plus className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Nuovo Post</span>
              <span className="sm:hidden">Nuovo</span>
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Filters */}
      <div className={cn('p-4 rounded-xl flex flex-col sm:flex-row items-start sm:items-center gap-4', cardBg)}>
        <div className="flex items-center gap-2 mb-2 sm:mb-0">
          <Filter className={cn('w-4 h-4', textSecondary)} />
          <span className={cn('text-sm font-medium', textSecondary)}>Filtri:</span>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
          {/* Platform Filter */}
          <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0 w-full sm:w-auto no-scrollbar">
            {PLATFORMS.map(platform => (
              <button
                key={platform.id}
                onClick={() => setFilterPlatform(filterPlatform === platform.id ? null : platform.id)}
                className={cn(
                  'p-2 rounded-lg transition-all flex-shrink-0',
                  filterPlatform === platform.id
                    ? 'ring-2 ring-gold-500'
                    : isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100'
                )}
                style={{
                  backgroundColor: filterPlatform === platform.id ? `${platform.color}20` : undefined
                }}
              >
                <platform.icon
                  className="w-5 h-5"
                  style={{ color: platform.color }}
                />
              </button>
            ))}
          </div>

          {/* Status Filter */}
          <select
            value={filterStatus || ''}
            onChange={(e) => setFilterStatus(e.target.value || null)}
            className={cn('px-3 py-2 rounded-lg text-sm w-full sm:w-auto', selectBg)}
          >
            <option value="">Tutti gli stati</option>
            {Object.entries(STATUS_CONFIG).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>

          {(filterPlatform || filterStatus) && (
            <button
              onClick={() => {
                setFilterPlatform(null);
                setFilterStatus(null);
              }}
              className={cn('text-sm whitespace-nowrap self-end sm:self-center', textSecondary, 'hover:text-gray-400')}
            >
              Rimuovi filtri
            </button>
          )}
        </div>
      </div>

      {/* Calendar Navigation */}
      <div className={cn('p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4', cardBg)}>
        <div className="flex items-center justify-between w-full sm:w-auto gap-4">
          <button
            onClick={goToPreviousMonth}
            className={cn('p-2 rounded-lg', isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100')}
          >
            <ChevronLeft className={cn('w-5 h-5', textPrimary)} />
          </button>
          <h2 className={cn('text-xl font-bold min-w-[180px] text-center', textPrimary)}>
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </h2>
          <button
            onClick={goToNextMonth}
            className={cn('p-2 rounded-lg', isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100')}
          >
            <ChevronRight className={cn('w-5 h-5', textPrimary)} />
          </button>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <button
            onClick={goToToday}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium flex-1 sm:flex-none text-center',
              isDark ? 'bg-white/10 hover:bg-white/20' : 'bg-gray-100 hover:bg-gray-200',
              textPrimary
            )}
          >
            Oggi
          </button>
          <button
            onClick={fetchPosts}
            className={cn(
              'p-2 rounded-lg flex-shrink-0',
              isDark ? 'hover:bg-white/10' : 'hover:bg-gray-100'
            )}
          >
            <RefreshCw className={cn('w-5 h-5', loading ? 'animate-spin' : '', textSecondary)} />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      {view === 'month' && (
        <div className={cn('rounded-xl overflow-hidden overflow-x-auto', cardBg)}>
          <div className="min-w-[800px]">
            {/* Day Headers */}
            <div className="grid grid-cols-7 border-b border-white/10">
              {dayNames.map(day => (
                <div
                  key={day}
                  className={cn(
                    'py-3 text-center text-sm font-medium',
                    textSecondary
                  )}
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Days */}
            <div className="grid grid-cols-7">
              {calendarDays.map((day, index) => (
                <div
                  key={index}
                  className={cn(
                    'min-h-[120px] p-2 border-b border-r',
                    isDark ? 'border-white/5' : 'border-gray-100',
                    !day.isCurrentMonth && 'opacity-40',
                    day.isToday && (isDark ? 'bg-gold-500/10' : 'bg-gold/10')
                  )}
                >
                  <div className={cn(
                    'text-sm font-medium mb-2',
                    day.isToday ? 'text-gold-500' : textPrimary
                  )}>
                    {day.date.getDate()}
                  </div>

                  <div className="space-y-1">
                    {day.posts.slice(0, 3).map(post => (
                      <motion.div
                        key={post.id}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => setSelectedPost(post)}
                        className={cn(
                          'p-1.5 rounded-md cursor-pointer text-xs truncate',
                          STATUS_CONFIG[post.status].color,
                          'text-white'
                        )}
                      >
                        <div className="flex items-center gap-1">
                          {post.platforms.slice(0, 2).map(p => {
                            const platform = PLATFORMS.find(pl => pl.id === p);
                            return platform ? (
                              <platform.icon key={p} className="w-3 h-3" />
                            ) : null;
                          })}
                          <span className="truncate">
                            {new Date(post.scheduled_at).toLocaleTimeString('it-IT', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                      </motion.div>
                    ))}
                    {day.posts.length > 3 && (
                      <div className={cn('text-xs', textSecondary)}>
                        +{day.posts.length - 3} altri
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* List View */}
      {view === 'list' && (
        <div className={cn('rounded-xl divide-y', cardBg, isDark ? 'divide-white/10' : 'divide-gray-100')}>
          {filteredPosts.length === 0 ? (
            <div className="p-12 text-center">
              <Calendar className={cn('w-12 h-12 mx-auto mb-4', textSecondary)} />
              <p className={textSecondary}>Nessun post programmato</p>
              <Button
                onClick={() => setShowCreateModal(true)}
                className="mt-4"
              >
                Crea il primo post
              </Button>
            </div>
          ) : (
            filteredPosts.map(post => (
              <div
                key={post.id}
                className={cn(
                  'p-4 flex items-center gap-4',
                  isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50'
                )}
              >
                {/* Status Badge */}
                <div className={cn(
                  'w-3 h-3 rounded-full',
                  STATUS_CONFIG[post.status].color
                )} />

                {/* Date/Time */}
                <div className="w-40">
                  <div className={cn('font-medium', textPrimary)}>
                    {new Date(post.scheduled_at).toLocaleDateString('it-IT', {
                      day: 'numeric',
                      month: 'short'
                    })}
                  </div>
                  <div className={textSecondary}>
                    {new Date(post.scheduled_at).toLocaleTimeString('it-IT', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>

                {/* Platforms */}
                <div className="flex gap-1">
                  {post.platforms.map(p => {
                    const platform = PLATFORMS.find(pl => pl.id === p);
                    return platform ? (
                      <platform.icon
                        key={p}
                        className="w-5 h-5"
                        style={{ color: platform.color }}
                      />
                    ) : null;
                  })}
                </div>

                {/* Content Preview */}
                <div className="flex-1">
                  <p className={cn('line-clamp-1', textPrimary)}>
                    {post.content}
                  </p>
                  {post.ai_generated && (
                    <span className="inline-flex items-center gap-1 text-xs text-gold-500">
                      <Sparkles className="w-3 h-3" /> AI Generated
                    </span>
                  )}
                </div>

                {/* Media */}
                {post.media_urls.length > 0 && (
                  <div className={cn('flex items-center gap-1', textSecondary)}>
                    <Image className="w-4 h-4" />
                    <span className="text-sm">{post.media_urls.length}</span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-2">
                  {post.status === 'scheduled' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handlePublishNow(post.id)}
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedPost(post)}
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDeletePost(post.id)}
                    className="text-gray-400 hover:bg-gray-500/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Create Post Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className={cn('w-full max-w-2xl rounded-2xl p-6', cardBg)}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className={cn('text-xl font-bold', textPrimary)}>
                  Nuovo Post Programmato
                </h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className={textSecondary}
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Platforms */}
                <div>
                  <label className={cn('block text-sm font-medium mb-2', textPrimary)}>
                    Piattaforme
                  </label>
                  <div className="flex gap-3">
                    {PLATFORMS.map(platform => (
                      <button
                        key={platform.id}
                        onClick={() => {
                          const platforms = newPost.platforms.includes(platform.id)
                            ? newPost.platforms.filter(p => p !== platform.id)
                            : [...newPost.platforms, platform.id];
                          setNewPost({ ...newPost, platforms });
                        }}
                        className={cn(
                          'p-3 rounded-lg transition-all',
                          newPost.platforms.includes(platform.id)
                            ? 'ring-2 ring-gold-500'
                            : isDark ? 'bg-white/5' : 'bg-gray-100'
                        )}
                        style={{
                          backgroundColor: newPost.platforms.includes(platform.id)
                            ? `${platform.color}20`
                            : undefined
                        }}
                      >
                        <platform.icon
                          className="w-6 h-6"
                          style={{ color: platform.color }}
                        />
                      </button>
                    ))}
                  </div>
                </div>

                {/* Content */}
                <div>
                  <label className={cn('block text-sm font-medium mb-2', textPrimary)}>
                    Contenuto
                  </label>
                  <textarea
                    value={newPost.content}
                    onChange={e => setNewPost({ ...newPost, content: e.target.value })}
                    placeholder="Scrivi il tuo post..."
                    rows={4}
                    className={cn(
                      'w-full px-4 py-3 rounded-lg resize-none',
                      inputBg
                    )}
                  />
                  <div className={cn('text-xs mt-1 text-right', textSecondary)}>
                    {newPost.content.length} caratteri
                  </div>
                </div>

                {/* Schedule */}
                <div>
                  <label className={cn('block text-sm font-medium mb-2', textPrimary)}>
                    Data e Ora
                  </label>
                  <input
                    type="datetime-local"
                    value={newPost.scheduled_at}
                    onChange={e => setNewPost({ ...newPost, scheduled_at: e.target.value })}
                    className={cn('w-full px-4 py-3 rounded-lg', inputBg)}
                  />
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setShowCreateModal(false)}
                  >
                    Annulla
                  </Button>
                  <Button
                    onClick={handleCreatePost}
                    disabled={!newPost.content || !newPost.scheduled_at || newPost.platforms.length === 0}
                    className="bg-gradient-to-r from-gold-500 to-gold-600 text-black"
                  >
                    <Clock className="w-4 h-4 mr-2" />
                    Programma Post
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Post Detail Modal */}
      <AnimatePresence>
        {selectedPost && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
            onClick={() => setSelectedPost(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className={cn('w-full max-w-lg rounded-2xl p-6', cardBg)}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs text-white',
                    STATUS_CONFIG[selectedPost.status].color
                  )}>
                    {STATUS_CONFIG[selectedPost.status].label}
                  </span>
                  {selectedPost.ai_generated && (
                    <span className="px-2 py-1 rounded-full text-xs bg-gold-500/20 text-gold-500">
                      AI Generated
                    </span>
                  )}
                </div>
                <button onClick={() => setSelectedPost(null)}>
                  <X className={cn('w-5 h-5', textSecondary)} />
                </button>
              </div>

              <div className="space-y-4">
                {/* Platforms */}
                <div className="flex gap-2">
                  {selectedPost.platforms.map(p => {
                    const platform = PLATFORMS.find(pl => pl.id === p);
                    return platform ? (
                      <div
                        key={p}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-full"
                        style={{ backgroundColor: `${platform.color}20` }}
                      >
                        <platform.icon className="w-4 h-4" style={{ color: platform.color }} />
                        <span style={{ color: platform.color }}>{platform.label}</span>
                      </div>
                    ) : null;
                  })}
                </div>

                {/* Schedule */}
                <div className={cn('flex items-center gap-2', textSecondary)}>
                  <Clock className="w-4 h-4" />
                  {new Date(selectedPost.scheduled_at).toLocaleString('it-IT')}
                </div>

                {/* Content */}
                <div className={cn('p-4 rounded-lg', isDark ? 'bg-white/5' : 'bg-gray-50')}>
                  <p className={textPrimary}>{selectedPost.content}</p>
                </div>

                {/* Error */}
                {selectedPost.error_message && (
                  <div className="p-4 rounded-lg bg-gray-500/10 text-gray-400">
                    <p className="text-sm">{selectedPost.error_message}</p>
                  </div>
                )}

                {/* Platform Results */}
                {Object.keys(selectedPost.platform_results).length > 0 && (
                  <div className="space-y-2">
                    <h4 className={cn('text-sm font-medium', textPrimary)}>Risultati</h4>
                    {Object.entries(selectedPost.platform_results).map(([platform, result]: [string, any]) => (
                      <div
                        key={platform}
                        className={cn(
                          'flex items-center justify-between p-2 rounded-lg',
                          isDark ? 'bg-white/5' : 'bg-gray-50'
                        )}
                      >
                        <span className={textPrimary}>{platform}</span>
                        <span className={result.status === 'success' ? 'text-gold' : 'text-gray-400'}>
                          {result.status === 'success' ? 'Pubblicato' : 'Errore'}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  {selectedPost.status === 'scheduled' && (
                    <>
                      <Button
                        onClick={() => {
                          handlePublishNow(selectedPost.id);
                          setSelectedPost(null);
                        }}
                        className="flex-1 bg-gold hover:bg-gold text-white"
                      >
                        <Send className="w-4 h-4 mr-2" />
                        Pubblica Ora
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => {
                          handleDeletePost(selectedPost.id);
                          setSelectedPost(null);
                        }}
                        className="text-gray-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </>
                  )}
                  {selectedPost.status === 'failed' && (
                    <Button
                      onClick={() => {
                        // Retry logic
                        handlePublishNow(selectedPost.id);
                        setSelectedPost(null);
                      }}
                      className="flex-1 bg-gold hover:bg-gold text-white"
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Riprova
                    </Button>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
