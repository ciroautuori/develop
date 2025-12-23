"""
CRUD operations per utenti APS e sistema utenti
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, text
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from app.models.aps_user import APSUser, BandoApplication, BandoWatchlist, AIRecommendation, OrganizationType
from app.models.bando import Bando
from app.crud.base import CRUDBase


class CRUDAPSUser(CRUDBase[APSUser, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations per utenti APS"""

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[APSUser]:
        """Trova utente per email"""
        result = await db.execute(
            select(APSUser).where(APSUser.contact_email == email)
        )
        return result.scalars().first()

    async def get_by_fiscal_code(self, db: AsyncSession, fiscal_code: str) -> Optional[APSUser]:
        """Trova utente per codice fiscale"""
        result = await db.execute(
            select(APSUser).where(APSUser.fiscal_code == fiscal_code)
        )
        return result.scalars().first()

    async def create_aps_user(self, db: AsyncSession, user_data: Dict[str, Any]) -> APSUser:
        """Crea nuovo utente APS"""
        db_user = APSUser(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def search_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        organization_type: Optional[OrganizationType] = None,
        region: Optional[str] = None,
        sectors: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[APSUser], int]:
        """Ricerca utenti con filtri"""
        
        query = select(APSUser)
        count_query = select(func.count(APSUser.id))
        
        # Filtri
        conditions = []
        
        if search:
            search_condition = or_(
                APSUser.organization_name.ilike(f"%{search}%"),
                APSUser.contact_email.ilike(f"%{search}%"),
                APSUser.city.ilike(f"%{search}%")
            )
            conditions.append(search_condition)
        
        if organization_type:
            conditions.append(APSUser.organization_type == organization_type)
        
        if region:
            conditions.append(APSUser.region == region)
        
        if is_active is not None:
            conditions.append(APSUser.is_active == is_active)
        
        if sectors:
            # Ricerca in JSON field
            for sector in sectors:
                conditions.append(text(f"JSON_CONTAINS(sectors, '\"{sector}\"')"))
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Count
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Results con paginazione
        query = query.order_by(desc(APSUser.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        
        return list(users), total

    async def get_user_dashboard_data(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Dati dashboard completa per utente"""
        
        # Carica utente con relazioni
        result = await db.execute(
            select(APSUser)
            .options(
                selectinload(APSUser.applications).selectinload(BandoApplication.bando),
                selectinload(APSUser.watchlists).selectinload(BandoWatchlist.bando),
                selectinload(APSUser.ai_recommendations).selectinload(AIRecommendation.bando)
            )
            .where(APSUser.id == user_id)
        )
        user = result.scalars().first()
        
        if not user:
            return {}
        
        # Statistiche candidature
        applications_stats = {
            'total': len(user.applications),
            'submitted': len([a for a in user.applications if a.status == 'submitted']),
            'in_review': len([a for a in user.applications if a.status == 'in_review']),
            'approved': len([a for a in user.applications if a.status == 'approved']),
            'rejected': len([a for a in user.applications if a.status == 'rejected']),
            'success_rate': 0
        }
        
        if applications_stats['total'] > 0:
            applications_stats['success_rate'] = (
                applications_stats['approved'] / applications_stats['total'] * 100
            )

        # Watchlist attiva
        active_watchlist = [w for w in user.watchlists if w.bando.status.value == 'attivo']
        
        # Raccomandazioni AI non viste
        unviewed_recommendations = [r for r in user.ai_recommendations if not r.viewed]
        
        # Bandi scadenti (prossimi 30 giorni)
        upcoming_deadlines = []
        cutoff_date = datetime.now() + timedelta(days=30)
        
        for watchlist in active_watchlist:
            if watchlist.bando.scadenza and watchlist.bando.scadenza <= cutoff_date:
                upcoming_deadlines.append({
                    'bando': watchlist.bando,
                    'days_left': (watchlist.bando.scadenza - datetime.now()).days,
                    'priority': watchlist.priority
                })
        
        return {
            'user': user,
            'applications_stats': applications_stats,
            'active_watchlist_count': len(active_watchlist),
            'unviewed_recommendations_count': len(unviewed_recommendations),
            'upcoming_deadlines': sorted(upcoming_deadlines, key=lambda x: x['days_left']),
            'recent_applications': sorted(user.applications, key=lambda x: x.application_date, reverse=True)[:5],
            'top_recommendations': sorted(unviewed_recommendations, key=lambda x: x.recommendation_score, reverse=True)[:5]
        }

    async def update_last_login(self, db: AsyncSession, user_id: int) -> None:
        """Aggiorna ultimo login"""
        await db.execute(
            text("UPDATE aps_users SET last_login = NOW() WHERE id = :user_id"),
            {"user_id": user_id}
        )
        await db.commit()


class CRUDBandoApplication(CRUDBase[BandoApplication, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations per candidature bandi"""

    async def create_application(self, db: AsyncSession, user_id: int, bando_id: int, application_data: Dict[str, Any]) -> BandoApplication:
        """Crea nuova candidatura"""
        app_data = {
            'aps_user_id': user_id,
            'bando_id': bando_id,
            **application_data
        }
        
        db_application = BandoApplication(**app_data)
        db.add(db_application)
        await db.commit()
        await db.refresh(db_application)
        return db_application

    async def get_user_applications(
        self,
        db: AsyncSession,
        user_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[BandoApplication]:
        """Recupera candidature utente"""
        
        query = select(BandoApplication).options(
            selectinload(BandoApplication.bando)
        ).where(BandoApplication.aps_user_id == user_id)
        
        if status:
            query = query.where(BandoApplication.status == status)
        
        query = query.order_by(desc(BandoApplication.application_date)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def update_application_status(self, db: AsyncSession, application_id: int, status: str, notes: Optional[str] = None) -> Optional[BandoApplication]:
        """Aggiorna stato candidatura"""
        result = await db.execute(
            select(BandoApplication).where(BandoApplication.id == application_id)
        )
        application = result.scalars().first()
        
        if application:
            application.status = status
            application.last_update = datetime.utcnow()
            if notes:
                application.internal_notes = notes
            
            await db.commit()
            await db.refresh(application)
        
        return application


class CRUDBandoWatchlist(CRUDBase[BandoWatchlist, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations per watchlist bandi"""

    async def add_to_watchlist(self, db: AsyncSession, user_id: int, bando_id: int, priority: str = "medium", notes: Optional[str] = None) -> BandoWatchlist:
        """Aggiunge bando alla watchlist"""
        
        # Controlla se già esiste
        existing = await db.execute(
            select(BandoWatchlist).where(
                and_(
                    BandoWatchlist.aps_user_id == user_id,
                    BandoWatchlist.bando_id == bando_id
                )
            )
        )
        
        if existing.scalars().first():
            raise ValueError("Bando già in watchlist")
        
        watchlist_item = BandoWatchlist(
            aps_user_id=user_id,
            bando_id=bando_id,
            priority=priority,
            notes=notes
        )
        
        db.add(watchlist_item)
        await db.commit()
        await db.refresh(watchlist_item)
        return watchlist_item

    async def get_user_watchlist(self, db: AsyncSession, user_id: int, active_only: bool = True) -> List[BandoWatchlist]:
        """Recupera watchlist utente"""
        
        query = select(BandoWatchlist).options(
            selectinload(BandoWatchlist.bando)
        ).where(BandoWatchlist.aps_user_id == user_id)
        
        if active_only:
            query = query.join(Bando).where(Bando.status == 'attivo')
        
        query = query.order_by(desc(BandoWatchlist.added_date))
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def remove_from_watchlist(self, db: AsyncSession, user_id: int, bando_id: int) -> bool:
        """Rimuove bando dalla watchlist"""
        
        result = await db.execute(
            select(BandoWatchlist).where(
                and_(
                    BandoWatchlist.aps_user_id == user_id,
                    BandoWatchlist.bando_id == bando_id
                )
            )
        )
        
        watchlist_item = result.scalars().first()
        if watchlist_item:
            await db.delete(watchlist_item)
            await db.commit()
            return True
        
        return False


# Instances
aps_user_crud = CRUDAPSUser(APSUser)
bando_application_crud = CRUDBandoApplication(BandoApplication)
bando_watchlist_crud = CRUDBandoWatchlist(BandoWatchlist)
