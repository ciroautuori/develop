import React from 'react';
import { Link } from '@tanstack/react-router';
import { Mail, MapPin, Phone, Facebook, Instagram, Linkedin, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/utils/cn';

interface FooterProps {
  className?: string;
}

export const Footer: React.FC<FooterProps> = ({ className }) => {
  const currentYear = new Date().getFullYear();

  const linkSections = [
    {
      title: 'Hub Bandi APS',
      links: [
        { name: 'Cerca Bandi', href: '/bandi' },
        { name: 'Statistiche', href: '/bandi/stats' },
        { name: 'Come Funziona', href: '/hub-bandi' },
        { name: 'API per Sviluppatori', href: '/api-docs' },
      ],
    },
    {
      title: 'Attività ISS',
      links: [
        { name: 'Corsi Digitali', href: '/corsi' },
        { name: 'Eventi', href: '/eventi' },
        { name: 'Progetti', href: '/progetti' },
        { name: 'Volontariato', href: '/volontariato' },
      ],
    },
    {
      title: 'Informazioni',
      links: [
        { name: 'Chi Siamo', href: '/about' },
        { name: 'La Nostra Mission', href: '/mission' },
        { name: 'Contatti', href: '/contatti' },
        { name: 'Blog', href: '/blog' },
      ],
    },
    {
      title: 'Supporto',
      links: [
        { name: 'FAQ', href: '/faq' },
        { name: 'Guida Utente', href: '/guida' },
        { name: 'Privacy Policy', href: '/privacy' },
        { name: 'Termini di Servizio', href: '/terms' },
      ],
    },
  ];

  const socialLinks = [
    { icon: Facebook, href: '#', label: 'Facebook' },
    { icon: Instagram, href: '#', label: 'Instagram' },
    { icon: Linkedin, href: '#', label: 'LinkedIn' },
  ];

  return (
    <footer className={cn('bg-muted/50 border-t mt-auto', className)}>
      <div className="container mx-auto px-4 py-12">
        {/* Main Footer Content */}
        <div className="grid gap-8 lg:grid-cols-5">
          {/* ISS Info */}
          <div className="lg:col-span-1 space-y-4">
            <Link to="/" className="flex items-center space-x-2">
              <div className="h-8 w-8">
                <img
                  src="/iss-logo.svg"
                  alt="ISS Logo"
                  className="w-full h-full object-contain"
                />
              </div>
              <span className="font-bold text-lg">ISS Salerno</span>
            </Link>

            <p className="text-sm text-muted-foreground">
              Innovazione Sociale Salernitana APS-ETS democratizza l'accesso ai bandi di finanziamento
              e promuove l'inclusione digitale nel territorio campano.
            </p>

            <div className="flex flex-wrap gap-2">
              <Badge variant="info" className="text-xs">
                Hub Bandi Regionale
              </Badge>
              <Badge variant="success" className="text-xs">
                Formazione Digitale
              </Badge>
            </div>

            {/* Contact Info */}
            <div className="space-y-2 pt-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>Via San Francesco di Paola 15, 84121 Salerno</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Mail className="h-4 w-4" />
                <a href="mailto:info@innovazionesocialesalernitana.it" className="hover:text-primary">
                  info@innovazionesocialesalernitana.it
                </a>
              </div>
            </div>
          </div>

          {/* Link Sections */}
          {linkSections.map((section) => (
            <div key={section.title} className="space-y-4">
              <h3 className="font-semibold text-sm">{section.title}</h3>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.name}>
                    <Link
                      to={link.href}
                      className="text-sm text-muted-foreground hover:text-primary transition-colors"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Newsletter Signup */}
        <div className="mt-12 py-8 border-t">
          <div className="max-w-md">
            <h3 className="font-semibold mb-2">Resta aggiornato</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Ricevi notifiche sui nuovi bandi e sulle attività ISS
            </p>
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="La tua email"
                className="flex-1 px-3 py-2 text-sm rounded-md border border-input bg-background"
              />
              <Button variant="iss-primary" size="sm">
                Iscriviti
              </Button>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-8 pt-8 border-t flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Copyright */}
          <div className="flex flex-col sm:flex-row items-center gap-2 text-sm text-muted-foreground">
            <span>© {currentYear} Innovazione Sociale Salernitana APS</span>
            <span className="hidden sm:inline">|</span>
            <span>C.F. 95201580651</span>
            <span className="hidden sm:inline">|</span>
            <span>Via San Francesco di Paola 15, Salerno</span>
          </div>

          {/* Social Links */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground mr-2">Seguici:</span>
            {socialLinks.map((social) => (
              <a
                key={social.label}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={social.label}
              >
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                >
                  <social.icon className="h-4 w-4" />
                </Button>
              </a>
            ))}
          </div>
        </div>

        {/* Made with Love */}
        <div className="mt-4 text-center">
          <p className="text-xs text-muted-foreground flex items-center justify-center gap-1">
            Realizzato con <Heart className="h-3 w-3 text-red-500 fill-current" /> per il territorio campano
          </p>
        </div>
      </div>
    </footer>
  );
};
