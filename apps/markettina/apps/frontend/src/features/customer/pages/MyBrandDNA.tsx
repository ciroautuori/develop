/**
 * MyBrandDNA - Customer's Brand DNA configuration
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Palette,
  MessageSquare,
  Target,
  Sparkles,
  Edit2,
  Save,
  RefreshCw,
} from 'lucide-react';
import { cn } from '../../../shared/lib/utils';

export function MyBrandDNA() {
  const [editing, setEditing] = useState(false);

  // Mock brand DNA data - replace with real API
  const brandDNA = {
    companyName: 'Azienda Srl',
    industry: 'E-commerce',
    toneOfVoice: 'Professionale ma accessibile',
    targetAudience: 'PMI e professionisti 25-55 anni',
    brandValues: ['Innovazione', 'Affidabilità', 'Trasparenza'],
    keywords: ['qualità', 'made in italy', 'sostenibile', 'premium'],
    colorPalette: ['#D4AF37', '#0A0A0A', '#FFFFFF'],
    lastUpdated: '2024-12-01',
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground flex items-center gap-2">
            <Brain className="h-7 w-7 text-primary" />
            Brand DNA
          </h1>
          <p className="text-muted-foreground mt-1">
            Il profilo AI del tuo brand
          </p>
        </div>

        <button
          onClick={() => setEditing(!editing)}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-colors',
            editing
              ? 'bg-green-500 text-white hover:bg-green-600'
              : 'bg-muted text-foreground hover:bg-muted/80'
          )}
        >
          {editing ? <Save className="h-4 w-4" /> : <Edit2 className="h-4 w-4" />}
          {editing ? 'Salva' : 'Modifica'}
        </button>
      </motion.div>

      {/* DNA Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Tone of Voice */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card border border-border rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-xl bg-purple-500/10">
              <MessageSquare className="h-5 w-5 text-purple-500" />
            </div>
            <h3 className="font-semibold text-foreground">Tone of Voice</h3>
          </div>
          <p className="text-muted-foreground">{brandDNA.toneOfVoice}</p>
        </motion.div>

        {/* Target Audience */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-card border border-border rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-xl bg-blue-500/10">
              <Target className="h-5 w-5 text-blue-500" />
            </div>
            <h3 className="font-semibold text-foreground">Target Audience</h3>
          </div>
          <p className="text-muted-foreground">{brandDNA.targetAudience}</p>
        </motion.div>

        {/* Brand Values */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-card border border-border rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-xl bg-amber-500/10">
              <Sparkles className="h-5 w-5 text-amber-500" />
            </div>
            <h3 className="font-semibold text-foreground">Valori del Brand</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {brandDNA.brandValues.map((value) => (
              <span key={value} className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm">
                {value}
              </span>
            ))}
          </div>
        </motion.div>

        {/* Keywords */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-card border border-border rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-xl bg-green-500/10">
              <Brain className="h-5 w-5 text-green-500" />
            </div>
            <h3 className="font-semibold text-foreground">Parole Chiave</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {brandDNA.keywords.map((keyword) => (
              <span key={keyword} className="px-3 py-1 rounded-full bg-muted text-muted-foreground text-sm">
                #{keyword}
              </span>
            ))}
          </div>
        </motion.div>

        {/* Color Palette */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-card border border-border rounded-2xl p-6 md:col-span-2"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-xl bg-pink-500/10">
              <Palette className="h-5 w-5 text-pink-500" />
            </div>
            <h3 className="font-semibold text-foreground">Palette Colori</h3>
          </div>
          <div className="flex gap-3">
            {brandDNA.colorPalette.map((color, index) => (
              <div key={index} className="text-center">
                <div
                  className="w-16 h-16 rounded-xl border border-border shadow-sm"
                  style={{ backgroundColor: color }}
                />
                <span className="text-xs text-muted-foreground mt-1 block">{color}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Regenerate DNA */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-2xl p-6 text-center"
      >
        <Brain className="h-12 w-12 mx-auto text-purple-500 mb-4" />
        <h3 className="font-semibold text-foreground mb-2">Rigenera Brand DNA</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Analizza nuovamente i tuoi social per aggiornare il profilo AI
        </p>
        <button className="inline-flex items-center gap-2 px-6 py-3 bg-purple-500 text-white rounded-xl font-medium hover:bg-purple-600 transition-colors">
          <RefreshCw className="h-4 w-4" />
          Rigenera DNA
        </button>
      </motion.div>
    </div>
  );
}
