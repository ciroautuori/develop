import React from 'react';
import {
  SlidersHorizontal,
  Banknote,
  CalendarDays,
  CheckCircle2,
  X,
  Building2,
  Landmark,
  Globe2,
  Heart,
  Rocket,
  Sparkles,
  ChevronRight,
  Flag
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/utils/cn';

// ============================================================
// CONFIGURAZIONE SEZIONI E FILTRI SPECIFICI
// ============================================================

const SEZIONI = [
  {
    id: 'tutti',
    label: 'Tutti i Bandi',
    icon: Sparkles,
    color: 'from-gray-500 to-gray-600',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
    description: 'Visualizza tutti i bandi disponibili'
  },
  {
    id: 'terzo_settore',
    label: 'Terzo Settore',
    icon: Heart,
    color: 'from-rose-500 to-pink-600',
    bgColor: 'bg-rose-50',
    borderColor: 'border-rose-200',
    description: 'Bandi per APS, ODV, ETS, Volontariato'
  },
  {
    id: 'invitalia',
    label: 'Invitalia & Nazionali',
    icon: Rocket,
    color: 'from-blue-500 to-indigo-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    description: 'Resto al Sud, Smart&Start, ON, Nuove Imprese'
  },
  {
    id: 'pnrr',
    label: 'PNRR & Europei',
    icon: Globe2,
    color: 'from-emerald-500 to-teal-600',
    bgColor: 'bg-emerald-50',
    borderColor: 'border-emerald-200',
    description: 'Italia Domani, Fondi Strutturali, NextGenEU'
  },
  {
    id: 'regionali',
    label: 'Regionali Campania',
    icon: Flag,
    color: 'from-amber-500 to-orange-600',
    bgColor: 'bg-amber-50',
    borderColor: 'border-amber-200',
    description: 'Regione Campania, FSE, FESR, Sviluppo Campania'
  },
  {
    id: 'locali',
    label: 'Locali & Fondazioni',
    icon: Building2,
    color: 'from-purple-500 to-violet-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    description: 'Comuni, CSV, Fondazioni Comunitarie'
  },
];

// Filtri specifici per ogni sezione
const FILTRI_SEZIONE: Record<string, { categorie: Array<{ id: string, label: string }>, subFonti: Array<{ id: string, label: string }> }> = {
  tutti: {
    categorie: [
      { id: 'sociale', label: 'Sociale & Welfare' },
      { id: 'cultura', label: 'Arte & Cultura' },
      { id: 'ambiente', label: 'Ambiente' },
      { id: 'sport', label: 'Sport' },
      { id: 'istruzione', label: 'Educazione' },
      { id: 'digitale', label: 'Digitale' },
      { id: 'impresa', label: 'Impresa' },
    ],
    subFonti: []
  },
  terzo_settore: {
    categorie: [
      { id: 'aps', label: 'APS - Promozione Sociale' },
      { id: 'odv', label: 'ODV - Volontariato' },
      { id: 'ets', label: 'ETS Generici' },
      { id: 'cooperazione', label: 'Cooperazione Sociale' },
      { id: 'impresa_sociale', label: 'Impresa Sociale' },
    ],
    subFonti: [
      { id: 'ministero_lavoro', label: 'Ministero Lavoro' },
      { id: 'fondazione_sud', label: 'Fondazione Con il Sud' },
      { id: 'csvnet', label: 'CSVnet Italia' },
      { id: 'cinque_per_mille', label: '5x1000' },
    ]
  },
  invitalia: {
    categorie: [
      { id: 'startup', label: 'Startup & Innovazione' },
      { id: 'nuove_imprese', label: 'Nuove Imprese' },
      { id: 'giovani', label: 'Under 35' },
      { id: 'donne', label: 'Imprenditoria Femminile' },
      { id: 'mezzogiorno', label: 'Sud Italia' },
    ],
    subFonti: [
      { id: 'resto_al_sud', label: 'Resto al Sud' },
      { id: 'smart_start', label: 'Smart&Start' },
      { id: 'on_nuove_imprese', label: 'ON - Oltre Nuove Imprese' },
      { id: 'cultura_crea', label: 'Cultura Crea 2.0' },
      { id: 'turismo', label: 'Fondo Turismo' },
    ]
  },
  pnrr: {
    categorie: [
      { id: 'rigenerazione', label: 'Rigenerazione Urbana' },
      { id: 'inclusione', label: 'Inclusione Sociale' },
      { id: 'transizione_verde', label: 'Transizione Verde' },
      { id: 'digitale', label: 'Transizione Digitale' },
      { id: 'giovani', label: 'Politiche Giovanili' },
    ],
    subFonti: [
      { id: 'italia_domani', label: 'Italia Domani' },
      { id: 'agenzia_coesione', label: 'Agenzia Coesione' },
      { id: 'pon_metro', label: 'PON Metro Plus' },
      { id: 'fse_plus', label: 'FSE+' },
    ]
  },
  regionali: {
    categorie: [
      { id: 'sociale', label: 'Politiche Sociali' },
      { id: 'lavoro', label: 'Lavoro & Formazione' },
      { id: 'cultura', label: 'Cultura & Turismo' },
      { id: 'ambiente', label: 'Ambiente & Territorio' },
      { id: 'agricoltura', label: 'Agricoltura' },
    ],
    subFonti: [
      { id: 'fse_campania', label: 'FSE Campania' },
      { id: 'fesr_campania', label: 'FESR Campania' },
      { id: 'sviluppo_campania', label: 'Sviluppo Campania' },
      { id: 'csr_campania', label: 'CSR Campania' },
    ]
  },
  locali: {
    categorie: [
      { id: 'sociale', label: 'Servizi Sociali' },
      { id: 'cultura', label: 'Eventi Culturali' },
      { id: 'sport', label: 'Sport & Tempo Libero' },
      { id: 'ambiente', label: 'Verde Pubblico' },
    ],
    subFonti: [
      { id: 'comune_salerno', label: 'Comune di Salerno' },
      { id: 'csv_salerno', label: 'CSV Salerno' },
      { id: 'csv_napoli', label: 'CSV Napoli' },
      { id: 'fondazione_comunita', label: 'Fondazione Comunità' },
    ]
  },
};

// ============================================================
// INTERFACES
// ============================================================

interface FiltersState {
  sezione: string;
  categorie: string[];
  importoMin: number;
  importoMax: number;
  soloAttivi: boolean;
  scadenzaBreve: boolean;
  fonte: string[];
  subFonti: string[];
}

interface SmartBandoFiltersProps {
  filters: FiltersState;
  onChange: (newFilters: FiltersState) => void;
  bandoCount?: Record<string, number>; // Conteggio bandi per sezione
  className?: string;
}

// ============================================================
// COMPONENTE PRINCIPALE
// ============================================================

export const SmartBandoFilters: React.FC<SmartBandoFiltersProps> = ({
  filters,
  onChange,
  bandoCount = {},
  className
}) => {
  const currentSezione = SEZIONI.find(s => s.id === filters.sezione) || SEZIONI[0];
  const currentFiltri = FILTRI_SEZIONE[filters.sezione] || FILTRI_SEZIONE.tutti;

  const updateFilter = <K extends keyof FiltersState>(key: K, value: FiltersState[K]) => {
    onChange({ ...filters, [key]: value });
  };

  const toggleArrayFilter = (key: 'categorie' | 'fonte' | 'subFonti', value: string) => {
    const current = filters[key];
    const next = current.includes(value)
      ? current.filter(item => item !== value)
      : [...current, value];
    updateFilter(key, next);
  };

  const handleSezioneChange = (sezioneId: string) => {
    onChange({
      ...filters,
      sezione: sezioneId,
      categorie: [],
      subFonti: [],
      fonte: sezioneId === 'tutti' ? [] : [sezioneId]
    });
  };

  const resetFilters = () => {
    onChange({
      sezione: 'tutti',
      categorie: [],
      importoMin: 0,
      importoMax: 1000000,
      soloAttivi: true,
      scadenzaBreve: false,
      fonte: [],
      subFonti: []
    });
  };

  const activeFiltersCount =
    filters.categorie.length +
    filters.subFonti.length +
    (filters.sezione !== 'tutti' ? 1 : 0) +
    (!filters.soloAttivi ? 1 : 0) +
    (filters.scadenzaBreve ? 1 : 0) +
    (filters.importoMin > 0 ? 1 : 0);

  return (
    <div className={cn('bg-white rounded-xl border border-gray-100 shadow-lg h-fit overflow-hidden', className)}>

      {/* HEADER */}
      <div className="p-4 bg-gradient-to-r from-iss-bordeaux-600 to-iss-bordeaux-700 text-white">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-lg flex items-center gap-2">
            <SlidersHorizontal className="w-5 h-5" /> Filtra Bandi
          </h3>
          {activeFiltersCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-white/80 hover:text-white hover:bg-white/20"
              onClick={resetFilters}
            >
              <X className="w-3 h-3 mr-1" /> Reset ({activeFiltersCount})
            </Button>
          )}
        </div>
        <p className="text-white/70 text-xs mt-1">Seleziona una sezione per filtri specifici</p>
      </div>

      <ScrollArea className="h-[calc(100vh-220px)]">
        <div className="p-4 space-y-5">

          {/* ============================================================ */}
          {/* SEZIONI PRINCIPALI - Card cliccabili */}
          {/* ============================================================ */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">
              Sezioni
            </h4>
            <div className="grid gap-2">
              {SEZIONI.map((sezione) => {
                const Icon = sezione.icon;
                const isActive = filters.sezione === sezione.id;
                const count = bandoCount[sezione.id] || 0;

                return (
                  <button
                    key={sezione.id}
                    onClick={() => handleSezioneChange(sezione.id)}
                    className={cn(
                      'w-full text-left p-3 rounded-lg border-2 transition-all duration-200',
                      'hover:shadow-md hover:scale-[1.02]',
                      isActive
                        ? `${sezione.bgColor} ${sezione.borderColor} shadow-md`
                        : 'bg-white border-gray-100 hover:border-gray-200'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          'w-10 h-10 rounded-lg flex items-center justify-center',
                          `bg-gradient-to-br ${sezione.color} text-white shadow-sm`
                        )}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div>
                          <p className={cn(
                            'font-semibold text-sm',
                            isActive ? 'text-gray-900' : 'text-gray-700'
                          )}>
                            {sezione.label}
                          </p>
                          <p className="text-xs text-gray-500 line-clamp-1">
                            {sezione.description}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {count > 0 && (
                          <Badge variant="secondary" className="text-xs font-bold">
                            {count}
                          </Badge>
                        )}
                        <ChevronRight className={cn(
                          'w-4 h-4 transition-transform text-gray-400',
                          isActive && 'rotate-90 text-gray-700'
                        )} />
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <Separator className="my-4" />

          {/* ============================================================ */}
          {/* FILTRI RAPIDI */}
          {/* ============================================================ */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400">
              Stato
            </h4>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="solo-attivi"
                checked={filters.soloAttivi}
                onCheckedChange={(c) => updateFilter('soloAttivi', c as boolean)}
              />
              <Label htmlFor="solo-attivi" className="text-sm font-medium flex items-center gap-2 cursor-pointer">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Solo Bandi Attivi
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="scadenza-breve"
                checked={filters.scadenzaBreve}
                onCheckedChange={(c) => updateFilter('scadenzaBreve', c as boolean)}
              />
              <Label htmlFor="scadenza-breve" className="text-sm font-medium flex items-center gap-2 cursor-pointer text-orange-700">
                <CalendarDays className="w-4 h-4" /> In Scadenza (7gg)
              </Label>
            </div>
          </div>

          <Separator className="my-4" />

          {/* ============================================================ */}
          {/* FILTRI SPECIFICI PER SEZIONE */}
          {/* ============================================================ */}
          {filters.sezione !== 'tutti' && (
            <>
              {/* Categorie specifiche della sezione */}
              {currentFiltri.categorie.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
                    <currentSezione.icon className="w-4 h-4" />
                    Tipologia {currentSezione.label}
                  </h4>
                  <div className="space-y-2">
                    {currentFiltri.categorie.map((cat) => (
                      <div key={cat.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`cat-${cat.id}`}
                          checked={filters.categorie.includes(cat.id)}
                          onCheckedChange={() => toggleArrayFilter('categorie', cat.id)}
                        />
                        <Label
                          htmlFor={`cat-${cat.id}`}
                          className="text-sm text-gray-600 font-normal cursor-pointer"
                        >
                          {cat.label}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Sub-fonti specifiche */}
              {currentFiltri.subFonti.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
                    <Landmark className="w-4 h-4" />
                    Ente Erogatore
                  </h4>
                  <div className="space-y-2">
                    {currentFiltri.subFonti.map((fonte) => (
                      <div key={fonte.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`fonte-${fonte.id}`}
                          checked={filters.subFonti.includes(fonte.id)}
                          onCheckedChange={() => toggleArrayFilter('subFonti', fonte.id)}
                        />
                        <Label
                          htmlFor={`fonte-${fonte.id}`}
                          className="text-sm text-gray-600 font-normal cursor-pointer"
                        >
                          {fonte.label}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <Separator className="my-4" />
            </>
          )}

          {/* ============================================================ */}
          {/* FILTRO IMPORTO */}
          {/* ============================================================ */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
              <Banknote className="w-4 h-4" /> Importo Minimo
            </h4>
            <div className="space-y-3">
              <input
                type="range"
                min="0"
                max="200000"
                step="5000"
                value={filters.importoMin}
                onChange={(e) => updateFilter('importoMin', parseInt(e.target.value))}
                className="w-full accent-iss-bordeaux-600 cursor-pointer h-2 rounded-lg"
              />
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">€0</span>
                <span className="text-iss-bordeaux-600 font-bold text-sm bg-iss-bordeaux-50 px-2 py-0.5 rounded">
                  €{filters.importoMin.toLocaleString()}+
                </span>
                <span className="text-gray-400">€200k+</span>
              </div>

              {/* Quick amount buttons */}
              <div className="grid grid-cols-3 gap-1 mt-2">
                {[5000, 15000, 50000].map((amount) => (
                  <Button
                    key={amount}
                    variant="outline"
                    size="sm"
                    className={cn(
                      'text-xs h-7',
                      filters.importoMin === amount && 'bg-iss-bordeaux-50 border-iss-bordeaux-300'
                    )}
                    onClick={() => updateFilter('importoMin', amount)}
                  >
                    €{(amount / 1000)}k
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* ============================================================ */}
          {/* CATEGORIE GENERALI (solo per "tutti") */}
          {/* ============================================================ */}
          {filters.sezione === 'tutti' && (
            <>
              <Separator className="my-4" />
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" /> Categoria
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {currentFiltri.categorie.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => toggleArrayFilter('categorie', cat.id)}
                      className={cn(
                        'p-2 rounded-lg border text-xs font-medium transition-all',
                        filters.categorie.includes(cat.id)
                          ? 'bg-iss-bordeaux-50 border-iss-bordeaux-300 text-iss-bordeaux-700'
                          : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                      )}
                    >
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

        </div>
      </ScrollArea>

      {/* FOOTER con conteggio */}
      {activeFiltersCount > 0 && (
        <div className="p-3 bg-gray-50 border-t border-gray-100">
          <div className="flex flex-wrap gap-1">
            {filters.sezione !== 'tutti' && (
              <Badge variant="secondary" className="text-xs">
                {currentSezione.label}
              </Badge>
            )}
            {filters.categorie.map(cat => (
              <Badge key={cat} variant="outline" className="text-xs">
                {cat}
              </Badge>
            ))}
            {filters.subFonti.map(fonte => (
              <Badge key={fonte} variant="outline" className="text-xs bg-blue-50">
                {fonte}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Export delle configurazioni per uso esterno
export { SEZIONI, FILTRI_SEZIONE };
export type { FiltersState };
