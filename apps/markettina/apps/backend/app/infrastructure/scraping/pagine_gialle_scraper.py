"""
Pagine Gialle Scraper - Find PMI without digital presence.

Scrapes real business data from Pagine Gialle to find companies that:
- Have only basic listings (phone, address)
- No website mentioned
- Traditional sectors (restaurants, shops, services)
- Perfect targets for digital transformation
"""

import asyncio
import logging
import random
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class PagineGialleResult:
    """Single business result from Pagine Gialle."""
    name: str
    address: str
    phone: str
    category: str
    city: str
    province: str
    website: str | None = None
    email: str | None = None
    has_digital_presence: bool = False
    score: int = 0  # Higher = better lead (less digital presence)


class PagineGialleScraper:
    """
    Scraper for Pagine Gialle to find non-digitalized PMI.

    Focuses on businesses with minimal online presence:
    - No website
    - Only phone contact
    - Traditional sectors
    """

    BASE_URL = "https://www.paginegialle.it"
    SEARCH_URL = f"{BASE_URL}/ricerca"

    # Industry mappings for Pagine Gialle categories
    CATEGORY_MAPPING = {
        "ristorazione": [
            "ristoranti", "pizzerie", "trattorie", "osterie",
            "bar", "pub", "tavole-calde", "rosticcerie"
        ],
        "retail": [
            "abbigliamento", "calzature", "gioiellerie",
            "librerie", "negozi-alimentari", "fioristi"
        ],
        "studi_professionali": [
            "avvocati", "commercialisti", "consulenti",
            "notai", "geometri", "architetti"
        ],
        "salute": [
            "medici", "dentisti", "fisioterapisti",
            "farmacie", "ottici", "veterinari"
        ],
        "beauty": [
            "parrucchieri", "estetiste", "centri-benessere",
            "barbieri", "nail-art", "solarium"
        ],
        "fitness": [
            "palestre", "centri-fitness", "piscine",
            "scuole-danza", "yoga", "pilates"
        ],
        "immobiliare": [
            "agenzie-immobiliari", "amministratori-condominio",
            "geometri", "periti", "costruzioni"
        ],
        "automotive": [
            "autofficine", "carrozzerie", "gommisti",
            "concessionarie", "autolavaggi", "elettrauto"
        ],
        "turismo": [
            "hotel", "bed-breakfast", "agenzie-viaggi",
            "guide-turistiche", "noleggio-auto"
        ],
        "artigianato": [
            "idraulici", "elettricisti", "falegnami",
            "fabbri", "imbianchini", "muratori"
        ],
        "formazione": [
            "scuole-private", "centri-formazione",
            "ripetizioni", "corsi-lingue", "autoscuole"
        ],
        "eventi": [
            "catering", "noleggio-attrezzature",
            "fotografi", "wedding-planner", "animatori"
        ]
    }

    def __init__(self):
        """Initialize scraper with rate limiting and headers."""
        self.session_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.rate_limit_delay = 2  # Seconds between requests

    async def search_businesses(
        self,
        industry: str,
        city: str,
        max_results: int = 15
    ) -> list[PagineGialleResult]:
        """
        Search for businesses in specific industry and city.

        Args:
            industry: Business category (e.g., 'ristorazione')
            city: Italian city name
            max_results: Maximum number of results to return

        Returns:
            List of business results, sorted by lead score (best leads first)
        """
        logger.info(f"Searching Pagine Gialle: {industry} in {city}")

        # Get categories for this industry
        categories = self.CATEGORY_MAPPING.get(industry, [industry])
        all_results = []

        try:
            async with httpx.AsyncClient(
                headers=self.session_headers,
                timeout=30.0,
                follow_redirects=True
            ) as client:

                # Search each category
                for category in categories[:2]:  # Limit to 2 categories to avoid rate limiting
                    try:
                        results = await self._search_category(client, category, city)
                        all_results.extend(results)

                        # Rate limiting
                        await asyncio.sleep(self.rate_limit_delay)

                        if len(all_results) >= max_results:
                            break

                    except Exception as e:
                        logger.warning(f"Failed to search category {category}: {e}")
                        continue

                # Process and score results
                processed_results = self._process_results(all_results, industry, city)

                # Sort by score (best leads first) and limit results
                processed_results.sort(key=lambda x: x.score, reverse=True)
                final_results = processed_results[:max_results]

                logger.info(f"Found {len(final_results)} businesses from Pagine Gialle")
                return final_results

        except Exception as e:
            logger.error(f"Pagine Gialle scraping error: {e}")
            return []

    async def _search_category(
        self,
        client: httpx.AsyncClient,
        category: str,
        city: str
    ) -> list[dict[str, Any]]:
        """Search specific category in city."""

        # Build search URL
        search_params = {
            "cosa": category,
            "dove": city
        }

        search_url = f"{self.SEARCH_URL}?cosa={quote_plus(category)}&dove={quote_plus(city)}"

        try:
            response = await client.get(search_url)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract business listings
            businesses = []

            # Find business containers (Pagine Gialle structure)
            business_containers = soup.find_all(["div", "article"], class_=re.compile(r"(result|listing|business|item)", re.I))

            for container in business_containers[:10]:  # Limit per category
                try:
                    business_data = self._extract_business_data(container)
                    if business_data:
                        businesses.append(business_data)
                except Exception as e:
                    logger.debug(f"Failed to extract business data: {e}")
                    continue

            return businesses

        except Exception as e:
            logger.error(f"Failed to search category {category}: {e}")
            return []

    def _extract_business_data(self, container) -> dict[str, Any] | None:
        """Extract business data from HTML container."""

        try:
            # Extract name
            name_elem = container.find(["h2", "h3", "a"], class_=re.compile(r"(name|title|business)", re.I))
            if not name_elem:
                name_elem = container.find("a", href=re.compile(r"/scheda/"))

            name = name_elem.get_text(strip=True) if name_elem else None
            if not name or len(name) < 3:
                return None

            # Extract address
            address_elem = container.find(["span", "div"], class_=re.compile(r"(address|indirizzo)", re.I))
            if not address_elem:
                address_elem = container.find(text=re.compile(r"Via|Corso|Piazza|Largo"))
                if address_elem:
                    address_elem = address_elem.parent

            address = address_elem.get_text(strip=True) if address_elem else ""

            # Extract phone
            phone_elem = container.find(["span", "a"], class_=re.compile(r"(phone|telefono)", re.I))
            if not phone_elem:
                phone_elem = container.find("a", href=re.compile(r"tel:"))
            if not phone_elem:
                # Look for phone pattern in text
                phone_text = container.get_text()
                phone_match = re.search(r"(\+39\s?)?(\d{2,4}[\s\-]?\d{6,8})", phone_text)
                phone = phone_match.group(0) if phone_match else ""
            else:
                phone = phone_elem.get_text(strip=True)

            # Extract website (if any)
            website_elem = container.find("a", href=re.compile(r"http"))
            website = website_elem.get("href") if website_elem else None

            # Extract email (if any)
            email_elem = container.find("a", href=re.compile(r"mailto:"))
            email = email_elem.get("href").replace("mailto:", "") if email_elem else None

            # Basic validation
            if not name or len(name) < 3:
                return None

            return {
                "name": name,
                "address": address,
                "phone": phone,
                "website": website,
                "email": email,
                "raw_html": str(container)[:500]  # For debugging
            }

        except Exception as e:
            logger.debug(f"Error extracting business data: {e}")
            return None

    def _process_results(
        self,
        raw_results: list[dict[str, Any]],
        industry: str,
        city: str
    ) -> list[PagineGialleResult]:
        """Process and score raw results."""

        processed = []

        for raw in raw_results:
            try:
                # Create result object
                result = PagineGialleResult(
                    name=raw["name"],
                    address=raw["address"],
                    phone=raw["phone"],
                    category=industry,
                    city=city,
                    province=self._extract_province(raw["address"]),
                    website=raw.get("website"),
                    email=raw.get("email"),
                )

                # Calculate digital presence and score
                result.has_digital_presence = bool(result.website or result.email)
                result.score = self._calculate_lead_score(result)

                processed.append(result)

            except Exception as e:
                logger.debug(f"Error processing result: {e}")
                continue

        return processed

    def _calculate_lead_score(self, result: PagineGialleResult) -> int:
        """
        Calculate lead score (higher = better lead).

        Perfect leads: No website, only phone, traditional business
        """
        score = 50  # Base score

        # No website = excellent lead
        if not result.website:
            score += 40

        # No email = good lead
        if not result.email:
            score += 20

        # Has phone = can be contacted
        if result.phone:
            score += 15

        # Traditional business name patterns (family names, local terms)
        name_lower = result.name.lower()
        traditional_indicators = [
            "da ", "del ", "della ", "di ", "bar ", "trattoria",
            "osteria", "pizzeria", "ristorante", "negozio"
        ]
        if any(indicator in name_lower for indicator in traditional_indicators):
            score += 10

        # Avoid chains/franchises
        chain_indicators = ["mc", "burger", "pizza hut", "kfc", "subway"]
        if any(chain in name_lower for chain in chain_indicators):
            score -= 30

        # Random variation to avoid identical scores
        score += random.randint(-5, 5)

        return max(0, min(100, score))

    def _extract_province(self, address: str) -> str:
        """Extract province from address."""

        # Common Italian province patterns
        province_patterns = [
            r"\b(SA|NA|AV|CE|BN)\b",  # Campania
            r"\b(RM|LT|FR|VT|RI)\b",  # Lazio
            r"\b(MI|CO|VA|BG|BS)\b",  # Lombardia
            r"\b(TO|CN|AL|AT|BI)\b",  # Piemonte
        ]

        for pattern in province_patterns:
            match = re.search(pattern, address, re.I)
            if match:
                return match.group(1).upper()

        # Default based on common cities
        city_to_province = {
            "salerno": "SA", "napoli": "NA", "avellino": "AV",
            "roma": "RM", "milano": "MI", "torino": "TO",
            "bologna": "BO", "firenze": "FI", "bari": "BA"
        }

        address_lower = address.lower()
        for city, prov in city_to_province.items():
            if city in address_lower:
                return prov

        return ""


# Singleton instance
pagine_gialle_scraper = PagineGialleScraper()
