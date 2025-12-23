/**
 * Project Card Component
 * CON ANIMAZIONI FRAMER MOTION - IMMAGINI DINAMICHE
 */

import { motion } from 'framer-motion';
import type { Project } from '../types/landing.types';

interface ProjectCardProps {
  project: Project;
  index: number;
}

export function ProjectCard({ project, index }: ProjectCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -50 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.6, delay: index * 0.2 }}
      className="relative mb-20 md:ml-20 hover-lift"
    >
      <div className="absolute -left-[4.5rem] top-8 w-8 h-8 rounded-full bg-gold hidden md:flex items-center justify-center">
        <div className="w-3 h-3 rounded-full bg-black"></div>
      </div>
      <div className="bg-white/5 backdrop-blur rounded-2xl p-8 border border-white/10 hover:border-gold/50 transition">
        {/* Immagine progetto se presente */}
        {(project.thumbnail_url || (project.images && project.images.length > 0)) && (
          <div className="mb-6 -mx-8 -mt-8 overflow-hidden rounded-t-2xl">
            <img
              src={project.thumbnail_url || project.images[0]}
              alt={project.title}
              className="w-full h-48 object-cover"
              loading="lazy"
            />
          </div>
        )}

        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="text-sm text-gold mb-2">
              {project.year} • {project.category}
            </div>
            <h3 className="text-3xl font-light mb-2">{project.title}</h3>
            <p className="text-gray-400">{project.description}</p>
          </div>
          {project.live_url && (
            <a href={project.live_url} target="_blank" rel="noopener noreferrer" className="px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm transition">
              Live →
            </a>
          )}
        </div>

        <div className="flex flex-wrap gap-2 mb-6">
          {project.technologies?.map((tech, i) => (
            <span key={i} className="px-3 py-1 bg-white/5 rounded-full text-xs text-gray-400">
              {tech}
            </span>
          ))}
        </div>

        <div className="grid md:grid-cols-3 gap-4 text-sm">
          {Object.entries(project.metrics || {}).map(([key, value], i) => (
            <div key={i} className="bg-white/5 rounded-lg p-4">
              <div className="text-2xl font-light text-gold mb-1">{value}</div>
              <div className="text-gray-400">{key}</div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
