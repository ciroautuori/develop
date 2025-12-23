import React, { useState, useEffect, useCallback } from 'react';
import { Search, Sparkles, Target, Brain, Loader2, Info } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/utils/cn';
import { aiService } from '@/services/api';
import type { Bando } from '@/types/api';

interface SemanticSearchProps {
  onResults: (results: SemanticSearchResult[]) => void;
  className?: string;
}

interface SemanticSearchResult {
  bando: Bando;
  similarity_score: number;
  match_explanation: string;
}

interface ProfileForm {
  organization_type: string;
  sectors: string[];
  target_groups: string[];
  keywords: string[];
  geographical_area: string;
  max_amount?: number;
}

const ORGANIZATION_TYPES = [
  { value: 'aps', label: 'APS - Associazione di Promozione Sociale' },
  { value: 'odv', label: 'ODV - Organizzazione di Volontariato' },
  { value: 'cooperativa', label: 'Cooperativa Sociale' },
  { value: 'ong', label: 'ONG - Organizzazione Non Governativa' },
  { value: 'fondazione', label: 'Fondazione' },
  { value: 'altro', label: 'Altro' }
];

const SECTORS = [
  'sociale', 'cultura', 'ambiente', 'sport', 'formazione', 
  'sanitario', 'ricerca', 'innovazione', 'digitale', 'turismo'
];

const TARGET_GROUPS = [
  'giovani', 'anziani', 'disabili', 'immigrati', 'donne', 
  'minori', 'famiglie', 'comunità', 'studenti', 'lavoratori'
];

