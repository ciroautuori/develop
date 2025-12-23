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
  title = 'MARKETTINA - AI-Powered Development Made in Italy',
  description = 'Sviluppo applicazioni enterprise con React 19 e FastAPI. Da Salerno, in 45 giorni dalla tua idea a un prodotto production-ready. Made in Italy 🇮🇹',
  keywords = 'sviluppo software, react, fastapi, salerno, italia, web development, ai development, enterprise applications',
  image = 'https://markettina.it/og-image.jpg',
  url = 'https://markettina.it',
  type = 'website',
}: SEOProps) {
  return (
    <Helmet>
      {/* Primary Meta Tags */}
      <title>{title}</title>
      <meta name="title" content={title} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content="Ciro Autuori - MARKETTINA" />
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
      <meta property="og:site_name" content="MARKETTINA" />

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
