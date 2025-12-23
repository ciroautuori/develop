from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
import hashlib

from app.models.bando import Bando, BandoStatus, BandoSource
from app.schemas.bando import BandoCreate, BandoUpdate, BandoSearch


class BandoCRUD:

    @staticmethod
    def generate_hash(title: str, ente: str, link: str) -> str:
        """Genera hash univoco per identificare un bando"""
        content = f"{title}_{ente}_{link}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    async def create_bando(self, db: AsyncSession, bando: BandoCreate) -> Bando:
        """Crea un nuovo bando"""
        hash_identifier = self.generate_hash(bando.title, bando.ente, bando.link)

        # Verifica se già esiste
        existing = await self.get_bando_by_hash(db, hash_identifier)
        if existing:
            return existing

        db_bando = Bando(
            **bando.model_dump(),
            hash_identifier=hash_identifier
        )
        db.add(db_bando)
        await db.commit()
        await db.refresh(db_bando)
        return db_bando

    async def get_bando(self, db: AsyncSession, bando_id: int) -> Optional[Bando]:
        """Recupera un bando per ID"""
        result = await db.execute(select(Bando).where(Bando.id == bando_id))
        return result.scalar_one_or_none()

    async def get_bando_by_hash(self, db: AsyncSession, hash_identifier: str) -> Optional[Bando]:
        """Recupera un bando per hash"""
        result = await db.execute(
            select(Bando).where(Bando.hash_identifier == hash_identifier)
        )
        return result.scalar_one_or_none()

    async def get_bandi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        search: Optional[BandoSearch] = None
    ) -> tuple[List[Bando], int]:
        """Recupera lista bandi con filtri e paginazione"""

        query = select(Bando)
        count_query = select(func.count(Bando.id))

        # Applica filtri
        if search:
            conditions = []

            if search.query:
                # Cerca ogni parola separatamente (AND logic)
                words = search.query.strip().split()
                for word in words:
                    if len(word) >= 2:  # Ignora parole troppo corte
                        word_term = f"%{word}%"
                        conditions.append(
                            or_(
                                Bando.title.ilike(word_term),
                                Bando.ente.ilike(word_term),
                                Bando.descrizione.ilike(word_term),
                                Bando.keyword_match.ilike(word_term)
                            )
                        )

            if search.fonte:
                conditions.append(Bando.fonte == search.fonte)

            if search.status:
                conditions.append(Bando.status == search.status)

            if search.date_from:
                conditions.append(Bando.data_trovato >= search.date_from)

            if search.date_to:
                conditions.append(Bando.data_trovato <= search.date_to)

            if search.keyword:
                keyword_term = f"%{search.keyword}%"
                conditions.append(Bando.keyword_match.ilike(keyword_term))

            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))

        # Ordina per data più recente
        query = query.order_by(desc(Bando.data_trovato))

        # Paginazione
        query = query.offset(skip).limit(limit)

        # Esegui query
        result = await db.execute(query)
        bandi = result.scalars().all()

        count_result = await db.execute(count_query)
        total = count_result.scalar()

        return list(bandi), total

    async def update_bando(
        self,
        db: AsyncSession,
        bando_id: int,
        bando_update: BandoUpdate
    ) -> Optional[Bando]:
        """Aggiorna un bando"""
        db_bando = await self.get_bando(db, bando_id)
        if not db_bando:
            return None

        update_data = bando_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_bando, field, value)

        await db.commit()
        await db.refresh(db_bando)
        return db_bando

    async def delete_bando(self, db: AsyncSession, bando_id: int) -> bool:
        """Elimina un bando"""
        db_bando = await self.get_bando(db, bando_id)
        if not db_bando:
            return False

        await db.delete(db_bando)
        await db.commit()
        return True

    async def mark_as_notified(
        self,
        db: AsyncSession,
        bando_id: int,
        email: bool = False,
        telegram: bool = False
    ) -> Optional[Bando]:
        """Marca un bando come notificato"""
        db_bando = await self.get_bando(db, bando_id)
        if not db_bando:
            return None

        if email:
            db_bando.notificato_email = True
        if telegram:
            db_bando.notificato_telegram = True

        await db.commit()
        await db.refresh(db_bando)
        return db_bando

    async def get_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Ottieni statistiche sui bandi"""

        # Conteggi totali
        total_query = select(func.count(Bando.id))
        total_result = await db.execute(total_query)
        totali = total_result.scalar() or 0

        # Bandi attivi
        active_query = select(func.count(Bando.id)).where(Bando.status == BandoStatus.ATTIVO)
        active_result = await db.execute(active_query)
        attivi = active_result.scalar() or 0

        # Bandi scaduti
        expired_query = select(func.count(Bando.id)).where(Bando.status == BandoStatus.SCADUTO)
        expired_result = await db.execute(expired_query)
        scaduti = expired_result.scalar() or 0

        # Bandi in scadenza (prossimi 30 giorni)
        future_30_days = datetime.now() + timedelta(days=30)
        expiring_query = select(func.count(Bando.id)).where(
            and_(
                Bando.status == BandoStatus.ATTIVO,
                Bando.scadenza <= future_30_days,
                Bando.scadenza >= datetime.now()
            )
        )
        expiring_result = await db.execute(expiring_query)
        in_scadenza = expiring_result.scalar() or 0

        # Bandi per fonte
        source_query = select(Bando.fonte, func.count(Bando.id)).group_by(Bando.fonte)
        source_result = await db.execute(source_query)
        fonti = {fonte.value if hasattr(fonte, 'value') else str(fonte): count
                for fonte, count in source_result.fetchall()}

        # Bandi per categoria
        category_query = select(Bando.categoria, func.count(Bando.id)).where(
            Bando.categoria.isnot(None)
        ).group_by(Bando.categoria)
        category_result = await db.execute(category_query)
        categorie = {categoria: count for categoria, count in category_result.fetchall()}

        # Ultimi 7 giorni
        week_ago = datetime.now() - timedelta(days=7)
        recent_query = select(func.count(Bando.id)).where(Bando.data_trovato >= week_ago)
        recent_result = await db.execute(recent_query)
        nuovi_settimana = recent_result.scalar() or 0

        # Calcolo importi (mock data per ora)
        importo_totale = 15000000.0  # €15M mock
        importo_medio = importo_totale / max(totali, 1)

        # Trend mensile (ultimi 6 mesi)
        trend_mensile = []
        for i in range(6):
            month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)

            month_query = select(func.count(Bando.id)).where(
                and_(
                    Bando.data_trovato >= month_start,
                    Bando.data_trovato < month_end
                )
            )
            month_result = await db.execute(month_query)
            count = month_result.scalar() or 0

            trend_mensile.append({
                "mese": month_start.strftime("%Y-%m"),
                "count": count,
                "importo": count * (importo_medio if count > 0 else 0)
            })

        trend_mensile.reverse()  # Ordine cronologico

        return {
            # Formato nuovo per il frontend
            "totali": totali,
            "attivi": attivi,
            "scaduti": scaduti,
            "in_scadenza": in_scadenza,
            "importo_totale": importo_totale,
            "importo_medio": importo_medio,
            "nuovi_settimana": nuovi_settimana,
            "fonti": fonti,
            "categorie": categorie,
            "trend_mensile": trend_mensile,

            # Campi legacy per compatibilità
            "total_bandi": totali,
            "bandi_attivi": attivi,
            "bandi_scaduti": scaduti,
            "bandi_per_fonte": fonti,
            "ultimi_trovati": nuovi_settimana,
            "media_giornaliera": round(nuovi_settimana / 7.0, 2)
        }

    async def get_recent_bandi(self, db: AsyncSession, limit: int = 10) -> List[Bando]:
        """Ottieni i bandi più recenti"""
        query = select(Bando).order_by(desc(Bando.data_trovato)).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def cleanup_old_bandi(self, db: AsyncSession, days_old: int = 365) -> int:
        """Pulisce i bandi vecchi (archivia)"""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        # Aggiorna status invece di eliminare
        update_query = (
            select(Bando)
            .where(and_(
                Bando.data_trovato < cutoff_date,
                Bando.status != BandoStatus.ARCHIVIATO
            ))
        )

        result = await db.execute(update_query)
        old_bandi = result.scalars().all()

        count = 0
        for bando in old_bandi:
            bando.status = BandoStatus.ARCHIVIATO
            count += 1

        await db.commit()
        return count


# Istanza singleton
bando_crud = BandoCRUD()
