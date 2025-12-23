/**
 * A/B Testing Manager - Gestione test A/B marketing.
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FlaskConical, Play, Pause, Square, Trash2, RefreshCw, Plus,
  ChevronRight, CheckCircle, Clock, AlertCircle, Loader2, X,
  BarChart3, TrendingUp, Users, Percent, Award
} from 'lucide-react';
import { useTheme } from '../../../../../shared/contexts/ThemeContext';
import { Button } from '../../../../../shared/components/ui/button';
import { toast } from 'sonner';
import { ABTest } from '../../../types/ab-testing.types';

// API Service
const ABTestApi = {
  baseUrl: '/api/v1/marketing/ab-tests',

  getHeaders() {
    return {
      'Authorization': `Bearer ${localStorage.getItem('admin_token')}`,
      'Content-Type': 'application/json',
    };
  },

  async listTests(): Promise<ABTest[]> {
    const res = await fetch(this.baseUrl, { headers: this.getHeaders() });
    return res.ok ? res.json() : [];
  },

  async createQuickEmailTest(name: string, subjects: string[]): Promise<ABTest> {
    const res = await fetch(`${this.baseUrl}/quick/email-subject`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ name, subjects }),
    });
    if (!res.ok) throw new Error('Failed to create test');
    return res.json();
  },

  async createQuickCTATest(name: string, cta_texts: string[]): Promise<ABTest> {
    const res = await fetch(`${this.baseUrl}/quick/cta`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ name, cta_texts }),
    });
    if (!res.ok) throw new Error('Failed to create test');
    return res.json();
  },

  async startTest(id: string): Promise<void> {
    await fetch(`${this.baseUrl}/${id}/start`, { method: 'POST', headers: this.getHeaders() });
  },

  async pauseTest(id: string): Promise<void> {
    await fetch(`${this.baseUrl}/${id}/pause`, { method: 'POST', headers: this.getHeaders() });
  },

  async stopTest(id: string): Promise<ABTest> {
    const res = await fetch(`${this.baseUrl}/${id}/stop`, { method: 'POST', headers: this.getHeaders() });
    return res.json();
  },

  async deleteTest(id: string): Promise<void> {
    await fetch(`${this.baseUrl}/${id}`, { method: 'DELETE', headers: this.getHeaders() });
  },

  async getResults(id: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}/${id}/results`, { headers: this.getHeaders() });
    return res.json();
  },
};

// Status Badge
function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; icon: typeof Clock }> = {
    draft: { bg: 'bg-gray-500/20', text: 'text-gray-400', icon: Clock },
    running: { bg: 'bg-green-500/20', text: 'text-green-400', icon: Play },
    paused: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', icon: Pause },
    completed: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: CheckCircle },
  };
  const c = config[status] || config.draft;
  const Icon = c.icon;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${c.bg} ${c.text}`}>
      <Icon className="w-3 h-3" />
      {status}
    </span>
  );
}

export function ABTestingManager() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [tests, setTests] = useState<ABTest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedTest, setSelectedTest] = useState<ABTest | null>(null);

  // Create form state
  const [testType, setTestType] = useState<'email' | 'cta'>('email');
  const [testName, setTestName] = useState('');
  const [variants, setVariants] = useState(['', '']);

  const cardBg = isDark
    ? 'bg-gradient-to-br from-[#0A0A0A] to-[#1A1A1A] border border-white/10'
    : 'bg-white border border-gray-200 shadow-lg';
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-500';
  const inputBg = isDark ? 'bg-[#1A1A1A] border-gray-600 text-white' : 'bg-white border-gray-300 text-gray-900';

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await ABTestApi.listTests();
      setTests(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const handleCreate = async () => {
    if (!testName.trim() || variants.filter(v => v.trim()).length < 2) {
      toast.error('Inserisci nome e almeno 2 varianti');
      return;
    }
    try {
      const validVariants = variants.filter(v => v.trim());
      if (testType === 'email') {
        await ABTestApi.createQuickEmailTest(testName, validVariants);
      } else {
        await ABTestApi.createQuickCTATest(testName, validVariants);
      }
      toast.success('Test creato!');
      setShowCreate(false);
      setTestName('');
      setVariants(['', '']);
      await loadData();
    } catch (e) {
      toast.error('Errore nella creazione');
    }
  };

  const handleStart = async (test: ABTest) => {
    await ABTestApi.startTest(test.id);
    toast.success('Test avviato');
    await loadData();
  };

  const handlePause = async (test: ABTest) => {
    await ABTestApi.pauseTest(test.id);
    toast.success('Test in pausa');
    await loadData();
  };

  const handleStop = async (test: ABTest) => {
    await ABTestApi.stopTest(test.id);
    toast.success('Test completato');
    await loadData();
  };

  const handleDelete = async (test: ABTest) => {
    if (!confirm(`Eliminare "${test.name}"?`)) return;
    await ABTestApi.deleteTest(test.id);
    toast.success('Test eliminato');
    setSelectedTest(null);
    await loadData();
  };

  const addVariant = () => setVariants([...variants, '']);
  const updateVariant = (i: number, val: string) => {
    const newVars = [...variants];
    newVars[i] = val;
    setVariants(newVars);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className={`${cardBg} rounded-xl p-6`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-purple-500/20">
              <FlaskConical className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h2 className={`text-xl font-bold ${textPrimary}`}>A/B Testing</h2>
              <p className={textSecondary}>Testa varianti e ottimizza conversioni</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={loadData} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Aggiorna
            </Button>
            <Button onClick={() => setShowCreate(true)} className="bg-purple-600 hover:bg-purple-700">
              <Plus className="w-4 h-4 mr-2" />
              Nuovo Test
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className={`text-2xl font-bold ${textPrimary}`}>{tests.length}</div>
            <div className={textSecondary}>Totali</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-green-400">
              {tests.filter(t => t.status === 'running').length}
            </div>
            <div className={textSecondary}>In Corso</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-blue-400">
              {tests.filter(t => t.status === 'completed').length}
            </div>
            <div className={textSecondary}>Completati</div>
          </div>
          <div className={`p-4 rounded-lg ${isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
            <div className="text-2xl font-bold text-yellow-400">
              {tests.filter(t => t.result?.significant).length}
            </div>
            <div className={textSecondary}>Con Winner</div>
          </div>
        </div>
      </div>

      {/* Tests Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test List */}
        <div className={`${cardBg} rounded-xl p-6`}>
          <h3 className={`font-semibold mb-4 ${textPrimary}`}>🧪 I Tuoi Test</h3>

          {isLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
            </div>
          ) : tests.length === 0 ? (
            <div className={`text-center py-8 ${textSecondary}`}>
              <FlaskConical className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Nessun test A/B</p>
              <p className="text-sm">Crea il tuo primo test</p>
            </div>
          ) : (
            <div className="space-y-3">
              {tests.map(test => (
                <motion.div
                  key={test.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-4 rounded-lg cursor-pointer transition-colors ${selectedTest?.id === test.id
                    ? 'bg-purple-500/20 border border-purple-500/50'
                    : isDark ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  onClick={() => setSelectedTest(test)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className={`font-medium ${textPrimary}`}>{test.name}</div>
                      <div className={`text-sm ${textSecondary}`}>
                        {test.variants.length} varianti • {test.type?.replace('_', ' ')}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={test.status} />
                      <ChevronRight className={`w-4 h-4 ${textSecondary}`} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Test Detail */}
        <div className={`${cardBg} rounded-xl p-6`}>
          {selectedTest ? (
            <>
              <div className="flex items-center justify-between mb-4">
                <h3 className={`font-semibold ${textPrimary}`}>{selectedTest.name}</h3>
                <StatusBadge status={selectedTest.status} />
              </div>

              {/* Actions */}
              <div className="flex gap-2 mb-6">
                {selectedTest.status === 'draft' && (
                  <Button size="sm" onClick={() => handleStart(selectedTest)} className="bg-green-600 hover:bg-green-700">
                    <Play className="w-4 h-4 mr-1" /> Avvia
                  </Button>
                )}
                {selectedTest.status === 'running' && (
                  <>
                    <Button size="sm" onClick={() => handlePause(selectedTest)} className="bg-yellow-600 hover:bg-yellow-700">
                      <Pause className="w-4 h-4 mr-1" /> Pausa
                    </Button>
                    <Button size="sm" onClick={() => handleStop(selectedTest)} className="bg-blue-600 hover:bg-blue-700">
                      <Square className="w-4 h-4 mr-1" /> Termina
                    </Button>
                  </>
                )}
                {selectedTest.status === 'paused' && (
                  <Button size="sm" onClick={() => handleStart(selectedTest)} className="bg-green-600 hover:bg-green-700">
                    <Play className="w-4 h-4 mr-1" /> Riprendi
                  </Button>
                )}
                <Button size="sm" variant="ghost" onClick={() => handleDelete(selectedTest)} className="text-red-400">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>

              {/* Variants */}
              <div className="mb-6">
                <h4 className={`text-sm font-medium mb-3 ${textSecondary}`}>Varianti</h4>
                <div className="space-y-3">
                  {selectedTest.variants.map((v, i) => (
                    <div
                      key={v.id}
                      className={`p-3 rounded-lg ${v.is_winner
                        ? 'bg-green-500/20 border border-green-500/50'
                        : isDark ? 'bg-white/5' : 'bg-gray-50'
                        }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className={`font-medium ${textPrimary}`}>
                          {v.is_winner && <Award className="w-4 h-4 inline mr-1 text-yellow-400" />}
                          {v.name}
                        </span>
                        <span className={`text-sm ${textSecondary}`}>{v.traffic_percent}% traffico</span>
                      </div>
                      <p className={`text-sm mb-2 ${textSecondary}`}>"{v.content}"</p>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className={`p-2 rounded ${isDark ? 'bg-black/20' : 'bg-white'}`}>
                          <Users className="w-3 h-3 inline mr-1" />
                          {v.impressions} impressions
                        </div>
                        <div className={`p-2 rounded ${isDark ? 'bg-black/20' : 'bg-white'}`}>
                          <TrendingUp className="w-3 h-3 inline mr-1" />
                          {v.conversions} conversioni
                        </div>
                        <div className={`p-2 rounded ${isDark ? 'bg-black/20' : 'bg-white'}`}>
                          <Percent className="w-3 h-3 inline mr-1" />
                          {v.conversion_rate?.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Results */}
              {selectedTest.result && (
                <div className={`p-4 rounded-lg ${selectedTest.result.significant ? 'bg-green-500/10' : isDark ? 'bg-white/5' : 'bg-gray-50'}`}>
                  <h4 className={`text-sm font-medium mb-2 ${textSecondary}`}>Risultati</h4>
                  <div className="grid grid-cols-2 gap-2 mb-2 text-sm">
                    <div>Confidence: <span className={textPrimary}>{selectedTest.result.confidence?.toFixed(1)}%</span></div>
                    <div>Lift: <span className="text-green-400">+{selectedTest.result.lift?.toFixed(1)}%</span></div>
                  </div>
                  <p className={`text-sm ${selectedTest.result.significant ? 'text-green-400' : textSecondary}`}>
                    {selectedTest.result.recommendation}
                  </p>
                </div>
              )}
            </>
          ) : (
            <div className={`text-center py-8 ${textSecondary}`}>
              <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Seleziona un test</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Modal */}
      <AnimatePresence>
        {showCreate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreate(false)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className={`${cardBg} rounded-2xl p-6 w-full max-w-md`}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className={`text-lg font-bold ${textPrimary}`}>Nuovo Test A/B</h3>
                <button onClick={() => setShowCreate(false)}><X className="w-5 h-5" /></button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className={`block text-sm mb-2 ${textSecondary}`}>Tipo Test</label>
                  <div className="flex gap-2">
                    {(['email', 'cta'] as const).map(t => (
                      <button
                        key={t}
                        onClick={() => setTestType(t)}
                        className={`flex-1 py-2 rounded-lg ${testType === t ? 'bg-purple-500 text-white' : isDark ? 'bg-white/10 text-gray-300' : 'bg-gray-100'
                          }`}
                      >
                        {t === 'email' ? '📧 Email Subject' : '🔘 CTA Button'}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className={`block text-sm mb-2 ${textSecondary}`}>Nome Test</label>
                  <input
                    type="text"
                    value={testName}
                    onChange={e => setTestName(e.target.value)}
                    placeholder="es: Test Oggetto Newsletter"
                    className={`w-full px-3 py-2 rounded-lg border ${inputBg}`}
                  />
                </div>

                <div>
                  <label className={`block text-sm mb-2 ${textSecondary}`}>
                    Varianti ({testType === 'email' ? 'Oggetti Email' : 'Testi CTA'})
                  </label>
                  {variants.map((v, i) => (
                    <input
                      key={i}
                      type="text"
                      value={v}
                      onChange={e => updateVariant(i, e.target.value)}
                      placeholder={`Variante ${String.fromCharCode(65 + i)}`}
                      className={`w-full px-3 py-2 rounded-lg border mb-2 ${inputBg}`}
                    />
                  ))}
                  {variants.length < 5 && (
                    <button onClick={addVariant} className={`text-sm ${textSecondary} hover:text-purple-400`}>
                      + Aggiungi variante
                    </button>
                  )}
                </div>
              </div>

              <div className="flex gap-2 mt-6">
                <Button variant="outline" onClick={() => setShowCreate(false)} className="flex-1">
                  Annulla
                </Button>
                <Button onClick={handleCreate} className="flex-1 bg-purple-600 hover:bg-purple-700">
                  Crea Test
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default ABTestingManager;
