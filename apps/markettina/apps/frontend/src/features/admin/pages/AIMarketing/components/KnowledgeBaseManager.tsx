/**
 * Knowledge Base Manager - Gestione documenti RAG
 *
 * Funzionalità:
 * - Upload documenti (.md, .txt, .json)
 * - Lista documenti indicizzati
 * - Eliminazione documenti
 * - Ricerca semantica test
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText,
  Upload,
  Trash2,
  Search,
  RefreshCw,
  Database,
  CheckCircle,
  AlertCircle,
  Loader2,
  Plus,
  X,
  File,
  Tag
} from 'lucide-react';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';

// Types
interface RAGDocument {
  id: string;
  filename: string;
  chunks_count: number;
  uploaded_at: string;
  user_id: number;
  metadata: {
    category?: string;
    tags?: string[];
    file_type?: string;
  };
}

interface SearchResult {
  text: string;
  similarity: number;
  source: string;
}

// API Service
const RAGApiService = {
  baseUrl: '/api/v1/rag',

  getHeaders(): HeadersInit {
    return {
      'Authorization': `Bearer ${localStorage.getItem('admin_token') || 'dev-api-key-change-in-production'}`,
    };
  },

  async listDocuments(): Promise<RAGDocument[]> {
    const res = await fetch(`${this.baseUrl}/documents`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async uploadDocument(file: File, category: string, tags: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    formData.append('tags', tags);

    const res = await fetch(`${this.baseUrl}/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('admin_token') || 'dev-api-key-change-in-production'}`,
      },
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload document');
    return res.json();
  },

  async deleteDocument(docId: string): Promise<void> {
    const res = await fetch(`${this.baseUrl}/documents/${docId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  async search(query: string): Promise<SearchResult[]> {
    const res = await fetch(`${this.baseUrl}/search`, {
      method: 'POST',
      headers: {
        ...this.getHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, k: 5, threshold: 0.5 }),
    });
    if (!res.ok) throw new Error('Search failed');
    const data = await res.json();
    return data.results;
  },
};

// Categories
const DOCUMENT_CATEGORIES = [
  { value: 'brand', label: 'Brand & Identità' },
  { value: 'services', label: 'Servizi' },
  { value: 'faq', label: 'FAQ & Supporto' },
  { value: 'case_studies', label: 'Case Studies' },
  { value: 'products', label: 'Prodotti' },
  { value: 'general', label: 'Generale' },
];

export function KnowledgeBaseManager() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // State
  const [documents, setDocuments] = useState<RAGDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Upload form state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadCategory, setUploadCategory] = useState('general');
  const [uploadTags, setUploadTags] = useState('');

  // Styles
  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-lg';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark
    ? 'bg-[#1A1A1A] border-gray-600 text-white'
    : 'bg-white border-gray-300 text-gray-900';

  // Load documents
  const loadDocuments = useCallback(async () => {
    setIsLoading(true);
    try {
      const docs = await RAGApiService.listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
      // Show empty state, not error - API might just be starting
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  // Upload handler
  const handleUpload = async () => {
    if (!uploadFile) {
      toast.error('Seleziona un file da caricare');
      return;
    }

    setIsUploading(true);
    try {
      await RAGApiService.uploadDocument(uploadFile, uploadCategory, uploadTags);
      toast.success(`${uploadFile.name} caricato e indicizzato!`);
      setShowUploadModal(false);
      setUploadFile(null);
      setUploadTags('');
      await loadDocuments();
    } catch (error) {
      toast.error('Errore durante il caricamento');
    } finally {
      setIsUploading(false);
    }
  };

  // Delete handler
  const handleDelete = async (docId: string, filename: string) => {
    if (!confirm(`Eliminare "${filename}"?`)) return;

    try {
      await RAGApiService.deleteDocument(docId);
      toast.success('Documento eliminato');
      await loadDocuments();
    } catch (error) {
      toast.error('Errore durante l\'eliminazione');
    }
  };

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const results = await RAGApiService.search(searchQuery);
      setSearchResults(results);
      if (results.length === 0) {
        toast.info('Nessun risultato trovato');
      }
    } catch (error) {
      toast.error('Errore durante la ricerca');
    } finally {
      setIsSearching(false);
    }
  };

  // Format date
  const formatDate = (isoDate: string) => {
    return new Date(isoDate).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`${cardBg} rounded-xl p-6`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-purple-500/20">
              <Database className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h2 className={`text-xl font-bold ${textPrimary}`}>
                Knowledge Base
              </h2>
              <p className={textSecondary}>
                Gestisci i documenti per la generazione AI
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={loadDocuments}
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Aggiorna
            </Button>
            <Button
              onClick={() => setShowUploadModal(true)}
              className="bg-purple-600 hover:bg-purple-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Carica Documento
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>
              {documents.length}
            </div>
            <div className={textSecondary}>Documenti</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>
              {documents.reduce((sum, d) => sum + d.chunks_count, 0)}
            </div>
            <div className={textSecondary}>Chunks Totali</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold text-green-400`}>
              <CheckCircle className="w-6 h-6 inline" />
            </div>
            <div className={textSecondary}>RAG Attivo</div>
          </div>
        </div>
      </div>

      {/* Search Section */}
      <div className={`${cardBg} rounded-xl p-6`}>
        <h3 className={`font-semibold mb-4 ${textPrimary}`}>
          🔍 Test Ricerca Semantica
        </h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Cerca nella knowledge base..."
            className={`flex-1 px-4 py-2 rounded-lg border ${inputBg}`}
          />
          <Button
            onClick={handleSearch}
            disabled={isSearching || !searchQuery.trim()}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isSearching ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
          </Button>
        </div>

        {/* Search Results */}
        <AnimatePresence>
          {searchResults.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 space-y-3"
            >
              {searchResults.map((result, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className={`text-sm ${textSecondary}`}>
                      📄 {result.source || 'Unknown'}
                    </span>
                    <span className="text-xs text-green-400">
                      {(result.similarity * 100).toFixed(1)}% match
                    </span>
                  </div>
                  <p className={`text-sm ${textPrimary}`}>
                    {result.text.slice(0, 300)}
                    {result.text.length > 300 && '...'}
                  </p>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Documents List */}
      <div className={`${cardBg} rounded-xl p-6`}>
        <h3 className={`font-semibold mb-4 ${textPrimary}`}>
          📚 Documenti Indicizzati
        </h3>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
          </div>
        ) : documents.length === 0 ? (
          <div className={`text-center py-8 ${textSecondary}`}>
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Nessun documento indicizzato</p>
            <p className="text-sm mt-1">
              Carica documenti per arricchire la generazione AI
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-4 rounded-lg flex items-center justify-between ${
                  isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100'
                } transition-colors`}
              >
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-lg bg-purple-500/20">
                    <File className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <div className={`font-medium ${textPrimary}`}>
                      {doc.filename}
                    </div>
                    <div className={`text-sm ${textSecondary}`}>
                      {doc.chunks_count} chunks • {formatDate(doc.uploaded_at)}
                    </div>
                    {doc.metadata.tags && doc.metadata.tags.length > 0 && (
                      <div className="flex gap-1 mt-1">
                        {doc.metadata.tags.map((tag, i) => (
                          <span
                            key={i}
                            className="px-2 py-0.5 text-xs rounded-full bg-purple-500/20 text-purple-300"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(doc.id, doc.filename)}
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/20"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
            onClick={() => setShowUploadModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className={`${cardBg} rounded-2xl p-6 w-full max-w-md`}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className={`text-lg font-bold ${textPrimary}`}>
                  Carica Documento
                </h3>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className={textSecondary}
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                {/* File Input */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                    File (.md, .txt, .json)
                  </label>
                  <input
                    type="file"
                    accept=".md,.txt,.json,.csv,.html"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className={`w-full px-4 py-2 rounded-lg border ${inputBg}`}
                  />
                  {uploadFile && (
                    <p className={`text-sm mt-1 ${textSecondary}`}>
                      Selezionato: {uploadFile.name}
                    </p>
                  )}
                </div>

                {/* Category */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                    Categoria
                  </label>
                  <select
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value)}
                    className={`w-full px-4 py-2 rounded-lg border ${inputBg}`}
                  >
                    {DOCUMENT_CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Tags */}
                <div>
                  <label className={`block text-sm font-medium mb-2 ${textSecondary}`}>
                    Tags (separati da virgola)
                  </label>
                  <input
                    type="text"
                    value={uploadTags}
                    onChange={(e) => setUploadTags(e.target.value)}
                    placeholder="marketing, brand, servizi"
                    className={`w-full px-4 py-2 rounded-lg border ${inputBg}`}
                  />
                </div>

                {/* Submit */}
                <Button
                  onClick={handleUpload}
                  disabled={!uploadFile || isUploading}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Caricamento...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Carica e Indicizza
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
}

export default KnowledgeBaseManager;
