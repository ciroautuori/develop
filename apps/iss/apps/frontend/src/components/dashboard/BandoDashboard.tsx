import React from 'react';
import { TrendingUp, AlertCircle, Calendar, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/utils/cn';
import type { BandoStats } from '@/types/api';

interface StatCardProps {
  title: string;
  value: number;
  change?: number;
  icon: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'info';
  className?: string;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  icon,
  variant = 'default',
  className,
}) => {
  const variantStyles = {
    default: 'border-border',
    success: 'border-iss-green-200 bg-iss-green-50/50',
    warning: 'border-iss-orange-200 bg-iss-orange-50/50',
    info: 'border-iss-bordeaux-200 bg-iss-bordeaux-50/50',
  };

  return (
    <Card className={cn(variantStyles[variant], className)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold text-foreground">{(value || 0).toLocaleString('it-IT')}</p>
            {change !== undefined && (
              <div className="flex items-center mt-1">
                <TrendingUp className={cn(
                  'h-3 w-3 mr-1',
                  change >= 0 ? 'text-iss-green-600' : 'text-red-600'
                )} />
                <span className={cn(
                  'text-xs font-medium',
                  change >= 0 ? 'text-iss-green-600' : 'text-red-600'
                )}>
                  {change >= 0 ? '+' : ''}{change}%
                </span>
              </div>
            )}
          </div>
          <div className={cn(
            'p-3 rounded-full',
            variant === 'success' && 'bg-iss-green-100 text-iss-green-600',
            variant === 'warning' && 'bg-iss-orange-100 text-iss-orange-600',
            variant === 'info' && 'bg-iss-bordeaux-100 text-iss-bordeaux-600',
            variant === 'default' && 'bg-muted text-muted-foreground'
          )}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

interface BandoDashboardProps {
  stats: BandoStats;
  loading?: boolean;
  className?: string;
}

export const BandoDashboard: React.FC<BandoDashboardProps> = ({
  stats,
  loading = false,
  className,
}) => {
  if (loading) {
    return (
      <div className={cn('space-y-6', className)}>
        {/* Loading skeletons */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-muted rounded mb-2"></div>
                <div className="h-8 bg-muted rounded mb-2"></div>
                <div className="h-3 bg-muted rounded w-16"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const urgentBandi = stats.per_fonte ? Object.values(stats.per_fonte).reduce((sum, count) => sum + count, 0) : 0;
  const lastUpdate = stats.ultimo_aggiornamento ? new Date(stats.ultimo_aggiornamento).toLocaleString('it-IT') : 'Non disponibile';

  return (
    <div className={cn('space-y-6', className)}>
      {/* Main Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Bandi Totali"
          value={stats.total_bandi || 0}
          icon={<Target className="h-5 w-5" />}
          variant="info"
        />
        
        <StatCard
          title="Bandi Attivi"
          value={stats.attivi || 0}
          icon={<AlertCircle className="h-5 w-5" />}
          variant="success"
        />
        
        <StatCard
          title="In Scadenza"
          value={stats.in_scadenza || 0}
          icon={<Calendar className="h-5 w-5" />}
          variant="warning"
        />
        
        <StatCard
          title="Nuovi Oggi"
          value={stats.nuovi_oggi || 0}
          change={stats.crescita_oggi || 0}
          icon={<TrendingUp className="h-5 w-5" />}
          variant="success"
        />
      </div>

      {/* Detailed Stats */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Sources Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Distribuzione per Fonte</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {stats.per_fonte ? Object.entries(stats.per_fonte).map(([fonte, count]) => {
              const percentage = stats.total_bandi > 0 ? (count / stats.total_bandi) * 100 : 0;
              const fonteLabels: Record<string, string> = {
                comune_salerno: 'Comune di Salerno',
                regione_campania: 'Regione Campania',
                csv_salerno: 'CSV Salerno',
                fondazione_comunita: 'Fondazione Comunità',
              };

              return (
                <div key={fonte} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">
                      {fonteLabels[fonte] || fonte}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">
                        {count} ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-iss-bordeaux-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            }) : (
              <div className="text-center text-muted-foreground py-4">
                Nessun dato disponibile per le fonti
              </div>
            )}
          </CardContent>
        </Card>

        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Distribuzione per Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {stats.per_status ? Object.entries(stats.per_status).map(([status, count]) => {
              const percentage = stats.total_bandi > 0 ? (count / stats.total_bandi) * 100 : 0;
              const statusLabels: Record<string, string> = {
                attivo: 'Attivi',
                scaduto: 'Scaduti',
                archiviato: 'Archiviati',
              };

              const statusColors: Record<string, string> = {
                attivo: 'bg-iss-green-500',
                scaduto: 'bg-red-500',
                archiviato: 'bg-gray-500',
              };

              return (
                <div key={status} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant={status as any} className="text-xs">
                        {statusLabels[status] || status}
                      </Badge>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {count} ({percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className={cn(statusColors[status], 'h-2 rounded-full transition-all duration-300')}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            }) : (
              <div className="text-center text-muted-foreground py-4">
                Nessun dato disponibile per gli status
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top Keywords */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Keywords più Ricercate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {stats.keywords_top && stats.keywords_top.length > 0 ? stats.keywords_top.slice(0, 10).map((item, index) => (
              <Badge
                key={index}
                variant="outline"
                className="text-sm px-3 py-1"
              >
                {item.keyword}
                <span className="ml-2 text-xs text-muted-foreground">
                  {item.count}
                </span>
              </Badge>
            )) : (
              <div className="text-center text-muted-foreground py-4">
                Nessuna keyword disponibile
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Last Update Info */}
      <div className="text-center text-sm text-muted-foreground">
        Ultimo aggiornamento: {lastUpdate}
      </div>
    </div>
  );
};
