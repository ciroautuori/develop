/**
 * Project Form - Create/Edit Project
 * CRUD completo enterprise per Progetti
 * LIGHT MODE SUPPORT
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'sonner';
import { Save, ArrowLeft, Trash2, Globe, Sparkles, Loader2 } from 'lucide-react';
import { useProject, useCreateProject, useUpdateProject, useDeleteProject } from '../hooks/usePortfolio';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';
import { cn } from '../../../shared/lib/utils';

export function ProjectForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Dynamic classes
  const cardBg = isDark
    ? 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
    : 'bg-white border border-gray-200 shadow-sm';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const textLabel = isDark ? 'text-gray-300' : 'text-gray-700';
  const inputBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-gray-50 border-gray-200 text-gray-900';
  const selectBg = isDark
    ? 'bg-white/5 border-white/10 text-white'
    : 'bg-white border-gray-300 text-gray-900';
  const tagBg = isDark ? 'bg-white/10 text-white' : 'bg-gray-100 text-gray-700';
  const buttonSecondary = isDark
    ? 'bg-white/5 hover:bg-white/10 text-white'
    : 'bg-gray-100 hover:bg-gray-200 text-gray-700';

  // Hooks
  const { data: project, isLoading } = useProject(Number(id));
  const createProject = useCreateProject();
  const updateProject = useUpdateProject();
  const deleteProject = useDeleteProject();

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    description: '',
    year: new Date().getFullYear(),
    category: '',
    live_url: '',
    github_url: '',
    demo_url: '',
    technologies: [] as string[],
    metrics: {} as Record<string, string>,
    status: 'active',
    is_featured: false,
    is_public: true,
    order: 0,
    thumbnail_url: '',
    images: [] as string[],
    translations: {
      en: { title: '', description: '' },
      es: { title: '', description: '' }
    } as Record<string, { title: string; description: string }>,
  });

  const [techInput, setTechInput] = useState('');
  const [metricKey, setMetricKey] = useState('');
  const [metricValue, setMetricValue] = useState('');
  const [imageInput, setImageInput] = useState('');
  const [isGeneratingTranslations, setIsGeneratingTranslations] = useState(false);

  // Generate translations with AI
  const generateTranslations = async () => {
    if (!formData.title || !formData.description) {
      toast.error('Inserisci titolo e descrizione in italiano prima di generare le traduzioni');
      return;
    }

    setIsGeneratingTranslations(true);
    try {
      const token = localStorage.getItem('admin_token');
      const res = await fetch('/api/v1/portfolio/admin/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: formData.title,
          description: formData.description,
          source_language: 'it',
          target_languages: ['en', 'es']
        })
      });

      if (res.ok) {
        const data = await res.json();
        setFormData(prev => ({
          ...prev,
          translations: {
            en: data.translations.en || prev.translations.en,
            es: data.translations.es || prev.translations.es
          }
        }));
        toast.success('🤖 Traduzioni generate con AI!');
      } else {
        const error = await res.json();
        throw new Error(error.detail || 'Errore nella generazione');
      }
    } catch (error: any) {
      console.error('Translation error:', error);
      toast.error(error.message || 'Errore nella generazione delle traduzioni');
    } finally {
      setIsGeneratingTranslations(false);
    }
  };

  // Load project data
  useEffect(() => {
    if (project) {
      setFormData({
        title: project.title || '',
        slug: project.slug || '',
        description: project.description || '',
        year: project.year || new Date().getFullYear(),
        category: project.category || '',
        live_url: project.live_url || '',
        github_url: project.github_url || '',
        demo_url: project.demo_url || '',
        technologies: project.technologies || [],
        metrics: project.metrics || {},
        status: project.status || 'active',
        is_featured: project.is_featured || false,
        is_public: project.is_public ?? true,
        order: project.order || 0,
        thumbnail_url: project.thumbnail_url || '',
        images: project.images || [],
        translations: project.translations || {
          en: { title: '', description: '' },
          es: { title: '', description: '' }
        },
      });
    }
  }, [project]);

  // Auto-generate slug
  const handleTitleChange = (value: string) => {
    setFormData(prev => ({
      ...prev,
      title: value,
      slug: value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
    }));
  };

  // Technologies
  const addTechnology = () => {
    if (techInput.trim()) {
      setFormData(prev => ({
        ...prev,
        technologies: [...prev.technologies, techInput.trim()]
      }));
      setTechInput('');
    }
  };

  const removeTechnology = (index: number) => {
    setFormData(prev => ({
      ...prev,
      technologies: prev.technologies.filter((_, i) => i !== index)
    }));
  };

  // Metrics
  const addMetric = () => {
    if (metricKey.trim() && metricValue.trim()) {
      setFormData(prev => ({
        ...prev,
        metrics: { ...prev.metrics, [metricKey.trim()]: metricValue.trim() }
      }));
      setMetricKey('');
      setMetricValue('');
    }
  };

  const removeMetric = (key: string) => {
    setFormData(prev => {
      const newMetrics = { ...prev.metrics };
      delete newMetrics[key];
      return { ...prev, metrics: newMetrics };
    });
  };

  // Submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (isEdit) {
        await updateProject.mutateAsync({ id: Number(id), data: formData });
        toast.success('Progetto aggiornato con successo!');
      } else {
        await createProject.mutateAsync(formData);
        toast.success('Progetto creato con successo!');
      }
      navigate('/admin/portfolio');
    } catch (error: any) {
      toast.error(error.message || 'Errore durante il salvataggio');
    }
  };

  // Delete
  const handleDelete = async () => {
    if (!confirm('Sei sicuro di voler eliminare questo progetto?')) return;
    try {
      await deleteProject.mutateAsync(Number(id));
      toast.success('Progetto eliminato!');
      navigate('/admin/portfolio');
    } catch (error: any) {
      toast.error('Errore durante l\'eliminazione');
    }
  };

  if (isLoading && isEdit) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gold text-xl">Caricamento...</div>
      </div>
    );
  }

  return (
    <div className={cn(SPACING.padding.full, SPACING.lg, 'pb-16')}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className={`text-4xl font-bold ${textPrimary}`}>
            {isEdit ? 'Modifica Progetto' : 'Nuovo Progetto'}
          </h1>
          <p className={`mt-2 ${textSecondary}`}>
            {isEdit ? 'Aggiorna i dettagli del progetto' : 'Crea un nuovo progetto per il portfolio'}
          </p>
        </div>
        <button
          onClick={() => navigate('/admin/portfolio')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${buttonSecondary}`}
        >
          <ArrowLeft className="h-5 w-5" />
          Indietro
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className={`${cardBg} rounded-3xl p-8`}>
          <h2 className={`text-2xl font-semibold mb-6 ${textPrimary}`}>Informazioni Base</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Titolo *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => handleTitleChange(e.target.value)}
                className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                required
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Slug</label>
              <input
                type="text"
                value={formData.slug}
                onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
                className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                required
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Anno *</label>
              <input
                type="number"
                value={formData.year}
                onChange={(e) => setFormData(prev => ({ ...prev, year: Number(e.target.value) }))}
                className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                required min="2000" max="2100"
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Categoria *</label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                placeholder="es. SaaS Platform, AI Platform"
                required
              />
            </div>
          </div>
          <div className="mt-6">
            <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Descrizione *</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
              rows={4}
              placeholder="Descrizione storytelling del progetto..."
              required
            />
          </div>
        </div>

        {/* URLs */}
        <div className={`${cardBg} rounded-3xl p-8`}>
          <h2 className={`text-2xl font-semibold mb-6 ${textPrimary}`}>Link</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <label className={`block text-sm font-medium mb-2 ${textLabel}`}>URL Live</label>
              <input
                type="url"
                value={formData.live_url}
                onChange={(e) => setFormData(prev => ({ ...prev, live_url: e.target.value }))}
                className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                placeholder="https://example.com"
              />
            </div>
            <div>
              <label className={`block text-sm font-medium mb-2 ${textLabel}`}>GitHub URL</label>
              <input
                type="url"
                value={formData.github_url}
                onChange={(e) => setFormData(prev => ({ ...prev, github_url: e.target.value }))}
                className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                placeholder="https://github.com/..."
              />
            </div>
          </div>
        </div>

        {/* Technologies */}
        <div className={`${cardBg} rounded-3xl p-8`}>
          <h2 className={`text-2xl font-semibold mb-6 ${textPrimary}`}>Tecnologie</h2>
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={techInput}
              onChange={(e) => setTechInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTechnology())}
              className={`flex-1 px-4 py-2 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
              placeholder="es. React 19, FastAPI, PostgreSQL"
            />
            <button type="button" onClick={addTechnology} className="px-6 py-2 bg-gold text-black rounded-lg hover:bg-gold/90 transition">
              Aggiungi
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.technologies.map((tech, index) => (
              <span key={index} className={`px-4 py-2 rounded-full text-sm flex items-center gap-2 ${tagBg}`}>
                {tech}
                <button type="button" onClick={() => removeTechnology(index)} className="text-gray-400 hover:text-gray-400">×</button>
              </span>
            ))}
          </div>
        </div>

        {/* Metrics */}
        <div className={`${cardBg} rounded-3xl p-8`}>
          <h2 className={`text-2xl font-semibold mb-6 ${textPrimary}`}>Metriche</h2>
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={metricKey}
              onChange={(e) => setMetricKey(e.target.value)}
              className={`flex-1 px-4 py-2 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
              placeholder="Chiave"
            />
            <input
              type="text"
              value={metricValue}
              onChange={(e) => setMetricValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addMetric())}
              className={`flex-1 px-4 py-2 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
              placeholder="Valore"
            />
            <button type="button" onClick={addMetric} className="px-6 py-2 bg-gold text-black rounded-lg hover:bg-gold/90 transition">
              Aggiungi
            </button>
          </div>
          <div className="space-y-2">
            {Object.entries(formData.metrics).map(([key, value]) => (
              <div key={key} className={`flex items-center justify-between px-4 py-3 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
                <span className={textPrimary}><strong>{key}:</strong> {value}</span>
                <button type="button" onClick={() => removeMetric(key)} className="text-gray-400 hover:text-gray-400">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Settings */}
        <div className={`${cardBg} rounded-3xl p-8`}>
          <h2 className={`text-2xl font-semibold mb-6 ${textPrimary}`}>Impostazioni</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <div>
              <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Stato</label>
              <select
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
                className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${selectBg}`}
              >
                <option value="active">Attivo</option>
                <option value="draft">Bozza</option>
                <option value="archived">Archiviato</option>
              </select>
            </div>
            <div>
              <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Ordine</label>
              <input
                type="number"
                value={formData.order}
                onChange={(e) => setFormData(prev => ({ ...prev, order: Number(e.target.value) }))}
                className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                min="0"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mt-4 sm:mt-6">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_public}
                onChange={(e) => setFormData(prev => ({ ...prev, is_public: e.target.checked }))}
                className={`w-5 h-5 rounded text-gold focus:ring-gold ${isDark ? 'border-white/20 bg-white/5' : 'border-gray-300 bg-white'}`}
              />
              <span className={textPrimary}>Pubblico</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_featured}
                onChange={(e) => setFormData(prev => ({ ...prev, is_featured: e.target.checked }))}
                className={`w-5 h-5 rounded text-gold focus:ring-gold ${isDark ? 'border-white/20 bg-white/5' : 'border-gray-300 bg-white'}`}
              />
              <span className={textPrimary}>In evidenza</span>
            </label>
          </div>
        </div>

        {/* Translations */}
        <div className={`${cardBg} rounded-3xl p-8`}>
          <div className="flex items-center justify-between mb-6">
            <h2 className={`text-2xl font-semibold ${textPrimary} flex items-center gap-2`}>
              <Globe className="h-6 w-6 text-gold" />
              Traduzioni (Multilingua)
            </h2>
            <button
              type="button"
              onClick={generateTranslations}
              disabled={isGeneratingTranslations}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-gold to-gold hover:from-gold/90 hover:to-gold text-white rounded-lg transition disabled:opacity-50"
            >
              {isGeneratingTranslations ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Sparkles className="h-5 w-5" />
              )}
              {isGeneratingTranslations ? 'Generazione...' : 'Genera con AI'}
            </button>
          </div>
          <p className={`mb-6 ${textSecondary}`}>
            Inserisci le traduzioni manualmente o usa il pulsante "Genera con AI" per tradurre automaticamente.
          </p>

          {/* English */}
          <div className="mb-6">
            <h3 className={`text-lg font-medium mb-4 ${textPrimary}`}>🇬🇧 English</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Title (EN)</label>
                <input
                  type="text"
                  value={formData.translations?.en?.title || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    translations: {
                      ...prev.translations,
                      en: { ...prev.translations.en, title: e.target.value }
                    }
                  }))}
                  className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                  placeholder="English title..."
                />
              </div>
              <div>
                <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Description (EN)</label>
                <textarea
                  value={formData.translations?.en?.description || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    translations: {
                      ...prev.translations,
                      en: { ...prev.translations.en, description: e.target.value }
                    }
                  }))}
                  className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                  rows={3}
                  placeholder="English description..."
                />
              </div>
            </div>
          </div>

          {/* Spanish */}
          <div>
            <h3 className={`text-lg font-medium mb-4 ${textPrimary}`}>🇪🇸 Español</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Título (ES)</label>
                <input
                  type="text"
                  value={formData.translations?.es?.title || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    translations: {
                      ...prev.translations,
                      es: { ...prev.translations.es, title: e.target.value }
                    }
                  }))}
                  className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                  placeholder="Título en español..."
                />
              </div>
              <div>
                <label className={`block text-sm font-medium mb-2 ${textLabel}`}>Descripción (ES)</label>
                <textarea
                  value={formData.translations?.es?.description || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    translations: {
                      ...prev.translations,
                      es: { ...prev.translations.es, description: e.target.value }
                    }
                  }))}
                  className={`w-full px-4 py-3 border rounded-lg focus:border-gold focus:outline-none ${inputBg}`}
                  rows={3}
                  placeholder="Descripción en español..."
                />
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <div>
            {isEdit && (
              <button type="button" onClick={handleDelete} className="flex items-center gap-2 px-6 py-3 bg-gray-500 hover:bg-white/10 text-white rounded-lg transition">
                <Trash2 className="h-5 w-5" />
                Elimina Progetto
              </button>
            )}
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={() => navigate('/admin/portfolio')} className={`px-6 py-3 rounded-lg transition ${buttonSecondary}`}>
              Annulla
            </button>
            <button
              type="submit"
              disabled={createProject.isPending || updateProject.isPending}
              className="flex items-center gap-2 px-6 py-3 bg-gold text-black rounded-lg hover:bg-gold/90 transition disabled:opacity-50"
            >
              <Save className="h-5 w-5" />
              {isEdit ? 'Salva Modifiche' : 'Crea Progetto'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
