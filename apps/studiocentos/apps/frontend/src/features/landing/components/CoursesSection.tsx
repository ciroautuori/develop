/**
 * Courses Section Component - Corso Tool AI
 * DINAMICO - Dati dal database via API
 */

import { motion } from 'framer-motion';
import type { Course } from '../types/landing.types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../../shared/components/ui/card';
import { Button } from '../../../shared/components/ui/button';
import { Badge } from '../../../shared/components/ui/badge';
import { ExternalLink, PlayCircle, Rocket, Sparkles, Star } from 'lucide-react';
import { useLanguage } from '../i18n';
import { NewsletterModal } from '@/features/newsletter/components/NewsletterModal';

interface CoursesSectionProps {
    courses: Course[];
}

const DIFFICULTY_LABELS: Record<string, Record<string, string>> = {
    beginner: { it: 'Base', en: 'Beginner', es: 'Básico' },
    intermediate: { it: 'Intermedio', en: 'Intermediate', es: 'Intermedio' },
    advanced: { it: 'Avanzato', en: 'Advanced', es: 'Avanzado' },
};

const BADGE_LABELS: Record<string, Record<string, string>> = {
    new: { it: 'NUOVO', en: 'NEW', es: 'NUEVO' },
    top: { it: 'TOP', en: 'TOP', es: 'TOP' },
};

