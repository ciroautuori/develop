"""
Sistema di Alert Automatici per ISS
Monitora bandi e invia notifiche automatiche basate su watchlist e profili utenti
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.database.database import get_db
from app.models.bando import Bando
from app.models.aps_user import APSUser, BandoWatchlist
from app.crud.aps_user import aps_user_crud, bando_watchlist_crud
from app.crud.bando import bando_crud
from app.services.email_notifications import email_notification_service
# Lazy import to avoid loading AI model at startup
# from app.services.semantic_search import semantic_search_service

logger = logging.getLogger(__name__)


class BandoAlertSystem:
    """Sistema di alert automatici per bandi e notifiche utenti"""

    def __init__(self):
        self.last_check = datetime.now()
        self.active = True

    async def check_new_bandi_alerts(self, db: AsyncSession) -> Dict[str, int]:
        """Controlla nuovi bandi e invia alert agli utenti interessati"""
        logger.info("🔍 Controllo nuovi bandi per alert...")

        results = {"users_notified": 0, "emails_sent": 0, "errors": 0}

        try:
            # Trova bandi nuovi (ultimi 24 ore)
            cutoff_time = datetime.now() - timedelta(hours=24)

            result = await db.execute(
                select(Bando).where(
                    and_(
                        Bando.data_trovato >= cutoff_time,
                        Bando.status == 'attivo'
                    )
                )
            )
            new_bandi = list(result.scalars().all())

            if not new_bandi:
                logger.info("📭 Nessun nuovo bando trovato")
                return results

            logger.info(f"🆕 Trovati {len(new_bandi)} nuovi bandi")

            # Recupera tutti gli utenti attivi con preferenze email
            users, _ = await aps_user_crud.search_users(db, skip=0, limit=1000, is_active=True)

            for user in users:
                try:
                    # Controlla preferenze notifiche
                    preferences = user.notification_preferences or {}
                    if not preferences.get('new_bandi_alerts', True):
                        continue

                    # Trova bandi rilevanti per l'utente usando AI
                    relevant_bandi = await self._find_relevant_bandi_for_user(db, user, new_bandi)

                    if relevant_bandi:
                        # Invia notifica email
                        success = await email_notification_service.send_new_bandi_alert(
                            user, relevant_bandi
                        )

                        if success:
                            results["emails_sent"] += 1
                            logger.info(f"📧 Alert inviato a {user.organization_name}: {len(relevant_bandi)} bandi")
                        else:
                            results["errors"] += 1

                        results["users_notified"] += 1

                except Exception as e:
                    logger.error(f"Errore alert per utente {user.id}: {e}")
                    results["errors"] += 1

            logger.info(f"✅ Alert nuovi bandi completato: {results}")
            return results

        except Exception as e:
            logger.error(f"❌ Errore controllo nuovi bandi: {e}")
            results["errors"] += 1
            return results

    async def check_deadline_reminders(self, db: AsyncSession) -> Dict[str, int]:
        """Controlla scadenze imminenti e invia reminder"""
        logger.info("⏰ Controllo scadenze imminenti...")

        results = {"reminders_sent": 0, "errors": 0}

        try:
            # Date di controllo: 7 giorni, 3 giorni, 1 giorno
            now = datetime.now()
            check_dates = [
                now + timedelta(days=7),   # 7 giorni prima
                now + timedelta(days=3),   # 3 giorni prima
                now + timedelta(days=1),   # 1 giorno prima
            ]

            for days_ahead, check_date in enumerate([7, 3, 1], 1):
                deadline_date = now + timedelta(days=check_date)

                # Trova bandi che scadono in questa data
                result = await db.execute(
                    select(Bando).where(
                        and_(
                            Bando.scadenza >= deadline_date.replace(hour=0, minute=0, second=0),
                            Bando.scadenza <= deadline_date.replace(hour=23, minute=59, second=59),
                            Bando.status == 'attivo'
                        )
                    )
                )
                expiring_bandi = list(result.scalars().all())

                if not expiring_bandi:
                    continue

                logger.info(f"⏰ {len(expiring_bandi)} bandi scadono in {check_date} giorni")

                for bando in expiring_bandi:
                    # Trova utenti che hanno questo bando in watchlist
                    watchlist_result = await db.execute(
                        select(BandoWatchlist).options(
                            selectinload(BandoWatchlist.aps_user)
                        ).where(BandoWatchlist.bando_id == bando.id)
                    )
                    watchlist_items = list(watchlist_result.scalars().all())

                    for item in watchlist_items:
                        user = item.aps_user

                        # Controlla preferenze
                        preferences = user.notification_preferences or {}
                        if not preferences.get('deadline_reminders', True):
                            continue

                        try:
                            success = await email_notification_service.send_deadline_reminder(
                                user, bando, check_date
                            )

                            if success:
                                results["reminders_sent"] += 1
                                logger.info(f"⏰ Reminder inviato a {user.organization_name} per {bando.title}")
                            else:
                                results["errors"] += 1

                        except Exception as e:
                            logger.error(f"Errore reminder per {user.organization_name}: {e}")
                            results["errors"] += 1

            logger.info(f"✅ Controllo scadenze completato: {results}")
            return results

        except Exception as e:
            logger.error(f"❌ Errore controllo scadenze: {e}")
            results["errors"] += 1
            return results

    async def send_weekly_newsletters(self, db: AsyncSession) -> Dict[str, int]:
        """Invia newsletter settimanali con statistiche e bandi"""
        logger.info("📊 Preparazione newsletter settimanali...")

        results = {"newsletters_sent": 0, "errors": 0}

        try:
            # Calcola statistiche settimanali
            stats = await self._calculate_weekly_stats(db)

            # Recupera utenti che vogliono la newsletter
            users, _ = await aps_user_crud.search_users(db, skip=0, limit=1000, is_active=True)

            for user in users:
                try:
                    # Controlla preferenze
                    preferences = user.notification_preferences or {}
                    if not preferences.get('weekly_newsletter', True):
                        continue

                    # Personalizza statistiche per l'utente
                    user_stats = await self._personalize_stats_for_user(db, user, stats)

                    success = await email_notification_service.send_weekly_newsletter(
                        user, user_stats
                    )

                    if success:
                        results["newsletters_sent"] += 1
                        logger.info(f"📊 Newsletter inviata a {user.organization_name}")
                    else:
                        results["errors"] += 1

                except Exception as e:
                    logger.error(f"Errore newsletter per {user.organization_name}: {e}")
                    results["errors"] += 1

            logger.info(f"✅ Newsletter settimanali completate: {results}")
            return results

        except Exception as e:
            logger.error(f"❌ Errore newsletter settimanali: {e}")
            results["errors"] += 1
            return results

    async def _find_relevant_bandi_for_user(self, db: AsyncSession, user: APSUser, bandi: List[Bando]) -> List[Bando]:
        """Trova bandi rilevanti per un utente specifico usando AI"""
        if not bandi:
            return []

        try:
            # Costruisci profilo utente per AI
            user_profile = {
                'organization_type': user.organization_type.value if user.organization_type else 'aps',
                'sectors': user.sectors or [],
                'target_groups': user.target_groups or [],
                'keywords': user.keywords or [],
                'geographical_scope': user.geographical_scope or 'Campania',
                'max_budget_interest': user.max_budget_interest,
                'description': user.description
            }

            # Usa AI per trovare match (lazy import)
            from app.services.semantic_search import semantic_search_service
            recommendations = await semantic_search_service.generate_user_recommendations(
                user_profile, db, limit=len(bandi)
            )

            # Filtra solo i bandi nuovi che sono stati raccomandati
            new_bando_ids = {b.id for b in bandi}
            relevant_bandi = []

            for rec in recommendations:
                if rec['bando'].id in new_bando_ids and rec['recommendation_score'] > 0.3:
                    relevant_bandi.append(rec['bando'])

            return relevant_bandi[:5]  # Max 5 bandi per email

        except Exception as e:
            logger.error(f"Errore ricerca bandi rilevanti per {user.organization_name}: {e}")
            # Fallback: usa matching semplice per settori
            relevant = []
            user_sectors = [s.lower() for s in (user.sectors or [])]

            for bando in bandi:
                if user_sectors and bando.categoria:
                    if any(sector in bando.categoria.lower() for sector in user_sectors):
                        relevant.append(bando)
                        if len(relevant) >= 3:
                            break

            return relevant

    async def _calculate_weekly_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Calcola statistiche settimanali per newsletter"""
        try:
            week_ago = datetime.now() - timedelta(days=7)

            # Nuovi bandi questa settimana
            new_bandi_result = await db.execute(
                select(Bando).where(Bando.data_trovato >= week_ago)
            )
            new_bandi = list(new_bandi_result.scalars().all())

            # Bandi attivi totali
            active_bandi_result = await db.execute(
                select(Bando).where(Bando.status == 'attivo')
            )
            active_bandi = list(active_bandi_result.scalars().all())

            # Calcola importo totale (quando possibile)
            total_amount = 0
            for bando in active_bandi:
                if bando.importo:
                    try:
                        # Estrai numeri dalla stringa importo
                        import re
                        numbers = re.findall(r'\d+(?:\.\d+)?', str(bando.importo))
                        if numbers:
                            total_amount += float(numbers[0])
                    except:
                        pass

            return {
                'nuovi_bandi': len(new_bandi),
                'totali_attivi': len(active_bandi),
                'importo_totale': f"{total_amount:,.0f}" if total_amount > 0 else None,
                'bandi_raccomandati': new_bandi[:3],  # Top 3 nuovi
                'scadenze_imminenti': []  # Verrà personalizzato per utente
            }

        except Exception as e:
            logger.error(f"Errore calcolo statistiche settimanali: {e}")
            return {
                'nuovi_bandi': 0,
                'totali_attivi': 0,
                'importo_totale': None,
                'bandi_raccomandati': [],
                'scadenze_imminenti': []
            }

    async def _personalize_stats_for_user(self, db: AsyncSession, user: APSUser, base_stats: Dict) -> Dict[str, Any]:
        """Personalizza le statistiche per un utente specifico"""
        personalized = base_stats.copy()

        try:
            # Aggiungi raccomandazioni AI personalizzate
            if user.id:
                user_profile = {
                    'organization_type': user.organization_type.value if user.organization_type else 'aps',
                    'sectors': user.sectors or [],
                    'target_groups': user.target_groups or [],
                    'keywords': user.keywords or [],
                    'geographical_scope': user.geographical_scope or 'Campania'
                }

                # Lazy import AI service
                from app.services.semantic_search import semantic_search_service
                recommendations = await semantic_search_service.generate_user_recommendations(
                    user_profile, db, limit=3
                )

                personalized['raccomandazioni_ai'] = len(recommendations)
                personalized['bandi_raccomandati'] = [rec['bando'] for rec in recommendations[:3]]

            # Aggiungi scadenze dalla watchlist dell'utente
            watchlist = await bando_watchlist_crud.get_user_watchlist(db, user.id)
            upcoming_deadlines = []

            now = datetime.now()
            for item in watchlist:
                if item.bando.scadenza and item.bando.scadenza > now:
                    days_left = (item.bando.scadenza - now).days
                    if days_left <= 30:  # Solo prossimi 30 giorni
                        upcoming_deadlines.append({
                            'bando': item.bando,
                            'days_left': days_left
                        })

            personalized['scadenze_imminenti'] = sorted(
                upcoming_deadlines,
                key=lambda x: x['days_left']
            )[:5]

        except Exception as e:
            logger.error(f"Errore personalizzazione stats per {user.organization_name}: {e}")

        return personalized


# Singleton service instance
alert_system = BandoAlertSystem()
