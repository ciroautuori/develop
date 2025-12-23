import asyncio
import logging
import os
import sys
import json
import httpx
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("update_google_presence")

# Load env vars from .env.production
def load_env_file(filepath):
    if not os.path.exists(filepath):
        # logger.warning(f"Env file not found: {filepath}")
        return
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            os.environ[key] = value

# Load env - Try to load but don't fail if missing (container env vars take precedence)
sys.path.append(os.getcwd())
try:
    load_env_file(os.path.join(os.getcwd(), "config/docker/.env.production"))
except Exception:
    pass

# ============================================================================
# STANDALONE CLIENTS (No dependencies on app.*)
# ============================================================================

class StandaloneGMBClient:
    def __init__(self, access_token):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        self.base_url = "https://mybusinessbusinessinformation.googleapis.com/v1"
        self.account_url = "https://mybusinessaccountmanagement.googleapis.com/v1"
        self.reviews_url = "https://mybusiness.googleapis.com/v4"

    async def list_locations(self):
        # 1. Get Accounts
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.account_url}/accounts", headers=self.headers)
            if resp.status_code != 200:
                logger.error(f"GMB Error getting accounts: {resp.text}")
                return []
            accounts = resp.json().get("accounts", [])
            if not accounts:
                return []

            account_id = accounts[0]["name"]

            # 2. Get Locations
            resp = await client.get(
                f"{self.base_url}/{account_id}/locations",
                headers=self.headers,
                params={"readMask": "name,title,storefrontAddress"}
            )
            if resp.status_code != 200:
                logger.error(f"GMB Error getting locations: {resp.text}")
                return []

            return resp.json().get("locations", [])

    async def create_post(self, location_name, summary, action_url, media_url):
        # Format location name if needed
        # location_name format: locations/XXXXX
        # API requires: accounts/XXXX/locations/XXXXX/localPosts

        # Need to find account ID again or extract from location if possible?
        # Actually v4 API uses accounts/XX/locations/XX structure.

        # Let's get account ID first
        async with httpx.AsyncClient() as client:
            acc_resp = await client.get(f"{self.account_url}/accounts", headers=self.headers)
            account_id = acc_resp.json().get("accounts", [])[0]["name"]

            url = f"{self.reviews_url}/{account_id}/{location_name}/localPosts"

            body = {
                "summary": summary,
                "languageCode": "it",
                "topicType": "STANDARD",
                "callToAction": {
                    "actionType": "LEARN_MORE",
                    "url": action_url
                },
                "media": [
                    {"mediaFormat": "PHOTO", "sourceUrl": media_url}
                ]
            }

            resp = await client.post(url, headers=self.headers, json=body)
            if resp.status_code not in [200, 201]:
                logger.error(f"GMB Post Error: {resp.text}")
                return None

            return resp.json()

class StandaloneGSCClient:
    def __init__(self, access_token, site_url):
        self.access_token = access_token
        self.site_url = site_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        self.base_url = "https://searchconsole.googleapis.com/webmasters/v3"

    async def submit_sitemap(self, sitemap_url):
        import urllib.parse
        encoded_site = urllib.parse.quote(self.site_url, safe="")
        encoded_sitemap = urllib.parse.quote(sitemap_url, safe="")

        url = f"{self.base_url}/sites/{encoded_site}/sitemaps/{encoded_sitemap}"

        async with httpx.AsyncClient() as client:
            resp = await client.put(url, headers=self.headers)
            if resp.status_code not in [200, 204]:
                logger.error(f"GSC Sitemap Error: {resp.text}")
                return False
            return True

# ============================================================================
# MAIN LOGIC
# ============================================================================

async def main():
    logger.info("🔄 STARTING GOOGLE PRESENCE UPDATE (STANDALONE) 🔄")

    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        logger.error("❌ GOOGLE_ACCESS_TOKEN not found in environment!")
        return

    # 1. Google Search Console
    try:
        logger.info("🚀 Updating Search Console...")
        site_url = "https://studiocentos.it"
        sitemap_url = f"{site_url}/sitemap.xml"

        gsc = StandaloneGSCClient(access_token, site_url)
        success = await gsc.submit_sitemap(sitemap_url)

        if success:
            logger.info("✅ Sitemap submitted successfully!")
        else:
            logger.warning("⚠️ Failed to submit sitemap (check permissions/token scope)")

    except Exception as e:
        logger.error(f"❌ GSC Error: {e}")

    # 2. Google Business Profile
    try:
        logger.info("🚀 Updating Business Profile...")
        gmb = StandaloneGMBClient(access_token)

        locations = await gmb.list_locations()
        if not locations:
            logger.warning("⚠️ No GMB locations found.")
        else:
            location = locations[0]
            location_name = location["name"].split("/")[-1] # Extract ID? No, keep full name
            # Actually, the name from API is like "locations/123456"
            # But v4 API needs "accounts/123/locations/456"

            # Use name as is (locations/XXX) and let client prepend account
            loc_full_name = location["name"]
            logger.info(f"🏢 Found location: {location.get('title')} ({loc_full_name})")

            post_summary = "🚀 StudioCentOS diventa la Prima Agenzia AI a Salerno! 🤖\n\nAbbiamo evoluto i nostri servizi: non più solo Software House, ma partner per la tua trasformazione con Intelligenza Artificiale.\n\n✅ Chatbot AI & Assistenti Virtuali\n✅ Marketing Automation Intelligente\n✅ Generazione Contenuti AI\n✅ Dashboard Analytics Predittive\n\nScopri come l'AI può far crescere il tuo business. Consulenza Gratuita!"
            action_url = "https://studiocentos.it"
            media_url = "https://studiocentos.it/og-image.png"

            post = await gmb.create_post(loc_full_name, post_summary, action_url, media_url)

            if post:
                logger.info("✅ GMB Post created successfully!")
                logger.info(f"📄 Post Link: {post.get('searchUrl')}")

    except Exception as e:
        logger.error(f"❌ GMB Error: {e}")

    logger.info("🏁 UPDATE COMPLETE 🏁")

if __name__ == "__main__":
    asyncio.run(main())
