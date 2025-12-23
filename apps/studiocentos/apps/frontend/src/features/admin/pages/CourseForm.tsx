/**
 * Course Form - Create/Edit course
 * Pattern: Same as ProjectForm
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    GraduationCap, Save, ArrowLeft, Loader2, Link as LinkIcon,
    Image, Clock, BookOpen
} from 'lucide-react';
import { Button } from '../../../shared/components/ui/button';
import { cn } from '../../../shared/lib/utils';
import { toast } from 'sonner';
import { useCourse, useCreateCourse, useUpdateCourse } from '../hooks/useCourses';
import { SPACING } from '../../../shared/config/constants';

const DIFFICULTY_OPTIONS = [
    { id: 'beginner', label: 'Base', color: 'emerald' },
    { id: 'intermediate', label: 'Intermedio', color: 'amber' },
    { id: 'advanced', label: 'Avanzato', color: 'red' },
];

const STATUS_OPTIONS = [
    { id: 'active', label: 'Attivo' },
    { id: 'draft', label: 'Bozza' },
    { id: 'archived', label: 'Archiviato' },
];

const ICON_OPTIONS = ['🎮', '🏗️', '✨', '✍️', '🎬', '📱', '💰', '🤖', '💡', '🚀', '⚡', '🔥', '📚', '🎯'];

export function CourseForm() {
    const navigate = useNavigate();
    const { id } = useParams<{ id: string }>();
    const isEditing = !!id && id !== 'new';

    const { data: existingCourse, isLoading: loadingCourse } = useCourse(isEditing ? parseInt(id) : 0);
    const createMutation = useCreateCourse();
    const updateMutation = useUpdateCourse();

    const [form, setForm] = useState({
        title: '',
        slug: '',
        description: '',
        icon: '🎮',
        module_number: 1,
        purchase_url: '',
        preview_url: '',
        duration_hours: '',
        difficulty: 'beginner',
        topics: '',
        price: '',
        status: 'active',
        is_featured: false,
        is_new: false,
        is_public: true,
        thumbnail_url: '',
        cover_image: '',
    });

    useEffect(() => {
        if (existingCourse) {
            setForm({
                title: existingCourse.title || '',
                slug: existingCourse.slug || '',
                description: existingCourse.description || '',
                icon: existingCourse.icon || '🎮',
                module_number: existingCourse.module_number || 1,
                purchase_url: existingCourse.purchase_url || '',
                preview_url: existingCourse.preview_url || '',
                duration_hours: existingCourse.duration_hours?.toString() || '',
                difficulty: existingCourse.difficulty || 'beginner',
                topics: (existingCourse.topics || []).join(', '),
                price: existingCourse.price || '',
                status: existingCourse.status || 'active',
                is_featured: existingCourse.is_featured || false,
                is_new: existingCourse.is_new || false,
                is_public: existingCourse.is_public ?? true,
                thumbnail_url: existingCourse.thumbnail_url || '',
                cover_image: existingCourse.cover_image || '',
            });
        }
    }, [existingCourse]);

    const generateSlug = (title: string) => {
        return title
            .toLowerCase()
            .replace(/[^a-z0-9\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim();
    };

    const handleTitleChange = (title: string) => {
        setForm(prev => ({
            ...prev,
            title,
            slug: isEditing ? prev.slug : generateSlug(title)
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!form.title || !form.slug || !form.description || !form.purchase_url) {
            toast.error('Compila tutti i campi obbligatori');
            return;
        }

        const courseData = {
            ...form,
            module_number: parseInt(form.module_number.toString()) || 1,
            duration_hours: form.duration_hours ? parseInt(form.duration_hours) : null,
            topics: form.topics.split(',').map(t => t.trim()).filter(Boolean),
        };

        try {
            if (isEditing) {
                await updateMutation.mutateAsync({ id: parseInt(id!), data: courseData });
                toast.success('Corso aggiornato!');
            } else {
                await createMutation.mutateAsync(courseData);
                toast.success('Corso creato!');
            }
            navigate('/admin/portfolio', { state: { activeTab: 'courses' } });
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Errore durante il salvataggio');
        }
    };

    const isSaving = createMutation.isPending || updateMutation.isPending;

    if (isEditing && loadingCourse) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className={cn(SPACING.padding.full, 'space-y-6 max-w-4xl mx-auto')}>
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between"
            >
                <div className="flex items-center gap-3">
                    <Button variant="ghost" size="sm" onClick={() => navigate('/admin/portfolio', { state: { activeTab: 'courses' } })}>
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Indietro
                    </Button>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
                            <GraduationCap className="w-5 h-5 text-primary-foreground" />
                        </div>
                        <h1 className="text-xl font-bold text-foreground">
                            {isEditing ? 'Modifica Corso' : 'Nuovo Corso'}
                        </h1>
                    </div>
                </div>
            </motion.div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Info */}
                <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-4">
                    <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                        <BookOpen className="w-5 h-5 text-primary" />
                        Informazioni Base
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-foreground mb-1">Titolo *</label>
                            <input
                                type="text"
                                value={form.title}
                                onChange={(e) => handleTitleChange(e.target.value)}
                                placeholder="Es: Visual Wow"
                                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">Slug *</label>
                            <input
                                type="text"
                                value={form.slug}
                                onChange={(e) => setForm(prev => ({ ...prev, slug: e.target.value }))}
                                placeholder="visual-wow"
                                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">Numero Modulo *</label>
                            <input
                                type="number"
                                min="1"
                                value={form.module_number}
                                onChange={(e) => setForm(prev => ({ ...prev, module_number: parseInt(e.target.value) || 1 }))}
                                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary"
                                required
                            />
                        </div>

                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-foreground mb-1">Descrizione *</label>
                            <textarea
                                value={form.description}
                                onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
                                rows={3}
                                placeholder="Descrizione del corso..."
                                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary resize-none"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">Icona</label>
                            <div className="flex flex-wrap gap-2">
                                {ICON_OPTIONS.map(icon => (
                                    <button
                                        key={icon}
                                        type="button"
                                        onClick={() => setForm(prev => ({ ...prev, icon }))}
                                        className={cn(
                                            'w-10 h-10 rounded-lg border-2 flex items-center justify-center text-xl transition-all',
                                            form.icon === icon ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/50'
                                        )}
                                    >
                                        {icon}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">Difficoltà</label>
                            <div className="flex gap-2">
                                {DIFFICULTY_OPTIONS.map(opt => (
                                    <button
                                        key={opt.id}
                                        type="button"
                                        onClick={() => setForm(prev => ({ ...prev, difficulty: opt.id }))}
                                        className={cn(
                                            'px-3 py-1.5 rounded-lg border text-sm font-medium transition-all',
                                            form.difficulty === opt.id
                                                ? 'border-primary bg-primary/10 text-primary'
                                                : 'border-border text-muted-foreground hover:border-primary/50'
                                        )}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Links */}
                <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-4">
                    <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                        <LinkIcon className="w-5 h-5 text-primary" />
                        Links
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">URL Acquisto *</label>
                            <input
                                type="url"
                                value={form.purchase_url}
                                onChange={(e) => setForm(prev => ({ ...prev, purchase_url: e.target.value }))}
                                placeholder="https://gum.co/..."
                                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">URL Preview</label>
                            <input
                                type="url"
                                value={form.preview_url}
                                onChange={(e) => setForm(prev => ({ ...prev, preview_url: e.target.value }))}
                                placeholder="https://..."
                                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">Prezzo</label>
                            <input
                                type="text"
                                value={form.price}
                                onChange={(e) => setForm(prev => ({ ...prev, price: e.target.value }))}
                                placeholder="€49"
                                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">Durata (ore)</label>
                            <input
                                type="number"
                                value={form.duration_hours}
                                onChange={(e) => setForm(prev => ({ ...prev, duration_hours: e.target.value }))}
                                placeholder="10"
                                className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:ring-2 focus:ring-primary"
                            />
                        </div>
                    </div>
                </div>

                {/* Status & Visibility */}
                <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-4">
                    <h2 className="text-lg font-semibold text-foreground">Stato e Visibilità</h2>

                    <div className="flex flex-wrap gap-4">
                        <div>
                            <label className="block text-sm font-medium text-foreground mb-1">Stato</label>
                            <div className="flex gap-2">
                                {STATUS_OPTIONS.map(opt => (
                                    <button
                                        key={opt.id}
                                        type="button"
                                        onClick={() => setForm(prev => ({ ...prev, status: opt.id }))}
                                        className={cn(
                                            'px-3 py-1.5 rounded-lg border text-sm font-medium transition-all',
                                            form.status === opt.id
                                                ? 'border-primary bg-primary/10 text-primary'
                                                : 'border-border text-muted-foreground hover:border-primary/50'
                                        )}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-4">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={form.is_featured}
                                    onChange={(e) => setForm(prev => ({ ...prev, is_featured: e.target.checked }))}
                                    className="w-4 h-4 rounded accent-primary"
                                />
                                <span className="text-sm text-foreground">In Evidenza</span>
                            </label>

                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={form.is_new}
                                    onChange={(e) => setForm(prev => ({ ...prev, is_new: e.target.checked }))}
                                    className="w-4 h-4 rounded accent-primary"
                                />
                                <span className="text-sm text-foreground">Nuovo</span>
                            </label>

                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={form.is_public}
                                    onChange={(e) => setForm(prev => ({ ...prev, is_public: e.target.checked }))}
                                    className="w-4 h-4 rounded accent-primary"
                                />
                                <span className="text-sm text-foreground">Pubblico</span>
                            </label>
                        </div>
                    </div>
                </div>

                {/* Submit */}
                <div className="flex justify-end gap-3">
                    <Button type="button" variant="outline" onClick={() => navigate('/admin/portfolio', { state: { activeTab: 'courses' } })}>
                        Annulla
                    </Button>
                    <Button type="submit" disabled={isSaving} className="bg-primary hover:bg-primary/90">
                        {isSaving ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Salvataggio...
                            </>
                        ) : (
                            <>
                                <Save className="w-4 h-4 mr-2" />
                                {isEditing ? 'Aggiorna' : 'Crea Corso'}
                            </>
                        )}
                    </Button>
                </div>
            </form>
        </div>
    );
}

export default CourseForm;
