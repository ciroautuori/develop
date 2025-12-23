import asyncio
import os
import sys
from app.domain.social.publisher_service import MetaPublisher

# Add project root to path
sys.path.append(os.getcwd())

async def discover():
    print("🔍 Avvio scoperta account Instagram collegato...")

    try:
        meta = MetaPublisher()
        if not meta.is_configured:
            print("❌ Errore: MetaPublisher non configurato. Controlla .env")
            return

        client = await meta.get_client()

        # 1. Get Page Token (verify access)
        page_token = await meta._get_page_token()
        if not page_token:
            print("❌ Errore: Impossibile ottenere il Page Token. Il token utente potrebbe essere scaduto o non avere i permessi 'pages_show_list' e 'pages_read_engagement'.")
            await meta.close()
            return

        print(f"✅ Page Token ottenuto per la pagina ID: {meta.page_id}")

        # 2. Check for Instagram Business Account
        url = f'{meta.BASE_URL}/{meta.page_id}'
        params = {
            'access_token': meta.access_token, # User token is usually better for reading connection info
            'fields': 'instagram_business_account,name'
        }

        r = await client.get(url, params=params)
        if r.status_code == 200:
            data = r.json()
            page_name = data.get('name')
            ig_account = data.get('instagram_business_account')

            print(f"📄 Pagina Facebook: {page_name}")

            if ig_account:
                ig_id = ig_account.get("id")
                print(f"\n🎉 TROVATO! Instagram Business Account ID: {ig_id}")
                print(f"👉 Aggiorna il tuo .env con: INSTAGRAM_ACCOUNT_ID={ig_id}")

                # Verify IG details
                r_ig = await client.get(
                    f'{meta.BASE_URL}/{ig_id}',
                    params={'access_token': meta.access_token, 'fields': 'username,name,profile_picture_url'}
                )
                if r_ig.status_code == 200:
                    ig_data = r_ig.json()
                    print(f"   Username: @{ig_data.get('username')}")
                    print(f"   Nome: {ig_data.get('name')}")

            else:
                print("\n⚠️ NESSUN account Instagram Business trovato collegato a questa pagina.")
                print("Assicurati di:")
                print("1. Avere un account Instagram 'Business' o 'Creator' (non personale).")
                print("2. Aver collegato Instagram alla Pagina Facebook (Impostazioni Pagina -> Account collegati).")
        else:
            print(f"❌ Errore API: {r.json()}")

        await meta.close()

    except Exception as e:
        print(f"❌ Eccezione imprevista: {e}")

if __name__ == "__main__":
    asyncio.run(discover())
