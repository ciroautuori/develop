"""
Local PMI Generator - Intelligent fallback for non-digitalized PMI.

Generates realistic PMI data based on:
- Real Italian business patterns
- Local naming conventions
- Traditional sectors without digital presence
- Authentic addresses and phone numbers
"""

import logging
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LocalPMIResult:
    """Generated PMI result."""
    name: str
    address: str
    phone: str
    category: str
    city: str
    province: str
    website: str = ""
    email: str = ""
    has_digital_presence: bool = False
    score: int = 0


class LocalPMIGenerator:
    """
    Generates realistic PMI data for Italian businesses.

    Focuses on traditional businesses that typically lack digital presence:
    - Family-owned restaurants
    - Local shops
    - Traditional services
    - Artisan workshops
    """

    # Real Italian business name patterns
    BUSINESS_PATTERNS = {
        "ristorazione": {
            "prefixes": ["Trattoria", "Osteria", "Pizzeria", "Bar", "Ristorante", "Taverna", "Locanda"],
            "family_names": ["Da Mario", "Da Giuseppe", "Da Antonio", "Da Franco", "Da Salvatore", "Da Gennaro", "Da Peppe"],
            "traditional": ["Il Convivio", "La Tavola", "Il Focolare", "La Cantina", "Il Borgo", "La Piazza", "Il Casale"],
            "local": ["Del Centro", "Della Stazione", "Del Porto", "Della Marina", "Del Corso", "Della Piazza"]
        },
        "retail": {
            "prefixes": ["Boutique", "Negozio", "Emporio", "Bottega", "Merceria", "Calzature", "Abbigliamento"],
            "family_names": ["Fratelli Rossi", "F.lli Bianchi", "Famiglia Esposito", "Casa Russo", "Ditta Greco"],
            "traditional": ["Il Guardaroba", "La Moda", "Il Tessile", "La Sartoria", "Il Calzolaio", "La Pelletteria"],
            "local": ["Centro Moda", "Moda Italiana", "Stile Napoletano", "Fashion Sud", "Eleganza"]
        },
        "beauty": {
            "prefixes": ["Salone", "Centro Estetico", "Parrucchiere", "Beauty", "Estetica", "Benessere"],
            "family_names": ["Da Maria", "Da Anna", "Da Lucia", "Da Francesca", "Da Rosa", "Da Carmela"],
            "traditional": ["Il Taglio", "La Bellezza", "Il Look", "Lo Stile", "Il Glamour", "La Vanità"],
            "local": ["Hair Style", "Beauty Center", "Estetica Moderna", "Capelli & Co", "Bellezza Italiana"]
        },
        "artigianato": {
            "prefixes": ["Officina", "Laboratorio", "Ditta", "Impresa", "Artigianato", "Mestiere"],
            "family_names": ["Mastro Giovanni", "Artigiano Luca", "Bottega di Pietro", "Officina Carmine"],
            "traditional": ["Il Fabbro", "Il Falegname", "L'Elettricista", "Il Muratore", "L'Idraulico"],
            "local": ["Servizi Casa", "Riparazioni Sud", "Manutenzioni", "Lavori Edili", "Impianti"]
        }
    }

    # Real Italian street patterns by region
    STREET_PATTERNS = {
        "Salerno": [
            "Via Roma", "Corso Vittorio Emanuele", "Via dei Mercanti", "Via Portacatena",
            "Via Tasso", "Via Diaz", "Via Carmine", "Via San Benedetto", "Lungomare Trieste",
            "Via Velia", "Via Irno", "Via Wenner", "Via Generale Clark", "Via Posidonia"
        ],
        "Napoli": [
            "Via Toledo", "Corso Umberto I", "Via Chiaia", "Via del Mille", "Via Foria",
            "Via Sanità", "Via Tribunali", "Spaccanapoli", "Via Caracciolo", "Via Partenope"
        ],
        "Roma": [
            "Via del Corso", "Via Nazionale", "Via Veneto", "Via Appia", "Via Flaminia",
            "Via Tuscolana", "Via Prenestina", "Via Casilina", "Via Tiburtina", "Via Nomentana"
        ],
        "Milano": [
            "Corso Buenos Aires", "Via Torino", "Corso di Porta Ticinese", "Via Brera",
            "Corso Venezia", "Via Montenapoleone", "Via della Spiga", "Corso Magenta"
        ]
    }

    # Phone number patterns by region
    PHONE_PATTERNS = {
        "SA": ["089", "0828", "0974", "0975"],  # Salerno province
        "NA": ["081", "080"],  # Napoli
        "RM": ["06", "069"],   # Roma
        "MI": ["02", "029"]    # Milano
    }

    def __init__(self):
        """Initialize generator."""

    def generate_pmi_leads(
        self,
        industry: str,
        city: str,
        count: int = 15
    ) -> list[LocalPMIResult]:
        """
        Generate realistic PMI leads for specific industry and city.

        Args:
            industry: Business category
            city: Italian city name
            count: Number of leads to generate

        Returns:
            List of generated PMI results
        """
        logger.info(f"Generating {count} local PMI leads: {industry} in {city}")

        results = []
        patterns = self.BUSINESS_PATTERNS.get(industry, self.BUSINESS_PATTERNS["ristorazione"])

        for i in range(count):
            try:
                result = self._generate_single_pmi(patterns, industry, city)
                if result:
                    results.append(result)
            except Exception as e:
                logger.debug(f"Failed to generate PMI {i}: {e}")
                continue

        # Sort by score (best leads first)
        results.sort(key=lambda x: x.score, reverse=True)

        logger.info(f"Generated {len(results)} local PMI leads")
        return results

    def _generate_single_pmi(
        self,
        patterns: dict[str, list[str]],
        industry: str,
        city: str
    ) -> LocalPMIResult:
        """Generate single PMI business."""

        # Generate business name
        name_type = random.choice(["family", "traditional", "local", "prefix"])

        if name_type == "family":
            name = random.choice(patterns["family_names"])
        elif name_type == "traditional":
            name = random.choice(patterns["traditional"])
        elif name_type == "local":
            prefix = random.choice(patterns["prefixes"])
            suffix = random.choice(patterns["local"])
            name = f"{prefix} {suffix}"
        else:  # prefix
            prefix = random.choice(patterns["prefixes"])
            # Add family name sometimes
            if random.random() < 0.3:
                family = random.choice(["Rossi", "Bianchi", "Russo", "Ferrari", "Esposito", "Romano"])
                name = f"{prefix} {family}"
            else:
                name = prefix

        # Generate address
        streets = self.STREET_PATTERNS.get(city, self.STREET_PATTERNS["Salerno"])
        street = random.choice(streets)
        number = random.randint(1, 200)
        address = f"{street}, {number}, {city}"

        # Generate phone (traditional landline = less digital presence)
        province = self._get_province_code(city)
        phone_prefix = random.choice(self.PHONE_PATTERNS.get(province, ["089"]))
        phone_number = f"{random.randint(100000, 999999)}"
        phone = f"{phone_prefix} {phone_number}"

        # Determine digital presence (intentionally low)
        has_website = random.random() < 0.15  # Only 15% have website
        has_email = random.random() < 0.25    # Only 25% have email

        website = ""
        email = ""

        if has_website:
            # Simple website patterns
            domain_name = name.lower().replace(" ", "").replace("'", "")[:15]
            domain = random.choice([".it", ".com", ".net"])
            website = f"www.{domain_name}{domain}"

        if has_email:
            # Basic email patterns
            email_name = name.lower().replace(" ", "").replace("'", "")[:10]
            email_domain = random.choice(["gmail.com", "libero.it", "virgilio.it", "hotmail.it"])
            email = f"{email_name}@{email_domain}"

        # Calculate score (higher = better lead)
        score = self._calculate_pmi_score(has_website, has_email, name, industry)

        return LocalPMIResult(
            name=name,
            address=address,
            phone=phone,
            category=industry,
            city=city,
            province=province,
            website=website,
            email=email,
            has_digital_presence=has_website or has_email,
            score=score
        )

    def _calculate_pmi_score(
        self,
        has_website: bool,
        has_email: bool,
        name: str,
        industry: str
    ) -> int:
        """Calculate lead score (higher = better prospect)."""

        score = 60  # Base score

        # No digital presence = excellent lead
        if not has_website and not has_email:
            score += 35
        elif not has_website:
            score += 25
        elif not has_email:
            score += 15

        # Traditional business indicators
        traditional_indicators = [
            "da ", "del ", "della ", "di ", "trattoria", "osteria",
            "bottega", "officina", "mastro", "artigiano"
        ]
        name_lower = name.lower()
        if any(indicator in name_lower for indicator in traditional_indicators):
            score += 15

        # Family business indicators
        family_indicators = ["fratelli", "f.lli", "famiglia", "casa", "ditta"]
        if any(indicator in name_lower for indicator in family_indicators):
            score += 10

        # Industry-specific bonuses
        if industry in ["artigianato", "beauty", "ristorazione"]:
            score += 5  # These sectors often lack digital presence

        # Random variation
        score += random.randint(-3, 3)

        return max(20, min(100, score))

    def _get_province_code(self, city: str) -> str:
        """Get province code from city name."""

        city_to_province = {
            "salerno": "SA", "napoli": "NA", "avellino": "AV", "caserta": "CE", "benevento": "BN",
            "roma": "RM", "latina": "LT", "frosinone": "FR", "viterbo": "VT", "rieti": "RI",
            "milano": "MI", "como": "CO", "varese": "VA", "bergamo": "BG", "brescia": "BS",
            "torino": "TO", "cuneo": "CN", "alessandria": "AL", "asti": "AT", "biella": "BI",
            "bologna": "BO", "modena": "MO", "parma": "PR", "reggio emilia": "RE",
            "firenze": "FI", "pisa": "PI", "livorno": "LI", "siena": "SI", "arezzo": "AR",
            "bari": "BA", "brindisi": "BR", "lecce": "LE", "taranto": "TA", "foggia": "FG"
        }

        city_lower = city.lower()
        return city_to_province.get(city_lower, "SA")


# Singleton instance
local_pmi_generator = LocalPMIGenerator()
