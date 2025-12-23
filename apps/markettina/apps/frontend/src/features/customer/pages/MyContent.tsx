/**
 * MyContent - Customer's content history and management
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import {
  FileText,
  Image,
  Video,
  Calendar,
  Filter,
  Search,
  Download,
  Eye,
  Trash2,
  MoreVertical,
  Clock,
  Check,
  X,
} from 'lucide-react';
import { cn } from '../../../shared/lib/utils';

interface ContentItem {
  id: number;
  type: 'post' | 'image' | 'video' | 'blog';
  title: string;
  platform?: string;
  status: 'draft' | 'scheduled' | 'published';
  createdAt: string;
  scheduledFor?: string;
  tokens: number;
}

export function MyContent() {
  const [filter, setFilter] = useState<'all' | 'post' | 'image' | 'video' | 'blog'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data - replace with real API
  const content: ContentItem[] = [
    { id: 1, type: 'post', title: 'Post Instagram - Nuovo prodotto', platform: 'Instagram', status: 'published', createdAt: '2024-12-10', tokens: 15 },
    { id: 2, type: 'image', title: 'Banner promozionale Q4', status: 'published', createdAt: '2024-12-09', tokens: 40 },
    { id: 3, type: 'video', title: 'Story prodotto lancio', platform: 'Instagram', status: 'scheduled', createdAt: '2024-12-08', scheduledFor: '2024-12-15', tokens: 200 },
    { id: 4, type: 'post', title: 'Post LinkedIn - Case study', platform: 'LinkedIn', status: 'draft', createdAt: '2024-12-07', tokens: 15 },
    { id: 5, type: 'blog', title: 'Guida SEO 2025', status: 'published', createdAt: '2024-12-05', tokens: 40 },
  ];

  const filteredContent = content.filter(item => {
    const matchesFilter = filter === 'all' || item.type === filter;
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'post': return FileText;
      case 'image': return Image;
      case 'video': return Video;
      case 'blog': return FileText;
      default: return FileText;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return <span className="px-2 py-1 text-xs rounded-full bg-green-500/10 text-green-500 flex items-center gap-1"><Check className="h-3 w-3" /> Pubblicato</span>;
      case 'scheduled':
        return <span className="px-2 py-1 text-xs rounded-full bg-blue-500/10 text-blue-500 flex items-center gap-1"><Calendar className="h-3 w-3" /> Programmato</span>;
      case 'draft':
        return <span className="px-2 py-1 text-xs rounded-full bg-gray-500/10 text-gray-500 flex items-center gap-1"><Clock className="h-3 w-3" /> Bozza</span>;
      default:
        return null;
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl sm:text-3xl font-bold text-foreground">I Miei Contenuti</h1>
        <p className="text-muted-foreground mt-1">Tutti i contenuti generati con AI</p>
      </motion.div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Cerca contenuti..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-border bg-card text-foreground"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">
          {['all', 'post', 'image', 'video', 'blog'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f as any)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
                filter === f
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              )}
            >
              {f === 'all' ? 'Tutti' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Content List */}
      <div className="space-y-3">
        {filteredContent.map((item) => {
          const Icon = getTypeIcon(item.type);

          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-card border border-border rounded-xl p-4 flex items-center gap-4 hover:bg-muted/30 transition-colors"
            >
              <div className="p-2.5 rounded-xl bg-primary/10">
                <Icon className="h-5 w-5 text-primary" />
              </div>

              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground truncate">{item.title}</p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground mt-0.5">
                  {item.platform && <span>{item.platform}</span>}
                  <span>•</span>
                  <span>{new Date(item.createdAt).toLocaleDateString('it-IT')}</span>
                  <span>•</span>
                  <span>{item.tokens} token</span>
                </div>
              </div>

              {getStatusBadge(item.status)}

              <button className="p-2 rounded-lg hover:bg-muted transition-colors">
                <Eye className="h-4 w-4 text-muted-foreground" />
              </button>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
