import { createFileRoute } from '@tanstack/react-router';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, Users, Scale, AlertCircle, CheckCircle, BookOpen } from 'lucide-react';

export const Route = createFileRoute('/terms')({
  component: TermsPage,
});

function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
              <FileText className="h-8 w-8 text-primary" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Termini e Condizioni
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-400">
              Regole di utilizzo della piattaforma
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
                  <BookOpen className="h-5 w-5 text-primary" />
                  Accettazione dei Termini
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>
                  Utilizzando la piattaforma <strong>Innovazione Sociale Salernitana</strong> (ISS), accetti i presenti
                  Termini e Condizioni. Se non accetti questi termini, ti preghiamo di non utilizzare il servizio.
                </p>
                <p>
                  La piattaforma è un servizio <strong>gratuito</strong> offerto dall'associazione ISS APS per supportare
                  le organizzazioni del Terzo Settore nella ricerca di bandi e finanziamenti.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  Utilizzo del Servizio
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>Il servizio è riservato a:</p>
                <ul>
                  <li>Associazioni di Promozione Sociale (APS)</li>
                  <li>Organizzazioni di Volontariato (OdV)</li>
                  <li>Enti del Terzo Settore (ETS)</li>
                  <li>Fondazioni e organizzazioni non profit</li>
                  <li>Cittadini interessati al mondo del Terzo Settore</li>
                </ul>
                <p>L'utilizzo della piattaforma deve essere conforme alle leggi italiane e dell'Unione Europea.</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-primary" />
                  Responsabilità dell'Utente
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>L'utente si impegna a:</p>
                <ul>
                  <li>Fornire informazioni accurate durante la registrazione</li>
                  <li>Mantenere riservate le proprie credenziali di accesso</li>
                  <li>Non utilizzare il servizio per scopi illegali o non autorizzati</li>
                  <li>Non tentare di accedere a dati di altri utenti</li>
                  <li>Segnalare eventuali vulnerabilità o problemi di sicurezza</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Scale className="h-5 w-5 text-primary" />
                  Limitazioni di Responsabilità
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>
                  <strong>Informazioni sui bandi:</strong> Le informazioni sui bandi presenti sulla piattaforma sono
                  raccolte da fonti pubbliche e aggiornate automaticamente. ISS non garantisce la completezza,
                  accuratezza o tempestività delle informazioni.
                </p>
                <p>
                  <strong>Ti invitiamo sempre</strong> a verificare le informazioni sui siti ufficiali degli enti
                  erogatori prima di presentare domande di finanziamento.
                </p>
                <p>
                  ISS non è responsabile per:
                </p>
                <ul>
                  <li>Decisioni prese sulla base delle informazioni della piattaforma</li>
                  <li>Interruzioni del servizio per manutenzione o cause di forza maggiore</li>
                  <li>Perdita di dati dovuta a eventi al di fuori del nostro controllo</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-primary" />
                  Proprietà Intellettuale
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>
                  La piattaforma ISS, inclusi design, codice e contenuti originali, è protetta da diritti d'autore.
                </p>
                <p>
                  Le informazioni sui bandi appartengono ai rispettivi enti erogatori e sono riportate a scopo
                  informativo nel rispetto delle licenze di utilizzo pubblico.
                </p>
                <p>
                  Il progetto ISS è sviluppato con filosofia <strong>open source</strong> per il bene della comunità.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  Modifiche ai Termini
                </CardTitle>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>
                  ISS si riserva il diritto di modificare questi Termini e Condizioni in qualsiasi momento.
                  Le modifiche saranno comunicate attraverso la piattaforma e/o via email.
                </p>
                <p>
                  L'utilizzo continuato del servizio dopo la pubblicazione delle modifiche costituisce accettazione
                  dei nuovi termini.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-primary/5 border-primary/20">
              <CardContent className="py-6">
                <p className="text-center text-gray-600 dark:text-gray-400">
                  Per domande sui Termini e Condizioni, contattaci all'indirizzo:{' '}
                  <a href="mailto:info@innovazionesocialesalernitana.it" className="text-primary hover:underline">
                    info@innovazionesocialesalernitana.it
                  </a>
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