export const SemanticSearch: React.FC<SemanticSearchProps> = ({ onResults, className }) => {
  const [activeTab, setActiveTab] = useState('search');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  
  // Profile form state
  const [profile, setProfile] = useState<ProfileForm>({
    organization_type: '',
    sectors: [],
    target_groups: [],
    keywords: [],
    geographical_area: 'Campania',
    max_amount: undefined
  });

  // Carica suggerimenti intelligenti
  useEffect(() => {
    const loadSuggestions = async () => {
      try {
        const response = await aiService.getIntelligentSuggestions({
          search_history: searchHistory,
          limit: 8
        });
        setSuggestions(response);
      } catch (error) {
        console.error('Errore caricamento suggerimenti:', error);
      }
    };

    loadSuggestions();
  }, [searchHistory]);

  const handleSemanticSearch = async (query: string) => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const results = await aiService.semanticSearch({
        query: query.trim(),
        limit: 10,
        threshold: 0.3
      });

      onResults(results);
      
      // Aggiorna storico
      const newHistory = [query, ...searchHistory.filter(h => h !== query)].slice(0, 10);
      setSearchHistory(newHistory);
      
    } catch (error) {
      console.error('Errore ricerca semantica:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileMatch = async () => {
    if (!profile.organization_type) return;

    setLoading(true);
    try {
      const results = await aiService.matchProfile({
        ...profile,
        keywords: profile.keywords.filter(k => k.trim()),
        limit: 10
      });

      onResults(results);
    } catch (error) {
      console.error('Errore match profilo:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    handleSemanticSearch(suggestion);
  };

  const addKeyword = (keyword: string) => {
    if (keyword.trim() && !profile.keywords.includes(keyword.trim())) {
      setProfile(prev => ({
        ...prev,
        keywords: [...prev.keywords, keyword.trim()]
      }));
    }
  };

  const removeKeyword = (keyword: string) => {
    setProfile(prev => ({
      ...prev,
      keywords: prev.keywords.filter(k => k !== keyword)
    }));
  };

  const toggleArrayItem = (array: string[], item: string): string[] => {
    return array.includes(item) 
      ? array.filter(i => i !== item)
      : [...array, item];
  };

  return (
    <div className={cn("w-full", className)}>
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="search" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            Ricerca AI
          </TabsTrigger>
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Match Profilo
          </TabsTrigger>
        </TabsList>

        <TabsContent value="search" className="space-y-4">
          {/* Ricerca Semantica */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="h-5 w-5 text-blue-600" />
              <h3 className="font-semibold">Ricerca Semantica AI</h3>
              <Info className="h-4 w-4 text-gray-500" title="Trova bandi per significato, non solo parole chiave" />
            </div>

            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Descrivi il tipo di progetto o settore che ti interessa..."
                  onKeyPress={(e) => e.key === 'Enter' && handleSemanticSearch(searchQuery)}
                  className="flex-1"
                />
                <Button 
                  onClick={() => handleSemanticSearch(searchQuery)}
                  disabled={loading || !searchQuery.trim()}
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                </Button>
              </div>

              {/* Suggerimenti Intelligenti */}
              {suggestions.length > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-2">💡 Suggerimenti intelligenti:</p>
                  <div className="flex flex-wrap gap-2">
                    {suggestions.map((suggestion, index) => (
                      <Badge 
                        key={index}
                        variant="outline" 
                        className="cursor-pointer hover:bg-blue-50 hover:border-blue-300"
                        onClick={() => handleSuggestionClick(suggestion)}
                      >
                        {suggestion}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Storico Ricerche */}
              {searchHistory.length > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-2">🕒 Ricerche recenti:</p>
                  <div className="flex flex-wrap gap-2">
                    {searchHistory.slice(0, 5).map((query, index) => (
                      <Badge 
                        key={index}
                        variant="secondary" 
                        className="cursor-pointer hover:bg-gray-200"
                        onClick={() => handleSuggestionClick(query)}
                      >
                        {query}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="profile" className="space-y-4">
          {/* Profile Matching */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Target className="h-5 w-5 text-green-600" />
              <h3 className="font-semibold">Match Automatico Profilo</h3>
              <Info className="h-4 w-4 text-gray-500" title="L'AI trova bandi perfetti per la tua organizzazione" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Tipo Organizzazione */}
              <div>
                <label className="text-sm font-medium mb-2 block">Tipo Organizzazione *</label>
                <Select value={profile.organization_type} onValueChange={(value) => 
                  setProfile(prev => ({ ...prev, organization_type: value }))
                }>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleziona tipo..." />
                  </SelectTrigger>
                  <SelectContent>
                    {ORGANIZATION_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Area Geografica */}
              <div>
                <label className="text-sm font-medium mb-2 block">Area Geografica</label>
                <Input
                  value={profile.geographical_area}
                  onChange={(e) => setProfile(prev => ({ ...prev, geographical_area: e.target.value }))}
                  placeholder="es. Salerno, Campania, Italia"
                />
              </div>

              {/* Importo Massimo */}
              <div>
                <label className="text-sm font-medium mb-2 block">Importo Massimo (€)</label>
                <Input
                  type="number"
                  value={profile.max_amount || ''}
                  onChange={(e) => setProfile(prev => ({ ...prev, max_amount: e.target.value ? parseInt(e.target.value) : undefined }))}
                  placeholder="es. 50000"
                />
              </div>
            </div>

            {/* Settori */}
            <div className="mt-4">
              <label className="text-sm font-medium mb-2 block">Settori di Interesse</label>
              <div className="flex flex-wrap gap-2">
                {SECTORS.map(sector => (
                  <Badge
                    key={sector}
                    variant={profile.sectors.includes(sector) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => setProfile(prev => ({
                      ...prev,
                      sectors: toggleArrayItem(prev.sectors, sector)
                    }))}
                  >
                    {sector}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Target Groups */}
            <div className="mt-4">
              <label className="text-sm font-medium mb-2 block">Gruppi Target</label>
              <div className="flex flex-wrap gap-2">
                {TARGET_GROUPS.map(group => (
                  <Badge
                    key={group}
                    variant={profile.target_groups.includes(group) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => setProfile(prev => ({
                      ...prev,
                      target_groups: toggleArrayItem(prev.target_groups, group)
                    }))}
                  >
                    {group}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Keywords Personalizzate */}
            <div className="mt-4">
              <label className="text-sm font-medium mb-2 block">Keywords Personalizzate</label>
              <div className="flex gap-2 mb-2">
                <Input
                  placeholder="Aggiungi keyword..."
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addKeyword(e.currentTarget.value);
                      e.currentTarget.value = '';
                    }
                  }}
                />
                <Button 
                  size="sm"
                  onClick={() => {
                    const input = document.querySelector('input[placeholder="Aggiungi keyword..."]') as HTMLInputElement;
                    if (input?.value) {
                      addKeyword(input.value);
                      input.value = '';
                    }
                  }}
                >
                  +
                </Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.keywords.map(keyword => (
                  <Badge 
                    key={keyword}
                    variant="secondary"
                    className="cursor-pointer"
                    onClick={() => removeKeyword(keyword)}
                  >
                    {keyword} ×
                  </Badge>
                ))}
              </div>
            </div>

            {/* Bottone Match */}
            <Button
              onClick={handleProfileMatch}
              disabled={loading || !profile.organization_type}
              className="w-full mt-6"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Analizzando profilo...
                </>
              ) : (
                <>
                  <Target className="h-4 w-4 mr-2" />
                  Trova Bandi Perfetti per Me
                </>
              )}
            </Button>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
