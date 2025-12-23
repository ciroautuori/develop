import { createFileRoute } from '@tanstack/react-router';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield, Lock, Eye, UserCheck, Database, Globe } from 'lucide-react';

export const Route = createFileRoute('/privacy')({
  component: PrivacyPage,
});

function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
              <Shield className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Informativa sulla Privacy
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              La tua privacy è importante per noi
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Ultimo aggiornamento: Novembre 2025
            </p>
          </div>

          {/* Content */}
          <div className="space-y-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <UserCheck className="h-5 w-5 text-primary" />
                  Titolare del Trattamento
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>
                  Il titolare del trattamento dei dati personali è <strong>Innovazione Sociale Salernitana APS</strong>,
                  con sede in Salerno (SA), Italia.
                </p>
                <p>
                  Per qualsiasi informazione relativa al trattamento dei tuoi dati personali puoi contattarci via email
                  all'indirizzo: <a href="mailto:privacy@innovazionesocialesalernitana.it" className="text-primary hover:underline">
                  privacy@innovazionesocialesalernitana.it</a>
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-primary" />
                  Dati Raccolti
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>La piattaforma raccoglie i seguenti dati personali:</p>
                <ul>
                  <li><strong>Dati di registrazione:</strong> nome, cognome, email, tipo di organizzazione</li>
                  <li><strong>Dati di navigazione:</strong> log di accesso, pagine visitate (anonimizzati)</li>
                  <li><strong>Preferenze:</strong> categorie di bandi di interesse, impostazioni di notifica</li>
                </ul>
                <p>
                  <strong>Non raccogliamo</strong> dati sensibili, informazioni bancarie o dati non strettamente
                  necessari al funzionamento del servizio.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="h-5 w-5 text-primary" />
                  Finalità del Trattamento
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>I tuoi dati vengono utilizzati per:</p>
                <ul>
                  <li>Fornirti accesso alla piattaforma e ai suoi servizi</li>
                  <li>Inviarti notifiche su nuovi bandi corrispondenti ai tuoi interessi</li>
                  <li>Migliorare la qualità del servizio attraverso analisi aggregate</li>
                  <li>Comunicazioni di servizio (aggiornamenti, manutenzioni)</li>
                </ul>
                <p>
                  <strong>Non vendiamo</strong> i tuoi dati a terzi e non li utilizziamo per profilazione commerciale.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lock className="h-5 w-5 text-primary" />
                  Sicurezza dei Dati
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>Adottiamo misure di sicurezza tecniche e organizzative per proteggere i tuoi dati:</p>
                <ul>
                  <li>Crittografia SSL/TLS per tutte le comunicazioni</li>
                  <li>Password crittografate con algoritmi sicuri</li>
                  <li>Accesso ai dati limitato al personale autorizzato</li>
                  <li>Backup regolari e procedure di disaster recovery</li>
                  <li>Server ubicati in data center europei conformi al GDPR</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-primary" />
                  I Tuoi Diritti
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>Ai sensi del GDPR (Regolamento UE 2016/679), hai diritto a:</p>
                <ul>
                  <li><strong>Accesso:</strong> ottenere conferma dei dati trattati</li>
                  <li><strong>Rettifica:</strong> correggere dati inesatti o incompleti</li>
                  <li><strong>Cancellazione:</strong> richiedere l'eliminazione dei tuoi dati</li>
                  <li><strong>Portabilità:</strong> ricevere i tuoi dati in formato strutturato</li>
                  <li><strong>Opposizione:</strong> opporti al trattamento per motivi legittimi</li>
                  <li><strong>Revoca del consenso:</strong> revocare il consenso in qualsiasi momento</li>
                </ul>
                <p>
                  Per esercitare questi diritti, contattaci all'indirizzo email sopra indicato.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-primary/5 border-primary/20">
              <CardContent className="py-6">
                <p className="text-center text-gray-600 dark:text-gray-400">
                  Questa informativa può essere aggiornata periodicamente.
                  Ti invitiamo a consultarla regolarmente.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
