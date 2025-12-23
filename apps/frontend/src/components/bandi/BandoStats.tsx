import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  Clock,
  Euro,
  Building2,
  Target,
  AlertTriangle,
  Calendar,
  CheckCircle
} from 'lucide-react';
import { cn } from '@/utils/cn';

interface BandoStatsData {
  totali: number;
  attivi: number;
  scaduti: number;
  in_scadenza: number;
  importo_totale: number;
  importo_medio: number;
  nuovi_settimana: number;
  fonti: {
    [key: string]: number;
  };
  categorie: {
    [key: string]: number;
  };
  trend_mensile: {
    mese: string;
    count: number;
    importo: number;
  }[];
}

interface BandoStatsProps {
  stats: BandoStatsData;
  className?: string;
  compact?: boolean;
}

export const BandoStats: React.FC<BandoStatsProps> = ({
  stats,
  className,
  compact = false
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
      notation: amount > 1000000 ? 'compact' : 'standard',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('it-IT').format(num);
  };

  const getStatusColor = (status: 'attivi' | 'scaduti' | 'in_scadenza') => {
    switch (status) {
      case 'attivi': return 'text-green-600';
      case 'scaduti': return 'text-gray-500';
      case 'in_scadenza': return 'text-orange-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusBadgeVariant = (status: 'attivi' | 'scaduti' | 'in_scadenza') => {
    switch (status) {
      case 'attivi': return 'success' as const;
      case 'scaduti': return 'secondary' as const;
      case 'in_scadenza': return 'warning' as const;
      default: return 'secondary' as const;
    }
  };

  if (compact) {
    return (
      <Card className={cn("w-full", className)}>
        <CardContent className="p-3 sm:p-4">
          <div className="flex items-center justify-around sm:justify-start sm:gap-4">
            <div className="text-center px-2">
              <div className="text-xl sm:text-2xl font-bold text-iss-bordeaux-600">
                {formatNumber(stats.attivi)}
              </div>
              <div className="text-[10px] sm:text-xs text-gray-500">Attivi</div>
            </div>
            <div className="h-6 sm:h-8 w-px bg-gray-200"></div>
            <div className="text-center px-2">
              <div className="text-base sm:text-lg font-semibold text-orange-600">
                {formatNumber(stats.in_scadenza)}
              </div>
              <div className="text-[10px] sm:text-xs text-gray-500">Scadenza</div>
            </div>
            <div className="h-6 sm:h-8 w-px bg-gray-200"></div>
            <div className="text-center px-2">
              <div className="text-sm font-medium text-green-600">
                +{formatNumber(stats.nuovi_settimana)}
              </div>
              <div className="text-[10px] sm:text-xs text-gray-500">Nuovi</div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={cn("grid gap-4 md:grid-cols-2 lg:grid-cols-4", className)}>
      {/* Statistiche principali */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Target className="h-4 w-4 text-iss-bordeaux-600" />
            Bandi Totali
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold text-gray-900">
                {formatNumber(stats.totali)}
              </div>
              <div className="flex items-center gap-2 mt-2">
                <Badge variant={getStatusBadgeVariant('attivi')} className="flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  {stats.attivi} attivi
                </Badge>
              </div>
            </div>
            {stats.nuovi_settimana > 0 && (
              <div className="text-right">
                <div className="flex items-center gap-1 text-green-600">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-sm font-medium">+{stats.nuovi_settimana}</span>
                </div>
                <div className="text-xs text-gray-500">questa settimana</div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* In scadenza */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <AlertTriangle className="h-4 w-4 text-orange-600" />
            In Scadenza
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold text-orange-600">
            {formatNumber(stats.in_scadenza)}
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Scadono nei prossimi 7 giorni
          </p>
          {stats.in_scadenza > 0 && (
            <div className="mt-3">
              <Badge variant="warning" className="text-xs">
                <Clock className="h-3 w-3 mr-1" />
                Azione richiesta
              </Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Importo totale */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Euro className="h-4 w-4 text-green-600" />
            Valore Totale
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">
            {formatCurrency(stats.importo_totale)}
          </div>
          <div className="text-sm text-gray-600 mt-2">
            Media: {formatCurrency(stats.importo_medio)}
          </div>
          <div className="mt-3">
            <div className="text-xs text-gray-500">
              Finanziamenti disponibili per APS
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Fonti principali */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Building2 className="h-4 w-4 text-blue-600" />
            Fonti Principali
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {stats.fonti && Object.entries(stats.fonti)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 3)
              .map(([fonte, count]) => (
                <div key={fonte} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 truncate">
                    {fonte.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                  <Badge variant="secondary" className="ml-2">
                    {count}
                  </Badge>
                </div>
              ))
            }
          </div>
        </CardContent>
      </Card>

      {/* Categorie più attive - Full width */}
      <Card className="md:col-span-2 lg:col-span-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-purple-600" />
            Categorie più Attive
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {stats.categorie && Object.entries(stats.categorie)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 6)
              .map(([categoria, count]) => {
                const percentage = (count / stats.totali) * 100;
                return (
                  <div key={categoria} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium capitalize">
                        {categoria.replace('_', ' ')}
                      </span>
                      <span className="text-sm text-gray-500">
                        {count} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-iss-bordeaux-500 to-iss-gold-500 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })
            }
          </div>
        </CardContent>
      </Card>

      {/* Trend mensile - Full width se disponibile */}
      {stats.trend_mensile && stats.trend_mensile.length > 0 && (
        <Card className="md:col-span-2 lg:col-span-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-indigo-600" />
              Trend Ultimi 6 Mesi
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
              {stats.trend_mensile.slice(-6).map((trend, index) => (
                <div key={trend.mese} className="text-center">
                  <div className="text-lg font-bold text-gray-900">
                    {trend.count}
                  </div>
                  <div className="text-xs text-gray-500 mb-2">
                    {trend.mese}
                  </div>
                  <div className="text-xs font-medium text-green-600">
                    {formatCurrency(trend.importo)}
                  </div>

                  {/* Mini bar chart */}
                  <div className="mt-2 h-1 bg-gray-100 rounded overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-iss-bordeaux-400 to-iss-gold-400"
                      style={{
                        width: `${(trend.count / Math.max(...stats.trend_mensile.map(t => t.count))) * 100}%`
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
