/**
 * Portfolio Hub - Centro Gestione Contenuti Landing
 * Unifica: Progetti + Servizi + ToolAI
 * Pattern: AIMarketing Hub (Tab Navigation + Inline Content)
 */

import { useState, Suspense, lazy } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Briefcase,
  Package,
  Bot,
  Plus,
  Edit,
  Loader2,
  Sparkles,
  RefreshCw,
  Trash2,
  Send,
  CheckCircle2,
  Clock,
  FileText,
  X,
  Cpu,
  Image as ImageIcon,
  Mic,
  Code,
  Video,
  Boxes,
  Star,
  ExternalLink,
  ChevronRight,
  Eye,
  Filter,
  Search,
  GraduationCap
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { SPACING } from '../../../shared/config/constants';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { useProjects, useServices } from '../hooks/usePortfolio';
import { useCourses, useDeleteCourse } from '../hooks/useCourses';
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

// ============================================================================
// TYPES
// ============================================================================

type PortfolioTabId = 'projects' | 'services' | 'courses' | 'toolai';

interface PortfolioTab {
  id: PortfolioTabId;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  color: string;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const PORTFOLIO_TABS: PortfolioTab[] = [
  { id: 'projects', label: 'Progetti', icon: Briefcase, description: 'Gestione progetti portfolio', color: 'from-amber-500 to-yellow-500' },
  { id: 'services', label: 'Servizi', icon: Package, description: 'Gestione servizi offerti', color: 'from-emerald-500 to-teal-500' },
  { id: 'courses', label: 'Corsi', icon: GraduationCap, description: 'Gestione corsi e moduli', color: 'from-blue-500 to-cyan-500' },
  { id: 'toolai', label: 'ToolAI', icon: Bot, description: 'Post AI del giorno', color: 'from-primary to-primary/60' },
];

// ToolAI Status configuration
const STATUS_CONFIG: Record<string, { label: string; color: string; bgColor: string }> = {
  draft: { label: 'Bozza', color: 'text-muted-foreground', bgColor: 'bg-muted' },
  scheduled: { label: 'Programmato', color: 'text-primary', bgColor: 'bg-primary/10' },
  published: { label: 'Pubblicato', color: 'text-green-500', bgColor: 'bg-green-500/10' },
  archived: { label: 'Archiviato', color: 'text-muted-foreground', bgColor: 'bg-muted' },
};

// ToolAI Category configuration
const CATEGORIES = [
  { id: 'llm', label: 'LLM', icon: Cpu, color: 'text-primary', bg: 'bg-primary/10' },
  { id: 'image', label: 'Immagini', icon: ImageIcon, color: 'text-pink-500', bg: 'bg-pink-500/10' },
  { id: 'audio', label: 'Audio', icon: Mic, color: 'text-amber-500', bg: 'bg-amber-500/10' },
  { id: 'code', label: 'Codice', icon: Code, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
  { id: 'video', label: 'Video', icon: Video, color: 'text-red-500', bg: 'bg-red-500/10' },
  { id: 'multimodal', label: 'Multimodale', icon: Boxes, color: 'text-primary/80', bg: 'bg-primary/10' },
];

// ============================================================================
// LOADING COMPONENT
// ============================================================================

function TabLoader() {
  return (
    <div className="flex items-center justify-center py-20">
      <Loader2 className="w-8 h-8 animate-spin text-primary" />
      <span className="ml-3 text-muted-foreground">Caricamento...</span>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function PortfolioHub() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const location = useLocation();

  // Tab State
  const [activeTab, setActiveTab] = useState<PortfolioTabId>((location.state as any)?.activeTab || 'projects');

  // Projects & Services
  const { data: projects, isLoading: loadingProjects, refetch: refetchProjects } = useProjects(1, {});
  const { data: services, isLoading: loadingServices, refetch: refetchServices } = useServices(1, {});

  // Courses
  const { data: coursesData, isLoading: loadingCourses, refetch: refetchCourses } = useCourses(1, {});
  const deleteCourseMutation = useDeleteCourse();
  const courses = coursesData?.items || [];

  const handleDeleteCourse = async (id: number) => {
    if (!confirm('Sei sicuro di voler eliminare questo corso?')) return;
    try {
      await deleteCourseMutation.mutateAsync(id);
      toast.success('Corso eliminato');
    } catch {
      toast.error('Errore durante l\'eliminazione');
    }
  };

  // ToolAI State
  const [posts, setPosts] = useState<ToolAIPost[]>([]);
  const [toolaiStats, setToolaiStats] = useState<ToolAIStats | null>(null);
  const [loadingToolai, setLoadingToolai] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generateForm, setGenerateForm] = useState<GeneratePostRequest>({
    num_tools: 3,
    categories: ['llm', 'image', 'code', 'audio'],
    auto_publish: false,
    translate: true,
    generate_image: true,
  });

  // Fetch ToolAI data
  const fetchToolaiData = async () => {
    setLoadingToolai(true);
    try {
      const status = statusFilter === 'all' ? undefined : statusFilter;
      const [postsData, statsData] = await Promise.all([
        fetchAdminPosts(1, 20, status),
        fetchStats(),
      ]);
      setPosts(postsData.posts || []);
      setToolaiStats(statsData);
    } catch (error) {
      console.error('Error fetching ToolAI data:', error);
      toast.error('Errore nel caricamento dei dati ToolAI');
    } finally {
      setLoadingToolai(false);
    }
  };

  // Load ToolAI data when tab is active
  useState(() => {
    if (activeTab === 'toolai') {
      fetchToolaiData();
    }
  });

  // Handle ToolAI generate
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
      fetchToolaiData();
    } catch (error) {
      console.error('Error generating post:', error);
      toast.error('Errore nella generazione del post');
    } finally {
      setGenerating(false);
    }
  };

