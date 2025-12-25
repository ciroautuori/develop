"""
SEO Sitemap Generator - Dynamic XML sitemap
Includes static pages + ToolAI dynamic posts
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.infrastructure.database.session import get_db

router = APIRouter(tags=["seo"])


@router.get("/sitemap.xml", response_class=Response)
async def get_sitemap(db: Session = Depends(get_db)):
    """
    Generate dynamic sitemap.xml with:
    - Static pages (homepage, sections)
    - ToolAI posts (dynamic, published)
    """

    # Get published ToolAI posts
    from app.domain.toolai.models import ToolAIPost

    posts = db.execute(
        select(ToolAIPost)
        .where(ToolAIPost.status == "published")
        .order_by(ToolAIPost.published_at.desc())
    ).scalars().all()

    # Build sitemap XML
    # IMPORTANTE: Solo URL reali, NO fragment (#) - Google li ignora!
    base_url = "https://studiocentos.it"
    today = datetime.now().strftime("%Y-%m-%d")

    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <!-- Homepage - Prima Agenzia AI Salerno -->
  <url>
    <loc>{base_url}/</loc>
    <xhtml:link rel="alternate" hreflang="it" href="{base_url}/" />
    <xhtml:link rel="alternate" hreflang="en" href="{base_url}/en/" />
    <xhtml:link rel="alternate" hreflang="x-default" href="{base_url}/" />
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
    <image:image>
      <image:loc>{base_url}/og-image.png</image:loc>
      <image:title>StudioCentOS - Prima Agenzia AI Salerno | Chatbot, Automazione, Analytics</image:title>
    </image:image>
  </url>

  <!-- ToolAI Hub - Scoperta quotidiana AI Tools -->
  <url>
    <loc>{base_url}/toolai</loc>
    <xhtml:link rel="alternate" hreflang="it" href="{base_url}/toolai" />
    <xhtml:link rel="alternate" hreflang="en" href="{base_url}/en/toolai" />
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
    <image:image>
      <image:loc>{base_url}/og-image.png</image:loc>
      <image:title>ToolAI - Scopri strumenti AI ogni giorno a Salerno</image:title>
    </image:image>
  </url>

  <!-- Servizio: Chatbot AI -->
  <url>
    <loc>{base_url}/#chatbot</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Servizio: Automazione Marketing AI -->
  <url>
    <loc>{base_url}/#marketing</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Servizio: Dashboard Analytics AI -->
  <url>
    <loc>{base_url}/#analytics</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>



  <!-- Privacy Policy -->
  <url>
    <loc>{base_url}/privacy</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>

  <!-- Terms of Service -->
  <url>
    <loc>{base_url}/terms</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>
'''

    # Add ToolAI posts
    for post in posts:
        post_date = post.published_at.strftime("%Y-%m-%d") if post.published_at else today

        # Clean title for SEO (use Italian title as default)
        title = (post.title_it or "ToolAI Post").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        xml_content += f'''
  <!-- ToolAI: {title} -->
  <url>
    <loc>{base_url}/toolai/{post.slug}</loc>
    <lastmod>{post_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>'''

        # Add image if present
        if post.image_url:
            image_url = post.image_url
            if not image_url.startswith("http"):
                image_url = f"{base_url}{image_url}"

            xml_content += f'''
    <image:image>
      <image:loc>{image_url}</image:loc>
      <image:title>{title}</image:title>
    </image:image>'''

        # Add Google News tags for recent posts (last 2 days)
        if post.published_at:
            days_old = (datetime.now() - post.published_at).days
            if days_old <= 2:
                pub_datetime = post.published_at.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                xml_content += f'''
    <news:news>
      <news:publication>
        <news:name>StudioCentOS ToolAI</news:name>
        <news:language>it</news:language>
      </news:publication>
      <news:publication_date>{pub_datetime}</news:publication_date>
      <news:title>{title}</news:title>
    </news:news>'''

        xml_content += '''
  </url>
'''

    # Close sitemap
    xml_content += '''
</urlset>
'''

    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "X-Robots-Tag": "all",
        }
    )


@router.get("/robots.txt", response_class=Response)
async def get_robots_txt():
    """
    Generate robots.txt with sitemap reference and AI scraper blocks
    """
    base_url = "https://studiocentos.it"

    content = f"""# StudioCentOS Robots.txt - SEO Optimized
# Prima Agenzia AI Salerno - https://studiocentos.it

User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /dashboard/
Disallow: /_next/
Disallow: /static/chunks/
Crawl-delay: 1

# Sitemaps
Sitemap: {base_url}/sitemap.xml

# ===========================================
# Google Crawlers - ALLOW ALL
# ===========================================
User-agent: Googlebot
Allow: /

User-agent: Googlebot-Image
Allow: /

User-agent: Googlebot-News
Allow: /

User-agent: Googlebot-Video
Allow: /

# ===========================================
# Bing Crawlers - ALLOW
# ===========================================
User-agent: Bingbot
Allow: /

User-agent: BingPreview
Allow: /

# ===========================================
# Social Media Crawlers - ALLOW (per Open Graph)
# ===========================================
User-agent: facebookexternalhit
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: LinkedInBot
Allow: /

User-agent: WhatsApp
Allow: /

User-agent: TelegramBot
Allow: /

# ===========================================
# AI SCRAPERS - BLOCK (protezione contenuti)
# ===========================================
User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: YouBot
Disallow: /

# ===========================================
# SEO Tool Crawlers - RATE LIMITED
# ===========================================
User-agent: AhrefsBot
Crawl-delay: 10

User-agent: SemrushBot
Crawl-delay: 10

User-agent: DotBot
Crawl-delay: 10

User-agent: MJ12bot
Disallow: /

User-agent: Rogerbot
Crawl-delay: 10

# ===========================================
# Bad Bots - BLOCK
# ===========================================
User-agent: MauiBot
Disallow: /

User-agent: SeznamBot
Disallow: /

User-agent: BLEXBot
Disallow: /

User-agent: DataForSeoBot
Disallow: /
"""

    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
        }
    )
