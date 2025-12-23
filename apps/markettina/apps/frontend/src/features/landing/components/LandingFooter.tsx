/**
 * MARKETTINA Landing Footer
 */
import { Link } from 'react-router-dom';
import { useLanguage } from '../../../shared/i18n';

export function LandingFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-border py-12 bg-background">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8 mb-12">
          <div className="col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <img src="/markettina-icon.png" alt="Markettina" className="w-8 h-8 object-contain" />
              <span className="text-xl font-bold text-foreground tracking-tight">
                MARKETTINA
              </span>
            </div>
            <p className="text-muted-foreground max-w-sm">
              Piattaforma di Marketing Automation Enterprise guidata dall'Intelligenza Artificiale.
              Sostituisci interi team con agenti AI specializzati.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-foreground mb-4">Piattaforma</h4>
            <ul className="space-y-2 text-muted-foreground">
              <li><a href="#features" className="hover:text-gold transition-colors">Features</a></li>
              <li><a href="#how-it-works" className="hover:text-gold transition-colors">Come Funziona</a></li>
              <li><a href="#pricing" className="hover:text-gold transition-colors">Pricing</a></li>
              <li><Link to="/admin/login" className="hover:text-gold transition-colors">Login</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-foreground mb-4">Legale</h4>
            <ul className="space-y-2 text-muted-foreground">
              <li><Link to="/privacy" className="hover:text-gold transition-colors">Privacy Policy</Link></li>
              <li><Link to="/terms" className="hover:text-gold transition-colors">Termini di Servizio</Link></li>
              <li><Link to="/cookies" className="hover:text-gold transition-colors">Cookie Policy</Link></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
          <p>© {currentYear} MARKETTINA. Tutti i diritti riservati.</p>
          <p>Made with ❤️ in Italy 🇮🇹</p>
        </div>
      </div>
    </footer>
  );
}
