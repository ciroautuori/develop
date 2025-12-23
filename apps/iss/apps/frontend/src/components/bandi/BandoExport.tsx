import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { bandoAPI } from '@/services/api';
import { BandoFilters } from '@/types/api';
import { 
  Download, 
  FileText, 
  FileSpreadsheet, 
  Printer,
  Mail,
  Share2,
  Settings,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { cn } from '@/utils/cn';

interface BandoExportProps {
  selectedBandi: string[];
  filters: BandoFilters;
  className?: string;
}

interface ExportOptions {
  format: 'pdf' | 'excel' | 'csv';
  fields: string[];
  includeFilters: boolean;
  includeStats: boolean;
  emailTo?: string;
}

const AVAILABLE_FIELDS = [
  { id: 'titolo', label: 'Titolo', required: true },
  { id: 'ente_erogatore', label: 'Ente Erogatore', required: true },
  { id: 'descrizione', label: 'Descrizione' },
  { id: 'categoria', label: 'Categoria' },
  { id: 'importo_max', label: 'Importo Massimo' },
  { id: 'data_scadenza', label: 'Data Scadenza' },
  { id: 'data_pubblicazione', label: 'Data Pubblicazione' },
  { id: 'link_bando', label: 'Link al Bando' },
  { id: 'requirements', label: 'Requisiti' },
  { id: 'tags', label: 'Tag' },
  { id: 'status', label: 'Stato' },
  { id: 'priority_score', label: 'Punteggio Priorità' },
] as const;

export const BandoExport: React.FC<BandoExportProps> = ({
  selectedBandi,
  filters,
  className
}) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'pdf',
    fields: ['titolo', 'ente_erogatore', 'categoria', 'importo_max', 'data_scadenza'],
    includeFilters: true,
    includeStats: false,
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportStatus, setExportStatus] = useState<'idle' | 'preparing' | 'generating' | 'complete'>('idle');

  // Quick export senza dialog
  const handleQuickExport = async (format: 'pdf' | 'excel' | 'csv') => {
    setIsExporting(true);
    setExportStatus('preparing');

    try {
      const response = await bandoAPI.export({
        format,
        bando_ids: selectedBandi,
        filters: selectedBandi.length === 0 ? filters : undefined,
        fields: ['titolo', 'ente_erogatore', 'categoria', 'importo_max', 'data_scadenza'],
        include_filters: true,
      });

      // Simula progresso
      setExportStatus('generating');
      for (let i = 0; i <= 100; i += 20) {
        setExportProgress(i);
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      // Download file
      const blob = new Blob([response.data], { 
        type: format === 'pdf' ? 'application/pdf' : 
              format === 'excel' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' :
              'text/csv'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bandi-iss-${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setExportStatus('complete');
      
    } catch (error) {
      console.error('Errore export:', error);
      setExportStatus('idle');
    } finally {
      setIsExporting(false);
      setTimeout(() => {
        setExportProgress(0);
        setExportStatus('idle');
      }, 2000);
    }
  };

  // Advanced export con opzioni
  const handleAdvancedExport = async () => {
    setIsExporting(true);
    setExportStatus('preparing');

    try {
      const response = await bandoAPI.export({
        format: exportOptions.format,
        bando_ids: selectedBandi,
        filters: selectedBandi.length === 0 ? filters : undefined,
        fields: exportOptions.fields,
        include_filters: exportOptions.includeFilters,
        include_stats: exportOptions.includeStats,
        email_to: exportOptions.emailTo,
      });

      setExportStatus('generating');
      for (let i = 0; i <= 100; i += 10) {
        setExportProgress(i);
        await new Promise(resolve => setTimeout(resolve, 300));
      }

      if (exportOptions.emailTo) {
        setExportStatus('complete');
      } else {
        // Download file
        const blob = new Blob([response.data]);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bandi-iss-${new Date().toISOString().split('T')[0]}.${exportOptions.format === 'excel' ? 'xlsx' : exportOptions.format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        setExportStatus('complete');
      }

    } catch (error) {
      console.error('Errore export:', error);
      setExportStatus('idle');
    } finally {
      setIsExporting(false);
      setIsDialogOpen(false);
      setTimeout(() => {
        setExportProgress(0);
        setExportStatus('idle');
      }, 3000);
    }
  };

  const updateField = (fieldId: string, checked: boolean) => {
    const field = AVAILABLE_FIELDS.find(f => f.id === fieldId);
    if (field?.required && !checked) return; // Non permettere deselezionare campi obbligatori

    setExportOptions(prev => ({
      ...prev,
      fields: checked 
        ? [...prev.fields, fieldId]
        : prev.fields.filter(id => id !== fieldId)
    }));
  };

  const ExportProgressDialog = () => (
    <Dialog open={isExporting} onOpenChange={() => !isExporting && setIsExporting(false)}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {exportStatus === 'complete' ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <Loader2 className="h-5 w-5 animate-spin text-iss-bordeaux-600" />
            )}
            {exportStatus === 'preparing' && 'Preparazione export...'}
            {exportStatus === 'generating' && 'Generazione file...'}
            {exportStatus === 'complete' && 'Export completato!'}
          </DialogTitle>
          <DialogDescription>
            {exportStatus === 'preparing' && 'Recupero dei dati dei bandi selezionati'}
            {exportStatus === 'generating' && 'Creazione del file per il download'}
            {exportStatus === 'complete' && exportOptions.emailTo 
              ? `File inviato via email a ${exportOptions.emailTo}`
              : 'Il download inizierà automaticamente'
            }
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <Progress value={exportProgress} className="w-full" />
          <p className="text-sm text-gray-500 mt-2 text-center">
            {exportProgress}% completato
          </p>
        </div>

        {exportStatus === 'complete' && (
          <DialogFooter>
            <Button 
              onClick={() => setIsExporting(false)}
              className="w-full"
            >
              Chiudi
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button 
            variant="outline" 
            size="sm"
            disabled={isExporting}
            className={cn("flex items-center gap-2", className)}
            aria-label="Esporta bandi"
          >
            <Download className="h-4 w-4" />
            Esporta
            {selectedBandi.length > 0 && (
              <span className="bg-iss-bordeaux-100 text-iss-bordeaux-800 px-1.5 py-0.5 rounded text-xs">
                {selectedBandi.length}
              </span>
            )}
          </Button>
        </DropdownMenuTrigger>

        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            {selectedBandi.length > 0 
              ? `${selectedBandi.length} bandi selezionati`
              : 'Tutti i bandi filtrati'
            }
          </DropdownMenuLabel>
          <DropdownMenuSeparator />

          {/* Quick exports */}
          <DropdownMenuItem
            onClick={() => handleQuickExport('pdf')}
            disabled={isExporting}
            className="flex items-center gap-2"
          >
            <FileText className="h-4 w-4 text-red-600" />
            <div>
              <div className="font-medium">Esporta PDF</div>
              <div className="text-xs text-gray-500">Report stampabile</div>
            </div>
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={() => handleQuickExport('excel')}
            disabled={isExporting}
            className="flex items-center gap-2"
          >
            <FileSpreadsheet className="h-4 w-4 text-green-600" />
            <div>
              <div className="font-medium">Esporta Excel</div>
              <div className="text-xs text-gray-500">Foglio di calcolo</div>
            </div>
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={() => handleQuickExport('csv')}
            disabled={isExporting}
            className="flex items-center gap-2"
          >
            <FileSpreadsheet className="h-4 w-4 text-blue-600" />
            <div>
              <div className="font-medium">Esporta CSV</div>
              <div className="text-xs text-gray-500">Dati tabulari</div>
            </div>
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          {/* Advanced options */}
          <DropdownMenuItem
            onClick={() => setIsDialogOpen(true)}
            disabled={isExporting}
            className="flex items-center gap-2"
          >
            <Settings className="h-4 w-4" />
            <div>
              <div className="font-medium">Opzioni avanzate</div>
              <div className="text-xs text-gray-500">Personalizza export</div>
            </div>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Advanced Export Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Esporta Bandi - Opzioni Avanzate</DialogTitle>
            <DialogDescription>
              Personalizza il formato e i contenuti dell'export
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Formato */}
            <div>
              <h3 className="font-medium mb-3">Formato file</h3>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: 'pdf', label: 'PDF', icon: FileText, color: 'text-red-600' },
                  { value: 'excel', label: 'Excel', icon: FileSpreadsheet, color: 'text-green-600' },
                  { value: 'csv', label: 'CSV', icon: FileSpreadsheet, color: 'text-blue-600' },
                ].map((format) => (
                  <label
                    key={format.value}
                    className={cn(
                      'flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors',
                      exportOptions.format === format.value 
                        ? 'border-iss-bordeaux-600 bg-iss-bordeaux-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    )}
                  >
                    <input
                      type="radio"
                      name="format"
                      value={format.value}
                      checked={exportOptions.format === format.value}
                      onChange={(e) => setExportOptions(prev => ({ 
                        ...prev, 
                        format: e.target.value as any 
                      }))}
                      className="sr-only"
                    />
                    <format.icon className={cn("h-5 w-5", format.color)} />
                    <span className="font-medium">{format.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Campi da includere */}
            <div>
              <h3 className="font-medium mb-3">Campi da includere</h3>
              <div className="grid grid-cols-2 gap-3">
                {AVAILABLE_FIELDS.map((field) => (
                  <label 
                    key={field.id}
                    className="flex items-center gap-2 p-2 rounded hover:bg-gray-50"
                  >
                    <Checkbox
                      checked={exportOptions.fields.includes(field.id)}
                      onCheckedChange={(checked) => updateField(field.id, !!checked)}
                      disabled={field.required}
                    />
                    <span className={cn(
                      "text-sm",
                      field.required && "font-medium"
                    )}>
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Opzioni aggiuntive */}
            <div>
              <h3 className="font-medium mb-3">Opzioni aggiuntive</h3>
              <div className="space-y-3">
                <label className="flex items-center gap-2">
                  <Checkbox
                    checked={exportOptions.includeFilters}
                    onCheckedChange={(checked) => setExportOptions(prev => ({
                      ...prev,
                      includeFilters: !!checked
                    }))}
                  />
                  <span className="text-sm">Includi riepilogo filtri applicati</span>
                </label>

                <label className="flex items-center gap-2">
                  <Checkbox
                    checked={exportOptions.includeStats}
                    onCheckedChange={(checked) => setExportOptions(prev => ({
                      ...prev,
                      includeStats: !!checked
                    }))}
                  />
                  <span className="text-sm">Includi statistiche generali</span>
                </label>
              </div>
            </div>

            {/* Invio via email */}
            <div>
              <h3 className="font-medium mb-3">Invio via email (opzionale)</h3>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-gray-400" />
                <input
                  type="email"
                  placeholder="indirizzo@email.com"
                  value={exportOptions.emailTo || ''}
                  onChange={(e) => setExportOptions(prev => ({
                    ...prev,
                    emailTo: e.target.value
                  }))}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Se specificato, il file verrà inviato via email invece del download diretto
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setIsDialogOpen(false)}
              disabled={isExporting}
            >
              Annulla
            </Button>
            <Button 
              onClick={handleAdvancedExport}
              disabled={isExporting || exportOptions.fields.length === 0}
              className="flex items-center gap-2"
            >
              {isExporting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              {exportOptions.emailTo ? 'Invia via Email' : 'Esporta'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ExportProgressDialog />
    </>
  );
};
