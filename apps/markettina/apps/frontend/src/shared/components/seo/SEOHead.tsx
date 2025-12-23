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
  schema?: Record<string, any>;
}

const DEFAULT_SEO = {
  siteName: 'MARKETTINA',
  title: 'MARKETTINA - AI-Powered Development Made in Italy',
  description: 'Sviluppo software AI-powered, frameworks custom e componenti enterprise. Soluzioni innovative per startup e aziende.',
  keywords: ['sviluppo software', 'AI', 'React', 'FastAPI', 'consulenza tech', 'made in italy'],
  image: 'https://markettina.it/og-image.jpg',
  url: 'https://markettina.it',
  author: 'Ciro Autuori',
  twitterHandle: '@markettina',
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
  schema,
}: SEOHeadProps) {
  const fullTitle = title ? `${title} | ${DEFAULT_SEO.siteName}` : DEFAULT_SEO.title;
  const canonical = url.startsWith('http') ? url : `${DEFAULT_SEO.url}${url}`;

  // Default Schema.org Organization
  const defaultSchema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'MARKETTINA',
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
      email: 'info@markettina.it',
    },
    sameAs: [
      'https://github.com/markettina',
      'https://linkedin.com/company/markettina',
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
      {noindex && <meta name="robots" content="noindex,nofollow" />}
      
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
      <meta name="theme-color" content="#0a0a0a" />
      <meta name="apple-mobile-web-app-capable" content="yes" />
      <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      
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
        name: 'MARKETTINA',
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
          name: 'MARKETTINA',
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
          name: 'MARKETTINA',
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