  // Handle ToolAI publish
  const handlePublish = async (postId: number) => {
    try {
      await publishPost(postId);
      toast.success('Post pubblicato!');
      fetchToolaiData();
    } catch (error) {
      toast.error('Errore nella pubblicazione');
    }
  };

  // Handle ToolAI delete
  const handleDelete = async (postId: number) => {
    if (!confirm('Sei sicuro di voler eliminare questo post?')) return;
    try {
      await deletePost(postId);
      toast.success('Post eliminato!');
      fetchToolaiData();
    } catch (error) {
      toast.error('Errore nell\'eliminazione');
    }
  };

  // Format date helper
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  // ============================================================================
  // RENDER PROJECTS TAB
  // ============================================================================

  const renderProjectsTab = () => (
    <div className="space-y-6">
      {/* Actions Bar */}
      <div className="bg-card border border-border rounded-xl p-3 sm:p-4 shadow-sm flex flex-col sm:flex-row justify-between gap-4 items-center">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground font-medium">
            {projects?.total || 0} progetti totali
          </span>
        </div>
        <Link to="/admin/portfolio/project/new" className="w-full sm:w-auto">
          <Button className="bg-primary text-primary-foreground w-full sm:w-auto shadow-md">
            <Plus className="h-4 w-4 mr-2" />
            Nuovo Progetto
          </Button>
        </Link>
      </div>

      {/* Projects Grid */}
      {loadingProjects ? (
        <TabLoader />
      ) : projects?.items && projects.items.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.items.map((project: any) => (
            <Link
              key={project.id}
              to={`/admin/portfolio/project/${project.id}`}
              className="group p-6 bg-card border border-border rounded-xl hover:border-primary/50 transition-all shadow-sm"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-foreground group-hover:text-primary transition">
                    {project.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {project.category} • {project.year}
                  </p>
                </div>
                <Edit className="h-4 w-4 text-muted-foreground group-hover:text-primary transition" />
              </div>
              <p className="text-sm text-muted-foreground line-clamp-2">{project.description}</p>
              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {project.is_public && (
                  <span className="px-2 py-1 bg-green-500/10 text-green-500 text-xs rounded">Pubblico</span>
                )}
                {project.is_featured && (
                  <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded">In evidenza</span>
                )}
                <span className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded">{project.status}</span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-card border border-border rounded-xl">
          <Briefcase className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground mb-4">Nessun progetto presente</p>
          <Link to="/admin/portfolio/project/new">
            <Button variant="outline">Crea il primo progetto</Button>
          </Link>
        </div>
      )}
    </div>
  );

  // ============================================================================
  // RENDER SERVICES TAB
  // ============================================================================

  const renderServicesTab = () => (
    <div className="space-y-6">
      {/* Actions Bar */}
      <div className="bg-card border border-border rounded-xl p-3 sm:p-4 shadow-sm flex flex-col sm:flex-row justify-between gap-4 items-center">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground font-medium">
            {services?.total || 0} servizi totali
          </span>
        </div>
        <Link to="/admin/portfolio/service/new" className="w-full sm:w-auto">
          <Button className="bg-primary text-primary-foreground w-full sm:w-auto shadow-md">
            <Plus className="h-4 w-4 mr-2" />
            Nuovo Servizio
          </Button>
        </Link>
      </div>

      {/* Services Grid */}
      {loadingServices ? (
        <TabLoader />
      ) : services?.items && services.items.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.items.map((service: any) => (
            <Link
              key={service.id}
              to={`/admin/portfolio/service/${service.id}`}
              className="group p-6 bg-card border border-border rounded-xl hover:border-primary/50 transition-all shadow-sm"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-foreground group-hover:text-primary transition">
                    {service.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {service.category}
                  </p>
                </div>
                <Edit className="h-4 w-4 text-muted-foreground group-hover:text-primary transition" />
              </div>
              <p className="text-sm text-muted-foreground line-clamp-2">{service.description}</p>
              <div className="flex items-center gap-2 mt-3 flex-wrap">
                {service.is_active && (
                  <span className="px-2 py-1 bg-green-500/10 text-green-500 text-xs rounded">Attivo</span>
                )}
                {service.is_featured && (
                  <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded">In evidenza</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-card border border-border rounded-xl">
          <Package className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground mb-4">Nessun servizio presente</p>
          <Link to="/admin/portfolio/service/new">
            <Button variant="outline">Crea il primo servizio</Button>
          </Link>
        </div>
      )}
    </div>
  );

  // ============================================================================
  // RENDER COURSES TAB
  // ============================================================================

  const renderCoursesTab = () => (
    <div className="space-y-6">
      {/* Actions Bar */}
      <div className="bg-card border border-border rounded-xl p-3 sm:p-4 shadow-sm flex flex-col sm:flex-row justify-between gap-4 items-center">
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground font-medium">
            {coursesData?.total || 0} corsi totali
          </span>
        </div>
        <Link to="/admin/courses/new" className="w-full sm:w-auto">
          <Button className="bg-primary text-primary-foreground w-full sm:w-auto shadow-md">
            <Plus className="h-4 w-4 mr-2" />
            Nuovo Corso
          </Button>
        </Link>
      </div>

      {/* Courses Grid */}
      {loadingCourses ? (
        <TabLoader />
      ) : courses && courses.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {courses.map((course: any) => (
            <div
              key={course.id}
              className="group p-6 bg-card border border-border rounded-xl hover:border-primary/50 transition-all shadow-sm"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">{course.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition">
                      {course.title}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      Modulo {course.module_number}
                    </p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Link to={`/admin/courses/${course.id}`}>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <Edit className="h-4 w-4 text-muted-foreground group-hover:text-primary transition" />
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                    onClick={() => handleDeleteCourse(course.id)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive opacity-70 hover:opacity-100 transition" />
                  </Button>
                </div>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-2 mb-3">{course.description}</p>
              <div className="flex items-center gap-2 flex-wrap">
                {course.is_new && (
                  <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded">Nuovo</span>
                )}
                <span className={cn(
                  'px-2 py-1 text-xs rounded',
                  course.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-muted text-muted-foreground'
                )}>
                  {course.status === 'active' ? 'Attivo' : course.status}
                </span>
                {course.purchase_url && (
                  <a href={course.purchase_url} target="_blank" rel="noopener noreferrer" className="ml-auto">
                    <ExternalLink className="w-4 h-4 text-muted-foreground hover:text-primary" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-card border border-border rounded-xl">
          <GraduationCap className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground mb-4">Nessun corso presente</p>
          <Link to="/admin/courses/new">
            <Button variant="outline">Crea il primo corso</Button>
          </Link>
        </div>
      )}
    </div>
  );

  const renderToolaiTab = () => (
    <div className="space-y-6">
      {/* Stats Cards */}
      {toolaiStats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground">Totale Post</p>
            <p className="text-2xl font-bold text-foreground">{toolaiStats.total_posts}</p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground">Pubblicati</p>
            <p className="text-2xl font-bold text-green-500">{toolaiStats.published_posts}</p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground">Bozze</p>
            <p className="text-2xl font-bold text-muted-foreground">{toolaiStats.draft_posts}</p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground">Tool Scoperti</p>
            <p className="text-2xl font-bold text-primary">{toolaiStats.total_tools_discovered}</p>
          </div>
        </div>
      )}

      {/* Actions Bar */}
      <div className="bg-card border border-border rounded-xl p-3 sm:p-4 shadow-sm flex flex-col sm:flex-row justify-between gap-4 items-center">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); fetchToolaiData(); }}
            className="flex-1 sm:flex-none px-3 py-2 rounded-lg border border-input bg-background text-foreground min-w-[140px]"
          >
            <option value="all">Tutti gli stati</option>
            <option value="draft">Bozze</option>
            <option value="published">Pubblicati</option>
            <option value="scheduled">Programmati</option>
          </select>
          <Button variant="outline" size="sm" onClick={fetchToolaiData} className="flex-shrink-0">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
        <Button
          onClick={() => setShowGenerateModal(true)}
          className="bg-primary text-primary-foreground w-full sm:w-auto shadow-md"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          Genera Post AI
        </Button>
      </div>

      {/* Posts List */}
      {loadingToolai ? (
        <TabLoader />
      ) : posts.length > 0 ? (
        <div className="space-y-3">
          {posts.map((post) => (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-card border border-border rounded-xl p-4 hover:border-primary/50 transition-all"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={cn('px-2 py-1 rounded text-xs', STATUS_CONFIG[post.status]?.bgColor, STATUS_CONFIG[post.status]?.color)}>
                      {STATUS_CONFIG[post.status]?.label}
                    </span>
                    {post.tools && post.tools.length > 0 && post.tools[0].category && (
                      <span className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded">
                        {post.tools[0].category}
                      </span>
                    )}
                  </div>
                  <h3 className="font-semibold text-foreground truncate">{post.title_it}</h3>
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{post.summary_it}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    {formatDate(post.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {post.status === 'draft' && (
                    <Button size="sm" variant="outline" onClick={() => handlePublish(post.id)}>
                      <Send className="h-4 w-4" />
                    </Button>
                  )}
                  <a href={`/toolai/${post.slug}`} target="_blank" rel="noopener noreferrer">
                    <Button size="sm" variant="outline">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </a>
                  <Button size="sm" variant="outline" onClick={() => handleDelete(post.id)}>
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-card border border-border rounded-xl">
          <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground mb-4">Nessun post ToolAI</p>
          <Button onClick={() => setShowGenerateModal(true)} variant="outline">
            Genera il primo post
          </Button>
        </div>
      )}

      {/* Generate Modal */}
      <AnimatePresence>
        {showGenerateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm"
            onClick={() => setShowGenerateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-card border border-border rounded-2xl p-6 w-full max-w-md shadow-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-foreground">Genera Post AI</h3>
                <Button variant="ghost" size="icon" onClick={() => setShowGenerateModal(false)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Numero di tool
                  </label>
                  <input
                    type="number"
                    min={1}
                    max={10}
                    value={generateForm.num_tools}
                    onChange={(e) => setGenerateForm({ ...generateForm, num_tools: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 rounded-lg border border-input bg-background text-foreground"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Categorie
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {CATEGORIES.map((cat) => (
                      <button
                        key={cat.id}
                        onClick={() => {
                          const cats = generateForm.categories || [];
                          if (cats.includes(cat.id)) {
                            setGenerateForm({ ...generateForm, categories: cats.filter(c => c !== cat.id) });
                          } else {
                            setGenerateForm({ ...generateForm, categories: [...cats, cat.id] });
                          }
                        }}
                        className={cn(
                          'px-3 py-1.5 rounded-lg text-sm transition-all',
                          generateForm.categories?.includes(cat.id)
                            ? `${cat.bg} ${cat.color} ring-2 ring-offset-2 ring-offset-background`
                            : 'bg-muted text-muted-foreground hover:bg-muted/80'
                        )}
                      >
                        {cat.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={generateForm.auto_publish}
                      onChange={(e) => setGenerateForm({ ...generateForm, auto_publish: e.target.checked })}
                      className="rounded border-input"
                    />
                    <span className="text-sm text-foreground">Pubblica automaticamente</span>
                  </label>
                </div>

                <Button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="w-full bg-primary text-primary-foreground"
                >
                  {generating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Generazione...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Genera Post
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <div className={cn(SPACING.padding.full, 'space-y-4 sm:space-y-6')}>
      {/* Header with Tab Navigation - Pattern AIMarketing */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-4"
      >
        {/* Title Row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
              <Briefcase className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Portfolio Hub</h1>
              <p className="text-sm text-muted-foreground">
                {PORTFOLIO_TABS.find(t => t.id === activeTab)?.description}
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation - Pattern AIMarketing */}
        <div className="bg-card border border-border rounded-2xl p-2 shadow-sm">
          <div className="flex gap-1 overflow-x-auto">
            {PORTFOLIO_TABS.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    if (tab.id === 'toolai') fetchToolaiData();
                  }}
                  className={cn(
                    'flex-1 min-w-[120px] flex flex-col items-center gap-1 py-3 px-4 rounded-xl transition-all',
                    isActive
                      ? `bg-gradient-to-r ${tab.color} text-white shadow-lg`
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-xs font-medium whitespace-nowrap">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </motion.div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'projects' && (
          <motion.div
            key="projects"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {renderProjectsTab()}
          </motion.div>
        )}

        {activeTab === 'services' && (
          <motion.div
            key="services"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {renderServicesTab()}
          </motion.div>
        )}

        {activeTab === 'courses' && (
          <motion.div
            key="courses"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {renderCoursesTab()}
          </motion.div>
        )}

        {activeTab === 'toolai' && (
          <motion.div
            key="toolai"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {renderToolaiTab()}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default PortfolioHub;
