/**
 * SEO Component - Meta tags per ottimizzazione SEO
 */

import { Helmet } from 'react-helmet-async';

interface SEOProps {
  title?: string;
  description?: string;
  keywords?: string;
  image?: string;
  url?: string;
  type?: string;
}

export function SEO({
  title = 'StudioCentOS - Prima Agenzia AI Salerno | Chatbot, Automazione, Analytics con Intelligenza Artificiale',
  description = 'Prima Agenzia AI a Salerno. Intelligenza Artificiale per Aziende: Chatbot AI, Automazione Marketing, Generazione Contenuti, Dashboard Analytics. GPT-4, Claude, Gemini. Unici in Campania 🤖',
  keywords = 'agenzia ai salerno, intelligenza artificiale salerno, chatbot ai salerno, automazione ai campania, ai marketing salerno, gpt salerno, claude ai campania, gemini ai salerno, machine learning salerno, ai per aziende salerno, consulenza ai salerno',
  image = 'https://studiocentos.it/og-image.png',
  url = 'https://studiocentos.it',
  type = 'website',
}: SEOProps) {
  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content="Ciro Autuori - STUDIOCENTOS Prima Agenzia AI Salerno" />
      <meta name="robots" content="index, follow" />
      <meta name="language" content="Italian" />
      <meta name="revisit-after" content="7 days" />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={image} />
      <meta property="og:locale" content="it_IT" />
      <meta property="og:site_name" content="STUDIOCENTOS - Agenzia AI Salerno" />

      {/* Twitter */}
      <meta property="twitter:card" content="summary_large_image" />
      <meta property="twitter:url" content={url} />
      <meta property="twitter:title" content={title} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={image} />

      {/* Additional Meta Tags */}
      <meta name="theme-color" content="#D4AF37" />
      <meta name="msapplication-TileColor" content="#0a0a0a" />
      <link rel="canonical" href={url} />
    </Helmet>
  );
}
