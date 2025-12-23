"""
SEO Sitemap Generator - Dynamic XML sitemap
Includes static pages + ToolAI dynamic posts
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

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
    base_url = "https://markettina.it"
    today = datetime.now().strftime("%Y-%m-%d")

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">

  <!-- Homepage -->
  <url>
    <loc>{base_url}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
    <image:image>
      <image:loc>{base_url}/og-image.png</image:loc>
      <image:title>MARKETTINA - Software House Salerno</image:title>
    </image:image>
  </url>

  <!-- Chi Siamo -->
  <url>
    <loc>{base_url}/#chi-siamo</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <!-- Servizi -->
  <url>
    <loc>{base_url}/#servizi</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <!-- Progetti -->
  <url>
    <loc>{base_url}/#progetti</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Contatti -->
  <url>
    <loc>{base_url}/#contatti</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Prenotazione -->
  <url>
    <loc>{base_url}/#prenota</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>
"""

    # Add ToolAI posts
    for post in posts:
        post_date = post.published_at.strftime("%Y-%m-%d") if post.published_at else today

        # Clean title for SEO (use Italian title as default)
        title = (post.title_it or "ToolAI Post").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        xml_content += f"""
  <!-- ToolAI: {title} -->
  <url>
    <loc>{base_url}/toolai/{post.slug}</loc>
    <lastmod>{post_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>"""

        # Add image if present
        if post.image_url:
            image_url = post.image_url
            if not image_url.startswith("http"):
                image_url = f"{base_url}{image_url}"

            xml_content += f"""
    <image:image>
      <image:loc>{image_url}</image:loc>
      <image:title>{title}</image:title>
    </image:image>"""

        # Add Google News tags for recent posts (last 2 days)
        if post.published_at:
            days_old = (datetime.now() - post.published_at).days
            if days_old <= 2:
                pub_datetime = post.published_at.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                xml_content += f"""
    <news:news>
      <news:publication>
        <news:name>MARKETTINA ToolAI</news:name>
        <news:language>it</news:language>
      </news:publication>
      <news:publication_date>{pub_datetime}</news:publication_date>
      <news:title>{title}</news:title>
    </news:news>"""

        xml_content += """
  </url>
"""

    # Close sitemap
    xml_content += """
</urlset>
"""

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
    Generate robots.txt with sitemap reference
    """
    base_url = "https://markettina.it"

    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /dashboard/

# Sitemaps
Sitemap: {base_url}/sitemap.xml

# Crawl-delay for polite crawling
Crawl-delay: 1

# Specific bot rules
User-agent: Googlebot
Allow: /

User-agent: Googlebot-Image
Allow: /

User-agent: Bingbot
Allow: /

# Block bad bots
User-agent: MJ12bot
Disallow: /

User-agent: AhrefsBot
Crawl-delay: 10
"""

    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
        }
    )
