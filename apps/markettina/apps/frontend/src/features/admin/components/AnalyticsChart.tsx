/**
 * Analytics Chart Component - Grafici per analytics
 */
interface AnalyticsChartProps {
  data: any[];
  type: 'line' | 'bar' | 'pie';
}

export function AnalyticsChart({ data, type }: AnalyticsChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-neutral-500">
        Nessun dato disponibile
      </div>
    );
  }
  
  // Implementazione semplificata - in produzione usare Recharts o Chart.js
  if (type === 'line') {
    return (
      <div className="h-64 w-full">
        <div className="flex h-full items-end justify-between gap-2">
          {data.map((item, index) => {
            const maxValue = Math.max(...data.map((d: any) => d.events || d.sessions || 0));
            const height = ((item.events || item.sessions || 0) / maxValue) * 100;
            
            return (
              <div key={index} className="flex flex-1 flex-col items-center gap-2">
                <div
                  className="w-full rounded-t bg-gold transition-all hover:bg-gold"
                  style={{ height: `${height}%` }}
                  title={`${item.date}: ${item.events || item.sessions}`}
                />
                <span className="text-xs text-neutral-600 dark:text-neutral-400">
                  {new Date(item.date).getDate()}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }
  
  if (type === 'bar') {
    return (
      <div className="space-y-3">
        {data.slice(0, 10).map((item, index) => {
          const maxValue = Math.max(...data.map((d: any) => d.value || d.views || 0));
          const width = ((item.value || item.views || 0) / maxValue) * 100;
          
          return (
            <div key={index} className="flex items-center gap-3">
              <span className="w-24 truncate text-sm text-neutral-700 dark:text-neutral-300">
                {item.label || item.name || `Item ${index + 1}`}
              </span>
              <div className="flex-1">
                <div className="h-8 w-full rounded-full bg-neutral-200 dark:bg-neutral-800">
                  <div
                    className="h-full rounded-full bg-gold transition-all"
                    style={{ width: `${width}%` }}
                  />
                </div>
              </div>
              <span className="w-16 text-right text-sm font-medium text-neutral-900 dark:text-neutral-100">
                {item.value || item.views || 0}
              </span>
            </div>
          );
        })}
      </div>
    );
  }
  
  // Pie chart placeholder
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="text-center">
        <div className="mx-auto h-32 w-32 rounded-full bg-gradient-to-br from-gold-400 to-gold-600"></div>
        <p className="mt-4 text-sm text-neutral-600 dark:text-neutral-400">
          Pie Chart - {data.length} items
        </p>
      </div>
    </div>
  );
}
