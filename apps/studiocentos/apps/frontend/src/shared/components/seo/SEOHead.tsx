/**
 * SEOHead Component - Dynamic meta tags for SEO optimization.
 * Includes Open Graph, Twitter Cards, Schema.org markup.
 */

import { Helmet } from 'react-helmet-async';

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string[];
  image?: string;
  url?: string;
  type?: 'website' | 'article' | 'profile';
  author?: string;
  publishedTime?: string;
  modifiedTime?: string;
  noindex?: boolean;
  nofollow?: boolean;
  schema?: Record<string, any>;
  hreflangIt?: string;
  hreflangEn?: string;
}

const DEFAULT_SEO = {
  siteName: 'StudioCentOS',
  title: 'StudioCentOS - Prima Agenzia AI Salerno | Intelligenza Artificiale per Aziende',
  description: 'Prima Agenzia AI a Salerno. Sviluppiamo Chatbot AI, Automazione Marketing, Dashboard Analytics con GPT-5.2 Pro, Opus 4.5, Gemini 3 Pro, DeepSeek V3.1. Unici in Campania.',
  keywords: ['agenzia ai salerno', 'intelligenza artificiale campania', 'chatbot ai', 'automazione marketing ai', 'studiocentos'],
  image: 'https://studiocentos.it/og-image.png',
  url: 'https://studiocentos.it',
  author: 'Ciro Autuori',
  twitterHandle: '@studiocentos',
};

export function SEOHead({
  title,
  description = DEFAULT_SEO.description,
  keywords = DEFAULT_SEO.keywords,
  image = DEFAULT_SEO.image,
  url = DEFAULT_SEO.url,
  type = 'website',
  author = DEFAULT_SEO.author,
  publishedTime,
  modifiedTime,
  noindex = false,
  nofollow = false,
  schema,
  hreflangIt,
  hreflangEn,
}: SEOHeadProps) {
  const fullTitle = title ? `${title} | ${DEFAULT_SEO.siteName}` : DEFAULT_SEO.title;
  const canonical = url && url.startsWith('http') ? url : `${DEFAULT_SEO.url}${url || ''}`;

  const robotsContent = [
    noindex ? 'noindex' : 'index',
    nofollow ? 'nofollow' : 'follow',
    'max-image-preview:large',
    'max-snippet:-1',
    'max-video-preview:-1'
  ].join(', ');

  // Default Schema.org Organization
  const defaultSchema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'StudioCentOS',
    description: DEFAULT_SEO.description,
    url: DEFAULT_SEO.url,
    logo: `${DEFAULT_SEO.url}/logo.png`,
    founder: {
      '@type': 'Person',
      name: 'Ciro Autuori',
      jobTitle: 'Full Stack Developer & AI Engineer',
    },
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'Customer Service',
      email: 'info@studiocentos.it',
    },
    sameAs: [
      'https://github.com/studiocentos',
      'https://linkedin.com/company/studiocentos',
    ],
  };

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords.join(', ')} />
      <meta name="author" content={author} />
      <link rel="canonical" href={canonical} />


      {/* Robots */}
      <meta name="robots" content={robotsContent} />
      <meta name="googlebot" content={robotsContent} />

      {/* Open Graph */}
      <meta property="og:site_name" content={DEFAULT_SEO.siteName} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:type" content={type} />
      <meta property="og:url" content={canonical} />
      <meta property="og:image" content={image} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:locale" content="it_IT" />
      <meta property="og:locale:alternate" content="en_US" />

      {/* Article specific */}
      {type === 'article' && publishedTime && (
        <meta property="article:published_time" content={publishedTime} />
      )}
      {type === 'article' && modifiedTime && (
        <meta property="article:modified_time" content={modifiedTime} />
      )}
      {type === 'article' && author && (
        <meta property="article:author" content={author} />
      )}

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:site" content={DEFAULT_SEO.twitterHandle} />
      <meta name="twitter:creator" content={DEFAULT_SEO.twitterHandle} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />

      {/* Additional Tags */}
      <meta name="theme-color" content="#D4AF37" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />

      {/* Geo Tags for Salerno */}
      <meta name="geo.region" content="IT-SA" />
      <meta name="geo.placename" content="Salerno" />
      <meta name="geo.position" content="40.68244;14.76874" />

      {/* hreflang for multilingual SEO */}
      {hreflangIt && <link rel="alternate" hrefLang="it" href={hreflangIt} />}
      {hreflangEn && <link rel="alternate" hrefLang="en" href={hreflangEn} />}
      <link rel="alternate" hrefLang="x-default" href={canonical} />

      {/* Schema.org JSON-LD */}
      <script type="application/ld+json">
        {JSON.stringify(schema || defaultSchema)}
      </script>
    </Helmet>
  );
}

// Pre-configured SEO for common pages

export function HomeSEO() {
  return (
    <SEOHead
      schema={{
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: 'StudioCentOS',
        url: DEFAULT_SEO.url,
        potentialAction: {
          '@type': 'SearchAction',
          target: `${DEFAULT_SEO.url}/search?q={search_term_string}`,
          'query-input': 'required name=search_term_string',
        },
      }}
    />
  );
}

export function ProjectSEO({
  title,
  description,
  image,
  technologies,
  year,
  url
}: {
  title: string;
  description: string;
  image?: string;
  technologies?: string[];
  year?: number;
  url?: string;
}) {
  return (
    <SEOHead
      title={title}
      description={description}
      image={image}
      url={url}
      type="article"
      keywords={['progetto', 'portfolio', ...(technologies || [])]}
      schema={{
        '@context': 'https://schema.org',
        '@type': 'CreativeWork',
        name: title,
        description,
        image,
        author: {
          '@type': 'Organization',
          name: 'StudioCentOS',
        },
        dateCreated: year ? `${year}-01-01` : undefined,
        keywords: technologies?.join(', '),
      }}
    />
  );
}

export function ServiceSEO({
  title,
  description,
  features
}: {
  title: string;
  description: string;
  features?: string[];
}) {
  return (
    <SEOHead
      title={title}
      description={description}
      type="article"
      schema={{
        '@context': 'https://schema.org',
        '@type': 'Service',
        name: title,
        description,
        provider: {
          '@type': 'Organization',
          name: 'StudioCentOS',
        },
        serviceType: 'Software Development',
        offers: features?.map(feature => ({
          '@type': 'Offer',
          name: feature,
        })),
      }}
    />
  );
}
