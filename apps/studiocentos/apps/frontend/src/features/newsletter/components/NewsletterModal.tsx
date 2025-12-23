import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Loader2, Mail, X } from 'lucide-react';
import { Button } from '@/shared/components/ui/button';
import { Input } from '@/shared/components/ui/input';
import { cn } from '@/shared/lib/utils';
import { useSubscribe } from '../api/useNewsletter';
import { toast } from 'sonner';
import { useLanguage } from '@/features/landing/i18n/LanguageContext';
import { useTheme } from '@/shared/contexts/ThemeContext';

interface NewsletterModalProps {
    children: React.ReactNode;
    source?: string;
}

export function NewsletterModal({ children, source = 'website' }: NewsletterModalProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [email, setEmail] = useState('');
    const { mutate, isPending } = useSubscribe();
    const { language } = useLanguage();
    const { theme } = useTheme();
    const isDark = theme === 'dark';

    // Fallback logic for language key
    const langKey = (language === 'en' || language === 'es') ? language : 'it';

    const labels: any = {
        title: {
            it: 'Rimani aggiornato',
            en: 'Stay updated',
            es: 'Mantente actualizado',
        },
        description: {
            it: 'Inserisci la tua email per ricevere notifiche sul lancio dei corsi e novità esclusive.',
            en: 'Enter your email to receive notifications about course launches and exclusive news.',
            es: 'Introduce tu correo electrónico para recibir notificaciones sobre el lanzamiento de cursos y noticias exclusivas.',
        },
        placeholder: {
            it: 'latua@email.com',
            en: 'your@email.com',
            es: 'tu@email.com',
        },
        button: {
            it: 'Iscriviti',
            en: 'Subscribe',
            es: 'Suscríbete',
        },
        success: {
            it: 'Iscrizione completata! Ti aggiorneremo presto.',
            en: 'Subscription complete! We will update you soon.',
            es: '¡Suscripción completada! Te actualizaremos pronto.',
        },
        error: {
            it: 'Qualcosa è andato storto. Riprova.',
            en: 'Something went wrong. Try again.',
            es: 'Algo salió mal. Inténtalo de nuevo.',
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!email) return;

        mutate(
            { email, source },
            {
                onSuccess: () => {
                    toast.success("✨ " + labels.success[langKey]);
                    setIsOpen(false);
                    setEmail('');
                },
                onError: () => {
                    toast.error("❌ " + labels.error[langKey]);
                },
            }
        );
    };

    // Styling constants
    const modalBg = 'bg-background/95 backdrop-blur-xl border border-primary/20';
    const textPrimary = 'text-foreground';
    const textSecondary = 'text-muted-foreground';
    const inputBg = 'bg-background/50 border-input';

    return (
        <>
            {/* Trigger */}
            <div onClick={() => setIsOpen(true)} className="inline-block cursor-pointer">
                {children}
            </div>

            {/* Modal */}
            <AnimatePresence>
                {isOpen && (
                    <>
                        {/* Backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsOpen(false)}
                            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
                        />

                        {/* Content */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="fixed inset-0 z-[101] flex items-center justify-center p-4"
                            onClick={(e) => e.stopPropagation()} // Prevent closing when clicking content
                        >
                            <div className={cn('w-full max-w-md rounded-2xl shadow-2xl p-6 relative', modalBg)}>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="absolute right-4 top-4 text-muted-foreground hover:text-foreground transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>

                                <div className="text-center mb-6">
                                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4 mx-auto text-primary">
                                        <Mail className="w-6 h-6" />
                                    </div>
                                    <h2 className={cn("text-2xl font-bold mb-2", textPrimary)}>
                                        {labels.title[langKey]}
                                    </h2>
                                    <p className={cn("text-sm", textSecondary)}>
                                        {labels.description[langKey]}
                                    </p>
                                </div>

                                <form onSubmit={handleSubmit} className="space-y-4">
                                    <Input
                                        type="email"
                                        placeholder={labels.placeholder[langKey]}
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        className={cn("w-full", inputBg)}
                                    />
                                    <Button
                                        type="submit"
                                        className="w-full font-bold shadow-lg shadow-primary/20"
                                        disabled={isPending}
                                    >
                                        {isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />}
                                        {labels.button[langKey]}
                                    </Button>
                                </form>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </>
    );
}
