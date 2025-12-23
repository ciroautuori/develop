import { createFileRoute } from '@tanstack/react-router';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart, Target, Users, Lightbulb, MapPin, Mail, ExternalLink, Calendar, Building2, Award } from 'lucide-react';
import { Link } from '@tanstack/react-router';

export const Route = createFileRoute('/about')({
  component: AboutPage,
});

function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-primary/10 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Chi Siamo
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto mb-8">
            <strong>Innovazione Sociale Salernitana APS</strong> è un'Associazione di Promozione Sociale
            costituita l'8 maggio 2024 a Salerno, dedicata all'inclusione digitale e all'innovazione sociale
            per il territorio campano.
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm">
            <span className="bg-white/80 dark:bg-gray-800 px-4 py-2 rounded-full flex items-center gap-2">
              <Calendar className="h-4 w-4 text-primary" />
              Costituita: 8 Maggio 2024
            </span>
            <span className="bg-white/80 dark:bg-gray-800 px-4 py-2 rounded-full flex items-center gap-2">
              <Building2 className="h-4 w-4 text-primary" />
              C.F. 95201580651
            </span>
            <span className="bg-white/80 dark:bg-gray-800 px-4 py-2 rounded-full flex items-center gap-2">
              <Award className="h-4 w-4 text-primary" />
              Iscritta al RUNTS
            </span>
          </div>
        </div>
      </section>

      <div className="container mx-auto px-4 py-16">
        {/* Mission & Vision */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <Target className="h-6 w-6 text-primary" />
                La Nostra Missione
              </CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert">
              <p>
                Rendere accessibili le opportunità di finanziamento a tutte le organizzazioni del
                Terzo Settore, indipendentemente dalle loro dimensioni o risorse.
              </p>
              <p>
                Crediamo che l'accesso all'informazione sia fondamentale per l'innovazione sociale
                e lo sviluppo delle comunità locali.
              </p>
            </CardContent>
          </Card>

          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <Lightbulb className="h-6 w-6 text-amber-500" />
                La Nostra Visione
              </CardTitle>
            </CardHeader>
            <CardContent className="prose dark:prose-invert">
              <p>
                Un ecosistema del Terzo Settore campano forte, connesso e capace di attrarre
                risorse per progetti di impatto sociale.
              </p>
              <p>
                Vogliamo che ogni APS, OdV e ETS abbia gli strumenti per realizzare la propria
                missione e contribuire al bene comune.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Values */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-white">
            I Nostri Valori
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 mb-4">
                <Heart className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Accessibilità</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Tutti i nostri servizi sono gratuiti e la piattaforma è progettata per essere
                accessibile a tutti.
              </p>
            </Card>

            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-500/10 mb-4">
                <Users className="h-6 w-6 text-green-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Comunità</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Crediamo nella forza della collaborazione e nella condivisione delle conoscenze
                tra organizzazioni.
              </p>
            </Card>

            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-purple-500/10 mb-4">
                <Lightbulb className="h-6 w-6 text-purple-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Innovazione</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Utilizziamo tecnologie avanzate come l'AI per semplificare la ricerca di
                finanziamenti.
              </p>
            </Card>
          </div>
        </section>

        {/* What We Do */}
        <section className="mb-16">
          <Card className="bg-gradient-to-r from-primary/5 to-purple-500/5">
            <CardHeader>
              <CardTitle className="text-2xl text-center">Cosa Facciamo (Art. 2 Statuto)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="font-semibold text-lg mb-2">🖥️ Inclusione Digitale</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Promuoviamo l'inclusione e l'innovazione digitale a Salerno e nelle aree limitrofe,
                    garantendo che ogni individuo possa accedere alle competenze digitali necessarie.
                  </p>

                  <h3 className="font-semibold text-lg mb-2">👴 Alfabetizzazione Digitale</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Corsi gratuiti per anziani e persone svantaggiate: uso di Internet, smartphone,
                    dispositivi smart e software per la quotidianità.
                  </p>

                  <h3 className="font-semibold text-lg mb-2">♿ Formazione Inclusiva</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Percorsi formativi per persone con disabilità, con tecnologie assistive
                    e mentoring professionale per l'integrazione lavorativa.
                  </p>
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-2">🔍 Hub Bandi per APS</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Sistema automatizzato con AI per monitorare quotidianamente i bandi di
                    finanziamento destinati al Terzo Settore campano.
                  </p>

                  <h3 className="font-semibold text-lg mb-2">🚀 Hackathon Sociali</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Organizziamo hackathon e competizioni software per generare soluzioni innovative
                    a problemi sociali, ambientali e della comunità.
                  </p>

                  <h3 className="font-semibold text-lg mb-2">💻 Laboratori Digitali</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Attività pratiche di apprendimento digitale per sviluppare competenze tecniche
                    in un ambiente inclusivo, dalla base all'avanzato.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Consiglio Direttivo */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-white">
            Consiglio Direttivo
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
                <Users className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-1">Fortunata Mautone</h3>
              <p className="text-primary font-medium mb-2">Presidente</p>
              <p className="text-sm text-gray-500">Mandato triennale 2024-2027</p>
            </Card>

            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/10 mb-4">
                <Users className="h-8 w-8 text-green-500" />
              </div>
              <h3 className="text-xl font-semibold mb-1">Giovanni Autuori</h3>
              <p className="text-green-600 font-medium mb-2">Vice-Presidente</p>
              <p className="text-sm text-gray-500">Mandato triennale 2024-2027</p>
            </Card>

            <Card className="text-center p-6">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-500/10 mb-4">
                <Users className="h-8 w-8 text-purple-500" />
              </div>
              <h3 className="text-xl font-semibold mb-1">Riccardo Marchesano</h3>
              <p className="text-purple-600 font-medium mb-2">Segretario</p>
              <p className="text-sm text-gray-500">Mandato triennale 2024-2027</p>
            </Card>
          </div>
          <p className="text-center text-sm text-gray-500 mt-6">
            L'associazione è stata fondata da 7 soci costituenti il 8 maggio 2024
          </p>
        </section>

        {/* Contact */}
        <section>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <MapPin className="h-6 w-6 text-primary" />
                Sede Legale e Contatti
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
                    <div>
                      <p className="font-medium">Innovazione Sociale Salernitana APS</p>
                      <p>Via San Francesco di Paola, 15</p>
                      <p>84121 Salerno (SA)</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Building2 className="h-5 w-5 text-gray-400" />
                    <span>C.F. 95201580651</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail className="h-5 w-5 text-gray-400" />
                    <a href="mailto:info@innovazionesocialesalernitana.it" className="text-primary hover:underline">
                      info@innovazionesocialesalernitana.it
                    </a>
                  </div>
                  <div className="flex items-center gap-3">
                    <ExternalLink className="h-5 w-5 text-gray-400" />
                    <a href="https://innovazionesocialesalernitana.it" className="text-primary hover:underline">
                      innovazionesocialesalernitana.it
                    </a>
                  </div>
                </div>
                <div className="flex flex-col justify-center items-start md:items-end gap-4">
                  <Link to="/bandi">
                    <Button size="lg">
                      Esplora i Bandi
                    </Button>
                  </Link>
                  <Link to="/auth/register">
                    <Button variant="outline" size="lg">
                      Registrati Gratis
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Dati legali */}
              <div className="mt-8 pt-6 border-t text-sm text-gray-500">
                <p>
                  Associazione di Promozione Sociale costituita ai sensi del D.Lgs. 117/2017 (Codice del Terzo Settore).
                  Atto costitutivo registrato presso l'Agenzia delle Entrate di Salerno il 23/05/2024 al n. 762.
                </p>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  );
}
