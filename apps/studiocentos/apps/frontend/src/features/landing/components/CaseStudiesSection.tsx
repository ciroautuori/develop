/**
 * Case Studies Section Component - Progetti dettagliati con storytelling
 * DINAMICO - Dati dal database via API - IMMAGINI REALI
 */

import { motion } from 'framer-motion';
import type { Project } from '../types/landing.types';
import { useLanguage } from '../i18n';

interface CaseStudiesSectionProps {
  projects: Project[];
}

// Fallback emojis solo se non c'è immagine
const projectEmojis = ['💼', '🤖', '🛍️', '🚀', '💡', '🎯', '⚡', '🔥'];

export function CaseStudiesSection({ projects }: CaseStudiesSectionProps) {
  const { t } = useLanguage();

  if (!projects || projects.length === 0) {
    return null;
  }

  return (
    <section id="progetti" className="max-w-6xl mx-auto px-4 md:px-6 py-12 md:py-24">
      <h2 className="text-3xl md:text-5xl font-light mb-10 md:mb-20 text-center text-white light:text-gray-900">
        {t.projects.title} <span className="text-gold">{t.projects.titleHighlight}</span>
      </h2>

      {projects.map((project, index) => (
        <motion.div
          key={project.id}
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, delay: index * 0.1 }}
          className="mb-16 md:mb-32"
        >
          <div className={`grid md:grid-cols-2 gap-12 items-center ${index % 2 === 1 ? 'md:flex-row-reverse' : ''}`}>
            <div className={index % 2 === 1 ? 'order-1 md:order-2' : ''}>
              <div className="text-sm text-gold mb-3">{t.projects.caseStudy} #{index + 1} • {project.year}</div>
              <h3 className="text-3xl md:text-4xl font-light mb-6 text-white light:text-gray-900">{project.title}</h3>
              <p className="text-lg md:text-xl text-gray-400 light:text-gray-600 mb-8 leading-relaxed">
                {project.description}
              </p>

              <div className="space-y-4 mb-8">
                {Object.entries(project.metrics || {}).map(([key, value], i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="text-gold text-2xl">✓</div>
                    <div>
                      <div className="font-medium text-white light:text-gray-900">{key}</div>
                      <div className="text-sm text-gray-400 light:text-gray-600">{value}</div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex gap-3 mb-6 flex-wrap">
                {project.technologies?.map((tech, i) => (
                  <span key={i} className="px-4 py-2 bg-white/5 light:bg-gray-200 rounded-full text-xs text-gray-300 light:text-gray-700">{tech}</span>
                ))}
              </div>

              {project.live_url && (
                <a href={project.live_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center text-gold hover:underline">
                  {t.projects.visitSite}
                </a>
              )}
            </div>

            {/* Immagine progetto - DINAMICA dal database */}
            <motion.div
              whileHover={{ scale: 1.05, rotate: 2 }}
              transition={{ duration: 0.3 }}
              className={`bg-gradient-to-br from-white/10 to-white/5 light:bg-gray-100 rounded-3xl overflow-hidden border border-white/10 light:border-gray-200 aspect-square flex items-center justify-center transition-colors duration-300 ${index % 2 === 1 ? 'order-2 md:order-1' : ''}`}
            >
              {project.thumbnail_url || (project.images && project.images.length > 0) ? (
                <img
                  src={project.thumbnail_url || project.images[0]}
                  alt={project.title}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              ) : (
                <div className="text-9xl p-12">{projectEmojis[index % projectEmojis.length]}</div>
              )}
            </motion.div>
          </div>
        </motion.div>
      ))}
    </section>
  );
}