export function CoursesSection({ courses }: CoursesSectionProps) {
    const { t, language } = useLanguage();

    // Helper for localized dynamic content
    const getLocalizedContent = (course: Course) => {
        // If language matches default or no translations, return direct fields
        // Assuming default content is Italian (or as seeded)
        // If we want to be strict: logic depends on how data is stored.
        // Usually: course.title is default. translations is JSON.

        if (language === 'it') {
            return { title: course.title, description: course.description };
        }

        const translations = typeof course.translations === 'string'
            ? JSON.parse(course.translations)
            : course.translations;

        if (translations && translations[language]) {
            return {
                title: translations[language].title || course.title,
                description: translations[language].description || course.description
            };
        }

        return { title: course.title, description: course.description };
    };

    // Enterprise 2025: Show section even if empty, with "Coming Soon" state
    const hasCourses = courses && courses.length > 0;

    return (
        <section id="corsi" className="py-12 md:py-24 bg-background relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(212,175,55,0.05)_0%,transparent_50%)]" />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="text-center mb-10 md:mb-16">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-block"
                    >
                        <Badge variant="outline" className="mb-4 border-primary/30 text-primary bg-primary/5 px-4 py-1.5 text-sm font-medium rounded-full">
                            <PlayCircle className="w-3.5 h-3.5 mr-2 animate-pulse" />
                            {t.courses.title.toUpperCase()}
                        </Badge>
                    </motion.div>

                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-3xl md:text-5xl font-bold tracking-tight text-foreground mb-4"
                    >
                        {t.courses.title} <span className="text-primary">{t.courses.titleHighlight}</span>
                    </motion.h2>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-base md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed"
                    >
                        {t.courses.subtitle}
                    </motion.p>
                </div>

                {hasCourses ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {courses.map((course, index) => {
                            const { title, description } = getLocalizedContent(course);
                            const langKey = (language === 'it' || language === 'en' || language === 'es') ? language : 'it';

                            return (
                                <motion.div
                                    key={course.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: index * 0.1 }}
                                >
                                    <Card className="h-full border-border/60 bg-card/50 backdrop-blur-sm hover:bg-card hover:border-primary/30 transition-all duration-300 group flex flex-col">
                                        <CardHeader className="pb-3">
                                            <div className="flex justify-between items-start mb-2">
                                                <span className="text-4xl font-black text-muted-foreground/10 group-hover:text-primary/10 transition-colors">
                                                    M{course.module_number}
                                                </span>
                                                <div className="flex gap-1.5">
                                                    {course.is_new && (
                                                        <Badge variant="secondary" className="bg-primary/20 text-primary hover:bg-primary/30 text-[10px] px-1.5 py-0.5 h-5">
                                                            <Sparkles className="w-3 h-3 mr-0.5" />
                                                            <Sparkles className="w-3 h-3 mr-0.5" />
                                                            {BADGE_LABELS.new[langKey]}
                                                        </Badge>
                                                    )}
                                                    {course.is_featured && (
                                                        <Badge variant="secondary" className="bg-amber-500/20 text-amber-400 text-[10px] px-1.5 py-0.5 h-5">
                                                            <Star className="w-3 h-3 mr-0.5 fill-current" />
                                                            {BADGE_LABELS.top[langKey]}
                                                        </Badge>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-3 group-hover:scale-110 transition-transform duration-300">
                                                <span className="text-2xl">{course.icon}</span>
                                            </div>
                                            <CardTitle className="text-lg font-bold leading-tight group-hover:text-primary transition-colors">
                                                {title}
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent className="flex-grow space-y-3">
                                            <CardDescription className="text-sm line-clamp-3 leading-relaxed">
                                                {description}
                                            </CardDescription>

                                            {/* Topics */}
                                            {course.topics && course.topics.length > 0 && (
                                                <div className="flex flex-wrap gap-1">
                                                    {course.topics.slice(0, 3).map((topic, i) => (
                                                        <span key={i} className="text-[10px] px-1.5 py-0.5 bg-muted rounded text-muted-foreground">
                                                            {topic}
                                                        </span>
                                                    ))}
                                                </div>
                                            )}

                                            {/* Metadata */}
                                            <div className="flex items-center gap-2 text-xs">
                                                <span className={`px-2 py-0.5 rounded-full ${DIFFICULTY_COLORS[course.difficulty] || DIFFICULTY_COLORS.beginner}`}>
                                                    {DIFFICULTY_LABELS[course.difficulty]?.[langKey] || 'Base'}
                                                </span>
                                                {course.price && (
                                                    <span className="text-primary font-semibold">{course.price}</span>
                                                )}
                                            </div>
                                        </CardContent>
                                        <CardFooter className="pt-2">
                                            <Button
                                                variant="outline"
                                                className="w-full justify-between group-hover:border-primary/50 group-hover:text-primary transition-all duration-300"
                                                asChild
                                            >
                                                <a href={course.purchase_url} target="_blank" rel="noopener noreferrer">
                                                    <span>{t.courses.exploreModule}</span>
                                                    <ExternalLink className="w-4 h-4 opacity-50 group-hover:opacity-100 transition-opacity" />
                                                </a>
                                            </Button>
                                        </CardFooter>
                                    </Card>
                                </motion.div>
                            );
                        })}

                        {/* Call to Action Card */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: courses.length * 0.1 }}
                            className="md:col-span-2 lg:col-span-1 xl:col-span-1"
                        >
                            <Card className="h-full bg-gradient-to-br from-primary/20 to-primary/5 border-primary/30 flex flex-col justify-center items-center text-center p-6 space-y-4 hover:shadow-[0_0_30px_rgba(212,175,55,0.1)] transition-all duration-300 cursor-pointer group">
                                <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-500">
                                    <Rocket className="w-8 h-8" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-foreground">{t.courses.emptyTitle}</h3>
                                    <p className="text-sm text-muted-foreground mt-2">{t.courses.emptySubtitle}</p>
                                </div>
                                <Button size="lg" className="w-full shadow-lg shadow-primary/20 hover:shadow-primary/40 transition-all font-bold">
                                    {t.courses.cta}
                                </Button>
                            </Card>
                        </motion.div>
                    </div>
                ) : (
                    /* Coming Soon State */

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className="relative z-10 max-w-2xl mx-auto text-center py-12 px-6 rounded-3xl border border-primary/20 bg-background/50 backdrop-blur-xl shadow-2xl shadow-primary/10"
                    >
                        <div className="w-20 h-20 mx-auto bg-primary/10 rounded-full flex items-center justify-center mb-6">
                            <Rocket className="w-10 h-10 text-primary animate-bounce" />
                        </div>
                        <h3 className="text-2xl font-bold text-foreground mb-3">{t.courses.comingSoonTitle}</h3>
                        <p className="text-muted-foreground mb-8 text-lg">
                            {t.courses.comingSoonSubtitle}
                        </p>
                        <NewsletterModal source="academy_coming_soon">
                            <Button size="lg" className="shadow-lg shadow-primary/20 font-bold bg-primary text-primary-foreground hover:bg-primary/90">
                                <Sparkles className="w-4 h-4 mr-2" />
                                {t.courses.comingSoonCta}
                            </Button>
                        </NewsletterModal>
                    </motion.div>
                )}
            </div>
        </section>
    );
}
