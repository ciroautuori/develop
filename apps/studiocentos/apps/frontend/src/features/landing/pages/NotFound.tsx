import { Link } from 'react-router-dom';
import { Button } from '../../../shared/components/ui/button';
import '../../../app/assets/styles/landing.css';

export function NotFound() {
    return (
        <div className="min-h-screen bg-background flex flex-col items-center justify-center text-center px-6">
            <div className="space-y-6 max-w-md">
                <div className="text-9xl font-bold text-primary/20">404</div>
                <h1 className="text-4xl font-bold text-foreground">Pagina non trovata</h1>
                <p className="text-muted-foreground text-lg">
                    La pagina che stai cercando non esiste o è stata spostata.
                </p>
                <div className="pt-6">
                    <Button asChild size="lg" className="rounded-full px-8">
                        <Link to="/">
                            Torna alla Home
                        </Link>
                    </Button>
                </div>
            </div>

            {/* Meta tag per SEO 404 - anche se tecnicamente è 200 OK per SPA, il contenuto è chiaro */}
            <meta name="robots" content="noindex" />
        </div>
    );
}
