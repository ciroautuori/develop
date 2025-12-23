/**
 * Portfolio Section Component
 * CON ANIMAZIONI FRAMER MOTION
 */

import { motion } from 'framer-motion';
import { ProjectCard } from './ProjectCard';
import type { Project } from '../types/landing.types';

interface PortfolioSectionProps {
  projects: Project[];
}

export function PortfolioSection({ projects }: PortfolioSectionProps) {
  if (!projects || projects.length === 0) {
    return null;
  }

  return (
    <section id="portfolio" className="max-w-6xl mx-auto px-6 py-32">
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mb-20 text-center"
      >
        <h2 className="text-4xl font-light mb-4">
          Prodotti <span className="text-gold">Realizzati</span>
        </h2>
        <p className="text-gray-400">Esempi concreti del nostro lavoro</p>
      </motion.div>

      {/* Timeline Vertical */}
      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-gold via-white/20 to-transparent hidden md:block"></div>

        {projects.map((project, index) => (
          <ProjectCard key={project.id} project={project} index={index} />
        ))}
      </div>
    </section>
  );
}
